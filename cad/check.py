"""Interference check for View 2: every pair of components, at home and at the four shift extremes.

Some contacts are designed (a flexure's preload, a press fit, a squeezed TPU part): each such pair has a
volume budget. Any other pair must not touch (0.05 mm3). Exit 1 on a failure.
"""
import sys, time
from build123d import *
from params import *
from assembly import assemble

BUDGET = {  # (prefix a, prefix b): max overlap in mm3, and why
    ("body", "y_plate"): (240, "flexure way: 0.25 mm preload along the tongue; detent bump pressed 0.4"),
    ("y_plate", "lens_panel"): (190, "flexure way: 0.25 mm preload along the tongue; detent bump pressed 0.4"),
    ("body", "rotator"): (6, "three spring bumps pressed 0.4 into the rotator's front face"),
    ("stop_peg", "body"): (8, "peg pressed into its hole"),
    ("knob_", "washer_"): (12, "wave washer's bumps squeezed 0.3 mm"),
    ("collar_rise", "body"): (8, "collar pressed into the side bore"),
    ("plug_worm", "body"): (20, "plug pressed into the worm's bore"),
    ("plug_rack", "body"): (30, "plug pressed into the rack's channel"),
    ("plug_y", "body"): (30, "plugs pressed into the groove ends"),
    ("plug_x", "y_plate"): (30, "plugs pressed into the groove ends"),
    ("rack_shift", "y_plate"): (40, "rack pressed into its slot"),
    ("mount", "helicoid"): (9999, "the mount's printed M65 stub in the helicoid's front thread (envelope)"),
    ("lens_body", "board"): (9999, "Copal 0 envelope through the board: not modelled in detail"),
    ("lens_glass", "lens_body"): (1e9, "the glass sits in the lens"),
    ("rb_", "graflok_"): (9999, "the blade clamps the back: envelope"),
    ("rb_", "rotator"): (9999, "the RB67 envelope has no Graflok lips or slots (proved on the real back)"),
    ("rb_", "rb_"): (9999, "the back's own parts"),
    ("graflok_wheel", "rotator"): (25, "printed M8 threads engaged"),
    ("dot", ""): (1e9, "paint fills of the dots: render only"),
}


def budget(a, b):
    for (p, q), v in BUDGET.items():
        if (a.startswith(p) and b.startswith(q)) or (a.startswith(q) and b.startswith(p)):
            return v
    return (0.05, "")


def overlap(sa, sb):
    ba, bb = sa.bounding_box(), sb.bounding_box()
    if ba.max.X < bb.min.X or bb.max.X < ba.min.X or ba.max.Y < bb.min.Y or bb.max.Y < ba.min.Y or ba.max.Z < bb.min.Z or bb.max.Z < ba.min.Z:
        return 0.0
    try:
        return (sa & sb).volume
    except Exception:
        return -1.0


def run(sx, sy, **kw):
    it = assemble(sx, sy, back=True, **kw)
    bad = []
    for i in range(len(it)):
        for j in range(i + 1, len(it)):
            v = overlap(it[i].shape, it[j].shape)
            lim, why = budget(it[i].name, it[j].name)
            if v > lim or v < 0:
                bad.append((it[i].name, it[j].name, round(v, 2), lim))
    return it, bad


if __name__ == "__main__":
    fails = 0
    it = assemble()
    solo = [(i.name, len(i.shape.solids())) for i in it if i.printed and len(i.shape.solids()) != 1]
    print(f"printed parts that are not one solid: {solo or 'none'}")
    fails += len(solo)
    S = int(SHIFT)
    states = [(0, 0, {}), (S, S, {}), (-S, -S, {}), (S, -S, {}), (-S, S, {}), (S, 0, {}), (0, -S, {}), (0, 0, {"blade_locked": False}),
              (0, 0, {"rho": -90.0}), (-S, S, {"rho": -90.0}), (0, 0, {"rho": -45.0})]
    for sx, sy, kw in states:
        t = time.time()
        _, bad = run(sx, sy, **kw)
        print(f"shift x={sx:+d} y={sy:+d} {kw or ''}: {len(bad)} problems ({time.time() - t:.0f}s)")
        for b in bad:
            print("   ", b)
        fails += len(bad)
    sys.exit(1 if fails else 0)
