# Software Factory: board work, locally or on Mutagent Cloud

Sources: https://docs.mutagent.io/factory/overview,
https://docs.mutagent.io/factory/quickstart,
https://docs.mutagent.io/factory/configuration,
https://docs.mutagent.io/factory/triggers,
https://docs.mutagent.io/factory/operating,
https://docs.mutagent.io/factory/cloud,
https://docs.mutagent.io/factory/reference/factory-yaml,
https://docs.mutagent.io/factory/reference/statuses,
https://docs.mutagent.io/factory/reference/cli, and `architech factory --help`.
Commands can change between releases: the live `--help` and the docs win.

## 0. What it is

The Software Factory turns issues on a GitHub Project board into reviewed pull
requests. Each stage is an agent session: an architect **plans**, a developer
**builds**, a different agent **reviews**, and the orchestrator **lands** the
change. The person approves twice: the plan, and the merge.

One committed file, `factory.yaml`, describes the board, the repositories,
the labels, the triggers and the merge policy. Onboarding writes it. Find it
with `git ls-files '*factory.yaml'`. It never holds credentials.

**Its CLI is `architech factory`, not `mutagent factory`.** `mutagent factory`
belongs to the Mutagent CLI and manages the Agent Factory (agentspecs of agents
and skills), a different product. Inside an Architech session, `/factory`
shows Factory state; it is not the shell CLI.

## 1. Local or Cloud: who runs the board work

| | Local (`mode: local`) | Cloud (`mode: cloud`) |
|---|---|---|
| Who runs it | The user's own Architech session, in their repository | Mutagent Cloud, in sandboxes |
| Starts work | The user, in the session: `/sync`, then `/dispatch` or `/execute` | Triggers: a person adds the pickup label to a board item; or `architech factory runs start` |
| Reaches GitHub with | The user's own GitHub sign-in (`gh`) | The Mutagent GitHub App, never a token in the file |
| Models | The session's `/login` and `/model` | The workspace's model providers; local credentials are not copied |
| Approvals | The session asks; the user answers | Labels on the issue or pull request, added by a person |
| Needs | Architech installed and onboarded with a board | All of local, plus a Mutagent sign-in, a model provider, GitHub connected, the file pushed, the Factory enabled |

Start local: onboarding writes `mode: local`, and the user can stay there. A
local file does not turn on Cloud pickup, and a local Factory is not a
self-hosted Cloud. Move to Cloud when the user wants board items picked up
without a session open. Pushing the file to Cloud is what sets `mode: cloud`.
Cloud sandboxes check out repositories without submodule contents.

## 2. Setup: board, repositories and the file

Needs a GitHub repository, a GitHub Project board the user can access, and
Architech installed and signed in (SKILL.md, sections 3 and 4).

1. **Onboard with a board.** In an interactive session, `/onboard` asks which
   GitHub Project board to use: its owner (organisation or user) and project
   number, or skip. Run `/onboard` again later to add a board. The docs say
   skipping writes no `factory.yaml`; Architech 0.1.49's onboarding says it
   always creates a local one. Go by what the live question says it will
   write. Relay the question; the user picks the board.
2. **Review the diff.** Onboarding shows a diff of `factory.yaml` (with
   `mode: local`, the board, repositories, label roles, issue naming and merge
   policy) and one pointer line in `CLAUDE.md`. After approval it commits those
   two together and nothing else. That is a write or commit question: relay it.
3. **Check the file** with the user: repository names and default branches,
   the board's owner and project number, the label names, the merge policy and
   the `context:` block. The repository list is the scope of board work, not
   every repository the organisation owns.
4. **Validate it**, offline: `architech factory validate <path> --json`. This
   checks the file's shape only, not whether Cloud can reach anything.

`architech factory init <path> --board github --repo owner/name` writes the
same format offline, with a comment on every key, without onboarding. Put it
where the configuration docs page says, so push and pull find it.

### What is in `factory.yaml`

| Key | What it sets |
|---|---|
| `mode` | `local` (onboarding) or `cloud` (set by push) |
| `board`, `boards.<name>` | Which board: `provider` (`github` or `linear` on Cloud), `ref` (GitHub: `owner`, `project`), optional `statusMap` (canonical status -> the board's exact column name; map only the columns that exist) |
| `repos[]` | `name` (`owner/repo`), `defaultBranch`, `zones.protected` (path globs that always wait for merge approval) |
| `labels` | Label roles -> the label names on the board (table below) |
| `policy.merge.preset` | Onboarding writes `standard`; the default is `as-ready`. Every preset waits for a person's approve or loosen label |
| `policy.autonomy` | `calibrating` (default), `standard` or `autonomous`: which gates apply |
| `plan.subItems` | `board` (default: each part of the plan becomes a sub-issue with its own pull request) or `none` (one item, one build, one pull request per repository) |
| `limits` | Open runs, sandboxes, dollars and sandbox hours; work over a cap waits |
| `triggers` | What starts work (section 3) |
| `context` | Which repositories inherit, require or don't need rules and memory |

### Labels: what they mean and who adds them

The names below are the defaults; the file's `labels` block holds the real
ones (onboarding writes `merge:approved` for the merge approval). Read them
from the file before naming one to the user.

| Role | Default | Who | What it does |
|---|---|---|---|
| `pickup` | `factory:pickup` | a person | Marks a board item for work; an item needs every pickup label |
| `approvePlan` | `factory:approved` | a person | Approves the waiting plan; build starts |
| `revisePlan` | `factory:changes` | a person | After a comment with notes: plan again |
| `approve` | `merge-ready` | a person | Approves the merge of the reviewed head; removed when new commits arrive |
| `revise` | `merge:changes` | a person | After a comment with notes: build again |
| `hold` | `merge:hold` | a person | Stops pickup and merge; wins over every other label |
| `loosen` | `merge:yolo` | a person | Allows a merge without `approve`; never past `hold` |
| `pr`, `origin` | none, `origin:*` | the Factory | Added to the pull requests and issues it opens |

"A person" is a GitHub user with write access. Labels added by a bot, an app
or the Factory approve nothing. Moving a card does not approve, and a comment
`/approve` with text after it is refused.

**Which gates apply.** Plan approval: before any build at `calibrating` and
`standard` autonomy. Merge approval: at `calibrating`, and at any autonomy for
a change to a protected path. The merge itself always waits for a person's
approve or loosen label, at every autonomy and with every preset.

## 3. Running work

### Local

In an interactive Architech session in the repository:

- `/sync` reads the board.
- Full-Loop: `/spec` (the user approves the plan) -> `/publish` (a parent
  issue and one sub-issue per task, on the board) -> `/dispatch <issue>`
  (agents build in parallel; each pull request is reviewed by an agent that
  did not build it). `/dispatch` never merges.
- Fast Mode: `/execute "<goal>"` plans, opens one issue, builds and has the
  pull request reviewed.
- `/status` follows dispatched work. Landing is `/ship`, the user's, in an
  interactive session (SKILL.md, section 5).

The `architech factory runs ...` commands control Cloud runs, not local work.

### Cloud

The user does these, or you run them after they say yes: each one signs in,
connects, commits or turns something on. Pass `--json` to every call.

1. `architech factory login --json`: the sign-in URL arrives on stderr; show
   it to the user word for word and wait while they approve it in a browser.
2. `architech factory status --json`: integrations, factories, setup progress.
3. The user adds a model provider to the workspace (docs:
   https://docs.mutagent.io/helix/cloud/setup).
4. `architech factory integrations connect github --wait --json`: the user
   opens the consent URL and gives the GitHub App access to the repositories.
5. `architech factory push --dry-run --json`, then `architech factory push --json`:
   sends the file, sets `mode: cloud` and commits it. Check `committed` and
   the notices. Push reports `linked`, `board` and `drift`; it links nothing.
6. If push says the board is not bound: `architech factory board bind <factory-id> --json`.
7. `architech factory enable <factory-id> --json`: triggers start work now.

The Factory ID is `metadata.name`; use the IDs the commands return.

**What starts a Cloud run.** With no `triggers` key in the file, a pickup label
starts `plan`, and failed CI on a `factory/*` branch sends that run back to
`build`. Whatever the trigger, a board item needs every pickup label, no hold
label, and a column other than `triage`. Assigning an item starts nothing.
`architech factory runs start "<request>" --repo owner/name --factory <id> --json`
starts a run without a board item. A trigger starts work; it never approves a
gate.

**Routines** are `schedule` triggers in the file: at a cron time one agent
session runs one command (`/arch-review` or `/triage`) once, with no run and
no gate. `architech factory triggers fire <name> --json` runs one now;
`triggers list --factory <id>` and `triggers test <trigger-id> --event-file <file>`
check what an event would start.

## 4. Following runs and answering gates

| To see | Local | Cloud |
|---|---|---|
| Progress | `/status` | `architech factory runs list --factory <id> --json`, `runs show <run-id> --json` |
| A run's stages, pull requests, pending gate | `/status`, the board | `architech factory runs logs <run-id> --follow --json` |
| Open questions | The session shows them | `architech factory escalations list --json` |
| Spend | | `architech factory cost --run <run-id> --json` |

Board statuses (`awaiting_approval`, `in_progress`, ...), run states
(`AWAITING_APPROVAL`, `BUILDING`, ...) and gate names (`plan`, `pr`) are three
different things; don't pass one where another is expected.

**A gate is the user's.** When a run waits for plan or merge approval, tell the
user which run, which gate, and where to read it (the plan on the issue, or the
pull request and the reviewer's notes). Name the label from the file that
approves it and the one that asks for changes (after a comment). The user adds
it in GitHub, or runs `architech factory runs approve <run-id> --gate <plan|pr>`
in their own terminal. Then check `runs show` again.

**A question (escalation) is relayed.** Quote it to the user word for word,
with its run and stage. If they want you to send their answer, send their
words unchanged: `architech factory escalations answer <id> "<their answer>" --json`.
Retrying the run does not answer it.

**Reading `--json` output.** Each call prints one `{ok, data, next}` object.
On `ok: false`, read `error.code`, `error.reason` and `error.fix`. `next` only
suggests commands: check each one against section 5 before you run it. Exit
codes: `0` success, `1` failure, `2` API key refused, `3` not signed in or no
workspace.

## 5. Safety

- **Never add or remove a person's label**, by any route (the GitHub web UI,
  `gh`, the API): `factory:pickup`, `factory:approved`, `factory:changes`,
  `merge-ready`, `merge:changes`, `merge:hold`, `merge:yolo`, or the names the
  file gives those roles. A label added from the user's account counts as the
  user's own decision, so adding one for them forges their approval, even
  when they ask in passing. Say which label to add, where, and let them add it.
- **Never approve or reject a gate yourself.** `runs approve` and
  `runs approve --reject` are the user's to run.
- **Never merge.** No `gh pr merge`, no `/ship` headless, no `merge:yolo`.
  The Factory lands a change only after a person's label; `/ship` is the
  user's, in an interactive session.
- **Pull requests only.** Work reaches the default branch through a pull
  request; never push to it.
- **`--force` needs a yes first.** Cancel, delete, disconnect and unbind stop
  sandboxes, triggers or a board. Ask the user, saying what will stop, before
  you pass `--force`. Never skip a gate or cancel a run to unblock it.
- **Ask before you change shared state:** push, pull, enable, disable, board
  bind, `triggers create`, `runs start`. Each one commits, starts or stops work.
- **Relay** every plan, merge, write or commit, or destructive question word
  for word, with its options. An earlier "set it up" or "ship it" is not an
  answer to the question asked now.
- **No secrets on a command line.** A Mutagent API key goes in with
  `architech factory login --api-key-stdin`, typed by the user; never in chat,
  never in `factory.yaml`.

## 6. Common failures and where to look

| Symptom | Look at / do |
|---|---|
| No `factory.yaml`, or one with no board | The board was skipped; run `/onboard` again and pick one |
| `validate` passes, Cloud setup fails | Validation is offline and checks shape only: run `architech factory status --json` |
| Work pauses with `NO_PROVIDER_CONFIGURED` | Add a model provider to the workspace; local sign-ins don't reach Cloud |
| Push can't link a repository | Its name in `repos`, and the GitHub App's access; push grants no permissions |
| Board not bound | `architech factory board bind <factory-id> --json`, after checking the GitHub connection and the board's owner and project number |
| A mapped column is missing | Fix its exact spelling, or remove the mapping |
| A board item is not picked up | Is the Factory enabled? Does the item have every pickup label, no hold label, and a column other than `triage`? Open runs over `limits.maxActiveRuns` wait in a queue |
| A run seems stuck | `runs show` names the pending gate or open question; a label added by a bot doesn't count, and `merge-ready` drops on a new commit |
| Push refuses: Cloud changed since the last sync | `architech factory pull --dry-run --json`, reconcile with the user, push again |
| A warning `factory.yaml is now behind` | A command changed Cloud in a way the file can't hold; read the operating docs before you push |
| Push succeeded but the file is uncommitted | Detached HEAD or a failed commit: check `committed` and the notices |
| Exit code `3` | Not signed in or no workspace: `architech factory login --json` |
| Local work doesn't show on the board | `/sync`; `/dispatch --no-status-update` doesn't move items |

More detail for a run: `architech factory runs show <run-id> --json`, its
logs, `escalations list`, and `cost`. In a local session: `/status`, and
`/trace` for the session logs.

Starting work from a Slack mention is a different path: a Mutagent CLI gateway
trigger (`mutagent gateway triggers create --on slack.mention ...`) runs one
session, not a Factory run. See https://docs.mutagent.io/factory/triggers.
