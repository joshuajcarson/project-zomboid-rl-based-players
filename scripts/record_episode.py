"""Record one episode as a top-down animated GIF (agents, zombies, trails, health bars) for sharing.

    python scripts/record_episode.py --task rendezvous --policy models/rendezvous.pt --out docs/media/rendezvous_trained.gif
    python scripts/record_episode.py --task fight --policy scripted --out docs/media/fight_scripted.gif

--policy is a checkpoint written by pzrl.train, or one of: scripted, idle, random.
The picture is drawn from the bridge's observations (positions, health, nearby zombies); it is not a game screenshot.
"""
import argparse
import math
import sys
import time

sys.path.insert(0, ".")
import numpy as np
import torch
from PIL import Image, ImageDraw

from pzrl.env import PZParallelEnv
from pzrl.tasks import TASKS
from pzrl.baselines import BASELINES, idle
from pzrl.train import ActorCritic

COLORS = ["#1f77b4", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf", "#8c564b"]


def frame(env, trails, size=520, pad=40, title=""):
    pts = [(p["x"], p["y"]) for p in env.state.values()]
    for p in env.state.values():
        pts += [tuple(z) for z in p["z"]]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    for t in trails.values():
        xs += [q[0] for q in t]; ys += [q[1] for q in t]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    span = max(30.0, max(xs) - min(xs), max(ys) - min(ys)) * 1.15
    k = (size - 2 * pad) / span
    def to_px(x, y):
        return size / 2 + (x - cx) * k, size / 2 + (y - cy) * k
    img = Image.new("RGB", (size, size + 40), "#f6f4ee"); d = ImageDraw.Draw(img)
    for g in range(-5, 6):                                       # 10-tile grid
        gx, gy = to_px(round(cx / 10) * 10 + g * 10, round(cy / 10) * 10 + g * 10)
        d.line([gx, 0, gx, size], fill="#e5e1d6"); d.line([0, gy, size, gy], fill="#e5e1d6")
    for i, (name, p) in enumerate(sorted(env.state.items())):
        col = COLORS[i % len(COLORS)]
        t = trails.get(name, [])
        if len(t) > 1:
            d.line([to_px(*q) for q in t], fill=col, width=2)
        for z in p["z"]:
            zx, zy = to_px(*z); d.ellipse([zx - 4, zy - 4, zx + 4, zy + 4], fill="#c0392b")
    for i, (name, p) in enumerate(sorted(env.state.items())):
        col = COLORS[i % len(COLORS)]
        px, py = to_px(p["x"], p["y"])
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=col, outline="black")
        d.rectangle([px - 14, py - 20, px + 14, py - 16], outline="black")
        d.rectangle([px - 14, py - 20, px - 14 + 28 * max(0, p["hp"]) / 100, py - 16], fill="#2ecc71" if p["hp"] > 40 else "#e74c3c")
        d.text((px + 11, py - 6), name[-2:], fill="black")
    d.text((10, size + 8), f"{title}   step {env.steps}   agents {len(env.state)}   scale {k:.1f}px/tile", fill="black")
    d.text((10, size + 22), "red = zombies near an agent, bar = health   (drawn from bridge observations, not a game screenshot)", fill="#666666")
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="rendezvous")
    ap.add_argument("--agents", type=int, default=2)
    ap.add_argument("--policy", default="scripted")
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--zombies", type=int, default=None)
    ap.add_argument("--time-scale", type=float, default=4.0)
    ap.add_argument("--box", type=float, nargs=4, default=(10650, 9350, 10800, 9500))
    ap.add_argument("--backend", default="fake")
    ap.add_argument("--out", default="docs/media/episode.gif")
    ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()
    if a.zombies is not None:
        TASKS[a.task].zombies_per_agent = a.zombies
    net = None
    if a.policy.endswith(".pt"):
        net = ActorCritic(25, 10); net.load_state_dict(torch.load(a.policy))
    env = PZParallelEnv(n_agents=a.agents, task=a.task, time_scale=a.time_scale, max_steps=a.steps, backend=a.backend,
                        seed=a.seed if a.seed is not None else int(time.time()) % 1000, spawn_box=tuple(a.box), keep_alive=a.backend == "rendered")
    frames, trails = [], {}
    title = f"{a.task} / {a.policy.split('/')[-1]} / {a.backend}"
    try:
        obs, _ = env.reset()
        for n, p in env.state.items():
            trails[n] = [(p["x"], p["y"])]
        frames.append(frame(env, trails, title=title))
        while env.agents:
            if net is not None:
                acts = {n: net.act(obs[n], greedy=True)[0] for n in env.agents}
            elif a.policy == "idle":
                acts = {n: idle(obs[n]) for n in env.agents}
            elif a.policy == "random":
                acts = {n: env.action_space(n).sample() for n in env.agents}
            else:
                acts = {n: BASELINES[a.task](obs[n]) for n in env.agents}
            obs, rew, term, trunc, _ = env.step(acts)
            for n, p in env.state.items():
                trails.setdefault(n, []).append((p["x"], p["y"]))
            frames.append(frame(env, trails, title=title))
    finally:
        env.close()
    frames[0].save(a.out, save_all=True, append_images=frames[1:] + [frames[-1]] * 6, duration=250, loop=0, optimize=True)
    frames[-1].save(a.out.replace(".gif", "_last.png"))
    print("wrote", a.out, len(frames), "frames")


if __name__ == "__main__":
    main()
