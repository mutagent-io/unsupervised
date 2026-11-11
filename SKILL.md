---
name: unsupervised
description: >-
  Architech, Mutagent's software-engineering harness: install it, onboard a
  repository and run it, so a team of agents plans, builds, reviews and ships
  code changes while you approve the plan and the merge. Use when someone wants
  to try or set up Architech, asks how to install, update or onboard it, which
  lifecycle command fits (/spec, /publish, /dispatch, /execute, /review, /ship,
  /monitor), how Full-Loop and Fast Mode differ, or wants to hand a task to
  Architech from Claude Code or Codex and read the result back, headless or in
  a background session that can still ask questions. Covers the public
  installer, sign-in, /onboard, approval gates, a handover brief and new-user
  questions. Triggers: "architech", "install architech",
  "set up architech", "onboard architech", "run architech", "dispatch to
  architech", "architech -p", "let agents build this unsupervised". Not for
  unsupervised machine learning, for building or evaluating LLM agents (that
  is Helix), or for changing Architech itself.
license: MIT
compatibility: >-
  Claude Code or Codex. Checked on macOS; Linux (arm64 or x64) and the Codex
  sandbox are expected to work, not yet tested. Needs bash, curl, a SHA-256
  tool, git and network
  access, and the user's own terminal once for the installer's email prompt.
  The background-session mode also needs tmux.
metadata:
  author: mutagent
  skill_version: "0.1.0"
  architech_checked: "0.1.46"
  homepage: "https://github.com/mutagent-io/unsupervised"
  docs: "https://docs.mutagent.io/architech/overview"
---

# unsupervised: get Architech running, then let it work

Architech is a harness for software engineering. You run `architech` in a
repository, describe the change, and a team of agents plans it, builds it,
tests it and reviews it. The person stays in charge of two things: **the plan**
and **the merge**. "Unsupervised" means the agents do the work in between
without someone watching each step; it never means skipping those two
approvals.

Commands and behaviour can change between releases. When this skill and the
live product disagree, the product wins: the boot screen a session prints
(the lifecycle commands, Full-Loop and Fast Mode come from it), `/help` in a
session, and https://docs.mutagent.io/architech/overview.

## 1. Route the request

| The user wants to... | Read |
|---|---|
| install Architech, update it, remove it | [references/install.md](references/install.md) |
| open a first session, sign in, run `/onboard` | [references/onboard.md](references/onboard.md) |
| know which command to run, or how the flow works | [references/workflows.md](references/workflows.md) |
| hand a task to Architech from this agent and get the result | [references/dispatch.md](references/dispatch.md) |
| ask "what is...", "why did...", "is it safe to..." | [references/faq.md](references/faq.md) |

Read only the file the request needs. Each one is self-contained.

## 2. Ground rules (every journey)

1. **Ask before you install or write.** The installer, onboarding's file
   changes and any merge need the user's yes. Say what will happen first.
2. **Show the installer before it runs.** Download it to a file, let the user
   read it, then run it. Never pipe a script you have not shown into a shell.
3. **The first install needs the user's own terminal.** The installer asks for
   an email on a terminal prompt, which an agent's shell tool cannot answer.
   Anyone can install; the email is all it asks for. Hand the user the exact
   command, wait for them to say it finished, then verify.
4. **No secrets on a command line.** Model sign-in happens inside the session
   with `/login`. Never ask the user to paste a key into chat or a command.
5. **The live session owns the command list.** This skill names the commands
   in section 4. For anything else, run `/help` and use what it prints; never
   guess a command or a flag.
6. **A finished task is not permission to merge.** The user reviews the plan
   and its acceptance criteria before the build, and the pull request before
   it reaches the default branch.
7. **Report what Architech said, not what you hoped.** Quote its output and
   its last line. An exit code of 0 means the turn ended, not that the work
   is done.

## 3. Quick start (new user, about ten minutes)

1. **Check the machine:** macOS or Linux, `bash`, `curl`, `git`, and
   `shasum` or `sha256sum`. Windows: use WSL.
2. **Install** (the user's terminal, after reading the script):
   ```bash
   curl -fsSL https://api.mutagent.io/architech/install.sh -o architech-install.sh
   bash architech-install.sh
   ```
   It asks for an email once, checks the download's checksum and prints where
   it put the `architech` command. It does not edit `PATH` or shell profiles.
3. **Verify:** `architech --version`, then `architech doctor --strict`.
4. **Open the project:** `cd` into the repository and run `architech`.
5. **Inside the session:** `/login` (pick a model provider), `/model`, then
   `/onboard`. Answer its questions; review the diff before you accept.
6. **First piece of work:** describe the change in plain words, or start the
   flow that fits (section 4).

## 4. Commands

**The lifecycle** (printed on every boot screen). Two routes through it:

- **Full-Loop** (a feature worth planning): `/spec` -> `/publish` ->
  `/dispatch` -> `/review` -> `/ship`
- **Fast Mode** (a contained change): `/execute` -> `/review` -> `/ship`

| Command | Stage | What it does |
|---|---|---|
| `/spec` | Plan | requirements -> design -> tasks; you approve the plan |
| `/publish` | Plan | turns the approved tasks into GitHub issues |
| `/dispatch <issue>` | Build | sends a planned issue's tasks to agents in parallel |
| `/execute "<goal>"` | Build | plans and acts in one pass |
| `/review <issue or PR>` | Review | code review by an agent that did not write it |
| `/ship <PR>` | Ship | review + CI + merge + watch, under your merge rules |
| `/monitor` | Monitor | CI/CD, deploy health, production |

**Session essentials:** `/help` (every command), `/login`, `/model`,
`/onboard`, `/status` (progress of dispatched work), `/sync` (read the
project board), `/agents` (the agent roster), `/trace` (browse session logs,
read-only), `/mcp` (your MCP servers), `/workflows` (saved multi-agent
scripts).

**Shell:** `architech --version`, `architech doctor --strict`,
`architech update --check`, `architech update`.

Pick a route: a small change with no board -> Fast Mode. A feature that
crosses files or repositories, or a team that tracks work in GitHub ->
Full-Loop. Details: [references/workflows.md](references/workflows.md).

## 5. Driving Architech from this agent

Two ways to hand Architech a task. The difference is **who answers its
questions**.

| | Headless run | Background session |
|---|---|---|
| Start | `architech -p "<brief>"` | `architech` in a tmux pane |
| Can it ask questions? | **No.** Nobody is there; it decides itself or stops | **Yes.** The question shows in the pane; you answer it |
| Result | stdout, exit code, last-line verdict | read from the pane; the user can attach and watch |
| Good for | a planned, well-briefed task; several in parallel | work with decisions in it; anything near a plan approval |
| Never for | merging (`/ship`) | answering a plan or merge approval for the user |

**Headless**, with the bundled script. It closes stdin, caps the wall clock,
grades the result, and if anything stops it early it stops Architech too and
writes `INTERRUPTED`. A run takes longer than one shell call may last (Claude
Code stops a call after 2 minutes by default, 10 at most), so **start it in
the background and poll for the verdict**. In Claude Code, use the shell
tool's background option; elsewhere, `nohup ... &`:

```bash
mkdir -p /abs/run
nohup scripts/run-headless.sh --cwd /abs/path/to/project \
  --brief /abs/run/brief.md --run /abs/run --timeout 1800 >/abs/run/runner.log 2>&1 &
# then, every minute or so, until the file exists:
cat /abs/run/verdict.txt   # DONE|BLOCKED|FAILED|NO_VERDICT|TIMEOUT|INTERRUPTED
```

The script refuses a `/ship` prompt: a headless run never merges.

Write the brief from [assets/brief-template.md](assets/brief-template.md):
absolute paths, the output file, "open a pull request, do not merge", and a
last-line `VERDICT:`. Because the run cannot ask, the brief must already hold
every answer it needs.

**Background session:** start `architech` in a detached tmux pane on a tmux
server of its own, type the task into it, and read the pane until it finishes
or asks something. Relay every plan, merge or destructive question to the user
and type their answer; answer a clarifying question yourself only when the
brief already holds the answer. The user can attach at any time.

```bash
tmux -L unsupervised new-session -d -s arch-fix-login -x 160 -y 50 -c /abs/path/to/project architech
tmux -L unsupervised send-keys -t '=arch-fix-login:' -l '<task>'
tmux -L unsupervised send-keys -t '=arch-fix-login:' Enter
tmux -L unsupervised capture-pane -p -t '=arch-fix-login:' -S -200
tmux -L unsupervised send-keys -t '=arch-fix-login:' -l '/exit'   # when done, then Enter
```

If `/exit` gets no answer, stop the pane's process group, not just the tmux
session: `kill-session` alone can leave Architech running with no screen. The
exact commands are in [references/dispatch.md](references/dispatch.md).

Always pass `-L unsupervised`, so you never touch the user's own tmux
sessions, and always an exact target (`'=name'`, plus `:` for pane commands):
a bare `-t name` also matches a longer name that starts with it, such as
another task's session. Never run `tmux kill-server`.

Commands for both modes, polling, and what to do with each verdict:
[references/dispatch.md](references/dispatch.md).

## 6. When something goes wrong

| Symptom | Do this |
|---|---|
| `architech: command not found` after install | Use the full path the installer printed, or add its directory to `PATH` |
| Installer says a terminal is required | The user runs it in their own terminal, not through this agent |
| `Email must look like name@example.com` | Retype it in that form |
| `Email not accepted (waitlist)` | The download service did not take that address: check the spelling and rerun; `--reset` enters a different one |
| No model answers in the session | `/login`, then `/model`; `architech doctor --strict` shows what it found |
| A headless run never returns | Use `scripts/run-headless.sh`; by hand, close stdin (`</dev/null`) and cap the time |
| A headless run ends with `NO_VERDICT` or `BLOCKED` | It could not ask you: read `out.txt`, add the missing answer to the brief, run again |
| A headless run ends `INTERRUPTED` | Something stopped the script (often the shell call's time limit); Architech was stopped too. Start it in the background |
| Onboarding wants to change files you care about | Decline that step; it never overwrites context you wrote |

## 7. Sources

- Architech docs: https://docs.mutagent.io/architech/overview (install,
  onboard, agents, features)
- This skill: https://github.com/mutagent-io/unsupervised
- Agent Skills format: https://agentskills.io/specification
