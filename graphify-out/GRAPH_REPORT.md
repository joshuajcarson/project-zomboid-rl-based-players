# Graph Report - project-zomboid-rl-based-players  (2026-11-15)

## Corpus Check
- 22 files · ~107,085 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 977 nodes · 1734 edges · 90 communities (36 shown, 54 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 98 edges (avg confidence: 0.84)
- Token cost: 244,525 input · 0 output

## Community Hubs (Navigation)
- Architecture options
- Experiment cards (batches 1-12)
- Java agent bridge
- Hybrid skill debugging (HB0 chain)
- PZParallelEnv core
- Server Lua bridge
- Training and imitation scripts
- Client bot commands
- Bytecode transformers
- Env scripts and demos
- Run validity watchdog
- Server channel and dev tools
- Benchmark and version tracking
- Environment invariants
- Rendered client control
- Scenario fixes (HBfix chain)
- Launcher process control
- Environment invariants
- Analysis scripts
- Environment invariants
- Milestones and calibration
- Hybrid planner track
- Launcher process control
- Server channel and dev tools
- Task definitions and rewards
- Training and imitation scripts
- Hybrid planner track
- Planner learning tracks (H-L, H-D)
- Milestones and calibration
- Planner vs rules and engagement gap
- Milestones and calibration
- PZParallelEnv core
- Milestones and calibration
- Planner-learning analysis script
- Community 28
- Milestones and calibration
- Hybrid planner track
- Training and imitation scripts
- Community 32
- Community 33
- Env lock and combat model
- Community 37
- Community 38
- Community 39
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
- Hybrid planner track
- Milestones and calibration
- Watchdog checks
- Watchdog checks
- Watchdog checks
- Watchdog checks
- Community 75
- Community 76
- Community 77

## God Nodes (most connected - your core abstractions)
1. `PZParallelEnv` - 44 edges
2. `ServerChannel` - 20 edges
3. `Journal and task queue` - 19 edges
4. `Planner learning design` - 19 edges
5. `ClientControl` - 18 edges
6. `main()` - 17 edges
7. `RenderedControl` - 16 edges
8. `Launcher` - 14 edges
9. `HB: Hybrid planner vs rule planner vs idle (survival)` - 14 edges
10. `main()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Separate training phase and frozen evaluation` --semantically_similar_to--> `Experiment batch protocol (pre-register, interleave, verdict)`  [INFERRED] [semantically similar]
  docs/planner-learning.md → CLAUDE.md
- `Interleaved arms in one session, 30+ eps, report z` --semantically_similar_to--> `benchmark.py --interleave`  [INFERRED] [semantically similar]
  docs/journal.md → CLAUDE.md
- `Acceptance-test rule (pooled >= 2 sessions, target + failure bound)` --semantically_similar_to--> `Experiment batch protocol (pre-register, interleave, verdict)`  [INFERRED] [semantically similar]
  docs/milestones.md → CLAUDE.md
- `try()` --calls--> `log()`  [INFERRED]
  scripts/rl_bot_dev.lua → mods/RLBridge/common/media/lua/server/RLBridge.lua
- `Fake calibration: bite 2.25 / hit scale 0.6` --references--> `Synthetic bite rule (fake zombie damage)`  [INFERRED]
  docs/journal.md → CLAUDE.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Engagement gap investigation (HB-F -> H-L1 -> H-D1)** — docs_experiments_2026_11_15_hbf_planner_vs_rules_fixed, docs_experiments_2026_11_15_hl1_lessons, docs_experiments_2026_11_15_hd1_engagement_reflex, docs_experiments_2026_11_15_hbf_planner_vs_rules_fixed_engagement_weakness [EXTRACTED 1.00]
- **Fake-backend fidelity chain (artifact fix, calibration, imitation gate)** — docs_journal_fake_one_kill_artifact, docs_journal_fake_calibration_bite_hit, docs_milestones_m2a, docs_milestones_m2, docs_milestones_m3a [EXTRACTED 1.00]
- **H-B0 loot-failure debugging chain (HB0b to HB0f)** — docs_experiments_2026_11_14_hb0b_skill_unit_tests_hb0b_experiment, docs_experiments_2026_11_14_hb0c_reliability_rerun_hb0c_experiment, docs_experiments_2026_11_14_hb0d_loot_by_coordinates_hb0d_experiment, docs_experiments_2026_11_14_hb0e_loot_reachable_hb0e_experiment, docs_experiments_2026_11_14_hb0f_loot_known_container_hb0f_experiment [EXTRACTED 1.00]
- **H-B interleaved arms llm/rule/idle** — docs_experiments_2026_11_14_hb_planner_vs_rules_llm_planner_arm, docs_experiments_2026_11_14_hb_planner_vs_rules_rule_planner_arm, docs_experiments_2026_11_14_hb_planner_vs_rules_idle_arm [EXTRACTED 1.00]
- **H-B scenario limitations to fix before next scenario** — docs_experiments_2026_11_14_hb_planner_vs_rules_thirst_not_set, docs_experiments_2026_11_14_hb_planner_vs_rules_survey_8_container_cap, docs_experiments_2026_11_14_hb_planner_vs_rules_shelf_accumulation [EXTRACTED 1.00]
- **HBfix to HBfix6 scenario validation chain** — docs_experiments_2026_11_14_hbfix_scenario_fixes, docs_experiments_2026_11_14_hbfix2_rerun, docs_experiments_2026_11_15_hbfix3_rerun, docs_experiments_2026_11_15_hbfix4_rerun, docs_experiments_2026_11_15_hbfix5_rerun, docs_experiments_2026_11_15_hbfix6_rerun [EXTRACTED 1.00]
- **Watchdog checks added from HBfix incidents** — docs_watchdog_stray_supplies, docs_watchdog_skill_health, docs_watchdog_immobile, docs_watchdog_add_check_rule [EXTRACTED 1.00]
- **M2 fake-vs-real calibration chain (B2-B9)** — docs_experiments_2026_10_30_b2_m2_fake_vs_real, docs_experiments_2026_10_30_b3_m2a_fake_one_kill, docs_experiments_2026_10_30_b4_m2a_fake_fix, docs_experiments_2026_10_30_b5_m2_bite_sweep, docs_experiments_2026_10_30_b6_m2_confirm, docs_experiments_2026_10_30_b7_m2_two_knob_sweep, docs_experiments_2026_10_30_b8_m2_low_bite_sweep, docs_experiments_2026_10_30_b9_m2_confirm_low_bite [EXTRACTED 1.00]
- **Option E bridge stack (agent sockets, RLBridge Lua, Python env)** — docs_approach_java_agent, docs_approach_rlbridge, docs_approach_server_channel, docs_approach_client_control_socket, docs_approach_pzparallelenv [EXTRACTED 1.00]
- **Planner learning mechanisms H-L1..H-L5** — docs_planner_learning_lessons_file, docs_planner_learning_skill_library, docs_planner_learning_instruction_tuning, docs_planner_learning_distillation, docs_planner_learning_model_choice [EXTRACTED 1.00]
- **Fake-backend fidelity calibrations against the real client** — docs_approach_synthetic_bite_rule, docs_approach_walk_speed_calibration, docs_approach_combat_calibration, docs_approach_explicit_melee, docs_approach_matched_comparison [INFERRED 0.85]
- **M0 measurement-trust nuisance variable investigations** — docs_experiments_2026_10_30_retro_r3_latency_hypothesis, docs_experiments_2026_10_30_retro_r4_time_of_day, docs_experiments_2026_10_30_retro_r5_corpses, docs_experiments_2026_10_30_retro_r8_spawn_geometry, docs_experiments_2026_10_30_retro_block_drift [INFERRED 0.85]
- **Measurement trust stack (invariants, interleaving, pooled acceptance, watchdog)** — docs_journal_environment_invariants, docs_journal_interleaved_arms_rule, docs_milestones_acceptance_test_rule, docs_journal_watchdog, claude_experiment_protocol [INFERRED 0.85]

## Communities (90 total, 54 thin omitted)

### Community 0 - "Architecture options"
Cohesion: 0.05
Nodes (53): Approach (architectures and evidence log), Aim override (RLMouse, rlAim) on the real client, Scripted baselines (pzrl/baselines.py, charge fighter), Fake-client control socket (goto, speed, tp, weapon, attack), Fake combat calibrated to real client (pzrl/combat.py: hit chance 0.46, lognormal damage), Connection flow CONNECT-LOGIN-CHECKSUM-LOAD_PROFILE-CREATE_PLAYER-PLAYER_CONNECT-RUN, DAgger cloning of the charge fighter onto the real client, zombie.network.FakeClientManager (headless load-test client) (+45 more)

### Community 1 - "Experiment cards (batches 1-12)"
Cohesion: 0.06
Nodes (45): B10 M3 gate A: PPO fighter on calibrated fake, pzrl.train shared-policy PPO (torch only), Sample throughput bottleneck (~3 samples/s; target >= 20), B11 M3a gate A: behaviour-cloned fighter vs scripted on fake, models/fight_bc3.pt behaviour-cloned checkpoint (sha1 e624cb83a0), B12 M3a Gate B Card (BC vs scripted, real client), fight_bc3.pt behaviour-cloned fighter, Session 2 restart-from-scratch resume plan (+37 more)

### Community 2 - "Java agent bridge"
Cohesion: 0.08
Nodes (4): RLAgent, RLClientControl, Peer, RLServerChannel

### Community 3 - "Hybrid skill debugging (HB0 chain)"
Cohesion: 0.07
Nodes (36): Server bot relay passes only two arguments (now three), Client-only items rejected by server-checked actions, Game entry points eatItem / onDrinkFluid, HB0b: in-game unit tests of one-shot skills, Characters persist across runs (inventory not reset), Rotten food counted by survey (now edible-only), Server seed command (seed|user|type|n|r), Container index renumbered by distance during decision (+28 more)

### Community 4 - "PZParallelEnv core"
Cohesion: 0.10
Nodes (4): PZParallelEnv, frame(), main(), wait_idle()

### Community 5 - "Server Lua bridge"
Cohesion: 0.09
Nodes (22): ack(), applyBites(), drain(), findPlayer(), handlers.bot(), handlers.ensure(), handlers.ensureroot(), handlers.give() (+14 more)

### Community 6 - "Training and imitation scripts"
Cohesion: 0.14
Nodes (11): collect(), fit(), main(), ActorCritic, evaluate(), gae(), main(), plot_curve() (+3 more)

### Community 7 - "Client bot commands"
Cohesion: 0.10
Nodes (22): commands.attack(), commands.equip(), commands.goto(), commands.info(), commands.reload(), equip(), log(), nearestZombie() (+14 more)

### Community 8 - "Bytecode transformers"
Cohesion: 0.12
Nodes (3): RLMouseTransformer, RLNoRenderTransformer, RLTimeTransformer

### Community 9 - "Env scripts and demos"
Cohesion: 0.12
Nodes (4): idle(), _acquire_lock(), _pid_alive(), _release_lock()

### Community 10 - "Run validity watchdog"
Cohesion: 0.09
Nodes (16): Run watchdog: checks and incidents, arm_rotation(), check(), episodes(), immobile(), main(), parse(), planner_health() (+8 more)

### Community 12 - "Benchmark and version tracking"
Cohesion: 0.14
Nodes (14): git_commit(), have_reference(), main(), report(), row(), run_interleaved(), run_lab(), run_policy() (+6 more)

### Community 13 - "Environment invariants"
Cohesion: 0.10
Nodes (12): ask(), busy(), client_query(), episode_log(), _kv(), lessons_system(), newest_log(), outcome() (+4 more)

### Community 14 - "Rendered client control"
Cohesion: 0.12
Nodes (3): RenderedControl, me(), me()

### Scenario fixes (HBfix chain) - "Scenario fixes (HBfix chain)"
Cohesion: 0.12
Nodes (23): HBfix2 Rerun with per-episode stray-seed clearing (INCONCLUSIVE), Loot by container index (lootat|x|y|ci), Planner over-gathering, Session-wide loot failure memory, HBfix Scenario Fixes Experiment (FAILURE), clearnear server command, hybrid_run --fixes scenario (auto-drink off, strip, clearat), Skill effectiveness criteria (drink/eat/loot >= 70%) (+15 more)

### Community 16 - "Launcher process control"
Cohesion: 0.14
Nodes (5): kill_clients(), kill_rendered(), kill_stale(), Launcher, _ps()

### Community 17 - "Environment invariants"
Cohesion: 0.16
Nodes (5): reflect(), client_count(), run_all(), world_snapshot(), items_total()

### Community 18 - "Analysis scripts"
Cohesion: 0.14
Nodes (9): rule_decide(), state_text(), sample_spawns(), Per-episode data 2026-10-30 (headless and drift hunt), corr(), feats(), geometry(), report() (+1 more)

### Community 19 - "Environment invariants"
Cohesion: 0.14
Nodes (12): check_alive(), check_in_arena(), check_one_bat(), parse_inv(), Chan, Ctl, fake_env(), test_bat_pile_is_repaired() (+4 more)

### Community 20 - "Milestones and calibration"
Cohesion: 0.15
Nodes (14): CLAUDE.md project instructions, benchmark.py --interleave, Cleanup script (scripts/cleanup.py), Daily milestone review job (pz-daily-milestone-review), Experiment cards (docs/experiments/), Game version tracking (track_game_version.py), Reset head start: zombies walk ~6-7 s before first action, Spawn geometry: damage rises with angular separation (+6 more)

### Community 21 - "Hybrid planner track"
Cohesion: 0.13
Nodes (17): H-A run 1 invalid (stale bot file), Journal and task queue, Bat pile-up from repeated giveitem, Corpse pile effect (+10.4 damage, z 1.25), Drift hunt: block-to-block variance of the same policy, Endurance and panic cut melee damage, Environment realism roadmap (pz-mechanics.md), Fixed scenario (hybrid_run --fixes, HBfix to HBfix6) (+9 more)

### Community 22 - "Launcher process control"
Cohesion: 0.17
Nodes (10): rendered_alive(), _ancestors(), kind(), listeners(), main(), ours(), procs(), show() (+2 more)

### Community 24 - "Task definitions and rewards"
Cohesion: 0.16
Nodes (7): dist(), Fight, nearest_other(), Rendezvous, SafeRendezvous, Survive, Task

### Community 25 - "Training and imitation scripts"
Cohesion: 0.20
Nodes (9): charge(), charge_param(), policy(), _dir_to_action(), flee(), nearest_mate_vec(), nearest_zombie_vec(), parse_policy() (+1 more)

### Community 26 - "Hybrid planner track"
Cohesion: 0.20
Nodes (13): H-A Hybrid Planner Plumbing Card, claude -p Sonnet planner (structured JSON, no tools), Last-skill outcome feedback to planner, Server-authoritative stats (RLBridge stats handler), Skill menu (fight, flee, wait, eat, drink, bandage, loot), Skill reliability gap (effects in 21-44% of uses), H-B0 Skill Reliability Card, busy command / run_one_shot wait-for-queue (+5 more)

### Planner learning tracks (H-L, H-D) - "Planner learning tracks (H-L, H-D)"
Cohesion: 0.23
Nodes (11): H-D1 Division of labour: horde/engagement skill vs planner [next], H-D2 Planner latency sweep [not started], H-F Planner vs rules on the fixed scenario [inconclusive], H-L1 Planner learns from a lessons file [inconclusive (negative)], H-L2 Skill library grows [not started], H-L3 Instruction tuning [not started], Planner learning design, Instruction tuning against measured weaknesses (+3 more)

### Community 28 - "Milestones and calibration"
Cohesion: 0.20
Nodes (10): Java agent (agent/, control socket and observation channel), Option E architecture (fake clients + Java agent + RLBridge Lua + pzrl), pzrl PZParallelEnv (PettingZoo-style, survive/rendezvous/fight), Rendered client backend (RLBot.lua, ~4 GB each), RLBridge server/client Lua mod, Synthetic bite rule (fake zombie damage), Time scaling (-TimeScale K), Headless client study (norender, clock patch) (+2 more)

### Planner vs rules and engagement gap - "Planner vs rules and engagement gap"
Cohesion: 0.25
Nodes (11): HB-F Planner vs rules vs idle on fixed scenario (INCONCLUSIVE), Planner engagement weakness (dies more, better needs), Rule planner (rule arm), Sonnet LLM planner (llm arm), H-D1 Engagement reflex experiment (pending), Division of labour: real-time skill vs planner, Engagement reflex (llmR: fight, flee below 35 hp within 3 tiles), H-L1 Lessons file experiment (INCONCLUSIVE, negative tendency) (+3 more)

### Community 30 - "Milestones and calibration"
Cohesion: 0.27
Nodes (10): BC checkpoint models/fight_bc3.pt, Fake calibration: bite 2.25 / hit scale 0.6, Fake one-kill artifact: server ignores lethal hits, PPO from scratch limited by ~3 samples/s, H-L4 Distil planner into a learned real-time policy [not started], M2 Fake-vs-real fidelity for the solo fight [done on means], M2a Fake fight artifact found and fixed [done], M3a Imitation gate (BC fighter non-inferior) [in progress] (+2 more)

### Community 32 - "Milestones and calibration"
Cohesion: 0.22
Nodes (9): fight-v4 protocol (dirt field 5377,10114), IsoHutch chunk-unload crash (dog house near arena), Open fight field search (openness scan, fight-v3/v4), Swing distance study (charge 1.3-3.0), Zero-population world breaks zombie spawns, Results ledger (generated report), Protocol fight-v1 results, Protocol fight-v3 results (cornfield 4010,11767) (+1 more)

### Planner-learning analysis script - "Planner-learning analysis script"
Cohesion: 0.48
Nodes (5): load(), main(), mse(), wasted(), z()

### Community 36 - "Milestones and calibration"
Cohesion: 0.33
Nodes (5): H-C Two agents cooperate through planner chat [not started], M5 Two cooperating agents, one real [not started], M6 Client memory budget for 2+ real clients [not started], M7 Four cooperating agents with real validation at two [not started], Layered agent end state

### Community 37 - "Hybrid planner track"
Cohesion: 0.33
Nodes (6): Hybrid planner (claude -p over a skill menu, pzrl/hybrid.py), seedat into reachable shelf 10753,9407, Skill reliability chain HB0 to HB0f, H-A Hybrid planner plumbing [done], Planner-as-supervisor (re-planning after skill failure), Stateless claude -p planner call with state text

### Community 41 - "Community 33"
Cohesion: 0.80
Nodes (4): enabled(), install(), log(), RL.createStep()

### Community 44 - "Community 37"
Cohesion: 0.83
Nodes (3): install(), log(), readCfg()

### Community 45 - "Community 38"
Cohesion: 0.83
Nodes (3): log(), report(), spawnNpc()

## Knowledge Gaps
- **66 isolated node(s):** `Fake-client scenario file (client/player/movements)`, `ServerMap.characterIn / GameServer.Players chunk loading`, `Per-client RAM ~4.2 GB regardless of drawing`, `Character stats and moodles`, `Panic melee penalty` (+61 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 354 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **54 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Planner learning design` connect `Planner learning tracks (H-L, H-D)` to `Milestones and calibration`, `Hybrid planner track`, `Milestones and calibration`, `Planner vs rules and engagement gap`, `Milestones and calibration`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **What connects `Fake-client scenario file (client/player/movements)`, `ServerMap.characterIn / GameServer.Players chunk loading`, `Per-client RAM ~4.2 GB regardless of drawing` to the rest of the system?**
  _66 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Architecture options` be split into smaller, more focused modules?**
  _Cohesion score 0.053185271770894216 - nodes in this community are weakly interconnected._
- **Why does `H-L1 Lessons file experiment (INCONCLUSIVE, negative tendency)` connect `Planner vs rules and engagement gap` to `Env scripts and demos`, `Planner-learning analysis script`, `Planner learning tracks (H-L, H-D)`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Should `Experiment cards (batches 1-12)` be split into smaller, more focused modules?**
  _Cohesion score 0.057912457912457915 - nodes in this community are weakly interconnected._
- **Why does `Journal and task queue` connect `Hybrid planner track` to `Milestones and calibration`, `Hybrid planner track`, `Analysis scripts`, `Milestones and calibration`, `Planner learning tracks (H-L, H-D)`, `Milestones and calibration`, `Milestones and calibration`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Should `Java agent bridge` be split into smaller, more focused modules?**
  _Cohesion score 0.08067375886524823 - nodes in this community are weakly interconnected._