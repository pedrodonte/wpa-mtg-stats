"""Tests del parser: simulan la entrada de listas ManaBox."""

from __future__ import annotations

from modules.parser import parse_decklist, total_cards
from test.manabox_samples import (
    SAMPLE_COMMANDER,
    SAMPLE_EDGE_CASES,
    SAMPLE_NO_COMMANDER,
    SAMPLE_WITH_ERRORS,
)


def test_parse_commander_marker():
    """La carta tras `// COMMANDER` se marca como comandante."""
    cards, errors, commander = parse_decklist(SAMPLE_COMMANDER)
    assert commander == "Teval, the Balanced Scale"
    assert errors == []
    # 6 hechizos/rocks + 2 tipos de tierra = 8 entradas.
    assert len(cards) == 8
    # Copias: 1*6 + 20 + 15 = 41.
    assert total_cards(cards) == 41
    cmd = [c for c in cards if c.is_commander]
    assert len(cmd) == 1 and cmd[0].name == "Teval, the Balanced Scale"


def test_parse_set_and_collector_number():
    """Extrae set y collector number entre paréntesis."""
    cards, _, _ = parse_decklist(SAMPLE_COMMANDER)
    sol = next(c for c in cards if c.name == "Sol Ring")
    assert sol.set == "C21"
    assert sol.collector_number == "250"
    assert sol.quantity == 1


def test_parse_no_commander_and_quantities():
    """Soporta '4x', ausencia de set y no marca comandante."""
    cards, errors, commander = parse_decklist(SAMPLE_NO_COMMANDER)
    assert commander is None
    assert errors == []
    bolt = next(c for c in cards if c.name == "Lightning Bolt")
    assert bolt.quantity == 4 and bolt.set == "2XM"
    elves = next(c for c in cards if c.name == "Llanowar Elves")
    assert elves.quantity == 4 and elves.set is None
    # 4 + 4 + 2 + 12 = 22 copias.
    assert total_cards(cards) == 22


def test_parse_tolerates_errors_and_comments():
    """Líneas inválidas van a 'errores'; comentarios y vacías se ignoran."""
    cards, errors, commander = parse_decklist(SAMPLE_WITH_ERRORS)
    assert commander == "Kilo, Apogee Mind"
    assert "esto no es una linea valida" in errors
    assert len(errors) == 1
    names = {c.name for c in cards}
    assert {"Arcane Signet", "Counterspell", "Island"} <= names


def test_parse_edge_cases_foil_and_alnum_cn():
    """Foil (*F*) y collector numbers alfanuméricos con guion."""
    cards, errors, _ = parse_decklist(SAMPLE_EDGE_CASES)
    assert errors == []
    passage = next(c for c in cards if c.name == "Fabled Passage")
    assert passage.set == "PLST" and passage.collector_number == "ELD-244"
    wastes = next(c for c in cards if c.name == "Wastes")
    assert wastes.quantity == 3 and wastes.collector_number == "183a"


def test_parse_empty_input():
    cards, errors, commander = parse_decklist("")
    assert cards == [] and errors == [] and commander is None


def run() -> None:
    """Ejecución directa sin pytest."""
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {name}")


if __name__ == "__main__":
    run()
    print("test_parser OK")
