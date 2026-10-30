# Headless real-client study (user-approved 1-hour spike, started 2026-10-30 07:50, stop 08:50)

Goal: find where a real (Build 42) client can be split into game logic and drawing, and what only exists in the full client (hit resolution, animations, zombie damage, aiming). Output: an easy / hard / unknown map backed by measurements, and a recommendation.

## RESUME HERE (update at every breakpoint)
- Status: started. Phase 0 (seam map) next.
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
