# Compositing an effect over a photo or a video

An effect generated on pure black is blended in screen mode: the black disappears and only the light adds up. One generated on pure white is blended in multiply mode (`mix-blend-mode:multiply`): the white disappears and only the dark part stays. An opaque element that was cut out is a PNG with transparency and needs no blend mode. In every case the element is placed with its point of origin on the exact spot (a hand, an object, a point of the scene) and fades out before it reaches the face.

## In HTML (covers and graphics)

```css
/* The effect centered on its origin; --w is its size on the canvas */
.fx{position:absolute;left:<origin x>px;top:<origin y>px;width:var(--w);height:var(--w);transform:translate(-50%,-50%);
  mix-blend-mode:screen;pointer-events:none;
  /* Fades out toward the face: two gradients combined; set their angle and stops so the effect ends before the face */
  -webkit-mask-image:linear-gradient(40deg,transparent 30%,#000 47%),linear-gradient(to bottom,#000 48%,transparent 60%);
  -webkit-mask-composite:source-in;mask-composite:intersect}
```

- If the effect's origin is not at the center of the image (a jet from a corner), position it with `left/top` and `transform-origin` at that point, and rotate with `rotate` around it.
- Adjust the mask percentages by looking at the crop at full size: no particle or flash over the eyes, the eyebrows or an accessory on the face, and no visible straight cut in the flash (a longer transition gradient softens it).
- With the person cut out and outlined, the effect goes above the cutout; the outline does not cover it.
- Check in the grid view (`preview.sh` of `design-reel-cover`) that the effect reads at small size and does not compete with the headline or the logo.

## In video (HyperFrames)

The same `mix-blend-mode:screen` on an `<img>` or `<video>` of the effect in a layer above the take, with animated entry and exit (scale from the origin and fade). If the person moves, the origin follows the point with `x/y` animated frame by frame, or the effect is anchored to a still stretch.
