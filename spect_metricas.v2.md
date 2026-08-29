---

## 3. Especificación de Extracción y Fórmulas Matemáticas

### 3.1. Aceleración de Maná y Creación de Fichas (Tokens)

Las cartas se clasifican analizando conjuntamente los campos `type_line` y `oracle_text`:

| Métrica | Condición de Tipo (`type_line`) | Expresión Regular (`oracle_text`) |
| :--- | :--- | :--- |
| **Mana Dorks (Criaturas de Maná)** | `Creature` en `type_line` y `Land` NOT in `type_line` | `r"add (one mana\|\\{[wubrgc]\\})"` |
| **Mana Rocks (Artefactos de Maná)**| `Artifact` en `type_line` y `Creature` NOT in `type_line` y `Land` NOT in `type_line` | `r"add (one mana\|\\{[wubrgc]\\})"` |
| **Token Producers (Motores de Fichas)**| Cualquier tipo | `r"\\b(create|creates)\\b\\s+(?:.*?)token"` |

---

### 3.2. Capacidad Ofensiva (Combat Clock & Evasion)

Mide la presión en mesa, la velocidad de daño y la capacidad de evadir bloqueadores:

1. **Poder Total Base ($P_{\\text{total}}$):**
   $$P_{\\text{total}} = \\sum_{i \\in \\text{Criaturas}} (\\text{power}_i \\times \\text{quantity}_i)$$
   *(Si el valor de power contiene `*` o `X`, se computa como 0 para la base estática y se clasifica en motores dinámicos).*

2. **Criaturas con Evasión ($E_{\\text{count}}$):**
   - **Condición:** `Creature` en `type_line`
   - **Regex:** `r"\\b(flying|trample|deathtouch|can't be blocked|shadow|fear|intimidate|menace)\\b"`

3. **Habilitadores de Prisa / Ataque Inmediato ($H_{\\text{count}}$):**
   - **Regex:** `r"\\bhaste\\b"`

4. **Clasificación de Reloj de Combate (Combat Clock Index):**
   $$\\text{CCI} = \\frac{P_{\\text{total}}}{\\text{Total Criaturas}} + (E_{\\text{count}} \\times 0.5) + (H_{\\text{count}} \\times 0.75)$$

---

### 3.3. Resiliencia, Sustento y Gestión de Vida

Evalúa la durabilidad del mazo frente a interacción enemiga y el balance de vida:

| Submétrica | Patrón Regex (`oracle_text`) | Objetivo Analítico |
| :--- | :--- | :--- |
| **Fuentes de Ganancia de Vida** | `r"\\blifelink\\b\|gain \\d+ life\|whenever .* gain life"` | Estabilización y soporte |
| **Consumo de Vida como Recurso** | `r"pay \\d+ life\|lose \\d+ life"` | Detección de motores agresivos (ej. *Bolas's Citadel*) |
| **Protección Activa** | `r"\\b(hexproof\|indestructible\|ward)\\b\|counter target"` | Salvaguarda ante removals y wipes |
| **Recursión de Cementerio** | `r"return .* from your graveyard\|cast .* from your graveyard\|play lands from your graveyard"` | Capacidad de recuperación |
| **Disparadores de Muerte (Death Triggers)** | `r"whenever .* dies"` | Resiliencia de valor (Aristocrats / Tokens) |

---

### 3.4. Consistencia de Maná y Probabilidades

1. **Intensidad de PIPs Coloreados:**
   Para cada color $c \\in \\{W, U, B, R, G, C\\}$:
   $$\\text{PIPs}(c) = \\sum_{j \\in \\text{Hechizos}} \\text{conteo}(\\{c\\}, \\text{mana\\_cost}_j) \\times \\text{quantity}_j$$

2. **Ratio de Cobertura de Color:**
   $$\\text{Ratio}(c) = \\begin{cases} \\frac{\\text{Fuentes}(c)}{\\text{PIPs}(c)} & \\text{si } \\text{PIPs}(c) > 0 \\\\ \\text{N/A} & \\text{si } \\text{PIPs}(c) = 0 \\end{cases}$$
   - **Diagnóstico:**
     - $\\text{Ratio} \\ge 0.85 \\rightarrow \\text{🟢 Óptimo}$
     - $0.55 \\le \\text{Ratio} < 0.85 \\rightarrow \\text{🟡 Ajustado}$
     - $\\text{Ratio} < 0.55 \\rightarrow \\text{🔴 Déficit}$

3. **Velocidad de Tierras (Taplands Index):**
   - **Tapland incondicional:** `enters tapped` en `oracle_text` SIN coincidencia con `unless` o `pay 2 life`.
   - Ratio de lentitud: $\\frac{\\text{Taplands}}{\\text{Total Tierras}} \\times 100$.

4. **Probabilidad Hipergeométrica Acumulada ($P(X \\ge k)$):**
   $$P(X \\ge k) = \\sum_{x=k}^{\\min(n, K)} \\frac{\\binom{K}{x} \\binom{N-K}{n-x}}{\\binom{N}{n}}$$
   - **$N$:** 99 (1 Comandante) o 98 (Comandantes con *Partner*).
   - **Turno 3 (Maná Consistente):** $n = 9$ (7 iniciales + 2 robos), $k = 3$, $K = \\text{Total Tierras}$.
   - **Turno 1 (Ramp Temprano):** $n = 7$, $k = 1$, $K = \\text{Total Ramp (Rocks + Dorks + Spells)}$.

---

## 4. Estructura de Salida Requerida en Markdown

El generador debe estructurar las métricas de la siguiente forma antes del manifiesto de cartas:

```markdown
## Métricas Cuantitativas y Telemetría

### Aceleración y Recursos
- **Artefactos de Maná (Mana Rocks):** X copias (Ej: Sol Ring, Arcane Signet...)
- **Criaturas de Maná (Mana Dorks):** X copias (Ej: Birds of Paradise...)
- **Motores de Creación de Fichas:** X cartas

### Capacidad Ofensiva (Combat Clock)
- **Poder Total Base en Criaturas:** X
- **Criaturas con Evasión:** X
- **Habilitadores de Prisa (Haste):** X
- **Poder Promedio / CMC Criaturas:** X.XX

### Resiliencia y Sustento
- **Fuentes de Ganancia de Vida:** X
- **Consumidores de Vida como Recurso:** X
- **Protección Activa (Hexproof/Indestructible/Counter):** X
- **Recursión de Cementerio:** X
- **Disparadores de Muerte (Death Triggers):** X

### Consistencia de Base de Maná
- **Tierras Totales:** X (Lentas/Taplands incondicionales: X)
- **P(≥3 tierras en T3 - 9 cartas):** XX.X%
- **P(≥1 Ramp en mano inicial - 7 cartas):** XX.X%