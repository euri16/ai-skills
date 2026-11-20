#!/usr/bin/env bash
# Recording by sentences: splits each repetition of each clip by its silences and transcribes each take separately.
# Silero VAD (vad.py) splits the takes by speech, not by level: a low recording or noise do not affect it,
# it discards stretches without voice and separates two repetitions said with a breath between them.
# Usage: takes.sh <folder_or_video> <output_dir> [language] [vocabulary]
#   language and vocabulary work as in transcribe.sh ($WHISPER_LANGUAGE, $WHISPER_VOCABULARY).
# Output: takes.md (table file | take | time | duration | text) and takes.json (with word times relative to the clip).
# Transcribing take by take keeps Whisper from merging repetitions or inventing text in long silences.
set -euo pipefail
if [ "$#" -lt 2 ]; then sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'; exit 1; fi
src="$1"; out="$2"; lang="${3:-${WHISPER_LANGUAGE:-auto}}"; vocab="${4:-}"
base="${WHISPER_VOCABULARY:-}"
vocab="$base${base:+${vocab:+, }}$vocab"
mkdir -p "$out"; out="$(cd "$out" && pwd)"
uv run -q --python 3.11 --with mlx-whisper --with silero-vad --with onnxruntime python - "$src" "$out" "$lang" "$vocab" "$(cd "$(dirname "$0")" && pwd)" <<'PY' 2>&1 | grep -v -E "Fetching|it/s\]|%\|"
import glob, json, os, re, subprocess, sys, unicodedata
import mlx_whisper
src, out, lang, vocab, here = sys.argv[1:6]
sys.path.insert(0, here)
import numpy as np
from vad import speech_segments
MEDIA = (".mp4", ".mov", ".m4v", ".m4a", ".wav", ".mp3")
files = sorted(f for f in glob.glob(os.path.join(src, "*")) if f.lower().endswith(MEDIA)) if os.path.isdir(src) else [src]
MIN_VOICE, BEFORE, AFTER = 0.35, 0.25, 0.15   # minimum speech stretch and air before and after each take (s)
NO_VOICE = "(no voice or noise)"               # read by choose-takes.py

def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))

def voice_stretches(f, d):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-map", "0:a:0", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    y = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    return [(a, min(b, d)) for a, b in speech_segments(y) if b - a > MIN_VOICE]

# YouTube filler phrases Whisper invents in silences (Spanish and English audio); extend for other languages
HALLUCINATIONS = re.compile(r"suscr[i\u00ed]bete|gracias por ver|subt[i\u00ed]tulos|amara\.org|subscribe to|thanks for watching|subtitles by", re.I)
VOCAB_TAIL = ", ".join(vocab.split(", ")[-3:]) if vocab else None
# Whisper language codes written in the Latin alphabet. In them, a segment with letters of another script is invented
# text; in every other language (Greek, Cyrillic, Arabic, Hindi, CJK...) the script says nothing and is not checked.
LATIN_SCRIPT = set("""af az bs br ca cs cy da de en es et eu fi fo fr gl ha haw hr ht hu id is it jw la lb ln lt lv mg mi
ms mt nl nn no oc pl pt ro sk sl sn so sq su sv sw tk tl tr vi yo""".split())

def foreign_script(t, language):
    """True if the take's language uses the Latin alphabet and t has a letter of another script. Digits, punctuation
    and symbols (a currency sign, an ellipsis, a curly apostrophe) are not letters and never count."""
    return language in LATIN_SCRIPT and any(c.isalpha() and "LATIN" not in unicodedata.name(c, "") for c in t)

def real_voice(seg, language):
    # Whisper invents text in stretches without voice: low confidence, loops, prompt echo, YouTube filler phrases
    # or another alphabet in a Latin-script language
    t = seg["text"].strip()
    return not (seg.get("no_speech_prob", 0) > 0.5 and seg.get("avg_logprob", 0) < -0.5
                or seg.get("compression_ratio", 0) > 2.4 or seg.get("avg_logprob", 0) < -1.0
                or "Vocabulary" in t or (VOCAB_TAIL and VOCAB_TAIL in t)
                or HALLUCINATIONS.search(t) or foreign_script(t, language))

res, wav = [], os.path.join(out, ".take.wav")
for f in files:
    d = dur(f)
    for i, (a, b) in enumerate(voice_stretches(f, d), 1):
        a0 = max(0, a - BEFORE)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a0:.2f}", "-to", f"{min(d, b + AFTER):.2f}", "-i", f,
                        "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
        r = mlx_whisper.transcribe(wav, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language=None if lang == "auto" else lang,
                                   condition_on_previous_text=False, word_timestamps=True,
                                   initial_prompt=f"Vocabulary: {vocab}." if vocab else None)
        language = r.get("language") if lang == "auto" else lang     # the requested language, or the one Whisper detected
        segs = [s for s in r["segments"] if s["text"].strip() and real_voice(s, language)]
        txt = " ".join(s["text"].strip() for s in segs).strip()
        words = [{"word": w["word"].strip(), "start": round(a0 + w["start"], 3), "end": round(a0 + w["end"], 3)}
                 for s in segs for w in s.get("words", []) if w.get("word", "").strip()]
        res.append({"file": os.path.basename(f), "take": i, "start": round(a, 2), "end": round(b, 2),
                    "text": txt or NO_VOICE, "words": words})
        print(f"{os.path.basename(f)} take {i} {a:.1f}-{b:.1f}: {res[-1]['text']}", flush=True)
if os.path.exists(wav): os.remove(wav)
json.dump(res, open(os.path.join(out, "takes.json"), "w"), ensure_ascii=False, indent=1)
with open(os.path.join(out, "takes.md"), "w") as o:
    o.write("# Takes per clip\n\n| File | Take | Time | Duration | Text (Whisper) |\n|---|---|---|---|---|\n")
    for x in res:
        o.write(f"| {x['file']} | {x['take']} | {x['start']}-{x['end']} s | {x['end'] - x['start']:.1f} s | {x['text']} |\n")
print(f"{len(res)} takes -> {out}/takes.md, takes.json")
PY
rm -f "$out/.take.wav"
