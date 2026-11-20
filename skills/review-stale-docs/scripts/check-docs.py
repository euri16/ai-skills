#!/usr/bin/env python3
"""Check a project's Markdown documents against the files that really exist.

Reports, for every .md file under ROOT:
  ERROR  a relative link that points to a file or folder that does not exist
  ERROR  a "Last reviewed: YYYY-MM-DD" date older than --max-age days
  ERROR  a missing "Last reviewed:" line, only with --require-review-date
  WARN   a path written in backticks (`src/app.py`) that starts in an existing folder but does not exist
  INFO   a document that no other document links to or names (a candidate to retire)

Exit code: 1 if there is any ERROR (or any WARN with --strict), 0 otherwise.
Python 3.7 or later, standard library only. Run with --help for the options.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__", "dist", "build",
    "target", "out", ".next", ".cache", ".idea", ".vscode", "vendor", "coverage",
}
# Files an agent or a person finds by location, so nobody needs to link to them.
ENTRY_POINTS = {"README.md", "AGENTS.md", "CLAUDE.md", "SKILL.md", "CHANGELOG.md", "LICENSE.md", "CONTRIBUTING.md"}

LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
CODE_SPAN = re.compile(r"`([^`\n]+)`")
REVIEWED = re.compile(r"^\s*(?:[-*]\s*)?(?:\*\*)?last reviewed:?(?:\*\*)?:?\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
FENCE = re.compile(r"^\s*(```|~~~)")
KNOWN_EXT = re.compile(r"\.(md|py|sh|mjs|js|ts|tsx|jsx|json|ya?ml|toml|html|css|sql|txt|kt|kts|swift|go|rs|rb|java|gradle|env\.example)$")
PLACEHOLDER = re.compile(r"[<>{}*$|]|\.\.\.|YYYY|\s")


def find_docs(root: Path) -> list[Path]:
    docs = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        docs += [Path(dirpath, f) for f in filenames if f.lower().endswith(".md")]
    return sorted(docs)


def prose_lines(text: str):
    """Yield (line number, line) for lines outside fenced code blocks."""
    in_fence = False
    for n, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield n, line


def looks_like_path(span: str) -> bool:
    if PLACEHOLDER.search(span) or "://" in span or span.startswith(("-", "@", "#", "~")):
        return False
    return "/" in span or bool(KNOWN_EXT.search(span))


def inside_project(span: str, doc: Path, root: Path) -> bool:
    """True when a missing path starts in a folder that exists, so it points into this project.

    A bare file name (`package.json`) or a path under a folder the project does not have
    (`.other-tool/config`) is a generic mention, not a broken reference.
    """
    while span.startswith("./"):
        span = span[2:]
    first = span.split("/", 1)
    if len(first) < 2 or not first[1]:
        return False
    return (doc.parent / first[0]).is_dir() or (root / first[0]).is_dir()


def resolve(target: str, doc: Path, root: Path) -> list[Path]:
    """Candidate locations for a reference: relative to the document, then to the root."""
    target = target.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return []
    if target.startswith("/"):
        return [root / target.lstrip("/")]
    return [(doc.parent / target), (root / target)]


def main() -> int:
    ap = argparse.ArgumentParser(description="Check Markdown documents against the files that exist.")
    ap.add_argument("root", nargs="?", default=".", help="project root (default: current folder)")
    ap.add_argument("--max-age", type=int, default=180, help="days before a 'Last reviewed:' date is stale (default 180)")
    ap.add_argument("--require-review-date", action="store_true", help="every document must have a 'Last reviewed:' line")
    ap.add_argument("--no-paths", action="store_true", help="skip the check of paths written in backticks")
    ap.add_argument("--no-orphans", action="store_true", help="skip the list of documents nobody references")
    ap.add_argument("--strict", action="store_true", help="exit 1 on warnings too")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"not a folder: {root}", file=sys.stderr)
        return 2

    today = dt.date.today()
    docs = find_docs(root)
    referenced: set[Path] = set()
    findings: list[tuple[str, str, int, str]] = []

    def report(level: str, doc: Path, line: int, msg: str) -> None:
        findings.append((level, str(doc.relative_to(root)), line, msg))

    for doc in docs:
        text = doc.read_text(encoding="utf-8", errors="replace")
        reviewed = None
        for n, line in prose_lines(text):
            m = REVIEWED.match(line) if reviewed is None else None
            if m:
                reviewed = (n, m.group(1))
            for target in LINK.findall(line):
                if "://" in target or target.startswith(("mailto:", "#", "tel:")):
                    continue
                candidates = resolve(target, doc, root)
                hit = next((c for c in candidates if c.exists()), None)
                if hit:
                    referenced.add(hit.resolve())
                elif candidates and not PLACEHOLDER.search(target):
                    report("ERROR", doc, n, f"broken link: {target}")
            for span in CODE_SPAN.findall(line):
                span = span.strip().rstrip(".,:;")
                if not looks_like_path(span):
                    continue
                hit = next((c for c in resolve(span, doc, root) if c.exists()), None)
                if hit:
                    referenced.add(hit.resolve())
                elif not args.no_paths and inside_project(span, doc, root):
                    report("WARN", doc, n, f"path not found: {span}")

        if reviewed:
            n, value = reviewed
            try:
                age = (today - dt.date.fromisoformat(value)).days
            except ValueError:
                report("ERROR", doc, n, f"invalid review date: {value}")
            else:
                if age > args.max_age:
                    report("ERROR", doc, n, f"last reviewed {age} days ago (limit {args.max_age})")
        elif args.require_review_date:
            report("ERROR", doc, 1, "no 'Last reviewed: YYYY-MM-DD' line")

    if not args.no_orphans:
        for doc in docs:
            if doc.name not in ENTRY_POINTS and doc.resolve() not in referenced:
                report("INFO", doc, 1, "no other document links to or names this file")

    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    for level, path, line, msg in sorted(findings, key=lambda f: (order[f[0]], f[1], f[2])):
        print(f"{path}:{line}: {level} {msg}")

    counts = {k: sum(1 for f in findings if f[0] == k) for k in order}
    print(f"{len(docs)} documents: {counts['ERROR']} errors, {counts['WARN']} warnings, {counts['INFO']} unreferenced")
    failed = counts["ERROR"] > 0 or (args.strict and counts["WARN"] > 0)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
