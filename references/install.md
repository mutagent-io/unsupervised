# Install, update, remove

Source of truth: https://docs.mutagent.io/architech/install. If this page and the
docs disagree, follow the docs.

## 1. Before you start

- macOS or Linux, on arm64 (Apple Silicon) or x64. Windows: use WSL.
- `bash`, `curl`, and `shasum` or `sha256sum`. `git` for real work.
- An email address. Anyone can install; the installer asks for the email once
  and saves it once it is accepted.
- Access to a model provider. Sign-in happens later, inside the session.

## 2. Check what is already there

```bash
architech --version
```

- Prints a version: Architech is installed. Run `architech update --check` and
  go to [onboard.md](onboard.md) if it is current.
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
checksum, and prints where it installed the `architech` command.

## 4. The user runs it in their own terminal

The installer reads the email from the terminal. An agent's shell tool has no
terminal, so the installer stops with "a terminal is required". Hand the user
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
| Remove Architech | `bash architech-install.sh uninstall` |
| Forget the saved email and enter a new one | `bash architech-install.sh --reset` |

`update --check` prints the installed version and whether it is current, for
example `architech 0.1.46 is up to date`.

## 7. When the install goes wrong

| Symptom | Cause | Do this |
|---|---|---|
| "a terminal is required" | The installer ran from an agent's shell | The user runs `bash architech-install.sh` in their own terminal |
| The email is rejected | It does not look like an email | Check it reads like `name@example.com` and run again |
| The saved email is refused later | An old or mistyped address | `bash architech-install.sh --reset`, then enter a new one |
| Checksum mismatch | A broken or tampered download | Download again. Never bypass the check |
| Unsupported platform | Windows, or an unusual CPU | Use WSL on Windows; otherwise macOS or Linux on arm64/x64 |
| `architech: command not found` | The install directory is not on `PATH` | Use the printed full path, or add the directory to `PATH` |
| `doctor --strict` fails | Something the session needs is missing | Quote the failing line to the user; it names the fix |
