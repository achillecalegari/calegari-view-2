# Calibration

[Back to the project](../README.md)

Most of the calibration happens before the camera exists, on the [test prints](test-prints.md): shrinkage, thread, bayonet, drive and dovetails. What is left is done once the camera is built.

## 1. Light test

1. In a dark room, put the camera on the tripod with the ground glass on and the shutter closed. Throw a dark cloth over the back and your head.
2. With a bright torch, sweep slowly along every joint between the body, the Y plate and the lens panel, from all sides.
3. Repeat with the plates at the four corners of their travel (rise and shift both at 30 mm).

The ground glass must stay black. A glow means the velvet has a gap or lifts at an edge: press it down, or cut a new piece from the template. The narrowest band of velvet between the plates is 6.1 mm at the worst position (`cad/seal_check.py`), so a gap is always a velvet problem, not a geometry one.

## 2. Infinity

The camera is drawn so that, with the reference lens (Super-Angulon 65/8, flange focal distance 70.5 mm), infinity is sharp 0.3 mm before the helicoid's closed stop: about 7 degrees of the grip. The grip turns 22.4 degrees per millimetre of travel.

1. Focus on something far away with a loupe and note how far the grip is from its closed stop, in degrees (a protractor printed on paper and taped to the panel helps).
2. Between 0 and 30 degrees: nothing to do. Paint the index (assembly, step 11).
3. More than 30 degrees: the lens sits too close to the film and you are losing close focus. Print the board again, raised by (degrees / 22.4 - 0.3) mm:

   ```
   python board.py 70.5 --trim 1.2
   ```

4. Not sharp even at the stop: the lens sits too far from the film. Print a board sunk by 0.5 mm (`--trim -0.5`) and repeat until it is.

The board is the only calibration part: a 20 minute print.

## 3. Other lenses

Every lens gets its own board, printed for its flange focal distance (the distance from the shutter's mounting face to the film at infinity; the data sheets call it flange focal distance or Auflagemaß). The board's plateau raises or sinks the lens so that infinity always sits at the same place on the helicoid.

```
python board.py 71.2
```

writes `print/stl/lens_board_71.2.stl`. The camera accepts flange focal distances from 68.0 to 78.5 mm; a board sunk by more than 0.5 mm prints with supports under the rim.

Then check infinity as above. The engraved distance scale is drawn for 65 mm; with a 75 mm lens read it as a rough guide.

## 4. Feel of the movements

| What | If | Do |
|---|---|---|
| A plate is stiff all along | the flexure way is too tight | one light coat of dry PTFE on the tongues; if it is still stiff, `WAY_INTERF` -0.05 and reprint the part with the slotted groove (body for the rise, Y plate for the shift) |
| A plate rocks | the way is loose | `WAY_INTERF` +0.05, same part |
| The front falls by itself with a heavy lens | the ways hold the weight, the knob only adds drag | `WAY_INTERF` +0.05 on the body |
| The knob is too free or too stiff | the wave washer | reprint the pinion with `KNOB_OFF` -0.1 (stiffer) or +0.1 (freer) |
| The click at zero is faint or hard | the spring | `DET_T` in `cad/parts.py`: +0.2 harder, -0.2 softer |

## 5. Limits

- **Movements:** 30 mm each way on each axis, mechanical stops.
- **Corners:** clean at 30 mm on one axis, and at 25 + 25 mm of rise and shift together, at infinity, f/22. Focused at about 0.9 m the combined figure drops to 22 + 22 mm: the helicoid's own rear tube, which the corner rays reach when the lens moves out. Past that, it is the lens's image circle that runs out: a 160 mm circle covers 30 mm on one axis and 25 + 25 combined.
- **Close focus:** about 0.45 m with the 17 to 31 mm helicoid.
