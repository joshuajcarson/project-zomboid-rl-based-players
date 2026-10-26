"""Small PPO with one policy shared by all agents (parameter sharing), for PZParallelEnv.

    python -m pzrl.train --task rendezvous --agents 2 --iters 60 --out models/rendezvous

Each iteration collects `episodes` episodes from the running env, then does a few PPO epochs. Progress goes to
<out>.jsonl (one JSON line per iteration), a checkpoint to <out>.pt and a learning-curve picture to <out>.png.
Needs only torch and numpy (PIL for the picture); no gymnasium or stable-baselines.
"""
import argparse
import json
import pathlib
import time

import numpy as np
import torch
import torch.nn as nn

from .env import PZParallelEnv
from .tasks import TASKS
from .baselines import BASELINES


class ActorCritic(nn.Module):
    def __init__(self, obs_dim, n_actions, hidden=64):
        super().__init__()
        self.trunk = nn.Sequential(nn.Linear(obs_dim, hidden), nn.Tanh(), nn.Linear(hidden, hidden), nn.Tanh())
        self.pi = nn.Linear(hidden, n_actions)
        self.v = nn.Linear(hidden, 1)

    def forward(self, x):
        h = self.trunk(x)
        return self.pi(h), self.v(h).squeeze(-1)

    def act(self, obs, greedy=False):
        with torch.no_grad():
            logits, v = self(torch.as_tensor(obs, dtype=torch.float32).unsqueeze(0))
            dist = torch.distributions.Categorical(logits=logits)
            a = logits.argmax(-1) if greedy else dist.sample()
            return int(a), float(dist.log_prob(a)), float(v)


def run_episode(env, net, greedy=False):
    """One episode of all agents. Returns per-agent trajectories and a summary dict."""
    obs, _ = env.reset()
    traj = {a: {"obs": [], "act": [], "logp": [], "val": [], "rew": [], "done": [], "last_v": 0.0} for a in env.agents}
    kills0 = {a: env.state[a]["kills"] for a in env.agents}
    hp0 = {a: env.state[a]["hp"] for a in env.agents}
    dmin = []
    while env.agents:
        acts, rec = {}, {}
        for a in env.agents:
            act, lp, v = net.act(obs[a], greedy)
            acts[a], rec[a] = act, (obs[a], act, lp, v)
        obs, rew, term, trunc, _ = env.step(acts)
        for a, (o, act, lp, v) in rec.items():
            t = traj[a]
            t["obs"].append(o); t["act"].append(act); t["logp"].append(lp); t["val"].append(v)
            t["rew"].append(rew[a]); t["done"].append(bool(term[a]))
            if trunc[a] and a in obs:      # time limit: bootstrap from the value of the last observation
                t["last_v"] = net.act(obs[a], True)[2]
        if env.task.name == "rendezvous" and len(env.state) > 1:
            ps = list(env.state.values())
            dmin.append(min(np.hypot(p["x"] - q["x"], p["y"] - q["y"]) for p in ps for q in ps if p is not q))
    summ = {"return": float(np.mean([sum(t["rew"]) for t in traj.values()])),
            "steps": env.steps,
            "kills": float(sum(env.state[a]["kills"] - kills0[a] for a in kills0)),
            "damage": float(np.mean([hp0[a] - env.state[a]["hp"] for a in hp0])),
            "deaths": float(sum(1 for a in hp0 if env.state[a]["hp"] <= 10)),
            "final_pair_distance": float(dmin[-1]) if dmin else None}
    return traj, summ


def gae(t, gamma, lam):
    n = len(t["rew"])
    adv = np.zeros(n, np.float32)
    last, nxt_v = 0.0, t["last_v"]
    for i in reversed(range(n)):
        nonterm = 0.0 if t["done"][i] else 1.0
        delta = t["rew"][i] + gamma * nxt_v * nonterm - t["val"][i]
        last = delta + gamma * lam * nonterm * last
        adv[i] = last
        nxt_v = t["val"][i]
    return adv, adv + np.array(t["val"], np.float32)


def ppo_update(net, opt, batch, epochs=4, mb=64, clip=0.2, ent=0.01, vf=0.5):
    obs = torch.as_tensor(np.array(batch["obs"]), dtype=torch.float32)
    act = torch.as_tensor(batch["act"]); old = torch.as_tensor(batch["logp"], dtype=torch.float32)
    adv = torch.as_tensor(batch["adv"]); ret = torch.as_tensor(batch["ret"])
    adv = (adv - adv.mean()) / (adv.std() + 1e-8)
    n = len(act)
    for _ in range(epochs):
        idx = torch.randperm(n)
        for s in range(0, n, mb):
            i = idx[s:s + mb]
            logits, v = net(obs[i])
            d = torch.distributions.Categorical(logits=logits)
            ratio = torch.exp(d.log_prob(act[i]) - old[i])
            loss = -torch.min(ratio * adv[i], torch.clamp(ratio, 1 - clip, 1 + clip) * adv[i]).mean() \
                   + vf * (v - ret[i]).pow(2).mean() - ent * d.entropy().mean()
            opt.zero_grad(); loss.backward(); nn.utils.clip_grad_norm_(net.parameters(), 0.5); opt.step()


def plot_curve(rows, path, title):
    """Tiny line chart with PIL (no matplotlib): mean return per iteration plus a moving average."""
    from PIL import Image, ImageDraw
    W, H, m = 900, 420, 55
    img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
    ys = [r["return"] for r in rows]
    if len(ys) < 2:
        return
    lo, hi = min(ys), max(ys)
    if hi - lo < 1e-6:
        hi = lo + 1
    def xy(i, y):
        return m + (W - 2 * m) * i / (len(ys) - 1), H - m - (H - 2 * m) * (y - lo) / (hi - lo)
    d.rectangle([m, m, W - m, H - m], outline="#999999")
    for g in range(5):
        y = lo + (hi - lo) * g / 4
        d.line([m, xy(0, y)[1], W - m, xy(0, y)[1]], fill="#eeeeee"); d.text((5, xy(0, y)[1] - 6), f"{y:.2f}", fill="#555555")
    d.line([xy(i, y) for i, y in enumerate(ys)], fill="#9ec5e8", width=2)
    k = 5
    ma = [sum(ys[max(0, i - k + 1):i + 1]) / len(ys[max(0, i - k + 1):i + 1]) for i in range(len(ys))]
    d.line([xy(i, y) for i, y in enumerate(ma)], fill="#1f5fa8", width=3)
    d.text((m, 15), f"{title}: mean episode return per iteration (light) and 5-iteration average (dark)", fill="black")
    d.text((m, H - 30), f"iteration 1..{len(ys)}", fill="#555555")
    img.save(path)


def evaluate(env, net, episodes, greedy=True, baseline=None):
    out = []
    for _ in range(episodes):
        if baseline:
            obs, _ = env.reset()
            tot = {a: 0.0 for a in env.agents}
            while env.agents:
                obs, rew, *_ = env.step({a: BASELINES[env.task.name](obs[a]) for a in env.agents})
                for a in rew: tot[a] += rew[a]
            out.append({"return": float(np.mean(list(tot.values())))})
        else:
            out.append(run_episode(env, net, greedy)[1])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="rendezvous", choices=list(TASKS))
    ap.add_argument("--agents", type=int, default=2)
    ap.add_argument("--iters", type=int, default=60)
    ap.add_argument("--episodes", type=int, default=3)
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--time-scale", type=float, default=4.0)
    ap.add_argument("--zombies", type=int, default=None)
    ap.add_argument("--ring", type=float, nargs=2, default=(12, 22))
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--gamma", type=float, default=0.97)
    ap.add_argument("--out", default=None)
    ap.add_argument("--resume", default=None)
    ap.add_argument("--eval-episodes", type=int, default=4)
    a = ap.parse_args()
    out = pathlib.Path(a.out or f"models/{a.task}"); out.parent.mkdir(parents=True, exist_ok=True)
    if a.zombies is not None:
        TASKS[a.task].zombies_per_agent = a.zombies
    env = PZParallelEnv(n_agents=a.agents, task=a.task, time_scale=a.time_scale, max_steps=a.steps, seed=int(time.time()) % 10000,
                        zombie_ring=tuple(a.ring), spawn_box=(10650, 9350, 10900, 9700))
    obs_dim = env.observation_space(env.possible_agents[0]).shape[0]
    n_act = env.action_space(env.possible_agents[0]).n
    net = ActorCritic(obs_dim, n_act)
    if a.resume:
        net.load_state_dict(torch.load(a.resume))
    opt = torch.optim.Adam(net.parameters(), lr=a.lr)
    rows = []
    log = open(str(out) + ".jsonl", "a")
    try:
        for it in range(1, a.iters + 1):
            t0 = time.time(); batch = {k: [] for k in ("obs", "act", "logp", "adv", "ret")}; sums = []
            for _ in range(a.episodes):
                traj, summ = run_episode(env, net)
                sums.append(summ)
                for t in traj.values():
                    if not t["rew"]:
                        continue
                    adv, ret = gae(t, a.gamma, 0.95)
                    batch["obs"] += t["obs"]; batch["act"] += t["act"]; batch["logp"] += t["logp"]
                    batch["adv"] += list(adv); batch["ret"] += list(ret)
            ppo_update(net, opt, batch)
            row = {"iter": it, "samples": len(batch["act"]), "secs": round(time.time() - t0, 1)}
            for k in ("return", "kills", "damage", "deaths", "steps"):
                row[k] = round(float(np.mean([s[k] for s in sums])), 3)
            fd = [s["final_pair_distance"] for s in sums if s["final_pair_distance"] is not None]
            if fd:
                row["final_pair_distance"] = round(float(np.mean(fd)), 1)
            rows.append(row); log.write(json.dumps(row) + "\n"); log.flush()
            print(json.dumps(row), flush=True)
            torch.save(net.state_dict(), str(out) + ".pt")
            if it % 5 == 0 or it == a.iters:
                plot_curve(rows, str(out) + ".png", f"{a.task} PPO")
        res = {"policy_greedy": evaluate(env, net, a.eval_episodes), "scripted": evaluate(env, net, a.eval_episodes, baseline=True)}
        summary = {k: {m: round(float(np.mean([e[m] for e in v if e.get(m) is not None])), 3) for m in v[0] if v[0][m] is not None}
                   for k, v in res.items()}
        print("EVAL", json.dumps(summary), flush=True)
        json.dump(summary, open(str(out) + "_eval.json", "w"), indent=1)
    finally:
        env.close()


if __name__ == "__main__":
    main()
