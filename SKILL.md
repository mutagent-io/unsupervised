---
name: unsupervised
description: >-
  Architech, Mutagent's software-engineering harness, and its Software
  Factory: install it, onboard a repository, set up the factory locally
  (then on Mutagent Cloud if wanted) and hand it work; agents plan, build,
  review and ship, by default the user approves plan and merge. Works
  from any agent harness that can run shell commands. Use to set up or
  operate Architech or the factory, pick a lifecycle command (/spec,
  /publish, /dispatch, /execute, /review, /ship, /monitor), or hand
  Architech a task. In a repository already set up with Architech, also for
  any build, fix or feature request: delegate it, never write the code
  yourself. Triggers: "architech", "install architech", "set up architech",
  "run architech", "dispatch to architech", "delegate to architech",
  "architech -p", "software factory", "architech factory", "let agents
  build this unsupervised". Not for unsupervised machine learning, for
  building or evaluating LLM agents (Helix), for the Agent Factory
  (mutagent factory), or for changing Architech itself.
license: MIT
compatibility: >-
  Any agent harness that can read files and run shell commands; tmux is
  optional. Checked on macOS with Claude Code and with Codex (whose default
  sandbox asks you to approve tmux and a few other commands). Linux: install
  checked on Ubuntu 24.04 arm64, no model run yet; Linux x64 and other
  harnesses expected to work, not yet tested. Needs bash, curl, a SHA-256
  tool, git and network access, and the user's own terminal once for the
  installer's email prompt.
metadata:
  author: mutagent
  skill_version: "0.1.4"
  architech_checked: "0.1.67"
  homepage: "https://github.com/mutagent-io/unsupervised"
  docs: "https://docs.mutagent.io/architech/overview"
---

# unsupervised: get Architech running, then let it work

Architech is a harness for software engineering. You run `architech` in a
repository, describe the change, and a team of agents plans it, builds it,
tests it and reviews it. With the default policy (`calibrating`) the person
approves **every plan** and **every merge**; "unsupervised" here means the
agents do the work in between without someone watching each step. The
factory's own `unsupervised` autonomy preset is different: it lets small
plans start and reviewed, green changes merge on their own (references/factory.md,
section 2). You never change that setting without the user's explicit ask.

This skill is for the agent the user talks to: **your harness**, operating
Architech and its Software Factory for them, locally and on Mutagent Cloud. It
works in three phases: **start** (install), **setup** (sign in, model,
onboard, the local factory, then the cloud question) and **operate** (hand
work over, relay questions, follow runs, report). Each phase works with
nothing more than reading files and running shell commands.

**You delegate; Architech writes the code.** A build, fix or feature request
in a repository set up with Architech goes to Architech or the factory, never
into your own edits: section 5.

| Phase | Section | Details |
|---|---|---|
| Start: install, update, remove | 3 | [references/install.md](references/install.md) |
| Setup: first session, `/login`, `/model`, `/onboard`, local factory, the cloud question | 4 | [references/onboard.md](references/onboard.md) |
| Operate: delegate a task, follow it, report | 5 | [references/dispatch.md](references/dispatch.md) |
| Which command or flow fits | 6 | [references/workflows.md](references/workflows.md) |
| Software Factory manual: set up local, run local, move to cloud, run on cloud, runs, failures, safety | 4-6 | [references/factory.md](references/factory.md) |
| "What is...", "is it safe to..." | | [references/faq.md](references/faq.md) |

Read only what the request needs. Commands and behaviour can change between
releases. When this skill and the live product disagree, the product wins: the
boot screen a session prints (the lifecycle commands, Full-Loop and Fast Mode
come from it), `/help` in a session, and
https://docs.mutagent.io/architech/overview.

## 1. What your harness needs

| Capability | Used for | Without it |
|---|---|---|
| Read files | This skill | Required |
| Run shell commands | Checks, headless runs, tmux | Give the user each command and ask for its output |
| Keep a command running after the shell call returns | Headless runs longer than one call | Use tmux as the detacher, keep the cap under one call's limit, or the user runs it |
| tmux | A background session that can ask questions | Headless only, or the user runs `architech` in their terminal |
| Ask its user a question mid-task | Relaying Architech's questions | The brief must hold every answer (headless only) |
| Delegate to sub-agents | Several runs in parallel | One run at a time |

What is known per host:

| Host | Notes |
|---|---|
| **Claude Code** | Loads this skill natively (plugin, or a folder in `~/.claude/skills`). A shell call stops after 2 minutes by default, 10 at most; it can run a command in the background and come back to it. |
| **Codex** | Loads this skill from `~/.agents/skills` or a repository's `.agents/skills`. Checked with codex-cli 0.159.0 in its default sandbox: every `tmux -L unsupervised` call (its socket lives outside the workspace), `architech update --check` (it writes outside the workspace) and `pgrep` stop for your approval, about 25 for a setup and one run; reads in the workspace and the headless run itself need none. Expect them and approve each one. Codex offers to stop asking for `tmux -L unsupervised` commands, but that saves a lasting rule: choose it only if you want it permanently. |
| **Other harnesses** | Point it at [AGENTS.md](AGENTS.md) or this file. Before the first run, find out from its docs or a quick test: does a shell call have a time limit, does a process started with `nohup ... &` survive the call, is tmux installed, and can it ask you a question mid-task? Section 5 picks the mode from the answers. |

## 2. Ground rules (every phase)

1. **Ask before you install or write.** The installer, onboarding's file
   changes and any merge need the user's yes. Say what will happen first.
2. **Show the installer before it runs.** Download it to a file, let the user
   read it, then run it. Never pipe a script you have not shown into a shell.
3. **The first install needs the user's own terminal.** The installer asks for
   an email on a terminal prompt, which no agent's shell can answer. It asks
   only for an email, which the download service must accept (Early Access).
4. **No secrets on a command line.** Model sign-in happens inside a session
   with `/login`, by the user. Never ask for a key in chat or a command.
5. **The live session owns the command list.** For anything not named in
   section 6, run `/help` and use what it prints; never guess a command.
6. **A finished task is not permission to merge.** You never merge, and you
   never approve a plan or a merge for the user. When Architech asks is the
   factory's `policy.autonomy`: under the default, `calibrating`, every plan
   and every merge waits for the user; with no factory file, every merge
   does. Headless runs open pull requests only. `/ship` and `/execute` can
   merge: they are the user's, in an interactive session, and you tell the
   user that before you start one.
7. **Report what Architech said, not what you hoped.** Quote its output and
   its last line. An exit code of 0 means the turn ended, not that the work
   is done.
8. **Architech writes the project's code, not you** (section 5).

## 3. Start: install Architech

1. **Already there?** `architech --version`. A version means it is installed:
   run `architech update --check` and go to section 4.
2. **Check the machine:** macOS or Linux, `bash`, `curl`, `git`, and
   `shasum` or `sha256sum`. Windows is not supported; WSL (Linux) may work
   but is untested.
3. **Ask, then download and show the installer:**
   ```bash
   curl -fsSL https://api.mutagent.io/architech/install.sh -o architech-install.sh
   ```
4. **The user runs it in their own terminal:** `bash architech-install.sh`.
   It asks for an email once, checks the download's checksum and prints where
   it put the `architech` command. It does not edit `PATH` or shell profiles.
   Wait for the user to say it finished.
5. **Verify:** `architech --version`, then `architech doctor --strict`. Quote
   both outputs.

## 4. Setup: sign in, pick a model, onboard

All three happen inside an interactive session (`architech` in the
repository), and two of them belong to the user: `/login` (their keys) and
the approvals `/onboard` asks for. Sign-in is once per machine; headless runs
use it too.

- **With tmux and a way to ask the user:** start a background session (section
  5). The user attaches to it for `/login` and `/model`; you then type
  `/onboard` and relay each of its questions.
- **Otherwise:** the user runs `architech` in their own terminal and types
  `/login`, `/model`, then `/onboard`. Help them answer from what you know of
  the repository.
- **Never headless:** `/onboard` asks before it scans and before it writes,
  and a headless run cannot ask.

What onboarding asks and writes: [references/onboard.md](references/onboard.md).

**Local first, then ask about the cloud.** Onboarding sets up the local
factory, with or without a board: a `factory.yaml` with `mode: local`, worked
from the user's own session ([references/factory.md](references/factory.md),
section 2). Once onboarding is done, ask the user whether to move the factory
to Mutagent Cloud, and say what that means: on the cloud, issues on the board
that a person labels for pickup run in Mutagent's sandboxes, even with this
machine off, and the user approves on GitHub (labels or a pull-request
review); local keeps every run in their session on this machine. Never
move it without a yes. "Not now" means stay local and carry on with the work;
don't ask again unless they bring it up. A yes: factory.md, section 4. No
board yet? Ask anyway, and say the cloud needs one: an organisation's GitHub
Project (on a personal account, the repository's own issues, which the CLI
can't push yet on 0.1.67: factory.md, section 2); meanwhile Architech works
locally without one.

## 5. Operate: hand work to Architech

**Delegate, never implement.** A request to build, add, fix or change code
goes to Architech. Your part is the brief, the relayed questions, following
the run and the report. You never edit, create or delete the project's files
yourself, not even a one-line fix; briefs and run folders live outside the
project. Check, then route; the first match wins:

1. **Not set up, and the user didn't ask for Architech** (`git ls-files
   '*factory.yaml'` prints nothing and there is no `.architech` folder): the
   skill steps aside. Say in one line that this repository isn't set up with
   Architech, offer to onboard it, and don't take the task over.
2. **A cloud factory** (its `factory.yaml` says `mode: cloud`): ask whether
   this job runs on the cloud or in a local session. Cloud: factory.md,
   sections 5 and 6.
3. **A local factory, or Architech without a board:** start Architech in the
   repository, in a background session or headless (below). A feature:
   `/spec` -> `/publish` -> `/dispatch`. A contained change:
   `/execute "<goal>"`, which merges as the merge rules allow (by default,
   `calibrating`, the user approves the merge): say so first.
   Or type the request in plain words and let the session pick.
4. **The user asked for Architech, but it is not installed or not
   onboarded:** set it up first (sections 3 and 4, local first, then the
   cloud question), then hand the work over.

You change the code yourself only when the user explicitly asks you to ("do
it yourself, without Architech"), and then you say first that you are not
using Architech or the factory for it. "Set it up", "quickly" or a slow run
is not that ask.

Two ways to hand Architech a task. The difference is **who answers its
questions**.

| | Headless run | Background session |
|---|---|---|
| Start | `architech -p "<brief>"` via the runner | `architech` in a tmux pane |
| Can it ask questions? | **No.** It decides itself or stops | **Yes.** The question shows in the pane; you relay it |
| Result | `verdict.txt`, `out.txt`, exit code | Read from the pane; the user can attach and watch |
| Needs | Shell; a way to outlast one call | Shell, tmux, a way to ask the user |
| Never for | Merging (`/ship`, `/execute`) | Answering a plan or merge approval for the user |

Pick by what your harness can do (section 1): shell and tmux and asking ->
either mode; shell without tmux -> headless only, or the user runs the
session; no shell -> the user runs Architech and you write the brief and read
what they paste back.

`<skill-dir>` below is the folder that holds this SKILL.md. The runner lives
in its `scripts/` folder, not in the project, so always call it by its absolute
path; the commands then work from any directory. If your harness showed the
skill's folder when it loaded it, that is `<skill-dir>`. If it shows the skill
only by name or URI, try these in order and use the first where
`<skill-dir>/scripts/run-headless.sh` exists:

1. `./.claude/skills/unsupervised` and `./.agents/skills/unsupervised` (in the
   project)
2. `~/.claude/skills/unsupervised` and `~/.agents/skills/unsupervised`
3. `~/.claude/plugins/cache/<marketplace>/unsupervised/<version>/` (the
   installed plugin copy; use the newest version)

Never search the whole home folder, never run a copy from another project, and
never re-type the runner from what you read. If none of these has it, ask the
user where the skill is.

**Headless**, with the bundled runner. It closes stdin, caps the wall clock,
grades the result, refuses `/ship` and `/execute` (both can merge), and if it
is stopped early (TERM, INT, HUP)
it stops Architech too and writes `INTERRUPTED`. A run usually outlasts one
shell call, so start it detached and check for the verdict later. When you
don't know how your harness ends a call and tmux is installed, use tmux: the
run then doesn't depend on the call at all.

```bash
mkdir -p /abs/run
# with tmux (a private server that loads no user config):
tmux -L unsupervised -f /dev/null new-session -d -s run-fix-login \
  "<skill-dir>/scripts/run-headless.sh --cwd /abs/path/to/project --brief /abs/run/brief.md --run /abs/run --timeout 1800"
# without tmux (or use your harness's own way to run in the background):
nohup <skill-dir>/scripts/run-headless.sh --cwd /abs/path/to/project \
  --brief /abs/run/brief.md --run /abs/run --timeout 1800 >/abs/run/runner.log 2>&1 &
# later:
cat /abs/run/verdict.txt   # DONE|BLOCKED|FAILED|NO_VERDICT|TIMEOUT|INTERRUPTED
```

When you check, there are three outcomes. `verdict.txt` exists: read it. No
verdict yet and the runner is still running: wait. **No verdict and the runner
is gone**: your harness killed it outright, which no script can catch, and
Architech may still be running unwatched. Stop exactly that run with
`kill -TERM -- -"$(cat /abs/run/pgid.txt)"`, then use tmux or ask the user to
run it. Details: [references/dispatch.md](references/dispatch.md).
Write the brief from [assets/brief-template.md](assets/brief-template.md):
absolute paths, the output file, "open a pull request, do not merge", and a
last-line `VERDICT:`. The run cannot ask, so the brief holds every answer.

**Background session:** start `architech` in a detached tmux pane on a tmux
server of its own, type the task, and read the pane until it finishes or asks
something.

```bash
tmux -L unsupervised -f /dev/null new-session -d -s arch-fix-login -x 160 -y 50 -c /abs/path/to/project architech
tmux -L unsupervised send-keys -t '=arch-fix-login:' -l '<task>'
tmux -L unsupervised send-keys -t '=arch-fix-login:' Enter
tmux -L unsupervised capture-pane -p -t '=arch-fix-login:' -S -200
tmux -L unsupervised send-keys -t '=arch-fix-login:' -l '/exit'   # when done, then Enter
```

Always pass `-L unsupervised`, so you never touch the user's own tmux
sessions; start that server with `-f /dev/null`, so it loads none of their
tmux config (plugins in it can restore or save their sessions); and use an
exact target (`'=name'`, plus `:` for pane commands): a bare
`-t name` also matches a longer name that starts with it. Never run
`tmux kill-server`. If `/exit` gets no answer, stop the pane's process group,
not just the tmux session: [references/dispatch.md](references/dispatch.md).

**Relaying questions:** every plan, merge, write or commit, or destructive
question goes to the user word for word, with its options; type their answer.
A choice between ways to land or merge a change is a merge question. An
earlier request ("ship it", "set it up") is not an answer to the question
Architech asks now: relay it. Answer a clarifying question yourself only when
the brief already holds the answer, and say so.
While the user is in `/login` in the pane, don't read the pane: wait until they
say they're done.

**Delegation:** if your harness delegates to sub-agents, give each run its own
brief, run directory and session name. A sub-agent that cannot reach the user
runs headless only, or passes each question back to you word for word; it
never answers a plan, merge, write or commit, or destructive question itself. The merge stays
with the user.

## 6. Commands

**The lifecycle** (printed on every boot screen). Two routes through it:

- **Full-Loop** (a feature worth planning): `/spec` -> `/publish` ->
  `/dispatch` -> `/review` -> `/ship`
- **Fast Mode** (a contained change): `/execute` -> `/review` -> `/ship`

| Command | Stage | What it does |
|---|---|---|
| `/spec` | Plan | requirements -> design -> tasks; you approve the plan |
| `/publish` | Plan | turns the approved tasks into GitHub issues |
| `/dispatch <issue>` | Build | sends a planned issue's tasks to agents in parallel |
| `/execute "<goal>"` | Build | plans, builds, reviews, then merges as your merge rules allow (by default you approve the plan and the merge) |
| `/review <issue or PR>` | Review | code review by an agent that did not write it; findings go back to the builder, 2 rounds by default |
| `/ship <PR>` | Ship | review + CI + merge + watch, under your merge rules |
| `/monitor` | Monitor | CI/CD, deploy health, production |

**Session essentials:** `/help` (every command), `/login`, `/model`,
`/onboard`, `/status` (progress of dispatched work), `/sync` (read the
project board), `/agents` (the agent roster), `/trace` (browse session logs,
read-only), `/mcp` (manage your MCP servers), `/workflows` (list saved
multi-agent scripts; it doesn't run them).

**Shell:** `architech --version`, `architech doctor --strict`,
`architech update --check`, `architech update`.

Pick a route: a small change with no board -> Fast Mode. A feature that
crosses files or repositories, or a team that tracks work in GitHub ->
Full-Loop. Details: [references/workflows.md](references/workflows.md).

**Software Factory** (board issues to reviewed pull requests). Local first:
the user's own session runs the board work (`/onboard` writes
`factory.yaml`; then `/sync`, `/spec` -> `/publish` -> `/dispatch`, or
`/execute`, which can merge). Who approves what is the file's
`policy.autonomy` (factory.md, section 2). Cloud, only after the user says
yes: Mutagent Cloud's sandboxes pick up issues on the board that a person
labels, after the user signs in, connects GitHub, and runs
`architech factory push` and `enable` (factory.md, section 4). Its shell CLI is
`architech factory`, not `mutagent factory` (a different product). Approval,
pickup and hold labels are the user's to set: never add or remove one, never approve
a gate or answer its question yourself, never merge. Details:
[references/factory.md](references/factory.md).

## 7. When something goes wrong

| Symptom | Do this |
|---|---|
| `architech: command not found` after install | Use the full path the installer printed, or add its directory to `PATH` |
| Installer says a terminal is required | The user runs it in their own terminal, not through your harness |
| `Email must look like name@example.com` | Retype it in that form |
| `Email not accepted (waitlist)` | The download service did not take that address: check the spelling and rerun; `--reset` enters a different one |
| No model answers in the session | `/login`, then `/model`; `architech doctor --strict` shows what it found |
| A headless run never returns | Use `<skill-dir>/scripts/run-headless.sh`; by hand, close stdin (`</dev/null`) and cap the time |
| A headless run ends with `NO_VERDICT` or `BLOCKED` | It could not ask you: read `out.txt`, add the missing answer to the brief, run again |
| A headless run ends `INTERRUPTED` | Something stopped the runner (often the shell call ending); Architech was stopped too. Start it detached (section 5) |
| Onboarding wants to change files you care about | Decline that step; it never overwrites context you wrote |

## 8. Sources

- Architech docs: https://docs.mutagent.io/architech/overview (install,
  onboard, agents, features)
- Software Factory docs: https://docs.mutagent.io/factory/overview
- This skill: https://github.com/mutagent-io/unsupervised
- Agent Skills format: https://agentskills.io/specification
