# Design notes

[Back to the project](../README.md)

View 2 asks one question of [View 1](https://github.com/achillecalegari/calegari-view-1): which of its sixty-odd bought fasteners can a printer replace, and how, without the camera getting worse? All of them, it turned out. Then two more: can it look like one object instead of a stack of parts, and can the film turn instead of the camera?

## What replaced what

| View 1 | View 2 | How it prints |
|---|---|---|
| Printed rails screwed on with M2.5 and M3 into inserts | grooves cut into the body and the Y plate, tongues printed on the moving plates | grooves open on the bed, tongues on top, 30 degree flanks |
| Gib strip and three grub screws per way | one groove's outer wall is a flexure beam, 1.2 mm thick and 7 mm tall, 0.25 mm interference | the slit prints open on the bed; the beam bends across the layers |
| M6 lead screw, brass nut, bushings, cap nut (rise) | a printed worm, 8 mm pitch diameter, and a rack moulded into the Y plate, cut as the negative of the worm; a printed miter pair turns it from the side knob | the worm and the knob's gear stand up; the rack's layers each hold the worm's tooth profile |
| M6 lead screw and nut (shift) | module 1 rack and 12-tooth pinion, 37.7 mm per turn | teeth in the bed plane: exact involutes; the rack prints lying on its side |
| O-ring under the knob | a TPU wave washer under each knob: a 0.8 mm ring on three feet each side, squeezed 0.3 mm | flat |
| Ball plunger and dimple | a flat spring cut into the moving plate's back, with a bump near its free end, and a dimple in the other plate | the spring prints flat over a cavity |
| Knobs with a stud, a nut and a grub screw | knurled knobs that snap onto D shafts: two tabs drop into a groove | crown down; the tabs bend in the bed plane |
| Hard stops at the ends of the screw channels | closed groove ends, and a plug pressed into the open end after assembly | |
| RafCamera metal flange, four screws | an M65 x 1 thread printed in the lens panel | 0.12 mm layers, thread axis vertical |
| Focus ring with four grub screws and a hidden stop | the helicoid's own grip; a scale engraved on the panel, an index painted on the grip | |
| Technika board, holder, latch, spring, screws, inserts | a 70 mm round board on a three-lug bayonet with a flexure detent | the lugs' undersides are chamfered: no overhang |
| Brass shims for other lenses | the board's plateau is printed for each lens's flange focal distance | `python board.py 71.2` |
| Graflok module, four screws, four inserts; an L bracket for portrait | a round rotator that carries the Graflok seat and turns the back 90 degrees, held by two lugs and three printed springs | front face down; the lugs are 45 degree cones, no overhang |
| Graflok wheel on an M3 screw | a printed wheel on a printed M6 stud | stud printed standing |
| Two aluminium Arca plates, screws, inserts | the foot is an Arca dovetail, printed with the body | 45 degree flanks |
| Top handle, screws, inserts, levels | printed with the body, full width | |

What stayed bought: the helicoid, a precision thread that must not wobble or tilt the lens, and it costs less than the test prints of a printed one; and the velvet. TPU lip seals were drawn and dropped: no single lip stays on solid faces on both sides while two plates slide in two directions. The velvet seals by area, as on View 1.

## Why the front standard stays up

The front standard (Y plate, lens panel, helicoid and a 65 mm lens in its shutter) weighs about 0.8 kg: 8 N on the rise drive. The first View 2 raised it with a rack and a 12-tooth pinion, like the shift. A spur pinion runs backwards as easily as forwards: 8 N at its 6 mm pitch radius is 0.05 N·m trying to turn the knob, and nothing but the friction of the ways was holding it. With a light coat of PTFE, which the guide recommended, the front would have crept down on its own.

The rise is now a worm. One turn of the knob moves the plate one lead, pi mm, and the lead climbs the 8 mm worm at 7.1 degrees. A load on the rack pushes along the worm's axis, and it can only turn the worm if the flank's slope beats the friction on it: dry ASA on ASA has a friction angle of about 17 degrees, far above 7.1. The worm cannot be turned by its load, at any position, with any lens. PTFE would bring the friction angle near the lead angle, so the worm and its rack stay dry; the shift, which gravity does not pull while the camera is level, keeps its fast rack and pinion.

The rack is the other half of the trick. A straight-toothed rack only matches a worm in the plane through its axis; a millimetre to either side the worm's flank has moved and the teeth collide (the first prototype did, by 3 to 9 mm³). But a worm that turns is the same surface as a worm that slides along its axis, so the rack that meshes with it over its whole face is simply the negative of the worm: a slice of a nut, cut by a worm 0.15 mm fatter than the real one. In each printed layer of the Y plate the rack's section is the worm's own tooth profile. `fitcheck.py` turns the worm through the whole travel against it: 0.003 mm³ of contact, numerical noise.

The worm stands inside the body's right side and nothing of it shows. Its top carries a small straight bevel gear; a second one, on a shaft through the side face, meets it at right angles: a miter pair, 12 teeth, module 0.75, one to one. The knob sits on that shaft; turned clockwise, it raises the front standard. Both gears stay inside the worm's own envelope, 10.2 mm across, so the body stays 22 mm deep around them. Their teeth end on the back cone, as on a real bevel gear: the core behind each heel stays inside the other gear's reach, and every slope is 45 degrees or steeper, so both print standing without support. A collar pressed into the side bore under the knob holds the knob's gear in; the pin at the worm's bottom stands in a plug pressed into the bore from below, and that seat is the thrust bearing. A small stub on the knob's gear, just above the worm's top, stops the worm lifting.

The knob sits in the middle of the side face, the body and the handle's post together. It cannot come lower: the gear sits above the worm, the worm above the rack's highest point, and the rack's channel has to stay behind the Y plate at every rise and fall, so the rack has only three teeth and starts as low as that allows.

## The back turns, the camera does not

View 1 needed an L bracket and a second Arca plate for portrait, and a camera on its side is awkward to use. View 2 turns the film instead. The Graflok seat, its rails, blade and wheel are one round plate, the rotator, 160 mm across, in a round recess in the body's back.

- **Held:** two lugs at the recess rim, 45 degree cones on the underside, over a matching bevel on the rotator's back edge. Three flat springs cut into the recess floor push the rotator back onto them. The cone contact centres it and sets its plane; the film plane is the rotator's seat, and the ground glass and the film sit on the same seat, so focus stays true in both positions.
- **Clicks:** each spring's bump drops into a shallow dimple at landscape and at portrait. The dimples are 0.25 mm deep against a 0.4 mm bump, so the springs keep part of their preload at rest: the rotator never floats.
- **Stops:** a peg pressed through the body's left side face runs in a 90 degree groove on the rotator's rim.
- **Goes in:** the rotator has two notches in its rim. Turned 135 degrees, and only there, they pass the lugs. The working range, 0 to -90, never reaches that angle, and the peg, pressed in last, makes sure of it.
- **Dark:** the rotator's front face meets the recess floor across a ring rib that sits in a groove: light coming round the rim has to turn twice. The openings in front are square, so the frame fits in both orientations; that is one reason the block grew from 162 mm.
- **The dark slide:** it comes out on the photographer's right in landscape and at the top in portrait. The body is notched for it on both sides, and the handle stands 2 mm off the back so the slide's grip passes under it.

The springs sit at 15, 135 and 255 degrees. Three springs 120 degrees apart never meet each other's dimples inside the working range, so the back clicks only at its two positions; and none of the six dimples falls in the dark-slide relief, where the rotator is thin.

## One block

At zero the body, the Y plate and the lens panel are one square, 180 mm, with the Y plate 1.5 mm smaller all round: from the side the three layers read as a single block with two shadow lines. The body and the handle share one front face, printed in one piece, with the same 9 mm corner at the top of the handle and at the bottom of the body; seen from the front the handle's posts and its bar are the same 16 mm. The front of the camera is the lens panel and the barrel, nothing else: the helicoid's grip and the lens mount are the same diameter, so they read as one barrel, and the distance scale is engraved around it. There are two controls, two knurled knobs as on View 1: the shift knob stands on the lens panel's top edge, centred in the handle's window, and rides with the lens; the rise knob stands in the middle of the right side face.

Without the side leg the camera sits on the tripod one way, and it needs no plinth: the foot is simply an Arca-Swiss dovetail across the whole width, 9.5 mm tall, centred 32 mm behind the body's front face under the rotator. At full fall the plates drop past it in front of the clamp.

## Why 30 mm and not 40

With sliding plates, the light seal is geometry. The middle plate must stay covered by the plate behind it at the end of its travel, and its own window has to be wider than the light cone by the other plate's travel. Each millimetre of travel costs about 3.2 mm of camera. At 30 mm each way the light needs 170 mm; the block is 180, and the extra 5 mm a side is where the rise's miter pair lives. At 40 mm it would be over 200 and the body would no longer print in one piece on a 256 mm bed. And a 65 mm lens with a 160 mm image circle covers 30 mm on one axis anyway, 25 + 25 combined: past that, a bigger camera buys nothing.

## Focusing and infinity

The helicoid is closed at 17 mm; infinity is at 17.3. That is 0.3 mm, about 7 degrees of the grip, of travel past infinity, which every lens has and which makes infinity easy to find by feel. The lens panel's front sits at 70.5 - 5 - 17.3 = 48.2 mm from the film, the mount is 5 mm long, the board's front is at the lens's flange focal distance. Changing lens changes only the board.

## Findings along the way

- **The helicoid's rear tube limits combined shifts.** Its bore (61 mm) sits 5.5 mm deep in the lens panel. At infinity the corners stay clean to 25 + 25 mm; focused at about 0.9 m the lens moves out, the corner rays open up and the tube clips them past 22 + 22 mm. View 1's ray trace did not model the tube.
- **A detent bump must sit near the spring's free end.** Near the root, a 1.4 mm ASA spring deflected 0.4 mm would see several times its yield stress; near the free end, 12 MPa and a light 2 N click. The bump also has to reach across the gap, or it never clicks.
- **A solid TPU washer is a brick.** Squeezed 0.3 mm over its whole face it would push with hundreds of newtons. The wave washer bends between its feet: a few newtons, an even drag.
- **Press fits need interference.** The plugs, the rack and the stop peg are drawn 0.1 mm larger than their slots; with zero they would fall out.
- **A part has to be able to go in, and in the right order.** The worm's gear is wider than the rack lets through, so the worm goes up its bore before the Y plate, and its plug is notched where the rack's channel crosses the bore: the rack slides up past it and threads onto the worm from below. A second plug closes the channel afterwards. `fitcheck.py` checks every path.
- **A long press fit is a stuck part.** A plug pressed over 25 mm would need a vice. The long plugs press only over a 6 mm band at the bottom and slide above it.
- **A slot must stay inside its part.** With View 1's M3 screw the Graflok blade's slot was small; with a printed M8 stud it grew until it broke 0.2 mm through the blade's top edge, a hairline split. The stud is now M6 and 1 mm lower: 1.9 mm of blade above the slot, 3 mm below, checked in `fitcheck.py`.
- **A name prefix can hide a part.** An early ray trace skipped everything whose name began with "lens", including the lens panel. The panel is in the trace now.

## Checks

`check.py` (every pair of parts at eleven positions, landscape, portrait and half way; designed contacts on a volume budget), `fitcheck.py` (the mechanisms: worm and rack over the whole travel, the rotator going in, held and stopped, the miter pair, the parts going in, the bayonet, the pinion, the knobs, the Graflok blade, the dovetails), `seal_check.py` (the velvet band), `optics_check.py` (ray trace through every part, at infinity and focused close, in both orientations).
