"""A lens board for your lens: its plateau puts the shutter's flange at the lens's own flange focal
distance, so infinity sits just short of the helicoid's closed stop with every lens.

python board.py 71.2          -> print/stl/lens_board_71.2.stl  (flange focal distance in mm, from the maker's data)
python board.py 70.5 --trim -0.2   same, 0.2 mm closer to the film (fine calibration, see docs/calibration.md)
"""
import argparse, pathlib, sys
import numpy as np
import trimesh
from params import FFD
import mech as M

ap = argparse.ArgumentParser()
ap.add_argument("ffd", type=float, help="the lens's flange focal distance, mm")
ap.add_argument("--trim", type=float, default=0.0, help="correction from the infinity test, mm (+ away from the film)")
a = ap.parse_args()
ffd = a.ffd + a.trim
d = ffd - FFD
if not -2.5 <= d <= 8.0:
    sys.exit(f"{ffd:.2f} mm is outside what the helicoid and the mount can reach ({FFD - 2.5:.1f} to {FFD + 8.0:.1f} mm)")
b = M.board(ffd)
vs, fs = b.tessellate(0.02, 0.15)
m = trimesh.Trimesh(np.array([(v.X, v.Y, v.Z) for v in vs]), np.array(fs), process=True)
m.merge_vertices()
m.apply_translation(-m.bounds[0])
out = pathlib.Path(__file__).resolve().parent.parent / "print" / "stl" / f"lens_board_{ffd:.1f}.stl"
m.export(str(out))
print(f"{out.name}: plateau {d:+.2f} mm from the reference board, watertight {m.is_watertight}")
