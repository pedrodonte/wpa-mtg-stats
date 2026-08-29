"""
Módulo 2: Cliente Scryfall Batch + Caché persistente.

- Endpoint batch: POST https://api.scryfall.com/cards/collection (máx. 75 ids/petición).
- Rate limiting: pausa de 100 ms entre lotes (política de Scryfall: 50-100ms).
- Caché en disco (JSON) indexada por nombre normalizado y por set:cn.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

import requests

from .parser import CardInput

SCRYFALL_COLLECTION_URL = "https://api.scryfall.com/cards/collection"
BATCH_SIZE = 75
RATE_LIMIT_SECONDS = 0.1
DEFAULT_CACHE_PATH = Path(__file__).resolve().parent.parent / ".cache" / "scryfall_cache.json"

_ATTRIBUTES = (
    "name",
    "mana_cost",
    "cmc",
    "type_line",
    "oracle_text",
    "colors",
    "produced_mana",
    "power",
    "toughness",
)


def _normalize_name(name: str) -> str:
    return name.strip().lower()


def _card_key(set_code: str | None, cn: str | None) -> str | None:
    if set_code and cn:
        return f"{set_code.lower()}:{cn.lower()}"
    return None


def _extract_attributes(raw: dict) -> dict:
    """Extrae y normaliza los atributos relevantes de un objeto Scryfall.

    Maneja cartas de doble cara (``card_faces``) fusionando texto y coste.
    """
    faces = raw.get("card_faces") or []

    def face_get(field_name: str) -> str:
        parts = [f.get(field_name, "") for f in faces if f.get(field_name)]
        return " // ".join(parts)

    mana_cost = raw.get("mana_cost")
    if not mana_cost and faces:
        mana_cost = face_get("mana_cost")

    oracle_text = raw.get("oracle_text")
    if not oracle_text and faces:
        oracle_text = face_get("oracle_text")

    type_line = raw.get("type_line") or (face_get("type_line") if faces else "")

    price = None
    prices = raw.get("prices") or {}
    if prices.get("usd"):
        try:
            price = float(prices["usd"])
        except (TypeError, ValueError):
            price = None

    return {
        "name": raw.get("name", ""),
        "mana_cost": mana_cost or "",
        "cmc": float(raw.get("cmc", 0.0) or 0.0),
        "type_line": type_line or "",
        "oracle_text": oracle_text or "",
        "colors": raw.get("colors") or [],
        "produced_mana": raw.get("produced_mana") or [],
        "power": raw.get("power"),
        "toughness": raw.get("toughness"),
        "price_usd": price,
    }


@dataclass
class EnrichedCard:
    """Carta de entrada + metadatos enriquecidos de Scryfall."""

    quantity: int
    name: str
    mana_cost: str = ""
    cmc: float = 0.0
    type_line: str = ""
    oracle_text: str = ""
    colors: list[str] = field(default_factory=list)
    produced_mana: list[str] = field(default_factory=list)
    power: str | None = None
    toughness: str | None = None
    price_usd: float | None = None
    found: bool = True

    @property
    def is_land(self) -> bool:
        return "land" in self.type_line.lower()


class ScryfallCache:
    """Caché JSON persistente indexada por nombre normalizado y set:cn."""

    def __init__(self, path: Path | str = DEFAULT_CACHE_PATH):
        self.path = Path(path)
        self._by_name: dict[str, dict] = {}
        self._by_setcn: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                self._by_name = data.get("by_name", {})
                self._by_setcn = data.get("by_setcn", {})
            except (json.JSONDecodeError, OSError):
                self._by_name, self._by_setcn = {}, {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"by_name": self._by_name, "by_setcn": self._by_setcn}
        self.path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def get(self, card: CardInput) -> dict | None:
        key = _card_key(card.set, card.collector_number)
        if key and key in self._by_setcn:
            return self._by_setcn[key]
        return self._by_name.get(_normalize_name(card.name))

    def put(self, attrs: dict, set_code: str | None = None, cn: str | None = None) -> None:
        name = _normalize_name(attrs.get("name", ""))
        if name:
            self._by_name[name] = attrs
        key = _card_key(set_code, cn)
        if key:
            self._by_setcn[key] = attrs


def _build_identifier(card: CardInput) -> dict:
    if card.set and card.collector_number:
        return {"set": card.set.lower(), "collector_number": card.collector_number}
    return {"name": card.name}


def enrich_cards(
    cards: list[CardInput],
    cache: ScryfallCache | None = None,
    progress_cb: Callable[[float, str], None] | None = None,
    session: requests.Session | None = None,
) -> tuple[list[EnrichedCard], list[str]]:
    """Enriquece la lista de cartas usando caché + peticiones batch a Scryfall.

    ``progress_cb(fraction, message)`` se invoca para reportar avance.
    Devuelve ``(cartas_enriquecidas, no_encontradas)``.
    """
    cache = cache or ScryfallCache()
    owns_session = session is None
    session = session or requests.Session()
    session.headers.update({"User-Agent": "MTGTelemetryAnalyzer/1.0", "Accept": "application/json"})

    enriched: list[EnrichedCard] = []
    not_found: list[str] = []

    def report(frac: float, msg: str) -> None:
        if progress_cb:
            progress_cb(max(0.0, min(1.0, frac)), msg)

    # 1) Resolver desde caché; acumular los que faltan.
    misses: list[CardInput] = []
    cached_attrs: dict[int, dict] = {}
    for idx, card in enumerate(cards):
        hit = cache.get(card)
        if hit is not None:
            cached_attrs[idx] = hit
        else:
            misses.append(card)

    report(0.15, f"Caché: {len(cached_attrs)} aciertos, {len(misses)} por consultar.")

    # 2) Consultar los faltantes en lotes de 75.
    fetched_by_key: dict[str, dict] = {}
    if misses:
        batches = list(_chunks(misses, BATCH_SIZE))
        for b_idx, batch in enumerate(batches):
            identifiers = [_build_identifier(c) for c in batch]
            try:
                resp = session.post(
                    SCRYFALL_COLLECTION_URL,
                    json={"identifiers": identifiers},
                    timeout=30,
                )
                resp.raise_for_status()
                payload = resp.json()
            except (requests.RequestException, ValueError) as exc:
                report(0.15, f"Error de red en lote {b_idx + 1}: {exc}")
                payload = {"data": [], "not_found": identifiers}

            for raw in payload.get("data", []):
                attrs = _extract_attributes(raw)
                cache.put(attrs, raw.get("set"), raw.get("collector_number"))
                fetched_by_key[_normalize_name(attrs["name"])] = attrs
                sc_key = _card_key(raw.get("set"), raw.get("collector_number"))
                if sc_key:
                    fetched_by_key[sc_key] = attrs

            for nf in payload.get("not_found", []):
                not_found.append(nf.get("name") or f"{nf.get('set')}:{nf.get('collector_number')}")

            report(
                0.15 + 0.75 * (b_idx + 1) / len(batches),
                f"Lote {b_idx + 1}/{len(batches)} procesado.",
            )
            if b_idx < len(batches) - 1:
                time.sleep(RATE_LIMIT_SECONDS)

        cache.save()

    # 3) Ensamblar resultado en el orden original.
    for idx, card in enumerate(cards):
        attrs = cached_attrs.get(idx)
        if attrs is None:
            key = _card_key(card.set, card.collector_number)
            attrs = (key and fetched_by_key.get(key)) or fetched_by_key.get(_normalize_name(card.name))
        if attrs is None:
            enriched.append(EnrichedCard(quantity=card.quantity, name=card.name, found=False))
            continue
        enriched.append(
            EnrichedCard(
                quantity=card.quantity,
                name=attrs.get("name", card.name),
                mana_cost=attrs.get("mana_cost", ""),
                cmc=float(attrs.get("cmc", 0.0) or 0.0),
                type_line=attrs.get("type_line", ""),
                oracle_text=attrs.get("oracle_text", ""),
                colors=list(attrs.get("colors", [])),
                produced_mana=list(attrs.get("produced_mana", [])),
                power=attrs.get("power"),
                toughness=attrs.get("toughness"),
                price_usd=attrs.get("price_usd"),
                found=True,
            )
        )

    report(1.0, "Enriquecimiento completado.")
    if owns_session:
        session.close()
    return enriched, not_found


def _chunks(seq: list, size: int) -> Iterable[list]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]
