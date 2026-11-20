#!/usr/bin/env python3
"""Serves a choice page locally and saves each selection in its JSON file instantly.

Usage: python3 serve-choice-page.py <dir> [port] [file.json] [page.html]
   (defaults 8766, sentences.json and choose-takes.html; run in the background)
Open http://localhost:<port>/<page>. Serves the take choice page of analyze-video and the sounds page of
find-video-audio (`serve-choice-page.py <candidates_dir> 8767 sounds.json choose-sounds.html`). The JSON file is a list
of rows, each with "clip" as id.

Protocol used by both pages:
- GET  /state   returns {clip: chosen} for the rows that already have "chosen", so the page restores the choice on load.
- POST /choose  with {"clip": ..., "choice": ...} saves "chosen" in that row ("take" is accepted as an alias of "choice").
  The clip id is compared as text, so "2" and 2 name the same row; an id that matches no row answers 404.
So the agent reads the choice without the user copying or pasting anything. Opened as a file (file://)
the page still works with its "Copy choice" button.
"""
import json, os, sys, threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"): sys.exit(__doc__)
tdir = os.path.abspath(sys.argv[1])
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8766
jf = os.path.join(tdir, sys.argv[3] if len(sys.argv) > 3 else "sentences.json")
page = sys.argv[4] if len(sys.argv) > 4 else "choose-takes.html"
lock = threading.Lock()

class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def _json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path == "/state":
            with lock: rows = json.load(open(jf))
            return self._json({r["clip"]: r["chosen"] for r in rows if r.get("chosen")})
        return super().do_GET()
    def do_POST(self):
        if self.path != "/choose": return self._json({"error": "unknown path"}, 404)
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or "{}")
        choice = data.get("choice", data.get("take"))
        clip, found = str(data.get("clip")), False            # the id may be a string or a number on either side
        with lock:
            rows = json.load(open(jf))
            for r in rows:
                if str(r["clip"]) == clip: r["chosen"], found = choice, True
            if found: json.dump(rows, open(jf, "w"), ensure_ascii=False, indent=1)
        if not found: return self._json({"error": f"no row with clip {clip}"}, 404)
        print(f"{clip}: {choice}", flush=True)
        return self._json({"ok": True})

print(f"http://localhost:{port}/{page}", flush=True)
ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=tdir)).serve_forever()
