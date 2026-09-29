"""Export everything needed to print View 2.

print/step/       STEP of every printed part, in assembly coordinates
print/stl/        STL of every printed part, oriented on the bed
print/plates/     Bambu P1S plates (256 x 256) as 3MF, one material and layer height per plate
print/templates/  1:1 SVG cutting templates for the two velvet pieces (print at 100 %)

python export.py      (run testplate.py for the test plates)
"""
import math, pathlib, sys
import numpy as np
import trimesh
from build123d import *
from params import *
import parts as P
import mech as M
from assembly import shift_shaft

ROOT = pathlib.Path(__file__).resolve().parent.parent / "print"
BED = 256.0
FLIP = trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0])
EYE = np.eye(4)
UP = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])   # assembly +Y up


def mesh(shape, tol=0.02):
    vs, fs = shape.tessellate(tol, 0.15)
    return trimesh.Trimesh(np.array([(v.X, v.Y, v.Z) for v in vs]), np.array(fs), process=True)


def on_bed(m, T):
    m = m.copy()
    m.apply_transform(T)
    m.apply_translation(-m.bounds[0])
    return m


def catalogue():
    """(name, shape, orientation, copies, plate group, why)"""
    return [
        ("body", P.body_part(), FLIP, 1, "black", "front face down: grooves, pockets and the engraved name on the bed"),
        ("y_plate", P.y_plate(), FLIP, 1, "black", "front face down: tongues, rack slot and detent spring on top"),
        ("lens_panel", P.lens_panel(thread=True), FLIP, 1, "black012", "front face down: engraved scale on the bed, M65 thread at 0.12 mm"),
        ("lens_mount", M.mount(thread=True), EYE, 1, "black012", "stub down: M65 thread at 0.12 mm; supports under the ring only (build plate only)"),
        ("rotator", P.rotator(), FLIP, 1, "black", "front face down: the seat, the rails and the M6 stud on top"),
        ("rise_worm", M.worm_part(), EYE, 1, "black012", "standing: pin down, the miter gear on top"),
        ("stop_peg", Rot(0, -90, 0) * P.stop_peg(), EYE, 1, "black", "standing"),
        ("graflok_wheel", P.graflok_wheel(), EYE, 1, "black", "M6 thread axis vertical"),
        ("lens_board", M.board(), EYE, 1, "black", "rear face down"),
        ("pinion_shift", M.pinion(shift_shaft()), EYE, 1, "black012", "teeth on the bed: exact involutes"),
        ("knob", M.knob(), EYE, 2, "black", "crown down: the knurl's ribs are drawn in the bed plane"),
        ("rise_knob_gear", M.knob_gear(), FLIP, 1, "black012", "shaft end down, the miter gear on top: every slope 45 degrees or steeper"),
        ("rise_collar", M.collar(), EYE, 1, "black", "flat"),
        ("plug_worm", M.worm_plug(), UP, 1, "black", "bottom face down"),
        ("plug_rack", M.rack_plug(), UP, 1, "black", "bottom face down"),
        ("rack_shift", M.rack(P.SHIFT_RACK[0]), EYE, 1, "black", "lying on its side: teeth in the bed plane"),
        ("plug_y_left", P.way_plug_y(1), EYE, 1, "black", ""),
        ("plug_y_right", P.way_plug_y(-1), EYE, 1, "black", ""),
        ("plug_x_top", P.way_plug_x(1), EYE, 1, "black", ""),
        ("plug_x_bottom", P.way_plug_x(-1), EYE, 1, "black", ""),
        ("graflok_blade", P.graflok_blade(), FLIP, 1, "red", "front face down"),
        ("drag_washer", M.drag_washer(), EYE, 2, "tpu", "TPU 95A, external spool"),
    ]


def pack(items, margin=6.0, gap=10.0):
    items = sorted(items, key=lambda it: -max(it[1].extents[:2]))
    plates = []
    for label, m in items:
        w, d = m.extents[0], m.extents[1]
        if w > BED - 2 * margin or d > BED - 2 * margin:
            raise ValueError(f"{label} does not fit: {w:.0f} x {d:.0f}")
        placed = False
        for pl in plates:
            x, y, row = pl["cursor"]
            if x + w > BED - margin:
                x, y, row = margin, y + row + gap, 0.0
            if y + d <= BED - margin:
                mm = m.copy(); mm.apply_translation([x, y, 0]); pl["parts"].append((label, mm))
                pl["cursor"] = (x + w + gap, y, max(row, d))
                placed = True
                break
        if not placed:
            mm = m.copy(); mm.apply_translation([margin, margin, 0])
            plates.append({"parts": [(label, mm)], "cursor": (margin + w + gap, margin, d)})
    for pl in plates:                                  # centre each plate
        lo = np.min([m.bounds[0][:2] for _, m in pl["parts"]], axis=0)
        hi = np.max([m.bounds[1][:2] for _, m in pl["parts"]], axis=0)
        sh = (BED - (hi - lo)) / 2 - lo
        for _, m in pl["parts"]:
            m.apply_translation([sh[0], sh[1], 0])
    return plates


def write_plate(path, parts):
    scene = trimesh.Scene()
    for label, m in parts:
        scene.add_geometry(m, node_name=label, geom_name=label)
    scene.export(str(path))


def svg_page(path, title, shape_face, note):
    """A4, 1:1: the face's outline and holes as paths, centred, with a 100 mm check bar."""
    W, Hh = 210.0, 297.0
    paths = []
    for f in shape_face.faces():
        for w in [f.outer_wire()] + list(f.inner_wires()):
            pts = [(v.X + W / 2, Hh / 2 - v.Y) for v in w.positions(np.linspace(0, 1, 600))]
            paths.append("M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z")
    body = "\n".join(f'<path d="{p}" fill="none" stroke="black" stroke-width="0.3"/>' for p in paths)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{Hh}mm" viewBox="0 0 {W} {Hh}">\n'
           f'<text x="12" y="16" font-family="Helvetica" font-size="5">{title}</text>\n'
           f'<text x="12" y="23" font-family="Helvetica" font-size="3.2">{note}</text>\n'
           f'<line x1="12" y1="285" x2="112" y2="285" stroke="black" stroke-width="0.4"/>'
           f'<text x="12" y="282" font-family="Helvetica" font-size="3">100 mm: check the print scale</text>\n{body}\n</svg>')
    pathlib.Path(path).write_text(svg)


if __name__ == "__main__":
    for d in ("step", "stl", "plates", "templates"):
        (ROOT / d).mkdir(parents=True, exist_ok=True)
        if d != "templates":
            for f in (ROOT / d).glob("*"):
                if f.suffix in (".step", ".stl") or (d == "plates" and not f.name.startswith("plate_00")):
                    f.unlink()
    groups, bad, report = {}, [], []
    for name, shape, T, copies, grp, why in catalogue():
        export_step(shape, str(ROOT / "step" / f"{name}.step"))
        m = on_bed(mesh(shape, 0.01 if grp.endswith("012") else 0.02), T)
        m.merge_vertices()
        if not m.is_watertight or m.body_count != 1:
            bad.append(name)
        m.export(str(ROOT / "stl" / f"{name}.stl"))
        for k in range(copies):
            groups.setdefault(grp, []).append((name if copies == 1 else f"{name}_{k + 1}", m))
        report.append(f"{name:18s} x{copies}  {grp:9s} {m.extents[0]:6.1f} x {m.extents[1]:6.1f} x {m.extents[2]:5.1f}  {why}")
    names = {"black": "black", "black012": "black_0.12mm_layers", "red": "red", "tpu": "tpu"}
    summary = []
    n = 0
    for grp in ("black", "black012", "red", "tpu"):
        for pl in pack(groups[grp]):
            n += 1
            path = ROOT / "plates" / f"plate_{n:02d}_{names[grp]}.3mf"
            write_plate(path, pl["parts"])
            summary.append(f"{path.name}: " + ", ".join(l for l, _ in pl["parts"]))
    svg_page(ROOT / "templates" / "velvet_V1_body.svg", "V1: velvet on the body front", P.velvet_body_outline(),
             "Cut the outline with scissors and the window with a blade. The top edge goes to the body's top.")
    svg_page(ROOT / "templates" / "velvet_V2_y_plate.svg", "V2: velvet on the Y plate front", P.velvet_yplate_outline(),
             "Cut the outline with scissors and the window with a blade.")
    (ROOT / "plates" / "PLATES.txt").write_text("\n".join(summary) + "\n\n" + "\n".join(report) + "\n")
    print("\n".join(summary))
    print(f"not watertight or not one body: {bad or 'none'}")
    sys.exit(1 if bad else 0)
