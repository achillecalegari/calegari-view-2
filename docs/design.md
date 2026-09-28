# Design notes

[Back to the project](../README.md)

View 2 asks one question of [View 1](https://github.com/achillecalegari/calegari-view-1): which of its sixty-odd bought fasteners can a printer replace, and how, without the camera getting worse? All of them, it turned out. Then a second question: can it look like one object instead of a stack of parts?

## What replaced what

| View 1 | View 2 | How it prints |
|---|---|---|
| Printed rails screwed on with M2.5 and M3 into inserts | grooves cut into the body and the Y plate, tongues printed on the moving plates | grooves open on the bed, tongues on top, 30 degree flanks |
| Gib strip and three grub screws per way | one groove's outer wall is a flexure beam, 1.2 mm thick and 7 mm tall, 0.25 mm interference | the slit prints open on the bed; the beam bends across the layers |
| M6 threaded rod, brass nut, bushings, cap nut | module 1 rack and 12-tooth pinion, 37.7 mm per turn | teeth in the bed plane: exact involutes; the racks print lying on their side |
| O-ring under the knob | a TPU wave washer: a 0.8 mm ring on three feet each side, squeezed 0.3 mm | flat |
| Ball plunger and dimple | a flat spring cut into the moving plate's back, with a bump near its free end, and a dimple in the other plate | the spring prints flat over a cavity |
| Stud, nut and grub screw in the knob | the knob snaps onto a D shaft: two tabs drop into a groove | the tabs bend in the bed plane |
| Hard stops at the ends of the screw channels | closed groove ends, and a plug pressed into the open end after assembly | |
| RafCamera metal flange, four screws | an M65 x 1 thread printed in the lens panel | 0.12 mm layers, thread axis vertical |
| Focus ring with four grub screws and a hidden stop | the helicoid's own grip; a scale engraved on the panel, an index painted on the grip | |
| Technika board, holder, latch, spring, screws, inserts | a 70 mm round board on a three-lug bayonet with a flexure detent | the lugs' undersides are chamfered: no overhang |
| Brass shims for other lenses | the board's plateau is printed for each lens's flange focal distance | `python board.py 71.2` |
| Four screws and inserts on the Graflok module | three snap hooks into the body's recess | the hooks bend in the module's plane |
| Graflok wheel on an M3 screw | a printed wheel on a printed M8 stud | stud printed standing |
| Aluminium Arca plates, screws, inserts | Arca dovetails printed with the body | 45 degree flanks |
| Top handle, screws, inserts, levels | printed with the body, full width; a shoe level if you want one | |

What stayed bought: the helicoid, a precision thread that must not wobble or tilt the lens, and it costs less than the test prints of a printed one; and the velvet. TPU lip seals were drawn and dropped: no single lip stays on solid faces on both sides while two plates slide in two directions. The velvet seals by area, as on View 1.

## One block

At zero the body, the Y plate and the lens panel are one square, 162 mm, with the Y plate 1.5 mm smaller all round: from the side the three layers read as a single block with two shadow lines. The body, the plinth, the side leg and the handle share one front face, printed in one piece. The front of the camera is the lens panel and the barrel, nothing else: the helicoid's grip and the lens mount are the same diameter, so they read as one barrel, and the distance scale is engraved around it. The knobs are the only things that stick out, one per movement, on the side and on top.

## Why 30 mm and not 40

With sliding plates, the light seal is geometry. The middle plate must stay covered by the plate behind it at the end of its travel, and its own window has to be wider than the light cone by the other plate's travel. Each millimetre of travel costs about 3.2 mm of camera. At 30 mm each way the block is 162 mm, 14 mm more than View 1 at 25; at 40 it would be about 195 mm and the body would no longer print in one piece on a 256 mm bed. And a 65 mm lens with a 160 mm image circle covers 30 mm on one axis anyway, 25 + 25 combined: past that, a bigger camera buys nothing.

## The drives

The rise pinion lives in the body, its knob on the photographer's right, and its rack in the back of the Y plate. The shift pinion lives in the lens panel and its rack in the front of the Y plate, so the shift knob rides on top of the lens: the knob is where the lens is. In both, the rack's tips stop 0.3 mm short of the pinion plate's face, and the pinion reaches across the gap into a shallow band in the other plate: nothing drags on the sliding faces. Each rack is placed so that a tooth space faces the pinion at zero, and the whole travel is checked for interference in `check.py`.

The rise pinion sits in a round pocket, not a square one: a square pocket would break into the relief for the RB67's dark slide behind it.

## Focusing and infinity

The helicoid is closed at 17 mm; infinity is at 17.3. That is 0.3 mm, about 7 degrees of the grip, of travel past infinity, which every lens has and which makes infinity easy to find by feel. Everything else follows: the lens panel's front sits at 70.5 - 5 - 17.3 = 48.2 mm from the film, the mount is 5 mm long, the board's front is at the lens's flange focal distance. Changing lens changes only the board.

## Findings along the way

- **The helicoid's rear tube limits combined shifts.** Its bore (61 mm) sits 5.5 mm deep in the lens panel. At infinity the corners stay clean to 25 + 25 mm. Focused at about 0.9 m the lens moves out, the corner rays open up and the tube clips them past 22 + 22 mm. View 1's ray trace did not model the tube.
- **A detent bump must sit near the spring's free end.** Near the root, a 1.4 mm ASA spring deflected 0.4 mm would see several times its yield stress; near the free end, 12 MPa and a light 2 N click. The bump also has to reach across the gap, or it never clicks.
- **A solid TPU washer is a brick.** Squeezed 0.3 mm over its whole face it would push with hundreds of newtons. The wave washer bends between its feet: a few newtons, an even drag. The weight of the front standard is held by the flexure ways, not by the knob.
- **Press fits need interference.** The plugs and the racks are drawn 0.1 mm larger than their slots; with zero they would fall out.
- **A name prefix can hide a part.** An early ray trace skipped everything whose name began with "lens", including the lens panel. The panel is in the trace now.

## Checks

`check.py` (every pair of parts, eight positions, designed contacts on a volume budget), `fitcheck.py` (the test plate mechanisms), `seal_check.py` (the velvet band), `optics_check.py` (ray trace through every part, at infinity and focused close).
