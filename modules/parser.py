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
    is_commander: bool = False

    @property
    def key(self) -> str:
        """Clave estable para deduplicación / caché."""
        if self.set and self.collector_number:
            return f"{self.set.lower()}:{self.collector_number.lower()}"
        return self.name.strip().lower()


# Comentario de ManaBox que marca al comandante en la línea siguiente.
_COMMANDER_MARKER_RE = re.compile(r"^//\s*commander\b", re.I)


def parse_decklist(
    raw_text: str,
) -> tuple[list[CardInput], list[str], str | None]:
    """Parsea texto crudo de ManaBox.

    Devuelve ``(cartas, errores, comandante)``:
      - ``errores``: líneas no vacías que no pudieron interpretarse.
      - ``comandante``: nombre del comandante detectado vía ``// COMMANDER``
        (la carta inmediatamente posterior al comentario), o ``None``.
    """
    cards: list[CardInput] = []
    errors: list[str] = []
    commander: str | None = None
    next_is_commander = False

    if not raw_text:
        return cards, errors, commander

    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        # Marca de comandante: la SIGUIENTE carta parseada es el comandante.
        if _COMMANDER_MARKER_RE.match(line):
            next_is_commander = True
            continue

        # Ignorar otros encabezados/comentarios y secciones vacías.
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

        is_cmd = next_is_commander
        next_is_commander = False
        if is_cmd and commander is None:
            commander = name

        cards.append(
            CardInput(
                quantity=qty,
                name=name,
                set=data.get("set"),
                collector_number=data.get("cn"),
                is_commander=is_cmd,
            )
        )

    return cards, errors, commander


def total_cards(cards: list[CardInput]) -> int:
    """Suma total de copias en la lista."""
    return sum(c.quantity for c in cards)
