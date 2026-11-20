---
name: analyze-video
description: Analyze a creator's video locally, without spending tokens on the audio, to understand its content before working with it. Transcribes the audio with Whisper on the Mac, detects shot cuts and builds a contact sheet of frames. With a recording by sentences (one clip per script sentence, repeated several times), it transcribes each take, proposes the favorite, computes the exact cut of each one and serves a page where the best take is chosen. Use whenever the user shares a video or audio file (.MOV, .mp4, .m4a...) and it is necessary to understand what it says or shows, transcribe it, get subtitles, choose frames or takes, write its caption, design its cover or edit it, even if they do not explicitly ask for a transcription.
---

# Analyze Video

Understand a video without watching it: what is said comes from the local transcription and what is seen, from a contact sheet. The scripts do the heavy work on the Mac; the model reads text and looks at images.

Script paths below are relative to this skill's folder (`scripts/`, `assets/`, `references/`). Piece folders follow the workspace layout described in the repo's `CONVENTIONS.md`.

There are three cases:

- **One video or one audio file** (a take to camera, a b-roll, an export, a voice recording): analyze it with `analyze.sh` and read the result (below).
- **A recording by sentences** (many clips, one per sentence, with several repetitions): follow `references/sentence-recording.md`. In short: transcribe take by take, decide what to do with the improvised material, propose the favorite of each sentence, compute the exact cut and give the user a page where they choose the best take by listening. Cuts are tight and the last frame of a take is still part of the sentence: any expression once it is over (the mouth closing or smiling, the eyes moving, the body moving) stays out.
- **A specific gesture or expression** (for a cover, a graphic or a shot): search for it in all takes with `references/find-gesture.md`: one sheet per take, then the instant frame by frame and finally the candidates at full resolution, side by side.

Everything the user reads (chat summaries, questions) is written in the user's language, or the one the workspace instructions set. The choice page's default UI strings are in English and all of them live in the template `assets/choose-takes.html`, including the ones the scripts write: its `<meta name="label-...">` tags hold the row labels of `choose-takes.py` and the phrases `score-takes.py` and `cuts.py` build each row's reason and warning with (`scripts/labels.py` reads them). If the workspace needs another language, translate the template before running `score-takes.py`, because the reasons are saved in `sentences.json` in the template's language.

The scripts assume one person on camera: with several faces in the frame, the largest one is measured. The contact sheets of `frames.sh` are laid out for vertical video; a horizontal one leaves empty space under each frame.

## Prerequisites

Check these when the skill is invoked, before doing anything else. Check that environment variables are set without printing their values. If a required item is missing, stop and tell the user, in their language, what is missing, what this skill needs it for and how to set it up. If an optional item is missing, say once what will be skipped and continue without it. Never replace a missing item with invented values. If everything is in place, continue without mentioning this check.

| Item | Required | Used for | How to set it up |
|---|---|---|---|
| The video or audio file; in a recording by sentences, the clips in `social/<piece>/source/recording/` | Yes | What is analyzed | Shared by the user; piece folder layout in `CONVENTIONS.md` in the ai-skills repo |
| macOS on Apple Silicon | Yes, for transcription | Local transcription with mlx-whisper (`transcribe.sh`, `analyze.sh`, `takes.sh`) | Cannot be installed: mlx-whisper runs only on Apple Silicon Macs, so on other systems this skill cannot transcribe |
| `ffmpeg` and `ffprobe`, with the `libx264` and `aac` encoders | Yes | Reading, cutting and measuring video and audio in every script; the encoders make the proxies of the choice page | `brew install ffmpeg` (its build includes both encoders) |
| Python 3 | Yes | The `.py` scripts and the helpers inside the shell scripts | `brew install python` |
| `uv` | Yes | Running the Python packages on demand, in temporary environments, with Python 3.11, which it also fetches: `mlx-whisper`, `silero-vad` (it installs `torch`), `onnxruntime`, `librosa`, `numpy`, `opencv-python-headless<5` and `pillow` | `brew install uv` (other methods at [docs.astral.sh/uv](https://docs.astral.sh/uv/)) |
| Internet on the first run | Yes, once | Downloading the Whisper model (`mlx-community/whisper-large-v3-turbo` from Hugging Face, about 1.6 GB) and those Python packages; later runs work offline | Nothing to install: the first run caches them |
| Google Chrome or Chromium | Yes, for `analyze.sh` and `frames.sh` | Rendering the contact sheet with headless Chrome | `brew install --cask google-chrome`, or set `CHROME_BIN` |
| A web browser and the local port 8766 free | Yes, for the choice page | `serve-choice-page.py` serves the page at `http://localhost:8766` (another port can be passed) and the user chooses the takes in the browser | Any browser; pass another port as the second argument if 8766 is taken |
| `CHROME_BIN` | No | Path to the Chrome or Chromium binary when it is not at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` | `export CHROME_BIN="/path/to/chrome"` |
| `WHISPER_LANGUAGE` | No | Default transcription language code (`en`, `es`...); unset or `auto`, Whisper detects it | `export WHISPER_LANGUAGE=en` |
| `VOICE_PITCH_RANGE` | No | Pitch search range of `score-takes.py`, as `min-max` in Hz; without it, 60 to 500 Hz, which covers low and high adult voices and children | Only to narrow it to one voice when the pitch measurements jump an octave: `export VOICE_PITCH_RANGE=70-300` |
| `WHISPER_VOCABULARY` | No | The workspace's standing list of proper names and jargon (the creator's name, brand and product terms), comma-separated; it is always added to the Whisper prompt, before the per-call vocabulary argument | `export WHISPER_VOCABULARY="Name, Brand, term"` |
| `CONTACT_SHEET_BG`, `CONTACT_SHEET_ACCENT` | No | Hex colors of the contact sheets and frame sheets; without them, a neutral palette (`#15171C` and `#4F8CFF`) | Export the brand colors of `brand-guide/visual-identity.md`, for example `export CONTACT_SHEET_ACCENT="#4F8CFF"` |
| `brand-guide/visual-identity.md` | No | The brand colors for those variables and for the tokens of `assets/choose-takes.html` | Write it following `CONVENTIONS.md` in the ai-skills repo; `examples/crumb-theory/brand-guide/visual-identity.md` there is a filled-in example |
| `social/<piece>/script.md` with its "For recording" table | No | Assigning each take to its script sentence in a recording by sentences; without it, the takes are grouped by clip and the user confirms each sentence | Written by `write-short-video-script` |
| Skill `generate-ai-images` | No | Editing the closest frame when a gesture exists in no take (`references/find-gesture.md`); without it, the way out is a new photo | Install the `generate-ai-images` skill from the ai-skills repo next to this one |

## Analyze a video

```bash
scripts/analyze.sh "<video|audio>" <work>/analysis [language] ["Name1, term2"]
```

- `<work>` is `social/<piece>/edit/analysis/<video>` when the video belongs to a piece (every work file of a piece lives in the project); only a standalone video without a piece is analyzed in a scratch folder. When the video belongs to a piece, copy the transcript (`transcript.srt` and `transcript.txt`) next to it in `social/<piece>/source/recording/` after the analysis; no script does it. The final exported video is transcribed in `social/<piece>/edit/analysis/final-video/`, which survives the cleanup of `source/` after publishing.
- Language: the argument, else `WHISPER_LANGUAGE`, else auto-detect. The last argument adds proper names or jargon from the audio so Whisper spells them correctly; the standing terms of the workspace come from `WHISPER_VOCABULARY`.

It leaves in the folder `analysis.md` (metadata, shots and transcript with times), `transcript.txt`, `.srt` and `.json`, `words.json` (start and end of each word, used by `edit-short-video` for subtitles and cuts and by `write-short-video-script` to measure the real pace) and `frames/contact.png` (one frame per shot and one every ~3 s in long shots, at most 24; at full resolution in `frames/f_<t>.png`). An audio file has no shots and no frames: it gets `analysis.md` with the metadata and the transcript, and the transcript files.

## Read the result

1. Read `analysis.md` and look at `frames/contact.png`.
2. Cross what is said with what is seen: which shot accompanies each sentence, where there is b-roll, on-screen text, scene changes and the ending.
3. Pay attention to what the transcription does not capture: props, gestures, wardrobe, visual jokes, music, burned-in subtitles and text cards. If something small matters, extract the full frame of that moment and enlarge it.
4. Check proper names and figures against the burned-in subtitles or against what the user said. Whisper can abbreviate or confuse names, and in stretches without voice it invents text; if a word that matters is doubtful, ask about it.

## Tools

| Script | What for |
|---|---|
| `analyze.sh <video\|audio> <dir> [language] [vocabulary]` | Full analysis: transcription, shots and contact sheet (transcription only for an audio file) |
| `transcribe.sh <video\|audio> <dir> [language] [vocabulary]` | Transcription only |
| `scenes.sh <video> [threshold]` | Shots (threshold 0.3; 0.2 detects softer cuts); nothing for a file without a video stream |
| `frames.sh <video> <dir> [t1 t2 ...]` | Frames and contact sheet (without times, 12 spread out); it stops with a message if Chrome is missing or the file has no video stream |
| `uv run -q --with pillow python frame-sheet.py <video> <output> <start> <duration> [--fps 6] [--crop x,y,w,h] [--width 270] [--cols 9]` | Every frame of a short stretch with its time, to find an exact gesture (see `references/find-gesture.md`) |
| `takes.sh`, `vad.py`, `voice-bank.py`, `choose-takes.py`, `score-takes.py`, `cuts.py`, `gaze.py`, `check-cuts.py`, `serve-choice-page.py` | Recording by sentences (see `references/sentence-recording.md`) |

## Deliver

A brief summary for the user: what the video is about, its structure by times (intro, development, punchline, ending), the tone and what is seen that the audio does not say. Flag transcription doubts instead of correcting them silently. Do not describe from memory what can be checked in a frame.
