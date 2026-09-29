"""Export the View 2 test plates: print them before anything else.

print/test/*.stl                       each test part on its own, in print orientation
print/plates/plate_00a_shrink_gauge.3mf
print/plates/plate_00b_test_lens_drive.3mf   ASA: M65 thread, mount + board, shift pinion rig, rise worm rig with its miter pair and knob
print/plates/plate_00c_test_ways_arca.3mf    ASA: dovetail ways, Arca
print/plates/plate_00d_test_tpu.3mf          TPU: two wave washers
"""
import math, pathlib, sys
import numpy as np
import trimesh
from build123d import *
from params import *
import mech as M

ROOT = pathlib.Path(__file__).resolve().parent.parent / "print"
BED = 256.0
ON_SIDE = trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0])
FLIP = trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0])
UP = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])


def mesh(shape, tol=0.02):
    vs, fs = shape.tessellate(tol, 0.15)
    return trimesh.Trimesh(np.array([(v.X, v.Y, v.Z) for v in vs]), np.array(fs), process=True)


def placed(m, T=None):
    m = m.copy()
    if T is not None:
        m.apply_transform(T)
    m.apply_translation(-m.bounds[0])
    return m


def pack(items, margin=8.0, gap=10.0):
    items = sorted(items, key=lambda it: -max(it[1].extents[:2]))
    x = y = row = margin
    row = 0.0
    out = []
    for label, m in items:
        w, d = m.extents[0], m.extents[1]
        if x + w > BED - margin:
            x, y, row = margin, y + row + gap, 0.0
        if y + d > BED - margin:
            raise ValueError(f"test plate full at {label}")
        mm = m.copy()
        mm.apply_translation([x, y, 0])
        out.append((label, mm))
        x += w + gap
        row = max(row, d)
    # centre on the bed
    lo = np.min([m.bounds[0][:2] for _, m in out], axis=0)
    hi = np.max([m.bounds[1][:2] for _, m in out], axis=0)
    shift = (BED - (hi - lo)) / 2 - lo
    for _, m in out:
        m.apply_translation([shift[0], shift[1], 0])
    return out


def write(path, placed_items):
    scene = trimesh.Scene()
    for label, m in placed_items:
        scene.add_geometry(m, node_name=label, geom_name=label)
    scene.export(str(path))


def asa_parts():
    return [
        ("thread_coupon_M65_female", placed(mesh(M.thread_coupon(), 0.01))),
        ("lens_mount", placed(mesh(M.mount(), 0.01))),
        ("lens_board", placed(mesh(M.board()))),
        ("pinion_shaft", placed(mesh(M.pinion(M.block_shaft_len()), 0.01))),
        ("knob", placed(mesh(M.knob()))),
        ("knob_b", placed(mesh(M.knob()))),
        ("rack_62", placed(mesh(M.rack(62.0), 0.01))),
        ("pinion_block", placed(mesh(M.pinion_block()))),
        ("rack_carrier", placed(mesh(M.rack_carrier()), FLIP)),
        ("worm_short", placed(mesh(M.test_worm(), 0.01))),
        ("worm_block", placed(mesh(M.worm_block()), FLIP)),
        ("worm_rig_plug", placed(mesh(M.rig_plug()), UP)),
        ("knob_gear", placed(mesh(M.knob_gear(), 0.01), FLIP)),
        ("collar", placed(mesh(M.collar()))),
        ("rise_rack_slice", placed(mesh(M.rack_slice()), FLIP)),
        ("way_groove_flexure", placed(mesh(M.way_coupon_fixed(True)))),
        ("way_groove_rigid", placed(mesh(M.way_coupon_fixed(False)))),
        ("way_tongue_flexure", placed(mesh(M.way_coupon_tongue(True)))),
        ("way_tongue_rigid", placed(mesh(M.way_coupon_tongue(False)))),
        ("arca_coupon", placed(mesh(M.arca_coupon()), ON_SIDE)),
    ]


if __name__ == "__main__":
    (ROOT / "test").mkdir(parents=True, exist_ok=True)
    (ROOT / "plates").mkdir(parents=True, exist_ok=True)
    asa = asa_parts()
    tpu = [("tpu_drag_washer", placed(mesh(M.drag_washer()))), ("tpu_drag_washer_b", placed(mesh(M.drag_washer())))]
    gauge = [("shrink_gauge_100mm", placed(mesh(M.shrink_gauge())))]
    bad = []
    for label, m in asa + tpu + gauge:
        if not m.is_watertight or m.body_count != 1:
            bad.append(label)
        m.export(str(ROOT / "test" / f"{label}.stl"))
    write(ROOT / "plates" / "plate_00a_shrink_gauge.3mf", pack(gauge))
    lens_drive = [it for it in asa if not it[0].startswith(("way_", "arca_"))]
    ways_seal = [it for it in asa if it[0].startswith(("way_", "arca_"))]
    write(ROOT / "plates" / "plate_00b_test_lens_drive.3mf", pack(lens_drive))
    write(ROOT / "plates" / "plate_00c_test_ways_arca.3mf", pack(ways_seal))
    write(ROOT / "plates" / "plate_00d_test_tpu.3mf", pack(tpu))
    print(f"{len(asa)} ASA parts, {len(tpu)} TPU, gauge; not watertight: {bad or 'none'}")
    sys.exit(1 if bad else 0)
