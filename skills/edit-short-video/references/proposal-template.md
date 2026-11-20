# Edit proposal

File: `social/<piece>/edit/proposal.md`. It is what the user reads before any render exists. Write it in the user's language (or the one the workspace instructions set), so it is understood without opening the project: timings, what is seen, what is heard and why. Translate the headings and labels of the template below into that language. The template is written for a talking-head piece; the notes after it say what a visual video writes in each section.

```markdown
# Edit proposal: <working title>

- Status: draft | approved (YYYY-MM-DD)
- Source: `source/recording/<file>.mov` (<duration>, <resolution>, <fps>, SDR or HDR); b-roll: <list>
- Platforms and target duration: <IG, TikTok, Shorts, LinkedIn>; <N> s
- Format: educational | demo | opinion | progress update | sketch | community or event | visual video (with voice-over | without voice) | other (describe)
- Screen layout: visuals around the creator | split view 2a (subtitle at the seam) | split view 2b (subtitle below the face) | full-frame scenes (visual video); split view sections inside the to-camera video (which); why
- Script: `script.md` (yes or no); Hook: <type and line>
- Speed: <normal | 110 %, or the speed the brand guide sets>

## Proposed cut

| Segment | Time in source | Sentence | Shot | Note |
|---|---|---|---|---|
| 1 | 00:00.4 to 00:03.1 | "..." | A (100 %) | opening |
| 2 | 00:03.6 to 00:07.9 | "..." | B (112 %) | filler word removed at 3.2 |

Resulting duration: <N> s. Removed: <silences, filler words, false starts, repetitions, with times>. Kept: <breaths or pauses with a function>. In a recording by sentences: the chosen take of each sentence and the pauses. Framing limit: <what stays out of the frame and the crop that leaves it out>.

## Layer map

| Time | Beat | On screen | On-screen text | B-roll and function | Transition and sound |
|---|---|---|---|---|---|
| 0.0 to 2.8 | Hook | Creator shot A cut out, slow push-in; behind, the piece's world in drifting layers | Hook word at double size in the accent with a scale hit; the rest on dark background pills; no subtitles | none | zoom hit on the hook word; the objects exit toward the next shot |
| 2.8 to 6.0 | Promise | Creator shot B | "Fact" pill | none | shot cut with a cut hit |
| ... | ... | ... | ... | ... | ... |

## Space map

`tests/space-map/space-map.png` and its report: one real frame per beat with the face, the subtitle and each graphic at real size. Everything fits; what did not fit is already solved in the layer map (another place, another size, card or removed).

## Subtitles

One line of 2 to 4 words below the face, key word in the accent. Sections where the subtitle moves or is hidden, and why: <list or "none">. Planned key words per block: <list>. Names and figures to check in the transcript: <list>.

## Showpiece effects

- Brand background behind the creator: <sections and reason>
- Giant typography: <figure and section> (one per video)
- Dynamic zoom: <section, target window>
- Parallax: <screenshot and section, or "not applicable">

## Sound

- Music: <yes or no>; character: <mood, energy, BPM, instrumentation>; candidates from `find-video-audio`: <list with license>
- SFX: <list per moment: time, type, catalog file>
- Voice: normalization to -14 LUFS, cleanup <yes or no and why>

## Open items and questions for the user

- <missing material, open decisions, claims to verify>
```

In a visual video:

- **Source.** The voice recording (`source/recording/<file>`, with its duration) or "no voice", and `script.md`.
- **Proposed cut.** With voice-over, the same table without the "Shot" column: the best reading of each sentence and what was removed. A piece where nobody speaks has no cut; the section is the screen table, and the resulting duration is the sum of its last column:

  | Scene | Exact text | Characters read | Lead visual and seconds it needs | Duration |
  |---|---|---|---|---|
  | 1 Hook | "..." | 30 | label struck out, 0.6 | 3.0 |
  | 2 | "..." | 44 | figure counting up, 1.0 | 4.5 |

  The duration of a scene follows "Without voice" in `visual-video.md`, and `scripts/verify-scenes.py` checks it once the project is built.
- **Layer map.** One row per scene: its lead visual and what it does, its text, how it arrives (from behind or from the side) and its sounds.
- **Space map.** Not part of the proposal: it runs at the visual test, on frames of the built composition.
- **Subtitles.** With voice-over, the same section without the face: default position, sections where a key phrase replaces the subtitle. Without voice: "none".
- **Showpiece effects.** Only giant typography and the dynamic zoom into a window apply; the others need the creator on camera.
- **Sound.** Without voice, music is required and the "Voice" line is left out; the bed is leveled to -16 LUFS and the final encode brings the mix to -14.
- **Speed.** Without voice: "built at its final pace".

Rules:

- Every b-roll carries a function from the closed list (illustrate, show the demo, compare, establish the location, cover a cut). If it has none, it does not go in.
- Every sound is tied to a specific movement in the layer map.
- Mark as an assumption everything the user has not said (for example, the order of two takes). Ask only what changes the edit.
- When approved, change the status to "approved" with the date and do not rewrite the proposal afterwards: if the edit changes during review, add a "Changes after review" section with what was agreed.
