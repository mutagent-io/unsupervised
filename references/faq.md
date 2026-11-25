# Questions new users ask

Short answers. Each links to the page with the detail.

## Access and cost

**Who can install it?** Anyone on macOS or Linux. Architech is in Early
Access: the installer asks for an email once, and the download service must
accept it. See [install.md](install.md).

**Which models does it use?** The provider you sign in to with `/login`. Pick
the model with `/model`. Model usage is billed by that provider, under your
account. A Cloud Factory run also uses Mutagent sandbox time, billed
separately: https://docs.mutagent.io/factory/costs

## Safety

**Will it merge without me?** Only if you set it to. Who is asked is the
factory's `policy.autonomy` in `factory.yaml`:

| Preset | Waits for you on |
|---|---|
| `calibrating` (the default) | Every plan and every merge |
| `approve-merges` | Every merge and a spec-sized plan (a small plan starts by itself) |
| `approve-plans` | Every plan; a pull request merges by itself once its review says APPROVE or WATCH and CI is green on the exact head |
| `unsupervised` | Only a spec-sized plan (a small plan starts by itself; a pull request merges as under `approve-plans`) |

A repository with no factory file asks before every merge. Even a merge that
runs by itself asks you for a protected path, an advisory review or a change
bigger than its plan, and `merge:hold` stops any merge. Review sends work back
to the builder at most 2 rounds by default, then asks you. `/execute` ends by
merging under the same rules. A finished task is not permission to merge, and
your agent never merges or changes that setting for you. See
[factory.md](factory.md), section 2.

**Does it scan my code without asking?** No. Onboarding asks before it scans
the repository.

**What does it write to my repository?** Onboarding writes project memory,
engineering rules, a record of your intent and setup, and ignore entries, and
shows them before you accept. With or without a board, also
`.architech/factory/factory.yaml` and a short pointer in `CLAUDE.md`, shown as
a diff first and committed together. See [onboard.md](onboard.md).

**Where do my keys go?** You enter them in `/login`, inside the session. Never
in chat, never on a command line.

**Does a headless run merge?** No. A headless brief says "open a pull request,
do not merge", and this skill never runs `/ship` or `/execute` headless (the
runner refuses a prompt that starts with either).

## Using it

**Does it work with my own agent harness?** Yes, if the harness can read files
and run shell commands. tmux and background commands help but are optional; see
section 1 of [SKILL.md](../SKILL.md).

**Do I need a GitHub board?** No. Without one, Architech still works for local
software work. To add one later, ask Architech in the session to run
`architech-onboard tracking --org <owner> --project <number>`. Mutagent Cloud
needs a board: an organisation's GitHub Project. Cloud can't bind a Project a
personal account owns; it accepts the repository's own issues instead, but on
Architech 0.1.67 the CLI can't validate or push that form yet (a fix is
pending in the next release). See [factory.md](factory.md), section 2.

**How does a board issue get picked up on the cloud?** It must be on the
bound board, outside Triage, carry the pickup label (`factory:pickup` by
default, added by a person), and the Factory must be enabled.

**Full-Loop or Fast Mode?** Fast Mode for a contained change, Full-Loop for a
feature worth planning. See [workflows.md](workflows.md).

**Can I steer an agent while it runs?** Yes. In the session you can watch each
sub-agent and type at it. Docs: https://docs.mutagent.io/architech/features/sub-agents

**Can a background Architech ask me things?** In a tmux background session,
yes. In a headless `architech -p` run, no: nobody is there to answer. See
[dispatch.md](dispatch.md).

**Does it read my `CLAUDE.md` or `AGENTS.md`?** Yes, in every mode, nearest
file last, and it passes them to the agents it dispatches.

**Can I use my own MCP servers?** Yes. List them in an `mcp.json` and manage
them with `/mcp` in the session. Docs:
https://docs.mutagent.io/architech/features/mcp

**How do I see what happened in a past session?** `/trace` opens session logs
read-only.

## Architech, Helix and this agent

| Use | For |
|---|---|
| Architech | Changes to your software: plan, build, review, ship |
| Helix | Building and evaluating LLM agents: https://docs.mutagent.io/helix/what-is-helix |
| This coding agent | Operating Architech for you; it edits code itself only when you explicitly ask it to, and says it isn't using Architech |

## Troubleshooting

- Install problems, with the installer's exact messages:
  [install.md, section 7](install.md#7-when-the-install-goes-wrong).
- Headless runs and their verdicts:
  [dispatch.md, section 2](dispatch.md#verdicts).
- Everything else: the symptom table in [SKILL.md](../SKILL.md), section 7.

## Where to read more

- What Architech is: https://docs.mutagent.io/architech/overview
- Install: https://docs.mutagent.io/architech/install
- Onboard: https://docs.mutagent.io/architech/onboard
- Agents: https://docs.mutagent.io/architech/agents
- Commands (plan, build, review, ship, monitor):
  https://docs.mutagent.io/architech/lifecycle-commands
- Software Factory: https://docs.mutagent.io/factory/overview (quickstart:
  https://docs.mutagent.io/factory/quickstart, gates:
  https://docs.mutagent.io/factory/gates, costs:
  https://docs.mutagent.io/factory/costs)
- Features (sub-agents, workflows, monitor, traces, context, MCP):
  https://docs.mutagent.io/architech/features
