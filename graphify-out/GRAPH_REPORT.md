# Graph Report - project-zomboid-rl-based-players  (2026-11-14)

## Corpus Check
- 21 files · ~95,802 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 906 nodes · 1598 edges · 76 communities (25 shown, 51 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 76 edges (avg confidence: 0.85)
- Token cost: 229,606 input · 0 output

## Community Hubs (Navigation)
- Architecture options
- Experiment cards (batches 1-12)
- Training and imitation scripts
- Java agent bridge
- Hybrid skill debugging (HB0 chain)
- Hybrid planner track
- Milestones and calibration
- PZParallelEnv core
- Server Lua bridge
- Client bot commands
- Bytecode transformers
- Env scripts and demos
- Launcher process control
- Benchmark and version tracking
- Analysis scripts
- Environment invariants
- Server channel and dev tools
- Run validity watchdog
- Environment invariants
- Launcher process control
- Server channel and dev tools
- Task definitions and rewards
- Rendered client control
- Environment invariants
- Environment invariants
- PZParallelEnv core
- Community 28
- Community 32
- Community 33
- Env lock and combat model
- Community 37
- Community 38
- Experiment protocol rules
- Community 39
- Community 36
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
- Later milestones M3-M7
- Milestones and calibration
- Community 75
- Community 76
- Community 77

## God Nodes (most connected - your core abstractions)
1. `PZParallelEnv` - 45 edges
2. `ServerChannel` - 20 edges
3. `ClientControl` - 18 edges
4. `main()` - 17 edges
5. `RenderedControl` - 16 edges
6. `HB: Hybrid planner vs rule planner vs idle (survival)` - 15 edges
7. `Launcher` - 14 edges
8. `main()` - 12 edges
9. `main()` - 12 edges
10. `findPlayer()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Experiment protocol (batches, pre-registration, interleaving)` --semantically_similar_to--> `Acceptance-test rule (pooled sessions, target and failure bound)`  [INFERRED] [semantically similar]
  CLAUDE.md → docs/milestones.md
- `try()` --calls--> `log()`  [INFERRED]
  scripts/rl_bot_dev.lua → mods/RLBridge/common/media/lua/server/RLBridge.lua
- `Interleaved arms in one session` --rationale_for--> `Experiment protocol (batches, pre-registration, interleaving)`  [INFERRED]
  docs/journal.md → CLAUDE.md
- `main()` --calls--> `ActorCritic`  [EXTRACTED]
  scripts/record_episode.py → pzrl/train.py
- `main()` --calls--> `idle()`  [EXTRACTED]
  scripts/record_episode.py → pzrl/baselines.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **M2 fake-vs-real calibration chain (B2-B9)** — docs_experiments_2026_10_30_b2_m2_fake_vs_real, docs_experiments_2026_10_30_b3_m2a_fake_one_kill, docs_experiments_2026_10_30_b4_m2a_fake_fix, docs_experiments_2026_10_30_b5_m2_bite_sweep, docs_experiments_2026_10_30_b6_m2_confirm, docs_experiments_2026_10_30_b7_m2_two_knob_sweep, docs_experiments_2026_10_30_b8_m2_low_bite_sweep, docs_experiments_2026_10_30_b9_m2_confirm_low_bite [EXTRACTED 1.00]
- **Option E bridge stack (agent sockets, RLBridge Lua, Python env)** — docs_approach_java_agent, docs_approach_rlbridge, docs_approach_server_channel, docs_approach_client_control_socket, docs_approach_pzparallelenv [EXTRACTED 1.00]
- **Fake-backend fidelity calibrations against the real client** — docs_approach_synthetic_bite_rule, docs_approach_walk_speed_calibration, docs_approach_combat_calibration, docs_approach_explicit_melee, docs_approach_matched_comparison [INFERRED 0.85]
- **M0 measurement-trust nuisance variable investigations** — docs_experiments_2026_10_30_retro_r3_latency_hypothesis, docs_experiments_2026_10_30_retro_r4_time_of_day, docs_experiments_2026_10_30_retro_r5_corpses, docs_experiments_2026_10_30_retro_r8_spawn_geometry, docs_experiments_2026_10_30_retro_block_drift [INFERRED 0.85]
- **Solo fight milestone chain (baseline -> fidelity -> imitation -> PPO)** — docs_milestones_m1, docs_milestones_m2a, docs_milestones_m2, docs_milestones_m3a, docs_milestones_m3b [EXTRACTED 1.00]
- **Hybrid planner track H (plumbing, skills, rule comparison)** — docs_journal_hybrid_planner, docs_journal_client_skills, docs_journal_skill_reliability_batches, docs_journal_rule_planner, docs_milestones_h_a, docs_milestones_h_b, docs_milestones_h_c [EXTRACTED 1.00]
- **Measurement rigor (drift, interleaving, pooled acceptance)** — docs_journal_block_drift, docs_journal_interleaved_arms, claude_experiment_protocol, docs_milestones_acceptance_test_rule [INFERRED 0.85]
- **H-B0 loot-failure debugging chain (HB0b to HB0f)** — docs_experiments_2026_11_14_hb0b_skill_unit_tests_hb0b_experiment, docs_experiments_2026_11_14_hb0c_reliability_rerun_hb0c_experiment, docs_experiments_2026_11_14_hb0d_loot_by_coordinates_hb0d_experiment, docs_experiments_2026_11_14_hb0e_loot_reachable_hb0e_experiment, docs_experiments_2026_11_14_hb0f_loot_known_container_hb0f_experiment [EXTRACTED 1.00]
- **H-B interleaved arms llm/rule/idle** — docs_experiments_2026_11_14_hb_planner_vs_rules_llm_planner_arm, docs_experiments_2026_11_14_hb_planner_vs_rules_rule_planner_arm, docs_experiments_2026_11_14_hb_planner_vs_rules_idle_arm [EXTRACTED 1.00]
- **H-B scenario limitations to fix before next scenario** — docs_experiments_2026_11_14_hb_planner_vs_rules_thirst_not_set, docs_experiments_2026_11_14_hb_planner_vs_rules_survey_8_container_cap, docs_experiments_2026_11_14_hb_planner_vs_rules_shelf_accumulation [EXTRACTED 1.00]

## Communities (76 total, 51 thin omitted)

### Community 0 - "Architecture options"
Cohesion: 0.05
Nodes (53): Approach (architectures and evidence log), Aim override (RLMouse, rlAim) on the real client, Scripted baselines (pzrl/baselines.py, charge fighter), Fake-client control socket (goto, speed, tp, weapon, attack), Fake combat calibrated to real client (pzrl/combat.py: hit chance 0.46, lognormal damage), Connection flow CONNECT-LOGIN-CHECKSUM-LOAD_PROFILE-CREATE_PLAYER-PLAYER_CONNECT-RUN, DAgger cloning of the charge fighter onto the real client, zombie.network.FakeClientManager (headless load-test client) (+45 more)

### Community 1 - "Experiment cards (batches 1-12)"
Cohesion: 0.05
Nodes (48): B10 M3 gate A: PPO fighter on calibrated fake, pzrl.train shared-policy PPO (torch only), Sample throughput bottleneck (~3 samples/s; target >= 20), B11 M3a gate A: behaviour-cloned fighter vs scripted on fake, models/fight_bc3.pt behaviour-cloned checkpoint (sha1 e624cb83a0), B12 M3a Gate B Card (BC vs scripted, real client), fight_bc3.pt behaviour-cloned fighter, Session 2 restart-from-scratch resume plan (+40 more)

### Community 2 - "Training and imitation scripts"
Cohesion: 0.07
Nodes (23): charge(), charge_param(), policy(), _dir_to_action(), flee(), idle(), nearest_mate_vec(), nearest_zombie_vec() (+15 more)

### Community 3 - "Java agent bridge"
Cohesion: 0.08
Nodes (4): RLAgent, RLClientControl, Peer, RLServerChannel

### Community 4 - "Hybrid skill debugging (HB0 chain)"
Cohesion: 0.06
Nodes (45): Server bot relay passes only two arguments (now three), Client-only items rejected by server-checked actions, Game entry points eatItem / onDrinkFluid, HB0b: in-game unit tests of one-shot skills, Characters persist across runs (inventory not reset), Rotten food counted by survey (now edible-only), Server seed command (seed|user|type|n|r), Container index renumbered by distance during decision (+37 more)

### Community 5 - "Hybrid planner track"
Cohesion: 0.06
Nodes (36): H-A Hybrid Planner Plumbing Card, claude -p Sonnet planner (structured JSON, no tools), Last-skill outcome feedback to planner, H-A run 1 invalid (stale bot file), Server-authoritative stats (RLBridge stats handler), Skill menu (fight, flee, wait, eat, drink, bandage, loot), Skill reliability gap (effects in 21-44% of uses), H-B0 Skill Reliability Card (+28 more)

### Community 6 - "Milestones and calibration"
Cohesion: 0.06
Nodes (36): CLAUDE.md project instructions, Cleanup script (scripts/cleanup.py), Experiment cards and daily milestone review, Option E architecture (fake clients + Java agent + RLBridge Lua + pzrl), Rendered clients backend (RLBot.lua, pzrl/rendered.py), Synthetic bite rule (not real-game behaviour), Time scaling (-TimeScale K), Journal and task queue (+28 more)

### Community 7 - "PZParallelEnv core"
Cohesion: 0.10
Nodes (4): PZParallelEnv, frame(), main(), wait_idle()

### Community 8 - "Server Lua bridge"
Cohesion: 0.10
Nodes (22): ack(), applyBites(), drain(), findPlayer(), handlers.bot(), handlers.ensure(), handlers.ensureroot(), handlers.give() (+14 more)

### Community 9 - "Client bot commands"
Cohesion: 0.10
Nodes (22): commands.attack(), commands.equip(), commands.goto(), commands.info(), commands.reload(), equip(), log(), nearestZombie() (+14 more)

### Community 10 - "Bytecode transformers"
Cohesion: 0.12
Nodes (3): RLMouseTransformer, RLNoRenderTransformer, RLTimeTransformer

### Community 11 - "Env scripts and demos"
Cohesion: 0.12
Nodes (3): _acquire_lock(), _pid_alive(), _release_lock()

### Community 12 - "Launcher process control"
Cohesion: 0.11
Nodes (5): kill_clients(), kill_rendered(), kill_stale(), Launcher, _ps()

### Community 13 - "Benchmark and version tracking"
Cohesion: 0.14
Nodes (14): git_commit(), have_reference(), main(), report(), row(), run_interleaved(), run_lab(), run_policy() (+6 more)

### Community 14 - "Analysis scripts"
Cohesion: 0.14
Nodes (5): sample_spawns(), corr(), feats(), geometry(), report()

### Community 15 - "Environment invariants"
Cohesion: 0.11
Nodes (12): ask(), busy(), client_query(), _kv(), newest_log(), outcome(), rule_decide(), run_one_shot() (+4 more)

### Community 16 - "Server channel and dev tools"
Cohesion: 0.11
Nodes (3): ServerChannel, me(), me()

### Community 17 - "Run validity watchdog"
Cohesion: 0.13
Nodes (12): arm_rotation(), check(), episodes(), main(), parse(), planner_health(), read_rows(), selftest() (+4 more)

### Community 18 - "Environment invariants"
Cohesion: 0.14
Nodes (12): check_alive(), check_in_arena(), check_one_bat(), parse_inv(), Chan, Ctl, fake_env(), test_bat_pile_is_repaired() (+4 more)

### Community 19 - "Launcher process control"
Cohesion: 0.17
Nodes (10): rendered_alive(), _ancestors(), kind(), listeners(), main(), ours(), procs(), show() (+2 more)

### Community 21 - "Task definitions and rewards"
Cohesion: 0.16
Nodes (7): dist(), Fight, nearest_other(), Rendezvous, SafeRendezvous, Survive, Task

### Community 24 - "Environment invariants"
Cohesion: 0.23
Nodes (3): client_count(), run_all(), world_snapshot()

### Community 29 - "Community 33"
Cohesion: 0.80
Nodes (4): enabled(), install(), log(), RL.createStep()

### Community 31 - "Community 37"
Cohesion: 0.83
Nodes (3): install(), log(), readCfg()

### Community 32 - "Community 38"
Cohesion: 0.83
Nodes (3): log(), report(), spawnNpc()

## Knowledge Gaps
- **52 isolated node(s):** `pzrl.train shared-policy PPO (torch only)`, `fight-v4 dirt field (5377,10114)`, `env.ztrace per-zombie instrumentation`, `Frame limiter spin (1-core client load)`, `PZ_SETTLE reset-wait multiplier` (+47 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 333 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **51 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Per-episode data 2026-10-30 (headless and drift hunt)` connect `Milestones and calibration` to `Training and imitation scripts`, `Analysis scripts`?**
  _High betweenness centrality (0.151) - this node is a cross-community bridge._
- **What connects `pzrl.train shared-policy PPO (torch only)`, `fight-v4 dirt field (5377,10114)`, `env.ztrace per-zombie instrumentation` to the rest of the system?**
  _52 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Architecture options` be split into smaller, more focused modules?**
  _Cohesion score 0.053185271770894216 - nodes in this community are weakly interconnected._
- **Should `Experiment cards (batches 1-12)` be split into smaller, more focused modules?**
  _Cohesion score 0.0544464609800363 - nodes in this community are weakly interconnected._
- **Should `Training and imitation scripts` be split into smaller, more focused modules?**
  _Cohesion score 0.07330827067669173 - nodes in this community are weakly interconnected._
- **Should `Java agent bridge` be split into smaller, more focused modules?**
  _Cohesion score 0.08067375886524823 - nodes in this community are weakly interconnected._
- **Should `Hybrid skill debugging (HB0 chain)` be split into smaller, more focused modules?**
  _Cohesion score 0.05851063829787234 - nodes in this community are weakly interconnected._