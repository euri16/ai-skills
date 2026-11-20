# Sound brief, verification and loop points

## Brief template

Write the brief in the user's language, or the one the workspace instructions set; the template below shows the structure.

```markdown
## Sound brief: <piece>

Format: <educational | demo | opinion | progress log | sketch | another format of the workspace> · Duration: <N> s · Tone: <one line>

### Effects

| Time | Movement | Type (catalog) | Character | Level under the voice | Candidate | Source and license |
|---|---|---|---|---|---|---|
| 0.9 | cut to close-up | dry cut hit | 200 ms, low, no tail | 8 dB | sfx/hits-and-impacts/<file> | pool (Freesound CC0, id ...) |
| 2.6 | emphasis zoom on "five hundred" | emphasis hit | 400 ms, with body | 6 dB | sfx/hits-and-impacts/<file> | pool |
| 12.0 | the screenshot comes in | entrance whoosh | 400 ms | 8 dB | sfx/whoosh-and-transitions/<file> | pool |

### Music

- Has music? <yes | no> · Reason: <...>
- Mood: <bright neutral | restrained with pulse | optimistic | comic suspense | another>
- Energy: <low | medium | high> · BPM: <range> · Instrumentation: <...> · No lyrics
- Duration needed: <N> s · Change points: <t1 lifts, t2 cuts dry>
- Candidates: <file, source, license, attribution>

### Pending
- <manual downloads the user has to do, sounds no source had>
```

## How to describe music to search for it or generate it

- Mood in two words and a functional reference ("explanation background, not the lead"), not an artist.
- BPM by format (table in `sound-catalog.md`); for generation, ask for a specific value.
- Instrumentation by exclusion: "no heavy drums, no vocals, no brass".
- Structure: a short intro that lets the voice come in within 1 s, a stable body, a lift point if there is a turn, and an ending that allows a dry cut or a 400 ms fade.
- Duration: the video's plus 2 s of margin.

## Verification with ffmpeg

`scripts/audio-check.sh <file> [...]` prints duration, sample peak, mean level, leading and trailing silence, whether the file is broken, and whether the levels of the first and the last 0.1 s are close enough to join in a loop (in very short SFX integrated loudness is not measurable, so sample peak and mean level are used). Rejection criteria: broken file or smaller than 2 KB, sample peak above -1 dBFS after preparation, leading silence longer than 150 ms in an SFX, a tail that extends beyond the movement it accompanies, music with lyrics.

Typical preparation:

```bash
# SFX: trim leading and trailing silence and normalize the sample peak to -3 dBFS (prepare-sfx.sh measures the peak with volumedetect; alimiter does not work because it renormalizes the level by default)
scripts/prepare-sfx.sh in.mp3 out.wav
# Music: starting level -34 LUFS (20 dB under a voice at -14) for the mix in HyperFrames
ffmpeg -y -i in.mp3 -af "loudnorm=I=-34:TP=-6:LRA=11" -ar 48000 -b:a 256k out.mp3
# Multi-hit sound: the instant of each hit, written to out.hits.json
scripts/hit-times.sh out.wav
```

## Loop points

The agent cannot hear where a phrase starts, so the loop is planned with levels and confirmed by the user's ear. Print the track's level second by second:

```bash
ffmpeg -hide_banner -nostats -i track.mp3 -af "aresample=48000,asetnsamples=n=48000,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-" -f null - 2>/dev/null \
  | awk -F'[:=]' '/pts_time/{t=$NF} /RMS_level/{printf "%5.0f s  %s dB\n", t, $NF}'
```

- **End of the musical part:** the last second before the level starts falling toward silence. Many tracks end with a fade of several seconds; the loop leaves before it.
- **Return point:** the first second after the intro at which the level reaches the level of the body. For a finer value, run the command again on that stretch with `asetnsamples=n=4800` (tenths of a second).

Those two times go into the "Music bed" recipe of `edit-short-video/references/hyperframes-recipes.md`, which chains the stretches with a 0.5 s crossfade. Put the built bed among the music candidates so the user hears the join on the choice page; if it sounds cut, move the return point and build it again.

For a loop file that repeats without a click (an ambience or a short pattern, not a track with phrases), crossfade the end into the start: the result is shorter by the length of the crossfade, starts where the crossfade ends and finishes where it begins.

```bash
D=1   # crossfade length in seconds
ffmpeg -y -i in.wav -filter_complex "[0]asplit[a][b];[a]atrim=start=$D,asetpts=PTS-STARTPTS[body];[b]atrim=end=$D,asetpts=PTS-STARTPTS[head];[body][head]acrossfade=d=$D:c1=tri:c2=tri" loop.wav
```
