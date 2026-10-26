# Journal and task queue

Read this first after a crash or a session reset. Newest entries on top. Details of the evidence live in `docs/approach.md`;
how to run things lives in `CLAUDE.md`. Rule from the user: commit and push after each finding, no need to ask.

## How to resume (state of the machine may differ, check first)
1. `git log --oneline -8` and read the top of this file.
2. Is a server running? `python -c "import socket;socket.create_connection(('127.0.0.1',17600),timeout=2)"` succeeds if so. Server boot takes about 5 minutes.
3. Never stop java by memory size (server and client are both big). Match command lines: the server has `rl-agent.jar`, rendered clients have `rl-agent-client`.
4. Client Lua edits (`mods/RLBridge/common/media/lua/client/*.lua`) need `scripts/install-mods.ps1 -Enable RLBridge` plus a server restart; `rl_bot_dev.lua` + `reload` is the no-restart iteration path.

## Task queue (top first)
1. Rerun `scripts/compare_backends.py fight 60 5 2` (fake vs rendered, matched spawns, path-keeping rendered goto) and record the table in docs/approach.md. Output goes to logs/compare_backends2.out and logs/compare_backends.json.
2. Fix whatever the rerun shows (rendered movement per step, kills counter, respawn after death for rendered players).
3. Screenshots for the user: try an in-game screenshot command (RLBot `shot`) and save good ones into docs/media/ (see Media below).
4. Train a first policy (shared-policy PPO) on the fake backend: survive, then rendezvous, then fight; needs gymnasium/pettingzoo/stable-baselines3 (ask before installing: the user is asleep, so write a small dependency-free learner in numpy instead, or install only if the user already said yes).
5. Evaluate trained policy on the rendered backend and record the transfer gap.
6. Longer-run stability, crash recovery, parallel servers; JDK env-var reminder is still open (memory file).

## Media
Screenshots and clips for the user go in `docs/media/` (commit them) with a one-line caption in the log below.

## Log (newest first)
- 2026-10-25 night: rendered backend works end to end (`PZParallelEnv(backend="rendered")`); first fake-vs-rendered table was unmatched (fake 4-20 zombies near, rendered 0-2) and showed rendered movement per step far lower than fake; spawn matching and path-keeping goto added, rerun in progress.
- 2026-10-25: unattended rendered-client start (auto character creation, click-through of "Click to Start"); rendered bot walks, equips, swings and kills with the game's own combat (aim comes from the mouse cursor, hit reaction blocks swings); real zombies hurt rendered players hard.
