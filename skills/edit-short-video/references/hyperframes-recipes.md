# HyperFrames recipes for the edit

Verified with `hyperframes` 0.8.229 (the pinned version) on macOS with Apple Silicon and a Homebrew ffmpeg built without libass, drawtext or zscale. Local render: about 4 s of processing per second of video at 30 fps. `<skill-dir>` in a command stands for the path of this skill's folder; replace it with the real path. Piece paths (`social/<piece>/...`) are relative to the workspace root (layout in the repo's `CONVENTIONS.md`); the `npx` commands and the paths that start with `assets/`, `renders/` or `clip.mp4` run from the project folder, `social/<piece>/edit/project/`.

Before the first composition of the session, invoke the `hyperframes-core` skill to have the full contract. Summary of the contract these recipes use: root `<div data-composition-id="main" data-start data-duration data-width data-height data-fps>`; every element visible over time carries `class="clip"`, `data-start`, `data-duration` and `data-track-index`, and a stable `id`; a `<video>` carries `data-has-audio`, and `<video>` and `<audio>` carry `data-volume`; a single paused GSAP timeline in `window.__timelines["main"]`; HyperFrames finds it and plays it deterministically.

## 1. Project

```
social/<piece>/edit/project/
  hyperframes.json      {"$schema":"https://hyperframes.heygen.com/schema/hyperframes.json","paths":{"blocks":"compositions","components":"compositions/components","assets":"assets"},"media":{"autoProxy":true}}
  index.html            the main composition
  clip.mp4, cut.json    the cut master and its times (see 2); voice.wav instead of clip.mp4 in a visual video with
                        voice-over, and neither in one without voice
  assets/brand.css      the brand tokens (see below)
  assets/fonts/         fonts.css, the stylesheet that loads the brand's display and text fonts, and the font files it
                        points at when it loads them from local files
  assets/logo.png       only if the piece uses the brand background with the faint logo behind: the logo from
                        brand-guide/assets/logo/ reduced to about 3 times its on-screen size with `sips -Z` (or its SVG)
  assets/icons/         only the SVGs from brand-guide/assets/icons/ the piece uses
  assets/textures/      the brand texture from brand-guide/assets/textures/, if the brand has one and the piece uses a brand background
  assets/broll/         prepared b-roll
  assets/sfx/, assets/music/   what find-video-audio delivers
  renders/
```

`assets/brand.css` holds the tokens of `visual-system.md` ("Brand tokens") with the values of the workspace's `brand-guide/visual-identity.md`; every recipe below reads them through `var(...)`. The values shown belong to Crumb Theory, the fictional example brand of the ai-skills repo (its palette: Rye, Crust, Flour, Berry, Sage):

```css
:root{
  --bg:#2A211B;          /* dark background (Rye) */
  --bg-rgb:42,33,27;
  --ink:#2A211B;         /* deep ink: window bars, depth layers (Rye) */
  --on-accent:#F7F1E6;   /* text on the accent (Flour) */
  --mid:#7A8F5C;         /* mid tone (Sage) */
  --accent:#C23B5A;      /* accent (Berry) */
  --accent-rgb:194,59,90;
  --light:#F7F1E6;       /* light neutral (Flour) */
  --text:#F7F1E6;        /* subtitles and headlines on dark (Flour) */
  --font-display:"Fraunces";
  --font-text:"Work Sans";
  /* optional, only for pieces that show windows with code or data */
  --code-bg:#6B4A33;     /* window background (Crust) */
  --font-mono:ui-monospace,"SF Mono",Menlo,monospace;   /* the brand's monospace; Crumb Theory uses the system stack */
}
```

`fonts.css` is a copy of `brand-guide/assets/fonts/fonts.css`, which loads the families named in `--font-display` and `--font-text`. It works in either of two ways:

- **Web fonts.** The file loads the families with `@import` from a font service, as the Crumb Theory example does with Google Fonts. Copy it as it is; every render then needs network access.
- **Local files.** The file has one `@font-face` per font and the font files sit next to it. Copy the file and the fonts it points at (renamed without spaces) and keep only the faces the piece uses. Example with a static display font and a variable text font:

```css
@font-face{font-family:"Fraunces";font-weight:700;src:url("Fraunces-Bold.woff2") format("woff2")}
@font-face{font-family:"Work Sans";font-weight:100 900;src:url("WorkSansVariable.woff2") format("woff2-variations"),url("WorkSansVariable.woff2") format("woff2")}
```

Either way, check in the first `snapshot` that the brand fonts loaded: a missing font is replaced by a wider one and the text overflows its box. A monospace given as a system stack renders with whatever monospace the render machine has; check it in the same snapshot.

Fonts and logos are not bundled with this skill; they come from the workspace.

## 2. Preparing the clips

`<skill-dir>/scripts/probe-media.sh <file>` prints codec, size, fps, color space and whether it is HDR. Every video that enters the composition is prepared the same way: 30 fps, Rec. 709, clean H.264 at CRF 10 with a keyframe every 15 frames. The recording goes through `build-cut.py` ("Cut master" below), which applies those settings and the framing given in `--vf`; a clip that enters whole, without cuts, is prepared with the same settings:

```bash
# optional crop (crop=width:height:x:y) before the scale, to reframe
ffmpeg -y -ss <start> -t <dur> -i source/recording/<file>.mov \
  -vf "scale=1296:2304:flags=lanczos,fps=30" \
  -c:v libx264 -crf 10 -g 15 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a aac -b:a 192k <output>.mp4
```

HyperFrames accepts the original 60 fps HEVC without converting, but preparing the clip at 30 fps and H.264 speeds up the render and fixes the color; a 25 fps source is converted the same way (ffmpeg duplicates frames). If `probe-media.sh` flags HDR, render with `--sdr`.

B-roll from recaps or long clips, at CRF 10 and at the size it is shown at its largest (1080x1920 at full screen; canvas size times its largest scale if it is zoomed, never above the source):

```bash
# n: final duration in frames = round(output * 30); d: source seconds; f = output/d
ffmpeg -y -ss <start> -t <d - 0.1> -i recap.mp4 \
  -vf "scale=1080:1920:flags=lanczos:force_original_aspect_ratio=increase,crop=1080:1920,setpts=<f>*PTS,fps=30,tpad=stop_mode=clone:stop_duration=0.4,setpts=N/30/TB" \
  -an -r 30 -frames:v <n> -c:v libx264 -crf 10 -g 15 -pix_fmt yuv420p assets/broll/<name>.mp4
```

Photos and images (b-roll photos, straightened or cleaned objects, screenshots) enter the composition as lossless WebP (`cwebp -lossless -z 9 -metadata none`, checking that the pixels match the original) or PNG, at the resolution of the original; the size on screen is set in the composition. A photo that is shown larger than its pixels allow is replaced by a better source (a dedicated photo or a sharper frame), never upscaled.

- `-ss` and `-t` go before `-i`: with `-t` after it, ffmpeg cuts the output to the source duration and the slowed-down clip stays frozen for the rest of its time on screen.
- The final duration is set with `-frames:v`, not with `-t` (which loses frames); `setpts=N/30/TB` regularizes the timestamps and `tpad` ensures there are enough frames.
- Subtract 0.1 s from the source range of an already edited recap: its last frame usually belongs to the next shot.
- If the clip is stretched more than 130 %, replace `fps=30` with `minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1` (interpolated slow motion) and check frame by frame that there are no artifacts.
- Check all prepared clips with `<skill-dir>/scripts/check-clips.sh assets/broll`: it lists those that have a shot cut inside, and fails if the folder has no clips or one cannot be read.

Punch-ins: do not crop the clip; they are done in the composition with `scale` on `#cam` (origin 50 % 40 %) so sizes can alternate. For that scale not to enlarge pixels, the master has the canvas size times the largest scale used on `#cam`, taken from the original and never above it, and the `<video>` shows it at 1080x1920 with `object-fit: cover`:

| Original | `--vf` of the master | Largest scale on `#cam` |
|---|---|---|
| 4K vertical (2160x3840) | `scale=1296:2304:flags=lanczos` | 1.2 (a larger master allows more, up to 2.0 with `scale=2160:3840`) |
| 1080x1920 | `scale=1080:1920:flags=lanczos` | 1.15: there are no spare pixels, so this is the one enlargement accepted |

Check it once per piece: the crop of the face in a punch-in frame from `snapshot` looks as sharp as the same crop at 100 %.

### Cut master

HyperFrames receives the recording already cut: `clip.mp4`, with `cut.json` next to it. The layer map timings are expressed on that cut clip. `build-cut.py` writes both, from a recording by sentences or from the cut list of a single take, and `verify-cut.py` measures them:

```bash
# recording by sentences: the chosen take of each row of edit/takes/sentences.json
python3 <skill-dir>/scripts/build-cut.py master social/<piece> --vf "scale=1296:2304:flags=lanczos"
# single take: a cut list and the words.json that analyze-video left for that take
python3 <skill-dir>/scripts/build-cut.py single social/<piece> social/<piece>/edit/cuts.json \
  --vf "scale=1296:2304:flags=lanczos" --words social/<piece>/edit/analysis/<take>/words.json
uv run -q --python 3.11 --with numpy --with silero-vad --with onnxruntime python <skill-dir>/scripts/verify-cut.py social/<piece>/edit/project
```

The cut list of a single take is a JSON with the file name in `source/recording/` and the segments in order, in seconds of the original:

```json
{"file": "<take>.mov",
 "segments": [{"start": 0.42, "end": 3.10, "sentence": "..."},
              {"start": 3.62, "end": 7.90, "sentence": "..."}]}
```

`cut.json` names its master (`"master": "clip.mp4"`) and holds, for each segment: the instant of the image change (`cut`), the cut of the take (`start`, `end`), the voice (`voice_start`, `voice_end`), the pause after it, the source range (`source`) and the time of every word on the master. Subtitles, animations, sounds and every other video of the piece are computed from `cut.json`, never from measurements of an encoded file. The rules `build-cut.py` applies:

- **Between sentences, only the gap of the exact cut.** The out point of one take plus the in point of the next is the breath between sentences. No gap is added and no frame is frozen: a still image between two sentences looks like a stuck video. In a single take, the cut list removes silences on the same continuous take, so the image between sentences is always real.
- **Pauses with real image.** In a recording by sentences, the silence the script asks for after a sentence is written as `"pause": s` in its row. It runs on the same take after its out point, only while the creator stays still and looking at the camera (`still_pause`, measured by `cuts.py` of `analyze-video`) and up to the start of the next attempt of the same clip minus 0.05 s (the attempts come from Silero VAD in `takes.json`). If that leaves less than 80 % of the pause, there is no pause: the take is cut when the voice ends and the script says so. Never frames from another take. In a single take, a pause is simply part of a segment.
- **Whole frames, computed.** Each segment lasts `round((out - in) * 30)` frames plus its pause, cut with `trim=end_frame` and the audio with `atrim` to the same duration. The duration that `ffprobe` gives for an encoded file includes AAC padding, and adding it up sentence by sentence shifts the times.
- **Fades of 8 ms in and 12 ms out** on the audio of every segment: without them, every join clicks when the wave is not at zero, and they are too short to eat a syllable.
- **No frame through an image.** Repeating or freezing a frame via PNG or JPG changes its color (YUV to RGB and back); if a frame has to be held, it is done inside the video with `tpad=stop_mode=clone`.
- **A segment with no words stops the build.** If the cut of a take holds no word of its transcript, the cut is wrong or the segment is silent on purpose; in the second case, give its `"voice": [start, end]`.

The framing goes in `--vf`, or per row or segment with `"vf"`. Sections that need another framing of the same takes (split view sections, the intro) are rebuilt with `build-cut.py video <project>/cut.json <dir> --vf "<framing>" [--clips 05,06]`, which cuts each segment with exactly the frames of the master and leaves it frame-aligned with its audio.

The voice-over of a visual video goes through the same script with `single --voice-only` in place of `--vf`: it takes only the audio of the recording and writes `voice.wav` and a `cut.json` whose master is `voice.wav`, with the same rules for frames, fades and words (`visual-video.md`, "With voice-over"). `build-cut.py video` refuses that `cut.json`: it has no image.

`verify-cut.py` reads the master `cut.json` names. On `voice.wav` the frozen image check does not apply and its output says so; the clicks, the pauses and the length are measured the same. It measures what the eye misses and fails with exit code 1: three identical consecutive frames (a frozen image, also after another encode), a click at a join (largest sample jump over 2 times the normal one) and speech inside a pause (Silero VAD; a breath is not speech), plus frames and audio matching `cut.json`. It imports `vad.py` from the sibling `analyze-video/scripts/` folder, so both skills are installed side by side.

### Voice level

The voice is leveled on the master (`clip.mp4`, or `voice.wav` in a visual video with voice-over, with the same commands), before composing, so every sound is mixed against a known level:

```bash
<skill-dir>/scripts/loudness.sh clip.mp4            # in range: -16 to -14 LUFS integrated, true peak -1 dBTP or lower
<skill-dir>/scripts/loudness.sh clip.mp4 --fix      # writes clip-norm.mp4 (video copied) at -14 LUFS, true peak target -1.5 dBTP
mv clip-norm.mp4 clip.mp4
```

Cleanup is moderate and only when the recording needs it (a hum, a constant hiss); listen before and after, and skip it if the voice loses body. It goes before the normalization:

```bash
ffmpeg -i clip.mp4 -c:v copy -af "highpass=f=80,afftdn=nr=10:nf=-40" -c:a aac -b:a 256k -ar 48000 clip-clean.mp4
```

After either step, run `verify-cut.py` again: the audio still has to match `cut.json`.

## 3. Composition skeleton

```html
<!doctype html><html lang="en" data-resolution="portrait"><head><meta charset="UTF-8">
<meta name="viewport" content="width=1080, height=1920">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<link rel="stylesheet" href="assets/fonts/fonts.css">
<link rel="stylesheet" href="assets/brand.css">
<style>
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:var(--bg)}
body{font-family:var(--font-text),Helvetica,Arial,sans-serif}
#cam{position:absolute;inset:0;transform-origin:50% 40%}
#cam video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="45" data-width="1080" data-height="1920" data-fps="30">
  <div id="cam"><video id="a-roll" class="clip" src="clip.mp4" playsinline data-start="0" data-duration="45" data-track-index="1" data-has-audio="true" data-volume="1"></video></div>
  <!-- layers -->
</div>
<script>
var tl = gsap.timeline({paused:true});
/* animations */
window.__timelines = window.__timelines || {}; window.__timelines["main"] = tl;
</script></body></html>
```

Set `lang` to the language of the piece. Every visible layer is a `.clip` with its time window; GSAP animates within that window. Two clips on the same track never overlap in time. A visual video does not start from this skeleton but from the base template in `assets/visual-video/`, which has no `#cam` and no `#a-roll` (`visual-video.md`). Track convention, the same in every recipe:

| Track | Content |
|---|---|
| 0 | Background behind the creator (brand background or context b-roll) |
| 1 | Camera (`#a-roll`); in a visual video, the voice-over (`#voice`) |
| 2 | The creator's cutout |
| 3 | B-roll (full screen, picture in picture); in a visual video, the scenes |
| 4 | Subtitles |
| 5 to 9 | Headlines, pills, windows and other graphics |
| 10 and 11 | SFX (11 for a sound that overlaps another) |
| 12 | Music |

## 4. Recipes

### Subtitles

```html
<div id="cap-3" class="cap clip" data-start="6.2" data-duration="1.9" data-track-index="4">the <span class="k">biggest hit</span> of the day</div>
```
```css
.cap{position:absolute;left:50%;transform:translateX(-50%);bottom:530px;max-width:880px;background:rgba(var(--bg-rgb),.80);color:var(--text);border-radius:24px;padding:18px 38px;font:700 64px/1.1 var(--font-text);text-align:center;white-space:nowrap;opacity:0}
.k{color:var(--accent)}
```
```js
document.querySelectorAll('.cap').forEach(function(el){var s=+el.dataset.start,d=+el.dataset.duration;
  tl.fromTo(el,{opacity:0,y:8},{opacity:1,y:0,duration:0.12,ease:'power2.out'},s);
  tl.to(el,{opacity:0,duration:0.1,ease:'power2.in'},s+d-0.1);});
```
`bottom:530px` puts the bottom edge of the box at y 1390, the default position of "Subtitles" in `visual-system.md` (a one-line box at 64 px is about 106 px tall, so it runs from about y 1284 to 1390). Generate the blocks from the `words` of `cut.json`: group 2 to 4 words, breaking at pauses longer than 250 ms and at punctuation, without one-word blocks; each block starts at the first word (never before the `start` of its segment) and ends at the end of the last one; mark the key word with `<span class="k">`. A block that does not fit on one line is split into two blocks, never into two lines.

### Beat headline

```html
<div id="headline-1" class="headline clip" data-start="0" data-duration="4.5" data-track-index="5">Only <span>3</span><br>ingredients</div>
```
```css
.headline{position:absolute;left:108px;top:300px;font:700 118px/1.02 var(--font-display);color:var(--text);text-shadow:0 6px 0 rgba(var(--bg-rgb),.6);opacity:0}.headline span{color:var(--accent)}
```
```js
tl.fromTo('#headline-1',{opacity:0,y:30},{opacity:1,y:0,duration:0.4,ease:'power3.out'},0.1);
tl.to('#headline-1',{opacity:0,y:-16,duration:0.2,ease:'power2.in'},4.3);
```

### Pill

```css
.pill{position:absolute;background:var(--accent);color:var(--on-accent);font:700 36px var(--font-text);padding:12px 26px;border-radius:40px;opacity:0}
.pill.ghost{background:transparent;color:var(--text);border:3px solid var(--text)}
```
Entry `fromTo {opacity:0,scale:.9,y:10} {opacity:1,scale:1,y:0,duration:.3,ease:'back.out(1.4)'}` only if the pill is the main element of the moment; otherwise, `power3.out` without bounce. Exit 180 ms `power2.in`.

### Punch-ins and emphasis zoom (with sound)

```js
tl.set('#cam',{scale:1.12},0.9);    // cut to close shot on a change of idea
tl.set('#cam',{scale:1.0},1.9);     // back to medium shot at the next change
tl.to('#cam',{scale:1.18,duration:0.12,ease:'power3.out'},2.6);   // emphasis
tl.to('#cam',{scale:1.0,duration:0.4,ease:'power3.inOut'},3.4);
```
```html
<audio id="s-cut-1" src="assets/sfx/cut.wav" data-start="0.9" data-duration="0.25" data-track-index="10" data-volume="0.7"></audio>
<audio id="sfx-1" src="assets/sfx/hit.wav" data-start="2.6" data-duration="0.4" data-track-index="10" data-volume="0.6"></audio>
```
Rule: every `set` or `to` on `#cam` has an `<audio>` at the same instant. The scales shown assume a 1296x2304 master; with a 1080x1920 original they stay at 1.15 or below. SFX share track 10 while they do not overlap; one that overlaps another goes on track 11.

Cut hits (the sound of a punch-in or of a cut between takes): the `id` starts with `s-cut-`, which is how `verify-sfx.py` knows to hold them to the stricter margin; every other effect has any other `id`. The attack falls on the frame of the cut (`data-start` = `cut` of `cut.json` minus 0.01 s). The tail is trimmed with a 30 ms fade so it ends right before `voice_start` of the new sentence; if the voice starts almost at the cut, only the hit remains (40 ms minimum). The fade goes in the file (`afade=t=out` with the length already trimmed in `assets/sfx/`). Then, with the composition finished:

```bash
uv run -q --python 3.11 --with numpy python <skill-dir>/scripts/verify-sfx.py social/<piece>/edit/project
```

It reads every `<audio>` of `index.html` except the voice and the music in `assets/music/`, and fails if an effect is less than 6 dB under the voice in a word it overlaps, or less than 10 dB for a cut hit, counting only the instants with real voice (Whisper's word times also cover the silence around each word). The voice is the master `cut.json` names: `clip.mp4` in `<video id="a-roll">`, or `voice.wav` in `<audio id="voice">`. It also fails if it finds no effect, no `cut.json`, no element carrying the voice, or an `<audio>` without its file or its timing; a visual video without voice has no word to mask and does not run it.

### Floating screenshot and window

```css
.win{position:absolute;left:100px;top:980px;width:880px;background:var(--code-bg,var(--ink));border:3px solid rgba(255,255,255,.14);border-radius:22px;box-shadow:0 30px 60px rgba(0,0,0,.35);overflow:hidden;opacity:0}
.bar{height:46px;background:var(--ink);display:flex;align-items:center;gap:10px;padding-left:20px}.bar i{width:16px;height:16px;border-radius:50%;background:var(--light);opacity:.5;display:block}
.code{padding:18px 26px;font:500 38px/1.5 var(--font-mono,monospace);color:var(--light)}.code div{white-space:pre}
.code .hl{background:rgba(var(--accent-rgb),.18);box-shadow:inset 8px 0 0 var(--accent);margin:0 -26px;padding:0 26px 0 18px}.code .faded{opacity:.45}
```
Entry `fromTo {opacity:0,y:30,scale:.96} {opacity:1,y:0,scale:1,duration:.4,ease:'power3.out'}` with whoosh; exit 200 ms. For a real screenshot, `<img>` inside `.win` without `.bar`, cropped to the relevant region and exported at 2x. The `.code` rules are for pieces that show code, a command or data in lines (one `<div>` per line, `.hl` on the line being discussed, `.faded` on the rest); they use the optional tokens `--code-bg` and `--font-mono`.

### Dynamic zoom into the screen

Wrap camera and window in `#scene` with `transform-origin` at the center of the window (x = left + width/2, y = top + height/2).

```js
var k = (1080 - 24) / 880;   // the window fills the width; never cuts text
tl.to('#scene',{scale:k,duration:0.7,ease:'power3.inOut'},1.2);      // whoosh at 1.15
// tick on the highlighted line: the accent at 18 % and 45 % (GSAP interpolates literal colors, so write the brand accent's RGB)
tl.fromTo('#hl',{backgroundColor:'rgba(194,59,90,0.18)'},{backgroundColor:'rgba(194,59,90,0.45)',duration:0.15,yoyo:true,repeat:1},1.95);
tl.to('#scene',{scale:1,duration:0.6,ease:'power3.inOut'},3.0);      // lower whoosh at 2.95
```

### Brand background behind the creator cut out

```bash
npx --yes hyperframes@0.8.229 remove-background clip.mp4 -o assets/cut.webm --quality best
```
About 22 s per 120 frames on CoreML; downloads a 168 MB model the first time. Run it on the master, so the cutout matches `clip.mp4` frame by frame. Output WebM VP9 with alpha.

```html
<div id="brand" class="clip" data-start="0" data-duration="45" data-track-index="0">
  <div id="texture" style="position:absolute;left:-200px;top:0;width:1480px;height:1920px;background:url(assets/textures/<texture>.png) center/cover;opacity:.5;filter:blur(3px)"></div>
  <img id="logobig" src="assets/logo.png" style="position:absolute;left:50%;top:46%;width:980px;transform:translate(-50%,-50%);opacity:.07">
</div>
<div id="cam"><video id="a-roll" class="clip" src="clip.mp4" playsinline data-start="0" data-duration="45" data-track-index="1" data-has-audio="true" data-volume="1"></video></div>
<video id="cutout" class="clip" src="assets/cut.webm" playsinline data-start="0" data-duration="45" data-track-index="2" data-has-audio="false" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover"></video>
```
```js
tl.fromTo('#texture',{x:-80},{x:0,duration:4,ease:'none'},0);        // slow drift
tl.to('#cam',{opacity:0,duration:0.4,ease:'power2.inOut'},0.8);      // the real background goes away, the cut-out creator remains
tl.to('#cam',{opacity:1,duration:0.4,ease:'power2.inOut'},3.4);      // the real background returns
```
The cutout always goes above the camera and in sync with it. To put context b-roll behind, replace `#brand` with the b-roll `<video>` on track 0. `#logobig` is optional: the brand's logo, large and at 7 % opacity, the only logo a video carries; leave it out if the brand has none or its guide keeps the logo out of video. `#texture` is the brand texture copied from `brand-guide/assets/textures/` (the soft blur hides the pixels of a small raster; a sharp vector texture goes without it); if the brand has no texture, leave `#texture` out and the dark background stays alone.

### Giant typography

```css
#dim{position:absolute;inset:0;background:rgba(var(--bg-rgb),.78);opacity:0}
#giant{position:absolute;left:0;right:0;top:560px;text-align:center;font:700 440px/1 var(--font-display);color:var(--accent);letter-spacing:-12px;opacity:0}
#giant2{position:absolute;left:0;right:0;top:1010px;text-align:center;font:700 120px/1 var(--font-display);color:var(--text);opacity:0}
```
```js
tl.to('#dim',{opacity:1,duration:0.3,ease:'power2.out'},1.0);
tl.fromTo('#giant',{opacity:0,scale:0.96},{opacity:1,scale:1,duration:0.4,ease:'power3.out'},1.0);   // low hit at 1.0
tl.fromTo('#giant2',{opacity:0,y:20},{opacity:1,y:0,duration:0.35,ease:'power3.out'},1.1);
tl.to(['#giant','#giant2'],{opacity:0,scale:1.02,duration:0.2,ease:'power2.in'},2.9);
tl.to('#dim',{opacity:0,duration:0.25,ease:'power2.in'},2.95);
```

### Parallax (continuous, no jump)

```css
#persp{position:absolute;inset:0;perspective:1800px}
#card{position:absolute;left:110px;top:1010px;width:860px;transform-style:preserve-3d;opacity:0}
#layerb{position:absolute;left:-40px;top:-60px;width:860px;height:560px;border-radius:26px;background:var(--ink);opacity:.9;transform:translateZ(-140px)}
```
```js
tl.set('#layerb',{x:-70},0); tl.set('#pill',{x:0},0);               // initial positions set at 0
tl.fromTo('#card',{opacity:0,y:40},{opacity:1,y:0,duration:0.5,ease:'power3.out'},0.4);
tl.fromTo('#card',{rotateY:-18,rotateX:7},{rotateY:-5,rotateX:3,duration:3.5,ease:'none'},0.4);  // a single linear drift
tl.to('#layerb',{x:-10,duration:3.5,ease:'none'},0.4); tl.to('#pill',{x:22,duration:3.5,ease:'none'},0.4);
```
The initial positions of the layers are set at second 0 and the drift is a single curve: setting them at the moment the drift starts makes the layers jump.

### Picture in picture

`#cam` reduced: `tl.set('#cam',{scale:0.32,x:-300,y:560,transformOrigin:'0% 100%'},t)` with `#cam video{border-radius:20px}` enabled by class, and the screen b-roll on track 3 full screen underneath. Return with a 400 ms `to`.

### Music bed

The music is built with ffmpeg into a single file, with its levels, joins and fades already applied, and enters the composition at a fixed volume: that way it is measured directly and does not depend on how the engine interprets automation.

1. Measure where the track ends musically: many have a fade to silence of several seconds at the end. If the video is longer than that part, the loop comes back from the start of a phrase after the intro, with a 0.5 s crossfade; the whole file is never repeated (it leaves a silent gap and the intro playing in the middle of the video).
2. Chain the sections and apply the levels by time (in seconds from when the music enters). In the command below, `<a>` is where the music starts in the track, `<e>` where it ends musically and `<l>` where the loop comes back; the example levels are 28 % until `<t1>`, 18 % until `<t2>` and 5 % under the voice from then on:

```bash
ffmpeg -ss <a> -to <e> -i track.mp3 -ss <l> -to <e> -i track.mp3 -ss <l> -to <e> -i track.mp3 -filter_complex \
 "[0:a][1:a]acrossfade=d=0.5[x1];[x1][2:a]acrossfade=d=0.5[x2];[x2]atrim=0:<length>,asetpts=PTS-STARTPTS,\
  volume='if(lt(t,<t1>),0.28,if(lt(t,<t2>),0.18,0.05))':eval=frame,aresample=48000[o]" -map "[o]" -ac 2 assets/music/bed.wav
```

3. Place it with `<audio id="music" src="assets/music/bed.wav" data-start="<entry>" data-duration="<length>" data-track-index="12" data-volume="1">`.
4. Check in the render that it plays throughout the video (lows against the clip without music, in `quality-control.md`) and that it sits about 20 dB below the voice.

`data-automation` works for simple ramps, with one condition: its times (`t`) are composition times, not from the start of the `<audio>`. Written as relative on a track that starts late, all the points fall in the past and the last value keeps playing.

### Speed and final encode

The whole composition is built at normal speed (the timings of `cut.json`, subtitles and sounds). Speed, loudness and the export preset are applied to the HyperFrames render in a single encode, so the recording is not encoded one more time, and the final time is the composition time divided by the speed:

```bash
<skill-dir>/scripts/final-encode.sh renders/final.mp4 ../../export/<slug>-<channel>.mp4 --speed 1.1   # pieces over the speed-up threshold
<skill-dir>/scripts/final-encode.sh renders/final.mp4 ../../export/<slug>-<channel>.mp4               # normal speed
<skill-dir>/scripts/check-render.sh ../../export/<slug>-<channel>.mp4
```

`final-encode.sh` measures the loudness of the audio already at its final speed, normalizes it in a second pass to -14 LUFS with a true peak target of -1.5 dBTP, encodes with the export preset of `quality-control.md` and ends by measuring the file with `loudness.sh`; it exits with 1 if the result is out of range. The target is -1.5 and not the -1 dBTP limit because AAC raises the peaks a little after normalizing. `atempo` changes the speed without changing the pitch of the voice. A video at or under the speed-up threshold (default 30 s, see "Speed" in `SKILL.md`) is not sped up, and neither is a visual video without voice, which is built at its final pace. The review render goes through the same script, so what the user reviews has the final speed and level.

### Design variants to decide

When a detail has to be chosen (the style of an edge, a background, the position of a subtitle, an effect), show two or three real variants instead of describing them. All on the same frame and without touching the approved project:

1. Save a copy of `index.html` outside the project (in the session's scratch folder) and note the frame time.
2. For each variant, write only the change into `index.html` (a CSS rule or a new layer inserted in its place), take `snapshot --at <t>` and copy the frame to `edit/tests/<topic>/<variant>.png`.
3. Restore the copy and check with `diff` that `index.html` is identical.
4. Review each variant at full size and crop the area that changes (for example, the edge and the head) for the close-up. Fix whatever fails in all of them before showing (an edge highlight crossing the forehead, a covered text).
5. Compose a single image with each full variant and its close-up below, with a label (letter and name), open it for the user, explain in one line what each one does, recommend one and ask with the structured question tool.
6. Write the chosen variant into `index.html`. If it sets a criterion for future pieces, propose to the user that it be added to the brand guide.

To explain a rule with an example (why an edge goes in one place and not another), do the same: the same frame with each option side by side and a "right" and "wrong" label or one per height.

## 5. Review and render

```bash
npx --yes hyperframes@0.8.229 check                      # lint, layout, motion, contrast
npx --yes hyperframes@0.8.229 snapshot --at 0.5,6,18,44 --no-end -o ../tests/<folder>   # exact frames and contact sheet
npx --yes hyperframes@0.8.229 render --quiet --fps 30 -q looks --output renders/review.mp4     # review
npx --yes hyperframes@0.8.229 render --quiet --fps 30 -q delivery --output renders/final.mp4   # final
<skill-dir>/scripts/review-frames.sh renders/final.mp4 ../tests/<folder> 0.5 3 8 15 25 40      # full-size frames and a sheet, to review like a designer
<skill-dir>/scripts/check-render.sh renders/final.mp4                                          # white strip, every frame
```

The deliverable is written from the render with `final-encode.sh` ("Speed and final encode").

Known render problems (macOS, Apple Silicon):

- Huge images (several thousand pixels per side, for example a full-resolution logo used large and faint behind the brand background) sometimes are not painted in the render and leave a stretched vertical white strip in their column; `snapshot` does not show it. Always use a copy reduced to about 3 times its on-screen size inside a container with fixed width and height, render with `--workers 1` and run `<skill-dir>/scripts/check-render.sh` on the render: it looks for the strip in every column of every frame and prints the time and x of each hit, to be looked at (a plain light vertical bar that belongs to the design reads the same).
- Every video that enters the composition (cut recording and b-roll) is encoded with dense keyframes (`-g 15`); the compiler warns about "sparse keyframes" when not, and that causes jumps and freezes.
- When trimming a section of an already edited recap, leave a margin of a couple of frames before the recap's next cut: the last frame may belong to the next shot.

Composition traps:

- What is placed as a sub-composition (`data-composition-src`) is painted above the elements of the root composition, even if they have a higher `z-index`. To make something from a sub-composition pass behind a text in the root (objects falling next to the hook headline), mask the host with a gradient (`mask-image: linear-gradient(...)`) that makes it appear below the text; do not rely on `z-index`.
- Sub-compositions inherit the global styles of `index.html` (for example `* { box-sizing: border-box }`): a card with padding ends up narrower than when it was built on its own. Review every element inside the final composition, never alone.
- A graphic's texts use the brand fonts loaded by `assets/fonts/fonts.css`. A system font (`-apple-system`, SF Pro) does not exist in the render engine: it is replaced by a wider one and the text overflows its box.
- A graphic placed with `scale()` shrinks its text: the size that counts is the on-screen one (36 px minimum after scaling).
- A subtitle never starts before its take: Whisper often places the first word before the cut. While a key phrase covers a line, that whole line goes without subtitle, so no loose word is left.

GSAP traps in HyperFrames:

- A clip's `data-duration` covers its exit animation; otherwise the exit is cut and the element disappears abruptly.
- A `fromTo` that starts late on an element that already has another tween carries `immediateRender: false`, so it does not overwrite the previous state.
- Shakes with absolute values that return to 0 (`x` from 0 to 8, -6, 3 and 0), never relative ones like `'+=8'`: a relative value accumulates when the render jumps along the timeline.
- Counters with `font-variant-numeric: tabular-nums` and `white-space: nowrap`.
- A full-screen overlay that starts visible triggers a lint error: its initial state goes inside the `fromTo`, not in the CSS.
- Positions are computed once when the composition loads, never with `getBoundingClientRect()` during a tween.

Known non-blocking `check` warnings: `studio_missing_editable_id` (give everything an `id`) and `duplicate_audio_track` when two SFX share a track and overlap (move one to track 11).
