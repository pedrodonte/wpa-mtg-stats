# Mi Mazo Kilo v5

> Reporte generado por **MTG Telemetry Analyzer** — 2026-08-29 15:12

**Estrategia:** Artefactos, proliferar contadores y constructos

## 1. Resumen Ejecutivo y Métricas Estadísticas

- **Cartas totales:** 100
- **Tierras:** 36
- **CMC Promedio:** 3.02
- **Valor estimado (USD):** $383.94

### Curva de Maná

- **CMC Promedio (sin tierras):** 3.02
- **Hechizos (no tierras):** 64

| CMC | Cartas | Distribución |
| :-: | :----: | :----------- |
| 0 | 3 | `███·················` |
| 1 | 9 | `█████████···········` |
| 2 | 12 | `███████████·········` |
| 3 | 21 | `████████████████████` |
| 4 | 8 | `████████············` |
| 5 | 7 | `███████·············` |
| 6 | 1 | `█···················` |
| 7+ | 3 | `███·················` |

### Balance de Maná (Intensidad de PIPs vs. Fuentes)

- **Tierras totales:** 36

| Color | PIPs Requeridos | Fuentes | Ratio | Diagnóstico |
| :---- | :-------------: | :-----: | :---: | :---------- |
| W (Blanco) | 18 | 21 | 1.17 | 🟢 Óptimo |
| U (Azul) | 33 | 25 | 0.76 | 🟡 Ajustado |
| B (Negro) | 0 | 7 | N/A | N/A |
| R (Rojo) | 8 | 19 | 2.38 | 🟢 Óptimo |
| G (Verde) | 0 | 7 | N/A | N/A |
| C (Incoloro) | 0 | 12 | N/A | N/A |

### Roles Tácticos

| Rol | Copias | Cartas Clave |
| :-- | :----: | :----------- |
| Ramp / Fixing | 18 | Aetheric Amplifier, An Offer You Can't Refuse, Arc Reactor, Arcane Signet, Astral Cornucopia, Azorius Signet … |
| Card Advantage | 10 | Insight Engine, Jhoira, Weatherlight Captain, Long-Range Sensor, Padeem, Consul of Innovation, Scene of the Crime, Shorikai, Genesis Engine … |
| Protection / Counter | 10 | Bronze Guardian, Counterspell, Darksteel Citadel, Inspirit, Flagship Vessel, Padeem, Consul of Innovation, Razortide Bridge … |
| Cost Reducers | 7 | Arc Reactor, Emry, Lurker of the Loch, Enthusiastic Mechanaut, Organic Extinction, Thought Monitor, Voyage Home … |
| Proliferate | 6 | Kilo, Apogee Mind, Cayth, Famed Mechanist, Karn's Bastion, Ripples of Potential, Surge Conductor, Tekuthal, Inquiry Dominus |
| Charge Synergies | 6 | Astral Cornucopia, Insight Engine, Inspirit, Flagship Vessel, Long-Range Sensor, The Seriema, Uthros Research Craft |
| Single Removal | 4 | Generous Gift, Path to Exile, Swords to Plowshares, Wear // Tear |
| Karnstruct Engine | 4 | Digsite Engineer, Simulacrum Synthesizer, Urza's Saga, Urza, Lord High Artificer |
| Board Wipe | 1 | Organic Extinction |

### Consistencia Hipergeométrica

- **Tamaño de mazo evaluado (N):** 99
- **P(≥3 tierras al turno 3, ver 9 cartas):** 70.4%
- **P(≥1 pieza de Ramp en mano inicial, 7 cartas):** 76.6%
- **Tierras totales (K tierras):** 36
- **Piezas de Ramp (K ramp):** 18

---

## Métricas Cuantitativas y Telemetría

### Aceleración y Recursos
- **Artefactos de Maná (Mana Rocks):** 16 copias (Ej: Aetheric Amplifier, Arc Reactor, Arcane Signet, Astral Cornucopia…)
- **Criaturas de Maná (Mana Dorks):** 2 copias (Ej: Karn, Legacy Reforged, Urza, Lord High Artificer)
- **Motores de Creación de Fichas:** 13 cartas (Ej: An Offer You Can't Refuse, Castle Doom, Cayth, Famed Mechanist, Digsite Engineer…)

### Capacidad Ofensiva (Combat Clock)
- **Poder Total Base en Criaturas:** 40
- **Criaturas con Evasión:** 4
- **Habilitadores de Prisa (Haste):** 2
- **Poder Promedio / Criatura:** 1.90
- **Índice de Reloj de Combate (CCI):** 5.40
- **Criaturas con Poder Dinámico (*/X):** 2

### Resiliencia y Sustento
- **Fuentes de Ganancia de Vida:** 2
- **Consumidores de Vida como Recurso:** 4
- **Protección Activa (Hexproof/Indestructible/Ward/Counter):** 13
- **Recursión de Cementerio:** 0
- **Disparadores de Muerte (Death Triggers):** 0

### Consistencia de Base de Maná
- **Tierras Totales:** 36 (Lentas/Taplands incondicionales: 5)
- **P(≥3 tierras en T3 - 9 cartas):** 70.4%
- **P(≥1 Ramp en mano inicial - 7 cartas):** 76.6%

---

## 2. Manifiesto Detallado de Cartas

_Formato compacto: coste, CMC, tipo y texto Oracle en una línea._

### Astral Cornucopia (x1)
- {X}{X}{X} | CMC 0 | Artifact | Oracle: This artifact enters with X charge counters on it. {T}: Choose a color. Add one mana of that color for each charge counter on this artifact.

### Paradise Mantle (x1)
- {0} | CMC 0 | Artifact — Equipment | Oracle: Equipped creature has "{T}: Add one mana of any color." Equip {1}

### Walking Ballista (x1)
- {X}{X} | CMC 0 | Artifact Creature — Construct | P/T: 0/0 | Oracle: This creature enters with X +1/+1 counters on it. {4}: Put a +1/+1 counter on this creature. Remove a +1/+1 counter from this creature: It deals 1 damage to any target.

### An Offer You Can't Refuse (x1)
- {U} | CMC 1 | Instant | Oracle: Counter target noncreature spell. Its controller creates two Treasure tokens. (They're artifacts with "{T}, Sacrifice this token: Add one mana of any color.")

### Dispatch (x1)
- {W} | CMC 1 | Instant | Oracle: Tap target creature. Metalcraft — If you control three or more artifacts, exile that creature.

### Manifold Key (x1)
- {1} | CMC 1 | Artifact | Oracle: {1}, {T}: Untap another target artifact. {3}, {T}: Target creature can't be blocked this turn.

### Path to Exile (x1)
- {W} | CMC 1 | Instant | Oracle: Exile target creature. Its controller may search their library for a basic land card, put that card onto the battlefield tapped, then shuffle.

### Sol Ring (x1)
- {1} | CMC 1 | Artifact | Oracle: {T}: Add {C}{C}.

### Springleaf Drum (x1)
- {1} | CMC 1 | Artifact | Oracle: {T}, Tap an untapped creature you control: Add one mana of any color.

### Swan Song (x1)
- {U} | CMC 1 | Instant | Oracle: Counter target enchantment, instant, or sorcery spell. Its controller creates a 2/2 blue Bird creature token with flying.

### Swords to Plowshares (x1)
- {W} | CMC 1 | Instant | Oracle: Exile target creature. Its controller gains life equal to its power.

### Voltaic Key (x1)
- {1} | CMC 1 | Artifact | Oracle: {1}, {T}: Untap target artifact.

### Arcane Signet (x1)
- {2} | CMC 2 | Artifact | Oracle: {T}: Add one mana of any color in your commander's color identity.

### Azorius Signet (x1)
- {2} | CMC 2 | Artifact | Oracle: {1}, {T}: Add {W}{U}.

### Boros Signet (x1)
- {2} | CMC 2 | Artifact | Oracle: {1}, {T}: Add {R}{W}.

### Counterspell (x1)
- {U}{U} | CMC 2 | Instant | Oracle: Counter target spell.

### Dovin's Veto (x1)
- {W}{U} | CMC 2 | Instant | Oracle: This spell can't be countered. Counter target noncreature spell.

### Enthusiastic Mechanaut (x1)
- {U}{R} | CMC 2 | Artifact Creature — Goblin Artificer | P/T: 2/2 | Oracle: Flying Artifact spells you cast cost {1} less to cast.

### Izzet Signet (x1)
- {2} | CMC 2 | Artifact | Oracle: {1}, {T}: Add {U}{R}.

### Ripples of Potential (x1)
- {1}{U} | CMC 2 | Instant | Oracle: Proliferate, then choose any number of permanents you control that had a counter put on them this way. Those permanents phase out. (To proliferate, choose any number of permanents and/or players, then give each another counter of each kind already there. Treat phased-out permanents and anything attached to them as though they don't exist until their controller's next turn.)

### Steel Overseer (x1)
- {2} | CMC 2 | Artifact Creature — Construct | P/T: 1/1 | Oracle: {T}: Put a +1/+1 counter on each artifact creature you control.

### Talisman of Conviction (x1)
- {2} | CMC 2 | Artifact | Oracle: {T}: Add {C}. {T}: Add {R} or {W}. This artifact deals 1 damage to you.

### Talisman of Creativity (x1)
- {2} | CMC 2 | Artifact | Oracle: {T}: Add {C}. {T}: Add {U} or {R}. This artifact deals 1 damage to you.

### Talisman of Progress (x1)
- {2} | CMC 2 | Artifact | Oracle: {T}: Add {C}. {T}: Add {W} or {U}. This artifact deals 1 damage to you.

### Aetheric Amplifier (x1)
- {3} | CMC 3 | Artifact | Oracle: {T}: Add one mana of any color. {4}, {T}: Choose one. Activate only as a sorcery. • Double the number of each kind of counter on target permanent. • Double the number of each kind of counter you have.

### Digsite Engineer (x1)
- {2}{W} | CMC 3 | Creature — Dwarf Artificer | P/T: 3/3 | Oracle: Whenever you cast an artifact spell, you may pay {2}. If you do, create a 0/0 colorless Construct artifact creature token with "This token gets +1/+1 for each artifact you control."

### Emry, Lurker of the Loch (x1)
- {2}{U} | CMC 3 | Legendary Creature — Merfolk Wizard | P/T: 1/2 | Oracle: Affinity for artifacts (This spell costs {1} less to cast for each artifact you control.) When Emry enters, mill four cards. {T}: Choose target artifact card in your graveyard. You may cast that card this turn. (You still pay its costs. Timing rules still apply.)

### Fabricate (x1)
- {2}{U} | CMC 3 | Sorcery | Oracle: Search your library for an artifact card, reveal it, put it into your hand, then shuffle.

### Freed from the Real (x1)
- {2}{U} | CMC 3 | Enchantment — Aura | Oracle: Enchant creature {U}: Tap enchanted creature. {U}: Untap enchanted creature.

### Generous Gift (x1)
- {2}{W} | CMC 3 | Instant | Oracle: Destroy target permanent. Its controller creates a 3/3 green Elephant creature token.

### Insight Engine (x1)
- {2}{U} | CMC 3 | Artifact | Oracle: {2}, {T}: Put a charge counter on this artifact, then draw a card for each charge counter on it.

### Inspirit, Flagship Vessel (x1)
- {U}{R}{W} | CMC 3 | Legendary Artifact — Spacecraft | P/T: 5/5 | Oracle: Station (Tap another creature you control: Put charge counters equal to its power on this Spacecraft. Station only as a sorcery. It's an artifact creature at 8+.) 1+ | At the beginning of combat on your turn, put your choice of a +1/+1 counter or two charge counters on up to one other target artifact. 8+ | Flying Other artifacts you control have hexproof and indestructible.

### Ioreth of the Healing House (x1)
- {2}{U} | CMC 3 | Legendary Creature — Human Cleric | P/T: 1/4 | Oracle: {T}: Untap another target permanent. {T}: Untap two other target legendary creatures.

### Kilo, Apogee Mind (x1)
- {U}{R}{W} | CMC 3 | Legendary Artifact Creature — Robot Artificer | P/T: 3/3 | Oracle: Haste Whenever Kilo becomes tapped, proliferate. (Choose any number of permanents and/or players, then give each another counter of each kind already there.)

### Long-Range Sensor (x1)
- {2}{R} | CMC 3 | Artifact | Oracle: Whenever you attack a player, put a charge counter on this artifact. {1}, Remove two charge counters from this artifact: Discover 4. Activate only as a sorcery. (Exile cards from the top of your library until you exile a nonland card with mana value 4 or less. Cast it without paying its mana cost or put it into your hand. Put the rest on the bottom in a random order.)

### Relic of Legends (x1)
- {3} | CMC 3 | Artifact | Oracle: {T}: Add one mana of any color. Tap an untapped legendary creature you control: Add one mana of any color.

### Simulacrum Synthesizer (x1)
- {2}{U} | CMC 3 | Artifact | Oracle: When this artifact enters, scry 2. Whenever another artifact you control with mana value 3 or greater enters, create a 0/0 colorless Construct artifact creature token with "This token gets +1/+1 for each artifact you control."

### Sonic Screwdriver (x1)
- {3} | CMC 3 | Artifact | Oracle: {T}: Add one mana of any color. {1}, {T}: Untap another target artifact. {2}, {T}: Scry 1. (Look at the top card of your library. You may put that card on the bottom.) {3}, {T}: Target creature can't be blocked this turn.

### Surge Conductor (x1)
- {3} | CMC 3 | Artifact Creature — Robot | P/T: 3/2 | Oracle: Whenever another nontoken artifact you control enters, proliferate. (Choose any number of permanents and/or players, then give each another counter of each kind already there.)

### Tezzeret, Cruel Captain (x1)
- {3} | CMC 3 | Legendary Planeswalker — Tezzeret | Oracle: Whenever an artifact you control enters, put a loyalty counter on Tezzeret. 0: Untap target artifact or creature. If it's an artifact creature, put a +1/+1 counter on it. −3: Search your library for an artifact card with mana value 1 or less, reveal it, put it into your hand, then shuffle. −7: You get an emblem with "At the beginning of combat on your turn, put three +1/+1 counters on target artifact you control. If it's not a creature, it becomes a 0/0 Robot artifact creature."

### The Seriema (x1)
- {1}{W}{W} | CMC 3 | Legendary Artifact — Spacecraft | P/T: 5/5 | Oracle: When The Seriema enters, search your library for a legendary creature card, reveal it, put it into your hand, then shuffle. Station (Tap another creature you control: Put charge counters equal to its power on this Spacecraft. Station only as a sorcery. It's an artifact creature at 7+.) 7+ | Flying Other tapped legendary creatures you control have indestructible.

### Ultron, Artificial Malevolence (x1)
- {3} | CMC 3 | Legendary Artifact Creature — Robot Villain | P/T: 2/4 | Oracle: Whenever another nontoken artifact you control enters, you may pay {2}. If you do, create a token that's a copy of it. If the token isn't a creature, it becomes a 2/2 Robot Villain creature in addition to its other types.

### Uthros Research Craft (x1)
- {2}{U} | CMC 3 | Artifact — Spacecraft | P/T: 0/8 | Oracle: Station (Tap another creature you control: Put charge counters equal to its power on this Spacecraft. Station only as a sorcery. It's an artifact creature at 12+.) 3+ | Whenever you cast an artifact spell, draw a card. Put a charge counter on this Spacecraft. 12+ | Flying This Spacecraft gets +1/+0 for each artifact you control.

### Wear // Tear (x1)
- {1}{R} // {W} | CMC 3 | Instant // Instant | Oracle: Destroy target artifact. Fuse (You may cast one or both halves of this card from your hand.) // Destroy target enchantment. Fuse (You may cast one or both halves of this card from your hand.)

### Whir of Invention (x1)
- {X}{U}{U}{U} | CMC 3 | Instant | Oracle: Improvise (Your artifacts can help cast this spell. Each artifact you tap after you're done activating mana abilities pays for {1}.) Search your library for an artifact card with mana value X or less, put it onto the battlefield, then shuffle.

### Cayth, Famed Mechanist (x1)
- {1}{U}{R}{W} | CMC 4 | Legendary Creature — Dwarf Artificer | P/T: 3/3 | Oracle: Fabricate 1 (When this creature enters, put a +1/+1 counter on it or create a 1/1 colorless Servo artifact creature token.) Other nontoken creatures you control have fabricate 1. {2}, {T}: Choose one — • Populate. • Proliferate.

### Jhoira, Weatherlight Captain (x1)
- {2}{U}{R} | CMC 4 | Legendary Creature — Human Artificer | P/T: 3/3 | Oracle: Whenever you cast a historic spell, draw a card. (Artifacts, legendaries, and Sagas are historic.)

### Padeem, Consul of Innovation (x1)
- {3}{U} | CMC 4 | Legendary Creature — Vedalken Artificer | P/T: 1/4 | Oracle: Artifacts you control have hexproof. (They can't be the targets of spells or abilities your opponents control.) At the beginning of your upkeep, if you control the artifact with the greatest mana value or tied for the greatest mana value, draw a card.

### Phyrexian Metamorph (x1)
- {3}{U/P} | CMC 4 | Artifact Creature — Phyrexian Shapeshifter | P/T: 0/0 | Oracle: ({U/P} can be paid with either {U} or 2 life.) You may have this creature enter as a copy of any artifact or creature on the battlefield, except it's an artifact in addition to its other types.

### Shorikai, Genesis Engine (x1)
- {2}{W}{U} | CMC 4 | Legendary Artifact — Vehicle | P/T: 8/8 | Oracle: {1}, {T}: Draw two cards, then discard a card. Create a 1/1 colorless Pilot creature token with "This token crews Vehicles as though its power were 2 greater." Crew 8 (Tap any number of creatures you control with total power 8 or more: This Vehicle becomes an artifact creature until end of turn.)

### Tekuthal, Inquiry Dominus (x1)
- {2}{U}{U} | CMC 4 | Legendary Creature — Phyrexian Horror | P/T: 3/5 | Oracle: Flying If you would proliferate, proliferate twice instead. {1}{U/P}{U/P}, Remove three counters from among other artifacts, creatures, and planeswalkers you control: Put an indestructible counter on Tekuthal. ({U/P} can be paid with either {U} or 2 life.)

### Unwinding Clock (x1)
- {4} | CMC 4 | Artifact | Oracle: Untap all artifacts you control during each other player's untap step.

### Urza, Lord High Artificer (x1)
- {2}{U}{U} | CMC 4 | Legendary Creature — Human Artificer | P/T: 1/4 | Oracle: When Urza enters, create a 0/0 colorless Construct artifact creature token with "This token gets +1/+1 for each artifact you control." Tap an untapped artifact you control: Add {U}. {5}: Shuffle your library, then exile the top card. Until end of turn, you may play that card without paying its mana cost.

### Alibou, Ancient Witness (x1)
- {3}{R}{W} | CMC 5 | Legendary Artifact Creature — Golem | P/T: 4/5 | Oracle: Other artifact creatures you control have haste. Whenever one or more artifact creatures you control attack, Alibou deals X damage to any target and you scry X, where X is the number of tapped artifacts you control.

### Arc Reactor (x1)
- {5} | CMC 5 | Artifact | Oracle: Improvise (Your artifacts can help cast this spell. Each artifact you tap after you're done activating mana abilities pays for {1}.) This artifact enters tapped. {T}: Add {C}{C}{C}.

### Bronze Guardian (x1)
- {4}{W} | CMC 5 | Artifact Creature — Golem | P/T: */5 | Oracle: Double strike Ward {2} (Whenever this creature becomes the target of a spell or ability an opponent controls, counter it unless that player pays {2}.) Other artifacts you control have ward {2}. Bronze Guardian's power is equal to the number of artifacts you control.

### Deepglow Skate (x1)
- {4}{U} | CMC 5 | Creature — Fish | P/T: 3/3 | Oracle: When this creature enters, double the number of each kind of counter on any number of target permanents.

### Forsaken Monument (x1)
- {5} | CMC 5 | Legendary Artifact | Oracle: Colorless creatures you control get +2/+2. Whenever you tap a permanent for {C}, add an additional {C}. Whenever you cast a colorless spell, you gain 2 life.

### Karn, Legacy Reforged (x1)
- {5} | CMC 5 | Legendary Artifact Creature — Golem | P/T: */* | Oracle: Karn's power and toughness are each equal to the greatest mana value among artifacts you control. At the beginning of your upkeep, add {C} for each artifact you control. This mana can't be spent to cast nonartifact spells. Until end of turn, you don't lose this mana as steps and phases end.

### Tezzeret, Artifice Master (x1)
- {3}{U}{U} | CMC 5 | Legendary Planeswalker — Tezzeret | Oracle: +1: Create a 1/1 colorless Thopter artifact creature token with flying. 0: Draw a card. If you control three or more artifacts, draw two cards instead. −9: You get an emblem with "At the beginning of your end step, search your library for a permanent card, put it onto the battlefield, then shuffle."

### Cyberdrive Awakener (x1)
- {5}{U} | CMC 6 | Artifact Creature — Construct | P/T: 4/4 | Oracle: Flying Other artifact creatures you control have flying. When this creature enters, each noncreature artifact you control becomes a 4/4 artifact creature until end of turn.

### Thought Monitor (x1)
- {6}{U} | CMC 7 | Artifact Creature — Construct | P/T: 2/2 | Oracle: Affinity for artifacts (This spell costs {1} less to cast for each artifact you control.) Flying When this creature enters, draw two cards.

### Voyage Home (x1)
- {5}{W}{U} | CMC 7 | Sorcery | Oracle: Affinity for artifacts (This spell costs {1} less to cast for each artifact you control.) You draw three cards and gain 3 life.

### Organic Extinction (x1)
- {8}{W}{W} | CMC 10 | Sorcery | Oracle: Improvise (Your artifacts can help cast this spell. Each artifact you tap after you're done activating mana abilities pays for {1}.) Destroy all nonartifact creatures.

### Adarkar Wastes (x1)
- — | CMC 0 | Land | Oracle: {T}: Add {C}. {T}: Add {W} or {U}. This land deals 1 damage to you.

### Ancient Den (x1)
- — | CMC 0 | Artifact Land | Oracle: {T}: Add {W}.

### Battlefield Forge (x1)
- — | CMC 0 | Land | Oracle: {T}: Add {C}. {T}: Add {R} or {W}. This land deals 1 damage to you.

### Cascade Bluffs (x1)
- — | CMC 0 | Land | Oracle: {T}: Add {C}. {U/R}, {T}: Add {U}{U}, {U}{R}, or {R}{R}.

### Castle Doom (x1)
- — | CMC 0 | Land | Oracle: {T}: Add {C}. {T}: Add one mana of any color. Spend this mana only to cast an artifact spell. {3}, {T}, Sacrifice an artifact: Create a 3/3 colorless Robot Villain artifact creature token named Doombot. Activate only as a sorcery.

### City of Brass (x1)
- — | CMC 0 | Land | Oracle: Whenever this land becomes tapped, it deals 1 damage to you. {T}: Add one mana of any color.

### Clifftop Retreat (x1)
- — | CMC 0 | Land | Oracle: This land enters tapped unless you control a Mountain or a Plains. {T}: Add {R} or {W}.

### Command Tower (x1)
- — | CMC 0 | Land | Oracle: {T}: Add one mana of any color in your commander's color identity.

### Darksteel Citadel (x1)
- — | CMC 0 | Artifact Land | Oracle: Indestructible {T}: Add {C}.

### Exotic Orchard (x1)
- — | CMC 0 | Land | Oracle: {T}: Add one mana of any color that a land an opponent controls could produce.

### Forbidden Orchard (x1)
- — | CMC 0 | Land | Oracle: {T}: Add one mana of any color. Whenever you tap this land for mana, target opponent creates a 1/1 colorless Spirit creature token.

### Glacial Fortress (x1)
- — | CMC 0 | Land | Oracle: This land enters tapped unless you control a Plains or an Island. {T}: Add {W} or {U}.

### Gleaming Bastion (x1)
- — | CMC 0 | Land | Oracle: {T}: Add {C}. {T}: Add {W} or {U}. Activate only if this land entered this turn or if you control a basic land.

### Great Furnace (x1)
- — | CMC 0 | Artifact Land | Oracle: {T}: Add {R}.

### Hallowed Fountain (x1)
- — | CMC 0 | Land — Plains Island | Oracle: ({T}: Add {W} or {U}.) As this land enters, you may pay 2 life. If you don't, it enters tapped.

### Island (x1)
- — | CMC 0 | Basic Land — Island | Oracle: ({T}: Add {U}.)

### Island (x1)
- — | CMC 0 | Basic Land — Island | Oracle: ({T}: Add {U}.)

### Island (x2)
- — | CMC 0 | Basic Land — Island | Oracle: ({T}: Add {U}.)

### Karn's Bastion (x1)
- — | CMC 0 | Land | Oracle: {T}: Add {C}. {4}, {T}: Proliferate. (Choose any number of permanents and/or players, then give each another counter of each kind already there.)

### Plains (x1)
- — | CMC 0 | Basic Land — Plains | Oracle: ({T}: Add {W}.)

### Port Town (x1)
- — | CMC 0 | Land | Oracle: As this land enters, you may reveal a Plains or Island card from your hand. If you don't, this land enters tapped. {T}: Add {W} or {U}.

### Razortide Bridge (x1)
- — | CMC 0 | Artifact Land | Oracle: This land enters tapped. Indestructible {T}: Add {W} or {U}.

### Rugged Prairie (x1)
- — | CMC 0 | Land | Oracle: {T}: Add {C}. {R/W}, {T}: Add {R}{R}, {R}{W}, or {W}{W}.

### Rustvale Bridge (x1)
- — | CMC 0 | Artifact Land | Oracle: This land enters tapped. Indestructible {T}: Add {R} or {W}.

### Sacred Foundry (x1)
- — | CMC 0 | Land — Mountain Plains | Oracle: ({T}: Add {R} or {W}.) As this land enters, you may pay 2 life. If you don't, it enters tapped.

### Scene of the Crime (x1)
- — | CMC 0 | Artifact Land — Clue | Oracle: This land enters tapped. {T}: Add {C}. {T}, Tap an untapped creature you control: Add one mana of any color. {2}, Sacrifice this land: Draw a card.

### Seat of the Synod (x1)
- — | CMC 0 | Artifact Land | Oracle: {T}: Add {U}.

### Shivan Reef (x1)
- — | CMC 0 | Land | Oracle: {T}: Add {C}. {T}: Add {U} or {R}. This land deals 1 damage to you.

### Silverbluff Bridge (x1)
- — | CMC 0 | Artifact Land | Oracle: This land enters tapped. Indestructible {T}: Add {U} or {R}.

### Skycloud Expanse (x1)
- — | CMC 0 | Land | Oracle: {1}, {T}: Add {W}{U}.

### Spire of Industry (x1)
- — | CMC 0 | Land | Oracle: {T}: Add {C}. {T}, Pay 1 life: Add one mana of any color. Activate only if you control an artifact.

### Steam Vents (x1)
- — | CMC 0 | Land — Island Mountain | Oracle: ({T}: Add {U} or {R}.) As this land enters, you may pay 2 life. If you don't, it enters tapped.

### Stormcarved Coast (x1)
- — | CMC 0 | Land | Oracle: This land enters tapped unless you control two or more other lands. {T}: Add {U} or {R}.

### Sulfur Falls (x1)
- — | CMC 0 | Land | Oracle: This land enters tapped unless you control an Island or a Mountain. {T}: Add {U} or {R}.

### Urza's Saga (x1)
- — | CMC 0 | Enchantment Land — Urza's Saga | Oracle: (As this Saga enters and after your draw step, add a lore counter. Sacrifice after III.) I — This Saga gains "{T}: Add {C}." II — This Saga gains "{2}, {T}: Create a 0/0 colorless Construct artifact creature token with 'This token gets +1/+1 for each artifact you control.'" III — Search your library for an artifact card with mana cost {0} or {1}, put it onto the battlefield, then shuffle.
