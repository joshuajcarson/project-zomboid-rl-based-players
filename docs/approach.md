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
