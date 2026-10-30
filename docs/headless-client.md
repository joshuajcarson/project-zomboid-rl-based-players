# Headless real-client study (user-approved 1-hour spike, started 2026-10-30 07:50, stop 08:50)

Goal: find where a real (Build 42) client can be split into game logic and drawing, and what only exists in the full client (hit resolution, animations, zombie damage, aiming). Output: an easy / hard / unknown map backed by measurements, and a recommendation.

## RESUME HERE (update at every breakpoint)
- Status (08:37): hour-1 spike COMPLETE (stopped at 08:37 of 08:50). Experiments 0, A, B, C, E, F(partly), G done; D compared on paper only. Everything stopped, scripts/cleanup.py clean. See the map and the open questions; start the next hour from "Open questions".
- Resume rules: read this file, `python scripts/cleanup.py`, check usage (90% rule), continue at the first unchecked experiment. Commit after every phase. javap output goes to `.scratch/` (never commit decompiled source or game code; notes in our own words only).
- Time budget: 60 min per hour-session. If promising but unfinished, the next session starts from "Open questions" below.

## Experiment list (grows as we learn)
- [x] 0 Seam map (javap): where update and draw meet (main loop, render thread, player/zombie render, animation events)
- [~] A Settings (only the -Small window/30 fps settings that we already use were measured; no further quality cuts tried) only: tiny window, shadows/lighting off, frame cap off; CPU/RAM; does the game clock change with uncapped frames?
- [x] B Skip drawing: patch the top-level draw call to no-op while update keeps running; client stays connected, character moves and swings?
- [x] C Combat (small sample) fidelity with drawing off: ~12 `charge:1.8:0` episodes vs normal; swing hit rate by distance, damage taken
- [~] D ZombieBuddy vs own transformer for the same patch (lines, build steps, break-on-update risk)
- [x] E Do animation events still fire without drawing (hits are probably animation-driven)?
- [~] F Hidden/tiny window vs no GL context at all
- [x] G Memory per client with drawing off; does a 2nd client fit?
- [ ] H Fallback: improve fake-client combat / zombie damage instead

## Findings (measurements, in our own words)
- 07:53 SEAM MAP (phase 0): `GameWindow.frameStep()` = `logic()` (network, Lua update, input, UI update) then `renderInternal()` (SpriteRenderer.NewFrame, lighting JNI, `GameStateMachine.render()` which draws the current state, Lua OnRender event, `Core.DoFrameReady`, `LightingThread.update`, `LuaEventManager.RunQueuedEvents`). So the draw call is one narrow method; logic is a separate method. Drawing runs via `RenderThread` on a GL context (frameStep wraps parts in `RenderThread.invokeOnRenderContext`).
- 07:54 ZombieBuddy v2.3.4 jar (13 MB, MIT) and zbNative.dll downloaded to .scratch/zb (git-ignored). On Windows ZB needs the native proxy because the game launcher's JRE cannot load instrument.dll; our launcher calls java directly with -javaagent (works today), a ZB mod needs the ZB mod folder, mod.info with javaJarFile/javaPkgName, policy=allow-all (else a native approval dialog), and a Gradle-or-javac build against ZB.jar.
- 07:55 Exp B patch (hand-rolled, 25 lines, agent option `norender`): flip `ifnull` to `ifnonnull` at the top of `GameStateMachine.render()` so no state draws; verifier-safe (both pop one reference). Env: `PZ_AGENT_EXTRA=norender` passed through start-client.ps1.

- 08:00 BASELINE (render on, full normal client, dirt field): client JVM 1.14 cores, 3.75 GB, 77 threads; server JVM 0.04 cores, 2.9 GB.
- 08:06-08:18 FIRST norender attempt (GameStateMachine.render skipped for ALL states) HUNG at startup: the client sat at "SafeMode is off" for 12 minutes with f:0. Menu and loading states do their transitions inside render, so a global render skip freezes login. LESSON: only the in-world state may skip drawing.
- 08:19 `norender=world` (IngameState.render's renderInternal call replaced by pop/nop/nop): client logs in, passes character creation, runs episodes; the Project Zomboid window is solid black. Offline test (.scratch/hl/PatchTest.java) confirms both patterns match the real class bytes.
- 08:26 world-draw-off cost: client 1.11 cores, 4.17 GB, 75 threads: NO saving (baseline 1.14 / 3.75). One thread (`MainThread`, the game loop) uses ~1.0 core, everything else ~0.05.
- 08:28 poor-man's profile of MainThread (15 jcmd dumps, draw off): 14 of 15 samples are inside `Thread.yield()` called from `MainThread.mainLoop`: the loop SPIN-WAITS (a frame limiter or a wait-for-render-thread), so the 1.0 core is mostly idle spinning, not work. Real per-frame work is small. One sample still showed IngameState.renderInternal / AnimatedModel render on the stack (world draw not fully off? to be checked).
- 08:30 ZombieBuddy comparison (not loaded yet): same patch is 5 lines (`@Patch(... "render") @Patch.OnEnter(skipOn = true)` returning true) vs 25 for the hand-rolled byte patch, and ZB can express CONDITIONAL skips (e.g. skip only when the state is IngameState) trivially, which our constant-pool patcher cannot. Costs: the release jar v2.3.4 uses package `me.zed_0xff.zombie_buddy.Patch` while the docs on master describe `.annotations.Patch` (docs ahead of the release); a mod folder + mod.info (javaJarFile, javaPkgName) + the ZombieBuddy mod stub; approval policy (policy=allow-all to avoid a dialog); Windows needs zbNative.dll or a plain -javaagent (ours works); a 13 MB third-party jar. For one-off byte flips our patcher is cheaper; for anything conditional ZB is far easier.
- 08:31 EXP C (combat fidelity), same seed/field, charge:1.8:0: render on 8 eps 1.25 kills / 40.4 dmg / 0 low-hp, 48 swings, 24.5 frames per swing; world draw off 9 eps 1.00 kills / 39.6 dmg / 0 low-hp, 43 swings, 23.0 frames per swing. Hit rate by swing distance: ~0.5 tiles 0.17 vs 0.18, ~1.0 tiles 0.58 vs 0.56 (1.5 tiles 0.73/n=22 vs 0.47/n=15, within small-sample noise). Swing animations complete and are timed the same (EXP E: animation-driven hit resolution survives with the world draw off, since swings finish, hit and take damage as before). Samples are tiny; a 30-episode repeat is needed to claim equivalence.
- 08:36 RENDER-ON A/B: normal client: 1.13 cores, 4.33 GB, 75 threads (patched: 1.11 cores, 4.17 GB). MainThread stack samples: Thread.yield0 in 19 of 20 in BOTH, and IsoWorld.render in 0 of 20 (normal) vs 1 of 20 (patched): the main thread does not spend visible time drawing in either case; the actual GL work is on the render thread / GPU and is not the CPU cost. The normal window shows the world, inventory and chat; the patched window is solid black: the patch works visually. Machine: 15.8 GB RAM, 10 cores/16 threads; server JVM 3.9 GB + client 4.3 GB already 8.2 GB, a second client would take ~12.5 GB before the OS, browsers and everything else.
- 08:30 SIDE EFFECT: with the world draw off Windows marks the game window "Not Responding" (the user noticed). The window stops servicing its event queue; the bot does not care, but a human cannot watch or interact with that client, and a recording would need a separate render-on client.

## Easy / hard / unknown map
| subsystem | verdict | evidence |
|---|---|---|
| world drawing | EASY to remove (one patch, 25 lines hand-rolled or 5 with ZombieBuddy) | client logs in, plays, window black; BUT it saves almost nothing (CPU 1.11 vs 1.14 cores, RAM 4.2 vs 3.8 GB) |
| menus / loading screens | HARD to skip: their state transitions run inside render() | global render skip hung the client at "SafeMode is off" for 12 min |
| animations and hit timing | EASY (they keep running with the draw off) | swings complete in 23.0 vs 24.5 frames, hit rate by distance matches; small sample (43/48 swings, 9/8 episodes) |
| zombie damage | not the draw's problem: same on the real client either way; the fake backend is the one that lacks it | bites and damage_end matched (39.6 vs 40.4 dmg) |
| aiming | EASY (melee follows facing; the aim marker is cosmetic) | docs/approach.md 2026-10-26; swing hit rates unchanged with a black window |
| per-client CPU | the 1.0 core is the FRAME LIMITER busy-polling (mainLoop yields; mainThreadStep checks lockFPS), real work is small and hidden under it | 14-19 of 20 stack samples in yield0 |
| per-client RAM | HARD: 4.2-4.3 GB with or without drawing (heap -Xmx3072m + native/texture memory) | needs heap and texture-memory experiments |
| running faster than 1x | PROMISING, untested: real per-frame work is small (frame limiter spin), the game clock follows wall time, so a client clock patch is the lever; the server has a clock patch (RLTimeTransformer), the client has none | RLTimeTransformer on the client is the next experiment |
| human watching / recording | LOST with the draw off: window goes "Not Responding" and shows black | a recording needs a render-on client |
| chunk loading, sound, UI | UNKNOWN (not touched; the UI draws inside the same skipped call) | |

## Open questions for a follow-up hour
1. (ANSWERED 08:39, by reading bytecode: `MainThread.mainLoop` is `while not close requested: mainThreadLoop.run(); Thread.yield()`; the loop body `GameWindow.mainThreadStep` reads nanoTime and compares it with `PerformanceSettings.getLockFPS` / `isFramerateUncapped`, calling `frameStep` only when the frame budget has elapsed. So the spin is the FRAME LIMITER busy-polling; at our `frameRate=30` option the real work is at most 30 frames/s and the core is mostly idle polling.) Consequence: the client has big headroom. Remaining question: the game clock (dt) follows wall time, so uncapping frames alone will not speed the game up; a client clock patch like the server's RLTimeTransformer (agent option `classes=`) is the way to run faster than 1x; the notes say the rendered client is '1x only' but I did not find a recorded attempt to scale the client clock, so try it: `classes=zombie/` on the client agent plus -Drl.timescale=2, check game time vs wall time and that swings keep their ~23-frame timing. Old wording of the question: why does MainThread spin in `Thread.yield`? Find the waiter (frame limiter vs wait for the render thread vs lighting thread). If it is a frame limiter, the real per-frame cost is small and a client clock patch (like the server's) might run the game faster than 1x: that is the multiplier that matters most.
2. Memory: try -Xmx 1.5-2 GB, smaller texture/model memory options, skipping the texture-pack loading for atlases we never draw. Goal: two or three clients plus the server in ~16 GB.
3. Does skipping the render thread entirely (not just the state draw) cut the 4 GB, or does the game need textures for animation (skinned models, hit zones)?
4. Repeat Exp C with 30 episodes per arm (the 8-vs-9-episode comparison only rules out large differences).
5. ZombieBuddy for real: install the ZB mod stub into `.pzclient/mods/ZombieBuddy`, allow-all policy, load the 5-line patch and make it conditional (skip only IngameState). Needed to decide use-vs-own-patcher on facts, and for per-state conditions we cannot express with constant-pool edits.
6. Hidden window / no GL context: `-Djava.awt.headless`, LWJGL offscreen; probably needs a real GL context for the render thread (not tried).
7. Fallback H: improve the fake backend's combat and zombie damage instead; compare cost-benefit against 2 and 3.
8. A render-on observer: since a draw-off client is not watchable, recordings need a second normal client or the render-on mode switched by a Lua command.
9. Side note: the fight field accumulates corpses (the HUD showed a Corpse container with 1.47/12 weight): check whether corpses pile up and add a corpse-clear invariant.


---
# Hour 2 (user-approved, started 2026-10-30 08:41, stop 09:41): client clock patch (faster than 1x) and memory
## RESUME HERE (hour 2)
- Status: wiring done (env guard opt-in `PZ_ALLOW_RENDERED_SCALE=1`, launcher passes -TimeScale to the rendered client, start-client.ps1 adds `classes=zombie/` when TimeScale != 1, lab reads `PZ_TIME_SCALE`). Next: run the lab at PZ_TIME_SCALE=2 (server and client both 2x) and compare with the 1x baseline: game-time vs wall-time rate, swing frames, hit rate by distance, kills/damage.
- Resume rules as hour 1: read this file, `python scripts/cleanup.py`, check usage, continue at the first unchecked item. Commit at each breakpoint.
- Experiments: [ ] H2-A client at 2x works (login, character, episodes) [ ] H2-B fidelity at 2x vs 1x (swing frames, hit rate, damage) [ ] H2-C 4x [ ] H2-D memory: -Xmx and texture options [ ] H2-E draw-off + clock patch together [ ] H2-F uncapped frame rate effect
## Findings (hour 2)
