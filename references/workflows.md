# Which command, which flow

Sources: the boot screen of a session; https://docs.mutagent.io/architech/agents;
https://docs.mutagent.io/architech/lifecycle-commands

## 0. Who does the work

**Delegate, never implement.** The commands below are what you start in an
Architech session (or, on a cloud factory, what its runs do); the code itself
is written by Architech's agents. You never edit the project's files
yourself, unless the user explicitly asks you to, and then you say you are
not using Architech. Where the work runs: a local session first; a cloud
factory only after the user chose it ([factory.md](factory.md)).

## 1. Plain words first

Describing the goal in plain language works. The session (the orchestrator)
reads the project and picks the route. The commands below are shortcuts for
when the user already knows the route.

## 2. Full-Loop: /spec -> /publish -> /dispatch -> /review -> /ship

For a feature worth planning: several files or repositories, or a team that
tracks work on a GitHub board.

| Step | What happens | Who decides |
|---|---|---|
| `/spec` | Requirements -> design -> tasks | **The user approves the plan** and its acceptance criteria (unless the factory sets `policy.plan.approve: never`) |
| `/publish` | The approved tasks become GitHub issues (a parent and sub-issues) | |
| `/dispatch <issue>` | The tasks go to agents in parallel. Independent fixes get one pull request each; a planned feature is built in waves on one branch, with one pull request per repository. Nothing merges yet | |
| `/review <issue or PR>` | A different agent reviews it; findings go back to the builder, up to the factory's review-loop limit (2 by default) | |
| `/ship <PR>` | Review + CI + merge + watch, under the project's merge rules | **The user allows the merge**, unless the factory's preset (`approve-plans`, `unsupervised`) lets `/ship` merge on a passing review and green CI |

## 3. Fast Mode: /execute -> /review -> /ship

For a contained change, no board needed. `/execute` plans and builds in one
pass, has the pull request reviewed, then merges it as the merge rules allow
and starts `/monitor` (not with `--local`). What the user approves depends on
the factory's `policy.autonomy`: with no factory file, the merge; under
`calibrating` (the default once `factory.yaml` exists), the plan and the
merge; under `approve-merges`, the merge and a spec-sized plan (a
spec-classed request goes through `/spec`'s sign-offs); under
`approve-plans`, the plan, and a merge only on an exception (an uncovered
protected file, an advisory review, a change bigger than its plan, facts it
could not read); under `unsupervised`, a spec-sized plan and a merge only on
an exception. Say which before you start it,
and relay every question it asks. `--interactive` pauses after the plan;
`--dry-run` writes the plan only.

```text
/execute "Fix the off-by-one in pagination and add a test"
/execute "Rename the config flag verbose to debug across the CLI"
/execute "Add a health-check endpoint that returns the build version"
```

`/review` asks for another review; `/ship` lands a pull request `/execute` has
not merged.

## 4. After shipping

- `/monitor`: CI/CD, deploy health, production.
- `/status`: progress of dispatched work.

## 5. Choosing a route

| Situation | Route | First command |
|---|---|---|
| A bug with a clear fix | Fast Mode | `/execute "<the fix>"` |
| A small feature in one place | Fast Mode | `/execute "<the feature>"` |
| A feature across files or repositories | Full-Loop | `/spec` |
| The team plans on a GitHub board | Full-Loop | `/spec`, then `/publish` |
| Someone else's pull request needs a review | Review only | `/review <PR>` |
| Is the last deploy healthy? | Monitor | `/monitor` |
| "Just help me understand this codebase" | No command | Ask in plain words |

## 6. The agents behind the commands

Architech ships four system agents:

| Agent | Role |
|---|---|
| Orchestrator | The session itself: reads the project, hands work out, brings results back, lands the change once approvals are in |
| Architect | Plans: requirements, design, tasks |
| Developer | Builds and tests the change |
| LLM-Whisperer | Prompt and agent work inside a change |

Review is always done by a separate agent that did not write the change, so no
agent approves its own work.

Details: https://docs.mutagent.io/architech/agents and
https://docs.mutagent.io/architech/features/framework-agents
