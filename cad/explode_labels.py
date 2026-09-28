"""Labelled exploded view of View 2: writes out/mesh_explode/points.json for render/white.py + annotate.py."""
import json, pathlib
from assembly import assemble
E = 30.0
it = {i.name: i.shape.bounding_box() for i in assemble(E=E, back=True)}
def corner(n, fx, fy, face="max"):
    b = it[n]
    z = b.max.Z if face == "max" else b.min.Z
    return (b.min.X + fx * (b.max.X - b.min.X), b.min.Y + fy * (b.max.Y - b.min.Y), z)
def centre(n):
    c = it[n].center(); return (c.X, c.Y, c.Z)
labels = [
    ("<Body, foot and handle: one print", corner("body", 0.25, 0.97)),
    ("<Graflok module, snaps in", corner("graflok_module", 0.1, 0.9, "min")),
    ("<Blade and printed wheel", centre("graflok_wheel")),
    ("<Rise pinion and knob", centre("knob_rise")),
    (">Y plate, flexure ways, both racks", corner("y_plate", 0.95, 0.95)),
    (">Shift pinion and knob, ride with the lens", centre("knob_shift")),
    (">Lens panel, printed M65 thread, engraved scale", corner("lens_panel", 0.97, 0.03)),
    (">Helicoid (bought)", corner("helicoid", 0.5, 0.0)),
    (">Lens mount, bayonet", corner("mount", 0.85, 0.15)),
    (">Round lens board", corner("board", 0.5, 1.0)),
]
out = pathlib.Path(__file__).resolve().parent.parent / "out" / "mesh_explode" / "points.json"
out.write_text(json.dumps({"title": "", "view": "explode34", "labels": [{"text": t, "points": [p]} for t, p in labels]}, indent=1))
print("ok")
