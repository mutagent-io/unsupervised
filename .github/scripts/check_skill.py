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
REFERENCES = ["install.md", "onboard.md", "workflows.md", "dispatch.md", "factory.md", "faq.md"]
# Label roles only a person may add (docs.mutagent.io/factory/reference/factory-yaml#labels),
# by their default names. factory.md must name each one in its safety rules.
# The README's install lines, verbatim: a rewrite must keep them working.
INSTALL_LINES = (
    "/plugin marketplace add mutagent-io/unsupervised",
    "/plugin install unsupervised@unsupervised",
    "claude plugin marketplace add mutagent-io/unsupervised",
    "claude plugin install unsupervised@unsupervised",
    "npx skills add mutagent-io/unsupervised",
    "git clone https://github.com/mutagent-io/unsupervised ~/.claude/skills/unsupervised",
    "git clone https://github.com/mutagent-io/unsupervised ~/.agents/skills/unsupervised",
)
PERSON_LABELS = ("factory:pickup", "factory:approved", "factory:changes", "merge:ready",
                 "merge:changes", "merge:hold", "merge:yolo")
REQUIRED = [
    "SKILL.md", "AGENTS.md", "README.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md",
    ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
    "agents/openai.yaml", "assets/brief-template.md", "assets/icon.png",
    "scripts/run-headless.sh", "evals/triggers.json",
] + [f"references/{r}" for r in REFERENCES]
LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
# Host-neutral: hosts are named only in SKILL.md's per-host table section.
HOSTS_RE = re.compile(r"Claude Code|Codex")
# The factory.yaml language of the Architech release in metadata.architech_checked: the four
# autonomy presets, and the retired forms its validate refuses (`retired: ...`).
AUTONOMY_PRESETS = ("calibrating", "approve-plans", "approve-merges", "unsupervised")
RETIRED_FACTORY_RE = re.compile(r"policy\.merge\.preset|(?<!policy\.)`plan\.subItems`|`autonomous`|merge-ready|merge:approved")
HOST_TOOL_RE = re.compile(r"Skill tool|Bash tool|run_in_background|background option|shell tool's", re.I)
HOST_SECTION_RE = re.compile(r"^## .*harness", re.I)
PHASES = ("Start", "Setup", "Operate")
# A private tmux server must not load the user's config (plugins can restore or
# autosave their sessions into it).
TMUX_START_RE = re.compile(r"tmux\b[^`\n]*?\bnew-session")
# The runner lives in the skill's folder, not the project: always an absolute path.
RUNNER_REL_RE = re.compile(r"(?<!<skill-dir>/)\bscripts/run-headless\.sh")

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


def check_host_neutral(fm: dict[str, str]) -> None:
    desc = fm.get("description", "")
    if "Claude Code or Codex" in desc:
        fail("description ties the skill to Claude Code or Codex; describe any agent harness")
    if not re.search(r"any (?:agent|coding agent|harness)", desc, re.I):
        fail("description must say the skill works from any agent harness")
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    body = text.split("\n---\n", 1)[1]
    section, host_sections = "", 0
    for line in body.splitlines():
        if line.startswith("## "):
            section = line
            host_sections += bool(HOST_SECTION_RE.match(line))
        if HOSTS_RE.search(line) and not HOST_SECTION_RE.match(section):
            fail(f"SKILL.md names a host outside the per-host section: {line.strip()[:80]!r}")
        if HOST_TOOL_RE.search(line):
            fail(f"SKILL.md uses a host tool name: {line.strip()[:80]!r}")
    if host_sections != 1:
        fail("SKILL.md needs exactly one '## ... harness' section holding the per-host table")
    for row in ("Claude Code", "Codex", "Other harnesses"):
        if not re.search(rf"^\| \*\*{row}", body, re.M):
            fail(f"the per-host table needs a row for {row}")
    for phase in PHASES:
        if not re.search(rf"^## \d+\. {phase}\b", body, re.M):
            fail(f"SKILL.md needs a '## n. {phase}' phase section")
    for p in [*sorted((ROOT / "references").glob("*.md")), ROOT / "assets/brief-template.md",
              ROOT / "scripts/run-headless.sh", ROOT / "AGENTS.md"]:
        if not p.is_file():
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if HOSTS_RE.search(line) or HOST_TOOL_RE.search(line):
                fail(f"{p.relative_to(ROOT)}:{n} is host-specific (host notes live in SKILL.md's table): {line.strip()[:70]!r}")


def check_operate_safety() -> None:
    """tmux servers start with -f /dev/null; runner calls use <skill-dir>/scripts/."""
    docs = [ROOT / "SKILL.md", ROOT / "AGENTS.md", ROOT / "README.md", *sorted((ROOT / "references").glob("*.md"))]
    for p in docs:
        if not p.is_file():
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for m in TMUX_START_RE.finditer(line):
                if "-f /dev/null" not in m.group(0):
                    fail(f"{p.relative_to(ROOT)}:{n} starts tmux without -f /dev/null: {line.strip()[:70]!r}")
            if RUNNER_REL_RE.search(line):
                fail(f"{p.relative_to(ROOT)}:{n} calls the runner by a relative path; use <skill-dir>/scripts/run-headless.sh")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8") if (ROOT / "SKILL.md").is_file() else ""
    if not re.search(r"`<skill-dir>`.*folder", skill):
        fail("SKILL.md must say what <skill-dir> is (the folder holding SKILL.md)")
    for where in ("./.claude/skills/unsupervised", "./.agents/skills/unsupervised",
                  "~/.claude/skills/unsupervised", "~/.agents/skills/unsupervised"):
        if where not in skill:
            fail(f"SKILL.md must list {where} among the places to find <skill-dir>")
    if "Never search the whole home folder" not in skill or "never re-type the runner" not in skill:
        fail("SKILL.md must forbid searching the whole home folder and re-typing the runner")
    relay = re.search(r"^\*\*Relaying questions:\*\*(.*?)(?=\n\n)", skill, re.M | re.S)
    relay = " ".join(relay.group(1).split()) if relay else ""
    if "plan, merge, write or commit, or destructive" not in relay or "land or merge" not in relay:
        fail("SKILL.md's Relaying questions paragraph must relay plan, merge, write or commit, and destructive questions, and treat a landing route as a merge question")
    onboard = (ROOT / "references/onboard.md").read_text(encoding="utf-8")
    flat = " ".join(onboard.split())
    if ("plan, merge, write or commit, or destructive" not in flat.lower()
            or "write or commit question" not in flat.split("## 4.", 1)[-1]):
        fail("onboard.md must relay plan, merge, write or commit, and destructive questions, including the commit question in section 4")
    for p in sorted((ROOT / "references").glob("*.md")):
        if re.search(r"[Aa]nswer for the user only when they asked", " ".join(p.read_text(encoding="utf-8").split())):
            fail(f"{p.relative_to(ROOT)} lets the agent answer for the user because they asked earlier")
    dispatch = (ROOT / "references/dispatch.md").read_text(encoding="utf-8")
    if "pgid.txt" not in dispatch or not re.search(r"[Nn]o `verdict\.txt`", dispatch):
        fail("dispatch.md must cover the hard-kill outcome: no verdict.txt, stop the group named in pgid.txt")


def check_factory(fm: dict[str, str]) -> None:
    """The Software Factory page: linked, its CLI not confused with the Agent Factory's,
    and the person-only rules (labels, merge, destructive commands) stated."""
    p = ROOT / "references/factory.md"
    if not p.is_file():
        return
    if "Software Factory" not in fm.get("description", ""):
        fail("description must name the Software Factory")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if "(references/factory.md)" not in skill:
        fail("SKILL.md must link references/factory.md")
    text = " ".join(p.read_text(encoding="utf-8").split())
    if "`architech factory`" not in text or "`mutagent factory`" not in text or "Agent Factory" not in text:
        fail("factory.md must say the Software Factory CLI is `architech factory`, not `mutagent factory` (the Agent Factory)")
    for preset in AUTONOMY_PRESETS:
        if f"`{preset}`" not in text:
            fail(f"factory.md must name the autonomy preset `{preset}`")
    for doc in [ROOT / "SKILL.md", ROOT / "README.md", *sorted((ROOT / "references").glob("*.md"))]:
        for n, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1):
            if RETIRED_FACTORY_RE.search(line):
                fail(f"{doc.relative_to(ROOT)}:{n} names a retired factory.yaml form or label: {line.strip()[:70]!r}")
    safety = re.search(r"^## \d+\. Safety\b(.*?)(?=^## |\Z)", p.read_text(encoding="utf-8"), re.M | re.S)
    if not safety:
        fail("factory.md needs a '## n. Safety' section")
        return
    rules = " ".join(safety.group(1).split())
    for label in PERSON_LABELS:
        if f"`{label}`" not in rules:
            fail(f"factory.md's safety section must name the person-only label `{label}`")
    for phrase in ("Never add or remove", "Never merge", "--force", "word for word", "`/execute`",
                   "--request-changes"):
        if phrase not in rules:
            fail(f"factory.md's safety section must say {phrase!r}")


def check_execute_merges() -> None:
    """/execute ends by merging as the merge rules allow (docs: lifecycle-commands).
    Every paragraph or row that says what it does must say so; the runner refuses it."""
    for rel in ("SKILL.md", "README.md", "references/workflows.md", "references/factory.md"):
        p = ROOT / rel
        if not p.is_file():
            continue
        for block in re.split(r"\n\s*\n", p.read_text(encoding="utf-8")):
            # one unit per paragraph, list item, numbered item or table row
            for unit in re.split(r"\n(?=\s*(?:[-*] |\d+\. |\|))", block):
                flat = " ".join(unit.split())
                if re.search(r"`/execute[^`]*`[^.]*\b(plans|builds)\b", flat) and "merge" not in flat:
                    fail(f"{rel}: says what /execute does without saying it merges: {flat[:80]!r}")
    dispatch = " ".join((ROOT / "references/dispatch.md").read_text(encoding="utf-8").split())
    if "`/execute`" not in dispatch:
        fail("dispatch.md must say the runner refuses /execute")


DELEGATE = "**Delegate, never implement.**"
# The factory manual's sections, in order: local first, the cloud only after the user's yes.
FACTORY_MANUAL = ("Set up the local factory", "Run work locally", "Move to the cloud",
                  "Run work on the cloud", "Follow runs", "failures", "Safety")
CODE_REQUEST_RE = re.compile(r"^(Add|Fix|Build|Implement|Refactor|Change|Rename)\b")


def first_paragraph(section: str) -> str:
    blocks = [b for b in re.split(r"\n\s*\n", section.strip()) if b.strip()]
    return " ".join(blocks[0].split()) if blocks else ""


def check_delegate(fm: dict[str, str]) -> None:
    """The host agent hands build work to Architech or the factory; it never writes the
    project's code itself unless the user explicitly asks. First in SKILL.md's operate
    phase, in the README, in dispatch.md's decision list and in workflows.md."""
    desc = " ".join(fm.get("description", "").split())
    if "never write the code yourself" not in desc or "already set up" not in desc:
        fail("description must say: in a repository already set up, delegate and never write the code yourself")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    operate = re.search(r"^## \d+\. Operate\b[^\n]*\n(.*?)(?=^## )", skill, re.M | re.S)
    operate_text = " ".join(operate.group(1).split()) if operate else ""
    if not first_paragraph(operate.group(1) if operate else "").startswith(DELEGATE):
        fail(f"SKILL.md's operate phase must open with {DELEGATE!r}")
    for phrase in ("never edit", "explicitly asks", "not using Architech", "steps aside"):
        if phrase not in operate_text:
            fail(f"SKILL.md's operate phase must say {phrase!r}")
    setup = re.search(r"^## \d+\. Setup\b[^\n]*\n(.*?)(?=^## )", skill, re.M | re.S)
    setup_text = " ".join(setup.group(1).split()) if setup else ""
    if "**Local first, then ask about the cloud.**" not in setup_text or "without a yes" not in setup_text:
        fail("SKILL.md's setup phase must set up the local factory first and move to the cloud only after a yes")
    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").is_file() else ""
    agents = re.search(r"^## For agents\b[^\n]*\n(.*?)(?=^## |\Z)", readme, re.M | re.S)
    if not first_paragraph(agents.group(1) if agents else "").startswith(DELEGATE):
        fail(f"README's 'For agents' section must open with {DELEGATE!r}")
    intro = " ".join(readme.split("\n## ", 1)[0].split())
    if "doesn't write the code itself" not in intro:
        fail("README's intro must say your agent doesn't write the code itself")
    dispatch = (ROOT / "references/dispatch.md").read_text(encoding="utf-8")
    decide = re.search(r"^## 1\.[^\n]*\n(.*?)(?=^## )", dispatch, re.M | re.S)
    items = re.split(r"\n(?=\d+\. )", decide.group(1).strip()) if decide else []
    first_item = " ".join(items[0].split()) if items else ""
    if not first_item.startswith("1. " + DELEGATE):
        fail(f"dispatch.md's decision list must start with {DELEGATE!r}")
    if DELEGATE not in (ROOT / "references/workflows.md").read_text(encoding="utf-8"):
        fail(f"workflows.md must say {DELEGATE!r}")
    for p in [ROOT / "SKILL.md", ROOT / "README.md", *sorted((ROOT / "references").glob("*.md"))]:
        flat = " ".join(p.read_text(encoding="utf-8").split())
        if re.search(r"can do itself\? Do it there|Quick local edits you want", flat):
            fail(f"{p.relative_to(ROOT)} tells the agent to make the change itself")
    factory = (ROOT / "references/factory.md").read_text(encoding="utf-8")
    heads = re.findall(r"^## \d+\. (.*)$", factory, re.M)
    pos = [next((i for i, h in enumerate(heads) if want.lower() in h.lower()), -1) for want in FACTORY_MANUAL]
    if -1 in pos or pos != sorted(pos):
        fail(f"factory.md must be a manual with sections in this order: {', '.join(FACTORY_MANUAL)}")
    move = re.search(r"^## \d+\. Move to the cloud[^\n]*\n(.*?)(?=^## )", factory, re.M | re.S)
    if not move or "Never move" not in " ".join(move.group(1).split()):
        fail("factory.md's 'Move to the cloud' section must say: never move without the user's yes")


def check_entry_point() -> None:
    """AGENTS.md and README point harnesses to SKILL.md without copying it."""
    p = ROOT / "AGENTS.md"
    if p.is_file():
        text = p.read_text(encoding="utf-8")
        if "SKILL.md" not in text:
            fail("AGENTS.md must point to SKILL.md")
        if text.count("\n") > 30 or "```" in text:
            fail("AGENTS.md must stay a short pointer (<=30 lines, no command blocks)")
    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").is_file() else ""
    m = re.search(r"^## For agents\b(.*?)(?=^## |\Z)", readme, re.M | re.S)
    if not m:
        fail("README.md needs a '## For agents' section")
    elif "SKILL.md" not in m.group(1) or "```" in m.group(1):
        fail("README's 'For agents' section must point to SKILL.md, not copy commands")


def check_readme_install(fm: dict[str, str]) -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").is_file() else ""
    for line in INSTALL_LINES:
        if not re.search(rf"^{re.escape(line)}$", readme, re.M):
            fail(f"README.md must keep the install line {line!r}")
    # The Quick start says which release it was tested with, and pins that release.
    # A version bump fails here until someone re-runs the Quick start and updates both.
    version = fm.get("metadata.skill_version", "")
    if not version:
        return
    if not re.search(rf"^Tested on \d{{4}}-\d{{2}}-\d{{2}} with `unsupervised` v{re.escape(version)}\b", readme, re.M):
        fail(f"README's Quick start needs a 'Tested on <YYYY-MM-DD> with `unsupervised` v{version}' line")
    pin = f"git clone --branch v{version} --depth 1 https://github.com/mutagent-io/unsupervised ~/.claude/skills/unsupervised"
    if not re.search(rf"^{re.escape(pin)}$", readme, re.M):
        fail(f"README.md must pin the current release: {pin!r}")


def check_release_gate() -> None:
    """A push to main publishes only after Validate passed on that commit."""
    p = ROOT / ".github/workflows/release.yml"
    if not p.is_file():
        return
    text = p.read_text(encoding="utf-8")
    on = re.search(r"^on:\n(.*?)(?=^\S)", text, re.M | re.S)
    on = on.group(1) if on else ""
    if re.search(r"^  push:", on, re.M):
        fail("release.yml must not start on push: it starts after Validate (workflow_run)")
    if not re.search(r"^  workflow_run:\n    workflows: \[Validate\]", on, re.M):
        fail("release.yml must start on workflow_run of Validate")
    if "github.event.workflow_run.conclusion == 'success'" not in text:
        fail("release.yml must release only when that Validate run succeeded")
    if "github.event.workflow_run.head_sha" not in text:
        fail("release.yml must check out the commit Validate checked")


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
    # "./", not ".": older Claude Code releases reject a bare "." here.
    if plugin.get("skills") != ["./"]:
        fail('plugin.json must declare "skills": ["./"] (the repo root is the skill)')
    first = re.search(r"^## \[([^\]]+)\]", (ROOT / "CHANGELOG.md").read_text(), re.M)
    if not first or first.group(1) != version:
        fail(f"CHANGELOG.md top entry is not [{version}]")


def check_manifests() -> None:
    """Codex's short_description is a 25-64 char UI blurb; the brief template's VERDICT
    lines are unindented, because the runner matches the reply's last line exactly."""
    p = ROOT / "agents/openai.yaml"
    if p.is_file():
        m = re.search(r'^  short_description: "([^"]*)"$', p.read_text(encoding="utf-8"), re.M)
        if not m or not 25 <= len(m.group(1)) <= 64:
            fail(f"agents/openai.yaml short_description must be 25-64 chars, is {len(m.group(1)) if m else 'missing'}")
    brief = ROOT / "assets/brief-template.md"
    if brief.is_file():
        for n, line in enumerate(brief.read_text(encoding="utf-8").splitlines(), 1):
            if re.match(r"^\s+VERDICT:", line):
                fail(f"assets/brief-template.md:{n} indents a VERDICT line; the runner needs it flush left")


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
        if not re.search(r"architech|software factory", prompt, re.I):
            fail(f"should_trigger prompt names neither Architech nor the Software Factory: {prompt!r}")
    if len([p for p in should if re.search(r"factory", p, re.I)]) < 3:
        fail("evals/triggers.json needs at least 3 should_trigger Software Factory prompts")
    if len([p for p in near if re.search(r"factory", p, re.I)]) < 3:
        fail("evals/triggers.json needs at least 3 near misses about other factories")
    generic = [p for p in should if re.search(r"harness|delegat|sub-agent|my bot|my agent", p, re.I)]
    if len(generic) < 3:
        fail("evals/triggers.json needs at least 3 should_trigger prompts phrased by a generic harness user")
    # The eval runs in an empty folder, not an onboarded repository: a plain code request
    # there must not load the skill. Asking for Architech or the factory to build it must.
    plain = [p for p in near if CODE_REQUEST_RE.match(p) and not re.search(r"architech|factory", p, re.I)]
    if len(plain) < 3:
        fail("evals/triggers.json needs at least 3 near misses that are plain code requests outside an onboarded repository")
    build = [p for p in should if re.search(r"\b(add|fix|build)\b", p, re.I)
             and re.search(r"architech|software factory", p, re.I)]
    if len(build) < 3:
        fail("evals/triggers.json needs at least 3 should_trigger build requests that ask for Architech or the factory")


def main() -> int:
    check_files()
    fm = check_skill_md() if (ROOT / "SKILL.md").is_file() else {}
    if fm:
        check_host_neutral(fm)
    check_operate_safety()
    if fm:
        check_factory(fm)
    if fm:
        check_delegate(fm)
    check_entry_point()
    check_readme_install(fm)
    check_execute_merges()
    check_release_gate()
    check_links()
    if fm and (ROOT / ".claude-plugin/plugin.json").is_file():
        check_versions(fm)
    check_icon()
    check_manifests()
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
