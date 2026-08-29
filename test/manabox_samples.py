"""Listas de ManaBox simuladas para pruebas de input/output.

Reproducen el formato real exportado por ManaBox:
  - Comentario `// COMMANDER` seguido de la carta del comandante.
  - Líneas `<cantidad> <nombre> (<set>) <cn> [*F*]`.
  - Líneas en blanco de separación.
"""

from __future__ import annotations

# Mazo mínimo completo con comandante marcado.
SAMPLE_COMMANDER = """// COMMANDER
1 Teval, the Balanced Scale (TDC) 8 *F*

1 Sol Ring (C21) 250
1 Arcane Signet (EOC) 53
1 Birds of Paradise (FIC) 483 *F*
1 Swords to Plowshares (STA) 4
1 Brainstorm (STA) 13
20 Forest (ANB) 112
15 Swamp (ANB) 113
"""

# Lista sin comandante (formato construido 60 cartas), con "4x" y sin set.
SAMPLE_NO_COMMANDER = """4 Lightning Bolt (2XM) 123
4x Llanowar Elves
2 Sol Ring
12 Mountain
"""

# Lista con líneas problemáticas para probar tolerancia a errores.
SAMPLE_WITH_ERRORS = """// COMMANDER
1 Kilo, Apogee Mind (EOC) 3

1 Arcane Signet (M3C) 283
esto no es una linea valida
1 Counterspell (STA) 15
   
# comentario suelto
2 Island
"""

# Foil y colector alfanumérico (edge cases de ManaBox).
SAMPLE_EDGE_CASES = """1 Fabled Passage (PLST) ELD-244 *F*
1 Lim-Dûl's Vault (PLST) CMA-30
3 Wastes (OGW) 183a
"""
