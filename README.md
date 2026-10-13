# GitHub Credential Group Manager

A small, Windows-focused Python CLI for finding GitHub credentials stored by Git Credential Manager (GCM), then identifying entries that contain the same secret. Milestone 1 is strictly read-only.

The report shows GCM credential target names and invocation-local labels such as `group-1`. It never prints token values, token fragments, or persistent token fingerprints.

## Requirements

- Windows 10 or later
- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/)
- GCM configured with the `wincredman` credential store

## Run

```powershell
uv sync
uv run python -m github_credential_groups.cli inventory --backend wincredman
```

Example with synthetic names:

```text
Supported GitHub credentials: 2
Credential groups: 1

group-1 (duplicate, 2 entries)
  - git:https://github.com/example/one
  - git:https://github.com/example/two

Unrecognized GitHub entries: 0
```

Group numbers are rebuilt for every invocation and are not suitable as persistent identifiers. The command enumerates the current user's vault through `CredEnumerateW`; it does not write, update, or delete credentials.

## Tests

```powershell
uv run python -m unittest discover -s tests -v
```

All automated tests use synthetic byte strings. They do not enumerate or modify the user's credential vault.

## Windows integration verification

This verification reads live credential metadata and secret values into this local process so it can compare them. It does not print the secrets or send them anywhere. Run it yourself in an interactive Windows session where GCM's `wincredman` store is available:

1. Run `uv run python -m github_credential_groups.cli inventory --backend wincredman`.
2. Confirm the listed targets correspond to GitHub entries visible in Windows Credential Manager.
3. If you know two repository-specific entries use the same token, confirm they appear in the same temporary group.
4. Confirm no token, token substring, or fingerprint appears in standard output or standard error.
5. Immediately after the inventory command, run `Write-Output $LASTEXITCODE`. Report that numeric exit code and whether each check passed. Do not paste credential values. (`$LASTEXITCODE` is the exit code of the most recent native program, which is `uv` here; `$?` reports only a Boolean success status.)

An empty vault is a successful inventory with zero entries. Malformed or unsupported GitHub-shaped GCM entries are listed under `Unrecognized GitHub entries`; unrelated credentials are ignored. Windows API errors produce a nonzero exit code and a numeric Windows error code.

## Scope

Persistent group configuration, audits, rotation, and DPAPI support are planned milestones. Rotation will not be implemented until live read-only inventory behavior has been verified. See [TASKS.md](TASKS.md) and [docs/gcm-wincredman-research.md](docs/gcm-wincredman-research.md).
