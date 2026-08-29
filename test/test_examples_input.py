"""Tests contra las listas reales exportadas desde ManaBox (examples/input).

El test de enriquecimiento con Scryfall es de integración: si no hay red o la
API falla, se omite en lugar de fallar.
"""

from __future__ import annotations

from pathlib import Path

from modules.analyzer import analyze
from modules.parser import parse_decklist, total_cards
from modules.scryfall_client import ScryfallCache, enrich_cards

INPUT_DIR = Path(__file__).resolve().parent.parent / "examples" / "input"

EXPECTED_COMMANDERS = {
    "Teval, the Balanced Scale (14).txt": "Teval, the Balanced Scale",
    "Kilo, Apogee Mind (5).txt": "Kilo, Apogee Mind",
    "Clavileño, First of the Blessed (4).txt": "Clavileño, First of the Blessed",
}


def _read(name: str) -> str:
    return (INPUT_DIR / name).read_text(encoding="utf-8")


def test_example_files_exist():
    files = {p.name for p in INPUT_DIR.glob("*.txt")}
    assert set(EXPECTED_COMMANDERS) <= files, f"faltan listas: {files}"


def test_example_commanders_and_totals():
    for name, expected_cmd in EXPECTED_COMMANDERS.items():
        cards, errors, commander = parse_decklist(_read(name))
        assert commander == expected_cmd, f"{name}: {commander!r}"
        assert errors == [], f"{name} tuvo errores: {errors[:3]}"
        # Mazos Commander: 100 cartas en total.
        assert total_cards(cards) == 100, f"{name}: {total_cards(cards)} copias"


def test_scryfall_enrichment_integration():
    """Integración real con Scryfall; se omite si no hay conectividad."""
    name = "Teval, the Balanced Scale (14).txt"
    cards, _, commander = parse_decklist(_read(name))
    try:
        enriched, not_found = enrich_cards(cards, cache=ScryfallCache())
    except Exception as exc:  # sin red / API caída
        _skip(f"Scryfall no disponible: {exc}")
        return

    found = sum(1 for e in enriched if e.found)
    if found == 0:
        _skip("Scryfall no devolvió datos (sin red).")
        return

    assert found >= len(enriched) - 2, f"demasiadas no encontradas: {not_found[:5]}"
    a = analyze(enriched, deck_size=99, commander=commander)
    assert a.total_cards == 100
    assert a.total_lands > 0
    assert a.curve.avg_cmc > 0
    # Diagnóstico de color debe existir para colores con PIPs.
    assert any(v != "N/A" for v in a.balance.diagnosis.values())


def _skip(msg: str) -> None:
    try:
        import pytest
        pytest.skip(msg)
    except ImportError:
        print(f"  ⏭  omitido: {msg}")


def run() -> None:
    for fn_name, fn in list(globals().items()):
        if fn_name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {fn_name}")


if __name__ == "__main__":
    run()
    print("test_examples_input OK")
