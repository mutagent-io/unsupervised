# Contributing

Thanks for helping. This repository is one skill, and **the repository root is
the skill folder**: whatever is here is copied to every user who installs it.
Keep it small, and treat every file as public.

## Rules

- **Public content only.** No machine paths, private repository names,
  internal tool names, environment variables, keys or tokens.
- **Every command the skill names must be public:** on the Architech boot
  screen or on https://docs.mutagent.io/architech. When the product and the
  skill disagree, the product wins; fix the skill.
- **No `CLAUDE.md` in this repository.** The root is the installed skill
  folder, and a `CLAUDE.md` here could load into users' sessions. Maintainer
  notes belong in this file.
- **No `allowed-tools` in `SKILL.md`.** A public skill does not pre-approve its
  own shell commands.
- Keep `SKILL.md` under 500 lines and the `description` under 1024 characters,
  starting with "Architech". References stay one level deep.

## Layout

| Path | What to edit |
|---|---|
| `SKILL.md` | The skill: rules, quick start, commands, the two hand-over modes |
| `references/*.md` | One page per user journey |
| `assets/brief-template.md` | The headless hand-over brief |
| `scripts/run-headless.sh` | The headless runner (bash only) |
| `evals/triggers.json` | Prompts that should and should not load the skill |
| `.claude-plugin/` | Plugin and marketplace manifests |
| `.github/` | CI and the check scripts |

## Run the checks

CI runs all of these on every pull request. Run them locally first:

```bash
python3 .github/scripts/check_skill.py        # structure, limits, versions, icon, trigger list
python3 .github/scripts/sanitize.py --check   # no machine paths, personal emails or secrets
python3 .github/scripts/sanitize.py --check --git   # the same, in commit authors and messages
bash .github/scripts/test-sanitize.sh         # the sanitizer's own tests
bash .github/scripts/test-run-headless.sh     # the runner, against a fake architech
bash .github/scripts/test-build-release.sh    # the release tarball and notes, dry run
shellcheck scripts/*.sh .github/scripts/*.sh
claude plugin validate .                      # Claude Code manifests
skills-ref validate "$PWD"                    # Agent Skills spec; needs a checkout folder named `unsupervised`
```

`skills-ref` installs with
`pip install "git+https://github.com/agentskills/agentskills.git@38a2ff82958afee88dadf4831509e6f7e9d8ef4e#subdirectory=skills-ref"`.
It requires the folder name to match the skill name, so validate from a clone
named `unsupervised`, and pass the path (`.` reads as an empty name).

When you change the description or the trigger list, also run the trigger eval
in Claude Code (one short session per prompt, using your own sign-in):

```bash
python3 .github/scripts/trigger_eval.py
```

It passes when at least 9 in 10 `should_trigger` prompts load the skill and at
most 1 in 10 near misses do.

## Versions and releases

Bump these together, in one pull request:

1. `metadata.skill_version` in `SKILL.md`
2. `version` in `.claude-plugin/plugin.json`
3. the plugin's `version` in `.claude-plugin/marketplace.json`
4. a new top entry in `CHANGELOG.md`

`check_skill.py` fails if they differ. When a merge to `main` changes the
version, the Release workflow tags `v<version>` and publishes the release with
the skill tarball in the same job (a tag pushed by a workflow does not start
other workflows). To publish or re-upload an existing tag, run the Release
workflow by hand with that tag.

When you re-check the skill against a new Architech release, update
`metadata.architech_checked`.
