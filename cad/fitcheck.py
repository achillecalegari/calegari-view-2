"""Fit checks for the View 2 mechanisms (test plate parts)."""
import math, sys
from build123d import *
from params import *
from util import *
import mech as M


def ov(a, b):
    try:
        return (a & b).volume
    except Exception:
        return -1.0


fails = 0
def report(name, v, lo, hi):
    global fails
    ok = lo <= v <= hi
    fails += not ok
    print(f"{name:52s} {v:9.3f} mm3  {'ok' if ok else 'FAIL'}  (expected {lo}..{hi})")


ad, bd = M.mount(thread=False), M.board()
report("board locked in the mount", ov(ad, bd), 0, 0.05)
for dz in (0.0, 1.0, 2.0, 3.2):
    b = Pos(0, 0, dz) * Rot(0, 0, LOCK_TURN) * bd
    v = ov(ad, b)
    report(f"board at entry angle, {dz:.1f} mm out (detent bump only)", v, 0, 1.2)
for t in (10.0, 20.0, 30.0):
    b = Rot(0, 0, LOCK_TURN - t) * bd
    report(f"board turning, {LOCK_TURN - t:.0f} deg from lock (detent bump only)", ov(ad, b), 0, 1.2)

# rack and pinion: pinion tooth down at x = 0, rack pitch line at y = 0
pin = extrude(poly_face(gear_profile(MOD, PIN_Z, PIN_X, PRESS)), amount=PIN_W)
rk = M.rack(62)
worst = 1e9
for k in range(12):
    th = k * (360 / PIN_Z) / 12
    p = Pos(0, M.CENTRE_TO_PITCH, 0) * Rot(0, 0, 180 / PIN_Z * 0 + th) * Rot(0, 0, 180 / PIN_Z) * pin
    r = Pos(math.radians(th) * M.PIN_R, 0, 0) * rk
    v = ov(p, r)
    worst = min(worst, -v) if v > 0 else worst
    if v > 0.01:
        report(f"pinion/rack at {th:.1f} deg", v, 0, 0.01)
print("pinion/rack: no interference over one tooth pitch" if worst == 1e9 else "")

# knob on the shaft: bumps in the groove, D flat engaged; 1 mm short of home the bumps ride the shaft
kn = M.knob()
sh_len = 34.0
pn = M.pinion(sh_len)
top = PIN_W + sh_len
home = Pos(0, 0, top - M.KNOB_BORE + 15.0) * Rot(180, 0, 0) * kn      # skirt at top - KNOB_BORE, crown up
report("knob home on the shaft (snap bumps in the groove)", ov(pn, home), 0, 0.05)
report("knob 1.5 mm short of home (bumps on the shaft: they flex)", ov(pn, Pos(0, 0, 1.5) * home), 0.3, 20)

# dovetails: rigid and flexure side
for flex in (False, True):
    g = M.way_coupon_fixed(flex)
    t = M.way_coupon_tongue(flex)
    v = ov(g, t)
    if flex:
        report("tongue in the flexure groove (planned 0.25 mm interference)", v, 20, 60)
    else:
        report("tongue in the rigid groove", v, 0, 0.05)

# the rig: pinion in the block, rack in the carrier riding on the block face on its 0.8 rails
blk = M.pinion_block()
w_pl, w_c = M.drive_layout()
sl = M.block_shaft_len()
pin_r = Pos(0, 0, w_c) * Rot(0, 90, 0) * Pos(0, 0, -PIN_W / 2) * M.pinion(sl)
car = Pos(0, 0, -GAP) * Rot(180, 0, 0) * M.rack_carrier()     # print frame -> rig frame: face at w = -GAP
rk = Location(Plane(origin=(-RACK_W / 2, 0, w_pl), x_dir=(0, 1, 0), z_dir=(1, 0, 0))) * M.rack(62.0)
report("rig: pinion vs block (none)", ov(pin_r, blk), 0, 0.01)
report("rig: carrier rails on the block face (touch, no overlap)", ov(car, blk), 0, 0.05)
report("rig: rack pressed in the carrier", ov(rk, car), 5, 40)
report("rig: rack tips 0.3 off the block face (none)", ov(rk, blk), 0, 0.01)
report("rig: carrier vs pinion (none)", ov(car, pin_r), 0, 0.01)

# wave washer between knob and face
d_in, d_out, t = DRAG_WASHER
washer = Pos(22.0, 0, w_c) * Rot(0, 90, 0) * M.drag_washer()
x_end = PIN_W / 2 + sl
knob_on = Pos(x_end - M.KNOB_BORE, 0, w_c) * Rot(0, -90, 0) * Pos(0, 0, -15.0) * M.knob()
report("wave washer squeeze (mm): free height minus the knob's offset", t - KNOB_OFF, 0.25, 0.35)
report("knob vs washer: only the bumps (mm3)", ov(knob_on, washer), 1, 12)
report("knob vs block (none)", ov(knob_on, blk), 0, 0.01)

# ------------------------------------------------------------------ rise worm and the Y plate's rack
import parts as P
body = P.body_part()
wp = M.worm_part()
rk = M.rise_rack()
worst = 0.0
for sy in (-30.0, -17.3, -5.1, 0.0, 7.7, 21.9, 30.0):
    th = -sy / M.WORM_LEAD * 360.0
    worst = max(worst, ov(M.worm_place(th) * wp, Pos(0, sy, 0) * rk))
report("worm vs rack over the whole travel (none)", worst, 0, 0.05)
report("worm in its trough and bearings (none)", ov(M.worm_place(0) * wp, body), 0, 0.05)
report("worm lifted by its pin to go in: clear of the body (none)", ov(Pos(0, M.WORM_PIN[1] + 0.6, 0) * M.worm_place(0) * wp, body), 0, 0.05)
lam = math.degrees(math.atan(M.WORM_LEAD / (math.pi * WORM_D)))
report("worm lead angle (deg): self-locking below the friction angle (about 17 dry)", lam, 0, 9)

# ------------------------------------------------------------------ rotating back
rot0 = P.rotator(0.0)
report("rotator at landscape vs body: spring bumps, 0.15 mm residual preload", ov(rot0, body), 0.1, 6)
report("rotator at portrait vs body: spring bumps, 0.15 mm residual preload", ov(P.rotator(-90.0), body), 0.1, 6)
for dz in (-1.0, -2.5, -4.0, -8.0):
    report(f"rotator turned {ROT_ENTRY:.0f} deg, {-dz:.1f} mm out: passes the lugs (bumps only)", ov(Pos(0, 0, dz) * P.rotator(ROT_ENTRY), body), 0, 6)
for rho in (0.0, -45.0, -90.0):
    report(f"rotator at {rho:.0f} deg pulled 1.5 mm back: held by the lugs", ov(Pos(0, 0, -1.5) * P.rotator(rho), body), 20, 1e6)
peg = P.stop_peg()
report("stop peg vs rotator at 0 and -90 (touch, no overlap)", max(ov(peg, P.rotator(0.0)), ov(peg, P.rotator(-90.0))), 0, 0.05)
report("stop peg vs rotator turned 3 deg past either end: it stops", min(ov(peg, P.rotator(3.0)), ov(peg, P.rotator(-93.0))), 0.5, 1e6)
sys.exit(1 if fails else 0)
