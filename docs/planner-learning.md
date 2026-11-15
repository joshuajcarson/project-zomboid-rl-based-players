# Planner learning: how the hybrid planner gets better at its goals over time

Written 2026-11-15 (user request). This is the design that track H-L in `docs/milestones.md` follows. Every claim below still goes through the batch protocol in CLAUDE.md: a pre-registered card, interleaved arms, pooled sessions, a watchdog on every run.

## Where we are

Each planner decision is a stateless `claude -p` call (Sonnet, no tools). It gets a fixed system prompt (the skills and goals), a state text (health, needs, wounds, inventory, zombie distances, nearby containers), what its last skill did, and which containers failed earlier. Nothing carries over between episodes except the failed-container marks. Every improvement so far (H-A, the H-B0 chain, HBfix to HBfix6) came from a person changing the harness: skills that work, a clean world, better state information.

## The two questions

1. **Can the planner get better at its goals from its own experience, without weight training?** H-L tracks this.
2. **Which work belongs in fast dedicated skills and which in the slow, adaptable planner?** This runs through every experiment: each H-L card records where the decisive behaviour came from.

## Ways to make it better, in the order we test them

| # | Mechanism | What changes | Cost | Track step |
|---|---|---|---|---|
| 1 | **Lessons file** (Reflexion / Voyager-style reflection) | After each episode, one extra model call reads that episode's decision log and outcome and rewrites a short list of lessons (at most 8, each under 25 words); the list goes into every later prompt | 1 call per episode | H-L1 |
| 2 | **Skill library** | New higher-level skills composed from existing ones (e.g. `restock`, `retreat_and_bandage`); proposed by the planner or written by us, kept only if a card shows they help | engineering per skill | H-L2 |
| 3 | **Instruction tuning** | Prompt edits aimed at measured weaknesses (over-gathering, far piles) | cheap, but hand-tuned: always a card, never a silent edit | H-L3 |
| 4 | **Distillation into a learned policy** | Planner decision logs (state, skill, outcome) become behaviour-cloning data; then PPO on the fake backend; the planner becomes a teacher, the student runs in real time without API calls | links to M3a/M3b | H-L4 |
| 5 | **Model choice** | Haiku / Sonnet / Opus as arms | per-call cost | H-L5 (any time) |

### Rules that apply to every learning arm

- **Learning and evaluation are separate phases.** A planner that changes during a session cannot be compared fairly inside it. Each H-L experiment has:
  - a *training phase*, where the lessons, skills or prompt evolve; we report its learning curve as exploratory;
  - a *frozen evaluation*: the learned artefact is fixed and tested against the plain planner (and the rule planner), interleaved, in fresh sessions, with pre-registered criteria.
- **Every learned artefact is a file in `results/`** (lessons JSON, skill list, prompt version) with its hash recorded on the card, so any result can be rerun with exactly what was learned.
- **No leaking of the evaluation.** Lessons are written only from training-phase episodes; evaluation sessions use other seeds.
- **Drift check.** A learned artefact is re-evaluated after any scenario or skill change. A lesson about one world layout ("the counters in the east building cannot be looted") is scenario knowledge, not general skill, and the card says which kind each lesson is.

## Skills vs planner: the division-of-labour question

Working hypothesis, from the evidence so far:

| Put it in a dedicated real-time skill when... | Leave it to the planner when... |
|---|---|
| the decision must change several times a second (melee spacing, swing timing, dodging, kiting a horde) | the situation changes over tens of seconds or longer (what to do next, where to go, what to carry) |
| the goal is fixed and measurable per tick (kill this zombie, break line of sight) | goals compete and the right trade-off depends on context (eat now vs loot first vs fight) |
| the world mechanics are known and stable (a weapon's reach, a door) | the situation is new or rare (an unknown building, an unexpected failure, a teammate's request) |
| a wrong half-second costs health (a planner's ~3 s latency is fatal) | being slow costs little and being wrong costs a lot (wasted trips, bad routes) |
| the behaviour can be learned or tuned offline (scripted charge, BC/PPO fighters) | the behaviour needs reading a varied state description or text (chat with teammates in H-C) |

Evidence so far:
- planner latency is about 3 s, fine for strategy and fatal for melee;
- the scripted fighter does the fighting in all hybrid runs;
- the planner manages needs better than the rule planner (pooled needs 0.20 vs 0.30 in H-B, 0.16 vs 0.30 in HB-F) but dies slightly more often;
- the planner's mistakes are judgement mistakes (over-gathering, chasing far piles), the kind lessons should fix.

How each experiment feeds this question. Every H-track card adds a line **"division of labour:"** saying which behaviours decided the outcome and whether they came from a skill or from the planner. Planned probes:
- **Horde handling (H-D1):** 6-10 zombies. Compare the planner choosing fight/flee every decision with a dedicated `horde` skill (scripted kiting and retreat, later learned) that the planner only switches on. This predicts the skill wins on survival and the planner adds value only in deciding when to engage.
- **Latency sweep (H-D2):** add an artificial 0 / 3 / 10 s decision delay to the planner arm on the needs scenario. This shows how much of its value survives slower thinking, and where the break-even with the rule planner lies.
- **Planner-as-supervisor:** skills report "done / failed / interrupted" (already partly in place through `outcome()`). Measure how often the planner's re-planning after a failure beats the rule planner's fixed fallback.

The expected end state is a layered agent:
- real-time skills (scripted or learned by RL) for anything at the scale of seconds;
- a planner choosing and parameterising skills at the scale of tens of seconds;
- lessons and a skill library that grow with experience;
- teammates coordinating through the planner (H-C).

## H-L1 (first experiment): does a lessons file make the planner better?

- **Scenario:** the validated fixed scenario (`hybrid_run.py --fixes`, as in HBfix6 / HB-F). It is kept unchanged so that only the learning differs.
- **Training phase:** arm `llmL` only, about 60 minutes. After each episode, a `reflect` call updates `lessons.json`, written to the run's results folder.
- **Evaluation:** the frozen lessons file. Arms `llm,llmL` (plus `rule` as an anchor), interleaved, 2 sessions on new seeds.
- **Target behaviours:** fewer wasted loots (looting while already supplied, loots that take nothing), fewer deaths, higher end health. The card fixes thresholds and the primary metric before launch.
