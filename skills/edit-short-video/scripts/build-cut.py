#!/usr/bin/env python3
"""Materialize the cut master of a piece: clip.mp4 with the chosen material joined in order, and cut.json.

Usage:
  python3 build-cut.py master <piece> --vf FILTER [--out DIR] [--takes-dir DIR] [--analysis-dir DIR]
  python3 build-cut.py single <piece> <cuts.json> --vf FILTER --words WORDS_JSON [--out DIR]
  python3 build-cut.py single <piece> <cuts.json> --voice-only --words WORDS_JSON [--out DIR]
  python3 build-cut.py video <cut.json> <out_dir> --vf FILTER [--clips 05,06]

--vf is the framing filter that leaves the image at the master size: the canvas (1080x1920) times the largest scale the
composition applies to the camera, taken from the original and never above it. For example "scale=1296:2304:flags=lanczos"
for punch-ins up to 120 % from a 4K original, or "scale=1080:1920:flags=lanczos" for a 1080x1920 original; a crop goes
before the scale ("crop=w:h:x:y,scale=...").

master (recording by sentences) reads <piece>/edit/takes/sentences.json (each row with "chosen", its "cuts" and, if
analyze-video's cuts.py wrote it, its "voice") and <piece>/edit/analysis/takes.json (every attempt of every clip, with its
words), cuts each chosen take from the original in source/recording/ and writes <out>/clip.mp4 and <out>/cut.json
(default out: edit/project). Optional fields of a row: "pause" (seconds of silence the script asks for after the
sentence) and "vf" (a framing for that row instead of --vf).

single (one continuous take) reads a cut list and the take's words.json (per-word times from analyze-video) and writes
the same clip.mp4 and cut.json. cuts.json, with times in seconds of the original:
  {"file": "<name in source/recording/>",
   "segments": [{"start": 0.42, "end": 3.10, "sentence": "..."}, {"start": 3.62, "end": 7.90, "sentence": "..."}]}
Optional fields of a segment: "part", "vf" and "voice" ([start, end] of the voice, for a segment without words).

single --voice-only (the voice-over of a visual video, which has no camera take) reads the same cut list and words.json,
uses only the audio of the recording (an audio file, or a video whose image is ignored) and writes voice.wav instead of
clip.mp4, with the same cut.json. It takes no --vf, and "vf" in a segment is an error.

video rebuilds, video only, the segments listed in cut.json with another framing (the split view sections, the intro),
each with exactly the frames of the master, so they match it frame by frame. One file per segment: <out_dir>/seg-<clip>.mp4.

Rules (edit-short-video/references/hyperframes-recipes.md, "Cut master"):
- Between sentences, only the gap each exact cut leaves. No added gap and never a frozen frame.
- A pause asked for by the script runs on the same take after its out point, only while the creator stays still and looking
  at the camera (the "still_pause" that cuts.py measured for that take) and never reaching the next attempt of the same
  clip (start of that attempt minus 0.05 s). If that leaves less than 80 % of the pause, there is no pause: the take ends
  at its out point and the script says so. Never frames from another take.
- Durations are whole frames, computed from the cut, never measured on an encoded file.
- The audio of each segment fades in over 8 ms and out over 12 ms: no click at the joins.
- Every frame comes from the video itself; nothing goes through PNG or JPG.

cut.json, times in seconds of the master (30 fps):
  master: the file the times refer to, "clip.mp4" or "voice.wav".
  segments[]: clip, part, sentence, file, take, cut (instant of the image change), start and end (the cut of the take;
  end is what counts for subtitles and sounds), voice_start, voice_end, pause (silence after end, until the next cut),
  source {file, from, frames} and words [{w, t0, t1}].
"""
import argparse, json, math, os, subprocess, sys

FPS, SR = 30, 48000
MARGIN = 0.05                       # s kept away from another attempt of the same clip
FADE_IN, FADE_OUT = 0.008, 0.012    # s of audio fade on each segment
ENC = ["-c:v", "libx264", "-crf", "10", "-g", "15", "-pix_fmt", "yuv420p",
       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]


def fail(msg):
    sys.exit(f"build-cut: {msg}")


def run(cmd):
    subprocess.run(cmd, check=True)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


def frame_count(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets",
                          "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout
    return int(out.strip().split(",")[0])


def sample_count(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=duration_ts",
                          "-of", "csv=p=0", path], capture_output=True, text=True, check=True).stdout
    return int(out.strip().split(",")[0])


def cut_segment(src, start, frames, vf, out, audio=True):
    """`frames` frames of src from second `start`, framed with vf; PCM audio with its fades. Reused if nothing changed.
    With vf None the segment is audio only (a WAV of exactly `frames` frames of sound)."""
    key = json.dumps([src, round(start, 4), frames, vf, audio, FADE_IN, FADE_OUT])
    stamp = out + ".key"
    if os.path.exists(out) and os.path.exists(stamp) and open(stamp).read() == key:
        return
    dur = frames / FPS
    v = f"[0:v]{vf},fps={FPS},trim=end_frame={frames},setpts=PTS-STARTPTS[v]"
    a = (f"[0:a]aresample={SR},apad,atrim=0:{dur:.6f},asetpts=PTS-STARTPTS,"
         f"afade=t=in:d={FADE_IN},afade=t=out:st={dur - FADE_OUT:.6f}:d={FADE_OUT}[a]")
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.4f}", "-t", f"{dur + 0.2:.4f}", "-i", src]
    if vf is None:
        if duration(src) < start + dur - 1 / FPS:
            fail(f"{os.path.basename(src)} ends before {start + dur:.2f} s: the cut list asks for sound that does not exist")
        want = round(dur * SR)
        # samples are renumbered from 0 and counted, so a decoder that starts a few milliseconds in cannot shorten the segment
        voice = (f"[0:a]aresample={SR},asetpts=N/{SR}/TB,apad,atrim=end_sample={want},"
                 f"afade=t=in:d={FADE_IN},afade=t=out:st={dur - FADE_OUT:.6f}:d={FADE_OUT}[a]")
        run(cmd + ["-filter_complex", voice, "-map", "[a]", "-vn", "-c:a", "pcm_s16le", "-ac", "2", out])
        got = sample_count(out)
        if got != want:
            fail(f"{os.path.basename(out)} came out with {got} samples instead of {want}")
        open(stamp, "w").write(key)
        return
    if audio:
        cmd += ["-filter_complex", f"{v};{a}", "-map", "[v]", "-map", "[a]"] + ENC + ["-c:a", "pcm_s16le", "-ac", "2", out]
    else:
        cmd += ["-filter_complex", v, "-map", "[v]", "-an"] + ENC + [out]
    run(cmd)
    got = frame_count(out)
    if got != frames:
        fail(f"{os.path.basename(out)} came out with {got} frames instead of {frames} (does the original end earlier?)")
    open(stamp, "w").write(key)


def load(path, what):
    if not os.path.exists(path):
        fail(f"{what} not found: {path}")
    return json.load(open(path))


def voice_of(given, words, cut_in, cut_out, name):
    """[start, end] of the voice of a segment, in seconds of the original."""
    if given:
        return given
    if not words:
        fail(f"{name} has no words between {cut_in:.2f} and {cut_out:.2f} s of its take and no \"voice\": "
             "check the cut, or give the voice range")
    return [words[0]["start"], words[-1]["end"]]


def plan_master(args):
    """One plan entry per row of sentences.json, in whole frames: n (the cut of the take), post (pause on this same take)."""
    piece = os.path.abspath(args.piece)
    takes_dir = args.takes_dir or os.path.join(piece, "edit/takes")
    analysis_dir = args.analysis_dir or os.path.join(piece, "edit/analysis")
    rec_dir = os.path.join(piece, "source/recording")
    rows = load(os.path.join(takes_dir, "sentences.json"), "sentences.json")
    attempts = load(os.path.join(analysis_dir, "takes.json"), "takes.json")
    by_take = {(x["file"], x["take"]): x for x in attempts}
    clip_durations = {}

    def free_after(clip_file, t):
        """Real time after t before the next attempt of the same clip (or the end of the clip)."""
        nxt = [x["start"] for x in attempts if x["file"] == clip_file and x["start"] > t]
        if nxt:
            return min(nxt) - MARGIN - t
        clip_durations.setdefault(clip_file, duration(os.path.join(rec_dir, clip_file)))
        return clip_durations[clip_file] - 0.1 - t

    plan = []
    for row in rows:
        label = row.get("chosen") or fail(f"sentence {row['clip']} has no chosen take")
        if label not in row.get("cuts", {}):
            fail(f"sentence {row['clip']} has no cut for its chosen take ({label}): run cuts.py")
        cut_in, cut_out = row["cuts"][label]
        n = round((cut_out - cut_in) * FPS)
        if n <= 0:
            fail(f"sentence {row['clip']}: the cut of {label} is empty ({cut_in} to {cut_out})")
        pause = round(row.get("pause", 0) * FPS)
        post = 0
        if pause:
            still = row.get("final", {}).get(label, {}).get("still_pause")
            if still is None:
                fail(f"sentence {row['clip']} asks for a pause and its take has no measured stillness: run cuts.py")
            free = free_after(row["file"], cut_in + n / FPS)
            post = max(0, math.floor(min(row["pause"], still, free) * FPS + 1e-6))
            if post < 0.8 * pause:
                print(f"warning: sentence {row['clip']} asks for a {row['pause']:.2f} s pause and {label} only stays still "
                      f"{min(still, free):.2f} s: no pause, the take is cut when the voice ends", file=sys.stderr)
                post = 0
        cut_end = cut_in + n / FPS
        take_ids = [int(k) for k in label.split()[1].split("+")]
        for k in take_ids:
            if (row["file"], k) not in by_take:
                fail(f"sentence {row['clip']}: take {k} of {row['file']} is not in takes.json")
        words = [w for k in take_ids for w in by_take[(row["file"], k)]["words"] if w["start"] < cut_end and w["end"] > cut_in]
        plan.append({"clip": row["clip"], "part": row.get("part"), "sentence": row.get("sentence"), "file": row["file"],
                     "label": label, "cut_in": cut_in, "n": n, "post": post, "vf": row.get("vf", args.vf), "words": words,
                     "voice": voice_of(row.get("voice", {}).get(label), words, cut_in, cut_end, f"sentence {row['clip']}")})
    return piece, plan


def plan_single(args):
    """One plan entry per segment of the cut list of a continuous take."""
    piece = os.path.abspath(args.piece)
    spec = load(args.cuts_json, "cut list")
    all_words = load(args.words, "words.json")
    if not spec.get("segments"):
        fail("the cut list has no segments")
    plan, last_end = [], None
    for k, seg in enumerate(spec["segments"], 1):
        cut_in, cut_out = float(seg["start"]), float(seg["end"])
        n = round((cut_out - cut_in) * FPS)
        if n <= 0:
            fail(f"segment {k}: empty range ({cut_in} to {cut_out})")
        if last_end is not None and cut_in < last_end:
            fail(f"segment {k} starts at {cut_in} s, before the end of the previous one ({last_end} s)")
        last_end = cut_out
        if args.voice_only and "vf" in seg:
            fail(f"segment {k} has a \"vf\" and --voice-only writes no image")
        cut_end = cut_in + n / FPS
        words = [w for w in all_words if w["start"] < cut_end and w["end"] > cut_in]
        plan.append({"clip": f"{k:02d}", "part": seg.get("part"), "sentence": seg.get("sentence"), "file": spec["file"],
                     "label": "single", "cut_in": cut_in, "n": n, "post": 0,
                     "vf": None if args.voice_only else seg.get("vf", args.vf), "words": words,
                     "voice": voice_of(seg.get("voice"), words, cut_in, cut_end, f"segment {k}")})
    return piece, plan


def build(args, piece, plan):
    out_dir = os.path.abspath(args.out or os.path.join(piece, "edit/project"))
    rec_dir = os.path.join(piece, "source/recording")
    for p in plan:
        if not os.path.exists(os.path.join(rec_dir, p["file"])):
            fail(f"original not found: {os.path.join(rec_dir, p['file'])}")
    seg_dir = os.path.join(out_dir, "assets/segments")
    os.makedirs(seg_dir, exist_ok=True)
    voice_only = getattr(args, "voice_only", False)
    ext = "wav" if voice_only else "mkv"
    segments, frame = [], 0                             # frame: master frame where the segment starts
    for p in plan:
        cut_in, n, voice = p["cut_in"], p["n"], p["voice"]
        total = n + p["post"]
        src = os.path.join(rec_dir, p["file"])
        cut_segment(src, cut_in, total, p["vf"], os.path.join(seg_dir, f"seg-{p['clip']}.{ext}"))
        start = frame / FPS
        segments.append({
            "clip": p["clip"], "part": p["part"], "sentence": p["sentence"], "file": p["file"], "take": p["label"],
            "cut": round(start, 4), "start": round(start, 4), "end": round(start + n / FPS, 4),
            "voice_start": round(start + voice[0] - cut_in, 4), "voice_end": round(start + voice[1] - cut_in, 4),
            "pause": 0.0,
            "source": {"file": os.path.relpath(src, out_dir), "from": round(cut_in, 4), "frames": total},
            "words": [{"w": w["word"], "t0": round(start + w["start"] - cut_in, 4), "t1": round(start + w["end"] - cut_in, 4)}
                      for w in p["words"]],
        })
        frame += total
    for s, nxt in zip(segments, segments[1:] + [None]):
        s["pause"] = round((nxt["start"] if nxt else frame / FPS) - s["end"], 4)

    name = "voice.wav" if voice_only else "clip.mp4"
    master = os.path.join(out_dir, name)
    if voice_only:
        # Audio only: each WAV segment already has its exact samples, so they are joined as they are
        inputs, graph = [], ""
        for k, s in enumerate(segments):
            inputs += ["-i", os.path.join(seg_dir, f"seg-{s['clip']}.wav")]
            graph += f"[{k}:a]"
        graph += f"concat=n={len(segments)}:v=0:a=1[a]"
        run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", graph, "-map", "[a]",
                                                        "-c:a", "pcm_s16le", "-ar", str(SR), "-ac", "2", master])
        got, want = sample_count(master), round(frame / FPS * SR)
        if got != want:
            fail(f"voice.wav has {got} samples and the cut adds up to {want}")
        write_cut(out_dir, name, frame, segments)
        return
    # Join with the concat filter: each segment enters with its exact frames and its audio cut to the same duration
    inputs, graph = [], ""
    for k, s in enumerate(segments):
        total = s["source"]["frames"]
        inputs += ["-i", os.path.join(seg_dir, f"seg-{s['clip']}.mkv")]
        graph += (f"[{k}:v]setpts=PTS-STARTPTS,trim=end_frame={total},setpts=N/{FPS}/TB[v{k}];"
                  f"[{k}:a]asetpts=PTS-STARTPTS,apad,atrim=0:{total / FPS:.6f}[a{k}];")
    graph += "".join(f"[v{k}][a{k}]" for k in range(len(segments))) + f"concat=n={len(segments)}:v=1:a=1[v][a]"
    run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", graph, "-map", "[v]", "-map", "[a]"] + ENC +
        ["-c:a", "aac", "-b:a", "192k", "-ar", str(SR), master])
    got = frame_count(master)
    if got != frame:
        fail(f"clip.mp4 has {got} frames and the cut adds up to {frame}")
    write_cut(out_dir, name, frame, segments)


def write_cut(out_dir, name, frame, segments):
    json.dump({"master": name, "fps": FPS, "frames": frame, "duration": round(frame / FPS, 4), "segments": segments},
              open(os.path.join(out_dir, "cut.json"), "w"), ensure_ascii=False, indent=1)
    pauses = [s for s in segments if s["pause"] > 0.3]
    print(f"{name} {frame / FPS:.2f} s, {frame} frames, {len(segments)} segments"
          + (", pauses: " + ", ".join(f"{s['clip']} {s['pause']:.2f} s" for s in pauses) if pauses else ""))


def rebuild_video(args):
    cut = json.load(open(args.cut_json))
    if cut.get("master") == "voice.wav":
        fail("this cut.json belongs to a voice-over (voice.wav): it has no image to rebuild")
    base = os.path.dirname(os.path.abspath(args.cut_json))
    only = set(args.clips.split(",")) if args.clips else None
    os.makedirs(args.out_dir, exist_ok=True)
    for s in cut["segments"]:
        if only and s["clip"] not in only:
            continue
        src = s["source"]
        cut_segment(os.path.join(base, src["file"]), src["from"], src["frames"], args.vf,
                    os.path.join(args.out_dir, f"seg-{s['clip']}.mp4"), audio=False)
        print(f"seg-{s['clip']}.mp4 {src['frames']} frames, from {s['cut']:.3f} s of the master")


parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
sub = parser.add_subparsers(dest="mode", required=True)
p_master = sub.add_parser("master")
p_master.add_argument("piece")
p_master.add_argument("--vf", required=True)
p_master.add_argument("--out")
p_master.add_argument("--takes-dir")
p_master.add_argument("--analysis-dir")
p_single = sub.add_parser("single")
p_single.add_argument("piece")
p_single.add_argument("cuts_json")
p_single.add_argument("--vf")
p_single.add_argument("--voice-only", action="store_true")
p_single.add_argument("--words", required=True)
p_single.add_argument("--out")
p_video = sub.add_parser("video")
p_video.add_argument("cut_json")
p_video.add_argument("out_dir")
p_video.add_argument("--vf", required=True)
p_video.add_argument("--clips")
args = parser.parse_args()
if args.mode == "master":
    build(args, *plan_master(args))
elif args.mode == "single":
    if bool(args.vf) == args.voice_only:
        parser.error("single needs exactly one of --vf FILTER (camera take) or --voice-only (voice-over)")
    build(args, *plan_single(args))
else:
    rebuild_video(args)
