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

1. **Install the skill** (below) and say: "Set up the software factory here."
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

## Install the skill

**Claude Code (plugin):**

```text
/plugin marketplace add mutagent-io/unsupervised
/plugin install unsupervised@unsupervised
```

It loads when you ask about Architech or the software factory, or run it as
`/unsupervised:unsupervised`.

**Any agent, with the skills CLI:**

```bash
npx skills add mutagent-io/unsupervised
```

**Claude Code, by hand** (runs as `/unsupervised`):

```bash
git clone https://github.com/mutagent-io/unsupervised ~/.claude/skills/unsupervised
```

**Codex, by hand:**

```bash
git clone https://github.com/mutagent-io/unsupervised ~/.agents/skills/unsupervised
```

Or clone it into a repository's `.agents/skills/` to use it there only. Any
other harness: clone it anywhere it can read, and see [For agents](#for-agents).
Pinned versions: every [release](https://github.com/mutagent-io/unsupervised/releases)
attaches `unsupervised-v<version>.tar.gz`.

## Then say

- "Set up the software factory here."
- "Add a CSV export to the reports page." (in a repository set up with Architech)
- "Plan this feature with Architech."
- "Why didn't the factory pick up my issue?"
- "Hand this bug to Architech and tell me when the PR is up."

## It never merges without you

- **Approvals are labels only a person can add.** The factory ignores labels
  from bots and apps. Your agent never adds one, never approves a gate for
  you, and never merges.
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
