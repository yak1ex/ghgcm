# GCM wincredman representation research

Research was performed on 2026-10-11 against Git Credential Manager revision `91d6da2f699d60802cdd5d339ba2b91b38dce549` and the linked Microsoft API documentation.

## Findings used by Milestone 1

- GCM's default credential namespace is `git` (`src/Core/Constants.cs`). Its Windows store creates targets in the form `git:<service URL>`, optionally inserting an escaped account as URI user information when a service already has another account (`src/Core/Interop/Windows/WindowsCredentialManager.cs`).
- With `credential.useHttpPath=true`, GCM documents GitHub examples such as `git:https://github.com/foo/bar`. Without it, the normal target is `git:https://github.com` (GCM [configuration documentation](https://github.com/git-ecosystem/git-credential-manager/blob/main/docs/configuration.md#credentialusehttppath)).
- The wincredman backend uses `CRED_TYPE_GENERIC`, persists secrets as UTF-16LE bytes, and reads through `CredEnumerateW`. Enumeration with `CRED_ENUMERATE_ALL_CREDENTIALS` may expose target names prefixed by `LegacyGeneric:target=`, which GCM strips before matching (`WindowsCredentialManager.cs` and `Advapi32.cs`).
- Microsoft defines `CredEnumerateW` as returning the current logon session's credential set and requires the returned buffer to be freed with `CredFree` ([CredEnumerateW](https://learn.microsoft.com/windows/win32/api/wincred/nf-wincred-credenumeratew), [CREDENTIALW](https://learn.microsoft.com/windows/win32/api/wincred/ns-wincred-credentialw)).
- GCM documents `wincredman` as Windows-only and unavailable over network/SSH sessions. Its `dpapi` store instead writes DPAPI-protected files under `%USERPROFILE%\.gcm\dpapi_store` by default ([credential stores](https://github.com/git-ecosystem/git-credential-manager/blob/main/docs/credstores.md)).

## Implementation consequences

The prototype uses Python's standard-library `ctypes`, enumerates without mutation, copies Generic credential blobs only long enough to classify and group them, and compares exact bytes. It emits per-run ordinal labels rather than hashes, so reports contain no reusable token fingerprint. It recognizes only HTTPS `github.com` targets in GCM's `git` namespace and explicitly reports malformed GitHub-shaped entries.

No third-party runtime dependency is justified for Milestone 1. Rotation remains gated on live integration verification and separate research into GCM's supported mutation interface.

