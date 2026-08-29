"""
Módulo 4: Generador de reporte Markdown optimizado para LLMs.

Estructura:
  1. Resumen ejecutivo y métricas (curva, balance, roles, hipergeométrica).
  2. Manifiesto detallado de cartas (una línea por carta, tokens compactos).
"""

from __future__ import annotations

import re
from datetime import datetime

from .analyzer import COLOR_NAMES, COLORS, DeckAnalysis
from .scryfall_client import EnrichedCard

_WS_RE = re.compile(r"\s+")


def _compact(text: str) -> str:
    """Compacta oracle_text a una sola línea para eficiencia de tokens."""
    if not text:
        return "—"
    return _WS_RE.sub(" ", text.replace("\n", " ")).strip()


def _bar(value: int, max_value: int, width: int = 20) -> str:
    if max_value <= 0:
        return ""
    filled = round(width * value / max_value)
    return "█" * filled + "·" * (width - filled)


def build_curve_section(analysis: DeckAnalysis) -> str:
    curve = analysis.curve
    max_v = max(curve.buckets.values()) if curve.buckets else 0
    lines = [
        "### Curva de Maná",
        "",
        f"- **CMC Promedio (sin tierras):** {curve.avg_cmc}",
        f"- **Hechizos (no tierras):** {curve.total_nonland}",
        "",
        "| CMC | Cartas | Distribución |",
        "| :-: | :----: | :----------- |",
    ]
    for key, count in curve.buckets.items():
        lines.append(f"| {key} | {count} | `{_bar(count, max_v)}` |")
    return "\n".join(lines)


def build_balance_section(analysis: DeckAnalysis) -> str:
    b = analysis.balance
    lines = [
        "### Balance de Maná (Intensidad de PIPs vs. Fuentes)",
        "",
        f"- **Tierras totales:** {b.total_lands}",
        "",
        "| Color | PIPs Requeridos | Fuentes | Ratio | Diagnóstico |",
        "| :---- | :-------------: | :-----: | :---: | :---------- |",
    ]
    for color in COLORS:
        req = b.pips_required.get(color, 0)
        src = b.sources_available.get(color, 0)
        if req == 0 and src == 0:
            continue
        ratio = b.coverage_ratio.get(color)
        ratio_str = "N/A" if ratio is None else f"{ratio}"
        diag = b.diagnosis.get(color, "N/A")
        lines.append(
            f"| {color} ({COLOR_NAMES[color]}) | {req} | {src} | {ratio_str} | {diag} |"
        )
    return "\n".join(lines)


def _examples(names: list[str], limit: int = 4) -> str:
    if not names:
        return ""
    sample = ", ".join(names[:limit]) + ("…" if len(names) > limit else "")
    return f" (Ej: {sample})"


def build_telemetry_section(analysis: DeckAnalysis) -> str:
    """Sección v2: Métricas Cuantitativas y Telemetría (spect_metricas.v2.md §4)."""
    acc = analysis.acceleration
    cc = analysis.combat
    res = analysis.resilience
    c = analysis.consistency

    lines = [
        "## Métricas Cuantitativas y Telemetría",
        "",
        "### Aceleración y Recursos",
        f"- **Artefactos de Maná (Mana Rocks):** {acc.mana_rocks} copias"
        f"{_examples(acc.rocks_examples)}",
        f"- **Criaturas de Maná (Mana Dorks):** {acc.mana_dorks} copias"
        f"{_examples(acc.dorks_examples)}",
        f"- **Motores de Creación de Fichas:** {acc.token_producers} cartas"
        f"{_examples(acc.token_examples)}",
        "",
        "### Capacidad Ofensiva (Combat Clock)",
        f"- **Poder Total Base en Criaturas:** {cc.total_power}",
        f"- **Criaturas con Evasión:** {cc.evasion_count}",
        f"- **Habilitadores de Prisa (Haste):** {cc.haste_count}",
        f"- **Poder Promedio / Criatura:** {cc.avg_power_per_creature:.2f}",
        f"- **Índice de Reloj de Combate (CCI):** {cc.combat_clock_index:.2f}",
        f"- **Criaturas con Poder Dinámico (*/X):** {cc.dynamic_power_creatures}",
        "",
        "### Resiliencia y Sustento",
        f"- **Fuentes de Ganancia de Vida:** {res.lifegain_sources}",
        f"- **Consumidores de Vida como Recurso:** {res.life_as_resource}",
        f"- **Protección Activa (Hexproof/Indestructible/Ward/Counter):** {res.active_protection}",
        f"- **Recursión de Cementerio:** {res.graveyard_recursion}",
        f"- **Disparadores de Muerte (Death Triggers):** {res.death_triggers}",
        "",
        "### Consistencia de Base de Maná",
        f"- **Tierras Totales:** {c.total_lands} "
        f"(Lentas/Taplands incondicionales: {analysis.taplands})",
        f"- **P(≥3 tierras en T3 - 9 cartas):** {c.p_lands_t3 * 100:.1f}%",
        f"- **P(≥1 Ramp en mano inicial - 7 cartas):** {c.p_ramp_opening * 100:.1f}%",
    ]
    return "\n".join(lines)


def build_roles_section(analysis: DeckAnalysis) -> str:
    roles = analysis.roles
    lines = ["### Roles Tácticos", ""]
    if not roles.counts:
        lines.append("_No se detectaron roles tácticos por heurística._")
        return "\n".join(lines)

    lines += ["| Rol | Copias | Cartas Clave |", "| :-- | :----: | :----------- |"]
    for role, count in sorted(roles.counts.items(), key=lambda kv: kv[1], reverse=True):
        cards = roles.cards_by_role.get(role, [])
        sample = ", ".join(cards[:6]) + (" …" if len(cards) > 6 else "")
        lines.append(f"| {role} | {count} | {sample} |")
    return "\n".join(lines)


def build_consistency_section(analysis: DeckAnalysis) -> str:
    c = analysis.consistency
    return "\n".join(
        [
            "### Consistencia Hipergeométrica",
            "",
            f"- **Tamaño de mazo evaluado (N):** {c.deck_size}",
            f"- **P(≥3 tierras al turno 3, ver 9 cartas):** {c.p_lands_t3 * 100:.1f}%",
            f"- **P(≥1 pieza de Ramp en mano inicial, 7 cartas):** {c.p_ramp_opening * 100:.1f}%",
            f"- **Tierras totales (K tierras):** {c.total_lands}",
            f"- **Piezas de Ramp (K ramp):** {c.total_ramp}",
        ]
    )


def build_summary(analysis: DeckAnalysis, deck_name: str, strategy: str) -> str:
    header = [
        f"# {deck_name}",
        "",
        f"> Reporte generado por **MTG Telemetry Analyzer** — {datetime.now():%Y-%m-%d %H:%M}",
        "",
    ]
    if analysis.commander:
        header += [f"**Comandante:** {analysis.commander}", ""]
    if strategy:
        header += [f"**Estrategia:** {strategy}", ""]
    header += [
        "## 1. Resumen Ejecutivo y Métricas Estadísticas",
        "",
        f"- **Comandante:** {analysis.commander or '—'}",
        f"- **Cartas totales:** {analysis.total_cards}",
        f"- **Tierras:** {analysis.total_lands}",
        f"- **CMC Promedio:** {analysis.curve.avg_cmc}",
        f"- **Valor estimado (USD):** ${analysis.total_value_usd:.2f}",
        "",
    ]
    return "\n".join(header)


def build_manifest(cards: list[EnrichedCard]) -> str:
    lines = [
        "## 2. Manifiesto Detallado de Cartas",
        "",
        "_Formato compacto: coste, CMC, tipo y texto Oracle en una línea._",
        "",
    ]
    # Orden: no tierras por CMC, luego tierras; alfabético como desempate.
    ordered = sorted(
        cards,
        key=lambda c: (c.is_land, c.cmc, c.name.lower()),
    )
    for card in ordered:
        if not card.found:
            lines.append(f"### {card.name} (x{card.quantity})")
            lines.append("- ⚠️ No encontrada en Scryfall.")
            lines.append("")
            continue
        cost = card.mana_cost or "—"
        pt = ""
        if card.power is not None and card.toughness is not None:
            pt = f" | P/T: {card.power}/{card.toughness}"
        lines.append(f"### {card.name} (x{card.quantity})")
        lines.append(
            f"- {cost} | CMC {int(card.cmc)} | {card.type_line}{pt} | "
            f"Oracle: {_compact(card.oracle_text)}"
        )
        lines.append("")
    return "\n".join(lines)


def build_report(
    cards: list[EnrichedCard],
    analysis: DeckAnalysis,
    deck_name: str = "Mazo sin nombre",
    strategy: str = "",
) -> str:
    """Ensambla el reporte Markdown completo."""
    sections = [
        build_summary(analysis, deck_name, strategy),
        build_curve_section(analysis),
        "",
        build_balance_section(analysis),
        "",
        build_roles_section(analysis),
        "",
        build_consistency_section(analysis),
        "",
        "---",
        "",
        build_telemetry_section(analysis),
        "",
        "---",
        "",
        build_manifest(cards),
    ]
    return "\n".join(sections).strip() + "\n"


# Bloque de instrucciones para pegar en un LLM (Gemini, ChatGPT, etc.).
LLM_PROMPT_HEADER = """\
# INSTRUCCIONES PARA EL MODELO DE IA

> Actúa como un analista competitivo de MTG Commander.
> Analiza la telemetría y el "Manifiesto de Cartas" adjunto.
>
> REGLAS OBLIGATORIAS:
> 1. Antes de sugerir una adición, verifica exhaustivamente que NO esté en el Manifiesto.
> 2. Justifica cada corte/adición usando las métricas (PIPs, CCI, CMC, Hipergeométrica, Resiliencia).
> 3. Entrega: Diagnóstico de Maná, Top 3 Cortes con justificación, Top 3 Adiciones \
(formato "Carta A entra por Carta B") y Power Level estimado (1-10).

---
"""


def build_llm_prompt() -> str:
    """Bloque de instrucciones para anteponer al reporte al pegarlo en un LLM."""
    return LLM_PROMPT_HEADER


def build_llm_report(
    cards: list[EnrichedCard],
    analysis: DeckAnalysis,
    deck_name: str = "Mazo sin nombre",
    strategy: str = "",
) -> str:
    """Reporte completo precedido del prompt de instrucciones para el LLM."""
    report = build_report(cards, analysis, deck_name=deck_name, strategy=strategy)
    return f"{build_llm_prompt()}\n{report}"
