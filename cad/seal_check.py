"""Light-seal check for View 2's two sliding interfaces, measured on the velvet (as View 1).

The seal is where both faces are solid AND the velvet lies between them. Light reaches the film through
the openings; the seal width is the shortest way from the openings to the edge of that band. The whole
shift range is swept in 5 mm steps. Exit 1 below MIN_SEAL.
"""
import sys
import numpy as np
import trimesh
from shapely.geometry import Point, Polygon
from shapely.affinity import translate
from shapely.ops import unary_union
from params import *
import parts as P

MIN_SEAL = 6.0
STEP = 5


def mesh(shape):
    vs, fs = shape.tessellate(0.05, 0.2)
    return trimesh.Trimesh(np.array([(v.X, v.Y, v.Z) for v in vs]), np.array(fs), process=True)


def section(m, z):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    planar, to3d = s.to_2D()
    out = []
    for p in planar.polygons_full:
        ext = trimesh.transform_points(np.column_stack([np.array(p.exterior.coords), np.zeros(len(p.exterior.coords))]), to3d)[:, :2]
        holes = [trimesh.transform_points(np.column_stack([np.array(r.coords), np.zeros(len(r.coords))]), to3d)[:, :2] for r in p.interiors]
        out.append(Polygon(ext, holes))
    return unary_union(out)


def opening_at(poly, cx, cy):
    for g in getattr(poly, "geoms", [poly]):
        for r in g.interiors:
            h = Polygon(r)
            if h.contains(Point(cx, cy)):
                return h
    raise ValueError("no opening around the axis")


def face2d(face):
    polys = []
    for f in face.faces():
        outer = [(v.X, v.Y) for v in f.outer_wire().positions(np.linspace(0, 1, 400))]
        inner = [[(v.X, v.Y) for v in w.positions(np.linspace(0, 1, 200))] for w in f.inner_wires()]
        polys.append(Polygon(outer, inner))
    return unary_union(polys)


def width(contact, light):
    region = unary_union([contact, light]).buffer(0.05).buffer(-0.05)
    return light.buffer(-0.01).distance(region.boundary)


if __name__ == "__main__":
    body = section(mesh(P.body_part()), BODY_Z1 - 0.05)
    ym = mesh(P.y_plate())
    y_rear, y_front = section(ym, YP_Z0 + 0.05), section(ym, YP_Z1 - 0.05)
    x_rear = section(mesh(P.lens_panel(thread=False)), XP_Z0 + 0.05)
    v1, v2 = face2d(P.velvet_body_outline()), face2d(P.velvet_yplate_outline())
    b_open, yr_open = opening_at(body, 0, 0), opening_at(y_rear, 0, 0)
    yf_open, x_open = opening_at(y_front, 0, 0), opening_at(x_rear, 0, 0)
    v1_win, v2_win = opening_at(v1, 0, 0), opening_at(v2, 0, 0)
    worst = (99.0, None)
    for sy in range(-int(FALL), int(RISE) + 1, STEP):
        for sx in range(-int(SHIFT), int(SHIFT) + 1, STEP):
            c1 = body.intersection(translate(y_rear, 0, sy)).intersection(v1)
            w1 = width(c1, unary_union([b_open, v1_win, translate(yr_open, 0, sy)]))
            c2 = translate(y_front, 0, sy).intersection(translate(x_rear, sx, sy)).intersection(translate(v2, 0, sy))
            w2 = width(c2, unary_union([translate(yf_open, 0, sy), translate(v2_win, 0, sy), translate(x_open, sx, sy)]))
            for w, name in ((w1, "body/Y plate"), (w2, "Y plate/lens panel")):
                if w < worst[0]:
                    worst = (w, f"{name} at x {sx:+d} y {sy:+d}")
    print(f"narrowest velvet seal {worst[0]:.2f} mm, {worst[1]} (minimum {MIN_SEAL}; swept every {STEP} mm)")
    sys.exit(0 if worst[0] >= MIN_SEAL else 1)
