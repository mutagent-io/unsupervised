# Install, update, remove

Source of truth: https://docs.mutagent.io/architech/install. If this page and the
docs disagree, follow the docs.

## 1. Before you start

- macOS, or Linux (glibc), on arm64 (Apple Silicon) or x64. Windows is not
  supported; WSL (Linux) may work but is untested.
- A normal user account: the installer refuses to run as root.
- `bash`, `curl`, and `shasum` or `sha256sum`. `git` for real work.
- An email address. Architech is in Early Access: the installer asks for the
  email once, the download service must accept it, and it is saved once
  accepted.
- At least 1 GiB of free disk space.
- Access to a model provider. Sign-in happens later, inside the session
  (`/login`, then `/model`).

If your harness cannot run shell commands, give the user each command on this
page and ask them to paste back what it prints.

## 2. Check what is already there

```bash
architech --version
```

- Prints a version: Architech is installed. Run `architech update --check`;
  if it reports `update available`, run `architech update` (with the user's
  yes). Then go to [onboard.md](onboard.md).
- `command not found`: it may be installed but not on `PATH` (see section 7),
  or not installed. Continue with section 3.

## 3. Ask, then download and show the installer

Ask first, in plain words:

> Architech isn't installed. I can download the installer so you can read it,
> then you run it in your own terminal. OK?

After a yes, download it to a file. Never pipe it straight into a shell.

```bash
curl -fsSL https://api.mutagent.io/architech/install.sh -o architech-install.sh
```

Show the user the top of the script and offer the whole file. Point out what it
does: asks for an email, downloads the binary for this machine, checks its
checksum, prints where it installed the `architech` command, and moves an
older plain `architech` binary aside (uninstall restores it).

## 4. The user runs it in their own terminal

The installer reads the email from the terminal. An agent harness's shell has
no terminal, so the installer stops with "a terminal is required" unless an
accepted email is already saved. Hand the user
this command, exactly:

```bash
bash architech-install.sh
```

What they will see:

1. An email prompt (once; saved after it is accepted).
2. The download and its checksum check.
3. The path of the installed `architech` command.

It does not change `PATH` or shell profiles. Wait for the user to say it
finished. Do not poll or type into their terminal.

## 5. Verify

```bash
architech --version
architech doctor --strict
```

Quote both outputs to the user. `doctor --strict` lists what it checked and
fails on anything that would stop a session.

Not on `PATH` yet: use the full path the installer printed, or ask the user
whether to add that directory to `PATH` in their shell profile. Their profile is
their file: ask before you edit it.

## 6. Specific version, update, remove

| Task | Command |
|---|---|
| Install a specific release | `bash architech-install.sh --version <version>` |
| Is there a newer release? | `architech update --check` |
| Update | `architech update` |
| Remove Architech (keeps the saved email, sessions and runtime caches) | `bash architech-install.sh uninstall` |
| Remove Architech and the saved email | `bash architech-install.sh uninstall --reset` |
| Forget the saved email, enter a new one and reinstall (in the user's terminal) | `bash architech-install.sh --reset` |

`update --check` prints one of two lines (checked on 0.1.66):

```text
architech 0.1.66 is up to date (channel: latest, tag: architech-v0.1.66).
update available: <new> (tag architech-v<new>) — installed: <current> (channel: latest).
```

## 7. When the install goes wrong

| Symptom | Cause | Do this |
|---|---|---|
| `architech: a terminal is required: rerun interactively ...` | The installer ran from an agent's shell | The user runs `bash architech-install.sh` in their own terminal |
| `architech: Email must look like name@example.com; try again` | It does not look like an email | Retype it in that form; after 3 bad tries it exits: rerun `bash architech-install.sh` |
| `architech: Email not accepted; try again` | The download service did not take that address | Check the spelling and type it again |
| `architech: Email not accepted (waitlist). Rerun the installer to enter it again (or rerun with --reset; ...)` | The address was refused on every try, or a saved one is refused now (a refused saved address is removed) | Check the spelling and rerun `bash architech-install.sh`; to use a different address, `bash architech-install.sh --reset` |
| `architech: checksum ... mismatch` (any variant) | A broken or tampered download | Download again. Never bypass the check |
| `architech: unsupported platform` or `unsupported architecture` | Windows, or an unusual CPU | macOS or Linux on arm64/x64 |
| `architech: installing as root is unsupported` | Ran as root (common in containers) | Create and use a normal user account, then rerun |
| `architech: refusing unknown command collision` | A different `architech` file is already on `PATH` | Show the user `command -v -a architech`; they decide whether to remove it |
| `architech: refusing ambiguous command placements` | Two `architech` entries on `PATH` | Show the user `command -v -a architech`; they decide which to remove |
| `architech: distribution is busy; wait a minute and rerun` | Rate limit | Wait a minute, rerun |
| `architech: distribution unreachable; check your network and rerun` | No network, or a sandbox blocks it | Check the network, rerun |
| `architech: insufficient disk space` | Less than 1 GiB free | Free space, rerun |
| `command not found: architech` (zsh) / `architech: command not found` (bash) | The install directory is not on `PATH` | Use the printed full path, or add the directory to `PATH` |
| `doctor --strict` fails | Something the session needs is missing | Quote the failing line to the user; it names the fix |
