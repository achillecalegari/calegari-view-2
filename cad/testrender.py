"""Scene of the test rigs, assembled, for the docs: python testrender.py -> out/mesh_test/manifest.json"""
import json, pathlib
from build123d import *
from params import *
from util import *
import mech as M

OUT = pathlib.Path(__file__).resolve().parent.parent / "out" / "mesh_test"
OUT.mkdir(parents=True, exist_ok=True)
items = []
# 1. mount with the board locked, and the thread ring beside it
ad = M.mount(); bd = M.board()
z_b = -M.Z_H + M.STUB_L
items += [("mount", Pos(-120, 60, z_b) * ad, "body_black"), ("board", Pos(-120, 60, z_b) * bd, "red")]
items += [("thread_ring", Pos(-120, -55, 0) * M.thread_coupon(), "body_black")]
# 2. pinion rig: block face up, pinion, shaft, washer, knob; the carrier with its rack lies on the face
w_pl, w_c = M.drive_layout()
blk = M.pinion_block()
flip = lambda s: Pos(0, 0, 20.0) * Rot(180, 0, 0) * s          # face up
sl = M.block_shaft_len()
pin = Pos(0, 0, w_c) * Rot(0, 90, 0) * Pos(0, 0, -PIN_W / 2) * M.pinion(sl)
x_end = PIN_W / 2 + sl
washer = Pos(22.0, 0, w_c) * Rot(0, 90, 0) * M.drag_washer()
kn = Pos(x_end - M.KNOB_BORE, 0, w_c) * Rot(0, -90, 0) * Pos(0, 0, -15.0) * M.knob()
rk = Location(Plane(origin=(-RACK_W / 2, 0, w_pl), x_dir=(0, 1, 0), z_dir=(1, 0, 0))) * M.rack(62.0)
car = Pos(0, 0, -GAP) * Rot(180, 0, 0) * M.rack_carrier()
for n, s, m in (("block", blk, "body_black"), ("pinion", pin, "grey"), ("washer", washer, "rubber"), ("knob", kn, "body_black"),
                ("rack", rk, "grey"), ("carrier", car, "red")):
    items.append((n, Pos(0, 40, 0) * flip(s), m))
# 2b. worm rig: the top of the body's right side (front face up), the short worm, the miter pair, the collar,
# the knob, the plug, and the rack slice riding on the face
T = Pos(185, 20, 0)
G = M.knob_gear_place(0)
side = (WORM_X - M.BEVEL_R) + H
kn = G * Pos(0, 0, side + KNOB_OFF + KNOB_H) * Rot(180, 0, 0) * M.knob()
for n, s, m in (("worm_block", M.worm_block(), "body_black"), ("worm", M.test_worm_place(0) * M.test_worm(), "grey"),
                ("worm_gear", G * M.knob_gear(), "grey"), ("worm_collar", Pos(-H, M.BEVEL_Y, WORM_Z) * orient(M.collar(), "+x"), "body_black"),
                ("worm_knob", kn, "body_black"), ("worm_plug", M.rig_plug(), "body_black"),
                ("rack_slice", Pos(0, -M.WORM_LEAD, 0) * M.rack_slice(), "red")):
    items.append((n, T * s, m))
# 3. dovetail pairs (tongue in groove), face up
for i, flex in enumerate((False, True)):
    g = M.way_coupon_fixed(flex); t = M.way_coupon_tongue(flex)
    items += [(f"groove_{i}", Pos(0 + 35 * i - 30, -50, 12) * Rot(180, 0, 0) * g, "body_black"),
              (f"tongue_{i}", Pos(0 + 35 * i - 30, -50, 12) * Rot(180, 0, 0) * t, "grey")]
# 5. Arca coupon
items += [("arca", Pos(110, -45, 0) * M.arca_coupon(), "body_black")]
man = []
for n, s, m in items:
    f = OUT / f"{n}.stl"
    export_stl(s, str(f), tolerance=0.03, angular_tolerance=0.12)
    man.append({"name": n, "file": str(f), "mat": m})
(OUT / "manifest.json").write_text(json.dumps(man, indent=1))
print(len(man))
