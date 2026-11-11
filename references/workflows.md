# Which command, which flow

Sources: the boot screen of a session; https://docs.mutagent.io/architech/agents

## 1. Plain words first

Describing the goal in plain language works. The session (the orchestrator)
reads the project and picks the route. The commands below are shortcuts for
when the user already knows the route.

## 2. Full-Loop: /spec -> /publish -> /dispatch -> /review -> /ship

For a feature worth planning: several files or repositories, or a team that
tracks work on a GitHub board.

| Step | What happens | Who decides |
|---|---|---|
| `/spec` | Requirements -> design -> tasks | **The user approves the plan** and its acceptance criteria |
| `/publish` | The approved tasks become GitHub issues (a parent and sub-issues) | |
| `/dispatch <issue>` | The tasks go to agents in parallel; each becomes a pull request | |
| `/review <issue or PR>` | A different agent reviews; work goes back to build until it passes | |
| `/ship <PR>` | Review + CI + merge + watch, under the project's merge rules | **The user allows the merge** |

## 3. Fast Mode: /execute -> /review -> /ship

For a contained change, no board needed. `/execute` plans and acts in one pass.

```text
/execute "Fix the off-by-one in pagination and add a test"
/execute "Rename the config flag verbose to debug across the CLI"
/execute "Add a health-check endpoint that returns the build version"
```

Then `/review` the result and `/ship` it when the user is happy.

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
