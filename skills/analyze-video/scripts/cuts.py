#!/usr/bin/env python3
"""Exact in and out cut of each candidate take, so the face is not seen changing.

Usage: uv run -q --python 3.11 --with numpy --with "opencv-python-headless<5" --with silero-vad --with onnxruntime python cuts.py <recording_dir> <takes_dir> [x0,y0,x1,y1]
Reads <takes_dir>/sentences.json and ../analysis/takes.json. Writes in each row "cuts": {"Take N": [in, out]}
and "voice": {"Take N": [start, end]} (the measured voice edges), in seconds of the original clip, and "face": [x0, y0, x1, y1]
(the face area used, in fractions of the frame). choose-takes.py cuts the proxies with those times, check-cuts.py crops its
sheets to that face and edit-short-video/scripts/build-cut.py assembles the master with the cuts.
The face is detected automatically in each clip (OpenCV, from the eyebrows to the chin), in a vertical, horizontal or square
frame; the optional last argument fixes it in fractions of the frame if detection fails.

How it decides:
- The voice is measured with energy in 10 ms windows (more precise than Whisper's word times), and Silero VAD
  decides which sound stretches are speech: a breath or a mouth click before speaking does not move the in point earlier.
  Anchored to the first and the last word: whatever sounds afterwards (a laugh, a comment) does not come in (see vad.py).
- The face is measured frame by frame: mean difference between frames inside the face area.
  A peak above 1.3 times the typical movement while speaking is a face change
  (opening the mouth before speaking, raising the eyebrows, relaxing the expression, looking away).
- Cuts are tight: no air beyond what the breath between sentences needs.
- In point: between 0.05 and 0.02 s before the voice, after the last face change in that stretch.
- The end of the voice is its audible end: the last syllable whole, including a final "s", whose soft hiss the energy
  threshold misses (see gaze.py).
- Out point: 0.04 s after the audible end (0.02 s if the sentence's "intonation" is "open" and it continues in the next one). Any
  expression once the sentence is over is not shown: a face change, the mouth leaving the shape of the last syllable
  (closing, pressing, smiling), the eyes moving or the body leaning, searched up to 0.25 s after the voice (0.12 s if
  "open") (gaze.py: eye and mouth bands stabilized on the face, whole frame). The cut goes before the first one, even if that trims the tail of
  the final consonant; the floor is the end of the voice plus one frame. If the eyes move before the last syllable ends,
  the word stays whole and the take is marked: it loses against a similar take that keeps its eyes still. The air of one
  take's out point plus the next take's in point is the whole breath between sentences: the edit adds no gap.
- A row with "hold": s holds the shot s seconds after the voice in all its takes, for a reaction the script
  asks for (a face of amazement after the hook): that reaction is content and is not cut like a face change.
- A row with "pause": s is a silence the script asks for (after a punchline, before the payoff), which the edit makes by
  letting the take run past its out point (edit-short-video/scripts/build-cut.py). Here it is measured how long each take
  stays still and looking at the camera after its out point ("final": {"Take N": {"still_pause": s}}), up to the first
  jump of the frame or the eyes. A take that holds at least 80 % of the pause has it; the others have no pause. If the
  favorite does not hold it and another take with the same text does, that one becomes the favorite; if none does, the row
  gets a "warning".
- Among takes whose voice score is close to the favorite's ("score" within 0.5, from score-takes.py), one that keeps its
  eyes still at the end beats one that moves them ("eyes_move_before_end"). The favorite only changes by these two
  reasons, and "reason" says which one. "reason" and "warning" are text for the user: their phrases are the
  "label-reason-..." and "label-warning-..." tags of ../assets/choose-takes.html (labels.py).
- A row with "manual_out": {"Take N": s} sets that out point by hand (for example, to hold the shot on a visual
  punchline while the face stays still); it is kept when recomputing.
- A row with "end_gesture": true ends with a closing gesture the brand guide defines, if any. The gesture is content, so
  the changes after the voice are not cut out. Its out point is where the image detail collapses after the voice: the
  frame with the least detail in the 0.4 s after the detail first falls under a quarter of its level while speaking,
  plus three frames. If the detail never collapses, the script says so: set the out point with "manual_out". Rows without
  it end like any sentence.
"""
import json, os, subprocess, sys
if len(sys.argv) < 3: sys.exit(__doc__)
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vad import voice_edges
from gaze import Gaze, audible_end, frame_size, _fps
from labels import label, take_name
rec, tdir = sys.argv[1:3]
SHORT = 108                                      # short side of the frames where movement is measured, px
import cv2
FIXED_ZONE = tuple(map(float, sys.argv[3].split(","))) if len(sys.argv) > 3 else None
CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")   # OpenCV 4; version 5 does not ship it

def face_zone(f, t):
    """Face box (fractions of the frame) at frame t, with margin for eyebrows and chin."""
    if FIXED_ZONE: return FIXED_ZONE
    X, Y = frame_size(f, SHORT * 4)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", f, "-frames:v", "1", "-vf", f"scale={X}:{Y},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    img = np.frombuffer(raw, np.uint8).reshape(Y, X)
    faces = CASCADE.detectMultiScale(img, 1.1, 5, minSize=(SHORT // 2, SHORT // 2))
    if not len(faces):
        print(f"  {os.path.basename(f)}: no face detected, using the center of the frame; pass x0,y0,x1,y1 if the face is elsewhere", flush=True)
        return (0.3, 0.2, 0.7, 0.55)
    x, y, w, h = max(faces, key=lambda c: c[2] * c[3])
    return (max(0, (x - 0.1 * w) / X), max(0, (y - 0.05 * h) / Y), min(1, (x + 1.1 * w) / X), min(1, (y + 1.15 * h) / Y))
sj = os.path.join(tdir, "sentences.json")
sentences = json.load(open(sj))
T = {(x["file"], x["take"]): x for x in json.load(open(os.path.join(tdir, "../analysis/takes.json")))}
BEFORE = (0.05, 0.02)                            # margin before the voice (maximum, minimum), s
AFTER = {"closed": (0.04, 0.25), "open": (0.02, 0.12)}   # after the audible end: (air of the cut, window where a change is searched)

def voice(f, a, b, w0, w1, w0e):
    """Start and end of the voice near Whisper's first (w0) and last (w1) word."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", f, "-vn", "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return voice_edges(np.frombuffer(raw, np.int16).astype(np.float32) / 32768, a, w0, w1, w0e)

def movement(f, a, b, zone):
    """Face movement and frame detail at the clip's own frame rate (resampling repeats frames, which measure zero)."""
    x0, y0, x1, y1 = zone
    W, H = frame_size(f, SHORT)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", f, "-an",
                          "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    v = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(float)
    face = v[:, int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)]
    m = np.r_[0, np.abs(np.diff(face, axis=0)).mean(axis=(1, 2))]
    detail = np.abs(np.diff(v, axis=2)).mean(axis=(1, 2))         # frame edges: the end gesture is found where they collapse
    return a + np.arange(len(m)) / _fps(f), m, detail

def choose_favorite(row):
    """Adjusts the favorite with what only the image tells: a pause held still and eyes still at the end."""
    fav = row.get("favorite")
    row.pop("warning", None)
    if row.get("favorite_locked") or fav not in row["final"]: return
    met, ends = row.get("metrics", {}), row["final"]
    pts = lambda k: met.get(k, {}).get("score", -99)
    text = lambda k: met.get(k, {}).get("text", 1)
    cand = [k for k in ends if text(k) >= min(0.97, text(fav))]
    warnings, reason = [], None
    pause = row.get("pause")
    if pause:
        held = [k for k in cand if ends[k].get("still_pause", 0) >= 0.8 * pause]
        if not held: warnings.append(label("warning-no-pause"))
        else:
            cand = held
            if fav not in held: fav, reason = max(held, key=pts), label("reason-holds-pause")
    if ends[fav]["eyes_move_before_end"]:
        still = [k for k in cand if not ends[k]["eyes_move_before_end"] and pts(k) >= pts(fav) - 0.5]
        if still: fav, reason = max(still, key=pts), label("reason-still-eyes")
        elif all(ends[k]["eyes_move_before_end"] for k in cand):
            warnings.append(label("warning-eyes-all"))
        else: warnings.append(label("warning-eyes-favorite", take=take_name(fav)))
    if reason and fav != row["favorite"]:
        row["reason"] = label("reason-by-voice", reason=reason, take=take_name(row["favorite"]))
        row["favorite"] = fav
    if warnings: row["warning"] = "; ".join(warnings)


zones = {}
for row in sentences:
    cuts, edges, final = {}, {}, {}
    for tk in row["takes"]:
        ks = tk if isinstance(tk, list) else [tk]
        lab = "Take " + "+".join(map(str, ks))
        f = os.path.join(rec, row["file"])
        a, b = T[(row["file"], ks[0])]["start"], T[(row["file"], ks[-1])]["end"]
        words = [p for k in ks for p in T[(row["file"], k)]["words"]]
        v_start, v_end = voice(f, max(0, a - 0.3), b + 0.3, words[0]["start"], words[-1]["end"], words[0]["end"])
        if row["file"] not in zones: zones[row["file"]] = face_zone(f, (v_start + v_end) / 2)
        zone = zones[row["file"]]
        extra = 1.5 if row.get("end_gesture") else 0.8
        t, m, detail = movement(f, max(0, v_start - 0.8), v_end + extra, zone)
        frame = 1 / _fps(f)
        audible = audible_end(f, v_end)
        speaking = m[(t >= v_start) & (t <= v_end)]
        threshold = 1.3 * (np.median(speaking) if len(speaking) else m.mean())
        # In point: after the last face change before the voice, no later than 0.02 s before the voice
        prior = t[(t >= v_start - BEFORE[0]) & (t < v_start - BEFORE[1]) & (m > threshold)]
        cut_in = min(prior[-1] + frame, v_start - BEFORE[1]) if len(prior) else v_start - BEFORE[0]
        # Out point: tight, just after the audible end; any change after the voice (face, mouth, eyes, body) is cut out,
        # even if that trims the tail of the final consonant; never before the end of the voice plus one frame
        air, window = AFTER[row.get("intonation", "closed")]
        floor = v_end + frame
        cut_out = audible + air
        later = t[(t > v_end) & (t <= audible + window) & (m > threshold)]
        if len(later): cut_out = min(cut_out, max(later[0] - frame, floor))
        final[lab] = {"eyes_move_before_end": False}
        if not row.get("end_gesture") and not row.get("hold"):
            pause = row.get("pause", 0)
            gz = Gaze(f, max(0, v_end - 1.2), audible + window + pause + 0.15, audible)
            s = gz.first_jump(audible, v_start, v_end, audible + window)              # the eyes move or the body leans
            if s is not None: cut_out = min(cut_out, max(s - frame, floor))
            s = gz.mouth_change(v_end)                                        # the mouth leaves the last syllable's shape
            if s is not None: cut_out = min(cut_out, max(s, floor))
            # the eyes move before the last syllable ends: the word stays whole and the take is marked
            r0 = max(v_start, v_end - 0.25)
            final[lab]["eyes_move_before_end"] = gz.first_jump(r0, v_start, r0, v_end) is not None
            if pause:
                # stillness after the out point, where the pause will run
                s = gz.first_jump(audible, v_start, cut_out, cut_out + pause)
                final[lab]["still_pause"] = round(max(0, (s - frame if s is not None else cut_out + pause) - cut_out), 2)
        if row.get("end_gesture"):
            # Closing gesture: it is content, so the take runs until the image detail collapses after the voice
            base = np.median(detail[(t >= v_start) & (t <= v_end)])
            collapsed = t[(t > v_end) & (detail < 0.25 * base)]
            if len(collapsed):
                # the gesture is complete on the frame with the least detail in the next 0.4 s
                win = (t >= collapsed[0]) & (t <= collapsed[0] + 0.4)
                cut_out = t[win][np.argmin(detail[win])] + 3 * frame       # three frames later: the gesture is seen complete
            else: print(f"  {row['clip']} {lab}: the end of the closing gesture was not found (the image detail never collapses); set manual_out", flush=True)
        if row.get("hold"):
            # Reaction asked for by the script after the sentence: it is content, the shot is held without looking at the face change,
            # without reaching the next take of the same clip
            nxt = [x["start"] for x in T.values() if x["file"] == row["file"] and x["start"] > v_end]
            cut_out = min(v_end + row["hold"], min(nxt) - 0.05) if nxt else v_end + row["hold"]
        if lab in row.get("manual_out", {}): cut_out = row["manual_out"][lab]   # manual adjustment (e.g., holding a visual punchline)
        cuts[lab] = [round(max(0, cut_in), 3), round(cut_out, 3)]
        edges[lab] = [round(v_start, 3), round(v_end, 3)]
    row["cuts"], row["voice"], row["final"] = cuts, edges, final
    if row["file"] in zones: row["face"] = [round(float(v), 3) for v in zones[row["file"]]]
    choose_favorite(row)
    print(row["clip"], " ".join(f"{k.split()[1]}:{v[0]:.2f}-{v[1]:.2f}" for k, v in cuts.items()), flush=True)
json.dump(sentences, open(sj, "w"), ensure_ascii=False, indent=1)
