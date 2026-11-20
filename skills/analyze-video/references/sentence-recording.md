# Recording by sentences

When the creator records one clip per script sentence (the "For recording" table of `script.md`) and repeats each sentence several times, the work is: transcribe each repetition, decide what to do with the improvised material, prepare the choice of the best take with the exact cut of each one, and hand `edit-short-video` the chosen take of each sentence.

Paths: the scripts are in this skill's `scripts/` folder; `<rec>` is `social/<piece>/source/recording`, `<analysis>` is `social/<piece>/edit/analysis` and `<takes>` is `social/<piece>/edit/takes`.

## 1. Transcribe take by take

```bash
takes.sh <rec> <analysis> [language] ["Name1, term2"]
```

Splits each repetition by the speech stretches that Silero VAD detects (`vad.py`, local) and runs Whisper on each take separately. Silero tells speech from noise, so the split does not depend on the recording level or on room noise, discards stretches without voice and separates two repetitions said with only a breath between them. On the whole clip, Whisper merges the repetitions into one line and invents text in the silences (YouTube filler such as "subscribe to the channel", the prompt's vocabulary); that is why it is transcribed take by take. It leaves `takes.md` (file, take, time, duration and text) and `takes.json` (the same, with the time of each word relative to the clip; a take without real speech has the text `(no voice or noise)`). A segment counts as invented when Whisper's confidence is low, the text loops, it echoes the prompt or it is a known YouTube filler phrase (the list in `takes.sh`, `HALLUCINATIONS`, covers Spanish and English; add the phrases of another language there); in a language written in the Latin alphabet (the requested one, or the one Whisper detects), also when it has letters of another script. Symbols and punctuation never count, and languages written in other scripts skip that last test. Language and vocabulary work as in `transcribe.sh` (`WHISPER_LANGUAGE`, `WHISPER_VOCABULARY`). To see the framing, `frames.sh` on one or two clips is enough.

## 2. Review what was said

- Assign each take to its script sentence. Whatever does not match is intentional improvisation: it is treated as an editorial option and new claims are verified before using them.
- Ask the user (with the structured question tool, if the agent has one) what to do with improvised material that changes the script or claims something unverified, with the full text of each version in the question (questions are written in the user's language).
- Discard incomplete takes, takes with stumbles or with a version the user discarded.

## 3. Prepare the sentences

```bash
python3 choose-takes.py <rec> <analysis> <takes> "<title>"
```

The first time it writes `<takes>/sentences.json` as a draft, one row per file with all the takes that have voice. It is edited by hand before continuing:

| Field | What it is |
|---|---|
| `clip`, `part`, `sentence` | Clip number and script part (Hook, B1...) and the decided sentence |
| `file`, `takes` | The clip and its candidate takes; a list such as `[4, 5]` joins two consecutive takes (a sentence split in two with its pause) |
| `intonation` | `open` if the sentence continues in the next clip; `closed` by default |
| `end_gesture` | Optional, `true` only when the creator ends that sentence with a closing gesture the brand guide defines, if any |
| `hold` | Seconds the shot continues after the voice in all takes, when the script asks for a reaction after the sentence ("a second and a half facing the camera"): the reaction is content and is not cut like a face change |
| `favorite`, `reason`, `metrics` | Written by `score-takes.py` by voice (each take's metrics with its `score`); `cuts.py` can then change the favorite for a pause held still or eyes still at the end, and `reason` says so; `favorite_locked: true` keeps a favorite set by hand. `reason` is written with the phrases of the template (`labels.py`) |
| `cuts`, `voice`, `face`, `final`, `warning` | Written by `cuts.py`: the cut of each take, its measured voice edges, the face area of the clip in fractions of the frame (`[x0, y0, x1, y1]`, which `check-cuts.py` crops to), what the image does at the end (`eyes_move_before_end`, `still_pause`) and a warning, in the template's phrases, when no take meets the pause or the eyes rule; `manual_out: {"Take N": s}` sets an out point by hand |
| `pause` | Seconds of silence the script asks for after the sentence (after a punchline, before the payoff); the edit makes it by letting the same take run while the person stays still (see "Pause") |
| `chosen` | The take chosen by the user |

Takes are labeled `Take N` (or `Take 4+5` for joined takes) in every field keyed by take; the page shows them with the template's word for "Take" (`label-take`).

## 4. Propose the favorite

```bash
uv run -q --python 3.11 --with librosa python score-takes.py <rec> <takes>
```

Measures in each take the fidelity to the text, the longest pause, the pace, the energy, the expressiveness of the pitch and whether the voice drops or stays up at the end according to its `intonation`, and writes the favorite with its reason. The pitch is searched between 60 and 500 Hz, wide enough for any adult or child voice; `VOICE_PITCH_RANGE` narrows it (see Prerequisites in `SKILL.md`). Review the surprising ones, such as a take that lasts twice as long or one that changes words: the reason flags it and names the best exact take.

## 5. Compute the exact cut

```bash
uv run -q --python 3.11 --with numpy --with "opencv-python-headless<5" --with silero-vad --with onnxruntime python cuts.py <rec> <takes> [x0,y0,x1,y1]
```

Writes in each row the in and out point of each take, in seconds of the original clip, so that the video does not show the face changing at the start or at the end.

| Rule | Value |
|---|---|
| Voice | Energy in 10 ms windows, with a threshold 32 dB under the peak and at least 6 dB above the background noise. A sound stretch counts as voice only if Silero hears speech in it: a breath or a mouth click before speaking does not move the in point earlier, and the consonant joined to its vowel comes in whole. An edge stretch separated from the sentence by 150 ms of silence and 12 dB quieter than it (a breath or a murmur before or after) does not come in either. Silero does not set the edge, because it marks the out point about 300 ms late and sometimes misses a soft consonant. It is anchored to the first and the last word (a laugh or a comment afterwards does not come in). If the recording starts while speaking, Whisper puts the first word at 0.0 even if the voice arrives later: the in point is searched up to the end of the first word. |
| Face | Detected automatically and its movement measured frame by frame, on frames that keep the clip's proportions (vertical, horizontal or square). If it is not detected, `cuts.py` says so and uses the center of the frame: pass the area as the last argument in fractions of the frame. The area used is saved in the row as `face`. |
| In point | Between 0.05 and 0.02 s before the voice, after the last face change. Cuts are tight: no air beyond the breath between sentences. |
| Out point | 0.04 s after the audible end of the last syllable (0.02 s if the sentence is `open`), including a final "s" (its hiss is soft and the energy threshold misses it: `gaze.py` follows the energy above 4 kHz). Any expression once the sentence is over stays out: the face relaxing, the mouth leaving the shape of the last syllable (closing, pressing, smiling), the eyes moving (a glance at the next sentence shows even if it lasts a few frames), the body leaning or a hand entering the frame, searched up to 0.25 s after the voice (0.12 s if the sentence is `open`). The cut goes before the first one, even if it lands right at the end of the voice and trims the tail of the final consonant (floor: end of the voice plus one frame). The eyes and the mouth are measured on their bands, aligned on the face so the head does not count; the body, on the whole frame (`gaze.py`). If the eyes move before the last syllable ends, the word stays whole and the take is marked: among takes with a close voice score, the one with still eyes wins. This air plus the next in point is the whole breath between sentences: the edit adds no gap. |
| End gesture | Only in rows with `end_gesture`. A closing gesture with intent is content, not a face change to leave out, so the take runs until the gesture is complete: `cuts.py` places the out point where the image detail collapses after the voice (the frame with the least detail in the 0.4 s after it first falls under a quarter of its level while speaking) plus three frames. If the detail never collapses, `cuts.py` says so and the out point is set with `manual_out`. |
| Pause | With `pause`, the silence runs on the same take after its out point, with its real image and audio, only while the person stays still and looking at the camera: `cuts.py` measures that stillness (`still_pause`) up to the first jump of the frame or the eyes. A take that holds at least 80 % of the pause has it; if the favorite does not and another take with the same text does, that one becomes the favorite. If none does, there is no pause, the take is cut when the voice ends and the row gets a `warning` to state in the proposal. Never frames from another take. |
| Held reaction | With `hold`, the out point is the end of the voice plus those seconds, without going past the start of the next take of the clip. When reviewing the favorite, check that this take has the reaction: the score only listens, and if the favorite does not have it, another one is set with `favorite_locked` and its reason. |
| Manual out point | `manual_out` holds the shot on a visual punchline (an object landing on the table after the last word) while the face stays still; check it first with frames. It is kept when recomputing. |

To change how the voice is detected (`vad.py`), measure before and after with `voice-bank.py <rec> <analysis>` (same dependencies as `cuts.py`, without opencv): it degrades the audio of the takes with noise, lower level, a click and breaths before and after the sentence, and reports how much the edges move. The change goes in only if it does not worsen those figures and leaves the already approved cuts of a piece unchanged (run `cuts.py` on a copy of its `sentences.json` and compare).

Check the cuts with frames:

```bash
python3 check-cuts.py <rec> <takes> social/<piece>/edit/tests/cuts favorite
```

Four frames of the face per sentence, cropped to the `face` area `cuts.py` saved in the row (the center of the frame if the row has none): 0.12 s before the in point, the in point, the last frame of the cut (0.02 s before the out point) and 0.12 s after the out point. Look at the sheets at full size: the in point looks the same as the previous frame and the out point shows no change. The mouth is too small on these sheets to judge: in the hook, the punchlines and any take with a smile, check the last frames with `frame-sheet.py` at 50 fps cropped on the mouth, and confirm that the last frame shown still has the shape of the last syllable. A failing cut is fixed in `cuts` (or with `manual_out`) and checked again.

## 6. Provide the choice page

Run `choose-takes.py` again: it leaves a light proxy per take, cut with its exact cut so it looks as it would enter the video, and `choose-takes.html` (template in `assets/choose-takes.html`), with one row per sentence, the favorite marked with its reason and already selected. Review the page at full size and serve it:

```bash
python3 serve-choice-page.py <takes>          # in the background; prints http://localhost:8766/choose-takes.html
```

Open the local link with `open`, never the file: every selection is saved automatically as `chosen` in `sentences.json` and on reload the choice is restored (opened as a file, only the "Copy choice" button remains). Explain how to use it: listen to 2 or 3 takes per sentence, make sure open sentences do not drop the voice at the end and, in the hook and the punchlines, give more weight to expression than to perfection. If the person notices a face change at the start or end of a take, that cut is adjusted.

The same server also serves the sounds page of `find-video-audio` (`serve-choice-page.py <candidates_dir> 8767 sounds.json choose-sounds.html`). Both pages use its protocol: `GET /state` returns `{clip: chosen}` and `POST /choose` with `{"clip", "choice"}` saves `chosen` in that row. The `clip` id is compared as text (`"2"` and `2` are the same row) and an id that matches no row answers 404.

## 7. Close the choice

When the user says they are done: stop the server, read `sentences.json` (whatever did not change keeps the favorite), record the choice with its cut in the "For recording" section of `script.md` and run `check-cuts.py` again with `chosen`. `edit-short-video` assembles each chosen take from the original clip with its exact cut (`edit-short-video/scripts/build-cut.py`).
