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
    "body": ["body"], "graflok": ["graflok_module"], "blade": ["graflok_blade"], "wheel": ["graflok_wheel"],
    "pin_r": ["pinion_rise"], "washer_r": ["washer_rise"], "knob_r": ["knob_rise", "dot_knob_rise"],
    "v1": ["velvet_body"], "y": ["y_plate"], "rack_r": ["rack_rise"], "rack_s": ["rack_shift"], "v2": ["velvet_yplate"],
    "plug_y": ["plug_y"], "panel": ["lens_panel"], "pin_s": ["pinion_shift"], "plug_x": ["plug_x"],
    "washer_s": ["washer_shift"], "knob_s": ["knob_shift", "dot_knob_shift"], "heli": ["helicoid"], "mount": ["mount"],
    "board": ["board"], "lens": ["lens_body", "lens_glass"], "back": ["rb_"],
}


def g(*keys):
    return [p for k in keys for p in G[k]]


C1 = g("body", "graflok", "blade", "wheel")
C2 = C1 + g("pin_r", "washer_r", "knob_r")
C3 = C2 + g("v1")
YP = g("y", "rack_r", "rack_s", "v2")
C5 = C3 + YP + g("plug_y")
C7 = C5 + g("panel", "pin_s", "plug_x", "washer_s", "knob_s")
C8 = C7 + g("heli", "mount")

# Blender view directions: +x photographer's left, +y behind the camera, +z up
V_REAR = (0.35, 1.0, 0.3)
V_OB_R = (0.95, 1.0, 0.45)
V_OB_F = (-0.95, -1.0, 0.45)
V_34 = (-0.62, -1.0, 0.3)
V_RIGHT = (-1.0, -0.55, 0.35)          # the photographer's right side, from the front

FIGS = []


def fig(name, title, view, show, new=(), labels=(), lines=(), state=None, doc="asm", **look):
    FIGS.append(dict(name=name, title=title, view=view, show=list(show), new=list(new), labels=list(labels),
                     lines=list(lines), state=state or {}, doc=doc, look=look))


fig("1_graflok", "1  Graflok module, blade and wheel", V_OB_R, g("body"),
    new=[(g("graflok"), (0, 0, -45)), (g("blade"), (0, 0, -80)), (g("wheel"), (0, 0, -110))],
    labels=[("A", "graflok_module"), ("B", "graflok_blade"), ("C", "graflok_wheel")], dist=4.6)
fig("2_rise_drive", "2  Rise pinion, washer and knob", V_RIGHT, C1,
    new=[(g("pin_r"), (0, 0, 40)), (g("washer_r"), (-30, 0, 0)), (g("knob_r"), (-60, 0, 0), ["knob_rise"])],
    labels=[("A", "pinion_rise"), ("B", "washer_rise"), ("C", "knob_rise"),
            ("D", [(RISE_PIN[0], RISE_PIN[1], BODY_Z1)])], dist=4.4)
fig("3_velvet_v1", "3  Velvet V1 on the body", V_OB_F, C2,
    new=[(g("v1"), (0, 0, 35))], labels=[("V1", "velvet_body"), ("D", [(RISE_PIN[0], RISE_PIN[1], BODY_Z1)])], dist=4.6)
fig("4a_rise_rack", "4a  Rise rack into the Y plate's back", V_REAR, g("y"),
    new=[(g("rack_r"), (0, 0, -30))], labels=[("A", "rack_rise"), ("B", [(P.RISE_DETENT[0], P.RISE_DETENT[1], YP_Z0)])], dist=4.0)
fig("4b_shift_rack_v2", "4b  Shift rack and velvet V2 on its front", V_OB_F, g("y", "rack_r"),
    new=[(g("rack_s"), (0, 0, 30)), (g("v2"), (0, 0, 55))], labels=[("C", "rack_shift"), ("V2", "velvet_yplate")], dist=4.0)
fig("5a_y_in", "5a  Y plate in from below", V_34, C3,
    new=[(YP, (0, -150, 0), ["y_plate"])], labels=[("A", "y_plate")],
    lines=[dict(points=[(-H - 25, -200, 40), (-H - 25, -110, 40)], style="arrow")], dist=5.4)
fig("5b_plugs_y", "5b  Two plugs under the plinth", (-0.55, -1.0, -0.7), C3 + YP, state=dict(sy=30.0),
    new=[(g("plug_y"), (0, -35, 0))], labels=[("B", "plug_y")], dist=4.4)
fig("6_shift_pinion", "6  Shift pinion into the lens panel", V_REAR, g("panel"),
    new=[(g("pin_s"), (0, 0, -35))], labels=[("A", "pinion_shift"), ("B", [(P.SHIFT_DETENT[0], P.SHIFT_DETENT[1], XP_Z0)])], dist=4.0)
fig("7_panel_in", "7  Lens panel in from the right, plugs, knob", V_34, C5,
    new=[(g("panel", "pin_s"), (-200, 0, 0), ["lens_panel"]), (g("plug_x"), (-30, 0, 0)),
         (g("washer_s"), (0, 25, 0)), (g("knob_s"), (0, 50, 0), ["knob_shift"])],
    labels=[("A", "lens_panel"), ("B", "plug_x"), ("C", "washer_shift"), ("D", "knob_shift")],
    lines=[dict(points=[(-H - 250, -H - 15, 45), (-H - 150, -H - 15, 45)], style="arrow")], dist=5.2)
fig("8_helicoid_mount", "8  Helicoid and lens mount", V_OB_F, C7,
    new=[(g("heli"), (0, 0, 45)), (g("mount"), (0, 0, 90))], labels=[("A", "helicoid"), ("B", "mount")], dist=4.8)
fig("9_board", "9  Lens on its board, board into the mount", (-1.0, -0.8, 0.35), C8,
    new=[(g("board"), (0, 0, 50)), (g("lens"), (0, 0, 105), ["lens_glass"])], state=dict(back=False),
    labels=[("A", "board"), ("B", [(0.0, 31.5, BOARD_Z1 + 105 + 9)]), ("C", [(0.0, MOUNT_R, BOARD_Z1)])], dist=5.0)
fig("10_back", "10  The back", V_OB_R, C8 + g("board", "lens"),
    new=[(g("back"), (0, 0, -70), ["rb_back"])], labels=[("A", "rb_back"), ("B", "graflok_blade"), ("C", "graflok_wheel")], dist=5.0)


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
