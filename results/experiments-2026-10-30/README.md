# Per-episode data, 2026-10-30 headless-client and drift-hunt experiments

One JSON line per episode as printed by `scripts/rendered_fight_lab.py` (fight-v4, dirt field 5377,10114, 2 zombies, `charge:1.8:0` unless noted).
Fields: steps, attack_actions, zombies_start/end, damage_end, min_hp, world (time of day, light, corpses, ...), arm, policy where present.
Episodes with steps < 5 are aborted resets after deaths and must be excluded (scripts/compare_arms.py does).
Analyse an interleaved file with `python scripts/compare_arms.py <file>.jsonl` (--by arm|policy).
Findings are in docs/journal.md (hour 1-3 and drift hunt sections) and docs/headless-client.md.

- `h1_baseline_render_on.jsonl` (8 episode lines): 1x, normal client, charge:1.8:0, fight-v4, 07:55, game time ~21h night, ~230 corpses
- `h1_world_draw_off.jsonl` (9 episode lines): 1x, norender=world patch, charge:1.8:0, 08:21, night, ~230 corpses
- `h2_2x_settle1_broken.jsonl` (8 episode lines): 2x clock, settle x1: fidelity collapse (reset waits too short in real time)
- `h2_2x_settle2_10eps.jsonl` (10 episode lines): 2x clock, PZ_SETTLE=2, 10 episodes
- `h2_4x_settle4_broken.jsonl` (10 episode lines): 4x clock, PZ_SETTLE=4: broken
- `h2_2x_settle2_24eps.jsonl` (22 episode lines): 2x clock, PZ_SETTLE=2, 24 requested (22 lines), seed 11
- `h3_1x_plus300ms.jsonl` (15 episode lines): 1x with PZ_CMD_DELAY_MS=300
- `h3_1x_control.jsonl` (10 episode lines): 1x no delay, same block as the delay run
- `drift_first_world_snapshots.jsonl` (1 episode lines): 1x, first run with per-episode world snapshot (night, 232 corpses)
- `drift_arm_v1_flawed.jsonl` (2 episode lines): interleaved arms v1: server-side corpse removal did not reach the client (kept as a record of the flaw)
- `drift_noon_cleared_pool.jsonl` (20 episode lines): arm run v2: both arms effectively noon with corpses cleared (arm A's changes persisted into arm B)
- `drift_dark_v1_flawed.jsonl` (30 episode lines): noon vs '1 AM' v1: arm B clock reverted to the server's noon (flawed)
- `drift_noon_vs_1am.jsonl` (40 episode lines): noon vs 1 AM, server clock per arm, corpses cleared in both: CLEAN null result
- `drift_cleared_vs_pile250.jsonl` (40 episode lines): noon, arm A corpses cleared vs arm B pile of 250 bodies: suggestive, not significant
