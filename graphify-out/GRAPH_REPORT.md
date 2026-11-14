# Graph Report - project-zomboid-rl-based-players  (2026-11-14)

## Corpus Check
- 153 files · ~80,603 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 72 file(s) not represented in the graph (top: .jsonl 42, .pt 14, .npz 6)
- WARNING: 72 of 225 files seen (32%) have no supported extractor and are missing from this graph entirely. It may look complete while representing only part of the codebase.

## Summary
- 776 nodes · 1400 edges · 83 communities (32 shown, 51 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 77 edges (avg confidence: 0.87)
- Token cost: 376,906 input · 0 output

## Community Hubs (Navigation)
- Experiment cards (batches 1-12)
- PZParallelEnv core
- Java agent bridge
- Training and imitation scripts
- Server Lua bridge
- Bytecode transformers
- Environment invariants
- Env scripts and demos
- Benchmark and version tracking
- Client bot commands
- Server channel and dev tools
- Architecture options
- Analysis scripts
- Fake client control
- Fake-vs-real modelling
- Launcher process control
- Task definitions and rewards
- Process cleanup tools
- Scripted baselines
- Rendered client control
- Experiment protocol rules
- Headless client study
- Milestones and calibration
- Rendered client plumbing
- Env lock and combat model
- Game mechanics catalogue
- Invariants and field fixes
- Later milestones M3-M7
- Realism roadmap
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
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
- Community 78
- Community 79
- Community 80
- Community 81

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
- `drift_noon_vs_1am.jsonl (clean null result)` --shares_data_with--> `Block-to-block drift of the same policy`  [INFERRED]
  results/experiments-2026-10-30/README.md → docs/journal.md
- `commands.reload()` --calls--> `f()`  [INFERRED]
  mods/RLBridge/common/media/lua/client/RLBot.lua → scripts/rl_bot_dev.lua
- `main()` --calls--> `idle()`  [EXTRACTED]
  scripts/record_episode.py → pzrl/baselines.py
- `main()` --calls--> `PZParallelEnv`  [EXTRACTED]
  scripts/record_episode.py → pzrl/env.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Option E bridge stack (agent sockets, RLBridge Lua, Python env)** — docs_approach_java_agent, docs_approach_rlbridge, docs_approach_server_channel, docs_approach_client_control_socket, docs_approach_pzparallelenv [EXTRACTED 1.00]
- **Fake-backend fidelity calibrations against the real client** — docs_approach_synthetic_bite_rule, docs_approach_walk_speed_calibration, docs_approach_combat_calibration, docs_approach_explicit_melee, docs_approach_matched_comparison [INFERRED 0.85]
- **Noise control for experiment comparisons** — docs_headless_client_block_drift, claude_interleaved_arms, claude_acceptance_tests, claude_experiment_protocol [INFERRED 0.85]
- **Fake-vs-real fidelity calibration (Batches 2-9)** — docs_milestones_m2a, docs_milestones_m2, docs_journal_fake_one_kill_artifact, docs_journal_fake_calibration_bite_hit, docs_journal_fake_combat_model [EXTRACTED 1.00]
- **Measurement-noise discipline (drift, interleaving, pooled acceptance)** — docs_journal_block_drift, docs_journal_interleaved_arms_rule, docs_milestones_acceptance_test_rule, docs_results_unpaired_rows, scripts_compare_arms [INFERRED 0.85]
- **State drift problems fixed by invariants** — docs_journal_bat_pileup, docs_journal_hutch_crash, docs_journal_server_inv_lies, docs_journal_invariants [EXTRACTED 1.00]
- **M2 fake-vs-real calibration chain (B2-B9)** — docs_experiments_2026_10_30_b2_m2_fake_vs_real, docs_experiments_2026_10_30_b3_m2a_fake_one_kill, docs_experiments_2026_10_30_b4_m2a_fake_fix, docs_experiments_2026_10_30_b5_m2_bite_sweep, docs_experiments_2026_10_30_b6_m2_confirm, docs_experiments_2026_10_30_b7_m2_two_knob_sweep, docs_experiments_2026_10_30_b8_m2_low_bite_sweep, docs_experiments_2026_10_30_b9_m2_confirm_low_bite [EXTRACTED 1.00]
- **M3 learned fighter gates (PPO gate A, BC gate A, BC gate B)** — docs_experiments_2026_10_30_b10_m3_ppo_fake_gate, docs_experiments_2026_10_30_b11_m3a_bc_gate, docs_experiments_2026_10_30_b12_m3a_gate_b_real, docs_experiments_2026_10_30_b10_m3_ppo_fake_gate_non_inferiority [EXTRACTED 1.00]
- **M0 measurement-trust nuisance variable investigations** — docs_experiments_2026_10_30_retro_r3_latency_hypothesis, docs_experiments_2026_10_30_retro_r4_time_of_day, docs_experiments_2026_10_30_retro_r5_corpses, docs_experiments_2026_10_30_retro_r8_spawn_geometry, docs_experiments_2026_10_30_retro_block_drift [INFERRED 0.85]

## Communities (83 total, 51 thin omitted)

### Community 0 - "Experiment cards (batches 1-12)"
Cohesion: 0.06
Nodes (44): B10 M3 gate A: PPO fighter on calibrated fake, pzrl.train shared-policy PPO (torch only), Sample throughput bottleneck (~3 samples/s; target >= 20), B11 M3a gate A: behaviour-cloned fighter vs scripted on fake, models/fight_bc3.pt behaviour-cloned checkpoint (sha1 e624cb83a0), B12 M3a gate B: BC fighter vs scripted on real client (paused), Death-reset arm alternation wrinkle / reset head start, B1 M1 confirmation: plain charge fighter on clean field (+36 more)

### Community 1 - "PZParallelEnv core"
Cohesion: 0.07
Nodes (4): PZParallelEnv, Box, Discrete, sample_spawns()

### Community 2 - "Java agent bridge"
Cohesion: 0.08
Nodes (4): RLAgent, RLClientControl, Peer, RLServerChannel

### Community 3 - "Training and imitation scripts"
Cohesion: 0.13
Nodes (13): collect(), fit(), main(), ActorCritic, evaluate(), gae(), main(), plot_curve() (+5 more)

### Community 4 - "Server Lua bridge"
Cohesion: 0.11
Nodes (20): ack(), applyBites(), drain(), findPlayer(), handlers.bot(), handlers.ensure(), handlers.ensureroot(), handlers.give() (+12 more)

### Community 5 - "Bytecode transformers"
Cohesion: 0.12
Nodes (3): RLMouseTransformer, RLNoRenderTransformer, RLTimeTransformer

### Community 6 - "Environment invariants"
Cohesion: 0.11
Nodes (15): check_alive(), check_in_arena(), check_one_bat(), client_count(), parse_inv(), run_all(), world_snapshot(), Chan (+7 more)

### Community 8 - "Benchmark and version tracking"
Cohesion: 0.14
Nodes (14): git_commit(), have_reference(), main(), report(), row(), run_interleaved(), run_lab(), run_policy() (+6 more)

### Community 9 - "Client bot commands"
Cohesion: 0.11
Nodes (14): commands.attack(), commands.equip(), commands.goto(), commands.info(), commands.reload(), equip(), log(), nearestZombie() (+6 more)

### Community 11 - "Architecture options"
Cohesion: 0.16
Nodes (20): Option E architecture in use (fake clients + Java agent + RLBridge + pzrl), Approach (architectures and evidence log), Aim override (RLMouse, rlAim) on the real client, Fake-client control socket (goto, speed, tp, weapon, attack), Connection flow CONNECT-LOGIN-CHECKSUM-LOAD_PROFILE-CREATE_PLAYER-PLAYER_CONNECT-RUN, zombie.network.FakeClientManager (headless load-test client), Java agent (agent/): rlGet, rlLoadArea, rlAddPlayer, channel, control, clock, Option A: fake clients driven by a policy (+12 more)

### Community 12 - "Analysis scripts"
Cohesion: 0.16
Nodes (4): corr(), feats(), geometry(), report()

### Community 14 - "Fake-vs-real modelling"
Cohesion: 0.17
Nodes (16): Scripted baselines (pzrl/baselines.py, charge fighter), Fake combat calibrated to real client (pzrl/combat.py: hit chance 0.46, lognormal damage), DAgger cloning of the charge fighter onto the real client, Matched fake vs rendered comparison (2 zombies, 5 eps), Option C: rendered clients + Lua bridge, Own PPO (pzrl/train.py) learned rendezvous policies, pzrl PZParallelEnv (PettingZoo-style env, 25-dim obs, 10 actions), Rendered backend (RLClient auto-login, RLAutoCreate, RLBot.lua, pzrl/rendered.py) (+8 more)

### Community 15 - "Launcher process control"
Cohesion: 0.16
Nodes (4): kill_clients(), kill_stale(), Launcher, _ps()

### Community 16 - "Task definitions and rewards"
Cohesion: 0.16
Nodes (7): dist(), Fight, nearest_other(), Rendezvous, SafeRendezvous, Survive, Task

### Community 17 - "Process cleanup tools"
Cohesion: 0.20
Nodes (9): _ancestors(), kind(), listeners(), main(), ours(), procs(), show(), kill() (+1 more)

### Community 18 - "Scripted baselines"
Cohesion: 0.20
Nodes (9): charge(), charge_param(), policy(), _dir_to_action(), flee(), nearest_mate_vec(), nearest_zombie_vec(), parse_policy() (+1 more)

### Community 20 - "Experiment protocol rules"
Cohesion: 0.18
Nodes (8): CLAUDE.md project instructions, benchmark.py --interleave tooling, scripts/cleanup.py end-of-run cleanup, Experiment cards in docs/experiments/ and daily milestone review, Game version tracking (track_game_version.py, versions/), docs/journal.md task queue and running log, docs/milestones.md milestone list, .pzdata server data with StarterKit sandbox

### Community 21 - "Headless client study"
Cohesion: 0.24
Nodes (10): Clock scaling RLClock / -TimeScale (constant-pool rewrite), Headless real-client study (hours 1-3), Block-to-block drift (same policy 25.7 to 49.9 damage), Client clock patch (rendered client at 2x), Per-client RAM ~4.2 GB regardless of drawing, Frame limiter busy-poll (MainThread Thread.yield spin), Reaction latency hypothesis and PZ_CMD_DELAY_MS injection, norender=world patch (IngameState render skip) (+2 more)

### Community 22 - "Milestones and calibration"
Cohesion: 0.18
Nodes (9): Fake calibration bite 2.25 / hit scale 0.6, Fake one-kill artifact (server ignores lethal hits; force-kill fix), Milestones toward the long-term goal, Daily milestone review (pz-daily-milestone-review), M1 Scripted solo fighter baseline (kills 1.36, damage 39.2), M1b Fewer deaths and stalls in scripted fighter, M2 Fake-vs-real fidelity for the solo fight, M2a Fake fight artifact found and fixed (+1 more)

### Community 24 - "Env lock and combat model"
Cohesion: 0.22
Nodes (5): hit_chance(), sample_swing(), _acquire_lock(), _pid_alive(), _release_lock()

### Community 25 - "Game mechanics catalogue"
Cohesion: 0.31
Nodes (6): Project Zomboid mechanics catalogue for the simulation, Character stats and moodles, Knox infection and wound types, Prioritised environment roadmap, Skills, traits, occupations, Zombie senses, speed, hordes, grab, drag-down

### Community 26 - "Invariants and field fixes"
Cohesion: 0.25
Nodes (8): Bat pile-up from repeated giveitem, Godmode between episodes, IsoHutch removeFromWorld NPE crash (dog house), Environment invariants as code (pzrl/invariants.py), Open fight field search (openness scan, find_open_field.py), Protocol fight-v4 (dirt field 5377,10114), Server inv lies about real client inventory (INVCOUNT), Protocol fight-v4 results (dirt field)

### Community 27 - "Later milestones M3-M7"
Cohesion: 0.32
Nodes (8): Batch 12 paused (session 2 interrupted), Shared-policy PPO (pzrl/train.py), Rendezvous movement transfer fake to real works, M3a Imitation gate (BC non-inferior to scripted), M3b PPO improves on scripted fighter (>= 20 samples/s), M5 Two cooperating agents, one real, M6 Client memory budget for 2+ real clients, M7 Four cooperating agents with real validation at two

### Community 29 - "Realism roadmap"
Cohesion: 0.33
Nodes (5): Combat state (endurance, panic, strain) cuts melee damage, Skill leveling (Strength, Blunt) not modelled on fake clients, Observation upgrade plan (zombie state, combat state, obstacle grid, wounds), Environment realism roadmap, M4 Solo survival loop beyond fighting

### Community 31 - "Community 31"
Cohesion: 0.33
Nodes (5): Journal and task queue, Reset head start (zombies walk before first action), Spawn geometry analysis (angular separation), M0 Trustworthy infrastructure and measurement, Per-episode data 2026-10-30 (headless and drift hunt)

### Community 32 - "Community 32"
Cohesion: 0.33
Nodes (6): scripts/benchmark.py and results ledger, Protocol fight-v2 (end when clear), Retreat below 35 hp (charge:1.8:35) did not replicate, Results ledger (generated report), Protocol fight-v1 results, Protocol fight-v3 results (cornfield 4010,11767)

### Community 36 - "Community 36"
Cohesion: 0.40
Nodes (5): Behaviour cloning of scripted charge (pzrl/imitate.py, fight_bc), Human demo recorder (record_demo.py, behaviour cloning + DAgger), Scripted charge fighter (charge:dist:flee), Swing-distance study (1.3-3.0), M8 Human-like play demo / recorder

### Community 37 - "Community 37"
Cohesion: 0.40
Nodes (5): Block-to-block drift of the same policy, Corpse pile on fight field (arm|hour|r clear), Light and visibility (omniscient zombie observation), drift_cleared_vs_pile250.jsonl (suggestive), drift_noon_vs_1am.jsonl (clean null result)

### Community 38 - "Community 38"
Cohesion: 0.40
Nodes (5): Client clock patch (2x, PZ_SETTLE), Headless client study (norender=world, frame limiter spin), M9 Faster-than-1x real client (parked), h1 render on/off episode files, h2 2x/4x clock episode files

### Community 39 - "Community 39"
Cohesion: 0.80
Nodes (4): enabled(), install(), log(), RL.createStep()

### Community 42 - "Community 42"
Cohesion: 0.83
Nodes (3): install(), log(), readCfg()

### Community 43 - "Community 43"
Cohesion: 0.83
Nodes (3): log(), report(), spawnNpc()

## Knowledge Gaps
- **47 isolated node(s):** `Game version tracking (track_game_version.py, versions/)`, `scripts/cleanup.py end-of-run cleanup`, `benchmark.py --interleave tooling`, `docs/journal.md task queue and running log`, `Experiment cards in docs/experiments/ and daily milestone review` (+42 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 297 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **51 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PZParallelEnv` connect `PZParallelEnv core` to `Training and imitation scripts`, `Env scripts and demos`, `Server channel and dev tools`, `Analysis scripts`, `Fake client control`, `Launcher process control`, `Rendered client control`, `Env lock and combat model`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `PZParallelEnv` (e.g. with `ClientControl` and `ServerChannel`) actually correct?**
  _`PZParallelEnv` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Game version tracking (track_game_version.py, versions/)`, `scripts/cleanup.py end-of-run cleanup`, `benchmark.py --interleave tooling` to the rest of the system?**
  _47 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Experiment cards (batches 1-12)` be split into smaller, more focused modules?**
  _Cohesion score 0.06386066763425254 - nodes in this community are weakly interconnected._
- **Why does `Interleaved arms in one session rule` connect `Milestones and calibration` to `Analysis scripts`, `Community 37`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Should `PZParallelEnv core` be split into smaller, more focused modules?**
  _Cohesion score 0.07265306122448979 - nodes in this community are weakly interconnected._
- **Why does `ClientControl` connect `Fake client control` to `PZParallelEnv core`, `Server channel and dev tools`, `Env scripts and demos`, `Rendered client plumbing`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._