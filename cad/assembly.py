"""Calegari View 2: the whole camera, every printed part and the few bought ones, in place.

assemble(sx, sy, E=0, back=True, blade_locked=True) -> list of Item(name, shape, mat, printed)
"""
from dataclasses import dataclass
import math
from build123d import *
from params import *
from util import *
import mech as M
import parts as P


@dataclass
class Item:
    name: str
    shape: object
    mat: str
    printed: bool = True


EXPLODE = {"body": (0, 0, 0), "graflok": (0, 0, -1.2), "blade": (0, 0, -1.7), "back": (0, 0, -3.2),
           "y": (0, 0, 0.9), "y_drive": (-0.8, 0, 0.3), "y_rack": (0, 0, 0.55), "seal_b": (0, 0, 0.45),
           "x": (0, 0, 1.8), "x_drive": (0, 0.8, 1.8), "x_rack": (0, 0, 1.35), "seal_y": (0, 0, 1.2),
           "heli": (0, 0, 2.4), "mount": (0, 0, 3.0), "board": (0, 0, 3.6), "lens": (0, 0, 4.3),
           "plug_y": (0, -0.8, 0), "plug_x": (-0.8, 0, 0.9)}


def rise_shaft():
    """Pinion face (toward the knob) to the shaft end, which sits KNOB_BORE inside the knob."""
    face = abs(RISE_PIN[0]) + PIN_W / 2
    return (H + KNOB_OFF + M.KNOB_BORE) - face


def shift_shaft():
    face = SHIFT_PIN[1] + PIN_W / 2
    return (H + KNOB_OFF + M.KNOB_BORE) - face


def assemble(sx=0.0, sy=0.0, E=0.0, back=True, blade_locked=True, thread=False, ext=0.0):
    """ext: helicoid extension from infinity (mm); the mount, board and lens travel with it."""
    items = []

    def add(name, shape, mat, group, printed=True):
        d = EXPLODE[group]
        if E:
            shape = Pos(d[0] * E, d[1] * E, d[2] * E) * shape
        items.append(Item(name, shape, mat, printed))

    add("body", P.body_part(), "body_black", "body")
    add("graflok_module", P.graflok_module(), "body_black", "graflok")
    add("graflok_blade", P.graflok_blade(blade_locked), "red", "blade")
    add("graflok_wheel", P.graflok_wheel(), "body_black", "blade")
    if back:
        bk, lev = P.rb67_back()
        add("rb_back", bk, "leather", "back", False)
        add("rb_lever", lev, "chrome", "back", False)

    # rise drive: pinion in the body; it turns as the rack on the Y plate goes by
    px, py, pz = RISE_PIN
    # pinion and knob as one sub-assembly (pinion frame: teeth z 0..PIN_W, shaft +Z), then placed
    kn = M.knob()
    kdot = Pos(0, -(KNOB_D / 2 - 4.2), 0) * Cylinder(1.2, 0.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    def drive(T, shaft):
        up = Pos(0, 0, PIN_W + shaft - M.KNOB_BORE + KNOB_H) * Rot(180, 0, 0)
        return (T * Pos(0, 0, -PIN_W / 2) * M.pinion(shaft), T * Pos(0, 0, -PIN_W / 2) * up * kn,
                T * Pos(0, 0, -PIN_W / 2) * up * kdot)
    T = Pos(px, py, pz) * Rot(math.degrees(-sy / M.PIN_R), 0, 0) * Rot(90, 0, 0) * Rot(0, -90, 0)
    pr, kr, kd = drive(T, rise_shaft())
    add("pinion_rise", pr, "body_black", "y_drive")
    add("knob_rise", kr, "body_black", "y_drive")
    add("dot_knob_rise", kd, "red", "y_drive", False)
    add("washer_rise", Pos(-H, py, pz) * orient(M.drag_washer(), "-x"), "rubber", "y_drive")
    add("velvet_body", P.velvet_body(), "velvet", "seal_b", False)
    for s in (-1, 1):
        add(f"plug_y_{s}", P.way_plug_y(s), "body_black", "plug_y")

    # Y plate with its two racks (rise in the back, shift in the front)
    add("y_plate", P.y_plate(sy), "body_black", "y")
    L, c = P.RISE_RACK
    w_pl, w_c = M.drive_layout()
    rk = Location(Plane(origin=(px - RACK_W / 2, c, BODY_Z1 - w_pl), x_dir=(0, -1, 0), z_dir=(1, 0, 0))) * M.rack(L)   # teeth toward -Z
    add("rack_rise", Pos(0, sy, 0) * rk, "body_black", "y_rack")
    qx, qy, qz = SHIFT_PIN
    L, c = P.SHIFT_RACK
    rk = Location(Plane(origin=(c, qy + RACK_W / 2, XP_Z0 + w_pl), x_dir=(1, 0, 0), z_dir=(0, -1, 0))) * M.rack(L)   # teeth toward +Z
    add("rack_shift", Pos(0, sy, 0) * rk, "body_black", "x_rack")
    add("velvet_yplate", Pos(0, sy, 0) * P.velvet_yplate(), "velvet", "seal_y", False)
    for s in (-1, 1):
        add(f"plug_x_{s}", Pos(0, sy, 0) * P.way_plug_x(s), "body_black", "plug_x")

    # lens panel with the shift drive (it rides with the lens), helicoid, mount, board, lens
    mv = Pos(sx, sy, 0)
    add("lens_panel", P.lens_panel(sx, sy, thread=thread), "body_black", "x")
    T = Pos(qx + sx, qy + sy, qz) * Rot(0, math.degrees(sx / M.PIN_R), 0) * Rot(0, 180, 0) * Rot(-90, 0, 0)
    ps, ks, kd = drive(T, shift_shaft())
    add("pinion_shift", ps, "body_black", "x_drive")
    add("knob_shift", ks, "body_black", "x_drive")
    add("dot_knob_shift", kd, "red", "x_drive", False)
    add("washer_shift", Pos(qx + sx, H + sy, qz) * orient(M.drag_washer(), "+y"), "rubber", "x_drive")
    fw = mv * Pos(0, 0, ext)
    add("helicoid", mv * P.helicoid_part(HELI_INF + ext), "alu_black", "heli", False)
    add("mount", fw * M.mount(thread=thread), "body_black", "mount")
    add("board", fw * M.board(), "body_black", "board")
    if not E:
        for n, sh, m in P.dot_inlays(sx, sy):
            add(n, sh, m, "body", False)
        add("dots_numerals", P.scale_numerals(sx, sy), "white_ink", "body", False)
    lm, lg = P.lens_part()
    add("lens_body", fw * lm, "lens_black", "lens", False)
    add("lens_glass", fw * lg, "glass", "lens", False)
    return items


if __name__ == "__main__":
    it = assemble()
    print(len(it), "items,", sum(i.printed for i in it), "printed")
