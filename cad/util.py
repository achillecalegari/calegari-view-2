"""Small geometry helpers shared by every part."""
import math
from build123d import *

try:
    from bd_warehouse.thread import IsoThread
except Exception:  # pragma: no cover
    IsoThread = None

Z_UP = (Align.CENTER, Align.CENTER, Align.MIN)


def sfillet(shape, edges, r):
    try:
        return fillet(edges, r)
    except Exception:
        return shape


def schamfer(shape, edges, r):
    try:
        return chamfer(edges, r)
    except Exception:
        return shape


def box_at(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def cyl_x(r, x0, x1, y, z):
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(r, abs(x1 - x0))


def cyl_y(r, y0, y1, x, z):
    return Pos(x, (y0 + y1) / 2, z) * Rot(90, 0, 0) * Cylinder(r, abs(y1 - y0))


def cyl_z(r, z0, z1, x=0.0, y=0.0):
    return Pos(x, y, min(z0, z1)) * Cylinder(r, abs(z1 - z0), align=Z_UP)


def orient(shape, axis):
    """Turn a shape built along +Z toward an axis."""
    rot = {"+z": Rot(0, 0, 0), "-z": Rot(180, 0, 0), "+y": Rot(-90, 0, 0), "-y": Rot(90, 0, 0),
           "+x": Rot(0, 90, 0), "-x": Rot(0, -90, 0)}[axis]
    return rot * shape


def poly_face(pts):
    return make_face(Polyline(*pts, close=True))


def ring_sector(r0, r1, a0, a1, z0, z1, n=24):
    """Annular sector between angles a0..a1 (degrees, from +Y toward -X like a clock turned)."""
    pts = [(-r1 * math.sin(math.radians(a0 + (a1 - a0) * i / n)), r1 * math.cos(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    pts += [(-r0 * math.sin(math.radians(a1 - (a1 - a0) * i / n)), r0 * math.cos(math.radians(a1 - (a1 - a0) * i / n))) for i in range(n + 1)]
    return Pos(0, 0, z0) * extrude(poly_face(pts), amount=z1 - z0)


def polar(r, a):
    """Point at radius r, angle a (degrees from +Y toward -X)."""
    return (-r * math.sin(math.radians(a)), r * math.cos(math.radians(a)))


# ------------------------------------------------------------------ involute gearing
def _inv(a):
    return math.tan(a) - a


def gear_profile(m, z, x=0.0, alpha=20.0, n=10):
    """Closed outline of a spur gear (involute flanks, profile shift x), centred on the origin."""
    al = math.radians(alpha)
    r = m * z / 2
    rb = r * math.cos(al)
    ra = r + m * (1 + x)
    rf = r - m * (1.25 - x)
    s = m * (math.pi / 2 + 2 * x * math.tan(al))
    half = s / (2 * r) + _inv(al)                 # half tooth angle measured at the base circle
    def flank(rho):
        rho = max(rho, rb)
        a_r = math.acos(rb / rho)
        return half - _inv(a_r)
    r_start = max(rb, rf)
    radii = [r_start + (ra - r_start) * i / n for i in range(n + 1)]
    pts = []
    pitch = 2 * math.pi / z
    for i in range(z):
        c = i * pitch
        left = [(rho, c - flank(rho)) for rho in radii]
        right = [(rho, c + flank(rho)) for rho in reversed(radii)]
        tooth = []
        if rf < rb:
            tooth.append((rf, c - flank(rb)))
        tooth += left + right
        if rf < rb:
            tooth.append((rf, c + flank(rb)))
        # root arc to the next tooth
        a0, a1 = tooth[-1][1], (i + 1) * pitch - flank(r_start)
        root = [(rf, a0 + (a1 - a0) * k / 4) for k in range(1, 4)]
        pts += tooth + root
    return [(rho * math.sin(a), rho * math.cos(a)) for rho, a in pts]


def rack_profile(m, length, base, alpha=20.0):
    """Rack along X, teeth pointing +Y, pitch line at y = 0; body down to y = -(1.25 m + base)."""
    p = math.pi * m
    t = math.tan(math.radians(alpha))
    ha, hf = m, 1.25 * m
    y0 = -hf - base
    pts = [(-length / 2, y0), (length / 2, y0)]
    teeth = []
    x = -length / 2
    n = int(length / p)
    x0 = -n * p / 2
    for i in range(n):
        xc = x0 + (i + 0.5) * p
        w_pitch = p / 2
        teeth += [(xc - w_pitch / 2 - hf * t, -hf), (xc - w_pitch / 2 + ha * t, ha),
                  (xc + w_pitch / 2 - ha * t, ha), (xc + w_pitch / 2 + hf * t, -hf)]
    top = [(length / 2, -hf)] + list(reversed(teeth)) + [(-length / 2, -hf)]
    return pts + top
