"""Figures for docs/assembly.md (as View 1).

python figures.py [name ...]   writes out/figs/<name>/manifest.json and points.json
render/figures.sh renders them (render/white.py with PTS) and annotates them (render/annotate.py).

A figure shows what is already built in place and only the parts of that step pulled out along the way
they go in, with a dashed guide from each part to where it goes. Letters match the tables in the guide.
"""
import json, pathlib, sys
from build123d import *
from params import *
import parts as P
import mech as M
from assembly import assemble

OUT = pathlib.Path(__file__).resolve().parent.parent / "out" / "figs"

G = {
    "body": ["body"], "rot": ["rotator"], "peg": ["stop_peg"], "blade": ["graflok_blade"], "wheel": ["graflok_wheel"],
    "worm": ["worm"], "gear_r": ["gear_rise"], "collar_r": ["collar_rise"], "washer_r": ["washer_rise"],
    "knob_r": ["knob_rise", "dot_knob_rise"], "plug_w": ["plug_worm"], "plug_rk": ["plug_rack"],
    "v1": ["velvet_body"], "y": ["y_plate"], "rack_s": ["rack_shift"], "v2": ["velvet_yplate"],
    "plug_y": ["plug_y"], "panel": ["lens_panel"], "pin_s": ["pinion_shift"], "plug_x": ["plug_x"],
    "washer_s": ["washer_shift"], "knob_s": ["knob_shift", "dot_knob_shift"], "heli": ["helicoid"], "mount": ["mount"],
    "board": ["board"], "lens": ["lens_body", "lens_glass"], "back": ["rb_"],
}


def g(*keys):
    return [p for k in keys for p in G[k]]


C1 = g("body", "gear_r", "collar_r", "washer_r", "knob_r")
C2 = C1 + g("rot", "peg", "blade", "wheel")
C3 = C2 + g("v1")
YP = g("y", "rack_s", "v2")
C5 = C3 + YP + g("worm", "plug_w", "plug_y", "plug_rk")
C7 = C5 + g("panel", "pin_s", "plug_x", "washer_s", "knob_s")
C8 = C7 + g("heli", "mount")

# Blender view directions: +x photographer's left, +y behind the camera, +z up
V_REAR = (0.35, 1.0, 0.3)
V_OB_R = (0.95, 1.0, 0.45)
V_OB_F = (-0.95, -1.0, 0.45)
V_34 = (-0.62, -1.0, 0.3)
V_RIGHT = (-1.0, -0.55, 0.35)          # the photographer's right side, from the front
V_TOPL = (-0.55, -0.8, 1.0)            # above the handle's left end
V_LEFT_R = (1.0, 0.55, 0.3)            # the photographer's left side, from behind
V_BELOW = (-0.55, -1.0, -0.7)

FIGS = []


def fig(name, title, view, show, new=(), labels=(), lines=(), state=None, doc="asm", **look):
    FIGS.append(dict(name=name, title=title, view=view, show=list(show), new=list(new), labels=list(labels),
                     lines=list(lines), state=state or {}, doc=doc, look=look))


import mech as M
WX, WZ = WORM_X, WORM_Z

# ------------------------------------------------------------------ 1 body and rise worm
fig("1a_body", "1a  The body: what to check", V_OB_R, g("body"),
    labels=[("A", [P.mpolar(ROT_SPRING_R, a) + (P.ROT_FLOOR,) for a in ROT_SPRINGS]),
            ("B", [P.mpolar(ROT_R, a) + (1.0,) for a in LUG_ANG]),
            ("C", [(H, 0.0, P.STOP_PEG["z"])]),
            ("D", [P.mpolar(P.LAB_R[1], 200.0) + (P.ROT_FLOOR - 0.4,)])], dist=4.4)
fig("1b_rise_gear", "1b  The knob's gear and the collar, into the right side", V_RIGHT, g("body"),
    new=[(g("gear_r"), (-45, 0, 0)), (g("collar_r"), (-22, 0, 0))],
    labels=[("A", "gear_rise"), ("B", "collar_rise")], dist=4.4)
fig("1c_rise_knob", "1c  Washer and rise knob", V_RIGHT, g("body", "gear_r", "collar_r"),
    new=[(g("washer_r"), (-14, 0, 0)), (g("knob_r"), (-32, 0, 0), ["knob_rise"])],
    labels=[("C", "washer_rise"), ("D", "knob_rise")], dist=4.4)

# ------------------------------------------------------------------ 2 rotating back
fig("2a_rotator_in", "2a  The rotator goes in turned 135 degrees", V_OB_R, C1, state=dict(rho=ROT_ENTRY),
    new=[(g("rot"), (0, 0, -45))],
    labels=[("A", "rotator"), ("B", [P.mpolar(ROT_R, a) + (1.0,) for a in LUG_ANG])], dist=4.6)
fig("2b_turn_peg", "2b  Turn it to landscape, then the stop peg", V_LEFT_R, C1 + g("rot"),
    new=[(g("peg"), (35, 0, 0))],
    labels=[("C", "stop_peg")], dist=4.4)
fig("2c_blade_wheel", "2c  Blade and wheel", V_OB_R, C1 + g("rot", "peg"),
    new=[(g("blade"), (0, 0, -35)), (g("wheel"), (0, 0, -60))],
    labels=[("D", "graflok_blade"), ("E", "graflok_wheel")], dist=4.6)

# ------------------------------------------------------------------ 3 velvet V1
fig("3_velvet_v1", "3  Velvet V1 on the body", V_OB_F, C2,
    new=[(g("v1"), (0, 0, 35))], labels=[("V1", "velvet_body"), ("F", [(P.RISE_DETENT[0], P.RISE_DETENT[1], BODY_Z1)])], dist=4.8)

# ------------------------------------------------------------------ 4 Y plate on the bench
fig("4a_yplate_back", "4a  The Y plate from behind: what to check", V_REAR, g("y"),
    labels=[("A", [((M.RACK_X[0] + M.RACK_X[1]) / 2, sum(WRACK) / 2, M.RACK_ZS[0])]),
            ("B", [(P.RISE_DETENT[0], P.RISE_DETENT[1], YP_Z0)])], dist=4.0)
fig("4b_shift_rack", "4b  Shift rack into the front", V_OB_F, g("y"),
    new=[(g("rack_s"), (0, 0, 30))], labels=[("C", "rack_shift")], dist=4.0)
fig("4c_velvet_v2", "4c  Velvet V2", V_OB_F, g("y", "rack_s"),
    new=[(g("v2"), (0, 0, 35))], labels=[("V2", "velvet_yplate")], dist=4.0)

# ------------------------------------------------------------------ 5 Y plate into the body
fig("5a_worm", "5a  The rise worm and its plug, up from below", V_BELOW, C3,
    new=[(g("worm"), (0, -125, 0)), (g("plug_w"), (0, -200, 0))],
    labels=[("A", "worm"), ("B", "plug_worm"), ("C", [(WX, M.BEVEL_Y, WZ)])], dist=6.0)
fig("5b_y_in", "5b  The Y plate, up from below", V_34, C3 + g("worm", "plug_w"),
    new=[(YP, (0, -150, 0), ["y_plate"])], labels=[("D", "y_plate"), ("E", "knob_rise")],
    lines=[dict(points=[(-H - 25, -215, 40), (-H - 25, -120, 40)], style="arrow")], dist=5.6)
fig("5c_plugs", "5c  Three plugs in the bottom face", V_BELOW, C3 + YP + g("worm", "plug_w"), state=dict(sy=30.0),
    new=[(g("plug_y"), (0, -35, 0)), (g("plug_rk"), (0, -35, 0))], labels=[("F", "plug_y"), ("G", "plug_rack")], dist=4.6)

# ------------------------------------------------------------------ 6 lens panel on the bench
fig("6_shift_pinion", "6  Shift pinion into the lens panel", V_REAR, g("panel"),
    new=[(g("pin_s"), (0, 0, -35))], labels=[("A", "pinion_shift"), ("B", [(P.SHIFT_DETENT[0], P.SHIFT_DETENT[1], XP_Z0)])], dist=4.0)

# ------------------------------------------------------------------ 7 lens panel onto the Y plate
fig("7a_panel_in", "7a  In from the photographer's right", V_34, C5,
    new=[(g("panel", "pin_s"), (-200, 0, 0), ["lens_panel"])], labels=[("A", "lens_panel")],
    lines=[dict(points=[(-H - 250, -H - 15, 45), (-H - 150, -H - 15, 45)], style="arrow")], dist=5.4)
fig("7b_plugs_x", "7b  Two plugs on the right", V_RIGHT, C5 + g("panel", "pin_s"), state=dict(sx=30.0),
    new=[(g("plug_x"), (-30, 0, 0))], labels=[("B", "plug_x")], dist=4.6)
fig("7c_shift_knob", "7c  Washer and shift knob", V_34, C5 + g("panel", "pin_s", "plug_x"),
    new=[(g("washer_s"), (0, 22, 0)), (g("knob_s"), (0, 45, 0), ["knob_shift"])],
    labels=[("C", "washer_shift"), ("D", "knob_shift")], dist=4.8)

# ------------------------------------------------------------------ 8, 9 the barrel and the lens
fig("8a_helicoid", "8a  The helicoid into the panel", V_OB_F, C7,
    new=[(g("heli"), (0, 0, 50))], labels=[("A", "helicoid")], dist=5.0)
fig("8b_mount", "8b  The lens mount into the helicoid", V_OB_F, C7 + g("heli"),
    new=[(g("mount"), (0, 0, 50))], labels=[("B", "mount")], dist=5.0)
fig("9a_lens_board", "9a  The lens on its board", (-1.0, -0.8, 0.35), [], state=dict(back=False),
    new=[(g("board"), (0, 0, 0)), (g("lens"), (0, 0, 45), ["lens_glass"])],
    labels=[("A", "board"), ("B", [(0.0, 31.5, BOARD_Z1 + 45 + 9)]), ("C", [(0.0, BOARD_R - 2.6, BOARD_Z1)])], dist=3.4)
fig("9b_board_in", "9b  The board into the mount", (-1.0, -0.8, 0.35), C8, state=dict(back=False),
    new=[(g("board", "lens"), (0, 0, 60), ["board"])],
    labels=[("D", [(0.0, MOUNT_R, BOARD_Z1)]), ("A", "board")], dist=5.0)

# ------------------------------------------------------------------ 10 the back
fig("10a_back", "10a  The back, landscape", V_OB_R, C8 + g("board", "lens"),
    new=[(g("back"), (0, 0, -70), ["rb_back"])], labels=[("A", "rb_back"), ("B", "graflok_blade"), ("C", "graflok_wheel")], dist=5.2)
fig("10b_portrait", "10b  Turned to portrait", V_OB_R, C8 + g("board", "lens", "back"), state=dict(rho=-90.0),
    labels=[("A", "rb_back")], dist=5.2)


# ------------------------------------------------------------------ build (as View 1)
_cache = {}


def items_for(state):
    key = tuple(sorted(state.items()))
    if key not in _cache:
        _cache[key] = assemble(**state)
    return _cache[key]


def matches(name, prefixes):
    return any(name.startswith(p) for p in prefixes)


def build(f):
    items = items_for(f["state"])
    shown_names = f["show"] + [p for nw in f["new"] for p in nw[0]]
    shown = [(i.name, i.shape, i.mat) for i in items if matches(i.name, shown_names)]
    base = [s for n, s, m in shown if not any(matches(n, nw[0]) for nw in f["new"])]
    ref = Compound(base).bounding_box().center() if base else Vector(0, 0, 0)
    guides, placed = [], {}
    for nw in f["new"]:
        prefixes, off = nw[0], nw[1]
        guided = nw[2] if len(nw) > 2 else None
        for k, (n, s, m) in enumerate(shown):
            if not matches(n, prefixes) or n in placed:
                continue
            c = s.bounding_box().center()
            v = list(off)
            shown[k] = (n, Pos(*v) * s, m)
            placed[n] = v
            if guided is None or any(n.startswith(p) for p in guided):
                guides.append({"points": [(c.X, c.Y, c.Z), (c.X + v[0], c.Y + v[1], c.Z + v[2])]})
    d = OUT / f["name"]
    d.mkdir(parents=True, exist_ok=True)
    for old in d.glob("*.stl"):
        old.unlink()
    manifest = []
    for n, s, m in shown:
        p = d / f"{n}.stl"
        export_stl(s, str(p), tolerance=0.04, angular_tolerance=0.15)
        manifest.append({"name": n, "file": str(p), "mat": m})
    (d / "manifest.json").write_text(json.dumps(manifest, indent=1))
    labels = []
    for text, spec in f["labels"]:
        if isinstance(spec, str):
            pts = [tuple(s.bounding_box().center()) for n, s, m in shown if n.startswith(spec)]
            if not pts:
                raise KeyError(f"{f['name']}: nothing matches {spec}")
        else:
            pts = [tuple(p) for p in spec]
        labels.append({"text": text, "points": pts})
    (d / "points.json").write_text(json.dumps({"title": f["title"], "view": f["view"], "doc": f["doc"], "labels": labels,
                                               "guides": guides, "lines": f["lines"], **f["look"]}, indent=1))
    print(f"{f['name']}: {len(manifest)} meshes, {len(labels)} labels, {len(guides)} guides")


if __name__ == "__main__":
    want = set(sys.argv[1:])
    for f in FIGS:
        if not want or f["name"] in want:
            build(f)
