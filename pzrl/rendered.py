"""Control of a rendered (real graphical) client through the server channel.

RenderedControl has the same goto/attack/equip surface the env uses on ClientControl, but the commands travel
server channel -> RLBridge.lua ("bot|user|...") -> sendServerCommand -> RLBot.lua on the rendered client, which walks the
local player with the game's own pathfinding and swings with the game's own attack input. Observations are unchanged
(the server-side bridge sees the rendered player like any other).
"""


class RenderedControl:
    def __init__(self, channel, user, state=None):
        self.ch, self.user = channel, user
        self._state = state          # callable returning the latest published player dict (for info())

    def _bot(self, cmd, a="", b=""):
        parts = ["bot", self.user, cmd] + ([str(a)] if a != "" else []) + ([str(b)] if b != "" else [])
        return self.ch.command("|".join(parts))

    def goto(self, x, y):
        me = self._state() if self._state else None
        if me is not None and (x - me["x"]) ** 2 + (y - me["y"]) ** 2 < 0.25:   # "stay": target is where it stands
            return self.stop()
        return self._bot("goto", f"{x:.2f}", f"{y:.2f}")

    def stop(self):
        return self._bot("stop")

    def attack(self):
        return self._bot("attack")

    def equip(self, item_type="Base.BaseballBat"):
        return self._bot("equip", item_type)

    def info(self):
        return self._bot("info")

    # --- the ClientControl surface PZParallelEnv uses -------------------------------------------------------------
    def tp(self, x, y, z=0):
        return self.ch.command(f"tp|{self.user}|{x:.1f}|{y:.1f}|{z}")

    def weapon(self, item_id):          # the rendered bot equips by item type, see equip()
        return {"ok": True}

    def autoattack(self, on):           # the real game has no auto melee
        return {"ok": True}

    def close(self):
        pass

    def give(self, item_type):
        return self.ch.command(f"give|{self.user}|{item_type}")
