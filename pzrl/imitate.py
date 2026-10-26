"""Behaviour cloning of a scripted baseline into the PPO network, as a warm start for training.

    python -m pzrl.imitate --task fight --agents 4 --episodes 16 --out models/fight_bc

Runs the env, labels every observation with what the scripted policy would do, executes the scripted action (with some random
actions mixed in for coverage), then fits the policy head by cross-entropy. PPO from scratch needs far more samples than we can
afford at one simulated second per step; starting from a policy that is already as good as the baseline lets PPO only improve on it.
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
from .train import ActorCritic


def collect(env, baseline, episodes, eps, rng):
    X, Y, stats = [], [], []
    for _ in range(episodes):
        obs, _ = env.reset()
        names = list(env.agents)
        kills0 = {a: env.state[a]["kills"] for a in names}
        hp0 = {a: env.state[a]["hp"] for a in names}
        while env.agents:
            acts = {}
            for a in env.agents:
                label = baseline(obs[a])
                X.append(obs[a].copy()); Y.append(label)
                acts[a] = int(rng.integers(0, 10)) if rng.random() < eps else label
            obs, rew, term, trunc, _ = env.step(acts)
        stats.append({"kills": sum(env.state[a]["kills"] - kills0[a] for a in names), "steps": env.steps,
                      "damage": float(np.mean([hp0[a] - env.state[a]["hp"] for a in names]))})
    return np.array(X, np.float32), np.array(Y, np.int64), stats


def fit(net, X, Y, epochs=40, lr=2e-3, batch=128):
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    Xt, Yt = torch.as_tensor(X), torch.as_tensor(Y)
    n = len(Yt)
    # the baseline mostly walks; weight rare actions (attack) up a little so they are not ignored
    counts = torch.bincount(Yt, minlength=10).float().clamp(min=1)
    weight = (counts.sum() / counts / 10).clamp(max=5.0)
    lossf = nn.CrossEntropyLoss(weight=weight)
    for e in range(epochs):
        idx = torch.randperm(n)
        tot = 0.0
        for s in range(0, n, batch):
            i = idx[s:s + batch]
            logits, _ = net(Xt[i])
            loss = lossf(logits, Yt[i])
            opt.zero_grad(); loss.backward(); opt.step(); tot += float(loss) * len(i)
        if e % 10 == 9 or e == epochs - 1:
            with torch.no_grad():
                acc = float((net(Xt)[0].argmax(-1) == Yt).float().mean())
            print(f"epoch {e + 1}: loss {tot / n:.3f} accuracy {acc:.3f}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="fight", choices=list(TASKS))
    ap.add_argument("--agents", type=int, default=4)
    ap.add_argument("--episodes", type=int, default=16)
    ap.add_argument("--steps", type=int, default=60)
    ap.add_argument("--time-scale", type=float, default=4.0)
    ap.add_argument("--zombies", type=int, default=2)
    ap.add_argument("--ring", type=float, nargs=2, default=(5, 9))
    ap.add_argument("--box", type=float, nargs=4, default=(10650, 9350, 10900, 9700))
    ap.add_argument("--eps", type=float, default=0.15, help="fraction of random actions executed (labels stay the baseline's)")
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--extra", nargs="*", default=[], help="extra labelled datasets (.npz with X, Y), e.g. observations from the real client")
    ap.add_argument("--extra-weight", type=int, default=3, help="repeat the extra data this many times (it is the data the policy will meet)")
    ap.add_argument("--skip-collect", default=None, help="reuse this saved fake-backend dataset instead of running the env")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = pathlib.Path(a.out or f"models/{a.task}_bc"); out.parent.mkdir(parents=True, exist_ok=True)
    TASKS[a.task].zombies_per_agent = a.zombies
    env = PZParallelEnv(n_agents=a.agents, task=a.task, time_scale=a.time_scale, max_steps=a.steps, seed=int(time.time()) % 10000,
                        zombie_ring=tuple(a.ring), spawn_box=tuple(a.box))
    rng = np.random.default_rng(0)
    if a.skip_collect:
        d = np.load(a.skip_collect); X, Y, stats = d["X"], d["Y"], []
        env.close()
    else:
        try:
            X, Y, stats = collect(env, BASELINES[a.task], a.episodes, a.eps, rng)
        finally:
            env.close()
    for path in a.extra:
        d = np.load(path)
        X = np.concatenate([X] + [d["X"]] * a.extra_weight); Y = np.concatenate([Y] + [d["Y"]] * a.extra_weight)
        print("added", len(d["Y"]), "x", a.extra_weight, "samples from", path, flush=True)
    print("collected", len(Y), "samples; action histogram", np.bincount(Y, minlength=10).tolist(), flush=True)
    print("data-collection episodes (baseline with %.0f%% random actions):" % (100 * a.eps), json.dumps(stats[:3]), "...", flush=True)
    np.savez_compressed(str(out) + "_data.npz", X=X, Y=Y)
    net = ActorCritic(X.shape[1], 10)
    fit(net, X, Y, a.epochs)
    torch.save(net.state_dict(), str(out) + ".pt")
    print("saved", str(out) + ".pt", flush=True)


if __name__ == "__main__":
    main()
