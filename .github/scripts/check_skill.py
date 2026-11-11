#!/usr/bin/env python3
"""Structure, limits and trigger-list checks for the unsupervised skill.

Runs with the standard library only. Exits non-zero and lists every failure.

    .github/scripts/check_skill.py
"""
from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REFERENCES = ["install.md", "onboard.md", "workflows.md", "dispatch.md", "faq.md"]
REQUIRED = [
    "SKILL.md", "README.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md",
    ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
    "agents/openai.yaml", "assets/brief-template.md", "assets/icon.png",
    "scripts/run-headless.sh", "evals/triggers.json",
] + [f"references/{r}" for r in REFERENCES]
LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def frontmatter(text: str) -> dict[str, str]:
    """Minimal YAML reader for this file's frontmatter: top-level scalars,
    folded `>-` blocks and one nested `metadata:` map."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        fail("SKILL.md: no frontmatter")
        return {}
    out: dict[str, str] = {}
    folded: str | None = None  # key of the open `>-` block
    parent = ""                # key of the open nested map
    for line in m.group(1).splitlines():
        top = re.match(r"^([a-z_-]+):\s*(.*)$", line)
        if top:
            folded, parent = None, ""
            name, val = top.groups()
            if val in (">-", ">", "|"):
                folded, out[name] = name, ""
            elif val == "":
                parent = name
            else:
                out[name] = val.strip('"')
            continue
        if folded:
            out[folded] = f"{out[folded]} {line.strip()}".strip()
            continue
        sub = re.match(r"^  ([a-z_-]+):\s*(.*)$", line)
        if sub and parent:
            out[f"{parent}.{sub.group(1)}"] = sub.group(2).strip('"')
    return out


def check_files() -> None:
    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            fail(f"missing file: {rel}")
    for p in ROOT.rglob("CLAUDE.md"):
        if ".git" not in p.parts:
            fail(f"{p.relative_to(ROOT)}: no CLAUDE.md in the repo (it would load into users' sessions)")
    script = ROOT / "scripts/run-headless.sh"
    if script.is_file() and not (script.stat().st_mode & 0o111):
        fail("scripts/run-headless.sh is not executable")
    for p in sorted(ROOT.rglob("*.md")):
        if ".git" in p.parts:
            continue
        text = p.read_text(encoding="utf-8")
        if re.search(r"\(OUTLINE\)|^# DRAFT", text, re.M):
            fail(f"{p.relative_to(ROOT)}: still an outline or draft")


def check_skill_md() -> dict[str, str]:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    fm = frontmatter(text)
    desc = fm.get("description", "")
    if fm.get("name") != "unsupervised":
        fail(f"name is {fm.get('name')!r}, expected 'unsupervised'")
    if not desc:
        fail("description is empty")
    if len(desc) > 1024:
        fail(f"description is {len(desc)} chars (limit 1024)")
    if not desc.startswith("Architech"):
        fail("description must start with 'Architech'")
    if "unsupervised machine learning" not in desc:
        fail("description must rule out unsupervised machine learning (near-miss guard)")
    if len(fm.get("compatibility", "")) > 500:
        fail("compatibility is over 500 chars")
    if fm.get("license") != "MIT":
        fail("license must be MIT")
    if "allowed-tools" in fm:
        fail("no allowed-tools: a public skill does not pre-approve its own commands")
    body = text.split("\n---\n", 1)[1] if "\n---\n" in text else text
    lines = text.count("\n") + 1
    if lines >= 500:
        fail(f"SKILL.md has {lines} lines (limit 500)")
    tokens = len(body) / 4  # rough: 4 characters per token
    if tokens >= 5000:
        fail(f"SKILL.md body is ~{int(tokens)} tokens (limit 5000)")
    return fm


def check_links() -> None:
    files = [ROOT / "SKILL.md", ROOT / "README.md"] + [ROOT / "references" / r for r in REFERENCES]
    for p in files:
        if not p.is_file():
            continue
        for target in LINK_RE.findall(p.read_text(encoding="utf-8")):
            if re.match(r"^[a-z]+:", target):
                continue
            resolved = (p.parent / target).resolve()
            if ROOT.resolve() not in resolved.parents and resolved != ROOT.resolve():
                fail(f"{p.relative_to(ROOT)}: link leaves the repo: {target}")
            elif not resolved.exists():
                fail(f"{p.relative_to(ROOT)}: broken link: {target}")
    ref_dir = ROOT / "references"
    if ref_dir.is_dir():
        for p in ref_dir.rglob("*"):
            if p.is_dir():
                fail(f"references/ must be one level deep: {p.relative_to(ROOT)}")


def check_versions(fm: dict[str, str]) -> None:
    version = fm.get("metadata.skill_version", "")
    if not version:
        fail("metadata.skill_version is missing")
        return
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    if plugin.get("version") != version:
        fail(f"plugin.json version {plugin.get('version')} != skill_version {version}")
    entries = [p for p in market.get("plugins", []) if p.get("name") == "unsupervised"]
    if not entries or entries[0].get("version") != version:
        fail(f"marketplace.json version does not match skill_version {version}")
    if plugin.get("skills") != ["."]:
        fail('plugin.json must declare "skills": ["."] (the repo root is the skill)')
    first = re.search(r"^## \[([^\]]+)\]", (ROOT / "CHANGELOG.md").read_text(), re.M)
    if not first or first.group(1) != version:
        fail(f"CHANGELOG.md top entry is not [{version}]")


def check_icon() -> None:
    p = ROOT / "assets/icon.png"
    if not p.is_file():
        return
    data = p.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        fail("assets/icon.png is not a PNG")
        return
    width, height = struct.unpack(">II", data[16:24])
    if width != height:
        fail(f"icon is {width}x{height}, must be square")
    if not 512 <= width <= 2048:
        fail(f"icon is {width} px, must be 512-2048 px")
    if len(data) >= 2 * 1024 * 1024:
        fail("icon must be under 2 MB")


def check_triggers(fm: dict[str, str]) -> None:
    p = ROOT / "evals/triggers.json"
    if not p.is_file():
        return
    cases = json.loads(p.read_text())
    should, near = cases.get("should_trigger", []), cases.get("should_not_trigger", [])
    if len(should) < 10 or len(near) < 10:
        fail("evals/triggers.json needs at least 10 should_trigger and 10 should_not_trigger prompts")
    phrases = [t.lower() for t in re.findall(r'"([^"]+)"', fm.get("description", "").split("Triggers:", 1)[-1])]
    if not phrases:
        fail("description has no Triggers: list")
    for prompt in near:
        hits = [t for t in phrases if t in prompt.lower()]
        if hits:
            fail(f"trigger phrase {hits} matches the near-miss prompt {prompt!r}")
    for prompt in should:
        if "architech" not in prompt.lower():
            fail(f"should_trigger prompt does not name Architech: {prompt!r}")


def main() -> int:
    check_files()
    fm = check_skill_md() if (ROOT / "SKILL.md").is_file() else {}
    check_links()
    if fm and (ROOT / ".claude-plugin/plugin.json").is_file():
        check_versions(fm)
    check_icon()
    check_triggers(fm)
    if failures:
        print(f"FAIL: {len(failures)} problem(s)", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    desc = fm.get("description", "")
    print(f"OK: skill checks pass (description {len(desc)}/1024 chars, "
          f"compatibility {len(fm.get('compatibility', ''))}/500 chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
