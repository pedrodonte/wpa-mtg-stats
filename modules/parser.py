"""
Módulo 1: Parser de listas exportadas desde ManaBox.

Formatos soportados por línea:
    4 Lightning Bolt
    4 Lightning Bolt (2XM) 123
    1 Sol Ring (C21) 250 *F*
    1x Sol Ring
El sufijo opcional ``*F*`` (foil) se ignora para el análisis.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Expresión regular de parsing (spec Módulo 1). Se acepta también "4x" (con la x).
_LINE_RE = re.compile(
    r"^(?P<qty>\d+)x?\s+"
    r"(?P<name>.+?)"
    r"(?:\s+\((?P<set>[A-Za-z0-9]+)\)\s+(?P<cn>[A-Za-z0-9\-★]+))?"
    r"(?:\s+\*F\*)?\s*$"
)


@dataclass
class CardInput:
    """Representa una entrada de carta parseada desde la lista."""

    quantity: int
    name: str
    set: str | None = None
    collector_number: str | None = None

    @property
    def key(self) -> str:
        """Clave estable para deduplicación / caché."""
        if self.set and self.collector_number:
            return f"{self.set.lower()}:{self.collector_number.lower()}"
        return self.name.strip().lower()


def parse_decklist(raw_text: str) -> tuple[list[CardInput], list[str]]:
    """Parsea texto crudo de ManaBox.

    Devuelve una tupla ``(cartas, errores)`` donde ``errores`` contiene las
    líneas no vacías que no pudieron interpretarse.
    """
    cards: list[CardInput] = []
    errors: list[str] = []

    if not raw_text:
        return cards, errors

    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # Ignorar encabezados/comentarios y secciones de sideboard vacías.
        if line.startswith(("#", "//")) or line.lower() in {"sideboard", "deck", "commander"}:
            continue

        match = _LINE_RE.match(line)
        if not match:
            errors.append(raw_line)
            continue

        data = match.groupdict()
        try:
            qty = int(data["qty"])
        except (TypeError, ValueError):
            errors.append(raw_line)
            continue

        name = (data["name"] or "").strip()
        if not name:
            errors.append(raw_line)
            continue

        cards.append(
            CardInput(
                quantity=qty,
                name=name,
                set=data.get("set"),
                collector_number=data.get("cn"),
            )
        )

    return cards, errors


def total_cards(cards: list[CardInput]) -> int:
    """Suma total de copias en la lista."""
    return sum(c.quantity for c in cards)
