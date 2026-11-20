#!/usr/bin/env bash
# Generates or edits images with Codex's image tool and checks that the requested files were produced.
# Usage: generate.sh <folder> <prompt.txt> <output1.png> [output2.png ...] [-- image1 image2 ...]
#   <folder>       where Codex works and leaves the outputs (the piece's folder, e.g. social/<piece>/cover-src/generated)
#   <prompt.txt>   the prompt (templates in references/prompts.md); goes through standard input
#   outputs        file names the prompt asks for, relative to <folder>
#   images         attachments (base and references), relative to <folder>
# Exits 2 on a missing folder, prompt, image or tool, before touching anything; 1 if Codex ends without every output,
# keeping its log in <folder>/generate-<time>.log.
set -euo pipefail
usage="Usage: generate.sh <folder> <prompt.txt> <output1.png> [output2.png ...] [-- image1 ...]"
case "${1:-}" in -h|--help) echo "$usage"; exit 0;; esac
[ $# -ge 3 ] || { echo "$usage" >&2; exit 2; }
dir="$1"; prompt="$2"; shift 2
outputs=(); images=()
while [ $# -gt 0 ]; do [ "$1" = "--" ] && { shift; images=("$@"); break; }; outputs+=("$1"); shift; done
[ ${#outputs[@]} -gt 0 ] || { echo "No output file named. $usage" >&2; exit 2; }
command -v codex >/dev/null || { echo "The Codex CLI (codex) is missing: npm install -g @openai/codex, then codex login." >&2; exit 2; }
[ -d "$dir" ] || { echo "Folder not found: $dir" >&2; exit 2; }
[ -s "$prompt" ] || { echo "Prompt file not found or empty: $prompt" >&2; exit 2; }
prompt="$(cd "$(dirname "$prompt")" && pwd)/$(basename "$prompt")"
cd "$dir"
for i in ${images[@]+"${images[@]}"}; do [ -f "$i" ] || { echo "Image not found in $dir: $i" >&2; exit 2; }; done
for s in "${outputs[@]}"; do
  for i in ${images[@]+"${images[@]}"}; do [ "$s" != "$i" ] || { echo "$s is both an attachment and an output: the output would replace the original." >&2; exit 2; }; done
done
for s in "${outputs[@]}"; do rm -f "$s"; done                       # so an old output does not count
args=(); for i in ${images[@]+"${images[@]}"}; do args+=(-i "$i"); done
log="generate-$(date +%H%M%S).log"
rc=0
codex exec --skip-git-repo-check -s workspace-write ${args[@]+"${args[@]}"} < "$prompt" > "$log" 2>&1 || rc=$?
missing=0
for s in "${outputs[@]}"; do
  if [ -s "$s" ]; then python3 -c 'import sys;from PIL import Image;print(sys.argv[1],Image.open(sys.argv[1]).size)' "$s" 2>/dev/null || echo "$s"
  else echo "MISSING: $s" >&2; missing=1; fi
done
if [ $missing -ne 0 ]; then
  echo "Codex ended (exit code $rc) without saving every output. Read $dir/$log: if it stopped halfway, relaunch; if it says there is no image generation tool or no session, fix that first." >&2
  exit 1
fi
rm -f "$log"
