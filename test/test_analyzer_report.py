"""Tests de analyzer + report_builder con cartas enriquecidas simuladas.

No usan red: construyen EnrichedCard a mano para verificar las métricas y la
estructura del Markdown de salida.
"""

from __future__ import annotations

from modules.analyzer import analyze, hypergeometric_at_least
from modules.report_builder import build_report
from modules.scryfall_client import EnrichedCard


def _deck() -> list[EnrichedCard]:
    """Mazo pequeño representativo (comandante + piezas + tierras)."""
    return [
        EnrichedCard(quantity=1, name="Teval, the Balanced Scale",
                     mana_cost="{1}{B}{G}", cmc=3,
                     type_line="Legendary Creature — Zombie Druid",
                     oracle_text="Whenever Teval attacks, mill three cards. "
                                 "Create a 2/2 black and green Zombie Druid token.",
                     colors=["B", "G"], power="3", toughness="3"),
        EnrichedCard(quantity=1, name="Sol Ring", mana_cost="{1}", cmc=1,
                     type_line="Artifact", oracle_text="{T}: Add {C}{C}.",
                     produced_mana=["C"], price_usd=1.50),
        EnrichedCard(quantity=1, name="Birds of Paradise", mana_cost="{G}", cmc=1,
                     type_line="Creature — Bird",
                     oracle_text="Flying. {T}: Add one mana of any color.",
                     colors=["G"], produced_mana=["W", "U", "B", "R", "G"],
                     power="0", toughness="1", price_usd=8.0),
        EnrichedCard(quantity=1, name="Swords to Plowshares", mana_cost="{W}", cmc=1,
                     type_line="Instant",
                     oracle_text="Exile target creature. Its controller gains life "
                                 "equal to its power.", colors=["W"], price_usd=2.0),
        EnrichedCard(quantity=1, name="Grave Titan", mana_cost="{4}{B}{B}", cmc=6,
                     type_line="Creature — Zombie Giant",
                     oracle_text="Deathtouch. When Grave Titan enters and attacks, "
                                 "create two 2/2 black Zombie creature tokens.",
                     colors=["B"], power="6", toughness="6", price_usd=5.0),
        EnrichedCard(quantity=10, name="Forest", cmc=0,
                     type_line="Basic Land — Forest", produced_mana=["G"]),
        EnrichedCard(quantity=8, name="Swamp", cmc=0,
                     type_line="Basic Land — Swamp", produced_mana=["B"]),
        EnrichedCard(quantity=1, name="Temple of Malady", cmc=0, type_line="Land",
                     oracle_text="Temple of Malady enters tapped. When it enters, scry 1.",
                     produced_mana=["B", "G"]),
    ]


def test_curve_excludes_lands():
    a = analyze(_deck(), deck_size=99)
    # 5 no-tierras: CMC 3,1,1,1,6.
    assert a.curve.total_nonland == 5
    assert a.curve.buckets["1"] == 3
    assert a.curve.buckets["3"] == 1
    assert a.curve.buckets["6"] == 1
    assert a.total_lands == 19


def test_mana_balance_and_diagnosis():
    a = analyze(_deck(), deck_size=99)
    # PIPs: G de Birds(1)+Teval(1)=2 ; B de Teval(1)+Grave Titan(2)=3 ; W de Swords=1.
    assert a.balance.pips_required["G"] == 2
    assert a.balance.pips_required["B"] == 3
    assert a.balance.pips_required["W"] == 1
    # W no tiene fuentes (0/1) -> déficit; sin fuentes blancas.
    assert a.balance.coverage_ratio["W"] == 0.0
    assert a.balance.diagnosis["W"] == "🔴 Déficit"
    # Colores sin PIPs -> N/A.
    assert a.balance.diagnosis["R"] == "N/A"


def test_acceleration_and_tokens():
    a = analyze(_deck(), deck_size=99)
    assert a.acceleration.mana_rocks == 1        # Sol Ring
    assert a.acceleration.mana_dorks == 1        # Birds
    assert a.acceleration.token_producers >= 2   # Teval + Grave Titan


def test_combat_clock():
    a = analyze(_deck(), deck_size=99)
    # Criaturas: Teval(3), Birds(0), Grave Titan(6) => poder 9, 3 criaturas.
    assert a.combat.total_creatures == 3
    assert a.combat.total_power == 9
    # Evasión: Birds(flying) + Grave Titan(deathtouch) = 2.
    assert a.combat.evasion_count == 2
    assert a.combat.combat_clock_index > 0


def test_taplands_and_value():
    a = analyze(_deck(), deck_size=99)
    assert a.taplands == 1                       # Temple of Malady
    assert a.total_value_usd == 16.5             # 1.5+8+2+5


def test_hypergeometric_bounds():
    assert hypergeometric_at_least(k=3, N=99, K=36, n=9) > 0
    assert 0.0 <= hypergeometric_at_least(k=1, N=99, K=10, n=7) <= 1.0
    # k mayor que la muestra => 0.
    assert hypergeometric_at_least(k=10, N=99, K=36, n=9) == 0.0


def test_report_contains_commander_and_sections():
    deck = _deck()
    a = analyze(deck, deck_size=99, commander="Teval, the Balanced Scale")
    md = build_report(deck, a, deck_name="Mazo Test", strategy="Tokens")
    assert "# Mazo Test" in md
    assert "**Comandante:** Teval, the Balanced Scale" in md
    assert "## Métricas Cuantitativas y Telemetría" in md
    assert "Combat Clock" in md
    assert "Taplands incondicionales" in md
    # El manifiesto lista cada carta.
    assert "### Sol Ring (x1)" in md
    assert "### Forest (x10)" in md


def run() -> None:
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {name}")


if __name__ == "__main__":
    run()
    print("test_analyzer_report OK")
