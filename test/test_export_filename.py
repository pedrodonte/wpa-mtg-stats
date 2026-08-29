"""Tests del nombre de archivo de exportación (app._export_filename)."""

from __future__ import annotations

from datetime import datetime

import app


def test_first_word_only():
    """Solo la primera palabra del comandante (corta en espacio/punto/coma)."""
    assert app._first_word("Teval, the Balanced Scale") == "Teval"
    assert app._first_word("Kilo, Apogee Mind") == "Kilo"
    assert app._first_word("Urza. Lord High Artificer") == "Urza"
    assert app._first_word("Niv-Mizzet") == "Niv-Mizzet"  # el guion no corta
    assert app._first_word("Sol") == "Sol"


def test_export_filename_format():
    """Formato {primera_palabra}_{yyyy}_{dia_del_año}.md."""
    d = datetime(2026, 8, 29)  # día 241 del año
    assert app._export_filename("Teval, the Balanced Scale", d) == "teval_2026_241.md"
    assert app._export_filename("Kilo, Apogee Mind", d) == "kilo_2026_241.md"


def test_export_filename_day_of_year_edges():
    assert app._export_filename("Sol", datetime(2026, 1, 1)) == "sol_2026_1.md"
    assert app._export_filename("Sol", datetime(2026, 12, 31)) == "sol_2026_365.md"


def test_export_filename_fallback():
    d = datetime(2026, 8, 29)
    # Nombre vacío tras el slug cae al fallback de _slug.
    assert app._export_filename("", d) == "mtg-report_2026_241.md"


def run() -> None:
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {name}")


if __name__ == "__main__":
    run()
    print("test_export_filename OK")
