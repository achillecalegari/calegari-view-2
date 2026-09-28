# Printing

[Back to the project](../README.md)

Bambu Lab P1S (or any enclosed printer with a 256 mm bed), textured PEI plate, ASA. Set the shrinkage and pass the [test prints](test-prints.md) first.

| Plate | Parts | Notes |
|---|---|---|
| `plate_01_black` | body (with plinth, side leg, handle and both Arca dovetails), knob | the long one; the body fills the plate |
| `plate_02_black` | Y plate, lens board, both racks, knob, Graflok wheel, four plugs | |
| `plate_03_black` | Graflok module | |
| `plate_04_black_0.12mm_layers` | lens panel, rise pinion, shift pinion | 0.12 mm layers: the M65 thread and the gear teeth |
| `plate_05_black_0.12mm_layers` | lens mount | 0.12 mm layers: the M65 thread |
| `plate_06_red` | Graflok blade | |
| `plate_07_tpu` | two wave washers | TPU 95A, external spool |

Every part is already oriented. The rule behind the orientations: whatever touches the bed is a face, a groove, a recess or an engraving, never a boss; tongues, bumps and rails are on top. The body, the Y plate and the lens panel print front face down, so the engraved name, the distance scale and the grooves come out crisp on the textured plate. Gear teeth and racks lie in the bed plane, where the printer is most precise. The flexures (the ways' beams, the zero-click springs, the module's hooks, the knob's tabs) bend across flat layers, never by pulling layers apart.

| Setting | Value |
|---|---|
| Layers | 0.16 mm; 0.12 mm on the two plates that say so |
| Walls | 5 on the body, Y plate, lens panel and module; 4 elsewhere |
| Infill | 30 % gyroid; 100 % for the pinions, racks, knobs, board, mount and plugs |
| Supports | none |
| Brim | ears on the body, Y plate and lens panel corners |

The wave washers bridge over their own three feet (half a millimetre, 8 mm spans): no supports, a little sag does no harm.

## After printing

1. Pull any stringing out of the pockets and bores.
2. Slide a fingernail along the four flexure slits (the thin slots beside two of the grooves): they must be open for their whole length.
3. Fill the dots and the distance numbers: a drop of red or white acrylic with a toothpick, wait a minute, wipe across with a damp cloth. Red for the zeros, infinity and the indexes, white for the rest. The name stays black.
4. The red index on the helicoid's grip is painted at the end of the assembly, at infinity.
