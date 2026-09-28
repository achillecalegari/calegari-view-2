"""View 2 mechanisms: the parts that replace View 1's hardware. They are real parts (the mount, the
board, the pinion, the knob, the rack, the washer) or exact slices of real parts (thread, dovetails, Arca),
so the test plate proves the camera before the body is printed.

Every part is built in its print orientation's frame unless noted: +Z up from the bed.
"""
import math
from functools import lru_cache
from build123d import *
from params import *
from util import *
try:
    from bd_warehouse.thread import Thread
except Exception:  # pragma: no cover
    Thread = None


# ------------------------------------------------------------------ M65 thread in the lens panel
def m65_female(z_face, length, into=-1):
    """Printed M65 x 1 female thread, from a face into the part (into=-1: toward -Z)."""
    z0 = z_face - length if into < 0 else z_face
    hole = cyl_z((M65 + M65_FIT) / 2, z0 - 0.01, z0 + length + 0.01)
    th = None
    if IsoThread is not None:
        th = Pos(0, 0, z0) * IsoThread(major_diameter=M65 + M65_FIT, pitch=1.0, length=length, external=False,
                                       end_finishes=("fade", "fade"))
    return hole, th


def thread_coupon():
    """A 10 mm ring of the lens panel with its M65 female thread: the helicoid's rear must screw in by hand."""
    t = 10.0
    r = cyl_z(45.0, 0, t) - cyl_z(31.5, -1, t + 1)
    hole, th = m65_female(0.0, PANEL_THREAD_L, into=+1)        # thread from the bed face, like the panel (front down)
    r -= hole
    if th is not None:
        r += th
    r = schamfer(r, [e for e in r.edges().filter_by(GeomType.CIRCLE) if e.radius > 44.9], 0.6)
    return r


# ------------------------------------------------------------------ lens mount with bayonet (prints stub down)
# The mount ring screws into the helicoid's front and is flush with it: helicoid and mount read as one
# barrel. The board goes in turned LOCK_TURN back: notches in the back of its rim pass the mount's three
# lugs, the turn puts the lugs in the rim groove behind the whole front of the rim, and the detent clicks.
# The lugs' ends of groove are the stop, so the shutter always ends upright.
Z_H = HELI_Z0 + HELI_INF                  # helicoid front face at infinity
MOUNT_BORE = 29.5
SEAT_R = BOARD_R + 0.3                    # board seat recess
GROOVE_Z = (BOARD_Z1 - 2.2, BOARD_Z1 - 1.2)   # the board's rim groove (lugs run in it)
LUG_IN = 1.25                             # lug depth, inward from the seat wall
DET_ANG = 60.0                            # detent position (degrees), between two lugs
PLATEAU_R = 29.2                          # the lens sits on a plateau: its height follows the lens's flange distance


def mount(thread=True):
    """Male M65 stub into the helicoid front, ring with the bayonet for the round board, and a flexure
    detent that clicks into the board at the locked position. Assembly coordinates."""
    z0, z1 = Z_H, BOARD_Z1
    a = cyl_z(MOUNT_R, z0, z1) - cyl_z(MOUNT_BORE, z0 - 1, z1 + 1)
    a -= cyl_z(SEAT_R, BOARD_Z1 - BOARD_T, z1 + 1)
    a = sfillet(a, [e for e in a.edges().filter_by(GeomType.CIRCLE) if e.radius > MOUNT_R - 0.1 and e.center().Z > z1 - 0.1], 0.8)
    # three lugs inward from the seat wall, in the board's rim groove; underside chamfered (no overhang)
    for c in BAYONET_LUGS:
        lug = ring_sector(SEAT_R - LUG_IN, SEAT_R + 0.2, c - BAYONET_SPAN / 2, c + BAYONET_SPAN / 2, GROOVE_Z[0] + 0.1, GROOVE_Z[1] - 0.1)
        lug = schamfer(lug, [e for e in lug.edges().filter_by(GeomType.CIRCLE)
                             if abs(e.radius - (SEAT_R - LUG_IN)) < 0.05 and e.center().Z < GROOVE_Z[0] + 0.2], 0.6)
        a += lug
    # detent: an arc beam in the seat wall with a bump that drops into a notch in the board rim
    beam_r0, beam_r1 = SEAT_R, SEAT_R + 1.2
    a -= ring_sector(beam_r1, beam_r1 + 1.0, DET_ANG - 22, DET_ANG + 8, GROOVE_Z[1] + 0.1, z1 + 1)
    a -= ring_sector(beam_r0 - 0.1, beam_r1 + 1.0, DET_ANG + 8, DET_ANG + 9, GROOVE_Z[1] + 0.1, z1 + 1)   # free end
    bump = Pos(*polar(SEAT_R - 0.15, DET_ANG), GROOVE_Z[1] + 0.2) * Rot(0, 0, -DET_ANG) * Rot(0, 0, 45) * Box(1.1, 1.1, z1 - GROOVE_Z[1] - 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    a += bump
    # index dot at the top (red): the board's dot meets it when locked
    a -= Pos(*polar((SEAT_R + MOUNT_R) / 2, 0.0), z1 - 0.6) * Cylinder(1.1, 1.4, align=Z_UP)
    # male M65 stub into the helicoid front
    stub = cyl_z(M65 / 2 - (0.6 if thread else 0.0), z0 - STUB_L, z0 + 0.1) - cyl_z(MOUNT_BORE, z0 - STUB_L - 1, z0 + 1)
    if thread and IsoThread is not None:
        stub += Pos(0, 0, z0 - STUB_L + 0.3) * IsoThread(major_diameter=M65 - 0.25, pitch=1.0, length=STUB_L - 0.8,
                                                         external=True, end_finishes=("fade", "square"))
    return a + stub


def board(ffd=FFD):
    """Round lens board, 70 mm: Copal 0 hole, rim groove for the three lugs, entry notches, detent notch.
    The rim always sits in the mount; the plateau that carries the lens is raised or sunk so that the
    lens's flange lands at its own flange focal distance `ffd` (-2.5 to +8 mm from the reference lens).
    Modelled locked (assembly coordinates); it goes in turned back by LOCK_TURN."""
    d = ffd - FFD
    assert -2.5 <= d <= 8.0, "outside the helicoid's range: see docs/calibration.md"
    z0, z1 = BOARD_Z1 - BOARD_T, BOARD_Z1
    b = cyl_z(BOARD_R, z0, z1)
    if d > 0.05:
        b += cyl_z(PLATEAU_R + 1.3, z1 - 0.01, z1 + d)
    elif d < -0.05:
        b -= cyl_z(PLATEAU_R, ffd, z1 + 1)
        b += cyl_z(PLATEAU_R, ffd - BOARD_T, ffd)
    b -= cyl_z(COPAL0_HOLE / 2, ffd - BOARD_T - 5, max(z1, ffd) + 1)
    gr0 = SEAT_R - LUG_IN - 0.25
    for c in BAYONET_LUGS:
        # groove from the entry position to the locked one (its end is the stop)
        b -= ring_sector(gr0, BOARD_R + 1, c - BAYONET_SPAN / 2 - LOCK_TURN - 1.0, c + BAYONET_SPAN / 2 + 0.3, GROOVE_Z[0], GROOVE_Z[1])
        # entry notch through the back of the rim, at the entry position: the lug passes it going in;
        # the rim in front of the groove stays whole and holds the board
        b -= ring_sector(gr0, BOARD_R + 1, c - BAYONET_SPAN / 2 - LOCK_TURN - 1.0, c + BAYONET_SPAN / 2 - LOCK_TURN + 1.0, z0 - 1, GROOVE_Z[0] + 0.01)
    # detent notch: a V in the rim, where the mount's bump drops in at lock
    b -= Pos(*polar(BOARD_R + 0.2, DET_ANG), GROOVE_Z[1]) * Rot(0, 0, -DET_ANG) * Rot(0, 0, 45) * Box(1.3, 1.3, z1 - GROOVE_Z[1] + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    b -= Pos(*polar(BOARD_R - 2.6, 0.0), z1 - 0.6) * Cylinder(1.1, 1.4, align=Z_UP)      # index dot (red)
    b = sfillet(b, [e for e in b.edges().filter_by(GeomType.CIRCLE) if e.radius > BOARD_R - 0.1 and e.center().Z > z1 - 0.1], 0.5)
    return b


# ------------------------------------------------------------------ rack and pinion
PIN_R = MOD * PIN_Z / 2
PIN_TIP = PIN_R + MOD * (1 + PIN_X)
CENTRE_TO_PITCH = PIN_R + PIN_X * MOD      # pinion centre to the rack pitch line


KNOB_BORE = 10.0                           # shaft length inside the knob
SNAP_FROM_END = 6.2                        # the shaft's snap groove starts this far from its end


def knob_end(s, top):
    """The end of a round shaft along +Z that ends at `top`: D flat for the knob and a ring groove for the
    knob's snap tabs."""
    s -= box_at(SHAFT_D / 2 - SHAFT_FLAT, SHAFT_D, -SHAFT_D, SHAFT_D, top - KNOB_BORE - 1.5, top + 1)
    zg = top - SNAP_FROM_END
    s -= cyl_z(SHAFT_D / 2 + 1, zg, zg + 1.2) - cyl_z(SHAFT_D / 2 - 0.5, zg - 1, zg + 2)
    s -= cyl_z(SHAFT_D / 2 + 1, zg + 1.2, zg + 1.7) - Pos(0, 0, zg + 1.2) * Cone(SHAFT_D / 2 - 0.5, SHAFT_D / 2, 0.5, align=Z_UP)
    return schamfer(s, s.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1], 0.5)


def pinion(shaft_len):
    """Pinion with its shaft, printed standing (teeth on the bed): D flat for the knob, a ring groove for
    the knob's snap tabs near the end."""
    g = extrude(poly_face(gear_profile(MOD, PIN_Z, PIN_X, PRESS)), amount=PIN_W)
    g = schamfer(g, g.edges().filter_by(Plane.XY).group_by(Axis.Z)[0], 0.3)   # elephant foot
    s = cyl_z(SHAFT_D / 2, PIN_W - 0.01, PIN_W + shaft_len)
    return g + knob_end(s, PIN_W + shaft_len)


def knob():
    """Leica-style knob, printed crown down: D bore for the shaft, two in-plane flexure tabs that snap
    into the shaft's groove (no pin, no grub, no nut). Built crown at z = 0, skirt up; axis +Z."""
    d, h = KNOB_D, KNOB_H
    k = Cylinder(d / 2, h, align=Z_UP)
    k = schamfer(k, k.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[0], 1.0)     # crown
    k = schamfer(k, k.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1], 0.4)
    L = h - 4.6
    for i in range(30):
        k -= Rot(0, 0, i * 12) * Pos(d / 2 + 0.25, 0, 3.4 + L / 2) * Cylinder(0.75, L)
    k -= cyl_z(d / 2 + 1, 3.4, 3.9) - cyl_z(d / 2 - 0.35, 3.0, 4.3)                      # hairline
    # D bore from the skirt, 10 deep
    bore = cyl_z(SHAFT_D / 2 + 0.12, h - 10.0, h + 1)
    bore -= box_at(SHAFT_D / 2 - SHAFT_FLAT + 0.12, SHAFT_D, -SHAFT_D, SHAFT_D, h - 11, h + 2)
    k -= bore
    k -= Pos(0, 0, h - 0.01) * Cone(SHAFT_D / 2 + 0.8, SHAFT_D / 2 + 0.12, 0.6, align=(Align.CENTER, Align.CENTER, Align.MAX))
    # snap: two arc slots leave two beams around the bore; each beam has a bump that drops into the groove
    zs = h - KNOB_BORE + SNAP_FROM_END - 0.05       # the bumps sit in the shaft's groove when the knob is home
    for c in (90.0, 270.0):
        k -= ring_sector(SHAFT_D / 2 + 1.1, SHAFT_D / 2 + 1.9, c - 60, c + 60, zs - 3.0, h + 1)
        k += ring_sector(SHAFT_D / 2 - 0.45, SHAFT_D / 2 + 0.2, c - 12, c + 12, zs - 1.1, zs)
    k -= Pos(0, -(d / 2 - 4.2), -0.01) * Cylinder(1.2, 0.61, align=Z_UP)                  # red dot on the crown
    return k


def rack(length):
    """Rack bar, printed lying on its side (teeth in the bed plane). Built: length along X, teeth +Y,
    face width along Z (0..RACK_W), pitch line at y = 0."""
    r = extrude(poly_face(rack_profile(MOD, length, RACK_BASE, PRESS)), amount=RACK_W)
    return schamfer(r, r.edges().filter_by(Axis.Z), 0.3)


def drive_layout():
    """Depths into the pinion plate from its face (w): rack pitch line and pinion centre. The rack's tips
    stop TIP_CLEAR short of the face; its back sits in a slot in the other plate, across the gap."""
    w_pl = -TIP_CLEAR - MOD
    return w_pl, w_pl + CENTRE_TO_PITCH


RACK_BACK = TIP_CLEAR + MOD + 1.25 * MOD + RACK_BASE - GAP      # rack slot depth in the rack plate: 4.75
BAND = PIN_TIP - (-TIP_CLEAR - MOD + CENTRE_TO_PITCH) - GAP + 0.25   # pinion band depth in the rack plate: 1.75


def pinion_block():
    """Test rig: the slice of the body where the rise pinion lives, printed like the body (face on the bed,
    w up). The shaft runs along X; the rack runs along Y in the carrier, which rides on the face on two
    rails as high as the gap. The drag comes from the TPU washer under the knob, as on the camera."""
    L, W, T = 44.0, 44.0, 20.0
    w_pl, w_c = drive_layout()
    blk = box_at(-L / 2, L / 2, -W / 2, W / 2, 0, T)
    blk = sfillet(blk, blk.edges().filter_by(Axis.Z), 2.0)
    blk -= box_at(-PIN_W / 2 - 0.5, PIN_W / 2 + 0.5, -PIN_TIP - 0.4, PIN_TIP + 0.4, -1, w_c + PIN_TIP + 0.4)
    blk -= cyl_x(SHAFT_D / 2 + PIN_BORE_C, PIN_W / 2, L / 2 + 1, 0, w_c)          # bearing, knob side
    blk -= cyl_x(SHAFT_D / 2 + PIN_BORE_C, -L / 2 + 6, -PIN_W / 2, 0, w_c)        # blind bearing, far side
    return blk


def rack_carrier(length=70.0):
    """Test rig: a slice of the Y plate with the rack slot and the pinion band, and two rails as high as the
    gap that ride on the block's face. Built face down (z = 0 is the face that meets the block, the rails
    below it): it prints rails up."""
    W = 34.0
    c = box_at(-W / 2, W / 2, -length / 2, length / 2, 0, 9.0)
    c = sfillet(c, c.edges().filter_by(Axis.Y), 1.0)
    c -= box_at(-PIN_W / 2 - 0.5, PIN_W / 2 + 0.5, -length / 2 - 1, length / 2 + 1, -1, BAND)
    c -= box_at(-RACK_W / 2 + PRESS_FIT / 2, RACK_W / 2 - PRESS_FIT / 2, -length / 2 + 4, length / 2 + 1, -1, RACK_BACK + 0.05)
    for s in (-1, 1):
        c += box_at(s * (W / 2 - 3.0), s * (W / 2), -length / 2, length / 2, -GAP, 0.01)
    return c


def drag_washer():
    """TPU wave washer, printed flat: a 0.8 mm ring with three bumps on each side, staggered. Squeezed, the
    ring bends between the bumps: a soft spring with an even drag, not a block of rubber."""
    d_in, d_out, t = DRAG_WASHER
    ring_t = 0.8
    bump = (t - ring_t) / 2
    w = cyl_z(d_out / 2, bump, bump + ring_t) - cyl_z(d_in / 2, -1, t + 1)
    rm = (d_in + d_out) / 4
    for i in range(3):
        for z0, off in ((0.0, 0.0), (bump + ring_t - 0.01, 60.0)):
            a = math.radians(i * 120 + off)
            w += Pos(rm * math.cos(a), rm * math.sin(a), z0) * Cylinder(1.4, bump + 0.01, align=Z_UP)
    return w


def block_shaft_len():
    """Shaft length for the test block: from the pinion face to the knob, which rides KNOB_OFF off the face."""
    return 44.0 / 2 + KNOB_OFF + KNOB_BORE - PIN_W / 2


# ------------------------------------------------------------------ rise worm (self-locking)
WORM_R = WORM_D / 2
WORM_LEAD = math.pi * MOD                  # single start: pi mm per turn
WORM_Y0 = WRACK[0] - RISE - 2.0            # thread from here (assembly y) ...
WORM_Y1 = WRACK[1] + RISE + 2.0            # ... to just above the rack's highest point
WORM_PIN = (3.0, 4.0)                      # bottom pin: diameter, length; it sits in the plug, its end the thrust bearing
WORM_BORE = WORM_R + MOD + 0.3             # the worm's bore in the body, straight up from the bottom face: it goes in from below

# the miter pair: the worm's gear on its top, the knob's gear on a shaft through the right side face.
# Their axes meet at (WORM_X, BEVEL_Y, WORM_Z); both gears stay inside the worm's own envelope (r 5.1).
BEVEL_R = BEVEL_M * BEVEL_Z / 2            # pitch radius at the heel
BEVEL_K = 1 - BEVEL_B * math.sin(math.radians(45)) / BEVEL_R   # toe / heel
BEVEL_BACK = 1.5                           # the back cone runs this far behind the heel's pitch circle
BEVEL_J = 3.5                              # the thread's end to the worm gear's heel: back cone and the cone to the journal
BEVEL_Y = WORM_Y1 + BEVEL_J + BEVEL_R      # where the axes meet: the knob's height on the side
assert abs(BEVEL_Y - HANDLE_H / 2) < 0.01    # the middle of the side face, body and handle post together
BEVEL_PHASE = 15.0                         # half a tooth: the knob's gear meets the worm's in a gap
COLLAR_L = 3.0                               # the collar pressed into the side bore holds the knob's gear in
_T20 = math.tan(math.radians(20))


def worm_thread(length, bl):
    """Module 1 worm along +Z from z = 0: straight-sided axial profile (ZA), teeth `bl` thinner than
    nominal (negative: fatter, for cutting the rack)."""
    core = cyl_z(WORM_R - 1.25 * MOD + 0.02, 0, length)
    th = Thread(apex_radius=WORM_R + MOD, apex_width=math.pi / 2 - 2 * _T20 - bl, root_radius=WORM_R - 1.25 * MOD,
                root_width=math.pi / 2 + 2 * 1.25 * _T20 - bl, pitch=WORM_LEAD, length=length, end_finishes=("fade", "fade"))
    return core + th


def miter():
    """Straight miter gear: heel pitch circle at z = 0, the teeth ruled toward the apex at z = BEVEL_R and
    ending on the back cone (45 degrees, through the heel's pitch circle), as on a real bevel gear: behind
    it only the core, inside the mating gear's reach. The core narrows along the back cone to BEVEL_BACK,
    then opens at 45 degrees to the journal. Standing, heel down, nothing overhangs past 45 degrees."""
    R, k, L0 = BEVEL_R, BEVEL_K, BEVEL_BACK
    pts = gear_profile(BEVEL_M, BEVEL_Z, BEVEL_X)
    s0 = (R + L0) / R
    heel = Plane.XY.offset(-L0) * poly_face([(x * s0, y * s0) for x, y in pts])
    toe = Plane.XY.offset(R * (1 - k)) * poly_face([(x * k, y * k) for x, y in pts])
    g = loft([heel, toe], ruled=True)
    g &= Pos(0, 0, -R) * Cone(0.01, 2 * R, 2 * R, align=Z_UP)                  # r <= R + z: the back cone
    rj = WORM_BORE - 0.3
    g += Pos(0, 0, -L0 - (rj - (R - L0))) * Cone(rj, R - L0, rj - (R - L0) + 0.01, align=Z_UP)
    return g


def worm_part(y0=WORM_Y0, y1=WORM_Y1):
    """The rise worm, printed standing (thread axis vertical): bottom pin, thread from y0 to y1, a journal
    that runs in the bore, the miter gear and a small boss on its toe (it stops the worm lifting against
    the knob's shaft). Built along +Z, z = 0 at the pin's end; assembly y = y0 - pin + z."""
    pd, pl = WORM_PIN
    base = y0 - pl
    w = cyl_z(pd / 2, 0, pl + 0.01)
    w += Pos(0, 0, pl) * worm_thread(y1 - y0, WORM_BL)
    zh = y1 + BEVEL_J - base
    zb = zh - BEVEL_BACK - (WORM_BORE - 0.3 - (BEVEL_R - BEVEL_BACK))
    w += cyl_z(WORM_BORE - 0.3, y1 - base - 0.01, zb + 0.01)
    w += Pos(0, 0, zh) * miter()
    zt = zh + BEVEL_R * (1 - BEVEL_K)
    w += cyl_z(1.4, zt - 0.01, zh + BEVEL_R - 1.5)
    return schamfer(w, w.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[0], 0.3)


def knob_gear():
    """The knob's shaft, printed standing, gear down: the miter gear with a stub toward the axes' meeting
    point, a journal in the side bore, then the D shaft out through the collar into the knob. Built
    along +Z with the heel at z = 0 and the gear toward -Z (the side face is at z = heel - side)."""
    side = (WORM_X - BEVEL_R) - (-H)                      # heel to the side face
    g = Rot(180, 0, 0) * (miter() + cyl_z(1.2, BEVEL_R * (1 - BEVEL_K) - 0.01, BEVEL_R + 1.5))
    zb = BEVEL_BACK + (WORM_BORE - 0.3 - (BEVEL_R - BEVEL_BACK))
    j = cyl_z(WORM_BORE - 0.3, zb - 0.01, side - COLLAR_L - 0.2)
    top = side + KNOB_OFF + KNOB_BORE
    s = knob_end(cyl_z(SHAFT_D / 2, side - COLLAR_L - 0.21, top), top)
    return g + j + s


def knob_gear_place(theta=0.0):
    """Knob gear frame -> assembly: axis -X out of the right side face; turned with the worm (1:1)."""
    return Pos(WORM_X - BEVEL_R, BEVEL_Y, WORM_Z) * Rot(0, -90, 0) * Rot(0, 0, theta - BEVEL_PHASE)


def collar():
    """Ring pressed into the side bore, flush with the face, under the knob: it keeps the knob's gear in.
    Built along +Z, z 0..COLLAR_L."""
    return cyl_z(WORM_BORE + PRESS_FIT / 2, 0, COLLAR_L) - cyl_z(SHAFT_D / 2 + PIN_BORE_C, -1, COLLAR_L + 1)


PLUG_BAND = 6.0                            # the long plugs press only over their bottom band; above it they slide


def worm_seat(y0, pin_end, cut=None):
    """Round plug from y0 up to just under the worm's thread, with the pin's hole: the pin's end bears on
    the hole's floor. It presses over its bottom band and slides above it. Assembly coordinates; `cut`
    is taken out of it (the rack's channel)."""
    pd, pl = WORM_PIN
    yt = pin_end + pl - 0.3
    cyl = lambda r, a, b: Pos(WORM_X, (a + b) / 2, WORM_Z) * Rot(90, 0, 0) * Cylinder(r, b - a)
    p = cyl(WORM_BORE - 0.1, y0, yt) + cyl(WORM_BORE + PRESS_FIT / 2, y0, y0 + PLUG_BAND)
    p -= cyl(pd / 2 + 0.15, pin_end, pin_end + pl + 0.2)
    return p - cut if cut is not None else p


def _channel(y0, y1, grow=0.0):
    return box_at(RACK_CH[0] - grow, RACK_CH[1] + grow, y0, y1, RACK_CH[2] - grow, BODY_Z1 + 1)


def worm_plug():
    """Pressed into the worm's bore from below right after the worm: its seat carries the worm's pin (the
    thrust bearing). Cut back where the rack's channel crosses the bore, so the Y plate's rack slides up
    past it. Assembly coordinates."""
    return worm_seat(-H, WORM_Y0 - WORM_PIN[1], _channel(-H - 1, 0.0, PRESS_FIT / 2))


def rack_plug():
    """Pressed into the rack's channel from below after the Y plate: it fills the channel up to the rack's
    lowest point, around the worm's thread. It presses over its bottom band and slides above it.
    Assembly coordinates."""
    yr = WRACK[0] - FALL - 0.4
    yw = WORM_Y0 - 0.3
    x0, x1, z0 = RACK_CH
    ch = box_at(x0 + 0.1, x1 - 0.1, -H, yr, z0 + 0.1, BODY_Z1 - 0.1)
    ch += _channel(-H, -H + PLUG_BAND, PRESS_FIT / 2) - box_at(x0 - 1, x1 + 1, -H - 1, -H + PLUG_BAND + 1, BODY_Z1, BODY_Z1 + 2)
    return ch - Pos(WORM_X, (yw + yr + 1) / 2, WORM_Z) * Rot(90, 0, 0) * Cylinder(WORM_BORE, yr + 1 - yw)


def worm_place(theta=0.0):
    """Worm frame -> assembly: axis +Y at (WORM_X, WORM_Z), turned theta degrees (right hand: turning it
    clockwise seen from above raises the rack)."""
    return Pos(WORM_X, WORM_Y0 - WORM_PIN[1], WORM_Z) * Rot(-90, 0, 0) * Rot(0, 0, theta)


RACK_X = (WORM_X + WORM_R - MOD + 0.25, WORM_X + WORM_R + 1.25 * MOD + RACK_BASE)   # tips .. base, on the worm's inboard side
RACK_ZS = (WORM_Z - WORM_R - MOD - 0.4, YP_Z0 + 0.01)                              # across the worm, up to the Y plate
RACK_CH = (RACK_X[0] - 0.4, RACK_X[1] + 0.5, RACK_ZS[0] - 0.4)                   # the rack's channel in the body: x0, x1, z0


@lru_cache(maxsize=None)
def rise_rack(y0=WRACK[0], y1=WRACK[1]):
    """Rise rack teeth on the Y plate's back (plate coordinates, the plate at zero). A worm that turns is
    the same surface as a worm that slides along its axis, so the rack that meshes with it everywhere
    across its face is simply the negative of the worm: a slice of a nut, cut by a worm WORM_BL fatter
    than the real one. In each printed layer the section is the worm's own tooth profile."""
    blk = box_at(RACK_X[0], RACK_X[1], y0, y1, *RACK_ZS)
    k0 = math.floor((y0 - 2 * WORM_LEAD - WORM_Y0) / WORM_LEAD)
    ys = WORM_Y0 + k0 * WORM_LEAD                  # in phase with the real worm's thread
    hob = worm_thread((y1 - y0) + 4 * WORM_LEAD, -WORM_BL)
    return blk - Pos(WORM_X, ys, WORM_Z) * Rot(-90, 0, 0) * hob


RIG_N = 13                                 # the rig's worm starts this many leads above the camera's: in phase with the rack
RIG_Y = (WORM_Y0 + RIG_N * WORM_LEAD - WORM_PIN[1] - 6.0, BEVEL_Y + 9.0)   # the rig: the top of the body's right side


def test_worm():
    """The rise worm, cut short for the rig: the same top (journal, miter), a shorter thread."""
    return worm_part(WORM_Y0 + RIG_N * WORM_LEAD, WORM_Y1)


def test_worm_place(theta=0.0):
    return Pos(WORM_X, WORM_Y0 + RIG_N * WORM_LEAD - WORM_PIN[1], WORM_Z) * Rot(-90, 0, 0) * Rot(0, 0, theta)


def rise_cuts(y_bottom):
    """The rise drive's room in the body (assembly coordinates): the worm's bore up from y_bottom, the
    side bore for the knob's gear and the collar, the rack's channel (open to the front)."""
    c = Pos(WORM_X, (y_bottom - 1 + BEVEL_Y) / 2, WORM_Z) * Rot(90, 0, 0) * Cylinder(WORM_BORE, BEVEL_Y - y_bottom + 1)
    x1 = WORM_X + 3.0                     # past the stub on the knob's gear
    c += Pos((-H - 1 + x1) / 2, BEVEL_Y, WORM_Z) * Rot(0, 90, 0) * Cylinder(WORM_BORE, x1 + H + 1)
    return c


def worm_block():
    """Test rig, assembly coordinates: the top of the body's right side around the drive (the worm's
    bore, the miter pair's room, the side bore, the rack's channel). It prints like the body, front face
    down; the worm goes in from below, a short plug closes the bore, then the rack slice slides up the
    channel past the plug."""
    y0, y1 = RIG_Y
    X0, X1 = -H, -60.0
    blk = box_at(X0, X1, y0, y1, WORM_Z - WORM_R - 4.0, BODY_Z1)
    blk -= box_at(RACK_CH[0], RACK_CH[1], y0 - 1, WRACK[1] + RISE + 0.5, RACK_CH[2], BODY_Z1 + 1)   # the slice goes in from below
    blk -= rise_cuts(y0)
    return sfillet(blk, blk.edges().filter_by(Axis.Y), 1.0)


def rig_plug():
    """The rig's bottom plug: the worm's pin seat, like the camera's."""
    return worm_seat(RIG_Y[0], RIG_Y[0] + 6.0, _channel(RIG_Y[0] - 1, RIG_Y[1], PRESS_FIT / 2))


def rack_slice():
    """Test rig, assembly coordinates: four teeth of the Y plate's rise rack on a slice of the plate, with
    two rails as high as the gap that ride on the block's face. It prints like the Y plate, plate down."""
    ya = WORM_Y0 + (RIG_N + 3) * WORM_LEAD
    yb = ya + 4 * WORM_LEAD
    part = rise_rack(ya, yb) + box_at(-85.0, -60.0, ya - 8, yb + 8, YP_Z0 - 0.01, YP_Z0 + 3.0)
    for x0, x1 in ((-85.0, -82.0), (-63.0, -60.0)):
        part += box_at(x0, x1, ya - 8, yb + 8, BODY_Z1 + 0.01, YP_Z0 + 0.01)
    return part


# ------------------------------------------------------------------ dovetail ways
def groove_profile(flex):
    """Groove cross-section (u, w): u outward, w into the fixed part from its face."""
    u0, um, d = WAY_U_IN, WAY_U_MOUTH, WAY_D
    return [(u0, -1.0), (um, -1.0), (um, 0.0), (um + d * WAY_TAN, d), (u0, d)]


def tongue_profile(flex):
    """Tongue cross-section on the moving plate (u, w), from the plate's back (w = -GAP) to the groove floor."""
    c = -WAY_INTERF if flex else WAY_C_RIGID
    off = c / math.cos(math.radians(30))
    u0 = WAY_U_IN + WAY_C_IN
    um = WAY_U_MOUTH - off
    return [(u0, -GAP - 0.5), (um - GAP * WAY_TAN, -GAP - 0.5), (um, 0.0), (um + WAY_D * WAY_TAN - 0.05, WAY_D), (u0, WAY_D)]


def flex_slit():
    """The slit behind the flexure beam: parallel to the outer flank, FLEX_T behind it, FLEX_DEPTH deep."""
    um, d, t = WAY_U_MOUTH, FLEX_DEPTH, FLEX_T / math.cos(math.radians(30))
    a = um + t
    return [(a, -1.0), (a + FLEX_SLIT, -1.0), (a + FLEX_SLIT + d * WAY_TAN, d), (a + d * WAY_TAN, d)]


def way_coupon_fixed(flex, length=40.0):
    """Slice of the body (or Y plate) with one groove, printed face down: built with the face on the bed
    (z = 0) and w going up."""
    blk = box_at(52.0, 74.0, -length / 2, length / 2, 0, 12.0)
    pr = lambda pts: extrude(Plane.XZ * poly_face([(u, w) for u, w in pts]), amount=length / 2 + 1, both=True)
    blk -= pr(groove_profile(flex))
    if flex:
        blk -= pr(flex_slit())
    return blk


def way_coupon_tongue(flex, length=40.0):
    """Slice of the moving plate with its tongue, printed plate front down: built with the tongue up.
    Coordinates: w from the fixed face as in the profiles, mirrored so the plate is on the bed."""
    plate = box_at(52.0, 74.0, -length / 2, length / 2, -GAP - 10.0, -GAP)
    t = extrude(Plane.XZ * poly_face(tongue_profile(flex)), amount=length / 2, both=True)
    return plate + t                   # plate front down (w = -GAP - 10), tongue up: as it prints


# ------------------------------------------------------------------ Arca-Swiss profile
def arca_profile():
    """38 mm Arca dovetail: 32 mm neck, 45 degree flanks, 38 mm clamp face. (u across, v away from the camera)"""
    return [(-16, -0.5), (16, -0.5), (16, 2.0), (19, 5.0), (19, 9.0), (-19, 9.0), (-19, 5.0), (-16, 2.0)]


def arca_coupon(length=50.0):
    """50 mm of the camera's printed Arca rail on a slice of the body's bottom, printed as on the body."""
    base = box_at(-24, 24, -length / 2, length / 2, 0, 8.0)
    rail = extrude(Plane.XZ * poly_face([(u, 8.0 + v) for u, v in arca_profile()]), amount=length / 2, both=True)
    return base + rail


def shrink_gauge():
    g = extrude(Rectangle(100, 100) - Rectangle(88, 88), amount=3.0)
    g += Pos(0, -54, 0) * extrude(Rectangle(20, 8), amount=3.0)
    return g
