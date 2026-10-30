# Headless real-client study (user-approved 1-hour spike, started 2026-10-30 07:50, stop 08:50)

Goal: find where a real (Build 42) client can be split into game logic and drawing, and what only exists in the full client (hit resolution, animations, zombie damage, aiming). Output: an easy / hard / unknown map backed by measurements, and a recommendation.

## RESUME HERE (update at every breakpoint)
- Status (08:32): phases 0, A, B done; C (combat fidelity) and the render-on/off A/B check running; D (ZombieBuddy) compared on paper (compiled, not loaded). Next: confirm draw is really off (window + stacks vs a normal client), then write the map.
- Resume rules: read this file, `python scripts/cleanup.py`, check usage (90% rule), continue at the first unchecked experiment. Commit after every phase. javap output goes to `.scratch/` (never commit decompiled source or game code; notes in our own words only).
- Time budget: 60 min per hour-session. If promising but unfinished, the next session starts from "Open questions" below.

## Experiment list (grows as we learn)
- [ ] 0 Seam map (javap): where update and draw meet (main loop, render thread, player/zombie render, animation events)
- [ ] A Settings only: tiny window, shadows/lighting off, frame cap off; CPU/RAM; does the game clock change with uncapped frames?
- [ ] B Skip drawing: patch the top-level draw call to no-op while update keeps running; client stays connected, character moves and swings?
- [ ] C Combat fidelity with drawing off: ~12 `charge:1.8:0` episodes vs normal; swing hit rate by distance, damage taken
- [ ] D ZombieBuddy vs own transformer for the same patch (lines, build steps, break-on-update risk)
- [ ] E Do animation events still fire without drawing (hits are probably animation-driven)?
- [ ] F Hidden/tiny window vs no GL context at all
- [ ] G Memory per client with drawing off; does a 2nd client fit?
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
- 08:30 SIDE EFFECT: with the world draw off Windows marks the game window "Not Responding" (the user noticed). The window stops servicing its event queue; the bot does not care, but a human cannot watch or interact with that client, and a recording would need a separate render-on client.

## Easy / hard / unknown map
| subsystem | verdict | evidence |
|---|---|---|
| drawing | ? | |
| animations and hit timing | ? | |
| zombie damage | ? | |
| aiming | likely easy (melee follows facing, cursor irrelevant; docs/approach.md 2026-10-26) | |
| chunk loading | ? | |
| sound | ? | |
| UI | ? | |

## Open questions for a follow-up hour
(none yet)
