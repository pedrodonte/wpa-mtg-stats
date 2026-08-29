# 🎴 MTG Telemetry Analyzer

Aplicación web ligera y **PWA** construida con **Streamlit** para analizar mazos de
*Magic: The Gathering* exportados desde **ManaBox**. Enriquece las cartas vía la API
**batch** de Scryfall, calcula métricas de consistencia de maná y roles tácticos, y
exporta un reporte **Markdown** optimizado como prompt para LLMs (Gemini, etc.).

Desplegada en: `https://wpa-mtg-stats.streamlit.app/`

## Características

- **Parser ManaBox**: lee `.txt` exportado o texto pegado (`4 Sol Ring (C21) 250 *F*`).
- **Cliente Scryfall Batch + Caché**: lotes de 75 cartas por petición, pausa de 100 ms
  entre lotes y caché JSON persistente (`.cache/`) para respuestas casi instantáneas.
- **Motor analítico**:
  - Curva de maná y CMC promedio (excluye tierras).
  - Balance de PIPs coloreados requeridos vs. fuentes de tierras (ratio de cobertura).
  - Consistencia hipergeométrica: P(≥3 tierras al T3), P(≥1 ramp en mano inicial).
  - Clasificación heurística de roles tácticos (ramp, card advantage, removal, wipes…).
- **Reporte Markdown** en dos secciones: resumen de métricas + manifiesto de cartas
  con texto Oracle compactado a una línea para eficiencia de tokens.
- **PWA instalable** en Android/iOS con manifest e iconos.

## Requisitos

- Python **3.10+** (probado con 3.11).

## Instalación y ejecución (Windows / PowerShell)

```powershell
# 1. Crear y activar entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # si falla: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. (opcional) Regenerar iconos PWA
python tools\gen_icons.py

# 4. Levantar la app
streamlit run app.py
```

Abre `http://localhost:8501`. Para instalarla como PWA en móvil, abre la URL de red
en Chrome/Safari y usa "Agregar a pantalla de inicio".

En macOS/Linux la activación del entorno es `source .venv/bin/activate` y las rutas
usan `/` (`python tools/gen_icons.py`).

## Estructura

```
mtg-telemetry-analyzer/
├── app.py                 # Entrypoint Streamlit + UI + PWA
├── manifest.json          # Manifiesto PWA
├── requirements.txt
├── .streamlit/config.toml # Static serving + tema oscuro
├── modules/
│   ├── parser.py          # Parsing de listas ManaBox
│   ├── scryfall_client.py # Cliente Scryfall batch + caché
│   ├── analyzer.py        # Curva, balance, hipergeométrica, roles
│   └── report_builder.py  # Generador de Markdown
├── static/                # manifest.json + iconos servidos por Streamlit
└── tools/gen_icons.py     # Generador de iconos PWA (stdlib)
```

## Notas

- La caché se guarda en `.cache/scryfall_cache.json`. Bórrala para forzar
  reconsultas a Scryfall.
- El tamaño de mazo (N) es configurable en la UI: 99 para Commander, 60 para
  formatos construidos. Alimenta los cálculos hipergeométricos.
