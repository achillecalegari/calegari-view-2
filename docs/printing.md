# Printing

[Back to the project](../README.md)

Bambu Lab P1S (or any enclosed printer with a 256 mm bed), textured PEI plate, ASA. Set the shrinkage and pass the [test prints](test-prints.md) first.

| Plate | Parts | Notes |
|---|---|---|
| `plate_01_black` | body (with its handle and the Arca foot), two knobs, stop peg | the long one |
| `plate_02_black` | Y plate (with the rise rack), shift rack, Graflok wheel, the rise collar, six plugs | |
| `plate_03_black` | rotator, lens board | |
| `plate_04_black_0.12mm_layers` | lens panel, shift pinion, rise worm, rise knob's gear | 0.12 mm layers: the M65 thread, the gear teeth, the worm's thread, the miter pair |
| `plate_05_black_0.12mm_layers` | lens mount | 0.12 mm layers: the M65 thread |
| `plate_06_red` | Graflok blade | |
| `plate_07_tpu` | two wave washers | TPU 95A, external spool |

Every part is already oriented. The rule behind the orientations: whatever touches the bed is a face, a groove, a recess or an engraving, never a boss; tongues, bumps and rails are on top. The body, the Y plate, the lens panel and the rotator print front face down, so the engraved name, the distance scale and the grooves come out crisp on the textured plate. Gear teeth and racks lie in the bed plane, where the printer is most precise; the rise worm stands up, so its thread is drawn layer by layer like a screw, and the Y plate's rise rack is cut in the plate so each layer holds the worm's exact tooth profile. The worm and the rise knob's gear stand up too: their miter gears end in 45 degree back cones, so nothing overhangs. The knobs print crown down. The flexures (the ways' beams, the zero-click springs, the rotator's springs, the knobs' tabs) bend across flat layers, never by pulling layers apart.

| Setting | Value |
|---|---|
| Layers | 0.16 mm; 0.12 mm on the two plates that say so |
| Walls | 5 on the body, Y plate, lens panel and rotator; 4 elsewhere |
| Infill | 30 % gyroid; 100 % for the worm, the knob's gear, the pinion, the rack, the knobs, the collar, the board, the mount, the plugs and the peg |
| Supports | none |
| Brim | ears on the body, Y plate, lens panel and rotator corners; a 5 mm brim around the worm (84 mm tall, 10 wide), the rise knob's gear and the two long plugs |

The wave washers bridge over their own three feet (half a millimetre, 8 mm spans): no supports, a little sag does no harm.

## After printing

1. Pull any stringing out of the pockets and bores.
2. Slide a fingernail along the flexure slits (the thin slots beside two of the grooves) and under the three springs in the rotator's recess: they must be free for their whole length.
3. Fill the dots and the distance numbers: a drop of red or white acrylic with a toothpick, wait a minute, wipe across with a damp cloth. Red for the zeros, infinity and the indexes, white for the rest. The name stays black.
4. The red index on the helicoid's grip is painted at the end of the assembly, at infinity.
