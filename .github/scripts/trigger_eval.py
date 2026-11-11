#!/usr/bin/env python3
"""Run evals/triggers.json in Claude Code and report how often the skill loads.

Each prompt runs in a fresh `claude -p` session, in an empty directory, with this
repo loaded as a plugin and ONLY the Skill tool available, so a prompt can load
a skill but cannot run commands or edit files. The run stops as soon as the
model picks a skill or finishes its reply.

Uses your Claude Code sign-in (one short session per prompt). Not run in CI.

    .github/scripts/trigger_eval.py [--model sonnet] [--claude claude]
Pass: at least 90% of should_trigger prompts load it, at most 10% of near misses do.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL_ID = "unsupervised"


def run_one(claude: str, model: str, prompt: str, cwd: str, cap: int = 120) -> tuple[str | None, bool]:
    """Return (skill the model invoked or None, whether our skill was listed)."""
    cmd = [claude, "-p", prompt, "--plugin-dir", str(ROOT), "--tools", "Skill",
           "--strict-mcp-config", "--no-session-persistence", "--model", model,
           "--output-format", "stream-json", "--verbose"]
    proc = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True, start_new_session=True)
    picked, listed, deadline = None, False, time.time() + cap
    try:
        for line in proc.stdout:  # type: ignore[union-attr]
            if time.time() > deadline:
                break
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "system" and ev.get("subtype") == "init":
                names = [str(s) for s in ev.get("skills", []) + ev.get("slash_commands", [])]
                listed = any(SKILL_ID in n for n in names)
            if ev.get("type") == "assistant":
                for block in ev.get("message", {}).get("content", []):
                    if block.get("type") == "tool_use" and block.get("name") == "Skill":
                        picked = str(block.get("input", {}).get("skill") or block.get("input"))
                        break
            if picked or ev.get("type") == "result":
                break
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
    return picked, listed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--claude", default="claude")
    args = ap.parse_args()
    cases = json.loads((ROOT / "evals/triggers.json").read_text())
    rows, ok = [], True
    with tempfile.TemporaryDirectory() as cwd:
        for kind in ("should_trigger", "should_not_trigger"):
            hits = 0
            for prompt in cases[kind]:
                picked, listed = run_one(args.claude, args.model, prompt, cwd)
                if not listed:
                    print(f"ERROR: the plugin skill was not listed in the session for {prompt!r}", file=sys.stderr)
                    return 2
                loaded = bool(picked and SKILL_ID in picked)
                hits += loaded
                print(f"{'LOAD' if loaded else '----'}  {kind:<18} {prompt}  [{picked or 'no skill'}]", flush=True)
            n = len(cases[kind])
            rows.append((kind, hits, n))
    for kind, hits, n in rows:
        rate = hits / n
        passed = rate >= 0.9 if kind == "should_trigger" else rate <= 0.1
        ok &= passed
        print(f"{kind}: {hits}/{n} loaded -> {'PASS' if passed else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
