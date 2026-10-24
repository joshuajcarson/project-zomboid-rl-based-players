"""Record which Project Zomboid build is installed and detect changes to the classes this project hooks.

Stores only facts about the game (version string, hashes, class names), never game code.

Usage:
    python scripts/track_game_version.py            # snapshot the current install, diff against the latest one
    python scripts/track_game_version.py --game-dir "D:/Games/ProjectZomboid"

Exit code 0 = no changes to watched classes, 1 = watched classes changed (review before running experiments),
2 = error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

DEFAULT_GAME_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid"
DEFAULT_USER_DIR = Path.home() / "Zomboid"

# Classes (and their inner classes) this project depends on. Add to this list as new hooks are written.
WATCHED_PREFIXES = [
    "zombie/network/FakeClientManager",
    "zombie/network/GameServer",
    "zombie/network/PacketTypes",
    "zombie/characters/IsoPlayer",
    "zombie/characters/IsoZombie",
    "zombie/ai/AIBrainPlayerControlVars",
]

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = REPO_ROOT / "versions"


def read_version(user_dir: Path) -> str:
    version_file = user_dir / "version.txt"
    if version_file.exists():
        first = version_file.read_text(encoding="utf-8", errors="replace").splitlines()[0].strip()
        return first.split()[0]
    return "unknown"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(game_dir: Path, user_dir: Path) -> dict:
    jar = game_dir / "projectzomboid.jar"
    if not jar.exists():
        raise FileNotFoundError(f"{jar} not found; pass --game-dir")
    watched: dict[str, str] = {}
    class_count = 0
    with zipfile.ZipFile(jar) as zf:
        for info in zf.infolist():
            if not info.filename.endswith(".class"):
                continue
            class_count += 1
            if any(info.filename.startswith(p) for p in WATCHED_PREFIXES):
                watched[info.filename] = hashlib.sha256(zf.read(info)).hexdigest()
    return {
        "version": read_version(user_dir),
        "jar_sha256": sha256_file(jar),
        "class_count": class_count,
        "watched_classes": dict(sorted(watched.items())),
    }


def latest_snapshot() -> dict | None:
    files = sorted(SNAPSHOT_DIR.glob("*.json"), key=os.path.getmtime)
    return json.loads(files[-1].read_text()) if files else None


def diff(old: dict, new: dict) -> list[str]:
    lines = []
    o, n = old["watched_classes"], new["watched_classes"]
    for name in sorted(set(o) | set(n)):
        if name not in n:
            lines.append(f"removed  {name}")
        elif name not in o:
            lines.append(f"added    {name}")
        elif o[name] != n[name]:
            lines.append(f"changed  {name}")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--game-dir", default=os.environ.get("PZ_GAME_DIR", DEFAULT_GAME_DIR))
    ap.add_argument("--user-dir", default=str(DEFAULT_USER_DIR))
    args = ap.parse_args()

    try:
        new = snapshot(Path(args.game_dir), Path(args.user_dir))
    except Exception as e:  # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        return 2

    old = latest_snapshot()
    SNAPSHOT_DIR.mkdir(exist_ok=True)

    if old and old["jar_sha256"] == new["jar_sha256"]:
        print(f"No change: build {new['version']} (jar {new['jar_sha256'][:12]})")
        return 0

    out = SNAPSHOT_DIR / f"{new['version']}_{new['jar_sha256'][:12]}.json"
    out.write_text(json.dumps(new, indent=2) + "\n")
    print(f"Recorded build {new['version']} -> {out.relative_to(REPO_ROOT)}")

    if old is None:
        return 0
    changes = diff(old, new)
    print(f"Previous build: {old['version']}")
    if not changes:
        print("Watched classes unchanged.")
        return 0
    print("Watched classes changed:")
    for line in changes:
        print("  " + line)
    return 1


if __name__ == "__main__":
    sys.exit(main())
