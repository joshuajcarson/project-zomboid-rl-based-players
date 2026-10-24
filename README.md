# Project Zomboid RL-based players

Experiments in running Project Zomboid survivors with reinforcement-learning policies instead of humans, starting with one agent and growing to four agents cooperating on one server.

Status: research / scaffolding. See [docs/approach.md](docs/approach.md) for the current plan.

## Ground rules

- Target build: **Build 42.21** (pinned; internals move between builds).
- Never commit The Indie Stone's game files, `projectzomboid.jar`, or decompiled game code. Scripts should read them from the user's own install.
- Third-party mods (e.g. Bandits) are referenced as dependencies, never vendored, unless their authors grant permission.

## License

MIT for code in this repository. See [LICENSE](LICENSE).
