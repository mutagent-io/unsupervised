<p align="center">
  <img src="assets/icon.png" alt="Mutagent" width="96" height="96">
</p>

# unsupervised

**Turn your GitHub board into a software factory.**

**idea → spec → board → agents build in parallel → independent review → CI →
merged PR**

You sign off on the plan and the merge. The agents do the rest.

Once a repository is set up, ask your agent for a feature or a fix and it
hands the work to Architech's factory: it writes the brief, relays the
questions and reports back, but it doesn't write the code itself, unless you
explicitly ask it to (and then it tells you it isn't using the factory).

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-spec-black.svg)](https://agentskills.io/specification)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-black.svg)](https://code.claude.com/docs/en/plugins)
[![Codex skill](https://img.shields.io/badge/Codex-skill-black.svg)](https://developers.openai.com/codex/skills)

`unsupervised` is an [Agent Skill](https://agentskills.io). Install it in
Claude Code, Codex or any agent that can run shell commands, say "set up the
software factory here", and your agent gets
[Architech](https://docs.mutagent.io/architech/overview) installed, linked to
your board and taking work.

## What you get

- **A plan before any code.** Requirements, design, tasks and an acceptance
  spec. In the Full-Loop, nothing gets built until you approve it.
- **Your board as the queue.** The plan becomes a parent issue with one
  sub-issue per task, on your GitHub Project board.
- **Agents that build the tasks in parallel** and open the pull requests.
- **Review by an agent that didn't write the code.** It sends work back to
  the builder; after two rounds, it comes to you.
- **CI that bounces back.** On the cloud factory, failed CI on its branch
  sends the work back to the builder, not to you.
- **A pull request waiting for one decision: yours.**

Small fix? Skip the ceremony: `/execute "fix the off-by-one in pagination"`
plans, builds, gets the pull request reviewed and merges it as your merge
rules allow. In Fast Mode, the merge is what you approve.

## How it runs, in 60 seconds

Same pipeline, two places to run it:

| | Local factory | Cloud factory |
|---|---|---|
| Runs in | Your own Architech session | Mutagent Cloud sandboxes |
| Work starts when | You type `/dispatch 42` | Someone adds the pickup label to an issue |
| You approve by | Answering the session | Adding a label on the issue or PR |
| Best for | Trying it on one repository | A board that keeps moving with your laptop shut |

On the cloud factory, label an issue before you log off and the plan is
waiting for you in the morning.

1. **Install the skill** ([Quick start](#quick-start)) and say: "Set up the
   software factory here."
2. **Your agent installs Architech.** It asks first and shows you the
   installer. You sign in with `/login`, then `/onboard` links your GitHub
   Project board, writes project memory and rules, and commits two files:
   `factory.yaml` and a one-line pointer in `CLAUDE.md`. That is your local
   factory.
3. **Your agent asks about the cloud.** Stay local, or move the factory to
   Mutagent Cloud: it walks you through `architech factory push` and `enable`
   only after you say yes. Then the board runs itself, up to your approvals.
4. **Hand it work:** ask for the feature or the fix in plain words. Your agent
   starts `/spec`, then `/publish` and `/dispatch`, or `/execute` for a quick
   fix, which goes on to merge as your merge rules allow; on the cloud, it
   puts the work on the board for you to label.

## Quick start

Tested on 2026-11-17 with `unsupervised` v0.1.2 (commit `a612ca5`), from
this public repository, each method in an empty home folder, on macOS (Apple
Silicon) with Claude Code 2.1.312, Codex CLI 0.159.0, skills CLI 1.9.0 and
git 2.50.1. The skill names in each app were checked at its prompt, without
sending a message. Installing the skill on Linux or Windows (WSL) is not
tested yet.

Pick one method. If you install the plugin and also keep a copy in
`~/.claude/skills/unsupervised`, Claude Code loads the plugin and reports the
copy as not loaded.

### 1. Claude Code plugin

In Claude Code:

```text
/plugin marketplace add mutagent-io/unsupervised
/plugin install unsupervised@unsupervised
```

`/plugin install` asks for a scope: "Install for you (user scope)" makes it
available in every project. The skill is active right away. Run it as
`/unsupervised:unsupervised`, or ask about Architech or the software factory.

Or from your shell, with the same result:

```bash
claude plugin marketplace add mutagent-io/unsupervised
claude plugin install unsupervised@unsupervised
claude plugin list   # unsupervised@unsupervised, Version: 0.1.2, enabled
```

The marketplace is this repository. The plugin installs from this
repository's own marketplace and is not listed in Anthropic's official plugin
directory, so a search in `/plugin` Discover won't find it until you add this
marketplace (the first command above). Claude Code clones the marketplace
over SSH and, when that fails, over HTTPS, so you need no GitHub account or
key.

| | Command |
|---|---|
| Update | `claude plugin marketplace update unsupervised`, then `claude plugin update unsupervised@unsupervised`, then restart Claude Code |
| Remove | `claude plugin uninstall unsupervised@unsupervised`, then `claude plugin marketplace remove unsupervised` |

### 2. Git clone

**Claude Code**, for every project (runs as `/unsupervised`):

```bash
git clone https://github.com/mutagent-io/unsupervised ~/.claude/skills/unsupervised
```

For one repository only, run
`git clone https://github.com/mutagent-io/unsupervised .claude/skills/unsupervised`
at its root. Claude Code loads it once you trust that folder.

**Codex**, for every project (type `$unsupervised`; Codex lists it as
"Unsupervised (Architech)"):

```bash
git clone https://github.com/mutagent-io/unsupervised ~/.agents/skills/unsupervised
```

For one repository only, clone it into `.agents/skills/unsupervised` at its
root.

**Any other agent:** clone it into the folder your agent loads skills from,
or anywhere it can read, and see [For agents](#for-agents).

**A pinned release** (git notes that the tag "is not a commit" and that you
are on a detached HEAD; both are expected for a tag):

```bash
git clone --branch v0.1.2 --depth 1 https://github.com/mutagent-io/unsupervised ~/.claude/skills/unsupervised
```

Every [release](https://github.com/mutagent-io/unsupervised/releases) also
attaches `unsupervised-v<version>.tar.gz`, which unpacks to an `unsupervised`
folder:

```bash
mkdir -p ~/.claude/skills
curl -fsSL https://github.com/mutagent-io/unsupervised/releases/download/v0.1.2/unsupervised-v0.1.2.tar.gz | tar -xz -C ~/.claude/skills
```

Use the folder you installed into (`~/.claude/skills/unsupervised` below):

| | Command |
|---|---|
| Update a clone | `git -C ~/.claude/skills/unsupervised pull --ff-only` |
| Move a pinned clone to another release | `git -C ~/.claude/skills/unsupervised fetch --depth 1 origin tag v<version>`, then `git -C ~/.claude/skills/unsupervised checkout v<version>` (`git pull` changes nothing on a pinned clone) |
| Remove | `rm -rf ~/.claude/skills/unsupervised` |

### 3. The skills CLI (any agent)

Needs Node.js for `npx`.

```bash
npx skills add mutagent-io/unsupervised
```

It asks which agents to install to (version 1.9.0 lists 79, some of them
preselected), then the scope, then symlink or copy. The default, project
scope, puts the skill in `.agents/skills/unsupervised` in the current folder,
links it into each chosen agent's folder (for example
`.claude/skills/unsupervised`) and writes `skills-lock.json`.

For every project, for Claude Code and Codex, without questions:

```bash
npx skills add mutagent-io/unsupervised -g -a claude-code codex -y
```

That puts the skill in `~/.agents/skills/unsupervised`, where Codex reads it,
and links `~/.claude/skills/unsupervised` to it, so Claude Code runs it as
`/unsupervised`.

| | Command |
|---|---|
| Update | `npx skills update -g -y` |
| Remove | `npx skills remove unsupervised -g -y` |

### What you need

- **An agent that can read files and run shell commands.** tmux is optional.
- **macOS or Linux** (on Windows, WSL), with `bash`, `curl`, `git`, and
  `shasum` or `sha256sum`.
- **Architech.** You don't install it first: your agent asks, downloads the
  installer with
  `curl -fsSL https://api.mutagent.io/architech/install.sh -o architech-install.sh`,
  shows it to you, and you run `bash architech-install.sh` in your own
  terminal. The installer asks for your email there; from an agent's shell
  it stops with "a terminal is required". See the
  [install docs](https://docs.mutagent.io/architech/install).
- **The GitHub CLI, signed in** (`gh auth status`), for the stages that work
  on GitHub, such as `/publish` and `/ship`.
- **A model provider.** You sign in inside the Architech session with
  `/login`, never in chat.

## When it loads

The skill's description tells your agent to use it when you install, set up
or run Architech or its Software Factory, pick a lifecycle command, or hand
Architech a task, and, in a repository already set up with Architech, for any
build, fix or feature request. It is not for unsupervised machine learning,
building or evaluating LLM agents (Helix), the Agent Factory
(`mutagent factory`) or changing Architech itself.

In a repository that isn't set up with Architech, when you didn't ask for
Architech, it steps aside: your agent says in one line that the repository
isn't set up and offers to onboard it, instead of taking the task over.

## Then say

- "Set up the software factory here."
- "Add a CSV export to the reports page." (in a repository set up with Architech)
- "Plan this feature with Architech."
- "Why didn't the factory pick up my issue?"
- "Hand this bug to Architech and tell me when the PR is up."

## It never merges without you

- **Approvals are yours.** Locally, you answer the session. On the cloud
  factory, an approval is a label only a person can add: labels from bots
  and apps approve nothing. Your agent never adds one, never approves a gate
  for you, and never merges.
- **Every change lands as a pull request.** The merge waits for your approval
  at every autonomy level.
- **It asks before it installs or writes anything**, and shows you the
  installer before it runs.
- **No keys in chat.** You sign in inside Architech with `/login`.

## For agents

**Delegate, never implement.** In a repository set up with Architech, a
request to build, add, fix or change code goes to Architech or its factory:
you write the brief, relay questions, follow the run and report, and you never
edit the project's code yourself unless the user explicitly asks you to. Set
the factory up locally first, and move it to Mutagent Cloud only after the
user says yes.

Running a harness that doesn't load skills natively? Read [SKILL.md](SKILL.md)
and follow its three phases: start (install), setup (sign in, model, onboard,
the local factory, the cloud question) and operate (hand work over, relay
questions, follow runs). Its first section says what your harness needs and
what to do without tmux or without a shell. For the Software Factory, read
the operator's manual, [references/factory.md](references/factory.md).
[AGENTS.md](AGENTS.md) points harnesses that load `AGENTS.md` to the same
place. A user can start you with: "Read github.com/mutagent-io/unsupervised and
set up Architech in this repo."

## Learn more

- Software Factory: https://docs.mutagent.io/factory/overview
- Architech: https://docs.mutagent.io/architech/overview
- Agent Skills format: https://agentskills.io/specification

## Contributing and licence

See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under the [MIT License](LICENSE).
