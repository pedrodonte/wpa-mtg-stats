"""
Módulo: Collection & Binder Processor.

Extiende MTG Telemetry Analyzer para analizar inventarios físicos exportados
desde ManaBox (álbumes/cajas temáticas: "Carpeta Naranja", "Caja Negra"...).

A diferencia del análisis de mazo (que optimiza un grupo de 99/60 cartas), este
módulo consolida múltiples contenedores físicos y extrae toda la información
posible de la colección:

  - Trazabilidad física multicontenedor (qué copia vive en qué caja/carpeta).
  - Reparto por color, tipo, rareza y set.
  - Curva de maná global, roles tácticos y telemetría (reutiliza analyzer.py).
  - Top de cartas por valor y valor total en USD.
  - Catálogo Markdown denso "Zero-Buy" optimizado para LLMs.

Dos formatos de entrada soportados:
  - **Texto** (export por mazo/lista): un archivo por contenedor; el contenedor
    se deriva del nombre del archivo (ManaBox no incluye metadatos ahí).
  - **CSV** (export "Collection" completo de ManaBox): un único archivo con
    todos los contenedores. Incluye ``Binder Name`` (contenedor real),
    ``Set code``, ``Collector number``, ``Rarity``, ``Quantity``, ``Foil``,
    ``Condition``, ``Purchase price``, etc.
"""

from __future__ import annotations

import csv
import io
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from .analyzer import (
    COLOR_NAMES,
    COLORS,
    DeckAnalysis,
    analyze,
)
from .parser import CardInput, parse_decklist
from .scryfall_client import EnrichedCard

_WS_RE = re.compile(r"\s+")

# Orden canónico de tipos primarios (para reparto por tipo).
_PRIMARY_TYPES = [
    ("Battle", "battle"),
    ("Planeswalker", "planeswalker"),
    ("Creature", "creature"),
    ("Instant", "instant"),
    ("Sorcery", "sorcery"),
    ("Artifact", "artifact"),
    ("Enchantment", "enchantment"),
    ("Land", "land"),
]

_RARITY_ORDER = ["mythic", "rare", "uncommon", "common", "special", "bonus"]
_RARITY_LABELS = {
    "mythic": "Mítica",
    "rare": "Rara",
    "uncommon": "Infrecuente",
    "common": "Común",
    "special": "Especial",
    "bonus": "Bonus",
}


def _compact(text: str) -> str:
    """Compacta oracle_text a una sola línea para eficiencia de tokens."""
    if not text:
        return "—"
    return _WS_RE.sub(" ", text.replace("\n", " ")).strip()


def container_name_from_filename(filename: str) -> str:
    """Deriva el nombre del contenedor físico desde el nombre de archivo.

    'caja negra.txt' -> 'Caja Negra'; 'Carpeta_Naranja.txt' -> 'Carpeta Naranja'.
    """
    base = re.sub(r"\.(txt|csv)$", "", filename.strip(), flags=re.I)
    base = base.replace("_", " ").replace("-", " ")
    base = _WS_RE.sub(" ", base).strip()
    return base.title() if base else "Contenedor"


# --------------------------------------------------------------------------- #
# Modelo de datos
# --------------------------------------------------------------------------- #
@dataclass
class BinderFile:
    """Un archivo de export de ManaBox con su contenedor derivado."""

    filename: str
    raw_text: str

    @property
    def container(self) -> str:
        return container_name_from_filename(self.filename)


@dataclass
class CollectionCard:
    """Carta consolidada de la colección con trazabilidad por contenedor."""

    card: EnrichedCard
    # contenedor -> copias en ese contenedor
    locations: dict[str, int] = field(default_factory=dict)

    @property
    def total_quantity(self) -> int:
        return sum(self.locations.values())

    @property
    def total_value(self) -> float:
        return (self.card.price_usd or 0.0) * self.total_quantity


@dataclass
class CollectionAnalysis:
    """Resultado agregado del análisis de colección."""

    containers: list[str]
    total_unique: int
    total_copies: int
    total_value_usd: float
    by_color: dict[str, int]
    by_type: dict[str, int]
    by_rarity: dict[str, int]
    by_set: dict[str, int]
    by_container: dict[str, int]  # contenedor -> copias
    top_value: list[tuple[str, float, int]]  # (nombre, precio_unit, copias)
    deck_analysis: DeckAnalysis
    cards: list[CollectionCard]
    not_found: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Parsing multi-contenedor
# --------------------------------------------------------------------------- #
def parse_binders(
    binders: list[BinderFile],
) -> tuple[list[CardInput], dict[str, dict[str, int]], list[str]]:
    """Parsea múltiples archivos de ManaBox.

    Devuelve:
      - ``inputs``: lista única de ``CardInput`` (deduplicada por clave), con la
        cantidad total sumada entre contenedores (para enriquecer una sola vez).
      - ``locations``: mapa ``clave_carta -> {contenedor: copias}``.
      - ``errors``: líneas no reconocidas (prefijadas con el contenedor).
    """
    merged: dict[str, CardInput] = {}
    locations: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    errors: list[str] = []

    for binder in binders:
        container = binder.container
        cards, file_errors, _commander = parse_decklist(binder.raw_text)
        for err in file_errors:
            errors.append(f"[{container}] {err}")
        for c in cards:
            key = c.key
            locations[key][container] += c.quantity
            if key in merged:
                merged[key].quantity += c.quantity
            else:
                # Copia para no mutar la instancia original del parser.
                merged[key] = CardInput(
                    quantity=c.quantity,
                    name=c.name,
                    set=c.set,
                    collector_number=c.collector_number,
                )

    # Normalizar defaultdicts a dicts planos.
    flat_locations = {k: dict(v) for k, v in locations.items()}
    return list(merged.values()), flat_locations, errors


# --------------------------------------------------------------------------- #
# Parsing del CSV de colección de ManaBox
# --------------------------------------------------------------------------- #
# Precios de compra por clave de carta (opcionales; sobreescriben el de mercado).
CsvPurchasePrices = dict


def parse_manabox_csv(
    raw_text: str,
) -> tuple[list[CardInput], dict[str, dict[str, int]], list[str], dict[str, float]]:
    """Parsea el CSV "Collection" exportado por ManaBox.

    A diferencia del export de texto, el CSV es un único archivo con TODOS los
    contenedores (columna ``Binder Name``) y metadatos ricos.

    Devuelve:
      - ``inputs``: lista única de ``CardInput`` (deduplicada por ``set:cn``),
        con la cantidad total sumada entre contenedores.
      - ``locations``: mapa ``clave_carta -> {contenedor: copias}``.
      - ``errors``: filas no interpretables (con índice de fila).
      - ``purchase_prices``: mapa ``clave_carta -> precio de compra unitario``
        (promedio ponderado si la carta aparece varias veces).
    """
    merged: dict[str, CardInput] = {}
    locations: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    errors: list[str] = []
    # Acumuladores para promedio ponderado de precio de compra.
    price_sum: dict[str, float] = defaultdict(float)
    price_qty: dict[str, int] = defaultdict(int)

    reader = csv.DictReader(io.StringIO(raw_text))
    if reader.fieldnames is None:
        return [], {}, ["CSV vacío o sin encabezado."], {}

    # Normaliza nombres de columna (tolerante a mayúsculas/espacios).
    def col(row: dict, name: str) -> str:
        return (row.get(name) or "").strip()

    for i, row in enumerate(reader, start=2):  # fila 2 = primera de datos
        name = col(row, "Name")
        if not name:
            errors.append(f"Fila {i}: sin nombre de carta.")
            continue

        try:
            qty = int(col(row, "Quantity") or "1")
        except ValueError:
            qty = 1
        if qty <= 0:
            qty = 1

        set_code = col(row, "Set code") or None
        cn = col(row, "Collector number") or None
        container = col(row, "Binder Name") or "Sin contenedor"

        card = CardInput(
            quantity=qty, name=name, set=set_code, collector_number=cn
        )
        key = card.key

        locations[key][container] += qty
        if key in merged:
            merged[key].quantity += qty
        else:
            merged[key] = card

        # Precio de compra (opcional).
        raw_price = col(row, "Purchase price")
        if raw_price:
            try:
                price = float(raw_price)
                price_sum[key] += price * qty
                price_qty[key] += qty
            except ValueError:
                pass

    flat_locations = {k: dict(v) for k, v in locations.items()}
    purchase_prices = {
        k: round(price_sum[k] / price_qty[k], 2)
        for k in price_sum
        if price_qty[k] > 0
    }
    return list(merged.values()), flat_locations, errors, purchase_prices


# --------------------------------------------------------------------------- #
# Agregación
# --------------------------------------------------------------------------- #
def _primary_type(type_line: str) -> str:
    low = (type_line or "").lower()
    for label, needle in _PRIMARY_TYPES:
        if needle in low:
            return label
    return "Otro"


def build_collection_analysis(
    enriched: list[EnrichedCard],
    inputs: list[CardInput],
    locations: dict[str, dict[str, int]],
    containers: list[str],
    not_found: list[str] | None = None,
    purchase_prices: dict[str, float] | None = None,
) -> CollectionAnalysis:
    """Consolida enriquecimiento + trazabilidad en un ``CollectionAnalysis``.

    ``enriched`` e ``inputs`` deben estar alineados por índice (mismo orden que
    devuelve ``enrich_cards`` para la lista ``inputs``).

    ``purchase_prices`` (opcional, del CSV de ManaBox): mapa ``clave -> precio``
    que se usa como respaldo cuando Scryfall no reporta precio de mercado.
    """
    purchase_prices = purchase_prices or {}
    by_color: dict[str, int] = {c: 0 for c in COLORS}
    by_type: dict[str, int] = defaultdict(int)
    by_rarity: dict[str, int] = defaultdict(int)
    by_set: dict[str, int] = defaultdict(int)
    by_container: dict[str, int] = defaultdict(int)
    cards: list[CollectionCard] = []

    for card, inp in zip(enriched, inputs):
        loc = locations.get(inp.key, {})
        qty = sum(loc.values()) or card.quantity

        # Respaldo de precio: usar el precio de compra del CSV si Scryfall no lo dio.
        if (card.price_usd is None or card.price_usd == 0.0) and inp.key in purchase_prices:
            card.price_usd = purchase_prices[inp.key]

        cards.append(CollectionCard(card=card, locations=loc))

        for container, copies in loc.items():
            by_container[container] += copies

        # Reparto por color (incoloro si no tiene colores).
        if card.colors:
            for color in card.colors:
                if color in by_color:
                    by_color[color] += qty
        else:
            by_color["C"] += qty

        by_type[_primary_type(card.type_line)] += qty
        by_rarity[(card.rarity or "desconocida").lower()] += qty
        set_label = card.set_name or (card.set.upper() if card.set else "Desconocido")
        by_set[set_label] += qty

    total_copies = sum(c.total_quantity for c in cards)
    total_value = round(sum(c.total_value for c in cards), 2)

    top_value = sorted(
        (
            (c.card.name, c.card.price_usd or 0.0, c.total_quantity)
            for c in cards
            if (c.card.price_usd or 0.0) > 0
        ),
        key=lambda t: t[1],
        reverse=True,
    )[:15]

    # Reutiliza el motor de análisis de mazo sobre toda la colección.
    deck_analysis = analyze(enriched, deck_size=max(total_copies, 1))

    return CollectionAnalysis(
        containers=containers,
        total_unique=len(cards),
        total_copies=total_copies,
        total_value_usd=total_value,
        by_color=dict(by_color),
        by_type=dict(by_type),
        by_rarity=dict(by_rarity),
        by_set=dict(by_set),
        by_container=dict(by_container),
        top_value=top_value,
        deck_analysis=deck_analysis,
        cards=cards,
        not_found=not_found or [],
    )


# --------------------------------------------------------------------------- #
# Catálogo Markdown "Zero-Buy"
# --------------------------------------------------------------------------- #
ZERO_BUY_PROMPT = """\
# INSTRUCCIONES PARA EL MODELO DE IA — DIRECTIVA "ZERO-BUY"

> Actúa como un asesor de construcción de mazos de MTG Commander.
> El siguiente documento es el **catálogo de mi colección física** (cartas que
> ya poseo, organizadas por contenedor).
>
> REGLAS OBLIGATORIAS:
> 1. Para cualquier sugerencia de mejora, reemplazo o construcción, usa
>    **única y exclusivamente cartas presentes en este catálogo**.
> 2. NO propongas adquirir cartas externas salvo que declares explícitamente
>    que la colección no cubre una necesidad concreta, y solo como último recurso.
> 3. Al proponer una carta, cita el contenedor físico donde se encuentra
>    (columna "Ubicación") para facilitar su localización.
> 4. Prioriza sinergias detectables en la telemetría (roles, aceleración,
>    resiliencia) y respeta la identidad de color del comandante objetivo.

---
"""


def _dist_table(title: str, rows: list[tuple[str, int]], total: int) -> str:
    lines = [f"### {title}", "", "| Categoría | Copias | % |", "| :-- | :-: | :-: |"]
    for label, count in rows:
        pct = (count / total * 100) if total else 0.0
        lines.append(f"| {label} | {count} | {pct:.1f}% |")
    return "\n".join(lines)


def build_collection_report(
    analysis: CollectionAnalysis,
    title: str = "Colección MTG",
) -> str:
    """Ensambla el catálogo Markdown completo de la colección."""
    da = analysis.deck_analysis
    sections: list[str] = []

    # Cabecera.
    header = [
        f"# {title}",
        "",
        f"> Catálogo de colección generado por **MTG Telemetry Analyzer** — "
        f"{datetime.now():%Y-%m-%d %H:%M}",
        "",
        "## 1. Resumen de la Colección",
        "",
        f"- **Contenedores:** {len(analysis.containers)} "
        f"({', '.join(analysis.containers)})",
        f"- **Cartas únicas:** {analysis.total_unique}",
        f"- **Copias totales:** {analysis.total_copies}",
        f"- **Valor estimado (USD):** ${analysis.total_value_usd:.2f}",
        f"- **CMC promedio (sin tierras):** {da.curve.avg_cmc}",
    ]
    sections.append("\n".join(header))

    # Reparto por contenedor.
    cont_rows = sorted(analysis.by_container.items(), key=lambda kv: kv[1], reverse=True)
    sections.append(_dist_table("Reparto por Contenedor", cont_rows, analysis.total_copies))

    # Reparto por color.
    color_rows = [
        (f"{c} · {COLOR_NAMES[c]}", analysis.by_color.get(c, 0))
        for c in COLORS
        if analysis.by_color.get(c, 0) > 0
    ]
    sections.append(_dist_table("Reparto por Color", color_rows, analysis.total_copies))

    # Reparto por tipo.
    type_rows = sorted(analysis.by_type.items(), key=lambda kv: kv[1], reverse=True)
    sections.append(_dist_table("Reparto por Tipo", type_rows, analysis.total_copies))

    # Reparto por rareza (orden canónico).
    rar_rows = [
        (_RARITY_LABELS.get(r, r.title()), analysis.by_rarity[r])
        for r in _RARITY_ORDER
        if analysis.by_rarity.get(r, 0) > 0
    ]
    for r, count in analysis.by_rarity.items():
        if r not in _RARITY_ORDER:
            rar_rows.append((r.title(), count))
    sections.append(_dist_table("Reparto por Rareza", rar_rows, analysis.total_copies))

    # Reparto por set (top 15).
    set_rows = sorted(analysis.by_set.items(), key=lambda kv: kv[1], reverse=True)[:15]
    sections.append(_dist_table("Reparto por Set (Top 15)", set_rows, analysis.total_copies))

    # Curva de maná.
    curve_lines = ["### Curva de Maná", "", "| CMC | Cartas |", "| :-: | :-: |"]
    for key, count in da.curve.buckets.items():
        curve_lines.append(f"| {key} | {count} |")
    sections.append("\n".join(curve_lines))

    # Roles tácticos agregados.
    roles = da.roles
    if roles.counts:
        role_lines = ["### Roles Tácticos", "", "| Rol | Copias | Ejemplos |", "| :-- | :-: | :-- |"]
        for role, count in sorted(roles.counts.items(), key=lambda kv: kv[1], reverse=True):
            ex = roles.cards_by_role.get(role, [])
            sample = ", ".join(ex[:5]) + (" …" if len(ex) > 5 else "")
            role_lines.append(f"| {role} | {count} | {sample} |")
        sections.append("\n".join(role_lines))

    # Telemetría resumida.
    acc = da.acceleration
    cc = da.combat
    res = da.resilience
    tel = [
        "### Telemetría",
        "",
        f"- **Mana Rocks:** {acc.mana_rocks} · **Mana Dorks:** {acc.mana_dorks} · "
        f"**Motores de Fichas:** {acc.token_producers}",
        f"- **Poder total en criaturas:** {cc.total_power} · "
        f"**Evasión:** {cc.evasion_count} · **Haste:** {cc.haste_count}",
        f"- **Ganancia de vida:** {res.lifegain_sources} · "
        f"**Protección activa:** {res.active_protection} · "
        f"**Recursión:** {res.graveyard_recursion} · "
        f"**Death triggers:** {res.death_triggers}",
    ]
    sections.append("\n".join(tel))

    # Top de cartas por valor.
    if analysis.top_value:
        val_lines = [
            "### Top 15 Cartas por Valor (USD)",
            "",
            "| Carta | Precio unit. | Copias |",
            "| :-- | :-: | :-: |",
        ]
        for name, price, copies in analysis.top_value:
            val_lines.append(f"| {name} | ${price:.2f} | {copies} |")
        sections.append("\n".join(val_lines))

    # Manifiesto denso con trazabilidad.
    sections.append(_build_collection_manifest(analysis))

    body = "\n\n".join(sections).strip() + "\n"
    return body


def _location_str(locations: dict[str, int]) -> str:
    if not locations:
        return "—"
    parts = [
        f"{cont} (x{copies})" if copies > 1 else cont
        for cont, copies in sorted(locations.items())
    ]
    return "; ".join(parts)


def _build_collection_manifest(analysis: CollectionAnalysis) -> str:
    lines = [
        "## 2. Manifiesto Detallado de la Colección",
        "",
        "_Formato compacto: coste, CMC, tipo, rareza, texto Oracle y ubicación física._",
        "",
    ]
    ordered = sorted(
        analysis.cards,
        key=lambda cc: (cc.card.is_land, cc.card.cmc, cc.card.name.lower()),
    )
    for cc in ordered:
        card = cc.card
        loc = _location_str(cc.locations)
        if not card.found:
            lines.append(f"### {card.name} (x{cc.total_quantity})")
            lines.append(f"- ⚠️ No encontrada en Scryfall. | Ubicación: {loc}")
            lines.append("")
            continue
        cost = card.mana_cost or "—"
        pt = ""
        if card.power is not None and card.toughness is not None:
            pt = f" | P/T: {card.power}/{card.toughness}"
        rarity = _RARITY_LABELS.get((card.rarity or "").lower(), card.rarity or "—")
        lines.append(f"### {card.name} (x{cc.total_quantity})")
        lines.append(
            f"- {cost} | CMC {int(card.cmc)} | {card.type_line}{pt} | "
            f"Rareza: {rarity} | Set: {card.set.upper()} | "
            f"Ubicación: {loc}"
        )
        lines.append(f"  - Oracle: {_compact(card.oracle_text)}")
        lines.append("")
    return "\n".join(lines)


def build_collection_llm_report(
    analysis: CollectionAnalysis,
    title: str = "Colección MTG",
) -> str:
    """Catálogo precedido del prompt de instrucciones Zero-Buy para LLMs."""
    report = build_collection_report(analysis, title=title)
    return f"{ZERO_BUY_PROMPT}\n{report}"


# --------------------------------------------------------------------------- #
# Nombre de archivo de exportación
# --------------------------------------------------------------------------- #
def _slug(name: str) -> str:
    keep = [c.lower() if c.isalnum() else "-" for c in name]
    slug = "".join(keep).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "coleccion"


def collection_export_filename(
    filenames: list[str],
    now: datetime | None = None,
) -> str:
    """Nombre del .md de colección con prefijo 'coleccion-mtg_'.

    - 1 archivo:  coleccion-mtg_<nombre-archivo>.md
    - varios:     coleccion-mtg_consolidada_<yyyy>_<dia_del_año>.md
    """
    now = now or datetime.now()
    if len(filenames) == 1:
        base = re.sub(r"\.(txt|csv)$", "", filenames[0].strip(), flags=re.I)
        return f"coleccion-mtg_{_slug(base)}.md"
    day_of_year = now.timetuple().tm_yday
    return f"coleccion-mtg_consolidada_{now.year}_{day_of_year}.md"
