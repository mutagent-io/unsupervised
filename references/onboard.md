# First session and /onboard

Source of truth: https://docs.mutagent.io/architech/onboard

## 0. Who does what

Two parts of setup are the user's: signing in (`/login`, their keys) and the
approvals `/onboard` asks for. If you are an agent helping:

- With tmux and a way to ask the user, start a background session (see
  [dispatch.md, section 3](dispatch.md)). The user attaches for `/login` and
  `/model`, and you don't read the pane meanwhile; then you type `/onboard`
  and relay each question.
- Otherwise the user runs `architech` in their own terminal and types the
  commands below; you help them answer.
- Never run `/onboard` headless: it asks before it scans and before it writes,
  and a headless run cannot ask.

## 1. Open the project

```bash
cd your-project
architech
```

Run it in a git repository. The boot screen shows the repository, its setup
state (onboarded or not, context, board) and the lifecycle commands. Everything
starting with `/` from here on is a **session command**, typed inside
Architech, not in the shell.

## 2. Sign in and pick a model

- `/login`: choose a model provider and sign in. A key is entered there, in
  the session, never in chat or on a command line.
- `/model`: pick the model the session uses.

## 3. Run /onboard

Type `/onboard`. Onboarding sets up the project locally and deploys nothing.
The agents and skills ship inside Architech, so it does not copy them into the
project. It asks:

| Question | How to help the user answer |
|---|---|
| New project or existing code? | Say what you see in the repository |
| Use a GitHub Project board, or skip it? | For a first try, recommend skipping. A board can be added later by running `/onboard` again |
| May it scan the repository to draft context and rules? | It never scans without a yes. Scanning gives better drafts; the user can still edit them |

Answer for the user only when they asked you to. Otherwise relay each question
and their answer.

## 4. Review what it proposes

Onboarding writes project memory, engineering rules, a record of the user's
intent and setup, and ignore entries. It never overwrites context the user
wrote, and it shows the proposed context before the user accepts it.

With a board, it also shows a diff for the board setup: a `factory.yaml` file
and one pointer line in `CLAUDE.md`. After approval it commits those two
together and nothing else. The repository list in `factory.yaml` is the scope
of board work, not every repository the organisation owns.

Then read the onboarding report and do the manual steps it lists.

## 5. Session essentials

| Command | What it does |
|---|---|
| `/help` | Lists every command in this release |
| `/status` | Progress of dispatched work |
| `/sync` | Reads the project board |
| `/agents` | The agent roster |
| `/trace` | Opens session logs read-only: list sessions, open one, step through it |
| `/mcp` | The user's own MCP servers: status, sign-in, reconnect |
| `/workflows` | Saved multi-agent scripts in the repository; run one by name |

## 6. After onboarding

- Project instructions live in `AGENTS.md` or `CLAUDE.md`. They load in every
  mode, nearest file last, and reach every agent Architech dispatches.
- To change how agents behave in this project, edit the project's context and
  rules, not the agents.
- Next: [workflows.md](workflows.md) to pick a first piece of work.
