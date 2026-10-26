# Project Zomboid mechanics catalogue for the simulation

Purpose: what the real game does (stats, injuries, combat, zombies, settings), what our training environment does today, and what to add over time so agents learn skills that survive the move to a real client. Written 2026-10-26 from pzwiki.net (read through the built-in browser; plain fetching is blocked with HTTP 403), summarised in our own words. The wiki is edited by players and often lags the game: every article carries a banner saying which build it was last updated for, so use the staleness table to decide how far to trust a number, and verify anything we encode against the game files (`media/scripts/generated/items/*.txt`, `media/lua/shared/Sandbox/*.lua`, javap on the jar).

The installed game is Build 42.21.0 (the wiki calls it "current stable").

## How fresh is each article (banner read on 2026-10-26)

| Article | Last updated for | Trust |
|---|---|---|
| Zombie | 42.21.0 (current) | high |
| Custom Sandbox | 42.20.4 | high for option names, check defaults |
| Strength | 42.18.0, but its numeric table is from 41.78.16 | medium: verify the multipliers |
| Long Blunt | 42.18.0 | medium |
| Weapon | 42.20.4 | high for stats (bat weight 2.0 confirmed in the game's own item script) |
| Health | 42.15.3 | medium |
| Moodles | 42.13.2 | medium; several moodles are "Build 42, currently unavailable" |
| Knox Infection | 42.13.1 | medium: matches the Zombie article's chances |
| Panic, Endurance, Heavy load | 42.12.3 | low to medium: numbers may have moved in the 9 builds since |

Not yet read (see the end): Fitness, Tired/Sleep, Nutrition, Stressed, Pain, Noise, AI, Weather, First Aid, Skills overview, Traits and Occupations pages, vehicles, farming, crafting, animals.

## 1. Infection and wounds (what "damage" really means)

- Only zombie attacks infect (the Knox Infection). Chances at default settings: bite 100%, laceration 25%, scratch 7%. (The user remembers scratches as about 33%: the wiki says 7% since Build 41; check the game's code before encoding either.) Non-zombie injuries never infect with Knox.
- Timeline after infection: stress and a temperature rise within hours, nausea stages over the first two days, fever, death at about 72 hours (default Infection Mortality "2-3 days"), reanimation within a minute. No cure. A character with the Resilient trait gets 25% slower progression, Prone to Illness 25% faster.
- Sandbox: Transmission (Blood+Saliva default / Saliva only = only bites / Everyone's infected / None), Infection Mortality (instant ... 2-3 days default ... 1-2 weeks, never), Reanimate Time. Our server uses Transmission 1 (Blood+Saliva), Mortality 5 (2-3 days).
- Wound infection (bacterial) is a different, minor thing: dirty bandage or untreated open wound, treatable with disinfectant, clean bandages, antibiotics; never fatal by itself.
- 17 body parts, each with injuries: scratch, laceration, bite, deep wound, burn, fracture, lodged bullet/glass. Each injury has a healing time in hours (scratch 7-15, laceration 10-20, bite 50-80, deep wound 15-20, fracture up to 60 days; Fast/Slow Healer traits shift these). Injuries "cap" the maximum health until they heal. Neck wounds ignore the cap and can kill within minutes if not bandaged. Bleeding wounds need bandages (First Aid skill speeds things and improves outcomes).
- Reaching zero health is permanent death.

What we do today: the bridge reads one number (`getBodyDamage():getHealth()`) and the fake backend's "bite" is plain hit-point loss. The reward cannot tell a bite (a death sentence) from a bruise (recoverable). Design decision recorded in the journal.

To add: publish bitten/scratched/lacerated/infected flags per player and model bite and scratch events for fake clients with the real chances (configurable); an infected agent counts as dead for training; recoverable injuries (strain, bruises, falls) get small penalties; bandaging as an action and bleeding as an observation; healing time and the health cap if we want long-lived agents.

## 2. Combat: what changes the damage of a swing

All of these are things the fake client does not model, and together they probably explain why real swings averaged only about 0.19 of a zombie's health in our tests.

- **Weapon**: Baseball bat: weight 2.0, damage 0.8-1.1, two-handed (usable one-handed at 50% damage and a large endurance cost; our bot equips it in both hands). Heavier weapons cost more endurance per swing (modifier up to 3x for mauls, 1.3x for a frying pan).
- **Strength skill** (starts at level 5, no XP boost): melee damage multiplier 75% at level 0, +5% per level, 125% at 10; also push knockdown, carry capacity (6 at level 0 up to 20 at 10), muscle strain. Gains XP from exercise, carrying more than half the capacity, running, and melee hits. Values in the table came from build 41.78.16.
- **Weapon skill** (Long Blunt for the bat): damage +10% at level 3, +20% at level 7; range +20% at 7; endurance cost -10% at 8+. Gains XP from hits. Starts at 0 for most characters (Baseball Player and Brawler traits +1).
- **Endurance** (exertion from running, swinging, carrying): out of breath (25% used) cuts melee damage by 50% and attack speed by 7% and walking speed by 19%; high exertion (50%) -80% damage and sprinting off; excessive (75%) -90%, running off; exhausted (90%) -95% damage and -28% attack speed. Recovers slowly when idle (faster sitting or with high Fitness); tiredness slows recovery. A bot that runs to a zombie and then swings repeatedly is in the 50-90% damage-loss band quickly. **This is the first thing to check for the real-client combat gap**: read `CharacterStat.ENDURANCE` during a fight.
- **Panic**: grows when zombies are seen (about 3% per zombie, more from behind), recovers faster the longer the character has survived (up to 150 days), is reduced by Brave/Desensitized, doubled by Cowardly. Melee damage -0.2 / -0.3 / -0.4 at alarmed / frightened / terrified (an absolute subtraction, big against a bat's 0.8-1.1), critical chance down, vision narrowed; firearm accuracy drops sharply with distance.
- **Stress, tiredness, pain**: also lower combat ability; pain from injuries and "exercise fatigue", arm injuries and fractures cut damage severely.
- **Muscle strain**: every swing adds strain to arms (scaled by weapon weight, endurance modifier, number of zombies hit, reduced by weapon skill (-7.5% per level) and Strength (-10% per level)); strained arms reduce damage and attack speed. Two-handed equip halves the strain increase.
- **Heavy load** (weight over capacity): >100% capacity: 19% slower, 7% slower attacks; >125%: 37% slower, no sprint; >150%: 56% slower, no run, health drains to 75%; >175%: 75% slower. Our characters once carried 22 bats (weight 2.0 each).
- Sandbox knobs that touch combat: Melee Movement Disruption (slowed while swinging, default on), Weapon Multi-Hit (off), Endurance Regeneration, Injury Severity, Rear Vulnerability, Zombie Strength and Toughness, XP Multiplier (does not apply to Strength and Fitness unless enabled).

What we do today: fake client hits for a fixed lethal amount with no state; the real client has all of the above, and our bot ignores them (it keeps running and swinging).

To add: read and log these stats from real clients (Endurance, Panic, Stress, Fatigue, Pain, muscle strain, Strength, Blunt, Fitness levels) and compare per-swing damage against them; then put endurance, panic and strain into the observation and make fake-backend damage depend on them, so agents learn to pace fights (retreat, rest, swap places). Leveling for long-lived agents (the accounts persist across our runs, so levels will drift).

## 3. Zombies (Zombie article, current build)

- Senses: sight (cone, range from the Sight setting), hearing (sounds draw them: radios, engines, gunfire, shouting, footsteps, fighting), memory (they walk to the last place a survivor was seen, then go idle). Settings: Sight, Hearing, Memory, Cognition (doors, navigation), Day/Night activity.
- Speed (Zombie Lore Speed): sprinters / fast shamblers / shamblers / random; sprinters are the only kind faster than an unencumbered player walking away. Our server: Speed 4 (random), Strength 2 (normal), Toughness 4, Memory 2, Sight 5, Hearing 5 (look up what the codes mean before relying on them).
- Hordes: zombies group around a leader (Rally settings); waking the leader draws the group. Population grows to a peak around day 28 (population multiplier, peak multiplier, respawn hours). Metagame events (helicopters, distant gunfire) move hordes.
- Attacks: grab and bite (a grab holds the survivor in place), scratches and lacerations; rear attacks are more dangerous (Rear Vulnerability); several zombies attacking from different sides can drag a survivor down, which is treated as certain death (Drag Down option, on); zombies vaulting fences can lunge at a nearby survivor (Fence Lunge, on). Crawlers are slow and easy to avoid; "fake dead" zombies can get up.
- The fake client's zombie model does very little damage to players and does not grab or drag down, so the synthetic bite rule stands in; the real client takes real zombie damage.

To add: drag-down death when three or more zombies are adjacent from different directions; grab (movement held); rear attacks; zombie sight and hearing ranges and memory matching the real settings; noise from combat attracting more zombies (so fighting spots matter and squads should withdraw or pull zombies away from each other); horde leaders. Compare fake-zombie behaviour against real zombies with the same Sandbox values before tuning (the first matched tests used real zombies on the real client, fake ones on fake clients).

## 4. Character stats and moodles (what a long-lived agent has to manage)

Hunger, thirst, tiredness (sleep), stress, boredom, unhappiness, temperature (hot, cold, wet, windchill), sickness (cold, food poisoning), pain, bleeding, endurance, panic, heavy load, injured, restricted movement (barefoot, leg injuries, heavy clothes), drunk. Some Build 42 moodle icons exist but the effects are not active yet (concentrating, dizzy, scared, happy, ...). Sleeping greatly speeds healing and can bring nightmares (panic). Nutrition is a separate system (weight gain and loss) from the hunger moodle. Sandbox: Stats Decrease rate, Endurance Regeneration, Nutrition on or off, Starter Kit (school bag, bat, hammer, water, chips: on in our server), Free Traits, XP multiplier.

What we do today: hunger, thirst and fatigue are published and nothing else; episodes are about 40 seconds, so none of this matters yet.

To add (only when episodes get long enough): eat, drink, sleep and rest actions; bandage and first-aid actions on self and teammates (the user pointed out first aid as a reason to stay close); stress and panic in the observation.

## 5. Skills, traits, occupations

Skill groups: passive (Fitness, Strength), agility (Lightfooted, Nimble, Running, Sneaking), combat (Axe, Long Blade, Long Blunt, Maintenance, Short Blade, Short Blunt, Spear), firearm (Aiming, Reloading), crafting (about twelve), farming, survivalist (First Aid, Fishing, Foraging, Tracking, Trapping). Each has an XP rate affected by traits (Fast/Slow Learner) and the sandbox multiplier. Characters have about 40 positive and 40 negative traits plus an occupation that sets starting skill levels and traits (for example Brave, Cowardly, Desensitized, Resilient, Thick Skinned, Fit, Strong, Weak, Prone to Illness, Slow Healer, Adrenaline Junkie).

What we do today: whatever the default character creation produced, identical for every agent; nothing is varied or read.

To add: read each agent's traits and key skill levels into the observation or at least the logs; vary them across agents (a squad of different specialists is closer to real play); character creation currently takes defaults, so the first agents are all the same default survivor.

## 6. Sandbox settings we can use to build a curriculum (and to match the real game)

World settings the training server can change without code: zombie count and distribution, respawn, speed, strength, toughness, sight, hearing, memory, transmission and mortality, drag down, rear vulnerability, injury severity, bone fracture, melee disruption, weapon multi-hit, endurance regeneration, stats decrease, day length, starting time of day, darkness at night, loot rarity. A curriculum can start with weak, slow, short-sighted zombies and tighten toward the real defaults; the final evaluation should always use the settings a human game would use. Note that a world's sandbox values are stored in its save; changing the file after the world exists may not apply (check by reading the values back in game).

## 7. Prioritised roadmap for the environment

1. **Find out why real swings are weak** (small experiment): log endurance, panic, stress, strain and Blunt/Strength levels at each swing on the real client; correlate with damage dealt. Cost: a day of experiments, big payoff for deciding whether a combat model is needed.
2. **Wound types in reward and observation** (bite = death sentence, scratch/laceration chances, recoverable injuries cheap). Needed before any claim about "not dying to zombies".
3. **Zombie fidelity**: drag down, grab, rear attacks, sight/hearing/memory aligned with the real Sandbox values; noise attraction. Needed for squad tactics.
4. **Combat state model on the fake side** (endurance, panic, strain) once step 1 shows which of them matter, plus the retreat/rest actions it makes necessary.
5. **Per-agent variation**: traits, skills, starting kit; leveling over long runs.
6. **Care actions**: bandage, first aid on a teammate, eat/drink/sleep for long-lived agents.
7. **Cohesion band** reward (close but not too close) and noise-aware spacing.
8. Out of scope for now: vehicles, farming, crafting, building, foraging, animals, electricity and water, weather beyond what changes visibility and temperature.

Unknowns to settle by reading the game files rather than the wiki: whether the Build 42 melee damage formula still uses the multipliers above; the exact scratch chance (7% per the wiki versus the user's recollection of about 33%); what the numeric codes of our server's zombie settings mean; whether panic and endurance apply to the bot's swings the way the wiki says.
