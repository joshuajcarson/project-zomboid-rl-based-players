import sys
sys.path.insert(0, ".")
from types import SimpleNamespace
from pzrl import invariants as inv


class Chan:
    def __init__(self, bats): self.bats = bats
    def command(self, line, timeout=10): return {"ok": True, "msg": "items=3 weight=1.0 bats=%d" % self.bats}


class Ctl:
    def __init__(self, chan): self.sent = []; self.chan = chan
    def _bot(self, cmd, arg=None):
        self.sent.append(cmd)
        if cmd == "tidy" and self.chan.bats > 1: self.chan.bats = 1
        if cmd == "giveitem" and self.chan.bats == 0: self.chan.bats = 1


def fake_env(bats, hp=100, x=10770, y=9410, dead=False):
    ch = Chan(bats)
    return SimpleNamespace(give_weapon="Base.BaseballBat", rendered={"Client40"}, channel=ch, possible_agents=["Client40"],
                           control={"Client40": Ctl(ch)}, spawn_box=(10730, 9380, 10810, 9440),
                           state={"Client40": {"x": x, "y": y, "hp": hp, "dead": dead}})


def test_parse():
    assert inv.parse_inv("items=12 weight=9.5 bats=1") == {"items": 12, "weight": 9.5, "bats": 1}


def test_bat_pile_is_repaired():
    e = fake_env(48)
    assert inv.check_one_bat(e, "Client40")[0] == "repaired" and e.channel.bats == 1


def test_missing_bat_is_given():
    e = fake_env(0)
    assert inv.check_one_bat(e, "Client40")[0] == "repaired" and e.channel.bats == 1


def test_good_state_is_ok():
    e = fake_env(1)
    assert [c(e, "Client40")[0] for c in inv.CHECKS] == ["ok", "ok", "ok"]


def test_dead_and_outside_fail():
    assert inv.check_alive(fake_env(1, dead=True), "Client40")[0] == "failed"
    assert inv.check_in_arena(fake_env(1, x=11500), "Client40")[0] == "failed"


if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"): v(); print("ok", k)
