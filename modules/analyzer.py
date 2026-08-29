"""
Módulo 3: Motor analítico.

Calcula:
  1. Curva de maná y CMC promedio (excluye tierras).
  2. Balance de maná: PIPs coloreados requeridos vs. fuentes de tierras.
  3. Consistencia hipergeométrica (P(X >= k)).
  4. Clasificación heurística de roles tácticos por regex sobre oracle_text/type_line.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

from .scryfall_client import EnrichedCard

COLORS = ["W", "U", "B", "R", "G", "C"]
COLOR_NAMES = {
    "W": "Blanco",
    "U": "Azul",
    "B": "Negro",
    "R": "Rojo",
    "G": "Verde",
    "C": "Incoloro",
}
BASIC_LAND_PRODUCES = {
    "plains": "W",
    "island": "U",
    "swamp": "B",
    "mountain": "R",
    "forest": "G",
    "wastes": "C",
}

_PIP_RE = re.compile(r"\{([WUBRGC])\}")


# --------------------------------------------------------------------------- #
# 1. Curva de maná
# --------------------------------------------------------------------------- #
@dataclass
class ManaCurve:
    buckets: dict[str, int]  # "0".."6", "7+"
    avg_cmc: float
    total_nonland: int


def compute_curve(cards: list[EnrichedCard]) -> ManaCurve:
    buckets = {str(i): 0 for i in range(7)}
    buckets["7+"] = 0
    total_nonland = 0
    weighted_sum = 0.0

    for card in cards:
        if card.is_land:
            continue
        cmc_int = int(card.cmc)
        total_nonland += card.quantity
        weighted_sum += card.cmc * card.quantity
        key = "7+" if cmc_int >= 7 else str(cmc_int)
        buckets[key] += card.quantity

    avg = (weighted_sum / total_nonland) if total_nonland else 0.0
    return ManaCurve(buckets=buckets, avg_cmc=round(avg, 2), total_nonland=total_nonland)


# --------------------------------------------------------------------------- #
# 2. Balance de maná
# --------------------------------------------------------------------------- #
@dataclass
class ManaBalance:
    pips_required: dict[str, int]
    sources_available: dict[str, int]
    coverage_ratio: dict[str, float]
    total_lands: int


def compute_mana_balance(cards: list[EnrichedCard]) -> ManaBalance:
    pips = {c: 0 for c in COLORS}
    sources = {c: 0 for c in COLORS}
    total_lands = 0

    for card in cards:
        # PIPs requeridos por hechizos (no tierras).
        if not card.is_land and card.mana_cost:
            for sym in _PIP_RE.findall(card.mana_cost):
                pips[sym] += card.quantity

        if card.is_land:
            total_lands += card.quantity
            produced = _land_sources(card)
            for color in produced:
                if color in sources:
                    sources[color] += card.quantity

    ratio = {}
    for color in COLORS:
        req = pips[color]
        ratio[color] = round(sources[color] / req, 2) if req else 0.0

    return ManaBalance(
        pips_required=pips,
        sources_available=sources,
        coverage_ratio=ratio,
        total_lands=total_lands,
    )


def _land_sources(card: EnrichedCard) -> set[str]:
    """Colores que una tierra puede producir."""
    produced: set[str] = set()
    for m in card.produced_mana:
        if m in COLORS:
            produced.add(m)
    # Fallback por subtipos de tierras básicas si no hay produced_mana.
    if not produced:
        low = card.type_line.lower()
        for subtype, color in BASIC_LAND_PRODUCES.items():
            if subtype in low:
                produced.add(color)
    return produced


# --------------------------------------------------------------------------- #
# 3. Consistencia hipergeométrica
# --------------------------------------------------------------------------- #
def hypergeometric_at_least(k: int, N: int, K: int, n: int) -> float:
    """P(X >= k) donde X ~ Hipergeométrica(N, K, n)."""
    if N <= 0 or n <= 0 or K < 0:
        return 0.0
    K = min(K, N)
    n = min(n, N)
    x_min = max(k, 0)
    x_max = min(K, n)
    if x_min > x_max:
        return 0.0
    denom = math.comb(N, n)
    if denom == 0:
        return 0.0
    total = 0
    for x in range(x_min, x_max + 1):
        total += math.comb(K, x) * math.comb(N - K, n - x)
    return round(total / denom, 4)


@dataclass
class Consistency:
    deck_size: int
    total_lands: int
    total_ramp: int
    p_lands_t3: float          # P(>=3 tierras vistas en T3, on the draw: n=9)
    p_ramp_opening: float      # P(>=1 pieza de ramp en mano inicial: n=7)


def compute_consistency(
    cards: list[EnrichedCard],
    role_index: "RoleIndex",
    deck_size: int = 99,
) -> Consistency:
    total_lands = sum(c.quantity for c in cards if c.is_land)
    total_ramp = role_index.counts.get("Ramp / Fixing", 0)

    p_lands = hypergeometric_at_least(k=3, N=deck_size, K=total_lands, n=9)
    p_ramp = hypergeometric_at_least(k=1, N=deck_size, K=total_ramp, n=7)

    return Consistency(
        deck_size=deck_size,
        total_lands=total_lands,
        total_ramp=total_ramp,
        p_lands_t3=p_lands,
        p_ramp_opening=p_ramp,
    )


# --------------------------------------------------------------------------- #
# 4. Roles tácticos
# --------------------------------------------------------------------------- #
# (nombre, patrón compilado, requiere_no_tierra)
_ROLE_PATTERNS: list[tuple[str, re.Pattern, bool]] = [
    ("Ramp / Fixing", re.compile(r"add (one mana|\{[wubrgc]\})|search your library.*land", re.I), True),
    ("Card Advantage", re.compile(r"draw (a|two|three|\d+) card|discover \d+|investigate", re.I), False),
    ("Single Removal", re.compile(r"(destroy|exile) target", re.I), False),
    ("Board Wipe", re.compile(r"(destroy|exile) all|each nonartifact creature", re.I), False),
    ("Proliferate", re.compile(r"proliferate", re.I), False),
    ("Charge Synergies", re.compile(r"charge counter", re.I), False),
    ("Protection / Counter", re.compile(r"hexproof|indestructible|ward|counter target spell", re.I), False),
    ("Cost Reducers", re.compile(r"affinity for artifacts|improvise|cost \{1\} less", re.I), False),
    ("Karnstruct Engine", re.compile(r"create a 0/0.*construct", re.I), False),
]


@dataclass
class RoleIndex:
    counts: dict[str, int] = field(default_factory=dict)          # copias por rol
    cards_by_role: dict[str, list[str]] = field(default_factory=dict)  # nombres clave


def classify_roles(cards: list[EnrichedCard]) -> RoleIndex:
    counts: dict[str, int] = {name: 0 for name, _, _ in _ROLE_PATTERNS}
    cards_by_role: dict[str, list[str]] = {name: [] for name, _, _ in _ROLE_PATTERNS}

    for card in cards:
        text = card.oracle_text or ""
        for role_name, pattern, needs_nonland in _ROLE_PATTERNS:
            if needs_nonland and card.is_land:
                continue
            if pattern.search(text):
                counts[role_name] += card.quantity
                if card.name not in cards_by_role[role_name]:
                    cards_by_role[role_name].append(card.name)

    # Eliminar roles sin coincidencias para un reporte más limpio.
    counts = {k: v for k, v in counts.items() if v > 0}
    cards_by_role = {k: v for k, v in cards_by_role.items() if v}
    return RoleIndex(counts=counts, cards_by_role=cards_by_role)


# --------------------------------------------------------------------------- #
# Agregado
# --------------------------------------------------------------------------- #
@dataclass
class DeckAnalysis:
    curve: ManaCurve
    balance: ManaBalance
    roles: RoleIndex
    consistency: Consistency
    total_cards: int
    total_lands: int
    total_value_usd: float


def analyze(cards: list[EnrichedCard], deck_size: int | None = None) -> DeckAnalysis:
    total_cards = sum(c.quantity for c in cards)
    size = deck_size or max(total_cards, 1)

    curve = compute_curve(cards)
    balance = compute_mana_balance(cards)
    roles = classify_roles(cards)
    consistency = compute_consistency(cards, roles, deck_size=size)
    total_value = round(
        sum((c.price_usd or 0.0) * c.quantity for c in cards), 2
    )

    return DeckAnalysis(
        curve=curve,
        balance=balance,
        roles=roles,
        consistency=consistency,
        total_cards=total_cards,
        total_lands=balance.total_lands,
        total_value_usd=total_value,
    )
