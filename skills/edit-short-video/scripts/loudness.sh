#!/usr/bin/env bash
# Measures integrated loudness and true peak of a video or audio file and says whether it is in range.
# In range: integrated between target - 2 and target LUFS (0.5 LU of measurement tolerance) and true peak at or below -1 dBTP.
# With --fix writes <name>-norm.<ext> normalized to the target with a true peak target of -1.5 dBTP (two loudnorm passes;
# video copied without re-encoding; AAC for mp4, mov, m4a and mkv, PCM for wav) and measures that copy.
# Usage: loudness.sh <file> [--fix] [--target -14]
# Exit code: 0 in range, 1 out of range or unreadable (with --fix, the result of the normalized copy), 2 wrong arguments.
set -uo pipefail
usage() { sed -n '2,7p' "$0" | sed 's/^# //'; }
if [ $# -eq 0 ]; then usage; exit 2; fi
case "$1" in -h|--help) usage; exit 0;; esac
f="$1"; shift
fix=0; target=-14
while [ $# -gt 0 ]; do
  case "$1" in
    --fix) fix=1;;
    --target) [ $# -ge 2 ] || { echo "loudness: --target needs a value in LUFS (for example -14)" >&2; exit 2; }; target="$2"; shift;;
    *) echo "loudness: unknown argument $1" >&2; usage >&2; exit 2;;
  esac
  shift
done
if ! [[ "$target" =~ ^-[0-9]+(\.[0-9]+)?$ ]]; then echo "loudness: --target must be a negative number of LUFS, got '$target'" >&2; exit 2; fi
[ -f "$f" ] || { echo "loudness: file not found: $f" >&2; exit 1; }
TP_TARGET=-1.5   # what --fix aims at; the encoder raises the peaks a little afterwards
TP_LIMIT=-1      # what a file must not exceed

measure() {   # prints the loudnorm JSON of a file, or nothing if it has no readable audio
  ffmpeg -hide_banner -nostats -i "$1" -vn -af "loudnorm=I=$target:TP=$TP_TARGET:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p'
}
report() {    # prints the measurement; returns 0 in range, 1 out of range
  python3 -I -c '
import sys, json
d = json.loads(sys.argv[1]); target, limit = float(sys.argv[2]), float(sys.argv[3])
print("  integrated: %s LUFS   true peak: %s dBTP   LRA: %s   threshold: %s" % (d["input_i"], d["input_tp"], d["input_lra"], d["input_thresh"]))
i, tp = float(d["input_i"]), float(d["input_tp"])
ok = target - 2.5 <= i <= target + 0.5 and tp <= limit
print("  result:", "in range" if ok else "out of range (integrated %g to %g LUFS with 0.5 LU of tolerance, that is %g to %g; true peak %g dBTP or lower)" % (target - 2, target, target - 2.5, target + 0.5, limit))
sys.exit(0 if ok else 1)' "$1" "$target" "$TP_LIMIT"
}
field() { python3 -I -c 'import sys,json; print(json.loads(sys.argv[1])[sys.argv[2]])' "$1" "$2"; }

echo "== measurement: $f"
m=$(measure "$f")
[ -n "$m" ] || { echo "loudness: no audio could be measured in $f" >&2; exit 1; }
report "$m"; rc=$?
[ "$fix" = 1 ] || exit $rc

ext="${f##*.}"; out="${f%.*}-norm.$ext"
case "$(printf '%s' "$ext" | tr '[:upper:]' '[:lower:]')" in
  wav) codec=(-vn -c:a pcm_s24le);;
  mp4|mov|m4v|m4a|mkv) codec=(-c:v copy -c:a aac -b:a 256k -movflags +faststart);;
  *) echo "loudness: --fix writes mp4, mov, m4v, m4a, mkv or wav; convert $f first" >&2; exit 2;;
esac
af="loudnorm=I=$target:TP=$TP_TARGET:LRA=11:measured_I=$(field "$m" input_i):measured_TP=$(field "$m" input_tp):measured_LRA=$(field "$m" input_lra):measured_thresh=$(field "$m" input_thresh):offset=$(field "$m" target_offset):linear=true"
ffmpeg -nostdin -y -hide_banner -loglevel error -i "$f" -af "$af" "${codec[@]}" -ar 48000 "$out" || { echo "loudness: could not write $out" >&2; exit 1; }
echo "== written: $out"
m2=$(measure "$out")
[ -n "$m2" ] || { echo "loudness: no audio could be measured in $out" >&2; exit 1; }
report "$m2"
