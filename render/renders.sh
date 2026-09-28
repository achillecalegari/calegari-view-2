#!/bin/zsh
# Product renders for the README and the project page (docs/img). About 15 minutes on an M-series Mac.
set -e
cd "${0:A:h}/.."
PY="$PWD/.venv/bin/python"
B=/Applications/Blender.app/Contents/MacOS/Blender
R=out/png; mkdir -p $R
( cd cad && $PY render_meshes.py --tag home --back && $PY render_meshes.py --tag moved --sx 25 --sy 30 --back \
          && $PY render_meshes.py --tag explode --explode 30 --back && $PY explode_labels.py && $PY testrender.py )
shot() {  # mesh view name dist [expo]
  env EXPO=${5:--2.6} DIST=$4 FSTOP=40 $B -b -P render/white.py -- out/mesh_$1/manifest.json $R/$3.png $2 96 2000 >/dev/null 2>&1
}
shot home hero 01_three_quarter 3.4
shot home w_front 02_front 3.5
shot home side 03_side 3.6
shot home rear_hero 04_rear 3.8
shot home top 05_top 3.6
shot moved hero 06_movements 3.7
shot test top 10_test_rigs 2.6 -2.4
$PY render/compose.py docs/img $R/0*.png $R/10_test_rigs.png
env EXPO=-2.6 DIST=4.2 FSTOP=90 PTS=out/mesh_explode/points.json $B -b -P render/white.py -- out/mesh_explode/manifest.json $R/07_exploded.png explode34 96 2000 >/dev/null 2>&1
$PY render/annotate.py docs/img $R/07_exploded.png
