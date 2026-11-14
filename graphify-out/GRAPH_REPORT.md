# Graph Report - project-zomboid-rl-based-players  (2026-11-14)

## Corpus Check
- 157 files · ~85,958 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 815 nodes · 1482 edges · 79 communities (32 shown, 47 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 81 edges (avg confidence: 0.85)
- Token cost: 137,156 input · 0 output

## Community Hubs (Navigation)
- Environment invariants
- Experiment cards (batches 1-12)
- PZParallelEnv core
- Launcher process control
- Java agent bridge
- Server channel and dev tools
- Server Lua bridge
- Training and imitation scripts
- Bytecode transformers
- Client bot commands
- Benchmark and version tracking
- Analysis scripts
- Env scripts and demos
- Rendered client control
- Architecture options
- Fake-vs-real modelling
- Task definitions and rewards
- Scripted baselines
- Hybrid planner track
- Experiment protocol rules
- Headless client study
- Env lock and combat model
- Game mechanics catalogue
- Milestones and calibration
- Invariants and field fixes
- Milestones and calibration
- Milestones and calibration
- Community 28
- Realism roadmap
- Later milestones M3-M7
- Later milestones M3-M7
- Community 32
- Community 33
- Training and imitation scripts
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Community 69
- Community 70
- Community 71
- Community 72
- Community 73
- Community 74
- Community 75
- Community 76
- Community 77

## God Nodes (most connected - your core abstractions)
1. `PZParallelEnv` - 48 edges
2. `ServerChannel` - 23 edges
3. `ClientControl` - 22 edges
4. `RenderedControl` - 20 edges
5. `Launcher` - 17 edges
6. `main()` - 17 edges
7. `CLAUDE.md project instructions` - 13 edges
8. `main()` - 12 edges
9. `main()` - 12 edges
10. `RLAgent` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Block-to-block drift (same policy 25.7 to 49.9 damage)` --rationale_for--> `Interleaved arms comparison (30+ episodes per arm, report z)`  [INFERRED]
  docs/headless-client.md → CLAUDE.md
- `try()` --calls--> `log()`  [INFERRED]
  scripts/rl_bot_dev.lua → mods/RLBridge/common/media/lua/server/RLBridge.lua
- `main()` --calls--> `PZParallelEnv`  [EXTRACTED]
  scripts/record_episode.py → pzrl/env.py
- `main()` --calls--> `idle()`  [EXTRACTED]
  scripts/record_episode.py → pzrl/baselines.py
- `commands.reload()` --calls--> `f()`  [INFERRED]
  mods/RLBridge/common/media/lua/client/RLBot.lua → scripts/rl_bot_dev.lua

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Hybrid planner track: H-A plumbing -> H-B0 reliability -> H-B0b unit tests -> H-B** — docs_experiments_2026_11_14_ha_hybrid_plumbing, docs_experiments_2026_11_14_hb0_skill_reliability, docs_experiments_2026_11_14_hb0_skill_reliability_hb0b_unit_tests, docs_milestones_h_a, docs_milestones_h_b [EXTRACTED 1.00]
- **M2 fake-vs-real calibration chain (B2-B9)** — docs_experiments_2026_10_30_b2_m2_fake_vs_real, docs_experiments_2026_10_30_b3_m2a_fake_one_kill, docs_experiments_2026_10_30_b4_m2a_fake_fix, docs_experiments_2026_10_30_b5_m2_bite_sweep, docs_experiments_2026_10_30_b6_m2_confirm, docs_experiments_2026_10_30_b7_m2_two_knob_sweep, docs_experiments_2026_10_30_b8_m2_low_bite_sweep, docs_experiments_2026_10_30_b9_m2_confirm_low_bite [EXTRACTED 1.00]
- **Option E bridge stack (agent sockets, RLBridge Lua, Python env)** — docs_approach_java_agent, docs_approach_rlbridge, docs_approach_server_channel, docs_approach_client_control_socket, docs_approach_pzparallelenv [EXTRACTED 1.00]
- **State-drift bugs that motivated invariants as code** — docs_journal_bat_pileup, docs_journal_hutch_crash, docs_journal_server_inv_phantom_items, docs_journal_environment_invariants [EXTRACTED 1.00]
- **Fake-backend fidelity calibrations against the real client** — docs_approach_synthetic_bite_rule, docs_approach_walk_speed_calibration, docs_approach_combat_calibration, docs_approach_explicit_melee, docs_approach_matched_comparison [INFERRED 0.85]
- **Fake-backend fidelity chain (artifact fix, calibration, M2)** — docs_journal_fake_lethal_hit_artifact, docs_journal_fake_calibration_bite_hit, docs_milestones_m2a, docs_milestones_m2, docs_journal_strategic_read [INFERRED 0.85]
- **M0 measurement-trust nuisance variable investigations** — docs_experiments_2026_10_30_retro_r3_latency_hypothesis, docs_experiments_2026_10_30_retro_r4_time_of_day, docs_experiments_2026_10_30_retro_r5_corpses, docs_experiments_2026_10_30_retro_r8_spawn_geometry, docs_experiments_2026_10_30_retro_block_drift [INFERRED 0.85]
- **Noise control for experiment comparisons** — docs_headless_client_block_drift, claude_interleaved_arms, claude_acceptance_tests, claude_experiment_protocol [INFERRED 0.85]

## Communities (79 total, 47 thin omitted)

### Community 0 - "Environment invariants"
Cohesion: 0.06
Nodes (26): ask(), busy(), client_query(), _kv(), newest_log(), outcome(), run_one_shot(), state_text() (+18 more)

### Community 1 - "Experiment cards (batches 1-12)"
Cohesion: 0.06
Nodes (42): B10 M3 gate A: PPO fighter on calibrated fake, pzrl.train shared-policy PPO (torch only), Sample throughput bottleneck (~3 samples/s; target >= 20), B11 M3a gate A: behaviour-cloned fighter vs scripted on fake, models/fight_bc3.pt behaviour-cloned checkpoint (sha1 e624cb83a0), B1 M1 confirmation: plain charge fighter on clean field, charge:1.8:0 scripted fighter, cleanup.py killed the batch wrapper (fixed) (+34 more)

### Community 2 - "PZParallelEnv core"
Cohesion: 0.07
Nodes (4): PZParallelEnv, Box, Discrete, sample_spawns()

### Community 3 - "Launcher process control"
Cohesion: 0.07
Nodes (19): _acquire_lock(), EnvInUse, _pid_alive(), _release_lock(), kill_clients(), kill_rendered(), kill_stale(), Launcher (+11 more)

### Community 4 - "Java agent bridge"
Cohesion: 0.08
Nodes (4): RLAgent, RLClientControl, Peer, RLServerChannel

### Community 6 - "Server Lua bridge"
Cohesion: 0.11
Nodes (21): ack(), applyBites(), drain(), findPlayer(), handlers.bot(), handlers.ensure(), handlers.ensureroot(), handlers.give() (+13 more)

### Community 7 - "Training and imitation scripts"
Cohesion: 0.14
Nodes (12): collect(), fit(), main(), ActorCritic, evaluate(), gae(), main(), plot_curve() (+4 more)

### Community 8 - "Bytecode transformers"
Cohesion: 0.12
Nodes (3): RLMouseTransformer, RLNoRenderTransformer, RLTimeTransformer

### Community 9 - "Client bot commands"
Cohesion: 0.10
Nodes (21): commands.attack(), commands.equip(), commands.goto(), commands.info(), commands.reload(), equip(), log(), nearestZombie() (+13 more)

### Community 10 - "Benchmark and version tracking"
Cohesion: 0.14
Nodes (14): git_commit(), have_reference(), main(), report(), row(), run_interleaved(), run_lab(), run_policy() (+6 more)

### Community 11 - "Analysis scripts"
Cohesion: 0.13
Nodes (5): Per-episode data 2026-10-30 (headless and drift hunt), corr(), feats(), geometry(), report()

### Community 13 - "Rendered client control"
Cohesion: 0.13
Nodes (3): RenderedControl, me(), me()

### Community 14 - "Architecture options"
Cohesion: 0.16
Nodes (20): Option E architecture in use (fake clients + Java agent + RLBridge + pzrl), Approach (architectures and evidence log), Aim override (RLMouse, rlAim) on the real client, Fake-client control socket (goto, speed, tp, weapon, attack), Connection flow CONNECT-LOGIN-CHECKSUM-LOAD_PROFILE-CREATE_PLAYER-PLAYER_CONNECT-RUN, zombie.network.FakeClientManager (headless load-test client), Java agent (agent/): rlGet, rlLoadArea, rlAddPlayer, channel, control, clock, Option A: fake clients driven by a policy (+12 more)

### Community 15 - "Fake-vs-real modelling"
Cohesion: 0.17
Nodes (16): Scripted baselines (pzrl/baselines.py, charge fighter), Fake combat calibrated to real client (pzrl/combat.py: hit chance 0.46, lognormal damage), DAgger cloning of the charge fighter onto the real client, Matched fake vs rendered comparison (2 zombies, 5 eps), Option C: rendered clients + Lua bridge, Own PPO (pzrl/train.py) learned rendezvous policies, pzrl PZParallelEnv (PettingZoo-style env, 25-dim obs, 10 actions), Rendered backend (RLClient auto-login, RLAutoCreate, RLBot.lua, pzrl/rendered.py) (+8 more)

### Community 16 - "Task definitions and rewards"
Cohesion: 0.16
Nodes (7): dist(), Fight, nearest_other(), Rendezvous, SafeRendezvous, Survive, Task

### Community 17 - "Scripted baselines"
Cohesion: 0.20
Nodes (9): charge(), charge_param(), policy(), _dir_to_action(), flee(), nearest_mate_vec(), nearest_zombie_vec(), parse_policy() (+1 more)

### Community 18 - "Hybrid planner track"
Cohesion: 0.24
Nodes (12): H-A Hybrid Planner Plumbing Card, Last-skill outcome feedback to planner, Skill reliability gap (effects in 21-44% of uses), H-B0 Skill Reliability Card, busy command / run_one_shot wait-for-queue, Eat never queued (food in backpack, transferIfNeeded fails), H-B0b in-game skill unit tests, Loot queued but stalls walking into building (+4 more)

### Community 19 - "Experiment protocol rules"
Cohesion: 0.18
Nodes (8): CLAUDE.md project instructions, benchmark.py --interleave tooling, scripts/cleanup.py end-of-run cleanup, Experiment cards in docs/experiments/ and daily milestone review, Game version tracking (track_game_version.py, versions/), docs/journal.md task queue and running log, docs/milestones.md milestone list, .pzdata server data with StarterKit sandbox

### Community 20 - "Headless client study"
Cohesion: 0.24
Nodes (10): Clock scaling RLClock / -TimeScale (constant-pool rewrite), Headless real-client study (hours 1-3), Block-to-block drift (same policy 25.7 to 49.9 damage), Client clock patch (rendered client at 2x), Per-client RAM ~4.2 GB regardless of drawing, Frame limiter busy-poll (MainThread Thread.yield spin), Reaction latency hypothesis and PZ_CMD_DELAY_MS injection, norender=world patch (IngameState render skip) (+2 more)

### Community 21 - "Env lock and combat model"
Cohesion: 0.24
Nodes (3): hit_chance(), sample_swing(), AgentDisconnected

### Community 22 - "Game mechanics catalogue"
Cohesion: 0.31
Nodes (6): Project Zomboid mechanics catalogue for the simulation, Character stats and moodles, Knox infection and wound types, Prioritised environment roadmap, Skills, traits, occupations, Zombie senses, speed, hordes, grab, drag-down

### Community 23 - "Milestones and calibration"
Cohesion: 0.25
Nodes (6): B12 M3a Gate B Card (BC vs scripted, real client), fight_bc3.pt behaviour-cloned fighter, Session 2 restart-from-scratch resume plan, Journal and Task Queue, Aborted post-death reset episodes dropped (steps < 5), Milestones Toward the Long-Term Goal

### Community 24 - "Invariants and field fixes"
Cohesion: 0.25
Nodes (7): H-A run 1 invalid (stale bot file), Server-authoritative stats (RLBridge stats handler), Bat pile-up / encumbrance bug, Fight protocols v1-v4 (open field, cornfield, dirt field 5377,10114), IsoHutch chunk-unload client crash (dog house), Server inv lies about real client inventory, Zero-population world breaks zspawn (Low used)

### Community 25 - "Milestones and calibration"
Cohesion: 0.25
Nodes (7): Drift hunt (darkness no effect, corpses maybe, mostly noise), Swing distance study (1.8-2.6 equal; 1.3, 3.0 worse), Results ledger (generated report), Protocol fight-v1 results, Protocol fight-v3 results (cornfield 4010,11767), Protocol fight-v4 results (dirt field), [unpaired] ledger rows (exploratory only)

### Community 27 - "Milestones and calibration"
Cohesion: 0.29
Nodes (6): Fake calibration bite 2.25 / hit scale 0.6, Fake server ignores lethal hits (force-kill fix), M1 Scripted solo fighter baseline (characterised), M1b Fewer deaths and stalls in scripted fighter, M2 Fake-vs-real fidelity for solo fight, M2a Fake fight artifact fixed

### Community 29 - "Realism roadmap"
Cohesion: 0.33
Nodes (5): claude -p Sonnet planner (structured JSON, no tools), Skill menu (fight, flee, wait, eat, drink, bandage, loot), Observation upgrade groups a-g, Light and visibility (agents see hidden zombies), M4 Solo survival loop beyond fighting

### Community 30 - "Later milestones M3-M7"
Cohesion: 0.40
Nodes (5): H-C Two agents cooperate through planner chat, M3a Imitation gate (BC non-inferior), M5 Two cooperating agents, one real, M6 Client memory budget for 2+ real clients, M7 Four cooperating agents (fakes) with real validation

### Community 31 - "Later milestones M3-M7"
Cohesion: 0.33
Nodes (6): Live status text in game window (env.say), PPO from scratch throughput limit (~3 samples/s), Reset head start (zombies walk ~6-7 s before first action), Spawn geometry (angular separation raises damage), M0 Trustworthy infrastructure and measurement, M3b PPO improves on scripted fighter

### Community 33 - "Community 33"
Cohesion: 0.80
Nodes (4): enabled(), install(), log(), RL.createStep()

### Community 36 - "Community 36"
Cohesion: 0.50
Nodes (4): Headless client study (no CPU/RAM win; frame limiter spin), Closed tracks (headless draw removal, scripted tuning, server NPCs), M9 Faster-than-1x real client (parked), h1 render on/off episode files

### Community 37 - "Community 37"
Cohesion: 0.83
Nodes (3): install(), log(), readCfg()

### Community 38 - "Community 38"
Cohesion: 0.83
Nodes (3): log(), report(), spawnNpc()

## Knowledge Gaps
- **45 isolated node(s):** `pzrl.train shared-policy PPO (torch only)`, `fight-v4 dirt field (5377,10114)`, `env.ztrace per-zombie instrumentation`, `Frame limiter spin (1-core client load)`, `PZ_SETTLE reset-wait multiplier` (+40 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 310 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **47 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Journal and Task Queue` connect `Milestones and calibration` to `Analysis scripts`, `Hybrid planner track`, `Milestones and calibration`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `PZParallelEnv` (e.g. with `ClientControl` and `ServerChannel`) actually correct?**
  _`PZParallelEnv` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `pzrl.train shared-policy PPO (torch only)`, `fight-v4 dirt field (5377,10114)`, `env.ztrace per-zombie instrumentation` to the rest of the system?**
  _45 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Environment invariants` be split into smaller, more focused modules?**
  _Cohesion score 0.05660377358490566 - nodes in this community are weakly interconnected._
- **Why does `Per-episode data 2026-10-30 (headless and drift hunt)` connect `Analysis scripts` to `Milestones and calibration`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Should `Experiment cards (batches 1-12)` be split into smaller, more focused modules?**
  _Cohesion score 0.06352941176470588 - nodes in this community are weakly interconnected._
- **Why does `B12 M3a Gate B Card (BC vs scripted, real client)` connect `Milestones and calibration` to `Experiment cards (batches 1-12)`, `Later milestones M3-M7`, `Later milestones M3-M7`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._