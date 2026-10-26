# Approach

## Goal

Agents that act as survivors, driven by an external RL policy (Python), running faster than a human-played session, and able to scale from 1 agent to 4 agents cooperating in the same world.

## Key finding: the game ships a headless player client

Build 42.21's `projectzomboid.jar` contains `zombie.network.FakeClientManager`, a standalone program (it has its own `main`) that The Indie Stone appears to use for multiplayer load testing. From inspecting its class signatures with `javap`:

- It is launched with `-scenarios=<file> -id=<n> [-loglevel=<n>]` and loads the non-Steam network library (`ZNetNoSteam64`), so it targets a server started without Steam.
- Each fake client goes through the real connection flow: `CONNECT → LOGIN → CHECKSUM → LOAD_PROFILE → CREATE_PLAYER → PLAYER_CONNECT → RUN`.
- Built-in behaviours include `Stay`, `Line`, `Circle`, `AIAttackZombies`, `AIRunAwayFromZombies`, `AIRunToAnotherPlayers` and `AINormal`, plus melee hits on zombies.
- It contains a `ZombieSimulator` that takes "authority" over nearby zombies, because in PZ multiplayer zombie AI is simulated by the nearest client, not the server.
- The scenario file is JSON-like with sections for `client` (server host/port, timeouts, checksums for lua/script/anim), `player` (fps, damage, speeds) and a list of `movements` (spawn, type, destination, delays, horde creation, sounds).

This means real, server-recognised players can exist with no rendered game client.

## Candidate architectures

### A. Fake clients driven by a policy (preferred first experiment)

1 headless server (`-nosteam`) + N fake-client processes. Replace or wrap the built-in behaviours so each fake client streams observations to Python and applies actions from it.

- Pros: truly headless, cheap per agent, natively multi-agent (4 agents = 4 connections), and the server stays authoritative.
- Cons: the fake client is a protocol-level puppet, not a full `IsoPlayer`. It moves and hits but likely does not do inventory, crafting, eating, or timed actions. Zombies near the agents are run by the fake client's simplified `ZombieSimulator`, not the real zombie AI, so fidelity is lower.
- Unknowns: whether 42.21 servers accept it without changes (checksums, auth), and how much of it can be extended without reimplementing it.

### B. Server-side NPCs via Java agent + Lua

A `-javaagent` on the server JVM spawns and drives player-like characters itself, keeps chunks loaded around them, and runs the real zombie AI on the server.

- Pros: full game fidelity, no clients at all.
- Cons: significant reverse-engineering; the engine assumes zombies are owned by clients and chunks are loaded by players.

### C. Rendered clients (fallback / ground truth)

One normal client per agent at minimum settings, with a Lua mod exposing state and actions over a file or socket bridge.

- Pros: full fidelity, lowest engineering risk, easy to debug visually.
- Cons: expensive per agent; four rendered clients on one PC is heavy.

## Plan

1. **Smoke test A.** Start a local `-nosteam` server, run one stock fake client with a minimal scenario, and confirm it logs in and appears in-world (verified by joining with a normal client).
2. **Measure.** Check what the fake client can and cannot do, how zombies behave around it, and the server tick rate with 1 and 4 fake clients.
3. **Bridge.** Build an observation/action bridge (Java side next to the fake client, Python side as a Gymnasium / PettingZoo environment for multi-agent).
4. **Decide** whether A's fidelity is enough, or whether to invest in B (or use C for evaluation runs).

## Smoke test result (Build 42.21, 2026-10-24)

- A stock fake client logged into a local `-nosteam` server and reached `RUN` in under a second (about 0.9s). No checksum rejection with the `checksum` block omitted.
- A normal client joining `127.0.0.1` sees "Client1" in the online players list, so the server treats it as a real player.
- Scenario gotcha: `config.movement` sits beside `config.player`, not inside it. The loader swallows JSON errors and only logs "Scenarios file load failed"; `java -Xlog:exceptions=info` reveals the real exception.
- Not yet measured: zombie behaviour around the client, server tick rate with 1 and 4 clients, and whether multiple fake clients collide on local UDP port 17500.

## Measurements and extensibility (Build 42.21, 2026-10-25)

Setup: one local `-nosteam` server (4 GB heap, ZGC), then 1 and 4 fake clients (`scenarios/multi-4.json`, one behaviour each, all spawning near 10650,9800). Single runs on Joshua's PC, so treat the numbers as rough.

- **Multi-client works.** All four clients reached `RUN` (about 10s apart as I started them). Each client process picks its own local UDP port automatically (17501 to 17504), so the 17500 collision worry is moot.
- **Server cost is small.** CPU (percent of one core): about 3 idle, 17 with 1 client, 29 with 4 clients, server working set around 4.6 GB. Per-agent cost looks cheap; world streaming dominates. Real tick rate was not measured (no obvious counter in the log).
- **Zombies exist and fight back.** The fake client "owns" zombies near it (14 at connect, 25 owned of 63 known later), and the count falls steadily for the `AIAttackZombies` agent, so its hits kill zombies.
- **Not extensible as-is.** `FakeClientManager$Player`, `$Network` and `$Movement` are package-private classes with private methods and fields (`run`, `hit`, `x`, `y`, `weaponId`). Only `Movement.moveTo(x,y)` and the connect/disconnect calls are public. A bridge would need reflection or our own launcher class, and it cannot do inventory, crafting or timed actions: it is a protocol puppet.
- **Option B hint.** `zombie.characters.IsoPlayer` has a `setNpc(boolean)` and a constructor taking a `SurvivorDesc`, so server-side NPC players are at least representable. Not tried.

### Where this leaves the options

- A (fake clients): feasible now for position, movement and melee only. Good enough for a first navigation or combat policy, not for survival play.
- B (server-side NPCs): highest fidelity and no client processes; unproven and needs reverse engineering.
- C (rendered clients + Lua bridge): safest for full game actions; about 3 GB heap per client, so 4 at once is heavy.

## Options compared (static analysis of 42.21 plus smoke/measurement runs, 2026-10-25)

Evidence level: **[run]** observed on this PC, **[javap]** read from class signatures/strings (behaviour not exercised), **[unverified]** inferred or from web search only.

### A. Fake clients (`FakeClientManager`) driven by a policy

What it can observe: its own position, remote players' positions (`RemotePlayer.x/y/z`, `PlayerPacket`), zombie positions/health/walk type (`Zombie`), chunk object state responses, and player stat packets (health, stats, effects, xp) [javap]. No inventory or rendered view.
What it can do: move to a target (`Movement.moveTo`), `Stay/Line/Circle`, built-in AI modes, melee hits on zombies with a hard-coded `Base.Axe`, create hordes, make sounds, teleport, disconnect/reconnect [javap, partly run].

Pros
- Works today: connects, spawns, and fights on the unmodified 42.21 server [run].
- Cheap: 4 clients cost the server about 29% of one core, and each client process is a small JVM (-Xmx1g in our script) [run].
- Natively multi-agent, server-authoritative, real `IsoPlayer`s on the server (shows in the player list) [run].
- No rendering or GPU, so many agents and fast resets are plausible.
Cons
- Protocol puppet: no inventory, crafting, eating, looting, building, doors/containers, or timed actions [javap].
- Zombie behaviour comes from the client's simplified `ZombieSimulator` (it takes authority for nearby zombies), so fidelity differs from vanilla [run/javap].
- Fake client internals are package-private/private, so a bridge needs reflection or classes injected into the `zombie.network` package; fragile across builds [javap].
- Observations are packet-level (no tile map or visibility), so we would need to rebuild world state ourselves.
- Anything beyond move/melee means implementing more of the client protocol ourselves.

### B. Server-side NPCs (Java agent or class patch + Lua)

Facts: `IsoPlayer.setNpc(boolean)` exists and `GameServer.Players` / `IDToPlayerMap` are public static, so injecting an extra `IsoPlayer` is mechanically possible [javap]. But zombie ownership (`popman.NetworkZombieManager`) is keyed by `UdpConnection`, and chunk loading / `ServerMap.characterIn` follow players [javap]. A connectionless NPC may not own zombies or keep chunks loaded [unverified].

Pros
- Highest ceiling for fidelity: real server-side player objects and the real zombie AI, no client processes at all.
- Could use server Lua with the full game API for actions on those characters [unverified].
- Cheapest per agent if it works.
Cons
- Unproven; likely the most reverse-engineering. Authority/chunk-loading assumptions (above) may need patching core classes.
- Needs a `-javaagent` or replacing classes ahead of `projectzomboid.jar` on the classpath (classpath is `.;projectzomboid.jar`, so replaced classes load first). Fragile across builds, and we must never commit game code [javap].
- Existing NPC mods (e.g. Bandits) are Lua mods and, as far as the web search showed, work in-engine with zombie-based characters; their exact design was not confirmed, and they carry no license we can reuse [unverified].
- Players spawned this way may not sync correctly to clients, which matters for human spectators.

### C. Rendered clients + Lua bridge

Facts: the stock client launches from our script with `-nosteam`, and the jar's argument parser accepts `+connect <host>`, `+password <pw>`, `-nosound`, `-novoip`, `-cachedir=`, `-modfolders` [javap]. Lua has file I/O (`getFileReader`, `getFileWriter`/`getModFileWriter`, `fileExists`, directory listing) limited to the user Lua/cache folders [javap], and a mod can read and drive its own `IsoPlayer`.

Pros
- Full game: inventory, crafting, timed actions, real zombie AI, real map; ground truth and easy to watch.
- Observations and actions use the same Lua API human players use; the least engine surgery.
- Pure Lua mod, no class patching; files as the bridge need no networking code.
- Auto-connect args mean runs can be scripted [javap].
Cons
- Heavy: one JVM and GPU window per agent (stock heap 3 GB); four at once is a lot for one PC [javap/estimate, not measured].
- Real-time only: no obvious way to run faster than 1x, and no frame-skip/headless mode found yet [unverified].
- File polling latency adds delay each tick; Lua is sandboxed (no sockets), so Python must poll files [javap].
- Focus/rendering quirks with several windows; a character-creation/login flow must be automated.
- Training throughput is the key weakness.

### D. (Extra) Own protocol client in Python/Java

A from-scratch client that speaks the RakNet protocol, borrowing the fake client's flow (`CONNECT, LOGIN, CHECKSUM, LOAD_PROFILE, CREATE_PLAYER, PLAYER_CONNECT, RUN`). Pros: no subclassing hacks, full control, light. Cons: large effort to reimplement serialization and packet set; no tile or inventory state unless we add it; same fidelity limits as A.

### Preliminary read

- For getting a first multi-agent loop running: A, because it already connects four agents cheaply.
- For survival gameplay beyond fighting: C is the only option known to expose everything, but throughput is its limit; B could beat it if the zombie-authority and chunk-loading problems are solvable.
- Suggested next experiments, in order: (1) a reflection bridge on A that reads observations and sets `moveTo` targets; (2) a minimal C mod that dumps state to a file and reads one command per tick, to measure real latency and per-client cost; (3) a time-boxed B probe: can a server-side `IsoPlayer.setNpc(true)` keep chunks loaded and zombies simulated?

## Option B findings

### B1: Lua-spawned NPC player (run, 2026-10-25)

Probe mod `mods/RLProbe` (install with `scripts/install-mods.ps1 -Enable RLProbe`; the probe also needs `PauseEmpty=false` in the server ini so the server ticks with nobody connected).

- `IsoPlayer.new(getCell(), SurvivorFactory.CreateSurvivor(), x, y, z)` works from **server** Lua, and `npc:setNpc(true)` is accepted. The NPC gets an ID and a position.
- It does **not** make the world load. 600 ticks after spawning at 10650,9800 the square under it was still unloaded, `zombiesInCell` stayed 0, and `onlinePlayers` stayed 0. Chunk loading and zombie population on the server follow connected players' positions (`ServerMap.characterIn`, called from `GameServer`), not `IsoPlayer` objects that merely exist.
- `ServerMap` (the class with `characterIn`, `loadOrKeepRelevent`, `importantAreaIn`) is not exposed to Lua, so the chunk loading hook needs Java: a `-javaagent` or a patched class.

### B2: Java agent as a reflection inspector (run, 2026-10-25)

`agent/` holds a Java agent (`scripts/build-agent.ps1`, started with `start-server.ps1 -JavaAgent`) compiled without any game classes. It registers two Lua globals on the server's main Lua environment, so server Lua (running on the game's own thread) can reach Java-only APIs:

- `rlGet("pkg.Class.staticField.method(1,2).field")` evaluates a reflection path and returns its string value. Combined with a text file the probe re-reads (`<cache>/Lua/rlprobe_exprs.txt`), this lets us inspect and call server internals **without restarting** (a boot takes about 4 minutes).
- `rlLoadArea(x, y, z)` calls `ServerMap.characterIn` / `importantAreaIn`.

Findings:
- Server cells are 64x64 squares (`ServerMap.CellSize` 64, 8 chunks per cell). World square 10650,9800 is server cell 166,153.
- Calling `ServerMap.loadOrKeepRelevent(166,153)` does register and load the cell (`releventNow` 1, `loadedCells` 1), but `releventNow` is cleared every frame. Calling it only every 30 ticks left `loadedCells` at 0. So a player-less area needs to be marked relevant **every tick**.
- The probe's "square loaded" check (`getCell():getGridSquare`) is always false on a dedicated server, even with a real player present. Ignore it; use `zombiesInCell` and the `ServerMap` expressions instead. With a fake client connected at the same spot the probe saw 53 to 86 zombies.
- Lesson on tooling: `tail -f | grep | cut` buffers and hides monitor output; read the log file directly.

### B3: NPC in `GameServer.Players` loads the world with no clients (run, 2026-10-25)

`GameServer.main` loops over the public static `GameServer.Players` list every frame, adds each alive `IsoPlayer` to the cell object list and calls `ServerMap.characterIn(player)`; the relevance list is rebuilt every frame in that window, which is why external per-tick `characterIn` calls from Lua never stuck.

Adding the Lua-spawned NPC to that list (agent function `rlAddPlayer`, `Players.add(npc)`) made the server load the world around it with **zero connected clients**: `loadedCells` 1, `ServerMap.zombieMap` 15 zombies, and the square under the NPC loaded. `ImportantAreaManager.updateOrAdd(x,y)` registers an area but did not load a cell by itself.

Open question: are those zombies simulated (they have no owning `UdpConnection`)? Checked next.

### B4: zombies near a connectionless NPC are inert (run, 2026-10-25)

With the NPC in `GameServer.Players` and teleported (`setX/setY`) to 3 tiles from the nearest zombie, that zombie stayed put for several 15 second reports: no target, state `GenericDefaultState`, position unchanged, and `isRemoteZombie()` true. `NetworkZombieManager.getUnauthorizedZombieCount()` was 15 of 15. So the world and zombies **load** around a server-side NPC, but no zombie AI runs: in this server, zombie simulation is delegated to the owning client and an unowned zombie is treated as remote.

### B5: server-side NPC cannot walk, and zombie ownership follows connections (run, 2026-10-25)

- With a fake client connected near the NPC, 89 zombies were loaded and 48 remained unauthorized (unowned, inert); the rest were owned by the client's connection. Zombie simulation is therefore delegated per `UdpConnection`, and a connectionless NPC (or any zombie nearer to it than to a client) gets no AI.
- `getPathFindBehavior2().pathToLocation(...)` on the server-side NPC returned without error but the NPC stayed in `IdleState` at the same position for several reports. Its movement/state machine is not driven by the dedicated server loop.

**Option B verdict so far:** the world will load around a server-side NPC (cheap, no client), but both zombie AI and NPC locomotion would have to be added by patching engine classes (override `isRemote`/ownership for the server, drive `IsoPlayer.update` for NPCs). That is a large, fragile reverse-engineering project, and unlike the fake client the result is not a supported code path. Not pursued further for now.

### New candidate: E. Fake clients + server-side Lua/Java bridge

The fake clients are genuine `IsoPlayer`s on the server (they appear in `GameServer.Players`, the world loads and zombies run around them, owned by the client). That means server Lua (with our agent as a transport) can **observe** everything about them (stats, inventory, nearby squares and zombies) and perform **actions that do not need locomotion** (give/remove items, eat, set stats, spawn things), while the fake client supplies movement and melee. A socket in the agent gives Python a low-latency bridge instead of file polling.

## Option E: fake clients + server-side Lua bridge (run, 2026-10-25)

`mods/RLBridge` (server Lua) runs every 60 ticks over `getOnlinePlayers()`; the fake client is an ordinary player there. One line per player (sample from a run with the attack-zombies behaviour):

```
RLOBS {"user":"Client1","x":6046.8,"y":5275.1,"z":0,"health":100.0,"hunger":0.155,"thirst":0.142,"fatigue":0.000,"items":3,"zombiesNear":4,"nearestZombie":2.1,"kills":5}
RLACT give Apple to Client1 ok=true items 2 -> 3
```

- **Observation works** for position, health, hunger/thirst/fatigue (Build 42 stats API: `getStats():get(CharacterStat.HUNGER)`), inventory, kill count and zombies from the server cell list (the cell zombie list works on the server once a client owns the area).
- **Actions work without locomotion:** `getInventory():AddItem("Base.Apple")` took effect on the server (items 2 to 3). Not yet checked: whether the item is visible to the fake client (it has no inventory UI), eating it, or consuming via timed actions.
- Server Lua tick: roughly 10 `OnTick` per second on this server (150 ticks per 15 s).
- Correction: the fake client does take damage. Over a 29 minute run Client1's health fell from 100 to 25 (and stayed there across relogins; player state persists per account) while it killed about 310 zombies.
- **Spawn:** the scenario's `spawn` (10650,9800) did not decide where the player ended up; the client was at about (6082,5254) (Riverside) soon after login, so the server's spawn handling placed it. Needs checking if we want fixed start locations.

## Validation against a rendered client (option C), first pass (run, 2026-10-25)

Setup: same server, same `RLBridge` observer applied to both a fake client (`Client1`, `AIAttackZombies`) and a human-driven rendered client (`admin`, joined with `scripts\start-client.ps1`, which uses an isolated `.pzclient` data folder holding the repo mods; the server's required mods must exist on the client). `scripts/analyze_obs.py` summarises the server log. Observations are about every 6 s.

| Measure | Fake client | Rendered client (human) | Verdict |
|---|---|---|---|
| Steady movement speed | 1.40 tiles/s (`run`=5) | about 2.1-2.3 sustained, 1.6-1.9 slower, bursts 2.8-5.7 | Different at defaults, **calibratable**: `config.movement.motion.run`=8 gives a steady 2.33 tiles/s (about 0.29 tiles/s per config unit, linear in the one point tested) |
| Kills | about 11 per minute, 315 total | 2 in about 90 s | **Not comparable**: one cautious human fight, unknown weapon, different local zombie density |
| Damage taken | 100 to 25 over 29 min | none in that 90 s | Not comparable |
| Server sees it as a player | yes | yes | Equivalent for observation and server-side actions (same Lua API) |
| RAM | 134 MB | 2951 MB | about 22x cheaper |
| CPU (one core = 100%) | 2.8% | 181% (plus GPU, window open, human playing) | about 65x cheaper |

Caveats: one sample each for cost; a single 90 s human trial; the rendered client was visible and being played.

**What is and is not established**
- Established: a fake client is a first-class server player (Lua sees the same object type), it can fight zombies, and its speed can be tuned to match a real player. Per-agent cost is one to two orders of magnitude lower, so many more agents fit on one PC.
- **Not established:** that combat and zombie behaviour are equivalent to the real game. Zombies near a fake client are driven by the fake client's own simplified simulator, whose hit/kill and damage model I have not compared to the real one; the kill-rate gap hints they may differ.
- **Not established:** that training can run faster than real time. The server loop and fake client both run on wall-clock time. Today the speedup is only parallelism (more cheap agents), not a faster clock.

**What a proper equivalence test needs:** a scripted rendered-client agent (client-side Lua mod, or computer-use) doing the same task as a fake client in the same place, with the same weapon, over repeated trials, comparing time-to-kill, damage per zombie contact, zombie aggro/approach distances and speeds.

## Faster than real time (run, 2026-10-25)

Question: can training run faster than wall-clock, and by how much?

**Parallelism (scale test, `scripts/scale-test.ps1`, one server, 1 to 16 fake clients, `scenarios/scale-16.json`).** Server CPU 6, 18, 47 and 108 percent of a core at 1, 4, 8 and 16 clients, roughly 5 to 7 percent of a core per client, about 4.1 to 4.6 GB server RAM. The server's Lua tick stayed at 10 Hz with 16 clients (14 of the 16 were reporting observations; two had not started reporting, cause not checked). Fake client processes use about 130 MB each (2 GB for 16). On this PC that is plenty of headroom, but a 16-client run already costs about one core, and part of it is the observer itself (it loops over every zombie per player each 6 s). Kill counts were too noisy to use as a work metric.

**Movement only, no clock change.** The scenario `run` speed can simply be raised: 3x (`run`=24) gave a steady 6.93 tiles/s, and the server accepted it (default anti-cheat settings, `AntiCheatSpeed=2`; no kicks logged). But this speeds up only the player, not zombies or timers, so it changes the game rather than fast-forwarding it.

**Clock scaling in the fake client JVM (agent, `-TimeScale`).** `agent/` can rewrite `System.nanoTime`, `System.currentTimeMillis` and `Thread.sleep(long)` call sites in chosen classes to a scaled clock (`RLClock`, `-Drl.timescale=K`). It does this by re-pointing the constant-pool method reference to a new class entry, so no bytecode library is needed, and only the fake client classes plus `UpdateLimit` are touched. Result (Client5, server unscaled): speed 2.35 / 4.58 / 9.15 / 18.25 tiles per real second at K = 1 / 2 / 4 / 8, i.e. linear. The fake client stays at about 150-170 MB and 6 percent of a core even at K=8, and the server kept accepting it. Unmodified state (hunger, thirst) is server-side and was unchanged across client scales, as expected.

**Clock scaling in the server JVM.** Same agent with `classes=zombie/` (`start-server.ps1 -TimeScale 2`). The server booted and ran with about 110 `zombie.*` classes rewritten; the Lua `OnTick` rate doubled from 10 to 19.9 per real second, the log timestamps stay real time. Gotcha: a leftover server process holds port 16261 and the agent jar, so the next server fails with `Connection Startup Failed. Code: 5`.

### Full-stack time scaling results (run, 2026-10-25)

Server and fake clients both started with the clock agent at the same factor K (`start-server.ps1 -JavaAgent ... -TimeScale K`, `run-fake-client.ps1 -TimeScale K`). Server tick, world clock and client speed measured against the wall clock (snapshots of the `RLBridge` output, `analyze_obs.py --snap`).

| K | clients | Lua ticks per real s (ideal 10K) | world clock, game hours per real hour (ideal 16K) | client speed, tiles per real s | server CPU (percent of a core) |
|---|---|---|---|---|---|
| 1 | 1 | 10.0 | 16.0 (expected) | 2.35 | about 6 |
| 2 | 1 | 19.9 to 20.0 | 31.4 (1.96x) | 4.58 | 31 |
| 8 | 4 | 71.8 (median 80, dips to 52) | 107.2 (6.7x) | 18.2 (single client run) | 84 |

- Everything that the agent rewrites runs K times faster, and **per game second the dynamics are unchanged** for what I measured: movement is 2.3 tiles per game second at every K.
- At K=8 the server falls behind a little (90 percent of target ticks, 84 percent of the ideal world clock). The practical ceiling on this PC for 4 clients is therefore somewhere around 8x; K=16 would likely saturate the server (it is already at 0.84 of a core and its cost per real second rises faster than K: 6, 31, 84 percent at K=1, 2, 8). Not tested.
- The fake client is cheap at every K (about 150-170 MB, 6 percent of a core), so the server is the bottleneck for fast-forwarding, not the agents.
- Net: 4 agents at 8x is roughly 27 to 32 agent-seconds of play per real second, from one server plus 4 small JVMs and no GPU, versus 1 agent-second per real second per rendered client (which costs about 3 GB and 2 cores).
- Caveats: only classes whose names start with `zombie/` are time-scaled on the server, and native code (RakNet, the native zombie population thread) uses its own clocks, so some timers may not scale; the two-sample hunger/thirst values are too coarse (3 decimals) to say whether stat decay scales, which is why world clock was used instead; the kill counts at K=8 (225 per minute across 4 clients) are not a validated measure of equivalence.

## Python bridge, first working pass (run, 2026-10-25)

Layout: `agent/` (Java), `mods/RLBridge` (server Lua), `pzrl/` (Python), `scripts/bridge_smoke.py`.

- **Server channel** (`-ChannelPort 17600`, agent argument `channel=`): server Lua calls `rlPublish(line)` / `rlPoll()`; the agent forwards lines over a localhost-only TCP socket. `RLBridge.lua` publishes one JSON line per 5 server ticks (every 0.5 game seconds at any clock factor) with every online player (position, health, hunger, thirst, fatigue, kills, wielded item, bag, the nearest zombies) and handles commands `heal`, `give`, `tp`, `zspawn`, `zclear`, `cfg`, acking each one.
- **Client control** (`-ControlPort`, agent argument `control=`): a localhost socket inside each fake client JVM that steers it by reflection: `goto x y`, `speed`, `say`, `tp`, `weapon id`, `info`. A scenario mover of type `Line` walks to the last `goto` target and stops, which is how the Python env moves agents.
- **Tested:** 2 fake clients connect, observations stream, `goto` moves a client about 2.3 tiles per game second, `heal`, `give` and `zspawn` work, and the `StarterKit` sandbox option (set `StarterKit = true` in the server's `*_SandboxVars.lua`) gives every new fake-client character a bag plus four items, so the server-side part of that option does run for fake clients. The bat sits in the bag, not in the hands.
- **Gotchas found:** a fake client connects after `connection.interval x id` ms (5 s per id by default, so id 30 waits 150 s); the generated scenarios set the interval to 200 ms. Starting a client with an id that is already logged in gets it kicked as a duplicate. `run-fake-client.ps1` array building needs the agent argument in its own variable (a `+` inside an array literal glued two arguments together).

## Python environment, first results (run, 2026-10-25)

`pzrl/env.py` is a PettingZoo-style parallel environment (reset/step, per-agent dicts, no hard dependency on pettingzoo or gymnasium; neither is installed here). 9 discrete actions (stay plus 8 compass moves), 25-dim observation (own health/hunger/thirst/fatigue/has-weapon/has-bag, the 4 nearest zombies and 2 nearest teammates as relative offsets, nearby-zombie count). One step is 1 game second regardless of the clock factor. Reset heals, teleports (the fake clients are promoted to admin through `rlPromote`, otherwise the server reverts client teleports), clears and respawns zombies. At startup each agent gets the starter kit (server option) plus a bat wielded through the control socket (`give` returns the item id, `weapon <id>` makes the fake client wield it).

Task rewards (`pzrl/tasks.py`): survive (alive bonus, health loss and death penalties), rendezvous (change in distance to nearest teammate plus a meeting bonus), fight (kills plus the survival terms). `pzrl/baselines.py` has scripted policies used as sanity checks.

First run, 4 agents, clock factor K=4, 60 steps per episode (`scripts/env_tasks_demo.py`):

| task | policy | game s per real s | mean return | notes |
|---|---|---|---|---|
| survive | random | 3.78 | 0.60 | 8 kills, no deaths |
| survive | flee nearest zombie | 4.00 | 0.58 | 1 kill, no deaths |
| rendezvous | random | 3.86 | 0.42 | final min pair distance 218 tiles |
| rendezvous | move toward nearest teammate | 4.00 | 15.35 | final min pair distance 1.1 tiles |
| fight | random | 4.00 | 3.10 | 10 kills |
| fight | move toward nearest zombie | 3.87 | 11.34 | 43 kills |

- The environment delivers the clock factor: 3.8 to 4.0 game seconds per real second at K=4 with 4 agents.
- Rendezvous and fight discriminate between random and a simple policy (36x and 3.7x return). Survive does not yet: nobody dies or loses health in 60 steps because the fake client melee kills any zombie in reach at once, so the task has no pressure. See the tuning below.

### Making survival real: explicit melee and bite damage (run, 2026-10-25)

Findings that shaped the final environment (4 agents, K=4, 120 steps, bat equipped, 14 zombies 6-12 tiles away, zombie behaviour `Attack`):

1. **The built-in melee is too strong to leave automatic.** The fake client hits any zombie within 2 tiles once per `attackPeriod`. Standing still, an agent killed 8 to 75 zombies in 2 minutes and lost almost nothing. Lowering `config.player.damage` (6x) and removing the weapon did not help: kills are decided by the server from the hit packets, and the config value only changes the client's own bookkeeping. So melee is now **explicit**: `autoattack off` turns the built-in swing off (cooldown set to a huge period) and an `attack` action performs the same 2-tile hit on demand (`RLClientControl`, `PZParallelEnv` action 9).
2. **Zombies reach the agent but do no damage.** An idle agent surrounded by four zombies at 0.1 tiles lost about 0.1 health per second, and the sandbox option `ZombieLore.Strength = Superhuman` made no difference (0 loss over 10+ seconds). The fake client's simplified zombie model walks them up to the player but its attacks effectively do not hurt. So `RLBridge.lua` has an explicit **bite rule**: every publish, each zombie within `biteRange` (1.2 tiles) removes `biteDamage` (1.5 hp per zombie per game second) from the player. This is a synthetic stand-in for real zombie attacks, not a measurement of them, and it is tunable (`cfg|biteDamage|x`).

Result with both changes (`scripts/env_tasks_demo.py 4 4 120 survive,fight idle,random,scripted 1.0 6 12 Attack Base.BaseballBat 14`):

| task | policy | game s per real s | mean return | kills | mean final hp | deaths (of 4) |
|---|---|---|---|---|---|---|
| survive | idle | 4.00 | -2.57 | 0 | 49.7 | 2 |
| survive | random | 3.94 | 0.49 | 1 | 94.4 | 0 |
| survive | flee nearest zombie | 3.98 | 0.30 | 0 | 85.0 | 0 |
| fight | idle | 4.00 | -3.24 | 0 | 51.3 | 2 |
| fight | random | 4.00 | -1.20 | 2 | 75.5 | 1 |
| fight | walk to zombie and swing | 4.00 | 10.44 | 42 | 78.9 | 0 |

Survival now punishes standing still (a learnable signal), and fight has a large gap between random and a simple scripted policy. The simple "flee" policy is not better than random walking, so survival still has headroom for a learned policy. Rendezvous earlier (K=4): random 0.88, move toward the nearest teammate 24.8 with final pair distance 2.9 tiles.

### What is and is not established for the curriculum

- Working: spawn, reset (heal, teleport, zombie clear and respawn), explicit move/attack actions, per-agent rewards for survive, rendezvous and fight, starter kit plus bat, and a clock factor of 4 delivering 3.9 to 4.0 game seconds per real second with 4 agents (the server kept up to about 8x in the earlier load test).
- **Not** equivalent to the real game: zombie damage is the synthetic bite rule above; the melee model is the fake client's (2 tile reach, fixed hit period, server-decided kills); zombies are driven by the fake client's simplified simulator. Conclusions from policies trained here should be checked against a rendered client before being trusted.
- Not done: any learning algorithm (only scripted baselines were run), a held-out check that a trained policy transfers to the rendered game, and long-run stability (all runs were minutes long).

## Real (rendered) client as the deployment target: first measurements (2026-10-25)

Goal: train cheaply with fake clients, then show the trained agents working together in the rendered game. For that the two backends should share one interface (same observations, same actions), so a policy trained on the fast backend runs unchanged on the rendered one. Observations already come from server Lua and work for any player; only the action side differs (walk, attack).

- **No headless real client.** The game has no built-in no-render mode (only dummy sound classes, used by the dedicated server). `+connect ip:port` is for the Steam join flow and leaves a blank window with `-nosteam`.
- **Auto-login works.** `mods/RLClient` (client-side Lua, enabled through the client's own `mods/default.txt` by `scripts/start-client.ps1 -User Client40 -Hash 0`) waits for the main menu, reads `Lua/rl_client.txt` from the client's isolated cache (`.pzclient`) and calls `ConnectToServer.instance:connect(...)`, the same call the Join dialog makes. A fake client's account can be reused by a rendered client when password hashing is off (the fake client sends its username as an unhashed password; with hashing on the server answers "Wrong username or password").
- **Next blocker: character creation.** After login the rendered client lands on "Select spawn location" (the account has no character the real client can load), so character creation (spawn, profession, traits, appearance) has to be automated or completed once by hand.
- **Cost of a rendered client, measured:** even at 640x480 and 30 fps with no sound or voice, about 3.5 to 4.2 GB of RAM and about 110 percent of a core at the menu and loading stages. The cost is textures, models and Lua, not pixels, so a no-render real client (patching out rendering) would still need those unless loading is also skipped. Screenshots of the OpenGL window through `CopyFromScreen` or `PrintWindow` come out blank; reading the game's console log and the server channel works.
- Pitfalls: the game rewrites a missing or minimal `options.ini` with defaults (1920x1080 fullscreen), so the launcher now copies a normal options file into the client's own folder and changes only window size and frame rate.

**Rendered client in the world (measured 2026-10-25, 640x480).** After auto-login the new account passes through four screens: spawn selection (Muldraugh), trait picking, appearance picking, then into the game. The player (Client40) then shows up on the server channel like any fake client (hp, items 11, bag true, zombie list), so the same observations work for rendered and fake clients. In-world cost: about 3.5 GB RAM and 140-145% of a core for the client, against about 1.1-1.3 GB and 14% of a core for the server with one player. A fake client is a small fraction of that, so rendered clients are for evaluation and recording, not training. Next: automate the three creation screens in RLClient.lua.

**Unattended rendered-client start (2026-10-25).** A fresh account now goes from launch to in-world with no clicks: `RLClient` logs in; `RLAutoCreate.lua` (inside RLBridge, because the client reloads the server's mod list after connecting and drops client-only mods) accepts spawn, traits and appearance with defaults after a 45-frame settle; the agent's `autostart` option sets `GameLoadingState.forceDone` once "Click to Start" shows (calling `Done()` does not work, the click is read from the mouse into that flag). Gotchas: any client Lua file must also exist in the server's mod folder, and the server's Lua checksum is taken at boot, so adding one needs a server restart (otherwise: kicked for "Lua incorrect checksum"); a separate client jar avoids the lock on the server's agent jar (`RL_AGENT_OUT` for build-agent.ps1, `RL_AGENT_JAR` for start-client.ps1). In the world the 640x480 client uses about 4.0 GB and 138% of a core.

**Rendered-client bot (2026-10-25).** `pzrl/rendered.py` (`RenderedControl`: goto, stop, attack, equip, info) sends `bot|user|cmd|a|b` over the server channel; RLBridge.lua forwards it with `sendServerCommand` to `RLBot.lua` on the rendered client, which walks with the game's own `ISWalkToTimedAction` (verified: moves toward the target, detours around obstacles; a target on a zombie's own tile does not path), equips the bat (both hands), and swings with the game's own combat code. Findings from getting the swing to work: (1) `pressedAttack()` is ignored while the player is in a hit-reaction or knocked-down state, so the bot raises the weapon (`setIsAiming(true)`) and retries every frame until `isAttackStarted()`; (2) the aim vector of a local player comes from the mouse cursor, so with the cursor idle the server logs attackType "miss" and damage of about 0.017; pointing the cursor at the zombie (`Mouse.setXY` from `ISCoordConversion.ToScreen`) gives real damage (zombie health 0.97, 0.84, 0.68, 0.51, then dead after about 6 swings; some swings still register as "miss"); (3) the rendered player is hurt by zombies for real (health fell 100 to 74 in 20 s next to three zombies, and a knockdown with several zombies killed it), unlike the fake client, which is why the synthetic bite rule is only needed there; (4) the server compares client Lua to its boot-time copy (kick or red 'doesn't match' screen), so for iteration `RLBot.lua` runs `<cache>/Lua/rl_bot_dev.lua` on a `reload` command, and `AntiCheatChecksum=4` was set in the research server's ini. Not done: kill counter in the bridge stays 0 for rendered kills (zombie count drops), respawn after death, hit rate and damage per swing are still below what the fake client's melee gives, one-handed versus two-handed use is not an action yet (the bat is always two-handed).

**Rendered backend in the env (2026-10-25).** `PZParallelEnv(..., backend="rendered")` (1x only) launches real 640x480 clients (`Launcher.start_rendered`, one login per 20 s), drives them with `RenderedControl` through the bot commands, and reads the same server-side observations, so the same policies and baselines run on both backends. First run, `scripts/env_rendered_demo.py fight scripted 45 1 2` (one agent, bat, zombies 5-8 tiles away): 45 steps in 45 s real time, health 100 to 61, zombie count 3 to 2, return -0.33, no crash. A fake client has to be compared on the same task before calling the two equivalent; known differences so far are that rendered zombies do real damage (no synthetic bite rule) and rendered swings are slower and less accurate (hit and kill rate still to measure), and rendered clients cost about 4 GB and 1.4 cores each.

**Fake backend vs rendered backend, same task and baselines (2026-10-25, `scripts/compare_backends.py fight 60 3 2`, 1 agent, bat, both at 1x, 3 episodes per cell; raw rows in logs/compare_backends.json).**

| backend / policy | kills (counter) | zombies near at start | damage taken | path walked (tiles) |
|---|---|---|---|---|
| fake / idle | 0 | 13.7 | 44 | 0 |
| fake / scripted | 5.0 | 4.0 | 64 | 23 |
| rendered / idle | 0 | 2.0 | 87 | 0.8 |
| rendered / scripted | 0.7 | 1.0 | 28 | 5.3 |

What this does and does not show. (1) The episodes are not matched: the fake runs started with 4 to 20 zombies near the agent (the world's own population at that spawn plus the 2 spawned), the rendered runs with 0 to 2, so absolute kills and damage are not comparable yet; the rendered scripted runs had few zombies left to fight (the 3 episodes started with 2, 1 and 0). Spawns must be matched (same coordinates, zombie clearing radius) before drawing conclusions. (2) Damage: a rendered idle player lost 85 to 89 health in about 20 s to two zombies that walked up to it, and the run ended at death threshold, whereas a fake idle player lost 0 to 100 (33 to 100) depending on how many zombies were near; the synthetic bite rule is therefore in the same range as real zombie damage per zombie, but the rendered number comes from only 2 zombies, so the real bite is harsher per zombie than the synthetic one (1.5 per second within 1.2 tiles). (3) Movement: the fake scripted policy walked 23 tiles per episode (20 net), the rendered one 5 (2 net), and 2 of 3 rendered scripted episodes never moved: the baseline steps in 1 second moves of about 3.5 tiles, the rendered `goto` is re-issued every step and restarts pathing, and the fake mover simply walks a straight line. Rendered movement per step is therefore much less than the fake mover's, which makes trained movement policies non-transferable until the rendered `goto` keeps its path across steps and uses running. (4) Kills: the rendered kill counter works (1 kill, zombie count drops with it); the fake counter counted 15 kills in one episode against a crowd. Not equivalent yet: movement per step and the unmatched spawn conditions. Probably comparable: damage scale and kill mechanics (swings kill in about 6 hits, damage against zombies per swing is lower than the fake client's).

Next: matched spawns (clear radius, spawn exactly N zombies on a ring), a rendered goto that does not restart its path each step, then repeat with 5+ episodes per cell.

**Matched comparison, fake vs rendered (2026-10-25 night; `scripts/compare_backends.py fight 60 5 2`, 1 agent, bat, exactly 2 zombies 5-8 tiles away at the start, 5 episodes per cell, 60 steps of 1 s; logs/compare_backends3.out for fake, logs/compare_backends7.out for rendered).**

| backend / policy | episodes | kills (of 2) | damage taken per episode | steps survived |
|---|---|---|---|---|
| fake / idle | 5 | 0 | 85, 85, 83, 89, 91 (death threshold reached) | 29-31 |
| fake / scripted (charge) | 5 | 2 in 4 of 5 episodes (the fifth wandered into the world's own zombies: 21 kills) | 36 (wandered), 18, 2, 3, 2 | 60 |
| rendered / idle | 5 | 0 | 87, 82, 92, 91, 85 | 16-37 |
| rendered / scripted (charge) | 5 | 0 | 87, 18, 87, 89, 82 | 31-60 |

Reading. (1) Spawn matching works (exactly 2 zombies at the start on both) after two fixes: reset waits until the teleport has arrived and chunks settled before clearing (radius 45) and spawning, and a real client has to be teleported by its own Lua (server-side teleport does nothing; the server's speed anti-cheat kicks the client-side teleport unless disabled). (2) Damage from zombies when standing still matches closely: both backends lose 82-92 health in 16-37 s to two zombies, so the synthetic bite rule (1.5 per second within 1.2 tiles) is a good stand-in for the real zombie damage. (3) Fighting does NOT match: the fake client's built-in melee kills both zombies within seconds for 2-18 damage, the rendered bot kills none in 5 episodes and takes as much damage as standing idle in 4 of 5. In the real game two zombies knock the player into hit-reaction and knocked-down states in which a swing cannot start (pressedAttack is ignored), and the bot's swing takes 30-55 frames and is restarted by every new attack command. So a policy that learns on the fake backend will see fighting as far easier than it is in the real game. (4) Movement per step of the rendered bot is lower than the fake mover's (4-10 tiles per episode against 2-84), partly because the player is mostly stuck in reactions. Conclusion: movement and zombie damage transfer, combat does not yet. Next: stop restarting a swing in progress, add attack-while-reacting handling (e.g. shove, step back), then re-measure; and make the fake backend's melee harder (a hit reaction delay and misses) so training does not overfit to free kills.

**Why rendered fighting is weak (investigation, 2026-10-25 night).** With the swing fixed to never restart while in progress and to wait out hit reactions (dev file v1, not yet folded into RLBot.lua), 4 rendered episodes with 2 zombies still ended with 0 kills and 45 to 96 damage. Evidence from the client log and the server's packet log: swings do start (state SwipeStatePlayer) and hits are sent to the server, but the damage per hit is small and very variable (server `PlayerHitZombie` packets: mean 0.19 of a zombie's 1.0 health, range 0.007 to 0.85, one outlier 6.8; attack types default, uppercut, overhead, miss), so a kill needs about 6 hits; each swing takes 30-55 frames and the player is in hit reaction, bumped or get-up states for a large share of the time (a zombie within 1 tile staggers it every second or two). The fake client's melee, by contrast, does not stagger and deals a fixed lethal hit. Lessons: (a) policies trained only on the fake backend will overestimate fighting; (b) a rendered-fidelity fight needs more than one `attack` action per second: dodging or backing away and attacking when not staggered matter, which a learned policy could discover but only if the training backend models it; (c) the real fight is a poor first target, survive and rendezvous transfer better. Charge (`chargeTime`, `useChargeDelta`) is 0 in all sent hits; whether holding the attack raises damage was not tested.

**First learned policy: PPO on rendezvous (2026-10-26).** `pzrl/train.py` (own PPO in torch, one shared policy for all agents, 25-dim observation, 10 discrete actions, 3 episodes of 40 one-second steps per iteration, 240 samples per iteration, lr 3e-4) on `rendezvous` with 2 agents, no zombies, a 150x150 spawn box, fake backend at 4x (about 2.4 minutes per iteration, 80 iterations in about 3.2 hours). Mean episode return rose from 0.4 (iteration 5) to 1.8 (15), 2.5 (30), 4.0-5.7 (50-65) and ended at 5.3 (training episodes, sampled actions); the pair distance at the end of an episode fell from about 100 tiles to 6-13. Greedy evaluation of the final checkpoint over 4 episodes: return 3.07, final pair distance 9.7 tiles; the scripted seek-mate baseline returns 10.3 on the same task, so the policy has learned to head for its teammate but is not as direct or as fast as the baseline. Curves: docs/media/rendezvous_learning_iter15.png, _iter30.png, _final.png; checkpoint models/rendezvous.pt (small, committed); raw per-iteration numbers models/rendezvous.jsonl.

**Transfer of the learned movement policy to a real client (2026-10-26, `scripts/eval_transfer.py models/rendezvous.pt 5 mixed`).** Rendezvous, no zombies, 2 agents at 1x: Client40 is a real rendered client, Client41 a fake client, both driven by the same greedy policy trained only on fake clients (`PZParallelEnv(backend="mixed")`). Per episode (start distance, final distance, path walked by the real client, by the fake one): 65 tiles -> 35.0 (real 0.0, fake 62.9); 80 -> 11.2 (50.5, 79.4); 77 -> 8.1 (42.0, 88.0); 146 -> 9.8 (56.2, 90.4); 117 -> 11.0 (22.9, 90.9). Fake-only greedy evaluation (80 training iterations): final distance 9.7 on average. So the movement skill transfers: in 4 of 5 episodes the pair ended inside 11 tiles with a real client doing the walking, although the real client walks about 35-55 tiles per episode against the fake mover's 80-90 (its pathing and its slower run speed; the policy compensates because the teammate also walks toward it). The first episode (real client never moved, 0.0 tiles) is the first reset after the client came up; its walking did not start, cause not found yet (suspects: first teleport right after load, first walk request ignored). Needs a repeat with more episodes and with the scripted baseline in the same setup.
