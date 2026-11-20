# Motion

How things move in Crumb Theory videos, animated graphics and covers with motion. Read by `edit-short-video`, which takes its default numbers from its own `references/visual-system.md` and lets this file override them, and by `visual-ideation.md` when filtering directions.

This file sets the character and the brand's numbers. Where it is silent, the skill's defaults apply.

## Core idea

**Rise, then set.** Elements arrive the way a batter rises in the oven: softly, from below, a little slower at the end, and then they stop and hold, like a crumb that has set. Nothing keeps wobbling after it lands.

## Principles

1. **Motion explains or it does not happen.** Every move points at the variable, reveals a result, compares two things or marks a change of beat. If you cannot name what it explains, it stays still.
2. **Rise in, slip out.** Entrances move up 20 to 30 px and ease out; exits are faster and simply fade with a small drop. In GSAP terms: `power3.out` for entrances, `power2.in` for exits.
3. **Durations by size.** A word or a pill: 280 to 360 ms. A card or a graphic: 450 to 550 ms. A full-frame change: up to 700 ms. Exits take about half of their entrance.
4. **Set and hold.** Once something lands it does not float, pulse or breathe. The attention moves to the next element.
5. **Comparisons move together.** Both halves of a side-by-side enter, zoom and label in sync, so the eye compares instead of following one side.
6. **The variable gets the motion.** In a test, only the changed sample moves or lights up in Berry. The control stays calm in Sage.
7. **Time is linear.** Timers, progress bars, time-lapse counters and slow background drift run at a constant speed (`none` in GSAP). Everything that lands eases.
8. **Numbers count like a scale.** A weight, a temperature or a percentage ticks up to its value in 400 to 600 ms and stops on the exact figure, which stays on screen long enough to read.
9. **Text never wobbles.** No jelly, squash or bounce on letters, however doughy the topic. Words enter about 50 ms apart; list items about 110 ms apart.
10. **One physical moment per piece.** A flour puff when a bowl lands, crumbs falling when a loaf is cut, steam when the oven opens. At most one per video, under one second, in Flour or translucent Flour, born exactly where the action happens and never over the face or the text.
11. **Sound and motion share the frame.** A highlighted move carries its sound on the same frame: a soft tap for a label, the brand's two-note ding for the result.

## Sound identity

The brand's short motif is a **rising major third, C to E**, bright and short, like a small kitchen bell. It plays on the result of a test and on the success sound, never more than twice per piece. In the generators of `find-video-audio`: `--notes C5,E5` for the success sound, `--notes C2,E2` for risers and block transitions, and C2 and E2 as the two note columns of the options file for tuned hits.

System sounds are fixed and repeat in every piece: a soft wooden tap when a label lands, a short airy whoosh for a moving comparison, a light tick for list items, and the motif on the result. Music changes from piece to piece.

## Never

- Spins, flips or rotations on anything with text.
- Glitch, neon, lens flares or sparkle trails.
- A bounce on every arrival, or one entrance recycled for every element.
- Fake slow motion or frame interpolation on a real bake result.
- "Magic" whooshes or sparkles over a result that came from chemistry: the point is that it is not magic.
- Generic crossfades between scenes. A scene changes by moving the camera, sliding the comparison or cutting on an action (the knife, the oven door).

## Applied example

The reveal of a two-pan test: both pans slide in together from below in 500 ms (2, 5); the frame holds still while the creator lifts each pancake (4); the soda pancake gets the Berry "Test" label and the powder one the Sage "Control" label at the same instant (5, 6); the height of each pancake counts up in millimeters (8); a single flour puff is not used here because the reveal is already strong (10); the C to E ding lands on the frame the numbers stop (11).
