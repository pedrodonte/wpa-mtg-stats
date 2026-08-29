"""
MTG Telemetry Analyzer — Entrypoint Streamlit + PWA.

Flujo: Carga → Procesamiento (Scryfall batch) → Visualización y Exportación.
Ejecutar con:  streamlit run app.py
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from modules.analyzer import COLOR_NAMES, COLORS, analyze
from modules.parser import parse_decklist, total_cards
from modules.report_builder import build_report
from modules.scryfall_client import ScryfallCache, enrich_cards

BASE_DIR = Path(__file__).resolve().parent

# --------------------------------------------------------------------------- #
# Configuración de página (mobile-first)
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="MTG Telemetry Analyzer",
    page_icon="🎴",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def inject_pwa() -> None:
    """Inyecta metadatos PWA y viewport móvil."""
    pwa_tags = """
    <link rel="manifest" href="./app/static/manifest.json">
    <meta name="theme-color" content="#E8493B">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    """
    st.markdown(pwa_tags, unsafe_allow_html=True)


def inject_theme() -> None:
    """Estilo Jeskai (W/U/R): barra de acento tricolor y detalles de UI."""
    css = """
    <style>
      /* Barra de acento Jeskai bajo el encabezado */
      .block-container h1:first-of-type {
        border-bottom: 4px solid transparent;
        border-image: linear-gradient(90deg,#F5F3E7 0%,#3B7DD8 50%,#E8493B 100%) 1;
        padding-bottom: 0.35rem;
      }
      /* Métricas: valor en rojo Jeskai */
      [data-testid="stMetricValue"] { color: #E8493B; }
      /* Pestaña activa subrayada en azul */
      .stTabs [aria-selected="true"] { color: #3B7DD8 !important; }
      .stTabs [data-baseweb="tab-highlight"] { background-color: #3B7DD8 !important; }
      /* Botón primario con degradado Jeskai */
      .stButton > button[kind="primary"] {
        background: linear-gradient(90deg,#3B7DD8 0%,#E8493B 100%);
        border: none; color: #F5F3E7; font-weight: 600;
      }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def copy_button(text: str, label: str = "📋 Copiar al portapapeles") -> None:
    """Botón JS de un toque para copiar Markdown al portapapeles."""
    payload = json.dumps(text)
    html = f"""
    <button id="copy-md" style="
        width:100%;padding:0.65rem 1rem;border:none;border-radius:0.5rem;
        background:linear-gradient(90deg,#F5F3E7 0%,#3B7DD8 50%,#E8493B 100%);
        color:#0B1220;font-size:1rem;font-weight:600;cursor:pointer;">
        {label}
    </button>
    <script>
    const btn = document.getElementById('copy-md');
    btn.addEventListener('click', async () => {{
        try {{
            await navigator.clipboard.writeText({payload});
            btn.innerText = '✅ Copiado';
            setTimeout(() => btn.innerText = '{label}', 1800);
        }} catch (e) {{
            btn.innerText = '⚠️ No se pudo copiar';
        }}
    }});
    </script>
    """
    st.components.v1.html(html, height=60)


# --------------------------------------------------------------------------- #
# Estado
# --------------------------------------------------------------------------- #
def init_state() -> None:
    st.session_state.setdefault("report_md", None)
    st.session_state.setdefault("analysis", None)
    st.session_state.setdefault("enriched", None)
    st.session_state.setdefault("not_found", [])
    st.session_state.setdefault("deck_name", "Mi Mazo")


def run_pipeline(raw_text: str, deck_name: str, strategy: str, deck_size: int) -> None:
    cards, errors = parse_decklist(raw_text)
    if not cards:
        st.error("No se pudieron parsear cartas. Verifica el formato de la lista.")
        return
    if errors:
        with st.expander(f"⚠️ {len(errors)} línea(s) no reconocida(s)"):
            st.code("\n".join(errors))

    st.info(f"Parseadas {len(cards)} entradas · {total_cards(cards)} copias totales.")

    progress = st.progress(0.0, text="Iniciando…")
    log = st.empty()

    def cb(frac: float, msg: str) -> None:
        progress.progress(frac, text=msg)
        log.caption(msg)

    cache = ScryfallCache()
    enriched, not_found = enrich_cards(cards, cache=cache, progress_cb=cb)
    progress.progress(1.0, text="Analizando…")

    analysis = analyze(enriched, deck_size=deck_size)
    report_md = build_report(enriched, analysis, deck_name=deck_name, strategy=strategy)

    st.session_state.report_md = report_md
    st.session_state.analysis = analysis
    st.session_state.enriched = enriched
    st.session_state.not_found = not_found
    st.session_state.deck_name = deck_name
    progress.empty()
    log.empty()


# --------------------------------------------------------------------------- #
# Vistas
# --------------------------------------------------------------------------- #
def render_upload() -> None:
    st.subheader("1 · Carga tu mazo")
    st.caption("Exporta desde ManaBox como texto plano, o pega la lista directamente.")

    deck_name = st.text_input("Nombre del mazo", value=st.session_state.deck_name)
    strategy = st.text_input("Estrategia (opcional)", placeholder="Ej: Artefactos / Karnstructs")
    deck_size = st.number_input(
        "Tamaño del mazo (N para hipergeométrica)",
        min_value=40, max_value=250, value=99, step=1,
        help="99 para Commander, 60 para formatos construidos.",
    )

    uploaded = st.file_uploader("Archivo .txt de ManaBox", type=["txt"])
    pasted = st.text_area(
        "…o pega la lista aquí",
        height=180,
        placeholder="1 Sol Ring (C21) 250\n1 Karn, the Great Creator (WAR) 1\n35 Mountain",
    )

    raw_text = ""
    if uploaded is not None:
        raw_text = uploaded.read().decode("utf-8", errors="ignore")
    elif pasted.strip():
        raw_text = pasted

    if st.button("🚀 Procesar mazo", type="primary", use_container_width=True):
        if not raw_text.strip():
            st.warning("Sube un archivo o pega una lista primero.")
        else:
            run_pipeline(raw_text, deck_name.strip() or "Mi Mazo", strategy.strip(), int(deck_size))


def render_metrics(analysis) -> None:
    c1, c2, c3 = st.columns(3)
    c1.metric("Cartas", analysis.total_cards)
    c2.metric("Tierras", analysis.total_lands)
    c3.metric("CMC prom.", analysis.curve.avg_cmc)
    c4, c5, c6 = st.columns(3)
    c4.metric("P(≥3 tierras T3)", f"{analysis.consistency.p_lands_t3 * 100:.0f}%")
    c5.metric("Índice CCI", f"{analysis.combat.combat_clock_index:.1f}")
    c6.metric("Valor USD", f"${analysis.total_value_usd:.0f}")


def render_stats_tab(analysis) -> None:
    st.markdown("#### Curva de Maná")
    st.bar_chart(
        {"Cartas": analysis.curve.buckets},
        use_container_width=True,
    )

    st.markdown("#### Balance de Color (Intensidad de PIPs)")
    rows = []
    for color in COLORS:
        req = analysis.balance.pips_required.get(color, 0)
        src = analysis.balance.sources_available.get(color, 0)
        if req == 0 and src == 0:
            continue
        ratio = analysis.balance.coverage_ratio.get(color)
        rows.append(
            {
                "Color": f"{color} · {COLOR_NAMES[color]}",
                "PIPs": req,
                "Fuentes": src,
                "Ratio": "N/A" if ratio is None else ratio,
                "Diagnóstico": analysis.balance.diagnosis.get(color, "N/A"),
            }
        )
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)

    st.markdown("#### Consistencia Hipergeométrica")
    st.write(
        f"- P(≥3 tierras al T3, 9 cartas): **{analysis.consistency.p_lands_t3 * 100:.1f}%**"
    )
    st.write(
        f"- P(≥1 ramp en mano inicial, 7 cartas): **{analysis.consistency.p_ramp_opening * 100:.1f}%**"
    )


def render_roles_tab(analysis) -> None:
    roles = analysis.roles
    if not roles.counts:
        st.info("No se detectaron roles tácticos por heurística.")
        return
    for role, count in sorted(roles.counts.items(), key=lambda kv: kv[1], reverse=True):
        with st.expander(f"{role} — {count} copias"):
            st.write(", ".join(roles.cards_by_role.get(role, [])))


def render_telemetry_tab(analysis) -> None:
    acc = analysis.acceleration
    cc = analysis.combat
    res = analysis.resilience

    st.markdown("#### 🚀 Aceleración y Recursos")
    a1, a2, a3 = st.columns(3)
    a1.metric("Mana Rocks", acc.mana_rocks)
    a2.metric("Mana Dorks", acc.mana_dorks)
    a3.metric("Motores de Fichas", acc.token_producers)
    if acc.rocks_examples:
        st.caption("Rocks: " + ", ".join(acc.rocks_examples[:6]))
    if acc.dorks_examples:
        st.caption("Dorks: " + ", ".join(acc.dorks_examples[:6]))
    if acc.token_examples:
        st.caption("Fichas: " + ", ".join(acc.token_examples[:6]))

    st.markdown("#### ⚔️ Capacidad Ofensiva (Combat Clock)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Poder Total", cc.total_power)
    c2.metric("Evasión", cc.evasion_count)
    c3.metric("Haste", cc.haste_count)
    c4, c5 = st.columns(2)
    c4.metric("Poder / Criatura", f"{cc.avg_power_per_creature:.2f}")
    c5.metric("Índice CCI", f"{cc.combat_clock_index:.2f}")
    if cc.dynamic_power_creatures:
        st.caption(f"Criaturas con poder dinámico (*/X): {cc.dynamic_power_creatures}")

    st.markdown("#### 🛡️ Resiliencia y Sustento")
    r1, r2, r3 = st.columns(3)
    r1.metric("Ganancia de Vida", res.lifegain_sources)
    r2.metric("Vida como Recurso", res.life_as_resource)
    r3.metric("Protección Activa", res.active_protection)
    r4, r5 = st.columns(2)
    r4.metric("Recursión Cementerio", res.graveyard_recursion)
    r5.metric("Death Triggers", res.death_triggers)

    st.markdown("#### 🌐 Base de Maná")
    total_lands = analysis.total_lands
    tap_pct = (analysis.taplands / total_lands * 100) if total_lands else 0.0
    b1, b2 = st.columns(2)
    b1.metric("Tierras Totales", total_lands)
    b2.metric("Taplands (lentas)", f"{analysis.taplands} · {tap_pct:.0f}%")


def render_results() -> None:
    analysis = st.session_state.analysis
    report_md = st.session_state.report_md
    if analysis is None or report_md is None:
        return

    st.subheader(f"2 · {st.session_state.deck_name}")
    render_metrics(analysis)

    if st.session_state.not_found:
        with st.expander(f"⚠️ {len(st.session_state.not_found)} carta(s) no encontrada(s)"):
            st.code("\n".join(st.session_state.not_found))

    tab_stats, tab_tel, tab_roles, tab_md = st.tabs(
        ["📊 Estadísticas", "📡 Telemetría", "🎯 Roles Tácticos", "📄 Vista Previa MD"]
    )
    with tab_stats:
        render_stats_tab(analysis)
    with tab_tel:
        render_telemetry_tab(analysis)
    with tab_roles:
        render_roles_tab(analysis)
    with tab_md:
        st.markdown(report_md)

    st.divider()
    st.subheader("3 · Exportar")
    copy_button(report_md)
    st.download_button(
        "⬇️ Descargar Markdown (.md)",
        data=report_md.encode("utf-8"),
        file_name=f"{_slug(st.session_state.deck_name)}.md",
        mime="text/markdown",
        use_container_width=True,
    )


def _slug(name: str) -> str:
    keep = [c.lower() if c.isalnum() else "-" for c in name]
    slug = "".join(keep).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "mtg-report"


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    init_state()
    inject_pwa()
    inject_theme()

    st.title("🎴 MTG Telemetry Analyzer")
    st.caption("Estilo Jeskai ⚪🔵🔴 · Analiza mazos de Magic desde ManaBox · métricas + reporte para LLMs.")

    render_upload()
    st.divider()
    render_results()


if __name__ == "__main__":
    main()
