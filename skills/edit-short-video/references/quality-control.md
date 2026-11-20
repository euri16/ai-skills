# Quality control and export

The agent reviews every render before showing it: first the review below, then the binary criteria. Both are written for a talking-head piece; "What applies to each format" says which checks and criteria a visual video runs, replaces or leaves out. Whatever does not pass is fixed all together and rendered again once. The list is reported (in the user's language) to the user along with the deliverable; it is not their job to find these failures. Brand values (fonts, palette) are those of the workspace's `brand-guide/visual-identity.md`, mapped to roles in `visual-system.md`.

## Render review

Composition, before rendering:

- `check` with no errors. A lint error can switch off the layout and overlap audits, which then report 0 samples as if everything were fine.
- Overlap warnings are reviewed one by one. What is intentional is marked with `data-layout-allow-overlap` on the specific block, so that any new warning is a real problem.

Image, on the render:

- Sheets with one frame per second of the whole video, 60 frames per sheet (`ffmpeg -i <render>.mp4 -vf "fps=1,scale=216:-2,tile=10x6" ../tests/<folder>/sheet-%02d.png` writes as many sheets as the duration needs), all looked at in full, and a full-size crop of every graphic with text, at its moments of change (entries, exits, transitions) and not only mid-scene (`scripts/review-frames.sh` extracts full-size frames at given times).
- Look for: text covered by another element or touching it (12 px of space minimum), lines without subtitles or loose subtitles, dead space in brand backgrounds, elements that linger into the next idea and objects that cross a text.
- What depends on measurements (text on one line, distance between text and object, size after scaling) is measured, not estimated by eye.
- The render is watched in motion at phone size.

Audio, measured on the render:

- First syllable of each line: the level of the first 0.3 s of each take matches that of the voice clip without effects or music. If a cut hit raises or masks it, shorten its tail so it ends before the first syllable.
- `scripts/verify-sfx.py` clean: every effect at least 6 dB under the voice in a word it overlaps, at least 10 dB for cut hits. A run that reports no effects checked is a failure, not a pass.
- Music present throughout the video: the lows below 80 Hz of the render (`-af "lowpass=f=80,lowpass=f=80,volumedetect"`) stay above those of the voice master without music (`clip.mp4`, or `voice.wav`) in every window of about 5 s from when the music enters. A window equal to the master is a window without music. A piece without voice has no master to compare with: there, `ffmpeg -i <deliverable> -af silencedetect=noise=-50dB:d=0.5 -f null -` reports no silence.

## Binary criteria

System
1. No font outside the brand's display and text fonts (plus the monospace, in pieces with windows of code or data). The fonts loaded in the render (check a frame with text at full size).
2. Text sizes only from the scale in `visual-system.md`, one value per role. Animated key phrases: at most one every 20 to 25 seconds (two or three in a one-minute Reel), never with their subtitle at the same time and never a headline per beat.
3. No color outside the brand palette.
4. Same margins and alignments throughout the piece.

Zones
5. No essential element outside x 60 to 1020 and y 210 to 1680, nor in the button column (x 945 to 1080 between y 1095 and 1850).
6. No subtitle box ends below y 1400.

Motion
7. No linear animation except continuous drifts.
8. Entries of 300 to 500 ms (up to 800 full screen); exits of 150 to 250 ms and shorter than their entry. Subtitles (100 to 150 ms in, 100 ms out) and the emphasis zoom (120 ms) have their own numbers in `visual-system.md`.
9. Bounce on only one element per scene and never on subtitles.
10. No zoom or shot change without a change of idea, and none without sound.
11. Continuous motion in parallax and drifts: no speed jumps.

Density
12. Never more than two simultaneous graphics besides the creator.
13. Every b-roll with a function named in the proposal and synced with the line.
14. Text that is not a subtitle: 6 words at most, names the idea.
15. Subtitles on one line of 2 to 4 words, in the position the piece set (by default below the face while the creator is on camera), no emojis and no all-caps text, names and figures checked.
16. No frozen frame of the creator anywhere in the piece.
17. Dynamic zoom: the window fills the width and does not cut text.

Legibility and composition
18. No text below 36 px on the 1080 canvas (labels, job titles, code and screenshots included); supporting text does not look tiny or compete with its headline.
19. The accent color does not saturate the screen (judged case by case); balanced lines, no single word alone on the last line of a headline or a punchline.
20. No shape or graphic element touches a text; no text covers the creator's face or gets in the way of reading by crossing their body; no dead space in cards and brand backgrounds.

Sound
21. Voice and final mix between -16 and -14 LUFS integrated, with the true peak at -1 dBTP or lower: `scripts/loudness.sh` exits with 0 on `clip.mp4` and on the deliverable.
22. Every punch-in, shot cut, zoom and card entry carries a sound; no sound on a cut without a change; never two identical sounds in a row; no SFX masks a syllable (`verify-sfx.py` clean; cut hits attack on the cut frame).
23. Music about 20 dB below the voice, without lyrics, present with no gaps or restarts from when it enters; license recorded in `piece.md`.

Color
24. All clips in Rec. 709; no HDR clip without `--sdr`.
25. The creator's skin consistent across shots.

Cuts and framing
26. No frame shows anything beyond the framing limit set at ingest (what the brand guide or the user wants out of the frame), including the sections with the creator cut out and the intro.
27. No take shows the face changing on the way in or out (from rest to speaking, eyebrows, relaxing, the lips closing, pressing or smiling after the last word, looking away, starting a movement): in a recording by sentences, each take uses its exact cut from `sentences.json` and the sheets of `analyze-video/scripts/check-cuts.py` with `chosen` confirm it. In the render, check the frame of every join.
28. Between takes, only the gap of the exact cut and the pauses of the script with real image: `scripts/verify-cut.py` clean on the master (no frozen frame, no click at a join, no speech inside a pause, frames and audio equal to `cut.json`).

Delivery
29. The hook is live: slow push-in, one or two zoom hits with sound (never one per word), the piece's world or darkened b-roll moving from frame 0, the hook word at double size in the accent and the rest on dark background pills without covering the gesture, and an exit that leads to the next shot (or a still hook declared as the sketch's joke). Unless the brand guide defines them: no logo or card before the hook, no logo as a signature and no closing card. If the piece belongs to a series with a defined intro, the intro goes right after the hook and matches the one in the series plan. The piece ends on the payoff and the call to action the script closes with, and the cut is hard.
30. Duration within what is recommended for the platform.
31. Correct export preset (below) and file in `social/<piece>/export/`.

Visual video
32. The hook builds from frame 0: its first block and first word are on screen on frame 0, the headline and the lead visual are complete within 2 s, and nothing stays half entered after that.
33. `scripts/verify-scenes.py` exits with 0 on the project: every scene starts on its word (with voice-over) or lasts its reading time without dragging (without voice), with no gap or overlap between scenes.
34. Every scene has one lead visual that acts once and then stays still; only the closing scene may be text only. Scene changes are moves from behind or from the side, each with its sound, never a fade.
35. A fact that rests on a source shows the source in the brand window, with its key line marked and its origin and date legible on the phone.
36. The piece closes on the payoff and the call to action, held for its reading time, then the hard cut.

## What applies to each format

A check that does not apply to a format is not run on it: every script below exits with a non-zero code when the file it measures is missing, so none of them can pass by seeing nothing.

| Check | Talking head | Visual video with voice-over | Visual video without voice |
|---|---|---|---|
| `scripts/probe-media.sh` | Every source file | The voice recording and any b-roll | Any b-roll |
| `scripts/build-cut.py` | `master` or `single` with `--vf`: `clip.mp4` | `single --voice-only`: `voice.wav` | Not run: there is no cut |
| `scripts/verify-cut.py` | Frozen image, clicks, pauses, length | Clicks, pauses, length; no image to check | Not run: no `cut.json` |
| `scripts/loudness.sh` on the master | `clip.mp4` | `voice.wav` | Not run; the music bed is leveled with `--target -16` |
| `scripts/space-map.py` | Before the proposal is presented, on frames of the recording | At the visual test, on `"image"` frames of the composition | At the visual test, on `"image"` frames of the composition |
| `scripts/verify-scenes.py` | Not run: the composition has no scenes | Scenes on their words, subtitles present | Reading time of each scene, music present, no subtitles |
| `scripts/verify-sfx.py` | Effects against the voice of `clip.mp4` | Effects against the voice of `voice.wav` | Not run: there is no voice to mask |
| `scripts/check-clips.sh` | Prepared b-roll | Prepared b-roll, if any | Prepared b-roll, if any |
| `check`, `snapshot`, frame sheets, `scripts/check-render.sh` | Yes | Yes | Yes |
| `scripts/final-encode.sh` and its `loudness.sh` measurement | Yes, at the speed of the piece | Yes, at the speed of the piece | Yes, without `--speed` |
| First syllable of each line | Yes | Yes, against `voice.wav` | Not applicable |
| Music present | Lows against `clip.mp4` | Lows against `voice.wav` | `silencedetect` reports no silence |
| Transcript of the export with `analyze-video` | Yes | Yes | Not run: `piece.md` records the scenes and their durations |

| Criteria | Talking head | Visual video with voice-over | Visual video without voice |
|---|---|---|---|
| 1 to 9, 11 to 13, 17 to 19, 21, 23, 24, 30, 31 | Apply | Apply | Apply (21 on the deliverable only; 23 with the music as the lead, not under a voice) |
| 10, 22 | Apply | Apply, reading "scene change" for "shot change" and "cut" | Apply the same way; nothing can mask a syllable |
| 14 | Apply | Applies | Replaced by the screen text limits of `visual-video.md` |
| 15 | Apply | Applies, in the default subtitle position | Not applicable: no subtitles |
| 16, 25, 26, 27 | Apply | Not applicable: no camera take | Not applicable |
| 20 | Applies | Applies, without the face clause | Applies, without the face clause |
| 28 | Applies | Applies to `voice.wav`, without the image clauses | Not applicable |
| 29 | Applies | Replaced by 32 | Replaced by 32 |
| 32 to 36 | Not applicable | Apply | Apply |

## Export preset (one file for the four platforms)

- MP4, H.264 High, 1080x1920, 30 fps, 8-bit 4:2:0, BT.709 tagged, VBR at about 11 Mbps (peak 20), a keyframe every second, moov at the front.
- AAC-LC 48 kHz stereo 256 kbps.
- Duration of 3 minutes or less (Instagram does not recommend longer Reels to non-followers; Shorts up to 3 minutes).
- Render: `npx --yes hyperframes@0.8.229 render -q delivery --fps 30`; then `scripts/final-encode.sh` applies speed, loudness (-14 LUFS, true peak target -1.5 dBTP) and this preset in a single encode and measures the result ("Speed and final encode" in the recipes).
- Light version, only if the piece goes by email or a messaging app and the master does not fit: `<slug>-light.mp4` in `export/`, at 720x1280 capped at 1.9 Mbps, about 11 MB per minute even if the piece has a lot of animation, and sharp on the phone: `ffmpeg -i final.mp4 -vf "scale=720:1280:flags=lanczos" -c:v libx264 -preset slow -crf 23 -maxrate 1900k -bufsize 3800k -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -c:a aac -b:a 128k -movflags +faststart final-light.mp4`. Without `-bufsize`, x264 ignores the `-maxrate` cap. When done, check that it lasts the same as the master (an interrupted encode leaves a short file that looks valid).

## Platform limits (verified on 2026-10-27)

| | Instagram Reels | TikTok | YouTube Shorts | LinkedIn |
|---|---|---|---|---|
| Resolution and fps | 1080x1920, 30 to 60 fps (minimum 30 in app) | 1080x1920, 23 to 60 fps | 1080x1920, upload at the recording rate | 1080x1920, 10 to 60 fps |
| Size and bitrate | 300 MB via API, 25 Mbps maximum | 4 GB | 8 Mbps at 30 fps, 12 Mbps at 60 fps (recommended) | 5 GB, 192 kbps to 30 Mbps |
| Duration | up to 3 min recommended to non-followers | up to 10 min | up to 3 min since October 2024 | up to 15 min, 15 s to 2 min recommended |
| Safe zone | 14 % top, 35 % bottom, 6 % sides (official for ads); organic, measured: full width, y 210 to 1680 (`visual-system.md`) | official template, depends on the caption | Google template: x 48 to 887, y 288 to 1247 | not documented |
| Subtitles | burned-in and automatic | burned-in and automatic | burned-in and automatic | burned-in; SRT only from desktop |
| Audio | no official LUFS | no official LUFS | normalizes down toward -14 LUFS (observed) | no official LUFS |
| HDR | preserves Dolby Vision only on iOS; HDR uploads have come out overexposed | not documented | converts to SDR automatically and imperfectly | not documented |
| Originality | penalizes watermarks from other apps, borders, mostly-text video, reposts | reused content without added value is ineligible for the feed; tiny text with keywords is spam | no monetization for reused or mass-produced content | not documented |

No commercial music burned in: TikTok requires its commercial library for branded content and YouTube blocks Shorts longer than one minute with a claim.
