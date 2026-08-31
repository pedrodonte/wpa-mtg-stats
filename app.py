"""
MTG Telemetry Analyzer — Entrypoint Streamlit + PWA.

Flujo: Carga → Procesamiento (Scryfall batch) → Visualización y Exportación.
Ejecutar con:  streamlit run app.py
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

from modules.analyzer import COLOR_NAMES, COLORS, analyze
from modules.parser import parse_decklist, total_cards
from modules.report_builder import build_llm_report, build_report
from modules.scryfall_client import ScryfallCache, enrich_cards

BASE_DIR = Path(__file__).resolve().parent

# Plantilla sugerida para el campo de estrategia (placeholder del formulario).
STRATEGY_TEMPLATE = """## Estrategia y Plan de Juego

- **Arquetipo Principal:** [Ej. Aristocrats / Graveyard Landfall / Artifact Combo]
- **Motor Principal (Engine):** [Cómo genera ventaja el mazo.]
- **Condiciones de Victoria (Wincons):**
  1. *Plan A (Primario):* [...]
  2. *Plan B (Alternativo):* [...]
  3. *Plan C (Combo / Explosivo):* [...]
- **Cartas Sagradas (Core / Intocables):** [3 a 6 cartas clave que nunca se cortan.]
- **Ejes de Sinergia Críticos:**
  - *Disparadores clave:* [...]
  - *Combustible:* [...]"""


def get_app_version() -> str:
    """Versión del build (APP_VERSION), formato yyyymmdd_hhmm.

    Prioriza la variable de entorno; si no está, la lee del `.env` del
    proyecto. Devuelve 'dev' si no hay ninguna definida.
    """
    version = os.environ.get("APP_VERSION")
    if version:
        return version
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("APP_VERSION="):
                return line.split("=", 1)[1].strip().strip('"').strip("'") or "dev"
    return "dev"

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
    <meta name="theme-color" content="#00FF41">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    """
    st.markdown(pwa_tags, unsafe_allow_html=True)


def inject_theme() -> None:
    """Tema Matrix: fondo casi negro, verde neón y fuente monoespaciada."""
    css = """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;800&display=swap');

      /* Fuente de código en toda la app */
      html, body, [class*="css"], .stMarkdown, .stMetric,
      button, input, textarea, .stDataFrame {
        font-family: 'JetBrains Mono', ui-monospace, 'Cascadia Code',
                     Consolas, monospace !important;
      }

      /* Título con brillo verde estilo terminal */
      .block-container h1:first-of-type {
        color: #00FF41;
        text-shadow: 0 0 8px rgba(0,255,65,0.55);
        border-bottom: 2px solid #00FF41;
        padding-bottom: 0.35rem;
        letter-spacing: 0.5px;
      }
      h2, h3, h4 { color: #39FF14 !important; }

      /* Métricas: valor en verde neón con leve glow */
      [data-testid="stMetricValue"] {
        color: #00FF41;
        text-shadow: 0 0 6px rgba(0,255,65,0.45);
      }
      [data-testid="stMetricLabel"] { color: #7CFF9B !important; }

      /* Pestaña activa en verde */
      .stTabs [aria-selected="true"] { color: #00FF41 !important; }
      .stTabs [data-baseweb="tab-highlight"] { background-color: #00FF41 !important; }

      /* Botón primario estilo terminal */
      .stButton > button[kind="primary"] {
        background: #00FF41; border: none; color: #05140A; font-weight: 800;
        box-shadow: 0 0 10px rgba(0,255,65,0.4);
      }
      .stButton > button {
        border: 1px solid #1f5f2f; color: #39FF14; background: #0F1A0F;
      }
      /* Barra de progreso verde */
      .stProgress > div > div > div > div { background-color: #00FF41; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def copy_button(
    text: str,
    label: str = "📋 Copiar al portapapeles",
    key: str = "md",
) -> None:
    """Botón JS de un toque para copiar texto al portapapeles.

    ``key`` distingue instancias cuando hay varios botones en la página.
    """
    payload = json.dumps(text)
    label_js = json.dumps(label)
    btn_id = f"copy-{key}"
    html = f"""
    <button id="{btn_id}" style="
        width:100%;padding:0.65rem 1rem;border:1px solid #00FF41;border-radius:0.5rem;
        background:#00FF41;color:#05140A;font-size:1rem;font-weight:800;
        font-family:'JetBrains Mono',monospace;cursor:pointer;
        box-shadow:0 0 10px rgba(0,255,65,0.4);">
        {label}
    </button>
    <script>
    (function() {{
        const btn = document.getElementById({json.dumps(btn_id)});
        const label = {label_js};
        btn.addEventListener('click', async () => {{
            try {{
                await navigator.clipboard.writeText({payload});
                btn.innerText = '✅ Copiado';
                setTimeout(() => btn.innerText = label, 1800);
            }} catch (e) {{
                btn.innerText = '⚠️ No se pudo copiar';
            }}
        }});
    }})();
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
    st.session_state.setdefault("commander", None)
    st.session_state.setdefault("llm_md", None)


def run_pipeline(raw_text: str, deck_size: int, strategy: str = "") -> None:
    cards, errors, commander = parse_decklist(raw_text)
    if not cards:
        st.error("No se pudieron parsear cartas. Verifica el formato de la lista.")
        return
    if errors:
        with st.expander(f"⚠️ {len(errors)} línea(s) no reconocida(s)"):
            st.code("\n".join(errors))

    # El nombre del mazo se deriva del comandante detectado.
    deck_name = commander or "Mi Mazo"

    st.info(f"Parseadas {len(cards)} entradas · {total_cards(cards)} copias totales.")

    progress = st.progress(0.0, text="Iniciando…")
    log = st.empty()

    def cb(frac: float, msg: str) -> None:
        progress.progress(frac, text=msg)
        log.caption(msg)

    cache = ScryfallCache()
    enriched, not_found = enrich_cards(cards, cache=cache, progress_cb=cb)
    progress.progress(1.0, text="Analizando…")

    analysis = analyze(enriched, deck_size=deck_size, commander=commander)
    report_md = build_report(enriched, analysis, deck_name=deck_name, strategy=strategy)
    llm_md = build_llm_report(enriched, analysis, deck_name=deck_name, strategy=strategy)

    st.session_state.report_md = report_md
    st.session_state.llm_md = llm_md
    st.session_state.analysis = analysis
    st.session_state.enriched = enriched
    st.session_state.not_found = not_found
    st.session_state.deck_name = deck_name
    st.session_state.commander = commander
    progress.empty()
    log.empty()


# --------------------------------------------------------------------------- #
# Vistas
# --------------------------------------------------------------------------- #
def render_upload() -> None:
    st.subheader("1 · Carga tu mazo")
    st.caption("Exporta desde ManaBox como texto plano, o pega la lista directamente.")

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

    strategy = st.text_area(
        "Estrategia y plan de juego (opcional)",
        height=220,
        help="Se incluye tal cual en el reporte. Admite Markdown; útil como "
             "contexto para el análisis con IA.",
        placeholder=STRATEGY_TEMPLATE,
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
            run_pipeline(raw_text, int(deck_size), strategy.strip())


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
    commander = getattr(analysis, "commander", None) or st.session_state.get("commander")
    if commander:
        st.markdown(f"**👑 Comandante:** {commander}")
    else:
        st.caption("👑 Comandante no detectado (marca `// COMMANDER` en la lista).")
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
    copy_button(report_md, "📋 Copiar reporte", key="report")

    llm_md = st.session_state.get("llm_md") or report_md
    copy_button(
        llm_md,
        "🤖 Copiar con prompt para IA",
        key="llm",
    )
    st.caption(
        "Incluye instrucciones para analizar el mazo en un LLM (Gemini, ChatGPT…)."
    )

    st.download_button(
        "⬇️ Descargar Markdown (.md)",
        data=report_md.encode("utf-8"),
        file_name=_export_filename(
            st.session_state.get("commander") or st.session_state.deck_name
        ),
        mime="text/markdown",
        use_container_width=True,
    )

    st.divider()
    if st.button("🔄 Procesar un nuevo mazo", use_container_width=True):
        reset_analysis()
        st.rerun()


def reset_analysis() -> None:
    """Limpia el resultado actual para empezar con un mazo nuevo."""
    st.session_state.report_md = None
    st.session_state.analysis = None
    st.session_state.enriched = None
    st.session_state.not_found = []
    st.session_state.deck_name = "Mi Mazo"
    st.session_state.commander = None
    st.session_state.llm_md = None


def _slug(name: str) -> str:
    keep = [c.lower() if c.isalnum() else "-" for c in name]
    slug = "".join(keep).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "mtg-report"


def _first_word(name: str) -> str:
    """Primera palabra del nombre: corta en el primer espacio, punto o coma."""
    for sep in (" ", ".", ","):
        name = name.split(sep, 1)[0]
    return name.strip()


def _export_filename(name: str, now: datetime | None = None) -> str:
    """Nombre del .md: {comandante}_{yyyy}_{dia_del_año}.md.

    Solo se usa la primera palabra del comandante (hasta el primer espacio,
    punto o coma). 'día del año' es el ordinal 1-366 (day-of-year).
    Ej: 'Teval, the Balanced Scale' -> 'teval_2026_241.md'.
    """
    now = now or datetime.now()
    year = now.year
    day_of_year = now.timetuple().tm_yday
    return f"{_slug(_first_word(name))}_{year}_{day_of_year}.md"


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    init_state()
    inject_pwa()
    inject_theme()

    st.title("🎴 MTG Telemetry Analyzer")
    st.caption(
        f"Analiza mazos de Magic desde ManaBox · métricas + reporte para LLMs. "
        f"· versión {get_app_version()}"
    )

    render_upload()
    st.divider()
    render_results()


if __name__ == "__main__":
    main()
