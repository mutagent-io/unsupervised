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
- Never run `/onboard` headless: it asks before it scans and before it writes.
  A headless run cannot ask, so it stops at "confirmation pending" and sets
  nothing up.

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
| New project or existing code? (asked only when the folder is not empty) | Say what you see in the repository |
| Connect a GitHub Project board (owner and project number), or leave it out? | A local factory file is created either way. The same question asks to approve the local writes, one commit of the factory file and its pointer (no push), and creating missing labels on GitHub: a write or commit question, so relay it. For a first try, recommend leaving the board out. A Project owned by a personal account works locally, but Mutagent Cloud can't bind it. The cloud alternative, the repository's issues, can't be pushed from the CLI yet on 0.1.67 ([factory.md](factory.md), section 2); for the cloud, use an organisation's Project |
| May it scan the repository to draft context and rules? (existing code only) | It never scans without a yes. Scanning gives better drafts; the user can still edit them |

To connect a board later, a bare `/onboard` doesn't ask again (the board
step counts as done). Ask Architech in the session to run
`architech-onboard tracking --org <owner> --project <number>`; onboarding
prints this as its board re-entry.

Relay every question to the user word for word, with its options, and type
their answer. Plan, merge, write or commit, or destructive questions are always
the user's, and a choice of how to land or merge a change counts as a merge
question. An earlier request ("set it up") is not an answer to the question
asked now. Answer one yourself only when the user's earlier words already give
that exact answer and it is none of those kinds, and say so (SKILL.md,
section 5).

## 4. Review what it proposes

Onboarding writes project memory (`.memory/`), engineering rules
(`.engineeringrules/`), a record of the user's intent and setup
(`.architech/onboarding/context.md`), ignore entries and a report. It never
overwrites context the user wrote, and it shows the proposed context before
the user accepts it.

With or without a board, it also shows a diff for the factory setup:
`.architech/factory/factory.yaml` (`mode: local`; the board, or
`provider: none`) and a short pointer block in `CLAUDE.md` (a new `CLAUDE.md`
holding only the pointer if there is none). After approval it commits those
two together and nothing else, and pushes nothing. The repository list in
`factory.yaml` is the scope of board work, not every repository the
organisation owns. What the file holds, and how board work then runs:
[factory.md](factory.md).

Onboarding's board question includes approving that commit and creating
labels on GitHub: that is a write or commit question. Relay it, even when the
user asked you to set Architech up.

Then read the onboarding report (`ONBOARDING-REPORT.md`), do the manual
steps it lists, and act on each yellow line. Labels: onboarding only checks
them. With the user's yes, ask Architech to run `architech-onboard labels
--apply` to create the missing ones; the factory needs them.

## 5. Session essentials

| Command | What it does |
|---|---|
| `/help` | Lists every command in this release |
| `/status` | Progress of dispatched work |
| `/sync` | Reads the project board |
| `/agents` | The agent roster |
| `/trace` | Opens session logs read-only: list sessions, open one, step through it |
| `/mcp` | The user's own MCP servers: status, sign-in, reconnect, enable or disable |
| `/workflows` | Lists the multi-agent scripts saved in `.architech/workflows/`; `/workflows <name>` shows one, it doesn't run it. To run one, ask for it in plain words ("run the review-changed workflow on src/a.ts") |

## 6. After onboarding

- Project instructions live in `AGENTS.md` or `CLAUDE.md`. They load in every
  mode, nearest file last, and reach every agent Architech dispatches. In one
  directory only one loads, and `AGENTS.md` wins over `CLAUDE.md`.
- To change how agents behave in this project, edit the project's context and
  rules, not the agents.
- Onboarding set up the local factory (`mode: local`), with or without a
  board. Next, ask the user whether to move it to Mutagent Cloud, and never
  move it without a yes: [factory.md](factory.md), section 4. The cloud needs
  a board: an organisation's GitHub Project (the repository's issues, for a
  personal account, can't be pushed from the CLI yet on 0.1.67).
- Next: [workflows.md](workflows.md) to pick a first piece of work, which
  Architech builds; you hand it over, you don't write it.
