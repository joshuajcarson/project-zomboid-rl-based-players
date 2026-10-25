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
