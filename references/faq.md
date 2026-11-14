# Questions new users ask

Short answers. Each links to the page with the detail.

## Access and cost

**Who can install it?** Anyone. The installer asks for an email once; that is
all it asks for. See [install.md](install.md).

**Which models does it use?** The provider you sign in to with `/login`. Pick
the model with `/model`. Model usage is billed by that provider, under your
account.

## Safety

**Will it merge without me?** No. You approve the plan before the build and the
merge before it lands. A finished task is not permission to merge.

**Does it scan my code without asking?** No. Onboarding asks before it scans
the repository.

**What does it write to my repository?** Onboarding writes project memory,
engineering rules, a record of your intent and setup, and ignore entries, and
shows them before you accept. With a board, also a `factory.yaml` and one
pointer line in `CLAUDE.md`, shown as a diff first. See [onboard.md](onboard.md).

**Where do my keys go?** You enter them in `/login`, inside the session. Never
in chat, never on a command line.

**Does a headless run merge?** No. A headless brief says "open a pull request,
do not merge", and this skill never runs `/ship` headless.

## Using it

**Does it work with my own agent harness?** Yes, if the harness can read files
and run shell commands. tmux and background commands help but are optional; see
section 1 of [SKILL.md](../SKILL.md).

**Do I need a GitHub board?** No. Without one, Architech still works for local
software work. You can add a board later by running `/onboard` again.

**Full-Loop or Fast Mode?** Fast Mode for a contained change, Full-Loop for a
feature worth planning. See [workflows.md](workflows.md).

**Can I steer an agent while it runs?** Yes. In the session you can watch each
sub-agent and type at it. Docs: https://docs.mutagent.io/architech/features/sub-agents

**Can a background Architech ask me things?** In a tmux background session,
yes. In a headless `architech -p` run, no: nobody is there to answer. See
[dispatch.md](dispatch.md).

**Does it read my `CLAUDE.md` or `AGENTS.md`?** Yes, in every mode, nearest
file last, and it passes them to the agents it dispatches.

**Can I use my own MCP servers?** Yes, with `/mcp`. Docs:
https://docs.mutagent.io/architech/features/mcp

**How do I see what happened in a past session?** `/trace` opens session logs
read-only.

## Architech, Helix and this agent

| Use | For |
|---|---|
| Architech | Changes to your software: plan, build, review, ship |
| Helix | Building and evaluating LLM agents: https://docs.mutagent.io/helix/what-is-helix |
| This coding agent | Quick local edits you want to make yourself, now |

## Troubleshooting

- Install problems, with the installer's exact messages:
  [install.md, section 7](install.md#7-when-the-install-goes-wrong).
- Headless runs and their verdicts:
  [dispatch.md, section 2](dispatch.md#verdicts).
- Everything else: the symptom table in [SKILL.md](../SKILL.md), section 6.

## Where to read more

- What Architech is: https://docs.mutagent.io/architech/overview
- Install: https://docs.mutagent.io/architech/install
- Onboard: https://docs.mutagent.io/architech/onboard
- Agents and commands: https://docs.mutagent.io/architech/agents
- Features (sub-agents, workflows, monitor, traces, context, MCP):
  https://docs.mutagent.io/architech/features
