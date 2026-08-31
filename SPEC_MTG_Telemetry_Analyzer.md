# Especificación Técnica de Producto (Spec)
## Proyecto: MTG Telemetry Analyzer (Streamlit PWA)

**Versión:** 1.0.0  
**Fecha:** 2026-08-28  
**Autor:** Pedro Carrasco Curín  
**Target:** Web / Progressive Web App (PWA) / AWS Cloud  

---

## 1. Resumen Ejecutivo y Objetivos

El objetivo de este proyecto es construir una aplicación web ligera, móvil y de alto rendimiento utilizando **Streamlit**, optimizada para ser ejecutada y anclada como **PWA (Progressive Web App)** en dispositivos móviles (Android / iOS). 

La herramienta permite procesar exportaciones de listas de mazos de *Magic: The Gathering* generadas desde **ManaBox**, enriquecer los metadatos de las cartas consultando la API de **Scryfall** por lotes (*batch requests*), computar métricas estadísticas avanzadas de consistencia de maná y roles tácticos, y exportar un reporte en formato **Markdown (.md)** optimizado tanto para lectura humana como para ser utilizado como prompt/input estructurado en modelos de lenguaje (LLMs como Gemini).

---

## 2. Arquitectura de la Solución

```
┌────────────────────────┐
│ Archivo ManaBox (.txt) │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│     Parser Module      │ ──► Extracción: Qty, Name, Set, CN
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐      ┌─────────────────────────┐
│ Scryfall Batch Client  │ ◄──► │ Caché Local (.json/DB)  │
└───────────┬────────────┘      └─────────────────────────┘
            │ (Enriquecimiento JSON)
            ▼
┌────────────────────────┐
│    Analytics Engine    │ ──► Curva de Maná, PIPs vs Fuentes,
└───────────┬────────────┘     Probabilidades Hipergeométricas, Roles
            │
            ▼
┌────────────────────────┐
│  Markdown & UI Output  │ ──► Render Web, Copiar Portapapeles,
└────────────────────────┘     Descarga .md para LLM
```

---

## 3. Especificación Funcional de Módulos

### Módulo 1: Parser de ManaBox (`parser.py`)
- **Entrada:** Archivo de texto plano exportado desde ManaBox o texto pegado desde portapapeles.
- **Expresión Regular de Parsing:**
  ```regex
  ^(?P<qty>\d+)\s+(?P<name>.+?)(?:\s+\((?P<set>[A-Za-z0-9]+)\)\s+(?P<cn>[A-Za-z0-9]+))?(?:\s+\*F\*)?$
  ```
- **Salida:** Lista de objetos estructurados `CardInput`:
  - `quantity: int`
  - `name: str`
  - `set: str | None`
  - `collector_number: str | None`

---

### Módulo 2: Cliente Scryfall Batch & Caché (`scryfall_client.py`)
- **Endpoint:** `POST https://api.scryfall.com/cards/collection`
- **Lotes (Batching):** Agrupación máxima de 75 cartas por petición HTTP para minimizar latencia de red (reducción de ~100 peticiones a solo 2).
- **Control de Rate Limiting:** Pausa mandatoria de 100 ms entre lotes.
- **Caché Persistente:** Almacenamiento local indexado por `nombre_normalizado` y `set_cn` para evitar llamadas redundantes a Scryfall.
- **Atributos a extraer y normalizar:**
  - `name`, `mana_cost`, `cmc`, `type_line`, `oracle_text`, `colors`, `produced_mana`, `power`, `toughness`, `prices.usd`.

---

### Módulo 3: Motor Analítico y Métricas (`analyzer.py`)

#### 1. Curva y CMC Promedio
- Conteo de cartas por CMC entero (0 a 7+), omitiendo tierras (`Land` en `type_line`).
- Cálculo de CMC Promedio:
  $$	ext{CMC}_{	ext{avg}} = \frac{\sum (\text{CMC}_i \times \text{Qty}_i)}{\text{Total No Tierras}}$$

#### 2. Balance de Maná (PIPs Requeridos vs. Fuentes de Tierras)
- Extracción de símbolos de coste coloreados en hechizos: `{W}`, `{U}`, `{B}`, `{R}`, `{G}`, `{C}`.
- Conteo de fuentes disponibles mapeadas desde `produced_mana` y subtipos de tierras básicas.
- Cálculo de ratio de cobertura: $\text{Ratio} = \frac{\text{Fuentes Disponibles}}{\text{PIPs Requeridos}}$.

#### 3. Consistencia Hipergeométrica
Cálculo de probabilidad acumulada $P(X \ge k)$ para estimar la consistencia de robo en turnos tempranos:
$$P(X \ge k) = \sum_{x=k}^{n} \frac{\binom{K}{x} \binom{N-K}{n-x}}{\binom{N}{n}}$$
- **Parámetros evaluados:**
  - $P(\ge 3 \text{ tierras en T3}): N=99, K=\text{Total Tierras}, n=9, k=3$.
  - $P(\ge 1 \text{ pieza de Ramp en Mano Inicial}): N=99, K=\text{Total Ramp}, n=7, k=1$.

#### 4. Clasificación Heurística de Roles Tácticos
Categorización automatizada mediante análisis de patrones en `oracle_text` y `type_line`:

| Rol Táctico | Patrón Regex / Condición |
| :--- | :--- |
| **Ramp / Fixing** | `add (one mana\|\{[wubrgc]\})`, `search your library.*land` (no tierras) |
| **Card Advantage** | `draw (a\|two\|three\|\d+) card`, `discover \d+`, `investigate` |
| **Single Removal** | `(destroy\|exile) target` |
| **Board Wipe** | `(destroy\|exile) all`, `each nonartifact creature` |
| **Proliferate** | `proliferate` |
| **Charge Synergies** | `charge counter` |
| **Protection / Counter**| `hexproof`, `indestructible`, `ward`, `counter target spell` |
| **Cost Reducers** | Improvisar (`improvise`), Afinidad (`affinity for \w+`, cualquier tipo), Convocar (`convoke`), Dragar (`delve`) y reducción de costes de maná: `cost(s) \{N\} less` (incl. híbridos), `cost(s) \{X\} less`, `cost(s) up to \{N\} less`, `cost(s) less to cast` |
| **Karnstruct Engine** | `create a 0/0.*construct` |

---

### Módulo 4: Generador de Reporte Markdown (`report_builder.py`)
Genera un archivo `.md` estructurado en dos secciones principales:
1. **Resumen Ejecutivo y Métricas Estadísticas:**
   - Tabla ASCII de curva de maná.
   - Tabla de balance de color y ratios de cobertura.
   - Distribución de roles tácticos con cartas clave.
   - Probabilidades hipergeométricas calculadas.
2. **Manifiesto Detallado de Cartas:**
   - Listado normalizado (`### Carta (xCantidad)`) con CMC, coste, tipo y texto Oracle compactado en una sola línea para maximizar eficiencia de tokens en LLMs.

---

## 4. Diseño de Interfaz y Experiencia de Usuario (Streamlit UI)

- **Diseño Mobile-First:** Ancho centrado (`layout="centered"`), fuentes legibles y controles adaptados a pantalla táctil.
- **Flujo de Pantallas:**
  1. **Carga:** Selector de archivo (`st.file_uploader`) para `.txt` con opción de pegar texto y definir nombre/estrategia.
  2. **Procesamiento:** Barra de progreso interactiva (`st.progress`) con log en tiempo real.
  3. **Visualización y Exportación:**
     - Tarjetas de métricas principales (`st.metric`).
     - Pestañas interactivas: *Estadísticas*, *Roles Tácticos*, *Vista Previa MD*.
     - Botón de un toque para **Copiar al Portapapeles** (mediante componente JS).
     - Botón de **Descarga directa** del archivo Markdown (`st.download_button`).

---

## 5. Configuración PWA (Progressive Web App)

### Inyección de Metadatos HTML (`st.markdown`)
```python
pwa_tags = """
<link rel="manifest" href="./manifest.json">
<meta name="theme-color" content="#1E1E1E">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
"""
st.markdown(pwa_tags, unsafe_allow_html=True)
```

### Manifiesto PWA (`manifest.json`)
```json
{
  "short_name": "MTGAnalyzer",
  "name": "MTG Telemetry Analyzer",
  "icons": [
    {
      "src": "/static/icon-192.png",
      "type": "image/png",
      "sizes": "192x192"
    },
    {
      "src": "/static/icon-512.png",
      "type": "image/png",
      "sizes": "512x512"
    }
  ],
  "start_url": "/",
  "background_color": "#0E1117",
  "theme_color": "#1E1E1E",
  "display": "standalone",
  "orientation": "portrait"
}
```

---

## 6. Estructura del Proyecto

```
mtg-telemetry-analyzer/
├── app.py                     # Entrypoint de Streamlit y UI
├── manifest.json              # Configuración PWA
├── requirements.txt           # Dependencias (streamlit>=1.35.0)
├── modules/
│   ├── __init__.py
│   ├── parser.py              # Parsing de listas ManaBox
│   ├── scryfall_client.py     # Cliente Scryfall Batch + Caché
│   ├── analyzer.py            # Métricas, Hipergeométrica y Roles
│   └── report_builder.py      # Generador de Markdown
├── static/
│   ├── icon-192.png
│   └── icon-512.png
└── README.md
```

---

## 7. Criterios de Aceptación

1. **Eficiencia en Red:** El procesamiento de un mazo de 100 cartas no debe requerir más de 2 peticiones HTTP a Scryfall.
2. **Resiliencia Offline/Caché:** Si las cartas ya existen en la caché local, el tiempo de procesamiento total debe ser inferior a 200 ms.
3. **PWA Instalable:** La aplicación debe permitir agregarse como icono independiente en la pantalla de inicio de navegadores móviles (Chrome Android / Safari iOS).
4. **Calidad de Salida para LLM:** El Markdown generado debe incluir toda la semántica del mazo estructurada sin pérdidas de información para un análisis fluido en Gemini.
