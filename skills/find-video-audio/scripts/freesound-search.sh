#!/usr/bin/env bash
# Searches sounds on Freesound (API v2) and, optionally, downloads the HQ MP3 previews of the first N.
# Usage: freesound-search.sh "<text>" [--license cc0|by|any] [--min 0.1 --max 1.5] [--tag loop] [--download <dir> --n 3] [--sort rating_desc|downloads_desc|score]
# --license: cc0 (default) searches CC0 only; by, CC BY only (credit required); any, both. A sound under any other
#   license (non-commercial ones included) is never listed or downloaded.
# Key: environment variable FREESOUND_API_KEY (a Freesound API v2 key), sent only to the search endpoint and never printed.
# Freesound's API terms (https://freesound.org/docs/api/terms_of_use.html) make the API free for non-commercial
#   purposes only: whether a use is commercial, and asking Freesound when it is, is the user's responsibility.
# Exits 1 when the search fails or returns nothing usable, 2 on a usage error or a missing tool or key.
set -euo pipefail
usage() { sed -n '2,8p' "$0" | sed 's/^# //'; }
case "${1:-}" in -h|--help) usage; exit 0;; "") usage >&2; exit 2;; esac
for tool in curl python3; do command -v "$tool" >/dev/null || { echo "$tool is not installed: this script needs it." >&2; exit 2; }; done
key="$(printf '%s' "${FREESOUND_API_KEY:-}" | tr -d '[:space:]')"
[ -n "$key" ] || { echo "FREESOUND_API_KEY is not set (create an account at freesound.org, request an API key and export it as FREESOUND_API_KEY). Continue with the other sources." >&2; exit 2; }
q="$1"; shift
lic="cc0"; mn=""; mx=""; tag=""; dl=""; n=3; sort="rating_desc"
while [ $# -gt 0 ]; do
  case "$1" in
    --license|--min|--max|--tag|--download|--n|--sort) [ $# -ge 2 ] || { echo "$1 needs a value." >&2; exit 2; };;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2;;
  esac
  case "$1" in
    --license) lic="$2";; --min) mn="$2";; --max) mx="$2";; --tag) tag="$2";;
    --download) dl="$2";; --n) n="$2";; --sort) sort="$2";;
  esac
  shift 2
done
filter=""
case "$lic" in
  cc0) filter='license:"Creative Commons 0"';; by) filter='license:"Attribution"';;
  any) filter='license:("Creative Commons 0" OR "Attribution")';;
  *) echo "--license takes cc0, by or any, not \"$lic\"." >&2; exit 2;;
esac
if [ -n "$mn$mx" ]; then filter="$filter duration:[${mn:-0} TO ${mx:-3600}]"; fi
if [ -n "$tag" ]; then filter="$filter tag:$tag"; fi
url=$(python3 -I - "$q" "$filter" "$sort" <<'PY'
import sys,urllib.parse
q,f,s=sys.argv[1:4]
params={"query":q,"fields":"id,name,username,license,duration,previews,tags,avg_rating,num_downloads","page_size":"15","sort":s}
if f.strip(): params["filter"]=f.strip()
print("https://freesound.org/apiv2/search/text/?"+urllib.parse.urlencode(params))
PY
)
tmpd="$(mktemp -d)"; trap 'rm -rf "$tmpd"' EXIT
resp="$tmpd/response.json"
curl -sS -H "Authorization: Token $key" -o "$resp" "$url" || { echo "The request to Freesound failed (network or curl error above)." >&2; exit 1; }
# The response goes to the parser as a file: the script itself arrives through standard input.
python3 -I - "$resp" "$dl" "$n" "$lic" <<'PY'
import sys, json, os, re, subprocess
resp, dl, n, lic = sys.argv[1:5]
if not n.isdigit() or int(n) < 1: sys.exit("--n takes a whole number of 1 or more, not \"%s\"." % n)
n = int(n)
try: d = json.load(open(resp))
except Exception: sys.exit("Freesound did not answer with JSON (empty or invalid response).")
if "results" not in d: sys.exit("Freesound error: %s" % (d.get("detail") or d))
def allowed(url):
    # Only the license asked for, and never anything but CC0 or CC BY: by-nc, sampling+ and the rest are left out,
    # whatever the search filter returned.
    u = (url or "").lower()
    return (lic != "by" and "/publicdomain/zero/" in u) or (lic != "cc0" and "/licenses/by/" in u)
found = d["results"]
res = [r for r in found if allowed(r.get("license"))]
if len(res) < len(found): print("%d result(s) left out: their license is not the one asked for (CC0, or CC BY with --license by or any)." % (len(found) - len(res)), file=sys.stderr)
if not res: sys.exit("No results under the license asked for: loosen the text, the license (--license any) or the duration range.")
print(f"{d.get('count',0)} results (showing {len(res)})")
print("| # | id | Name | Author | License | Dur. s | Rating | Downloads | Page |")
print("|---|---|---|---|---|---|---|---|---|")
for i,r in enumerate(res,1):
    print(f"| {i} | {r['id']} | {r['name']} | {r['username']} | {r['license'].split('/')[-3] if 'creativecommons' in r['license'] else r['license']} | {r['duration']:.2f} | {r.get('avg_rating') or 0:.1f} | {r.get('num_downloads',0)} | https://freesound.org/s/{r['id']}/ |")
if dl:
    os.makedirs(dl, exist_ok=True)
    failed = 0
    for r in res[:n]:
        url=(r.get("previews") or {}).get("preview-hq-mp3"); slug=re.sub(r"[^a-z0-9]+","-",r["name"].lower()).strip("-")[:40]
        out=os.path.join(dl, f"{slug}-fs{r['id']}.mp3")
        # Previews are public files: the API token is not sent to them.
        ok = bool(url) and subprocess.run(["curl","-sSfL","-o",out,url]).returncode == 0 and os.path.getsize(out) > 0
        if not ok:
            failed += 1; print("DOWNLOAD FAILED:", r["id"], r["name"], file=sys.stderr); continue
        print("downloaded:", out, "| license:", r["license"], "| author:", r["username"])
    if failed: sys.exit("%d of %d previews could not be downloaded." % (failed, min(n, len(res))))
PY
