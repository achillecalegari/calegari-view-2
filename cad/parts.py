"""Calegari View 2: every printed part, in assembly coordinates (Z optical axis, 0 = film).

Print orientation of each part is in export.py. The rule for features: whatever faces the bed is a
groove, a recess or an engraving (never a boss); bosses, bumps and tongues live on the top face.
"""
import math
from build123d import *
from params import *
from util import *
from util import IsoThread
import mech as M

# ------------------------------------------------------------------ light path (as View 1)
PUPIL_Z, PUPIL_R, LIGHT_MARGIN = 55.0, 18.0, 1.5


FRAME_HALF = max(FILM_W, FILM_H) / 2      # the back turns: the fixed openings see both orientations


def cone_half(z, rel_x=0.0, rel_y=0.0):
    """Half-size of the light bundle at z, for a lens displaced (rel_x, rel_y) from the plate that cuts it:
    a plate that moves with the lens sees the bundle slide by (t - 1) times the move."""
    t = z / PUPIL_Z
    hx = (1 - t) * FRAME_HALF + t * PUPIL_R
    hy = (1 - t) * FRAME_HALF + t * PUPIL_R
    return hx + abs(rel_x) + LIGHT_MARGIN, hy + abs(rel_y) + LIGHT_MARGIN


def opening_body(z):
    t = z / PUPIL_Z
    return cone_half(z, t * SHIFT, t * RISE)


def opening_yplate(z):
    """The Y plate moves with the rise: the bundle slides by (t - 1) rise in its frame; the shift is t shift."""
    t = z / PUPIL_Z
    return cone_half(z, t * SHIFT, (1 - t) * RISE)


def opening_panel(z):
    t = z / PUPIL_Z
    return cone_half(z, (1 - t) * SHIFT, (1 - t) * RISE)


def rect_loft(z0, half0, z1, half1, r=3.0):
    a = Pos(0, 0, z0) * RectangleRounded(2 * half0[0], 2 * half0[1], r)
    b = Pos(0, 0, z1) * RectangleRounded(2 * half1[0], 2 * half1[1], r)
    return loft([a, b])


def slab(w, h, z0, z1, r=CORNER_R, cx=0.0, cy=0.0):
    s = extrude(Pos(cx, cy, z0) * RectangleRounded(w, h, r), amount=z1 - z0)
    return sfillet(s, s.edges().filter_by(Plane.XY), EDGE)


def dot(d, depth, axis="+z", lift=0.3):
    return orient(Pos(0, 0, -depth) * Cylinder(d / 2, depth + lift, align=Z_UP), axis)


def engraving(text, size, depth=0.5, tracking=0.0, font_style=FontStyle.REGULAR):
    """Text on the XY plane, centred on the origin, cut from z = 0 down to -depth; letters spaced by
    `tracking` (in text heights)."""
    parts, x = [], 0.0
    for ch in text:
        if ch == " ":
            x += size * (0.45 + tracking)
            continue
        if ch == ".":                              # the font's period is too small to engrave: a round dot
            parts.append(Pos(x + size * 0.16, -size * 0.34, 0) * Circle(size * 0.13))
            x += size * (0.32 + tracking)
            continue
        g = Text(ch, font_size=size, font_style=font_style, align=(Align.MIN, Align.CENTER))
        w = g.bounding_box().size.X
        parts.append(Pos(x, 0, 0) * g)
        x += w + size * tracking
    x -= size * tracking
    solid = None
    for p in parts:
        s = extrude(Pos(-x / 2, 0, 0) * p, amount=-depth)
        solid = s if solid is None else solid + s
    return solid, x


# ------------------------------------------------------------------ way prisms
def prism_y(pts_uw, side, z_face, y0, y1):
    """Profile (u, w) on the side s = +/-1 of the Y axis: x = s u, z = z_face - w; run along Y."""
    f = make_face(Polyline(*[(side * u, y0, z_face - w) for u, w in pts_uw], close=True))
    return extrude(f, amount=y1 - y0, dir=(0, 1, 0))


def prism_x(pts_uw, side, z_face, x0, x1):
    """Profile (u, w) on the side s = +/-1 of the X axis: y = s u, z = z_face - w; run along X."""
    f = make_face(Polyline(*[(x0, side * u, z_face - w) for u, w in pts_uw], close=True))
    return extrude(f, amount=x1 - x0, dir=(1, 0, 0))


FLEX_SIDE_Y = 1          # the +X groove of the body is the flexure
FLEX_SIDE_X = -1         # the bottom groove of the Y plate is the flexure

VELVET_T = GAP                          # self-adhesive velvet, about 1 mm, pressed into the 0.8 mm gap
V1_X, V1_Y = 48.0, (-H + 0.3, H - 0.3)            # body velvet: inside the ways, the body's full height
V2_X, V2_Y = YP_HALF - 1.0, 48.0                   # Y plate velvet: inside the horizontal ways


# ------------------------------------------------------------------ zero detents
# A flat spring (12 x 6, 1.4 thick) cut in the moving plate's back, fixed at its -X end, with a bump near
# the free end. The bump crosses the gap and presses 0.4 into the other face; at zero it drops into a
# dimple and the spring relaxes: a light click. Bump and dimple positions are in the moving plate's frame.
RISE_DETENT = (70.0, -30.0)             # on the Y plate's back; dimple in the body
SHIFT_DETENT = (0.0, -72.0)             # on the lens panel's back; dimple in the Y plate
DET_L, DET_W, DET_T = 12.0, 6.0, 1.4


def detent_cut(xy, z_face, into):
    """U slit through the skin plus a 1 mm cavity behind it. `into` = +1 if the plate lies at z > z_face."""
    xb, yb = xy
    x0, x1 = xb - DET_L + 1.5, xb + 1.5          # root at x0, free end at x1
    zc0, zc1 = (z_face + DET_T, z_face + DET_T + 1.0) if into > 0 else (z_face - DET_T - 1.0, z_face - DET_T)
    cut = box_at(x0, x1 + 0.8, yb - DET_W / 2 - 0.8, yb + DET_W / 2 + 0.8, zc0, zc1)
    zs0, zs1 = (z_face - 1, z_face + DET_T + 0.01) if into > 0 else (z_face - DET_T - 0.01, z_face + 1)
    u = box_at(x0, x1 + 0.8, yb - DET_W / 2 - 0.8, yb + DET_W / 2 + 0.8, zs0, zs1) - box_at(x0 - 1, x1, yb - DET_W / 2, yb + DET_W / 2, zs0 - 1, zs1 + 1)
    return cut + u


def detent_bump(xy, z_face, out, gap=GAP):
    xb, yb = xy
    h = gap + 0.4
    return Pos(xb, yb, z_face) * orient(Pos(0, 0, -0.01) * Cone(1.3, 0.3, h + 0.01, align=Z_UP), "+z" if out > 0 else "-z")


def dimple(xy, z_face, into, depth=0.6):
    """Cone into the face. 0.6 deep: the bump sinks its 0.4 and the spring relaxes (the plates, held by
    their flexure ways). Shallower: the spring keeps part of its preload (the rotator, held on its lugs)."""
    xb, yb = xy
    c = Cone(1.2, 1.2 - depth / 0.6, depth + 0.01, align=Z_UP)
    return Pos(xb, yb, z_face) * orient(Pos(0, 0, -0.01) * c, "+z" if into > 0 else "-z")


# ------------------------------------------------------------------ racks: a tooth space faces the pinion at zero
def rack_span(pin, lo, hi, hard_lo=-1e9, hard_hi=1e9):
    """(length, centre) of the shortest rack that covers lo..hi, stays inside hard_lo..hard_hi and has a
    tooth space at `pin` (the pinion has a tooth pointing at the rack at zero)."""
    p = math.pi * MOD
    for n in range(int((hi - lo) / p), 200):
        for k in range(6, 60):
            L = n * p + k * 0.05                   # the ends trim a partial tooth; int(L / p) stays n
            off = 0.0 if n % 2 == 0 else p / 2
            for m in range(-60, 61):
                c = pin - off + m * p
                if c - L / 2 <= lo and c + L / 2 >= hi and c - L / 2 >= hard_lo and c + L / 2 <= hard_hi:
                    return L, c
    raise ValueError("no rack length")


SHIFT_RACK = rack_span(SHIFT_PIN[0], SHIFT_PIN[0] - SHIFT - 4.0, SHIFT_PIN[0] + SHIFT + 4.0, hard_hi=YP_HALF - 2.0)   # on the Y plate (x)


# ------------------------------------------------------------------ Graflok seat on the rotator (as View 1)
GF_HALF = 65.0
POCKET_Y0, POCKET_Y1, POCKET_WALL_X = -39.3, 40.0, 55.0
TRAP_X, TRAP_Y, TRAP_D = (-47.5, -42.5), (-36.0, 36.5), 1.5
LOOP_X, LOOP_Y = 43.0, 34.5
SLIDE_RELIEF_X, SLIDE_RELIEF_Y, SLIDE_RELIEF_Z = -56.0, 40.0, SEAT_Z + 3.5
LIP_RELIEF_X, LIP_RELIEF_Y, LIP_RELIEF_D = 44.0, (51.0, 64.0), 2.2
GATE_W, GATE_H = 78.0, 60.0
BLADE_TRAVEL, BLADE_Y0, BLADE_W, BLADE_T = 4.5, 40.6, 16.2, 2.2
TONGUE_X = (-26.0, 26.0)
WHEEL_XY = (0.0, 47.0)                   # the blade's slot must stay inside the blade: 1.9 mm above, 3 below
STUD_D, STUD_L = 6.0, 7.5
STUD_PITCH = 1.0
ROT_FLOOR = ROT_Z1 + 0.2                 # the body's floor: the springs push the rotator 0.2 back onto the lugs
GAP_ROT = ROT_FLOOR - ROT_Z1
LAB_R = (69.8, 71.6)                     # labyrinth rib on the body floor, groove in the rotator
STOP_PEG = dict(ang=0.0, z=5.2, d=3.0, r0=ROT_R - 1.1)   # radial peg through the body's side, into the rotator's arc groove
HANDLE_Z0 = 10.0                         # the handle stands off the back: z 10..22, the dark slide's grip passes under it


def msector(r0, r1, a0, a1, z0, z1):
    """Annular sector, angles in degrees counterclockwise from +X seen from the front."""
    return ring_sector(r0, r1, a0 - 90.0, a1 - 90.0, z0, z1)


def mpolar(r, a):
    return (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))


def rot_cone(c=0.0):
    """The rotator's back edge, a 45 degree cone from ROT_R - LUG_CONE at its rear face to ROT_R."""
    return Pos(0, 0, GF_Z0) * Cone(ROT_R - LUG_CONE + c, ROT_R + c + 0.01, LUG_CONE + 0.01, align=Z_UP)


# ================================================================== BODY (one print, front face down)
NAME = "CALEGARI VIEW 2"
NAME_SIZE, NAME_TRACK = 4.2, 0.28


def name_plate():
    """Engraved name with a red dot before it, centred on the handle bar's front face."""
    txt, w = engraving(NAME, NAME_SIZE, 0.5, NAME_TRACK, FontStyle.BOLD)
    xc = 4.0
    yc = H + HANDLE_H - HANDLE_BAR / 2
    return Pos(xc, yc, BODY_Z1) * txt, (xc - w / 2 - 6.0, yc)


def body_part():
    # one front block: body and handle share the front face; the foot is an Arca dovetail, set back
    y0, y1 = -H, H + HANDLE_H
    b = extrude(Pos(0, (y0 + y1) / 2, BODY_Z0) * RectangleRounded(BODY, y1 - y0, CORNER_R), amount=BODY_Z1 - BODY_Z0)
    b -= Pos(0, (H + y1 - HANDLE_BAR) / 2, BODY_Z0 - 1) * extrude(
        RectangleRounded(BODY - 2 * HANDLE_POST, y1 - HANDLE_BAR - H, 4.0), amount=BODY_Z1 - BODY_Z0 + 2)
    b -= box_at(-H + HANDLE_POST + 4.0, H - HANDLE_POST - 4.0, H - 0.5, H + 4.0, BODY_Z0 - 1, BODY_Z1 + 1)
    b -= box_at(-H - 1, H + 1, H + 0.01, y1 + 1, BODY_Z0 - 1, HANDLE_Z0)          # the handle stands off the back
    b = sfillet(b, b.edges().filter_by(Plane.XY), EDGE)
    foot = arca_rail(Plane(origin=(0, -H, ARCA_ZC), x_dir=(0, 0, 1), z_dir=(1, 0, 0)))
    foot = sfillet(foot, foot.edges().filter_by(Axis.Z), 2.0)
    b += foot

    # the rotator's recess, its two lugs (45 degree cones), the floor's labyrinth rib
    b -= cyl_z(ROT_R + ROT_C, BODY_Z0 - 1, ROT_FLOOR)
    for a in LUG_ANG:
        lug = msector(ROT_R - LUG_CONE - 0.5, ROT_R + ROT_C + 0.5, a - LUG_SPAN / 2, a + LUG_SPAN / 2, BODY_Z0, BODY_Z0 + LUG_CONE)
        lug -= rot_cone(0.08)
        b += lug
    b += cyl_z(LAB_R[1], ROT_FLOOR - 0.4, ROT_FLOOR + 0.01) - cyl_z(LAB_R[0], ROT_FLOOR - 1, ROT_FLOOR + 1)
    # three flat springs in the floor push the rotator back and click into its dimples
    for a in ROT_SPRINGS:
        T = Rot(0, 0, a) * Pos(ROT_SPRING_R, 0, 0) * Rot(0, 0, 90)
        b -= T * detent_cut((0.0, 0.0), ROT_FLOOR, +1)
        b += T * detent_bump((0.0, 0.0), ROT_FLOOR, -1, GAP_ROT)
    # the stop peg's hole, radial, from the photographer's left side face
    pa, pz, pd = STOP_PEG["ang"], STOP_PEG["z"], STOP_PEG["d"]
    b -= Rot(0, 0, pa) * Pos((STOP_PEG["r0"] + H + 2) / 2, 0, pz) * Rot(0, 90, 0) * Cylinder(pd / 2 - PRESS_FIT / 2, H + 2 - STOP_PEG["r0"])
    # the dark slide leaves on the photographer's right in landscape and at the top in portrait
    b -= box_at(-H - 1, -ROT_R + 1, -SLIDE_RELIEF_Y, SLIDE_RELIEF_Y, BODY_Z0 - 1, SLIDE_RELIEF_Z)
    b -= box_at(-SLIDE_RELIEF_Y, SLIDE_RELIEF_Y, ROT_R - 1, H + 1, BODY_Z0 - 1, SLIDE_RELIEF_Z)
    # the light path in front of the rotator: square (both orientations), stepped against flare
    h0 = opening_body(ROT_FLOOR)
    b -= rect_loft(ROT_FLOOR - 0.5, h0, BODY_Z1 + 0.5, opening_body(BODY_Z1))
    for z in (12.0, 16.0):
        hz = opening_body(z)
        b -= box_at(-hz[0] - 1.6, hz[0] + 1.6, -hz[1] - 1.6, hz[1] + 1.6, z, z + 2.0)

    # vertical ways: two grooves, open at the bottom of the plinth, closed at the top
    y_top = Y_TONGUE[1] + RISE
    for sd in (-1, 1):
        b -= prism_y(M.groove_profile(sd == FLEX_SIDE_Y), sd, BODY_Z1, -H - 1, y_top)
        if sd == FLEX_SIDE_Y:
            b -= prism_y(M.flex_slit(), sd, BODY_Z1, -H + 6.0, y_top - 4.0)
    # rise drive: the worm's bore straight up from the bottom face (the worm goes in from below after the
    # Y plate), the side bore for the knob's gear and its collar, and the channel for the Y plate's rack,
    # open at the bottom (the plate goes in from below); one plug closes the bore and the channel
    b -= box_at(M.RACK_CH[0], M.RACK_CH[1], -H - 1, WRACK[1] + RISE + 0.5, M.RACK_CH[2], BODY_Z1 + 1)
    b -= M.rise_cuts(-H)
    b -= dimple(RISE_DETENT, BODY_Z1, -1)
    # rise index (red dot) on the right side face, by the Y plate's scale
    b -= Pos(-H, 0.0, BODY_Z1 - 2.2) * dot(2.4, 0.6, "-x")
    # name on the handle
    txt, dxy = name_plate()
    b -= txt
    b -= Pos(dxy[0], dxy[1], BODY_Z1) * dot(2.6, 0.6)
    return b


def arca_rail(plane):
    f = plane * make_face(Polyline(*M.arca_profile(), close=True))
    return extrude(f, amount=ARCA_LEN / 2, both=True)


# ================================================================== GRAFLOK MODULE, BLADE, WHEEL (as before)
def rotator(rho=0.0):
    """The rotating back: View 1's Graflok seat on a round plate that turns rho degrees (0 landscape,
    -90 portrait) in the body's recess. Its back edge is a 45 degree cone under the body's two lugs; three
    springs in the recess floor push it onto them and click into its dimples at 0 and -90. Two notches
    let it past the lugs only when turned ROT_ENTRY; the stop peg runs in an arc groove on its rim.
    Printed front face down: the seat, the rails and the stud on top."""
    z0, z1 = GF_Z0, ROT_Z1
    g = rot_cone() + cyl_z(ROT_R, z0 + LUG_CONE, z1)
    g = sfillet(g, g.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1], 0.6)
    # the Graflok seat (as View 1): the back's nose pocket, the dark-slide relief, the lip reliefs
    g -= box_at(-ROT_R - 1, POCKET_WALL_X, POCKET_Y0, POCKET_Y1, z0 - 1, SEAT_Z)
    g -= box_at(-ROT_R - 1, SLIDE_RELIEF_X, -SLIDE_RELIEF_Y, SLIDE_RELIEF_Y, z0 - 1, SLIDE_RELIEF_Z)
    for sd in (1, -1):
        g -= box_at(-LIP_RELIEF_X, LIP_RELIEF_X, sd * LIP_RELIEF_Y[0], sd * LIP_RELIEF_Y[1], z0 - 1, z0 + LIP_RELIEF_D)
    # the gate and the seat's light traps (they turn with the frame)
    h0 = opening_body(SEAT_Z)
    g -= box_at(-GATE_W / 2, GATE_W / 2, -GATE_H / 2, GATE_H / 2, SEAT_Z - 1, z1 + 1)
    g -= box_at(TRAP_X[0], TRAP_X[1], TRAP_Y[0], TRAP_Y[1], SEAT_Z - 0.01, SEAT_Z + TRAP_D)
    loop = Rectangle(2 * LOOP_X + 1.2, 2 * LOOP_Y + 1.2) - Rectangle(2 * LOOP_X - 1.2, 2 * LOOP_Y - 1.2)
    g -= Pos(0, 0, SEAT_Z - 0.01) * extrude(loop, amount=1.0)
    # the back's bottom rail and the blade's rails, the clamp stud (as View 1)
    rail = box_at(-56.0, 47.0, -43.0, POCKET_Y0, SEAT_Z - 6.6, z0 + 0.01)
    rail += box_at(-56.0, 47.0, -51.0, -43.0, SEAT_Z - 8.4, z0 + 0.01)
    rail = sfillet(rail, rail.edges().filter_by(Axis.X).group_by(Axis.Z)[0], 0.8)
    g += rail
    for sd in (-1, 1):
        prof = [(42.7, 0.0), (47.0, 0.0), (47.0, BLADE_T + 1.2), (41.2, BLADE_T + 1.2), (41.2, BLADE_T), (42.7, 0.7)]
        f = make_face(Polyline(*[(sd * u, BLADE_Y0 - BLADE_TRAVEL - 1.5, z0 - w) for u, w in prof], close=True))
        g += extrude(f, amount=BLADE_W + BLADE_TRAVEL + 4.0, dir=(0, 1, 0))
    wx, wy = WHEEL_XY
    g += cyl_z(STUD_D / 2 - 0.7, z0 - STUD_L, z0 + 0.01, wx, wy)
    if IsoThread is not None:
        g += Pos(wx, wy, z0 - STUD_L + 0.4) * IsoThread(major_diameter=STUD_D - 0.2, pitch=STUD_PITCH, length=STUD_L - 0.9,
                                                        external=True, end_finishes=("fade", "square"))
    # front face: the labyrinth groove, a dimple for each spring at both positions
    g -= cyl_z(LAB_R[1] + 0.3, z1 - 0.5, z1 + 1) - cyl_z(LAB_R[0] - 0.3, z1 - 1, z1 + 2)
    for a in ROT_SPRINGS:
        for r in (0.0, -90.0):
            g -= Rot(0, 0, a - r) * Pos(ROT_SPRING_R, 0, 0) * dimple((0.0, 0.0), z1, -1, 0.25)
    # rim: two notches (the lugs pass here when it is turned ROT_ENTRY), the stop peg's arc groove
    for a in LUG_ANG:
        g -= msector(ROT_R - LUG_CONE - 0.4, ROT_R + 1, a - ROT_ENTRY - LUG_SPAN / 2 - 3, a - ROT_ENTRY + LUG_SPAN / 2 + 3, z0 - 1, z1 + 1)
    pa, pz, pd = STOP_PEG["ang"], STOP_PEG["z"], STOP_PEG["d"]
    half = math.degrees((pd / 2 + 0.3) / ROT_R)
    g -= msector(STOP_PEG["r0"] - 0.4, ROT_R + 1, pa - half, pa + 90.0 + half, pz - pd / 2 - 0.3, pz + pd / 2 + 0.3)
    return Rot(0, 0, rho) * g


def stop_peg():
    """Radial peg, pressed through the body's left side face into the rotator's groove: it stops the back
    at landscape and at portrait."""
    pa, pz, pd = STOP_PEG["ang"], STOP_PEG["z"], STOP_PEG["d"]
    L = H - STOP_PEG["r0"]
    return Rot(0, 0, pa) * Pos(STOP_PEG["r0"] + L / 2, 0, pz) * Rot(0, 90, 0) * Cylinder(pd / 2, L - 0.05)


def graflok_blade(locked=True, rho=0.0):
    z0 = GF_Z0 - BLADE_T
    oy = 0.0 if locked else -BLADE_TRAVEL
    y0 = BLADE_Y0
    pts = [(-42.4, y0 + 3.0), (-39.4, y0), (39.4, y0), (42.4, y0 + 3.0), (42.4, y0 + BLADE_W), (-42.4, y0 + BLADE_W)]
    blade = Pos(0, 0, z0) * extrude(make_face(Polyline(*pts, close=True)), amount=BLADE_T)
    for tx in TONGUE_X:
        tng = make_face(Polyline((tx - 7, y0 + BLADE_W - 0.01), (tx + 7, y0 + BLADE_W - 0.01),
                                 (tx + 5.5, y0 + BLADE_W + 3.9), (tx - 5.5, y0 + BLADE_W + 3.9), close=True))
        blade += Pos(0, 0, z0) * extrude(tng, amount=BLADE_T)
    blade -= Pos(WHEEL_XY[0], WHEEL_XY[1] + BLADE_TRAVEL / 2, z0 - 1) * extrude(SlotCenterToCenter(BLADE_TRAVEL + 0.4, STUD_D + 0.4, rotation=90), amount=5)
    zf = GF_Z0
    for s in (-1, 1):
        cut = make_face(Polyline((s * 42.45, y0 - 1, zf - 0.95), (s * 43.5, y0 - 1, zf - 0.95), (s * 43.5, y0 - 1, z0 - 0.01),
                                 (s * 40.7, y0 - 1, z0 - 0.01), close=True))
        blade -= extrude(cut, amount=BLADE_W + 6, dir=(0, 1, 0))
    return Rot(0, 0, rho) * Pos(0, oy, 0) * blade


def graflok_wheel(rho=0.0):
    z1 = GF_Z0 - BLADE_T
    z0 = z1 - 5.0
    w = cyl_z(8.0, z0, z1)
    for i in range(24):
        w -= Rot(0, 0, i * 15) * Pos(8.3, 0, (z0 + z1) / 2) * Cylinder(0.7, 6)
    w -= cyl_z((STUD_D + 0.3) / 2, z0 - 1, z1 + 1)
    if IsoThread is not None:
        w += Pos(0, 0, z0) * IsoThread(major_diameter=STUD_D + 0.3, pitch=STUD_PITCH, length=5.0, external=False, end_finishes=("fade", "fade"))
    w = schamfer(w, w.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[0], 0.5)
    return Rot(0, 0, rho) * Pos(*WHEEL_XY, 0) * w


# ================================================================== Y PLATE (front face down)
SCALE_STEP = 5
YP_MID = (YP_Z0 + YP_Z1) / 2


def scale_dot(mm):
    return 2.6 if mm == 0 else (1.8 if mm % 10 == 0 else 1.2)


def y_plate(sy=0.0):
    p = slab(2 * YP_HALF, 2 * YP_HALF, YP_Z0, YP_Z1)
    p -= rect_loft(YP_Z0 - 0.5, opening_yplate(YP_Z0), YP_Z1 + 0.5, opening_yplate(YP_Z1))
    # tongues on the back, into the body's grooves
    for s in (-1, 1):
        p += prism_y(M.tongue_profile(s == FLEX_SIDE_Y), s, BODY_Z1, *Y_TONGUE)
    # horizontal ways on the front: grooves open at the photographer's right (-X), closed at the left
    x_end = X_TONGUE[1] + SHIFT
    for s in (-1, 1):
        p -= prism_x(M.groove_profile(s == FLEX_SIDE_X), s, YP_Z1, -YP_HALF - 1, x_end)
        if s == FLEX_SIDE_X:
            p -= prism_x(M.flex_slit(), s, YP_Z1, -YP_HALF + 6.0, x_end - 4.0)
    # rise rack: part of the plate, on its back; its teeth are the negative of the worm in the body
    p += M.rise_rack()
    # shift rack in the front, fixed: the panel's pinion runs in a band open at the -X edge
    qx, qy, qz = SHIFT_PIN
    L, c = SHIFT_RACK
    p -= box_at(-YP_HALF - 1, qx + SHIFT + M.PIN_TIP + 0.6, qy - PIN_W / 2 - 0.5, qy + PIN_W / 2 + 0.5, YP_Z1 - M.BAND, YP_Z1 + 1)
    p -= box_at(c - L / 2 - 0.02, c + L / 2 + 0.02, qy - RACK_W / 2 + PRESS_FIT / 2, qy + RACK_W / 2 - PRESS_FIT / 2, YP_Z1 - M.RACK_BACK - 0.05, YP_Z1 + 1)
    # detents: spring and bump in the back (rise), dimple in the front (shift)
    p -= detent_cut(RISE_DETENT, YP_Z0, +1)
    p += detent_bump(RISE_DETENT, YP_Z0, -1)
    p -= dimple(SHIFT_DETENT, YP_Z1, -1)
    # rise scale on the right side face (the body carries the red index); shift scale on the top face
    for mm in range(-int(RISE), int(RISE) + 1, SCALE_STEP):
        p -= Pos(-YP_HALF, -mm, YP_MID) * dot(scale_dot(mm), 0.6, "-x")
    for mm in range(-int(SHIFT), int(SHIFT) + 1, SCALE_STEP):
        p -= Pos(mm, YP_HALF, YP_MID) * dot(scale_dot(mm), 0.6, "+y")
    return Pos(0, sy, 0) * p


# ================================================================== LENS PANEL (front face down)
SCALE_R = HELI_OD / 2 + 5.5              # distance dots, just outside the helicoid's grip
NUM_R = SCALE_R + 6.0
DISTANCES = (10.0, 5.0, 3.0, 2.0, 1.0, 0.7, 0.5)


def focus_angle(d_m, f=65.0):
    """Angle of the helicoid's grip from infinity to distance d (m): the extension f^2 / (d - f), at
    HELI_ROT / HELI_TRAVEL degrees per mm. Clockwise from the front if FOCUS_DIR = 1 (negative here)."""
    d = d_m * 1000.0
    e = f * f / (d - f)
    return -FOCUS_DIR * e * HELI_ROT / HELI_TRAVEL


def label(d):
    return f"{d:g}"


def lens_panel(sx=0.0, sy=0.0, thread=True):
    z0, z1 = XP_Z0, XP_Z1
    p = slab(BODY, BODY, z0, z1)
    # light path: a rectangular funnel from the back to the helicoid's bore
    zt = z1 - PANEL_THREAD_L
    p -= rect_loft(z0 - 0.5, opening_panel(z0), zt, opening_panel(zt), r=6.0)
    p -= cyl_z(31.5, zt - 0.01, z1 + 1)
    hole, th = M.m65_female(z1, PANEL_THREAD_L, into=-1)
    p -= hole
    if thread and th is not None:
        p += th
    # tongues on the back, into the Y plate's grooves
    for s in (-1, 1):
        p += prism_x(M.tongue_profile(s == FLEX_SIDE_X), s, YP_Z1, *X_TONGUE)
    # shift pinion: pocket open to the back, bearing up to the top edge, where the knob sits
    qx, qy, qz = SHIFT_PIN
    p -= box_at(qx - M.PIN_TIP - 0.4, qx + M.PIN_TIP + 0.4, qy - PIN_W / 2 - 0.5, qy + PIN_W / 2 + 0.5, z0 - 1, qz + M.PIN_TIP + 0.4)
    p -= cyl_y(SHAFT_D / 2 + PIN_BORE_C, qy, H + 1, qx, qz)
    # shift detent: spring and bump in the back
    p -= detent_cut(SHIFT_DETENT, z0, +1)
    p += detent_bump(SHIFT_DETENT, z0, -1)
    # shift index on the top face, against the Y plate's dots
    p -= Pos(0, H, z0 + 2.2) * dot(2.4, 0.6, "+y")
    # distance scale around the helicoid: engraved on the face that prints on the bed
    p -= Pos(*polar(SCALE_R, 0.0), z1) * dot(2.6, 0.6)
    for dm in DISTANCES:
        a = focus_angle(dm)
        p -= Pos(*polar(SCALE_R, a), z1) * dot(1.4, 0.6)
        txt, _ = engraving(label(dm), 3.0, 0.4, 0.12)
        p -= Pos(*polar(NUM_R, a), z1) * txt
    return Pos(sx, sy, 0) * p


# ================================================================== PLUGS, VELVET
def plug_profile():
    """The groove's section, PRESS_FIT larger on the flanks: pressed in, it stays."""
    e = PRESS_FIT / 2
    return [(WAY_U_IN - e, 0.0), (WAY_U_MOUTH + e, 0.0), (WAY_U_MOUTH + WAY_D * WAY_TAN + e, WAY_D - 0.05), (WAY_U_IN - e, WAY_D - 0.05)]


def way_plug_y(side):
    """Plug pressed into the bottom end of a vertical groove: stops the fall, keeps the plate in."""
    return prism_y(plug_profile(), side, BODY_Z1, -H - 0.01, Y_TONGUE[0] - FALL)


def way_plug_x(side):
    """Plug pressed into the -X end of a horizontal groove: stops the shift, keeps the panel in."""
    return prism_x(plug_profile(), side, YP_Z1, -YP_HALF - 0.01, X_TONGUE[0] - SHIFT)


def velvet_body_outline():
    op = opening_body(BODY_Z1)
    outer = Pos(0, sum(V1_Y) / 2) * Rectangle(2 * V1_X, V1_Y[1] - V1_Y[0])
    return outer - RectangleRounded(2 * (op[0] + 0.3), 2 * (op[1] + 0.3), 3.0)


def velvet_yplate_outline():
    op = opening_yplate(YP_Z1)
    return Rectangle(2 * V2_X, 2 * V2_Y) - RectangleRounded(2 * (op[0] + 0.3), 2 * (op[1] + 0.3), 3.0)


def velvet_body():
    return Pos(0, 0, BODY_Z1) * extrude(velvet_body_outline(), amount=VELVET_T)


def velvet_yplate():
    return Pos(0, 0, YP_Z1) * extrude(velvet_yplate_outline(), amount=VELVET_T)


# ================================================================== BOUGHT (envelopes for checks and renders)
def helicoid_part(length=HELI_INF):
    z0 = HELI_Z0
    core = cyl_z(HELI_OD / 2 - 4, z0, z0 + length) - cyl_z(61.0 / 2, z0 - 1, z0 + length + 1)
    grip = cyl_z(HELI_OD / 2, z0 + HELI_GRIP[0], z0 + HELI_GRIP[1]) - cyl_z(HELI_OD / 2 - 5, z0, z0 + 13)
    for i in range(72):
        grip -= Rot(0, 0, i * 5) * Pos(HELI_OD / 2 + 0.35, 0, z0 + 6.5) * Cylinder(0.8, 8.6)
    front = cyl_z(HELI_OD / 2, z0 + HELI_GRIP[1] + 0.8, z0 + length) - cyl_z(HELI_OD / 2 - 4.5, z0, z0 + length + 1)
    rear = cyl_z(M65 / 2 - 0.2, z0 - PANEL_THREAD_L + 0.3, z0 + 0.01) - cyl_z(61.0 / 2, z0 - 7, z0 + 1)
    h = core + grip + front + rear
    h -= cyl_z(M65 / 2 + 0.1, z0 + length - STUB_L, z0 + length + 1)          # female M65 in the front
    return h


def lens_part(ffd=FFD):
    z = ffd
    rear = cyl_z(21, z - 21, z - 1)
    ring = cyl_z(21.5, z - BOARD_T - 3, z - BOARD_T) - cyl_z(16, z - BOARD_T - 4, z - BOARD_T + 1)
    sh = cyl_z(31.5, z, z + 19)
    shutter = sfillet(sh, sh.edges(), 1.5)
    front = cyl_z(28, z + 19, z + 42) - cyl_z(24.8, z + 36, z + 43)
    glass = (Pos(0, 0, z + 30) * Sphere(27)) & cyl_z(24.8, z + 19, z + 41)
    return rear + ring + shutter + front, glass


def rb67_back(rho=0.0):
    zf = GF_Z0 - 0.5
    nose = box_at(-61.0, POCKET_WALL_X - 0.3, POCKET_Y0 + 0.3, POCKET_Y1 - 0.3, zf, SEAT_Z)
    shell = Pos(0, 0, zf - 24) * Box(122, 108, 48)
    shell = sfillet(shell, shell.edges().filter_by(Axis.Z), 5.0)
    slide_handle = box_at(-66.0, -61.0, -36.0, 36.0, zf - 10.0, zf + 2.0)
    counter = box_at(-30, 30, 54, 58, zf - 40, zf - 8)
    lever = Pos(-44, 60, zf - 8) * Box(40, 5, 8)
    return Rot(0, 0, rho) * (nose + shell + slide_handle + counter), Rot(0, 0, rho) * lever


# ================================================================== DOT INLAYS (renders; paint in print)
def _dot_fill(d, axis):
    return orient(Pos(0, 0, -0.6) * Cylinder(d / 2, 0.6, align=Z_UP), axis)


def dot_inlays(sx=0.0, sy=0.0):
    """Paint fills of the dots and engravings, as (name, shape, material): red for zeros, infinity and
    indexes; white for the scales. The name stays unpainted, as on View 1."""
    red, white = [], []
    red.append(Pos(-H, 0.0, BODY_Z1 - 2.2) * _dot_fill(2.4, "-x"))
    _, dxy = name_plate()
    red.append(Pos(dxy[0], dxy[1], BODY_Z1) * _dot_fill(2.6, "+z"))
    yv = Pos(0, sy, 0)
    for mm in range(-int(RISE), int(RISE) + 1, SCALE_STEP):
        (red if mm == 0 else white).append(yv * Pos(-YP_HALF, -mm, YP_MID) * _dot_fill(scale_dot(mm), "-x"))
    for mm in range(-int(SHIFT), int(SHIFT) + 1, SCALE_STEP):
        (red if mm == 0 else white).append(yv * Pos(mm, YP_HALF, YP_MID) * _dot_fill(scale_dot(mm), "+y"))
    mv = Pos(sx, sy, 0)
    red.append(mv * Pos(0, H, XP_Z0 + 2.2) * _dot_fill(2.4, "+y"))
    red.append(mv * Pos(*polar(SCALE_R, 0.0), XP_Z1) * _dot_fill(2.6, "+z"))
    for dm in DISTANCES:
        a = focus_angle(dm)
        white.append(mv * Pos(*polar(SCALE_R, a), XP_Z1) * _dot_fill(1.4, "+z"))
    # the helicoid's grip gets a painted index at infinity (top)
    red.append(mv * Pos(0, HELI_OD / 2 + 0.3, HELI_Z0 + 6.5) * orient(Cylinder(1.1, 0.6, align=Z_UP), "+y"))
    red.append(mv * Pos(*polar((M.SEAT_R + MOUNT_R) / 2, 0.0), BOARD_Z1) * _dot_fill(2.2, "+z"))
    red.append(mv * Pos(*polar(BOARD_R - 2.6, 0.0), BOARD_Z1) * _dot_fill(2.2, "+z"))
    return [("dots_red", Compound(red), "red"), ("dots_white", Compound(white), "white_ink")]


def scale_numerals(sx=0.0, sy=0.0):
    """White fill of the distance numerals (renders)."""
    out = []
    for dm in DISTANCES:
        a = focus_angle(dm)
        txt, _ = engraving(label(dm), 3.0, 0.4, 0.12)
        out.append(Pos(sx, sy, 0) * Pos(*polar(NUM_R, a), XP_Z1 - 0.02) * txt)
    return Compound(out)
