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

# --- Patrones v2 (spect_metricas.v2.md) --------------------------------------
_ADD_MANA_RE = re.compile(r"add (one mana|\{[wubrgc]\})", re.I)
_TOKEN_RE = re.compile(r"\b(create|creates)\b\s+(?:.*?)token", re.I)
_EVASION_RE = re.compile(
    r"\b(flying|trample|deathtouch|can't be blocked|shadow|fear|intimidate|menace)\b", re.I
)
_HASTE_RE = re.compile(r"\bhaste\b", re.I)
_LIFEGAIN_RE = re.compile(r"\blifelink\b|gain \d+ life|whenever .* gain life", re.I)
_LIFECOST_RE = re.compile(r"pay \d+ life|lose \d+ life", re.I)
_PROTECTION_RE = re.compile(r"\b(hexproof|indestructible|ward)\b|counter target", re.I)
_RECURSION_RE = re.compile(
    r"return .* from your graveyard|cast .* from your graveyard|play lands from your graveyard",
    re.I,
)
_DEATH_TRIGGER_RE = re.compile(r"whenever .* dies", re.I)
_TAPLAND_RE = re.compile(r"enters tapped", re.I)
_TAPLAND_COND_RE = re.compile(r"unless|pay 2 life", re.I)


def _dynamic_power(power: str | None) -> bool:
    """True si el poder es dinámico (`*` o `X`), no estático."""
    if power is None:
        return False
    return "*" in power or "x" in power.lower()


def _static_power(power: str | None) -> int:
    """Poder base estático; `*`/`X` computan 0 (spec 3.2)."""
    if power is None or _dynamic_power(power):
        return 0
    try:
        return int(power)
    except ValueError:
        return 0


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
def diagnose_ratio(ratio: float | None) -> str:
    """Diagnóstico de cobertura de color (spec 3.4.2)."""
    if ratio is None:
        return "N/A"
    if ratio >= 0.85:
        return "🟢 Óptimo"
    if ratio >= 0.55:
        return "🟡 Ajustado"
    return "🔴 Déficit"


@dataclass
class ManaBalance:
    pips_required: dict[str, int]
    sources_available: dict[str, int]
    coverage_ratio: dict[str, float | None]  # None => PIPs(c) == 0 (N/A)
    diagnosis: dict[str, str]
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

    ratio: dict[str, float | None] = {}
    diagnosis: dict[str, str] = {}
    for color in COLORS:
        req = pips[color]
        if req > 0:
            r = round(sources[color] / req, 2)
            ratio[color] = r
            diagnosis[color] = diagnose_ratio(r)
        else:
            ratio[color] = None
            diagnosis[color] = "N/A"

    return ManaBalance(
        pips_required=pips,
        sources_available=sources,
        coverage_ratio=ratio,
        diagnosis=diagnosis,
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
    acceleration: "Acceleration | None" = None,
    deck_size: int = 99,
) -> Consistency:
    total_lands = sum(c.quantity for c in cards if c.is_land)

    # Total Ramp (spec 3.4.4): Rocks + Dorks + hechizos de ramp/fixing.
    # Unimos las piezas basadas en producción de maná (rocks/dorks) con las
    # detectadas por rol (ramp/fixing como búsqueda de tierras) evitando
    # doble conteo mediante el máximo entre ambas señales.
    ramp_spells = role_index.counts.get("Ramp / Fixing", 0)
    ramp_pieces = acceleration.total_ramp_pieces if acceleration else 0
    total_ramp = max(ramp_spells, ramp_pieces)

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
# 5. Aceleración de maná y creación de fichas (spec 3.1)
# --------------------------------------------------------------------------- #
@dataclass
class Acceleration:
    mana_rocks: int
    mana_dorks: int
    token_producers: int
    rocks_examples: list[str] = field(default_factory=list)
    dorks_examples: list[str] = field(default_factory=list)
    token_examples: list[str] = field(default_factory=list)

    @property
    def total_ramp_pieces(self) -> int:
        """Rocks + Dorks (piezas de ramp basadas en producción de maná)."""
        return self.mana_rocks + self.mana_dorks


def compute_acceleration(cards: list[EnrichedCard]) -> Acceleration:
    rocks = dorks = tokens = 0
    rocks_ex: list[str] = []
    dorks_ex: list[str] = []
    tokens_ex: list[str] = []

    for card in cards:
        tl = card.type_line.lower()
        text = card.oracle_text or ""
        is_creature = "creature" in tl
        is_artifact = "artifact" in tl
        is_land = "land" in tl
        produces = bool(_ADD_MANA_RE.search(text)) or bool(card.produced_mana)

        # Mana Dorks: criatura no-tierra que produce maná.
        if is_creature and not is_land and produces:
            dorks += card.quantity
            if card.name not in dorks_ex:
                dorks_ex.append(card.name)
        # Mana Rocks: artefacto no-criatura no-tierra que produce maná.
        elif is_artifact and not is_creature and not is_land and produces:
            rocks += card.quantity
            if card.name not in rocks_ex:
                rocks_ex.append(card.name)

        # Token producers: cualquier tipo.
        if _TOKEN_RE.search(text):
            tokens += card.quantity
            if card.name not in tokens_ex:
                tokens_ex.append(card.name)

    return Acceleration(
        mana_rocks=rocks,
        mana_dorks=dorks,
        token_producers=tokens,
        rocks_examples=rocks_ex,
        dorks_examples=dorks_ex,
        token_examples=tokens_ex,
    )


# --------------------------------------------------------------------------- #
# 6. Capacidad ofensiva — Combat Clock (spec 3.2)
# --------------------------------------------------------------------------- #
@dataclass
class CombatClock:
    total_power: int
    total_creatures: int
    dynamic_power_creatures: int
    evasion_count: int
    haste_count: int
    avg_power_per_creature: float
    combat_clock_index: float


def compute_combat_clock(cards: list[EnrichedCard]) -> CombatClock:
    total_power = 0
    total_creatures = 0
    dynamic = 0
    evasion = 0
    haste = 0

    for card in cards:
        if "creature" not in card.type_line.lower():
            continue
        total_creatures += card.quantity
        if _dynamic_power(card.power):
            dynamic += card.quantity
        total_power += _static_power(card.power) * card.quantity

        text = card.oracle_text or ""
        if _EVASION_RE.search(text):
            evasion += card.quantity
        if _HASTE_RE.search(text):
            haste += card.quantity

    avg = (total_power / total_creatures) if total_creatures else 0.0
    cci = avg + (evasion * 0.5) + (haste * 0.75)

    return CombatClock(
        total_power=total_power,
        total_creatures=total_creatures,
        dynamic_power_creatures=dynamic,
        evasion_count=evasion,
        haste_count=haste,
        avg_power_per_creature=round(avg, 2),
        combat_clock_index=round(cci, 2),
    )


# --------------------------------------------------------------------------- #
# 7. Resiliencia, sustento y gestión de vida (spec 3.3)
# --------------------------------------------------------------------------- #
@dataclass
class Resilience:
    lifegain_sources: int
    life_as_resource: int
    active_protection: int
    graveyard_recursion: int
    death_triggers: int


def compute_resilience(cards: list[EnrichedCard]) -> Resilience:
    lifegain = life_cost = protection = recursion = death = 0
    for card in cards:
        text = card.oracle_text or ""
        if not text:
            continue
        if _LIFEGAIN_RE.search(text):
            lifegain += card.quantity
        if _LIFECOST_RE.search(text):
            life_cost += card.quantity
        if _PROTECTION_RE.search(text):
            protection += card.quantity
        if _RECURSION_RE.search(text):
            recursion += card.quantity
        if _DEATH_TRIGGER_RE.search(text):
            death += card.quantity

    return Resilience(
        lifegain_sources=lifegain,
        life_as_resource=life_cost,
        active_protection=protection,
        graveyard_recursion=recursion,
        death_triggers=death,
    )


def count_taplands(cards: list[EnrichedCard]) -> int:
    """Taplands incondicionales: 'enters tapped' sin 'unless'/'pay 2 life'."""
    taps = 0
    for card in cards:
        if not card.is_land:
            continue
        text = card.oracle_text or ""
        if _TAPLAND_RE.search(text) and not _TAPLAND_COND_RE.search(text):
            taps += card.quantity
    return taps


# --------------------------------------------------------------------------- #
# Agregado
# --------------------------------------------------------------------------- #
@dataclass
class DeckAnalysis:
    curve: ManaCurve
    balance: ManaBalance
    roles: RoleIndex
    consistency: Consistency
    acceleration: Acceleration
    combat: CombatClock
    resilience: Resilience
    taplands: int
    total_cards: int
    total_lands: int
    total_value_usd: float
    commander: str | None = None


def analyze(
    cards: list[EnrichedCard],
    deck_size: int | None = None,
    commander: str | None = None,
) -> DeckAnalysis:
    total_cards = sum(c.quantity for c in cards)
    size = deck_size or max(total_cards, 1)

    curve = compute_curve(cards)
    balance = compute_mana_balance(cards)
    roles = classify_roles(cards)
    acceleration = compute_acceleration(cards)
    combat = compute_combat_clock(cards)
    resilience = compute_resilience(cards)
    taplands = count_taplands(cards)
    consistency = compute_consistency(
        cards, roles, acceleration, deck_size=size
    )
    total_value = round(
        sum((c.price_usd or 0.0) * c.quantity for c in cards), 2
    )

    return DeckAnalysis(
        curve=curve,
        balance=balance,
        roles=roles,
        consistency=consistency,
        acceleration=acceleration,
        combat=combat,
        resilience=resilience,
        taplands=taplands,
        total_cards=total_cards,
        total_lands=balance.total_lands,
        total_value_usd=total_value,
        commander=commander,
    )
