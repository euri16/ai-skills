# Visual video

A visual video is a short vertical piece with no camera take: full-frame scenes of motion graphics, plus screenshots, b-roll or generated images when the piece has them. The creator is heard in a voice-over or not present at all. It suits an announcement, a figure, a comparison, a set of steps or a product scene, and it usually runs 15 to 45 s: without a face, each extra second has to be earned by a new screen.

It comes in two variants, chosen with the script:

- **With voice-over.** The creator's voice tells the piece and sets the timing; the screen shows what the voice names and carries the subtitles.
- **Without voice.** What appears written on screen is the whole script, each screen lasts what it takes to read, and music and effects carry the sound.

This file holds what is specific to the format. Everything it does not mention is the same as in a talking-head piece and lives in the other references: brand tokens, canvas and zones, type scale, motion and sound numbers in `visual-system.md`; the project, the recipes, the render and the final encode in `hyperframes-recipes.md`; the review and the export preset in `quality-control.md`.

## What changes from a talking-head piece

| Step | Talking head | Visual video with voice-over | Visual video without voice |
|---|---|---|---|
| Source | Camera recording in `source/recording/` | Voice recording in `source/recording/` and `script.md` | `script.md` |
| Analysis | `analyze-video` on every recorded clip | `analyze-video` on the voice recording (`words.json`) | None |
| Cut master | `clip.mp4` and `cut.json` | `voice.wav` and `cut.json` (`build-cut.py single --voice-only`) | None |
| Timing comes from | The words of `cut.json` | The words of `cut.json` | The reading time of each screen |
| Screen layout | Around the creator, or split view | Full-frame scenes | Full-frame scenes |
| Subtitles | Below the face | In the standard position, no face to avoid | None |
| Space map | Before the proposal is presented, on frames of the recording | At the visual test, on frames of the composition | At the visual test, on frames of the composition |
| Sound | Voice, cut hits, featured sounds, optional music | Voice, a whoosh per scene change, featured sounds, optional music | Music (required), a whoosh per scene change, featured sounds |
| Speed | The speed rule of `SKILL.md` | The speed rule of `SKILL.md` | Built at its final pace, never sped up |

"What applies to each format" in `quality-control.md` lists every check and criterion per variant.

## Scenes

The layout is full-frame scenes: one scene on screen at a time over a backdrop that lasts the whole piece, so the frame is never empty and never jumps to black.

- **One lead per scene.** Each scene has one lead visual and the text that goes with it; the rest is at rest or out. If a scene has two ideas, it is two scenes.
- **A visual in every scene, not only text.** The lead visual shows the thing the scene is about and acts once: a number climbing to its final value, a tag crossed out with one stroke, one line of a document getting highlighted, steps ticked off in turn, a bar filling up, a product image with a slow push-in, a muted b-roll clip in a card. After it acts it stays still. The closing scene is the one scene that may be text only.
- **The thing itself before a metaphor.** A scene about a price shows the price; a scene about a document shows the document. Built screens, documents and data follow "Generated scenes" in `visual-system.md`: literally true, fictional demo data, recreated instead of pasted.
- **A fact shows where it comes from.** A claim that rests on a source (a release note, a study, a measurement, a product page) gets a scene where that source sits in a window styled with the brand, its key line highlighted, and its origin and date in a line the viewer can read.
- **The piece evolves.** From scene to scene something carries over (the same object in a new state, the same window with another line marked, the figure that becomes the label of the next scene) so the piece reads as one thing and not as unrelated slides.
- **Scene changes are moves, not fades.** The scene on screen exits toward the viewer in 0.2 s and its successor comes in from behind in 0.45 s: the default, for going deeper (from the claim to its proof). A scene that sits at the same level as the previous one (steps, items of a list, a before and after) arrives from the side instead. Every scene change carries the entrance whoosh.
- **The hook assembles itself in view, starting on frame 0.** The first block and the first word are already there on frame 0, the rest of the headline follows word by word and the lead visual acts, all within 2 s. No logo, title card or empty backdrop first. Frame 0 shows what the hook card of the script describes.
- **The close.** The payoff as a headline and the call to action in one line below it, held for its reading time, then the hard cut. The defaults of "Opening and closing" in `visual-system.md` apply: no outro and no logo, unless the brand guide defines a closing card.

Text on a scene:

- With voice-over, the rule of the talking-head piece holds: the subtitles carry what is said, and a scene adds only what is not spoken (a figure, a date, a label), 6 words at most.
- Without voice, the text of the scenes is all the script there is. A screen reads as one headline of up to 8 words and at most one supporting line of up to 10; a short tag above the headline, a pill and the labels printed on the visual get a glance and are not counted. Sizes come from "Typography and scale" in `visual-system.md`.

## The base template

`assets/visual-video/` is a complete HyperFrames project that follows the contract of the recipes: the same root, `class="clip"` with `data-start`, `data-duration` and `data-track-index` on everything timed, one paused GSAP timeline, colors and fonts only through the tokens of `assets/brand.css`, and fonts loaded by the project's `assets/fonts/fonts.css`.

```
assets/visual-video/
  index.html            five example scenes: hook, figure, source, steps and close
  hyperframes.json
  assets/brand.css      the brand tokens, filled with the values of the fictional example brand Crumb Theory
```

To start a piece, copy the folder to `social/<piece>/edit/project/`, replace the values of `assets/brand.css` with those of the workspace's `brand-guide/visual-identity.md`, copy `brand-guide/assets/fonts/fonts.css` (and the font files it points at) to `assets/fonts/`, and replace the example scenes with the scenes of the piece. The example text, figures and file names are invented; none of them stays in a real piece. The template carries no audio files: as copied, `verify-scenes.py` fails on it for lack of music, and passes once the bed of the piece is in place.

What the template's script reads from the markup, so the timing lives in one place:

| Attribute or class | On | Meaning |
|---|---|---|
| `class="scene clip"`, `data-start`, `data-duration` | Each scene | When the scene is on screen. Scenes follow each other with no gap and no overlap, the first starts at 0 and the last ends with the composition |
| `data-visual-seconds` | Each scene | Seconds its lead visual needs to act (0 when the scene has none). Required: `verify-scenes.py` adds it to the scene's reading time |
| `data-transition="side"` | A scene | It arrives from the side instead of from behind |
| `data-word` | Each scene, with voice-over | Index, from 0 and counted across all segments of `cut.json`, of the first word of the scene's beat |
| `class="stage"` | The one child of a scene | The area a scene may fill: x 108 to 930 and y 210 to 1680, inside the safe zone and left of the button column. Its children are the scene's blocks and enter in order |
| `class="voiced"` | The root, with voice-over | Ends the stage at y 1240, above the subtitle |
| `class="read"` | A block | Text the viewer has to read; it counts toward the reading time. Blocks without it are glanced at |
| `class="words"` | A text block | Reveals word by word. With `data-times="t t t"`, one composition time per word, each word appears at its time |
| `data-at` | A block, with voice-over | Composition time at which the block enters, when it waits for a word |
| `data-act`, `data-kind` | The lead visual | Seconds after the scene starts at which it acts, and what it does: `count` (with `data-from` and `data-to`), `strike`, `mark` or `check` |

The chain inside a scene: blocks enter one after the other, 0.25 s apart, and a `words` block reveals a word every 0.09 s; the hook goes faster (0.2 s and 0.06 s). These are the template's defaults; `brand-guide/motion.md` can set others. A lead visual the template does not have (another object, a chart, a b-roll card) is built with the recipes and the motion numbers of `visual-system.md`, given a `data-kind` of its own and its action added to the `act` function, with class names the template does not already use.

Tracks, the same convention as the recipes with two differences: there is no camera, so track 1 holds the voice-over (`#voice`) and track 3 holds the scenes.

| Track | Content |
|---|---|
| 0 | Backdrop (`#backdrop`), the whole piece |
| 1 | Voice-over (`#voice`), when there is one |
| 3 | Scenes |
| 4 | Subtitles, with voice-over |
| 5 to 9 | Graphics that live outside a scene |
| 10 and 11 | SFX |
| 12 | Music |

`check` reports three warnings that come with building the piece as one file: `nested_structure_needs_subcomposition` (a scene is a timed element with children), `timeline_track_too_dense` (several scenes or subtitles on one track) and, with voice-over, `line_unread` on subtitles, which follow speech and not reading time. Anything else is reviewed.

## Without voice

1. **Scenes from the script.** One scene per row of the script's screen table, with its exact text and its lead visual.
2. **Timing by reading.** A scene lasts at least: 0.45 s of entry (not the first scene), plus its reading time, plus the seconds its lead visual needs (`data-visual-seconds`), plus 0.8 s of hold on the closing scene. The reading time is the characters of its read text divided by the reading ceiling of "Subtitles" in `visual-system.md` (17 characters per second by default, configurable per language), and never under 1 s. A scene does not last over 1.5 s more than that: a screen that stays after it has been read drags. Every start and duration falls on a whole frame at 30 fps.
3. **Check it.** `python3 <skill-dir>/scripts/verify-scenes.py social/<piece>/edit/project` (with `--cps N` when the piece's language uses another reading ceiling) prints, per scene, its words, its characters, the time it needs and the time it has, and fails on a scene that is too short or drags, on a gap or an overlap between scenes, on a missing `data-visual-seconds`, on subtitles, and when there is no music. Write the text first, run it, and set each `data-duration` from what it prints.
4. **Music is required.** It carries the piece. Build the bed into one file ("Music bed" in the recipes), level it with `<skill-dir>/scripts/loudness.sh assets/music/bed.wav --fix --target -16` and place it at `data-volume="1"` for the whole piece; the final encode brings the mix to the delivery level. If the piece will play in a loop or be forwarded on its own, end the bed with a 3 s fade (`afade=t=out`) instead of the hard cut.
5. **Sounds.** The entrance whoosh on every scene change, at the scene's `data-start`, and a featured sound when a lead visual acts, at the scene's `data-start` plus its `data-act`. The budget of "Punch-ins, zooms and sounds" in `visual-system.md` holds: the scene whooshes play the part of the cut hits and stay outside the budget of featured sounds, which is unchanged.
6. **Speed.** The piece is built at its final pace: `final-encode.sh` runs without `--speed`.

## With voice-over

1. **Recording.** One audio file (or a video whose image is ignored) in `source/recording/`, read in one go from the script. When a sentence goes wrong the creator repeats it and keeps going; a second of silence before each repetition makes the cut easy to find. The sentence-by-sentence takes flow of `analyze-video` measures the face and does not apply to a voice recording.
2. **Analysis.** Invoke the `analyze-video` skill on the recording. Its `words.json` gives the time of every word.
3. **Cut.** Write the cut list as for a single take ("Cut" in `SKILL.md`): the best reading of each sentence, without long silences, filler or false starts, and the last segment ending 0.5 s after the last word. Then:

   ```bash
   python3 <skill-dir>/scripts/build-cut.py single social/<piece> social/<piece>/edit/cuts.json \
     --voice-only --words social/<piece>/edit/analysis/<recording>/words.json
   uv run -q --python 3.11 --with numpy --with silero-vad --with onnxruntime python <skill-dir>/scripts/verify-cut.py social/<piece>/edit/project
   <skill-dir>/scripts/loudness.sh social/<piece>/edit/project/voice.wav --fix      # then rename voice-norm.wav to voice.wav
   ```

   `build-cut.py` writes `voice.wav` and `cut.json` (whose `master` is `voice.wav`) with the same rules as a camera cut: whole frames, an 8 ms fade in and a 12 ms fade out per segment, the time of every word on the master. `verify-cut.py` runs its click, pause and length checks; it has no image to check and says so. After leveling, run it again.
4. **Scenes on the words.** Each scene belongs to a beat of the script and declares in `data-word` the first word of that beat. The first scene starts at 0; every other scene starts 0.3 s before its word, so it has settled when the word is heard, and stays up to the start of the scene after it. The composition lasts as long as `voice.wav`. A lead visual acts on the word that names it (`data-act` = the word's time minus the scene's start), and a block that has to wait for a word carries `data-at`.
5. **The hook.** Its headline is the hook line as animated typography, each word appearing as it is spoken: `data-times` with the `t0` of each word. The hook has no subtitle, as in a talking-head piece.
6. **Subtitles.** From the second sentence on, built from the `words` of `cut.json` with the recipe "Subtitles" and the rules of "Subtitles" in `visual-system.md`, in the default position: there is no face to stay below, and the `voiced` class keeps the scenes above them. While a scene shows a key phrase as typography, that line has no subtitle.
7. **Music and sounds.** Music is optional and follows the level rule of "Sound" in `visual-system.md`. The whoosh of a scene change carries an `id` that starts with `s-cut-`, so `verify-sfx.py` holds it 10 dB under any word it overlaps; featured sounds stay 6 dB under.
8. **Check it.** `verify-scenes.py` on the project fails when a scene does not start on its word, when `data-word` is missing or out of order, when the composition and the voice differ in length, and when there are no subtitles or one falls outside the voice. Then `verify-sfx.py`, as in any piece with a voice.

The elements a voiced piece adds to the template, inside the root:

```html
<div id="root" class="voiced" data-composition-id="main" data-start="0" data-duration="24.4" data-width="1080" data-height="1920" data-fps="30">
  <audio id="voice" src="voice.wav" data-start="0" data-duration="24.4" data-track-index="1" data-volume="1"></audio>
  <div id="s2" class="scene clip" data-start="3.1" data-duration="5.4" data-track-index="3" data-visual-seconds="1" data-word="9">...</div>
  <div id="cap-1" class="cap clip" data-start="3.4" data-duration="1.1" data-track-index="4">straight from <span class="k">the bag</span></div>
  <audio id="s-cut-2" src="assets/sfx/whoosh.wav" data-start="3.1" data-duration="0.3" data-track-index="10" data-volume="0.5"></audio>
  <audio id="sfx-figure" src="assets/sfx/hit.wav" data-start="5.2" data-duration="0.4" data-track-index="11" data-volume="0.6"></audio>
  <audio id="music" src="assets/music/bed.wav" data-start="0" data-duration="24.4" data-track-index="12" data-volume="1"></audio>
</div>
```

A piece without voice has the same `<audio>` elements except `#voice`, no `voiced` class, no `data-word` and no subtitles, and its whooshes can take any `id`.

## Proposal, visual test and review

- **Proposal.** The cut section is the voice-over cut list, or the screen table when there is no voice; the layer map has one row per scene ("Edit proposal" template). There is no framing to measure, so the space map is not part of the proposal.
- **Visual test.** After `check`, take one `snapshot` per scene at the instant it is complete, and run the space map on those frames: each beat of `edit/space.json` gives `"image"` (the frame), `"face": false`, the subtitle box if the piece has subtitles, and one graphic per block of the scene with its box as seen in the frame and its smallest text. It fails on anything outside the safe zone, in the button column, under 36 px or touching the subtitle. Review the frames at full size and check that the brand fonts loaded.
- **Review render and final render.** As in any piece, with the checks "What applies to each format" lists for the variant.
