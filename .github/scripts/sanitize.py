#!/usr/bin/env python3
"""
Check that nothing private or machine-specific ships in this public repo.

The whole repository is the installed skill folder, so every text file is
scanned, not only the skill's markdown. Patterns are generic on purpose: a
public list of private names would publish the names it protects. Maintainers
run their own private list before each pull request (see CONTRIBUTING.md).

Usage:
    ./.github/scripts/sanitize.py --check     # verify only (CI)
    ./.github/scripts/sanitize.py --check <path>
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()

# (label, regex). Each one is generic: shapes, not names.
LEAK_PATTERNS: list[tuple[str, str]] = [
    ("absolute home path", r"(?<![\w.~])/(?:Users|home)/[A-Za-z0-9._-]+/"),
    ("Windows user path", r"[A-Za-z]:\\Users\\"),
    ("macOS temp path", r"/var/folders/[a-z0-9_]{2}/"),
    ("private key block", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("GitHub token", r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"),
    ("API key", r"\b(?:sk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,}|xox[abpr]-[A-Za-z0-9-]{10,})"),
    ("AWS key id", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("bearer token", r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{24,}"),
    ("assignment of a secret", r"(?i)\b(?:api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"\s<>]{12,}['\"]"),
]
# Links that leave the repository are checked by check_skill.py, which resolves them.
LEAK_RE = [(label, re.compile(rx)) for label, rx in LEAK_PATTERNS]

SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__"}
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".gz", ".zip"}


def files_in(scope: Path) -> list[Path]:
    if scope.is_file():
        return [scope]
    out = []
    for p in sorted(scope.rglob("*")):
        if not p.is_file() or p.resolve() == SELF:
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(scope).parts):
            continue
        if p.suffix.lower() in BINARY_SUFFIXES:
            continue
        out.append(p)
    return out


def scan(files: list[Path]) -> list[tuple[Path, int, str, str]]:
    hits = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for label, rx in LEAK_RE:
                if rx.search(line):
                    hits.append((path, lineno, label, line.strip()[:160]))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description="Check for private or machine-specific content.")
    parser.add_argument("scope", nargs="?", default=str(REPO_ROOT))
    parser.add_argument("--check", action="store_true", help="verify only (the default; kept for CI parity)")
    args = parser.parse_args()

    scope = Path(args.scope).resolve()
    if not scope.exists():
        print(f"ERROR: scope does not exist: {scope}", file=sys.stderr)
        return 2
    files = files_in(scope)
    hits = scan(files)
    if hits:
        print(f"ERROR: {len(hits)} leak match(es):", file=sys.stderr)
        base = scope if scope.is_dir() else scope.parent
        for path, lineno, label, line in hits:
            print(f"  {path.relative_to(base)}:{lineno}: [{label}] {line}", file=sys.stderr)
        return 1
    print(f"OK: {len(files)} file(s) scanned, no leaks detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
