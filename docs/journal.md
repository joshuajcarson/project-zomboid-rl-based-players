# Journal and task queue

Read this first after a crash or a session reset. Newest entries on top. Details of the evidence live in `docs/approach.md`;
how to run things lives in `CLAUDE.md`. Rule from the user: commit and push after each finding, no need to ask.

## How to resume (state of the machine may differ, check first)
1. `git log --oneline -8` and read the top of this file.
2. Is a server running? `python -c "import socket;socket.create_connection(('127.0.0.1',17600),timeout=2)"` succeeds if so. Server boot takes about 5 minutes.
3. Never stop java by memory size (server and client are both big). Match command lines: the server has `rl-agent.jar`, rendered clients have `rl-agent-client`.
4. Client Lua edits (`mods/RLBridge/common/media/lua/client/*.lua`) need `scripts/install-mods.ps1 -Enable RLBridge` plus a server restart; `rl_bot_dev.lua` + `reload` is the no-restart iteration path.

## Task queue (top first)
1. DONE: matched comparison (docs/approach.md): damage when idle matches, fighting does not (rendered bot gets 0 kills of 2 in 5 episodes, fake gets 2 of 2).
2. Make rendered fighting work: do not restart a swing in progress (RLBot commands.attack), handle hit-reaction and knockdown states (wait, shove, step back), then re-measure with compare_backends.py rendered. Iterate through `.pzclient/Lua/rl_bot_dev.lua` (the env sends `reload` on rendered start), fold into RLBot.lua and restart the server only when done. Also remove the `shot` command (it crashes the client).
3. Media for the user: game screenshots are not possible so far (TakeScreenshot kills the client; window capture blank). Use scripts/record_episode.py (top-down GIF from observations) for trained policies and save into docs/media/.
4. Train a first policy (shared-policy PPO) on the fake backend: survive, then rendezvous, then fight; needs gymnasium/pettingzoo/stable-baselines3 (ask before installing: the user is asleep, so write a small dependency-free learner in numpy instead, or install only if the user already said yes).
5. Evaluate trained policy on the rendered backend and record the transfer gap.
6. Longer-run stability, crash recovery, parallel servers; JDK env-var reminder is still open (memory file).

## Media
Screenshots and clips for the user go in `docs/media/` (commit them) with a one-line caption in the log below.

## Log (newest first)
- 2026-10-26 11:30: transfer with zombies: policy trained on fakes works with a real client (it ends 14 tiles from its mate on average vs 2.5 all-fake, never took damage). BIGGEST GAP: the fake mover walks ~3 tiles/s, the real runner ~1.4 tiles/s. TODO next: calibrate both speeds in a straight line, set the fake client's speed to the real one, retrain rendezvous_safe, retest. Also still open: the first teleport right after a rendered client enters the world leaves it unable to walk (a 20 s settle was added in env.py, unverified).
- 2026-10-26 10:00: rendezvous_safe policy (models/rendezvous_safe.pt): greedy eval damage 22 (was 54), deaths 0 (was 0.75), pair distance 3.3, return 7.85 vs scripted -2.94. Next: test it with one real client against real zombies (scripts/eval_transfer.py needs task/zombie args), then 4 agents on the real+fake mix if memory allows (15.8 GB total; a real client is 4 GB).
- 2026-10-26 07:00: 4-agent rendezvous with 2 zombies per agent trained (60 its, models/rendezvous4z.pt): greedy eval return 9.86 vs scripted 4.76, pair distance 2.4, but 54 damage and 0.75 deaths per episode: agents gather but do not avoid zombie damage. Next idea: reward shaping that makes damage matter more (survive_terms weights), more zombies, or add an explicit flee/fight curriculum stage; also compare transfer on the real client.
- 2026-10-26 03:00: media in docs/media/: rendezvous_trained_fake.gif, rendezvous_scripted_fake.gif, rendezvous_trained_real_client.gif (one agent is a real rendered client; top-down drawing from bridge observations, not game footage) plus *_last.png frames and the learning curves rendezvous_learning_*.png.
- 2026-10-26 02:30: TRANSFER WORKS for movement: rendezvous policy trained only on fake clients, run with one real rendered client (backend="mixed", scripts/eval_transfer.py): final distance 8-11 tiles in 4 of 5 episodes (fake-only 9.7). Episode 0 the real client did not move at all (first reset after load; cause unknown). Only 15.8 GB RAM: one real client + server + fake clients fits, two real clients do not.
- 2026-10-26 00:40: rendezvous PPO iteration 30: return 2.49, final pair distance 18 tiles (from ~100 at iteration 1). Picture docs/media/rendezvous_learning_iter30.png.
- 2026-10-26 00:00: FIRST LEARNING: PPO (pzrl/train.py, shared policy, torch CPU) on rendezvous (2 agents, no zombies, 150x150 spawn box, fake backend at 4x): mean return 0.37 -> 0.75 -> 1.79 at iterations 5/10/15, final pair distance 95 -> 73 -> 61 tiles. Picture: docs/media/rendezvous_learning_iter15.png (run: logs/train_rendezvous4.out, checkpoint models/rendezvous.pt, curve models/rendezvous.png). Run continues to iteration 80 then evaluates against the scripted baseline.
- 2026-10-25 23:00: rendered fighting investigated (docs/approach.md, last section): hits land but do ~0.19 of a zombie's health on average and staggers block swings, so 0 kills in 4 episodes with the improved swing; dev file v1 is NOT folded into RLBot.lua. Decision: move on to training PPO (torch CPU is installed) on the fake backend for survive/rendezvous first and evaluate on the rendered backend; revisit fighting later (try holding the attack for charge, backing away between swings).
- 2026-10-25 22:30: matched comparison done, see docs/approach.md: idle damage matches (82-92 both), fighting does not (fake kills 2/2 for 2-18 damage, rendered 0 kills and ~85 damage in 4 of 5).
- 2026-10-25 22:10: DO NOT send the RLBot `shot` command: `getCore():TakeScreenshot()` kills the rendered client's JVM without a log line (twice). Media must come from elsewhere (data-driven plots, or a window capture if the screen is on). Also found: a real client's position is client-authoritative (server `teleportTo` does nothing; RLBot `tp` does the move), the server anti-cheat kicks that teleport for speed (all AntiCheat* options are set to 4 = off in .pzdata/Server/rl.ini, research server only), and a teleport of ~750 tiles can crash the client (keep spawn boxes small).
- 2026-10-25 night: rendered backend works end to end (`PZParallelEnv(backend="rendered")`); first fake-vs-rendered table was unmatched (fake 4-20 zombies near, rendered 0-2) and showed rendered movement per step far lower than fake; spawn matching and path-keeping goto added, rerun in progress.
- 2026-10-25: unattended rendered-client start (auto character creation, click-through of "Click to Start"); rendered bot walks, equips, swings and kills with the game's own combat (aim comes from the mouse cursor, hit reaction blocks swings); real zombies hurt rendered players hard.
