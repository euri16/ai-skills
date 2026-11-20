#!/usr/bin/env python3
"""Proposes the favorite take of each sentence with audio and text measurements.

Usage: uv run -q --python 3.11 --with librosa python score-takes.py <recording_dir> <takes_dir>
Reads <takes_dir>/sentences.json and ../analysis/takes.json. Writes in each row "favorite" (the proposed take),
"reason" (in one line) and "metrics" per take, with its total "score". The favorite is by voice only: cuts.py then
adjusts it with what the image tells (a pause held still, eyes still at the end). Does not touch "chosen", which belongs to the user.
A row with "favorite_locked": true keeps the favorite the agent set by hand.
"reason" is text for the user: its phrases are the "label-reason-..." tags of ../assets/choose-takes.html (labels.py),
so it comes out in the language the template is in.

Measurements per take (relative to the other takes of the same sentence):
- text: similarity to the decided sentence (penalizes changed words).
- pause: the longest pause between words; more than 0.45 s sounds like a stumble (except takes joined on purpose).
- pace: words per second; fluent without rushing.
- energy: mean volume of the voice.
- expressiveness: pitch variation in semitones; a flat voice subtracts.
- final_drop: whether the pitch drops on the last word ("closed") or stays up ("open"), according to the row's "intonation".

The pitch is searched between 60 and 500 Hz, which covers low adult voices, high adult voices and children.
$VOICE_PITCH_RANGE ("min-max" in Hz, for example "70-300") narrows it to one voice when the pitch jumps an octave.
"""
import difflib, json, os, re, subprocess, sys, tempfile
if len(sys.argv) < 3: sys.exit(__doc__)
import numpy as np, librosa
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from labels import label, take_name
rec, tdir = sys.argv[1:3]
sj = os.path.join(tdir, "sentences.json")
sentences = json.load(open(sj))
T = {(x["file"], x["take"]): x for x in json.load(open(os.path.join(tdir, "../analysis/takes.json")))}
norm = lambda s: re.sub(r"[^\w ]", "", s.lower()).split()
_range = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*", os.environ.get("VOICE_PITCH_RANGE") or "60-500")
if not _range or not 40 <= float(_range[1]) < float(_range[2]) <= 2000:
    sys.exit('VOICE_PITCH_RANGE must be "min-max" in Hz, between 40 and 2000 (for example "60-500")')
PITCH_MIN, PITCH_MAX = float(_range[1]), float(_range[2])

def audio(f, a, b):
    with tempfile.NamedTemporaryFile(suffix=".wav") as w:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.2f}", "-to", f"{b:.2f}", "-i", f, "-vn", "-ac", "1", "-ar", "16000", w.name], check=True)
        y, sr = librosa.load(w.name, sr=16000)
    return y, sr

def measure(f, ks, sentence):
    xs = [T[(f, k)] for k in ks]
    words = [p for x in xs for p in x["words"]]
    if not words: return None
    a, b = words[0]["start"], words[-1]["end"]
    y, sr = audio(os.path.join(rec, f), a, b)
    # Pitch with YIN in the voiced stretches (the loudest ones); pyin loses the voice in many takes
    f0 = librosa.yin(y, fmin=PITCH_MIN, fmax=PITCH_MAX, sr=sr, frame_length=2048)
    rms = librosa.feature.rms(y=y, frame_length=2048)[0][:len(f0)]
    # a value stuck at either end of the range is YIN not finding a pitch, not a note
    voiced = (rms > rms.max() * 10 ** (-15 / 20)) & (f0 > PITCH_MIN * 1.05) & (f0 < PITCH_MAX * 0.97)
    st = 12 * np.log2(f0 / 100)
    last = words[-1]
    i0 = int((last["start"] - a) * sr / 512)
    body, tail = st[:i0][voiced[:i0]], st[i0:][voiced[i0:]]
    q = np.percentile(st[voiced], [25, 75]) if voiced.sum() > 4 else [0, 0]
    expressiveness = float(q[1] - q[0])                                             # interquartile range in semitones
    drop = float(np.median(body) - np.median(tail)) if len(tail) > 2 and len(body) > 2 else 0.0   # + = drops at the end
    pauses = [words[i + 1]["start"] - words[i]["end"] for i in range(len(words) - 1)]
    joined = len(ks) > 1
    return {
        "text": round(difflib.SequenceMatcher(None, norm(" ".join(x["text"] for x in xs)), norm(sentence)).ratio(), 3),
        "pause": round(max([p for p in pauses] or [0]) if not joined else max([p for p in pauses if p < 0.8] or [0]), 2),
        "pace": round(len(words) / max(b - a, 0.1), 2),
        "energy": round(float(20 * np.log10(np.sqrt(np.mean(y ** 2)) + 1e-9)), 1),
        "expressiveness": round(expressiveness, 2),
        "final_drop": round(drop, 2),
    }

def z(v):
    v = np.array(v, float); s = v.std()
    return (v - v.mean()) / s if s > 1e-6 else v * 0

for row in sentences:
    if row.get("favorite_locked"): continue
    intonation = row.get("intonation", "closed")
    takes = [tk if isinstance(tk, list) else [tk] for tk in row["takes"]]
    ms = [measure(row["file"], ks, row["sentence"]) for ks in takes]
    ok = [i for i, m in enumerate(ms) if m]
    if not ok: continue
    M = {k: [ms[i][k] for i in ok] for k in ms[ok[0]]}
    final = np.array(M["final_drop"]) * (1 if intonation == "closed" else -1)
    pace_med = np.median(M["pace"])
    score = (12 * (np.array(M["text"]) - 1)                          # a changed word weighs more than expressiveness
             - 2.5 * np.clip(np.array(M["pause"]) - 0.45, 0, None)   # stumbles
             - 0.6 * np.abs(z(M["pace"])) * (np.array(M["pace"]) < pace_med)  # slow subtracts, fast does not
             + 0.5 * z(M["energy"]) + 0.6 * z(M["expressiveness"]) + 0.5 * z(final))
    best = ok[int(np.argmax(score))]; m = ms[best]
    reasons = []
    if m["text"] == max(M["text"]): reasons.append(label("reason-exact" if m["text"] > 0.97 else "reason-faithful"))
    if m["pause"] <= 0.45: reasons.append(label("reason-no-stumbles"))
    if m["expressiveness"] >= np.median(M["expressiveness"]): reasons.append(label("reason-expressive"))
    if m["energy"] >= np.median(M["energy"]): reasons.append(label("reason-energy"))
    if (m["final_drop"] > 0.5) if intonation == "closed" else (m["final_drop"] < 0.5): reasons.append(label("reason-closes" if intonation == "closed" else "reason-keeps-up"))
    row["favorite"] = "Take " + "+".join(map(str, takes[best]))
    row["reason"] = ", ".join(reasons[:3]) or label("reason-balanced")
    if m["text"] < 0.97:
        exact = [i for i in ok if ms[i]["text"] > 0.97]
        alt = max(exact, key=lambda i: score[ok.index(i)]) if exact else None
        best_exact = label("reason-best-exact", take=take_name("Take " + "+".join(map(str, takes[alt])))) if alt is not None else ""
        row["reason"] += ", " + label("reason-changes-word") + (f" ({best_exact})" if best_exact else "")
    for j, i in enumerate(ok): ms[i]["score"] = round(float(score[j]), 2)       # cuts.py uses it to break ties by image
    row["metrics"] = {"Take " + "+".join(map(str, takes[i])): ms[i] for i in ok}
    print(row["clip"], row["favorite"], "·", row["reason"], flush=True)
json.dump(sentences, open(sj, "w"), ensure_ascii=False, indent=1)
