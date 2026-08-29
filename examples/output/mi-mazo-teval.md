# Mi Mazo Teval

> Reporte generado por **MTG Telemetry Analyzer** — 2026-08-29 15:21

**Estrategia:** Tierras desde el cementerio y orda de tokens

## 1. Resumen Ejecutivo y Métricas Estadísticas

- **Cartas totales:** 100
- **Tierras:** 36
- **CMC Promedio:** 2.83
- **Valor estimado (USD):** $601.03

### Curva de Maná

- **CMC Promedio (sin tierras):** 2.83
- **Hechizos (no tierras):** 64

| CMC | Cartas | Distribución |
| :-: | :----: | :----------- |
| 0 | 1 | `█···················` |
| 1 | 11 | `██████████··········` |
| 2 | 14 | `█████████████·······` |
| 3 | 21 | `████████████████████` |
| 4 | 9 | `█████████···········` |
| 5 | 7 | `███████·············` |
| 6 | 0 | `····················` |
| 7+ | 1 | `█···················` |

### Balance de Maná (Intensidad de PIPs vs. Fuentes)

- **Tierras totales:** 36

| Color | PIPs Requeridos | Fuentes | Ratio | Diagnóstico |
| :---- | :-------------: | :-----: | :---: | :---------- |
| W (Blanco) | 0 | 5 | N/A | N/A |
| U (Azul) | 7 | 14 | 2.0 | 🟢 Óptimo |
| B (Negro) | 21 | 23 | 1.1 | 🟢 Óptimo |
| R (Rojo) | 0 | 5 | N/A | N/A |
| G (Verde) | 46 | 18 | 0.39 | 🔴 Déficit |
| C (Incoloro) | 0 | 2 | N/A | N/A |

### Roles Tácticos

| Rol | Copias | Cartas Clave |
| :-- | :----: | :----------- |
| Card Advantage | 15 | Arcane Denial, Barren Moor, Braids, Arisen Nightmare, Brainstorm, Dakmor Salvage, Festering Thicket … |
| Ramp / Fixing | 11 | An Offer You Can't Refuse, Arcane Signet, Birds of Paradise, Crop Rotation, Insidious Roots, Lotus Cobra … |
| Single Removal | 8 | Abrupt Decay, Assassin's Trophy, Beast Within, Bojuka Bog, Grist, the Hunger Tide, Haywire Mite … |
| Protection / Counter | 7 | Arcane Denial, Heroic Intervention, Lotus Field, Maha, Its Feathers Night, Toski, Bearer of Secrets, Tyvar's Stand … |

### Consistencia Hipergeométrica

- **Tamaño de mazo evaluado (N):** 99
- **P(≥3 tierras al turno 3, ver 9 cartas):** 70.4%
- **P(≥1 pieza de Ramp en mano inicial, 7 cartas):** 57.4%
- **Tierras totales (K tierras):** 36
- **Piezas de Ramp (K ramp):** 11

---

## Métricas Cuantitativas y Telemetría

### Aceleración y Recursos
- **Artefactos de Maná (Mana Rocks):** 2 copias (Ej: Arcane Signet, Sol Ring)
- **Criaturas de Maná (Mana Dorks):** 4 copias (Ej: Birds of Paradise, Lotus Cobra, Pitiless Plunderer, Tireless Provisioner)
- **Motores de Creación de Fichas:** 15 cartas (Ej: Teval, the Balanced Scale, An Offer You Can't Refuse, Beast Within, Doubling Season…)

### Capacidad Ofensiva (Combat Clock)
- **Poder Total Base en Criaturas:** 74
- **Criaturas con Evasión:** 7
- **Habilitadores de Prisa (Haste):** 0
- **Poder Promedio / Criatura:** 2.47
- **Índice de Reloj de Combate (CCI):** 5.97
- **Criaturas con Poder Dinámico (*/X):** 0

### Resiliencia y Sustento
- **Fuentes de Ganancia de Vida:** 6
- **Consumidores de Vida como Recurso:** 6
- **Protección Activa (Hexproof/Indestructible/Ward/Counter):** 9
- **Recursión de Cementerio:** 14
- **Disparadores de Muerte (Death Triggers):** 4

### Consistencia de Base de Maná
- **Tierras Totales:** 36 (Lentas/Taplands incondicionales: 7)
- **P(≥3 tierras en T3 - 9 cartas):** 70.4%
- **P(≥1 Ramp en mano inicial - 7 cartas):** 57.4%

---

## 2. Manifiesto Detallado de Cartas

_Formato compacto: coste, CMC, tipo y texto Oracle en una línea._

### Zuran Orb (x1)
- {0} | CMC 0 | Artifact | Oracle: Sacrifice a land: You gain 2 life.

### An Offer You Can't Refuse (x1)
- {U} | CMC 1 | Instant | Oracle: Counter target noncreature spell. Its controller creates two Treasure tokens. (They're artifacts with "{T}, Sacrifice this token: Add one mana of any color.")

### Birds of Paradise (x1)
- {G} | CMC 1 | Creature — Bird | P/T: 0/1 | Oracle: Flying {T}: Add one mana of any color.

### Brainstorm (x1)
- {U} | CMC 1 | Instant | Oracle: Draw three cards, then put two cards from your hand on top of your library in any order.

### Crop Rotation (x1)
- {G} | CMC 1 | Instant | Oracle: As an additional cost to cast this spell, sacrifice a land. Search your library for a land card, put that card onto the battlefield, then shuffle.

### Haywire Mite (x1)
- {1} | CMC 1 | Artifact Creature — Insect | P/T: 1/1 | Oracle: When this creature dies, you gain 2 life. {G}, Sacrifice this creature: Exile target noncreature artifact or noncreature enchantment.

### Phyrexian Reclamation (x1)
- {B} | CMC 1 | Enchantment | Oracle: {1}{B}, Pay 2 life: Return target creature card from your graveyard to your hand.

### Skullclamp (x1)
- {1} | CMC 1 | Artifact — Equipment | Oracle: Equipped creature gets +1/-1. Whenever equipped creature dies, draw two cards. Equip {1}

### Sol Ring (x1)
- {1} | CMC 1 | Artifact | Oracle: {T}: Add {C}{C}.

### Tyvar's Stand (x1)
- {X}{G} | CMC 1 | Instant | Oracle: Target creature you control gets +X/+X and gains hexproof and indestructible until end of turn. (It can't be the target of spells or abilities your opponents control. Damage and effects that say "destroy" don't destroy it.)

### Veil of Summer (x1)
- {G} | CMC 1 | Instant | Oracle: Draw a card if an opponent has cast a blue or black spell this turn. Spells you control can't be countered this turn. You and permanents you control gain hexproof from blue and from black until end of turn. (You and they can't be the targets of blue or black spells or abilities your opponents control.)

### Worldly Tutor (x1)
- {G} | CMC 1 | Instant | Oracle: Search your library for a creature card, reveal it, then shuffle and put the card on top.

### Abrupt Decay (x1)
- {B}{G} | CMC 2 | Instant | Oracle: This spell can't be countered. Destroy target nonland permanent with mana value 3 or less.

### Accursed Marauder (x1)
- {1}{B} | CMC 2 | Creature — Zombie Warrior | P/T: 2/1 | Oracle: When this creature enters, each player sacrifices a nontoken creature of their choice.

### Arcane Denial (x1)
- {1}{U} | CMC 2 | Instant | Oracle: Counter target spell. Its controller may draw up to two cards at the beginning of the next turn's upkeep. You draw a card at the beginning of the next turn's upkeep.

### Arcane Signet (x1)
- {2} | CMC 2 | Artifact | Oracle: {T}: Add one mana of any color in your commander's color identity.

### Assassin's Trophy (x1)
- {B}{G} | CMC 2 | Instant | Oracle: Destroy target permanent an opponent controls. Its controller may search their library for a basic land card, put it onto the battlefield, then shuffle.

### Heroic Intervention (x1)
- {1}{G} | CMC 2 | Instant | Oracle: Permanents you control gain hexproof and indestructible until end of turn.

### Insidious Roots (x1)
- {B}{G} | CMC 2 | Enchantment | Oracle: Creature tokens you control have "{T}: Add one mana of any color." Whenever one or more creature cards leave your graveyard, create a 0/1 green Plant creature token, then put a +1/+1 counter on each Plant you control.

### Lightning Greaves (x1)
- {2} | CMC 2 | Artifact — Equipment | Oracle: Equipped creature has haste and shroud. (It can't be the target of spells or abilities.) Equip {0}

### Lotus Cobra (x1)
- {1}{G} | CMC 2 | Creature — Snake | P/T: 2/1 | Oracle: Landfall — Whenever a land you control enters, add one mana of any color.

### Nature's Lore (x1)
- {1}{G} | CMC 2 | Sorcery | Oracle: Search your library for a Forest card, put that card onto the battlefield, then shuffle.

### Negate (x1)
- {1}{U} | CMC 2 | Instant | Oracle: Counter target noncreature spell.

### Sakura-Tribe Elder (x1)
- {1}{G} | CMC 2 | Creature — Snake Shaman | P/T: 1/1 | Oracle: Sacrifice this creature: Search your library for a basic land card, put that card onto the battlefield tapped, then shuffle.

### Tear Asunder (x1)
- {1}{G} | CMC 2 | Instant | Oracle: Kicker {1}{B} (You may pay an additional {1}{B} as you cast this spell.) Exile target artifact or enchantment. If this spell was kicked, exile target nonland permanent instead.

### Three Visits (x1)
- {1}{G} | CMC 2 | Sorcery | Oracle: Search your library for a Forest card, put it onto the battlefield, then shuffle.

### Azusa, Lost but Seeking (x1)
- {2}{G} | CMC 3 | Legendary Creature — Human Monk | P/T: 1/2 | Oracle: You may play two additional lands on each of your turns.

### Beast Within (x1)
- {2}{G} | CMC 3 | Instant | Oracle: Destroy target permanent. Its controller creates a 3/3 green Beast creature token.

### Beastmaster Ascension (x1)
- {2}{G} | CMC 3 | Enchantment | Oracle: Whenever a creature you control attacks, you may put a quest counter on this enchantment. As long as this enchantment has seven or more quest counters on it, creatures you control get +5/+5.

### Braids, Arisen Nightmare (x1)
- {1}{B}{B} | CMC 3 | Legendary Creature — Nightmare | P/T: 3/3 | Oracle: At the beginning of your end step, you may sacrifice an artifact, creature, enchantment, land, or planeswalker. If you do, each opponent may sacrifice a permanent of their choice that shares a card type with it. For each opponent who doesn't, that player loses 2 life and you draw a card.

### Chatterfang, Squirrel General (x1)
- {2}{G} | CMC 3 | Legendary Creature — Squirrel Warrior | P/T: 3/3 | Oracle: Forestwalk (This creature can't be blocked as long as defending player controls a Forest.) If one or more tokens would be created under your control, those tokens plus that many 1/1 green Squirrel creature tokens are created instead. {B}, Sacrifice X Squirrels: Target creature gets +X/-X until end of turn.

### Crucible of Worlds (x1)
- {3} | CMC 3 | Artifact | Oracle: You may play lands from your graveyard.

### Dismember (x1)
- {1}{B/P}{B/P} | CMC 3 | Instant | Oracle: ({B/P} can be paid with either {B} or 2 life.) Target creature gets -5/-5 until end of turn.

### Formidable Speaker (x1)
- {2}{G} | CMC 3 | Creature — Elf Druid | P/T: 2/4 | Oracle: When this creature enters, you may discard a card. If you do, search your library for a creature card, reveal it, put it into your hand, then shuffle. {1}, {T}: Untap another target permanent.

### Formless Genesis (x1)
- {2}{G} | CMC 3 | Kindred Sorcery — Shapeshifter | Oracle: Changeling (This card is every creature type.) Create an X/X colorless Shapeshifter creature token with changeling and deathtouch, where X is the number of land cards in your graveyard. Retrace (You may cast this card from your graveyard by discarding a land card in addition to paying its other costs.)

### Grist, the Hunger Tide (x1)
- {1}{B}{G} | CMC 3 | Legendary Planeswalker — Grist | Oracle: As long as Grist isn't on the battlefield, it's a 1/1 Insect creature in addition to its other types. +1: Create a 1/1 black and green Insect creature token, then mill a card. If an Insect card was milled this way, put a loyalty counter on Grist and repeat this process. −2: You may sacrifice a creature. When you do, destroy target creature or planeswalker. −5: Each opponent loses life equal to the number of creature cards in your graveyard.

### Mole Man, Moloid Master (x1)
- {2}{G} | CMC 3 | Legendary Creature — Human Villain | P/T: 1/1 | Oracle: You may play lands from your graveyard. Landfall — Whenever a land you control enters, create a 1/1 green Minion creature token named Moloid with "Whenever this token attacks, you may mill a card."

### Peregrin Took (x1)
- {2}{G} | CMC 3 | Legendary Creature — Halfling Citizen | P/T: 2/3 | Oracle: If one or more tokens would be created under your control, those tokens plus an additional Food token are created instead. (It's an artifact with "{2}, {T}, Sacrifice this token: You gain 3 life.") Sacrifice three Foods: Draw a card.

### Ramunap Excavator (x1)
- {2}{G} | CMC 3 | Creature — Snake Cleric | P/T: 2/3 | Oracle: You may play lands from your graveyard.

### Reclamation Sage (x1)
- {2}{G} | CMC 3 | Creature — Elf Shaman | P/T: 2/1 | Oracle: When this creature enters, you may destroy target artifact or enchantment.

### Scute Swarm (x1)
- {2}{G} | CMC 3 | Creature — Insect | P/T: 1/1 | Oracle: Landfall — Whenever a land you control enters, create a 1/1 green Insect creature token. If you control six or more lands, create a token that's a copy of this creature instead.

### Six (x1)
- {2}{G} | CMC 3 | Legendary Creature — Treefolk | P/T: 2/4 | Oracle: Reach Whenever Six attacks, mill three cards. You may put a land card from among them into your hand. During your turn, nonland permanent cards in your graveyard have retrace. (You may cast permanent cards from your graveyard by discarding a land card in addition to paying their other costs.)

### Spelunking (x1)
- {2}{G} | CMC 3 | Enchantment | Oracle: When this enchantment enters, draw a card, then you may put a land card from your hand onto the battlefield. If you put a Cave onto the battlefield this way, you gain 4 life. Lands you control enter untapped.

### Tireless Provisioner (x1)
- {2}{G} | CMC 3 | Creature — Elf Scout | P/T: 3/2 | Oracle: Landfall — Whenever a land you control enters, create a Food token or a Treasure token. (Food is an artifact with "{2}, {T}, Sacrifice this token: You gain 3 life." Treasure is an artifact with "{T}, Sacrifice this token: Add one mana of any color.")

### Tireless Tracker (x1)
- {2}{G} | CMC 3 | Creature — Human Scout | P/T: 3/2 | Oracle: Landfall — Whenever a land you control enters, investigate. (Create a Clue token. It's an artifact with "{2}, Sacrifice this token: Draw a card.") Whenever you sacrifice a Clue, put a +1/+1 counter on this creature.

### Toxic Deluge (x1)
- {2}{B} | CMC 3 | Sorcery | Oracle: As an additional cost to cast this spell, pay X life. All creatures get -X/-X until end of turn.

### Victimize (x1)
- {2}{B} | CMC 3 | Sorcery | Oracle: Choose two target creature cards in your graveyard. Sacrifice a creature. If you do, return the chosen cards to the battlefield tapped.

### Icetill Explorer (x1)
- {2}{G}{G} | CMC 4 | Creature — Insect Scout | P/T: 2/4 | Oracle: You may play an additional land on each of your turns. You may play lands from your graveyard. Landfall — Whenever a land you control enters, mill a card.

### Meren of Clan Nel Toth (x1)
- {2}{B}{G} | CMC 4 | Legendary Creature — Human Shaman | P/T: 3/4 | Oracle: Whenever another creature you control dies, you get an experience counter. At the beginning of your end step, choose target creature card in your graveyard. If that card's mana value is less than or equal to the number of experience counters you have, return it to the battlefield. Otherwise, put it into your hand.

### Mirkwood Bats (x1)
- {3}{B} | CMC 4 | Creature — Bat | P/T: 2/3 | Oracle: Flying Whenever you create or sacrifice a token, each opponent loses 1 life.

### Pitiless Plunderer (x1)
- {3}{B} | CMC 4 | Creature — Human Pirate | P/T: 1/4 | Oracle: Whenever another creature you control dies, create a Treasure token. (It's an artifact with "{T}, Sacrifice this token: Add one mana of any color.")

### Scapeshift (x1)
- {2}{G}{G} | CMC 4 | Sorcery | Oracle: Sacrifice any number of lands. Search your library for up to that many land cards, put them onto the battlefield tapped, then shuffle.

### Teval, the Balanced Scale (x1)
- {1}{B}{G}{U} | CMC 4 | Legendary Creature — Spirit Dragon | P/T: 4/4 | Oracle: Flying Whenever Teval attacks, mill three cards. Then you may return a land card from your graveyard to the battlefield tapped. Whenever one or more cards leave your graveyard, create a 2/2 black Zombie Druid creature token.

### Toski, Bearer of Secrets (x1)
- {3}{G} | CMC 4 | Legendary Creature — Squirrel | P/T: 1/1 | Oracle: This spell can't be countered. Indestructible Toski attacks each combat if able. Whenever a creature you control deals combat damage to a player, draw a card.

### Wonder (x1)
- {3}{U} | CMC 4 | Creature — Incarnation | P/T: 2/2 | Oracle: Flying As long as this card is in your graveyard and you control an Island, creatures you control have flying.

### World Shaper (x1)
- {3}{G} | CMC 4 | Creature — Merfolk Shaman | P/T: 3/3 | Oracle: Whenever this creature attacks, you may mill three cards. When this creature dies, return all land cards from your graveyard to the battlefield tapped.

### Doubling Season (x1)
- {4}{G} | CMC 5 | Enchantment | Oracle: If an effect would create one or more tokens under your control, it creates twice that many of those tokens instead. If an effect would put one or more counters on a permanent you control, it puts twice that many of those counters on that permanent instead.

### Living Death (x1)
- {3}{B}{B} | CMC 5 | Sorcery | Oracle: Each player exiles all creature cards from their graveyard, then sacrifices all creatures they control, then puts all cards they exiled this way onto the battlefield.

### Maha, Its Feathers Night (x1)
- {3}{B}{B} | CMC 5 | Legendary Creature — Elemental Bird | P/T: 6/5 | Oracle: Flying, trample Ward—Discard a card. Creatures your opponents control have base toughness 1.

### Syr Konrad, the Grim (x1)
- {3}{B}{B} | CMC 5 | Legendary Creature — Human Knight | P/T: 5/4 | Oracle: Whenever another creature dies, or a creature card is put into a graveyard from anywhere other than the battlefield, or a creature card leaves your graveyard, Syr Konrad deals 1 damage to each opponent. {1}{B}: Each player mills a card. (They each put the top card of their library into their graveyard.)

### Tatyova, Benthic Druid (x1)
- {3}{G}{U} | CMC 5 | Legendary Creature — Merfolk Druid | P/T: 3/3 | Oracle: Landfall — Whenever a land you control enters, you gain 1 life and draw a card.

### The Gitrog Monster (x1)
- {3}{B}{G} | CMC 5 | Legendary Creature — Frog Horror | P/T: 6/6 | Oracle: Deathtouch At the beginning of your upkeep, sacrifice The Gitrog Monster unless you sacrifice a land. You may play an additional land on each of your turns. Whenever one or more land cards are put into your graveyard from anywhere, draw a card.

### Titania, Protector of Argoth (x1)
- {3}{G}{G} | CMC 5 | Legendary Creature — Elemental | P/T: 5/3 | Oracle: When Titania enters, return target land card from your graveyard to the battlefield. Whenever a land you control is put into a graveyard from the battlefield, create a 5/3 green Elemental creature token.

### Walk-In Closet // Forgotten Cellar (x1)
- {2}{G} // {3}{G}{G} | CMC 8 | Enchantment — Room // Enchantment — Room | Oracle: You may play lands from your graveyard. (You may cast either half. That door unlocks on the battlefield. As a sorcery, you may pay the mana cost of a locked door to unlock it.) // When you unlock this door, you may cast spells from your graveyard this turn, and if a card would be put into your graveyard from anywhere this turn, exile it instead. (You may cast either half. That door unlocks on the battlefield. As a sorcery, you may pay the mana cost of a locked door to unlock it.)

### Barren Moor (x1)
- — | CMC 0 | Land | Oracle: This land enters tapped. {T}: Add {B}. Cycling {B} ({B}, Discard this card: Draw a card.)

### Blooming Marsh (x1)
- — | CMC 0 | Land | Oracle: This land enters tapped unless you control two or fewer other lands. {T}: Add {B} or {G}.

### Bojuka Bog (x1)
- — | CMC 0 | Land | Oracle: This land enters tapped. When this land enters, exile target player's graveyard. {T}: Add {B}.

### Breeding Pool (x1)
- — | CMC 0 | Land — Forest Island | Oracle: ({T}: Add {G} or {U}.) As this land enters, you may pay 2 life. If you don't, it enters tapped.

### City of Brass (x1)
- — | CMC 0 | Land | Oracle: Whenever this land becomes tapped, it deals 1 damage to you. {T}: Add one mana of any color.

### Command Tower (x1)
- — | CMC 0 | Land | Oracle: {T}: Add one mana of any color in your commander's color identity.

### Dakmor Salvage (x1)
- — | CMC 0 | Land | Oracle: This land enters tapped. {T}: Add {B}. Dredge 2 (If you would draw a card, you may mill two cards instead. If you do, return this card from your graveyard to your hand.)

### Darkwater Catacombs (x1)
- — | CMC 0 | Land | Oracle: {1}, {T}: Add {U}{B}.

### Deathcap Glade (x1)
- — | CMC 0 | Land | Oracle: This land enters tapped unless you control two or more other lands. {T}: Add {B} or {G}.

### Drowned Catacomb (x1)
- — | CMC 0 | Land | Oracle: This land enters tapped unless you control an Island or a Swamp. {T}: Add {U} or {B}.

### Exotic Orchard (x1)
- — | CMC 0 | Land | Oracle: {T}: Add one mana of any color that a land an opponent controls could produce.

### Fabled Passage (x1)
- — | CMC 0 | Land | Oracle: {T}, Sacrifice this land: Search your library for a basic land card, put it onto the battlefield tapped, then shuffle. Then if you control four or more lands, untap that land.

### Festering Thicket (x1)
- — | CMC 0 | Land — Swamp Forest | Oracle: ({T}: Add {B} or {G}.) This land enters tapped. Cycling {2} ({2}, Discard this card: Draw a card.)

### Flooded Strand (x1)
- — | CMC 0 | Land | Oracle: {T}, Pay 1 life, Sacrifice this land: Search your library for a Plains or Island card, put it onto the battlefield, then shuffle.

### Forbidden Orchard (x1)
- — | CMC 0 | Land | Oracle: {T}: Add one mana of any color. Whenever you tap this land for mana, target opponent creates a 1/1 colorless Spirit creature token.

### Forest (x2)
- — | CMC 0 | Basic Land — Forest | Oracle: ({T}: Add {G}.)

### Island (x3)
- — | CMC 0 | Basic Land — Island | Oracle: ({T}: Add {U}.)

### Llanowar Wastes (x1)
- — | CMC 0 | Land | Oracle: {T}: Add {C}. {T}: Add {B} or {G}. This land deals 1 damage to you.

### Lonely Sandbar (x1)
- — | CMC 0 | Land | Oracle: This land enters tapped. {T}: Add {U}. Cycling {U} ({U}, Discard this card: Draw a card.)

### Lotus Field (x1)
- — | CMC 0 | Land | Oracle: Hexproof This land enters tapped. When this land enters, sacrifice two lands. {T}: Add three mana of any one color.

### Mudflat Village (x1)
- — | CMC 0 | Land | Oracle: {T}: Add {C}. {T}: Add {B}. Spend this mana only to cast a creature spell. {1}{B}, {T}, Sacrifice this land: Return target Bat, Lizard, Rat, or Squirrel card from your graveyard to your hand.

### Overgrown Tomb (x1)
- — | CMC 0 | Land — Swamp Forest | Oracle: ({T}: Add {B} or {G}.) As this land enters, you may pay 2 life. If you don't, it enters tapped.

### Shifting Woodland (x1)
- — | CMC 0 | Land | Oracle: This land enters tapped unless you control a Forest. {T}: Add {G}. Delirium — {2}{G}{G}: This land becomes a copy of target permanent card in your graveyard until end of turn. Activate only if there are four or more card types among cards in your graveyard.

### Sunken Hollow (x1)
- — | CMC 0 | Land — Island Swamp | Oracle: ({T}: Add {U} or {B}.) This land enters tapped unless you control two or more basic lands.

### Swamp (x2)
- — | CMC 0 | Basic Land — Swamp | Oracle: ({T}: Add {B}.)

### Undergrowth Stadium (x1)
- — | CMC 0 | Land | Oracle: This land enters tapped unless you have two or more opponents. {T}: Add {B} or {G}.

### Urborg, Tomb of Yawgmoth (x1)
- — | CMC 0 | Legendary Land | Oracle: Each land is a Swamp in addition to its other land types.

### Watery Grave (x1)
- — | CMC 0 | Land — Island Swamp | Oracle: ({T}: Add {U} or {B}.) As this land enters, you may pay 2 life. If you don't, it enters tapped.

### Wooded Foothills (x1)
- — | CMC 0 | Land | Oracle: {T}, Pay 1 life, Sacrifice this land: Search your library for a Mountain or Forest card, put it onto the battlefield, then shuffle.

### Woodland Cemetery (x1)
- — | CMC 0 | Land | Oracle: This land enters tapped unless you control a Swamp or a Forest. {T}: Add {B} or {G}.

### Yavimaya, Cradle of Growth (x1)
- — | CMC 0 | Legendary Land | Oracle: Each land is a Forest in addition to its other land types.

### Bala Ged Recovery // Bala Ged Sanctuary (x1)
- {2}{G} | CMC 3 | Sorcery // Land | Oracle: Return target card from your graveyard to your hand. // This land enters tapped. {T}: Add {G}.
