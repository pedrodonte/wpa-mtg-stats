"""Tests del módulo Collection & Binder Processor.

No usan red: el parsing se prueba con los archivos de ejemplo reales y la
agregación con EnrichedCard construidas a mano.
"""

from __future__ import annotations

from pathlib import Path

from modules.collection import (
    BinderFile,
    build_collection_analysis,
    build_collection_llm_report,
    build_collection_report,
    collection_export_filename,
    container_name_from_filename,
    parse_binders,
    parse_manabox_csv,
)
from modules.parser import CardInput
from modules.scryfall_client import EnrichedCard

EXAMPLES_DIR = (
    Path(__file__).resolve().parent.parent / "examples" / "input_collection_binding"
)


def test_container_name_from_filename():
    assert container_name_from_filename("caja negra.txt") == "Caja Negra"
    assert container_name_from_filename("Carpeta_Naranja.txt") == "Carpeta Naranja"
    assert container_name_from_filename("caja-verde.csv") == "Caja Verde"


def test_parse_binders_merges_and_traces():
    binder_a = BinderFile(
        filename="caja negra.txt",
        raw_text="1 Murder (M19) 110\n2 Swamp\n",
    )
    binder_b = BinderFile(
        filename="caja verde.txt",
        raw_text="1 Murder (M19) 110\n1 Forest\n",
    )
    inputs, locations, errors = parse_binders([binder_a, binder_b])

    assert not errors
    # Murder aparece en ambos contenedores: se consolida en una entrada.
    names = {i.name: i.quantity for i in inputs}
    assert names["Murder"] == 2
    murder_key = next(i.key for i in inputs if i.name == "Murder")
    assert locations[murder_key] == {"Caja Negra": 1, "Caja Verde": 1}


def test_parse_binders_reports_errors_with_container():
    binder = BinderFile(
        filename="caja negra.txt",
        raw_text="1 Murder (M19) 110\nlinea invalida\n",
    )
    _inputs, _loc, errors = parse_binders([binder])
    assert any("[Caja Negra]" in e for e in errors)


def _enriched_from_inputs(inputs: list[CardInput]) -> list[EnrichedCard]:
    """Simula enrich_cards: EnrichedCard mínima alineada con inputs."""
    fixtures = {
        "murder": dict(
            mana_cost="{1}{B}{B}", cmc=3, type_line="Instant",
            oracle_text="Destroy target creature.", colors=["B"],
            rarity="uncommon", set="m19", set_name="Core Set 2019",
            price_usd=0.25,
        ),
        "swamp": dict(
            cmc=0, type_line="Basic Land — Swamp", produced_mana=["B"],
            rarity="common", set="m19", set_name="Core Set 2019",
        ),
        "forest": dict(
            cmc=0, type_line="Basic Land — Forest", produced_mana=["G"],
            rarity="common", set="m19", set_name="Core Set 2019",
        ),
    }
    out = []
    for inp in inputs:
        f = fixtures.get(inp.name.lower(), {})
        out.append(EnrichedCard(quantity=inp.quantity, name=inp.name, **f))
    return out


def test_build_collection_analysis_aggregates():
    binder_a = BinderFile("caja negra.txt", "1 Murder (M19) 110\n2 Swamp\n")
    binder_b = BinderFile("caja verde.txt", "1 Murder (M19) 110\n1 Forest\n")
    inputs, locations, _errors = parse_binders([binder_a, binder_b])
    enriched = _enriched_from_inputs(inputs)

    analysis = build_collection_analysis(
        enriched, inputs, locations, ["Caja Negra", "Caja Verde"]
    )

    # Murder(2) + Swamp(2) + Forest(1) = 5 copias, 3 únicas.
    assert analysis.total_unique == 3
    assert analysis.total_copies == 5
    assert analysis.by_container["Caja Negra"] == 3   # 1 Murder + 2 Swamp
    assert analysis.by_container["Caja Verde"] == 2    # 1 Murder + 1 Forest
    assert analysis.by_type["Instant"] == 2
    assert analysis.by_type["Land"] == 3
    assert analysis.by_color["B"] == 2                 # Murder es negra
    assert analysis.by_rarity["uncommon"] == 2
    # Valor: Murder 0.25 x2 = 0.50.
    assert analysis.total_value_usd == 0.50


def test_collection_report_and_zero_buy_prompt():
    binder = BinderFile("caja negra.txt", "1 Murder (M19) 110\n2 Swamp\n")
    inputs, locations, _errors = parse_binders([binder])
    enriched = _enriched_from_inputs(inputs)
    analysis = build_collection_analysis(enriched, inputs, locations, ["Caja Negra"])

    md = build_collection_report(analysis, title="Colección Test")
    assert "# Colección Test" in md
    assert "## 1. Resumen de la Colección" in md
    assert "Reparto por Contenedor" in md
    assert "## 2. Manifiesto Detallado de la Colección" in md
    # Trazabilidad física en el manifiesto.
    assert "Ubicación: Caja Negra" in md
    assert "### Murder (x1)" in md

    llm = build_collection_llm_report(analysis, title="Colección Test")
    assert llm.startswith("# INSTRUCCIONES PARA EL MODELO DE IA")
    assert "ZERO-BUY" in llm
    assert md.strip() in llm


def test_collection_export_filename():
    assert collection_export_filename(["caja negra.txt"]) == (
        "coleccion-mtg_caja-negra.md"
    )
    multi = collection_export_filename(["caja negra.txt", "caja verde.txt"])
    assert multi.startswith("coleccion-mtg_consolidada_")
    assert multi.endswith(".md")


def test_example_files_parse():
    """Los archivos de ejemplo reales parsean sin errores de formato."""
    files = sorted(EXAMPLES_DIR.glob("*.txt"))
    assert files, "No hay archivos de ejemplo de colección."
    binders = [
        BinderFile(filename=f.name, raw_text=f.read_text(encoding="utf-8"))
        for f in files
    ]
    inputs, locations, errors = parse_binders(binders)
    assert inputs, "No se parseó ninguna carta de los ejemplos."
    assert not errors, f"Líneas no reconocidas: {errors[:5]}"
    # Cada carta debe tener al menos un contenedor asociado.
    assert all(locations[i.key] for i in inputs)


_CSV_SAMPLE = (
    "Binder Name,Binder Type,Name,Set code,Set name,Collector number,Foil,"
    "Rarity,Quantity,ManaBox ID,Scryfall ID,Purchase price,Misprint,Altered,"
    "Condition,Language,Purchase price currency,Added\n"
    "caja negra,binder,Murder,M19,Core Set 2019,110,normal,uncommon,1,1202,"
    "abc,0.35,false,false,near_mint,es,USD,2026-09-02T19:27:22Z\n"
    'caja negra,binder,"Syr Konrad, the Grim",DSC,Duskmourn Commander,158,'
    "normal,uncommon,2,99128,def,1.79,false,false,near_mint,es,USD,2026Z\n"
    "caja verde,binder,Murder,M19,Core Set 2019,110,normal,uncommon,1,1202,"
    "abc,0.35,false,false,near_mint,es,USD,2026-09-02T19:27:22Z\n"
)


def test_parse_manabox_csv_basic():
    inputs, locations, errors, prices = parse_manabox_csv(_CSV_SAMPLE)
    assert not errors
    names = {i.name: i.quantity for i in inputs}
    # Murder aparece en 2 contenedores (1+1); Syr Konrad x2 en uno.
    assert names["Murder"] == 2
    assert names["Syr Konrad, the Grim"] == 2
    murder_key = next(i.key for i in inputs if i.name == "Murder")
    assert locations[murder_key] == {"caja negra": 1, "caja verde": 1}
    # Precio de compra parseado.
    assert prices[murder_key] == 0.35


def test_parse_manabox_csv_quoted_names():
    """Los nombres con coma van entre comillas y no deben romper el parse."""
    inputs, _loc, _err, _prices = parse_manabox_csv(_CSV_SAMPLE)
    assert any(i.name == "Syr Konrad, the Grim" for i in inputs)


def test_csv_analysis_uses_purchase_price_fallback():
    inputs, locations, _err, prices = parse_manabox_csv(_CSV_SAMPLE)
    # EnrichedCard sin precio de mercado: debe caer al purchase price del CSV.
    enriched = [
        EnrichedCard(quantity=i.quantity, name=i.name, type_line="Instant")
        for i in inputs
    ]
    analysis = build_collection_analysis(
        enriched, inputs, locations, ["caja negra", "caja verde"],
        purchase_prices=prices,
    )
    # Murder(0.35 x2) + Syr Konrad(1.79 x2) = 0.70 + 3.58 = 4.28.
    assert analysis.total_value_usd == 4.28


def test_real_csv_parses_if_present():
    csv_path = EXAMPLES_DIR / "ManaBox_Collection.csv"
    if not csv_path.exists():
        return  # opcional: el CSV real puede no estar versionado.
    inputs, locations, errors, _prices = parse_manabox_csv(
        csv_path.read_text(encoding="utf-8")
    )
    assert inputs
    assert not errors
    containers = {cont for loc in locations.values() for cont in loc}
    assert len(containers) >= 1


def run() -> None:
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {name}")


if __name__ == "__main__":
    run()
    print("test_collection OK")
