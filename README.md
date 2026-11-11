<p align="center">
  <img src="assets/icon.png" alt="Mutagent" width="96" height="96">
</p>

# unsupervised

**Let a team of agents plan, build, review and ship your code change. You
approve the plan and the merge.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-spec-black.svg)](https://agentskills.io/specification)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-black.svg)](https://code.claude.com/docs/en/plugins)
[![Codex skill](https://img.shields.io/badge/Codex-skill-black.svg)](https://developers.openai.com/codex/skills)

`unsupervised` is an [Agent Skill](https://agentskills.io) for Claude Code and
Codex. It gets [Architech](https://docs.mutagent.io/architech/overview),
Mutagent's software-engineering harness, installed and running in your
repository, then lets your coding agent hand work to it.

## What it does

- **Installs Architech** with the public installer, after asking you and
  showing you the script.
- **Walks you through sign-in and `/onboard`**, and picks Full-Loop or Fast
  Mode for your change.
- **Lets Claude Code or Codex hand work to Architech**: headless, or in a
  background session that can still ask you questions.

## Install the skill

**Claude Code (plugin):**

```text
/plugin marketplace add mutagent-io/unsupervised
/plugin install unsupervised@unsupervised
```

It loads when you ask about Architech, or run it as `/unsupervised:unsupervised`.

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

Or clone it into a repository's `.agents/skills/` to use it in that repository only.

**Pinned:** every release on the
[releases page](https://github.com/mutagent-io/unsupervised/releases) attaches
`unsupervised-v<version>.tar.gz`, which unpacks to an `unsupervised/` skill
folder: copy it into `~/.claude/skills/` or `~/.agents/skills/`.

## Then say

- "Set up Architech in this repo."
- "Plan this feature with Architech."
- "Hand this bug to Architech and tell me when the PR is up."

## What is inside

```text
SKILL.md                    the skill: rules, quick start, commands, the two hand-over modes
references/
  install.md                install, verify, update, remove, install problems
  onboard.md                first session, sign-in, /onboard and what it writes
  workflows.md              Full-Loop vs Fast Mode, which command when
  dispatch.md               hand work over: headless or a background tmux session
  faq.md                    questions new users ask
assets/
  brief-template.md         the hand-over brief for a headless run
  icon.png                  the Mutagent mark
scripts/
  run-headless.sh           one headless run: stdin closed, time capped, result graded
agents/openai.yaml          Codex display metadata
evals/triggers.json         prompts that should, and should not, load the skill
.claude-plugin/             Claude Code plugin and marketplace manifests
.github/                    checks that run on every pull request
```

## Safety

- It **asks before** it installs anything or writes to your repository.
- It **never merges for you**: you approve the plan and the merge.
- It **never asks for keys in chat**: you sign in inside Architech with `/login`.
- **Headless runs open pull requests only**; they never run `/ship`.

## Learn more

- Architech docs: https://docs.mutagent.io/architech/overview
- Agent Skills format: https://agentskills.io/specification

## Contributing and licence

See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under the [MIT License](LICENSE).
