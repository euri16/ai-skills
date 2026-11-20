#!/usr/bin/env bash
# Transcribes the audio of a video or audio file locally with mlx-whisper (Apple Silicon). Does not use any API.
# Usage: transcribe.sh <video|audio> <output_dir> [language] [vocabulary]
#   language:   Whisper language code (es, en...). Default: $WHISPER_LANGUAGE, or auto-detect if unset ("auto" also detects).
#   vocabulary: proper names and terms that appear in the audio, comma-separated, so Whisper spells them correctly.
#               They are added to $WHISPER_VOCABULARY (the workspace's standing list: the creator's name, brand terms...).
# Output: transcript.txt (with times), transcript.srt, transcript.json and words.json (per-word times, for subtitles and cuts)
set -euo pipefail
if [ "$#" -lt 2 ]; then sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'; exit 1; fi
src="$1"; out="$2"; lang="${3:-${WHISPER_LANGUAGE:-auto}}"; vocab="${4:-}"
base="${WHISPER_VOCABULARY:-}"
vocab="$base${base:+${vocab:+, }}$vocab"
mkdir -p "$out"; out="$(cd "$out" && pwd)"
ffmpeg -v error -y -i "$src" -vn -ac 1 -ar 16000 "$out/.audio.wav"
uv run -q --python 3.11 --with mlx-whisper python - "$out" "$lang" "$vocab" <<'PY' 2>&1 | grep -v -E "Fetching|it/s\]|%\|"
import json, sys
import mlx_whisper
out, lang, vocab = sys.argv[1], sys.argv[2], sys.argv[3]
r = mlx_whisper.transcribe(f"{out}/.audio.wav", path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
                           language=None if lang == "auto" else lang, condition_on_previous_text=False, word_timestamps=True,
                           initial_prompt=f"Vocabulary: {vocab}." if vocab else None)
def ts(t, sep=","):
    h, m = int(t // 3600), int(t % 3600 // 60)
    return f"{h:02d}:{m:02d}:{t % 60:06.3f}".replace(".", sep)
segs = [s for s in r["segments"] if s["text"].strip()]
with open(f"{out}/transcript.txt", "w") as f:
    for s in segs:
        f.write(f"[{s['start']:6.1f}-{s['end']:6.1f}] {s['text'].strip()}\n")
with open(f"{out}/transcript.srt", "w") as f:
    for i, s in enumerate(segs, 1):
        f.write(f"{i}\n{ts(s['start'])} --> {ts(s['end'])}\n{s['text'].strip()}\n\n")
with open(f"{out}/transcript.json", "w") as f:
    json.dump([{"start": s["start"], "end": s["end"], "text": s["text"].strip()} for s in segs], f, ensure_ascii=False, indent=1)
words = [{"word": w["word"].strip(), "start": round(w["start"], 3), "end": round(w["end"], 3)} for s in segs for w in s.get("words", []) if w.get("word", "").strip()]
with open(f"{out}/words.json", "w") as f:
    json.dump(words, f, ensure_ascii=False, indent=0)
print(f"{len(segs)} segments, {len(words)} words -> {out}/transcript.txt, words.json")
PY
rm -f "$out/.audio.wav"
