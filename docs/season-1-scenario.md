# ComelyWorld — Season 1: The Twelve Eyes

A scenario for the first season of ComelyWorld, a Vanilla+ survival server: the story, the server mechanics, the artifacts and the events, and what it takes to build them. This is a proposal; nothing in it is implemented yet.

**Assumed baseline:** Minecraft Java Edition 26.3 on Paper, an optional server resource pack, about 40 active players, a 12-week season and an open-ended epilogue. Section 8 covers other sizes and the decisions still open.

**Organizers' copy.** It spoils the story and every event. A player-facing version should carry only the rules from sections 3 and 4.1.

## 1. The season in one minute

Players land in a world that an older people, the Comely, built, loved and then walked out of. The Comely lived by one rule: *what is admired endures*. Here, things that are looked at and cared for stay vivid, and things that are forgotten fade. The fading is called the Pallor, and it has been winning since the Comely left.

Twelve of their Masterworks are still hidden in the world, and each holds one Eye of the sealed End gate. Over twelve weeks the server recovers the Masterworks, keeps the world admired enough to hold the Pallor back, and finally carries the twelve Eyes to the Gate.

Nothing in the story is imported. It is told through places and creatures vanilla already has (trail ruins, abandoned camps, trial chambers, pale gardens, ancient cities, strongholds), and its motif is *looking*: Eyes of Ender, eyeblossoms, the Creaking that moves only when nobody watches it, the Endermen who cannot bear to be watched, the Warden that cannot see at all.

### The loop

| Players do this | It feeds | The server gets |
|---|---|---|
| Build, and visit each other's builds | **Laurels** (weekly tokens of admiration) and **Landmarks** (builds enough players admired) | **Regard**, the world's shared health bar |
| Deliver materials at spawn | **Great Works**, community buildings that rise in stages | The Nether, a museum, a market, forecasts, a wider border |
| Turn up for the Saturday story event | **Recoveries**, twelve events that each return one **Masterwork** | Twelve lit **Eyes**, then the Gate |
| Compete at the craft they are best at | **Rites**, the contests that decide who bears a Masterwork | Artifacts that keep moving to active players |
| Let any of it slide | The **Pallor**: pale groves erupting in the wild | Something to fight, and a reason to care |

### What a new player is told

1. Build something and stand your Plinth in front of it.
2. Every week you get three Laurels. Leave them at builds you like.
3. Bring materials to the Great Work at spawn.
4. Be there on Saturday night.

Everything else is found by playing.

### Design rules

1. **Vanilla first.** Every system extends something the game already does. No teleport commands, no virtual money, no gear with inflated stats, no custom mobs.
2. **Sidegrades, not upgrades.** An artifact changes how its bearer plays and always costs something, usually an equipment slot.
3. **One of each, in public.** Every Masterwork is unique and everyone can see who bears it.
4. **The world answers the players.** What happens next depends on what the community did, not only on the calendar.
5. **Nobody's base is collateral.** Events happen in the wild or at prepared sites, and PvP is by consent.
6. **Every way of playing gets a turn.** Builders, farmers, engineers, explorers, fighters and traders each have a Masterwork and an event of their own.

## 2. The story

### 2.1 The myth

1. The Comely were makers. They learned that this world keeps what is *regarded*, meaning looked at and cared for, and lets go of what is forgotten. The trail ruins are their towns.
2. To keep the world vivid they made twelve Masterworks, one for each craft they honored. Nobody inherited a Masterwork: the right to bear one was won in a Rite. The trial chambers are where the Rites were held.
3. Tending a world never ends, and in time they wanted a place where nothing fades. They built the Gate (the strongholds), set an Eye from each Masterwork into it and went through. Nothing fades in the End because nothing lives there.
4. The last Masters stayed behind. They pulled the Eyes back out, hid each Masterwork where its craft would be tested, and walked into the wild. The abandoned camps are theirs.
5. Since then the world has been forgetting itself. Pale gardens are places the Pallor has already taken, and the Creaking is neglect given legs. In the ancient cities the Comely tried one last idea: if the world will not look, let it listen. The sculk is still listening.
6. Those who went through the Gate are still there. They cannot stand to be looked at any more.

The last point is never stated outright; players should work the Endermen out for themselves. What the Dragon is, and what its Egg is, stays open for Season 2.

### 2.2 How it is told

- **Journal pages.** Twelve pages of the last Master's journal are added to abandoned-camp loot. Each page turns up only in the camps of certain biomes, so the full set takes travel and trading. A page gives one piece of the myth and one hint for a Recovery.
- **The Reliquary.** The hall at spawn with twelve pedestals. Each inscription changes when its Masterwork is recovered.
- **The Archive.** The museum keeps a copy of every page on lecterns for players who missed them.
- **The Lens.** One Masterwork lets its bearer read inscriptions nobody else can see, and decide whether to share them.

There are no cutscenes and no dialogue trees.

### 2.3 Chapters

| Chapter | Weeks | What the story reveals | Masterworks recovered | What opens |
|---|---|---|---|---|
| 1. Landfall | 1–2 | Twelve empty pedestals and a cold gate. The old works still answer to hands. | Trowel, Lantern | Nether, Archive |
| 2. Roots | 3–4 | The creed and the Rites. A town worth raiding. | Seal, Horn | Market Hall and Fair |
| 3. Ember and Storm | 5–6 | How the Masterworks were hidden, each where its craft is tested. | Cindertreads, Stormcaller | — |
| 4. The Pallor | 7–8 | Why the Comely left and what the pale gardens are. Regard can now fall. | Bough, Needle | Observatory, Pale Incursions |
| 5. The Proving | 9–10 | The hardest sites. "If the world will not look, let it listen." | Aegis, Wrench, Shroud | Causeway begins |
| 6. The Twelve Eyes | 11–12 | The last page: "We took the Eyes out so that no one would follow." | Lens | The Gate |
| Afterglow | 13+ | The choice, and what was left behind. | (the Egg) | The End |

**Opening night.** Everyone starts in the Reliquary. The pedestals are dark, Nether portals will not light, and the first Great Work board is already asking for materials. Each player receives two Plinths, three Laurels and the first journal page.

## 3. Server mechanics

### 3.1 Regard and the Pallor

Regard is one number from 0 to 100 for the whole server: how well the world is being looked after. It shows as a ring of lamps in the Reliquary and as a bar while a player is at spawn.

| Raises Regard | By | Lowers Regard | By |
|---|---|---|---|
| A Laurel is given | +0.2 | Each day that passes | −4 |
| A build becomes a Landmark, Marvel, Wonder | +2, +3, +5 | A Pale Incursion expires uncleansed | −3 |
| An Archive exhibit is donated | +0.1 | A Masterwork goes Dormant | −3 |
| An Archive wing is completed | +5 | | |
| A Great Work stage is finished | +3 | | |
| A Pale Incursion is cleansed | +2 | | |
| A Masterwork is recovered | +5 | | |

These values suit 40 active players. Scale the Laurel and exhibit values by 40 ÷ active players, then adjust the daily drain until an ordinary week roughly breaks even.

| State | Regard | What changes |
|---|---|---|
| Vivid | 70–100 | No phantoms. Starfall twice as often. The Caravan brings one extra rare lot. Incursions are rare. |
| Fair | 30–69 | The vanilla world. |
| Wan | 0–29 | Pale Incursions every night, and larger. |

- Until week 7 Regard cannot drop below 30: the world is still running on what the Comely left. The downside arrives with the Pallor chapter.
- Reaching 100 starts a **Vivid Festival** and reaching 0 starts **the Pale Night** (5.2).

*Why:* it turns three separate systems (Laurels, the Archive, Incursions) into one question the whole server can answer: is the world brighter than last week? It also lets the antagonist act without an admin flipping a switch. Low Regard is not a punishment. It produces more Incursions, which are content and the fastest way to raise Regard again.

### 3.2 Laurels and Landmarks

- Every Monday each player who was active the week before receives three **Laurels**. Unused Laurels wither after two weeks.
- A player marks a build by standing a **Plinth** in front of it and naming it. Everyone starts with two Plinths and earns another with each Landmark, up to five.
- Visitors leave a Laurel on the Plinth. One Laurel per visitor per build, and never on your own, so a build's count is simply how many different players admired it.
- At a quarter of the active players (10 of 40) the build becomes a **Landmark**; at half, a **Marvel**; at three quarters, a **Wonder**. Each tier adds a plaque, a marker on the web map, an entry in the *Grand Tour* book at spawn, and Regard. A Wonder's builder receives a Laurel Wreath.
- Giving counts too: a player who gives all three Laurels in a week receives one Starglass.
- Laurels are also the ballots for every judged contest. Contest Laurels are issued at the event and do not count toward Landmarks.

*Why:* the best thing on any survival server is other people's builds, and the usual problem is that nobody visits them. Laurels pay players to tour. Rewards are cosmetic and each admirer counts once per build, which keeps vote-trading pointless.

### 3.3 Great Works

A Great Work is a building at spawn that rises in stages as the community delivers materials to its site.

- Each stage has a public list. Anything on the list that is put into the site's drop-off barrels is consumed and credited to the player.
- When a stage is complete, the next part of the building appears and the next list is posted.
- Lists mix basics with harder items (stone, wood, glass, food, dyes, redstone), so new players can help and farms cannot finish a stage alone.
- Size each Work so that a third of the active players, contributing casually, finish it in three to five days.
- Every contributor is carved on a founders' stone and receives a Founder's token. Ideally the building's design is itself the winner of a player build contest.

| # | Great Work | Week | What it unlocks |
|---|---|---|---|
| 1 | The Hearthgate | 1 | Nether portals light. Reveals the Trowel. |
| 2 | The Archive | 2 | The museum opens for donations (3.4). |
| 3 | The Market Hall | 3 | Shop stalls, the weekly Fair, the Caravan. Reveals the Seal. Border +1,000. |
| 4 | The Observatory | 7 | Starfall and Incursion sites show on the locator bar. Reveals the five dig sites. Border +1,000. |
| 5 | The Causeway | 10–11 | A lit road from spawn to the stronghold, built by the players in twelve segments, one per Masterwork. Required for the Procession. |

### 3.4 The Archive

The Archive is the server's museum. Each exhibit slot accepts one specific item, once, and the donor's name goes on its plaque. Every donation adds Regard.

| Wing | Exhibits | Completing it |
|---|---|---|
| Antiquities | Every pottery sherd, armor trim, banner pattern and music disc that can be found before the End opens, and the twelve journal pages | Opens the reading room and the Lens (Recovery XII) |
| Natural history | Every sapling, flower, mushroom and coral; the Overworld and Nether mob heads; turtle and sniffer eggs; the three froglights | The Caravan stocks every sapling and flower |
| Mineralogy | Every ore, raw metal and gem; each stage of copper; amethyst, sulfur and cinnabar | The Caravan buys surplus ore for Starglass |
| The Gallery | Map art by players, hung by Laurel vote each month | A set of Keepsake paintings |
| The Far Wing | What only the End holds: the Spire trim, the dragon head, shulker shells, chorus, elytra | Opens with Afterglow, as the epilogue's collecting goal |

*Why:* collectors and explorers get a goal that lasts the whole season, and a rare find becomes a public moment instead of a line in someone's chest.

### 3.5 The Reliquary and the sealed Gate

- The Reliquary at spawn holds twelve pedestals, the ring of Regard lamps, the Ledger (who bears each Masterwork, since when, and everyone before them) and the board where Rites are called.
- Eyes of Ender still fly toward strongholds, but they cannot be set into portal frames. The Gate accepts only the twelve Eyes from the Reliquary.
- When a Masterwork is recovered its pedestal lights and its Eye appears there, fixed in place until the Procession.
- Twelve lit pedestals and a finished Causeway allow the Procession to be called (5.4).

### 3.6 House rules

| Topic | Rule |
|---|---|
| Difficulty and death | Hard. Items drop on death as in vanilla. |
| Travel | No teleport commands. Nether roads, boats, mounts, and elytra after the finale. |
| Money | Diamonds and barter. No virtual currency. Starglass buys Keepsakes only. |
| Land | No claims. Block logging and rollback stand behind the rule "don't touch what isn't yours". |
| PvP | By consent: duels both sides agreed to, and Rites that say so. |
| Sleep | The night passes when 30% of online players sleep. |
| Locator bar | On. The server uses it to point at event sites. |
| Farms | Allowed. Contests and lists are designed around things farms cannot mass-produce. |
| Border | Radius 3,000 at launch, +1,000 with the Market Hall, +1,000 with the Observatory. One more expansion is held back for the next game drop, so its terrain generates in fresh chunks. |
| The End | Shut until the finale. The outer islands are reset once, a week after opening, so late arrivals still find elytra. |

## 4. Artifacts

There are three tiers: twelve **Masterworks** (unique, powerful, contested), **the Egg** (unique, and the only thing that may be stolen) and **Keepsakes** (anyone can earn them).

### 4.1 Rules every Masterwork follows

1. **Unique.** Exactly one exists. It cannot break, burn or despawn, and if it is ever lost (the void, a glitch) it reappears on its pedestal.
2. **Public.** The Ledger names the current bearer and everyone before them, and a sigil sits next to the bearer's name in the player list.
3. **One per player.** A second Masterwork will not enter a bearer's inventory.
4. **Carried, not stored.** It will not go into ender chests, shulker boxes or bundles.
5. **Bound until yielded.** It stays with its bearer through death. It changes hands in four ways only:
   - **Gift.** The bearer hands it over.
   - **Rite.** Its contest, when someone calls it.
   - **Wager.** Any stake two players agree on, sealed by the Notary.
   - **Dormancy.** If the bearer has not carried it online for seven days, it returns to its pedestal and its next Rite is open to all.
6. **Calling a Rite.** Once a Masterwork has been held for 14 days, any player can call its Rite at the Reliquary by staking 8 diamonds. Others join for the same stake, the bearer defends in person or forfeits, and the winner takes the Masterwork and the pot. Up to two Rites run each Sunday in the order they were called, and a Masterwork cannot be called again for 14 days.
7. **A burden for every boon.** Each Masterwork takes an equipment slot or carries a cost, heavier the closer its boon comes to combat, travel or resources.
8. **Duels are bare.** In consensual PvP, Masterworks are set aside unless both sides agree otherwise.

*Why bound:* nobody ever has a reason to kill or rob a bearer, so Masterworks cause contests instead of grief. A server that wants more danger can switch on the hard variant: Masterworks drop on death and wait ten minutes for their bearer before anyone else can lift them.

### 4.2 The twelve Masterworks

| # | Masterwork | Craft | Carried as | Recovered in |
|---|---|---|---|---|
| I | The Mason's Trowel | Building | Held item | Week 2, First Stone |
| II | The First Lantern | Delving | Off-hand | Week 2, The Descent |
| III | The Notary's Seal | Commerce and law | Held item | Week 3, The Charter |
| IV | The Herald's Horn | Gathering | Held item | Week 4, The Long Raid |
| V | Cindertreads | The Nether roads | Boots | Week 5, The Ashen Road |
| VI | Stormcaller | Seafaring | Trident | Week 6, The Drowned Vault |
| VII | The Evergreen Bough | Tending | Off-hand | Week 7, The First Cleansing |
| VIII | The Seeker's Needle | Wayfinding | Held item | Week 8, The Dig |
| IX | The Aegis | Guarding | Shield | Week 9, The Proving |
| X | The Tinker's Wrench | Engineering | Held item | Week 9, The Jammed Sky |
| XI | The Hushed Shroud | Listening | Chest slot | Week 10, The Hush |
| XII | The Lens of Memory | Remembering | Spyglass | Week 11, The Grand Tour |

#### I. The Mason's Trowel

- **Boon.** Each click places a random block from the hotbar, for instant texture mixes. Three extra blocks of reach while it is in either hand.
- **Burden.** Light by design: it gives no edge in combat or resources. The extra reach does not apply to attacks.
- **Rite of Stone.** A timed build on a surprise theme, with the same plot and materials for everyone. Visitors vote with Laurels.

#### II. The First Lantern

- **Boon.** Full light around the bearer, under water too. The Darkness effect never takes hold of them. Sneak-use plants a lasting spark (an invisible light), up to 32 at a time, oldest fading first.
- **Burden.** It fills the off-hand: no shield, no totem, no rockets.
- **Rite of Depths.** A race down an unlit cave course where placing light is disabled. First to ring the bell at the bottom.

#### III. The Notary's Seal

- **Boon.** Notarizes a signed book: it gains an unforgeable line naming the Notary and the day, and can no longer be copied. That makes contracts, deeds, IOUs and banknotes possible. The Notary also assigns stalls in the Market Hall and seals Wagers in an escrow chest that opens only for the named winner.
- **Burden.** It is an office, not a prize. It is the only Masterwork with a fixed term: an election every three weeks, and a recall if a quarter of the active players petition.
- **Rite of Ballots.** Each candidate's urn (a decorated pot) stands in the Market Hall for 48 hours. Every player gets one ballot to drop in.

#### IV. The Herald's Horn

- **Boon.** Three times a day the whole server hears the Horn and sees one line of the bearer's choosing. For ten minutes the bearer shows in gold on everyone's locator bar, and players who answer the call (arrive within 16 blocks) get Regeneration and Speed for a minute.
- **Burden.** The Herald cannot hide. Sneaking, carved pumpkins and invisibility do not take them off the locator bar.
- **Rite of Song.** The best note-block piece, performed live and voted on with Laurels.

#### V. Cindertreads

- **Boon.** Fire and lava do not burn the bearer. Lava crusts over under their feet for a few seconds, so they can walk across lava seas.
- **Burden.** Water turns on them: rain and water hurt them as they hurt a Blaze. The boot slot is gone, and with it Feather Falling, Depth Strider and Soul Speed.
- **Rite of Ash.** A strider race across a lava lake, Treads off.

#### VI. Stormcaller

- **Boon.** A trident whose Channeling works in any weather under open sky, once every 45 seconds. Lightning on demand means charged creepers (and so mob heads), witches from villagers, and scrubbed copper. It returns when thrown and never breaks.
- **Burden.** In a real thunderstorm, lightning seeks the bearer whenever they stand under open sky.
- **Rite of Storms.** The Regatta: a boat race around sea buoys in a summoned storm.

#### VII. The Evergreen Bough

- **Boon.** Crops, saplings and other growing things within 8 blocks grow about three times as fast. Animals nearby are ready to breed again in half the time. Flowers spring up in the bearer's footsteps on grass.
- **Burden.** It fills the off-hand, and it only works where the bearer is standing.
- **Rite of Harvest.** The Harvest Table at the Fair: the most different foods laid on the table within the hour.

#### VIII. The Seeker's Needle

- **Boon.** Show it a piece of a place and it points to the nearest such place. Hold a token in the off-hand: a prismarine shard for an ocean monument, a trial key for a trial chamber, an echo shard for an ancient city, a nether brick for a fortress, gilded blackstone for a bastion, any sapling for its biome, a resin clump for an active Incursion.
- **Burden.** The token is consumed and the Needle rests for half an hour. It finds places, not people: its bearer loses the locator bar.
- **Rite of the Hunt.** The bearer is the quarry. They hide inside a marked square of wilderness; whoever lands a snowball on them takes the Needle; if they last twenty minutes they keep it.

#### IX. The Aegis

- **Boon.** A shield that stops what no shield stops: the Warden's sonic boom. Blocked projectiles fly back at whoever sent them. While the bearer is blocking, allies within 6 blocks gain Resistance.
- **Burden.** It is heavy: 15% slower movement while it is on the arm. Off-hand again, so no totem.
- **Rite of Blades.** The Gauntlet: solo wave survival in a trial arena with supplied gear, most waves wins. Servers that prefer it can run a duel bracket instead.

#### X. The Tinker's Wrench

- **Boon.** Use it on a block to turn it without breaking it (pistons, observers, hoppers, stairs, logs, rails, glazed terracotta). It can also lift what cannot normally be moved: a budding amethyst once a day or a monster spawner once a week, as an item that still works when placed.
- **Burden.** Lifting costs 10 levels for a budding amethyst and 30 for a spawner.
- **Rite of Gears.** An engineering brief, such as the smallest working 3×3 door, built in equal plots with supplied materials. Function is scored first and block count second.

#### XI. The Hushed Shroud

- **Boon.** The bearer makes no vibrations: sculk sensors, shriekers and the Warden cannot hear them. Mobs notice them from half the usual distance. They are hidden from the locator bar and their nameplate does not show through walls.
- **Burden.** The Hush takes your voice: no chat while it is worn. It also takes the chest slot, so no chestplate and no elytra.
- **Rite of Silence.** A stealth run through an ancient city to light a candle on the far altar. Any shriek ends the run; the fastest clean run wins.

#### XII. The Lens of Memory

- **Boon.** Look at a block through it to read the block's memory: who placed or broke it and when, and who last opened a container. Five readings a day. At story sites and Landmarks it also shows inscriptions nobody else can see, and the bearer decides whether to share, trade or sit on what they learn.
- **Burden.** Each reading costs 3 levels, and looking leaves a mark: a block that has been read glints for ten minutes.
- **Rite of Riddles.** The Grand Tour: a riddle trail whose clues are hidden at player-built Landmarks. First to the end.

Several Masterworks are jobs as much as tools: the Notary, the Herald, the storm-caller who supplies mob heads, the Tinker who moves spawners for a fee, the Seeker who sells directions, the detective with the Lens. That is deliberate. A unique service gives its bearer a place in the server's economy and gives everyone else a reason to talk to them.

### 4.3 The Egg

The Egg is the thirteenth artifact and the only one the Comely did not make. It appears when the Dragon falls for the second time (5.4).

- It is the one thing in ComelyWorld that may be stolen. Thieves take the Egg and nothing else, and repair what they break.
- It has to stand as a placed block somewhere a visitor can walk to, and its position always shows on everyone's locator bar.
- Each full day a player keeps it earns one Starglass and the title Keeper of the Egg. Whoever holds it when the season ends is named in the next season's Reliquary.

*Why:* after the finale the server needs a new game. One visible, stealable trophy turns every base into a vault and every evening into a heist, without loosening the no-grief rule for anything else.

### 4.4 Keepsakes

| Keepsake | What it is | How it is earned |
|---|---|---|
| Starglass | Shards of fallen stars. The only currency for Keepsakes; it cannot buy gear. | Starfalls, cleansed Incursions, the Naturalist's List, giving all three Laurels |
| Hats and masks | Wearable cosmetic models with no armor value | The Caravan, for Starglass |
| Wardlamp | A lantern that stops hostile mobs spawning within 8 blocks. Four per player. | The Caravan, for Starglass |
| Trophies | Display pieces for event winners, and player heads from duels | Rites and Recoveries |
| Founder's token | A named memento of one Great Work | Delivering to that Work |
| Laurel Wreath | A wearable wreath | Building a Wonder |
| Comely discs and paintings | Server-made music discs, and paintings by players chosen by Laurel vote | The Caravan, Archive wings |

## 5. Events

### 5.1 Recoveries: the twelve story events

Each Recovery returns one Masterwork, lights one Eye and adds 5 Regard. The sites are ordinary vanilla structures, chosen when the world is generated and sealed until their week. Five of the twelve run over several days, so players who cannot make Saturday still have Recoveries they can win.

Who becomes the first bearer depends on the kind of event. If the Recovery is a race or a contest, the winner bears the Masterwork. If the server won it together, **the Choosing** decides: everyone who took part stands in a ring, a light jumps from player to player and stops on one, with odds weighted by what each contributed.

**I. First Stone** (weeks 1–2, spawn). The server completes the Hearthgate and the Trowel is found in its foundation. Its first bearer comes from the first Rite of Stone: every build with a Plinth placed in the first two weeks is entered, and the most Laurels at the end of week 2 wins. This teaches Plinths and Laurels on day one and makes starter bases matter.

**II. The Descent** (week 2, a deep cave). A Comely lamp-shrine sits at the bottom of an unvisited cave inside the border. One hint is posted each day, each narrowing the search. Whoever reaches the shrine takes the Lantern.

**III. The Charter** (week 3, the Market Hall). Completing the Market Hall opens its strongroom, where the Seal lies. The first Notary is elected: the candidates' urns stand in the hall for 48 hours and every player has one ballot.

**IV. The Long Raid** (week 4, spawn town). The first Fair is raided by the Unregarding, the illagers, who take what they never made. The raiders are vanilla, but there are more waves and several captains, and the town's villagers have to survive. The last captain carries the Horn. First bearer: the Choosing.

**V. The Ashen Road** (week 5, the Nether). A basalt shrine stands on an island in a lava sea, about 800 blocks from where the Hearthgate comes out. Its coordinates are announced at the starting horn. Any route and any means: striders, bridges, potions. First to stand on the shrine takes the Treads.

**VI. The Drowned Vault** (week 6, the ocean monument nearest spawn). The server takes the monument and its three elder guardians. The vault in its core opens only to lightning, which cannot reach under water, so players drain a shaft from the surface down to the core and stand a lightning rod on the vault while a summoned storm rolls in. First bearer: the Choosing.

**VII. The First Cleansing** (week 7, wilderness near spawn). The first and largest Pale Incursion: a grove with seven creaking hearts appears overnight. An Incursion heart can only be broken while it is awake, at night, when its Creaking is out. A Creaking cannot be hurt and only stops when someone is looking at it, so players work in pairs, one watching and one chopping. When the last heart breaks, the Bough is growing in its place. First bearer: the Choosing. From this night on, Incursions are a recurring world event and Regard can fall below 30.

**VIII. The Dig** (week 8, five ruins). The finished Observatory points at five dig sites. Each hides one fragment of the Needle in suspicious sand or gravel, among ordinary finds. Fragments can be given, traded or wagered, and the first player to hold all five assembles the Needle at the Reliquary. Expect a week of diplomacy.

**IX. The Proving** (week 9, a trial chamber). The Aegis lies in a vault with twelve locks. Twelve different players must each win an ominous trial key in that chamber during the event and turn it in the vault. The twelve then contest the first Rite of Blades on the spot.

**X. The Jammed Sky** (week 9, the Observatory, all week). The Observatory's mechanism has seized and the Wrench is wedged in its works. The first Rite of Gears decides who frees it: the brief is posted on Monday and entries are tested on Sunday.

**XI. The Hush** (week 10, an ancient city). The Shroud hangs at the city's center. To take it a player must stand at the altar for thirty unbroken seconds, and any shriek anywhere in the city resets everyone's count. A Warden, once summoned, is everybody's problem. First to finish the count takes the Shroud.

**XII. The Grand Tour** (week 11, the players' own Landmarks). When the Archive's Antiquities wing is complete, or in week 11 at the latest, its reading room opens on the Lens and the first Rite of Riddles: a trail of riddles, each answered by visiting a Landmark that players built. First to the end takes the Lens.

### 5.2 World events

These run on their own, with no admin present.

| Event | When | What happens | Outcome |
|---|---|---|---|
| Starfall | From week 3, every two or three nights; twice as often when Vivid | A star crosses the sky and lands in the wild. A rough direction is announced; once the Observatory stands, the site shows on the locator bar. Every player who reaches the crater within 20 minutes can open its Star Core once. | Starglass, and a small chance of a Keepsake |
| Pale Incursion | From week 7: rare when Vivid, every two or three nights when Fair, nightly when Wan | A pale grove with one to three creaking hearts erupts in unsettled land. Every heart has to be broken within three nights. | Cleansed: Starglass and resin for everyone who helped, Regard +2. Expired: Regard −3, and a patch of pale moss stays as a scar. |
| The Caravan | Friday to Sunday, from week 3 | The Peddler arrives at the Market Hall. He sells Keepsakes for Starglass, buys one "wanted" vanilla good that changes weekly, and sells one Rumor (a hint about something hidden). | A different farm or trade matters each week |
| The Naturalist's List | Monday to Sunday, from week 2 | Five things to find and bring to the Archive desk, chosen from what farms cannot mass-produce: a pink sheep, a particular wolf or frog variant, a named goat horn, a rare flower. | Starglass for everyone who completes it and a Keepsake for the first three. Missing exhibits go into the Archive. |
| Vivid Festival | Regard reaches 100 | Fireworks at spawn, an extra Laurel for everyone, and the Caravan stays a full week. Regard then settles at 85. | A celebration the server earned |
| The Pale Night | Regard reaches 0 | Several Incursions erupt at once on the outskirts of spawn and must all be cleansed before dawn. At sunrise Regard returns to 30. | The low point, and the way back up |

Starfalls and Incursions never land in settled land: not within 150 blocks of a Plinth or a bed, and not in chunks where players have spent real time.

### 5.3 The weekly rhythm

| Day | What happens |
|---|---|
| Monday | Laurels are issued. The Naturalist's List and the Great Work stage list are posted. Rite calls open. |
| Wednesday | A guaranteed Starfall, the midweek shower. |
| Friday | The Caravan arrives and the Fair opens with player stalls. |
| Saturday | Story night: the week's Recovery. |
| Sunday | Rite night: up to two called Rites. Then the Laurel count, with new Landmarks and the Regard report. The List closes and the Caravan leaves. |

### 5.4 The finale

1. **The Procession.** The bearers of the twelve Masterworks, or players they name, lift the Eyes from the Reliquary and walk the Causeway to the stronghold. Eyes cannot pass through Nether portals or go into containers, so the only way is the road. Night holds until the walk is over and Incursions erupt beside the Causeway. If a carrier dies, the Eye lies where they fell: anyone may pick it up and go on, and an Eye left on the ground for a minute returns to the last waystation. Everyone without an Eye is an escort.
2. **The Gate.** The twelve set their Eyes and the portal opens. From this moment ordinary Eyes of Ender work in every other stronghold.
3. **The Dragon.** The fight is vanilla, with the Dragon's health scaled to the turnout. When it falls the crystals relight on their own, the vanilla respawn sequence plays, and it has to be beaten a second time. Then the Egg appears.
4. **The choice.** Back at the Reliquary the server votes with ballots: seal the Gate again, or leave it open. The result is the opening state of Season 2.

### 5.5 Afterglow

- The End is open: the outer islands, End cities, elytra.
- The Egg game begins (4.3).
- A last Fair hosts the season's awards: most admired build, most generous admirer, greatest founder, and the longest-serving bearer of each Masterwork. The names go on a wall that is carried into the next season's Reliquary.
- The world is published as a download.

**Season 2 hooks.** If the Gate was sealed, the next season opens with the Eyes scattered again and one of them missing. If it was left open, the Comely start coming back.

## 6. Season calendar

| Week | Chapter | Great Work | Story event (Saturday unless noted) | New this week |
|---|---|---|---|---|
| 1 | Landfall | Hearthgate | Opening night; First Stone begins | Laurels, Plinths, Regard |
| 2 | Landfall | Archive | The Descent (all week); First Stone judged on Sunday | Archive donations, Naturalist's List |
| 3 | Roots | Market Hall | The Charter (48-hour election) | Fair, Caravan, Starfall |
| 4 | Roots | — | The Long Raid | Rites can be called |
| 5 | Ember and Storm | — | The Ashen Road | — |
| 6 | Ember and Storm | — | The Drowned Vault | Second election |
| 7 | The Pallor | Observatory | The First Cleansing | Pale Incursions; Regard can fall below 30 |
| 8 | The Pallor | — | The Dig (all week) | Event sites on the locator bar |
| 9 | The Proving | — | The Proving; The Jammed Sky (all week) | Third election |
| 10 | The Proving | Causeway | The Hush | — |
| 11 | The Twelve Eyes | Causeway | The Grand Tour | — |
| 12 | The Twelve Eyes | — | Procession, Gate, Dragon, the choice | — |
| 13+ | Afterglow | — | Last Fair and awards | The End, the Egg |

## 7. Building it

Players join with an unmodified client. The resource pack is optional and only changes how Masterworks and Keepsakes look.

| Layer | What it carries |
|---|---|
| Vanilla settings | Sleep percentage, phantoms on or off (the Vivid perk), locator bar, world border, difficulty |
| Data pack | Journal pages in abandoned-camp loot; per-player rewards as vault blocks (one opening per player is built in); custom paintings and music discs; a season advancement tab that works as the quest log; structures for craters, groves and Great Work stages |
| Resource pack | Models and textures for Masterworks, Keepsakes, Laurels and Plinths, and a few sounds |
| Custom Paper plugin | Everything that keeps state: Masterwork binding and abilities, the Ledger, Regard, Laurels and Plinths, Great Work deliveries, the Archive, the event scheduler, Rite scoring, the Nether and Gate locks |
| Existing plugins | Block logging for rollbacks (the Lens reads from it); a web map for Landmarks (optional) |

**Build order.** Each step is playable on its own, and only the first three are needed before launch.

1. The Reliquary and the Masterwork framework (binding, Ledger, Dormancy), with the two simplest Masterworks: Trowel and Lantern.
2. Laurels, Plinths, Landmarks and the Regard counter.
3. Great Works and the Nether lock. **The season can open here.**
4. The Archive and the Naturalist's List (week 2).
5. Starfall, Starglass and the Caravan (week 3).
6. Pale Incursions and the Regard states (week 7).
7. The remaining Masterworks, in calendar order, one or two a week.
8. The Procession and the Gate (week 12).

**Running it.** One live evening a week (Saturday, 60 to 90 minutes) and one prepared site or building a week. Everything recurring is automatic.

## 8. Tuning and open decisions

| If the server | Change |
|---|---|
| Has fewer than about 20 active players | Run six Masterworks, one per chapter, each lighting two Eyes: Trowel, Seal, Stormcaller, Bough, Shroud, Lens. Landmark tiers are percentages and need no change. |
| Wants a shorter season | Eight weeks: chapters 1 to 4 take one week each, with both Recoveries on the weekend. |
| Wants stricter vanilla | Drop spawner lifting from the Wrench and drop the Wardlamp. Nothing else gives resources or safety that vanilla does not. |
| Wants more danger | Turn on the hard variant for Masterworks (4.1) and let Regard fall below 30 from week 1. |
| Gets a new game drop mid-season | Spend the reserved border expansion so the new terrain generates in fresh chunks. |

**Open decisions**

1. How many active players to plan for, and whether twelve weeks is the right length.
2. PvP: consent only, as written, or the hard variant.
3. Whether a custom Paper plugin is in scope. Without one, the story, the journal pages, Great Works run by hand and cosmetic artifacts still work, but Regard, Laurels and the Masterwork rules need it.
4. Which stronghold, monument, trial chamber and ancient city are the event sites. Pick them when the world is generated and seal them until their chapter.
