"""Meshes + manifest for render/white.py.  python render_meshes.py --tag home [--sx 0 --sy 0 --explode 0 --back]"""
import argparse, json, pathlib
from build123d import *
from assembly import assemble

ap = argparse.ArgumentParser()
ap.add_argument("--tag", default="home")
ap.add_argument("--sx", type=float, default=0.0)
ap.add_argument("--sy", type=float, default=0.0)
ap.add_argument("--explode", type=float, default=0.0)
ap.add_argument("--back", action="store_true")
ap.add_argument("--thread", action="store_true")
ap.add_argument("--rho", type=float, default=0.0)
a = ap.parse_args()
OUT = pathlib.Path(__file__).resolve().parent.parent / "out" / f"mesh_{a.tag}"
OUT.mkdir(parents=True, exist_ok=True)
for f in OUT.glob("*.stl"):
    f.unlink()
man = []
for i in assemble(a.sx, a.sy, a.explode, back=a.back, thread=a.thread, rho=a.rho):
    f = OUT / f"{i.name}.stl"
    export_stl(i.shape, str(f), tolerance=0.04, angular_tolerance=0.15)
    man.append({"name": i.name, "file": str(f), "mat": i.mat})
(OUT / "manifest.json").write_text(json.dumps(man, indent=1))
print(a.tag, len(man))
