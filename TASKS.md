# TASKS.md

## Project objective

Build a Windows-focused Python CLI, managed with uv, that safely inventories and groups GitHub credentials stored by Git Credential Manager, then adds explicit audited rotation and DPAPI support in later verified milestones.

## Scope and constraints

- In scope: wincredman inventory, duplicate-secret grouping, safe output, synthetic tests, persistent group design, audited rotation after verification, and explicit DPAPI backend support.
- Out of scope: automatic backend migration, non-Windows credential stores, secret-bearing reports, and live credential modification without explicit authorization.
- Deployment target: Local Windows 10+ interactive sessions with Python 3.11+ and GCM.
- Important constraints: Standard library preferred; dependencies require approval; live secrets never leave the local process; rotation is gated on T006; no commits or pushes without authorization.

## Current status

The project scaffold and read-only Milestone 1 inventory is verified with standard-library Windows API bindings, synthetic unit tests, and user-run checks on three Windows hosts. Live enumeration, target recognition, exact-secret grouping, secret-safe output, and successful exit status are confirmed. Persistent group configuration and drift auditing are implemented and synthetically verified.

## Current plan

1. `T008` — Validate a supported GCM mutation path, then design and implement authorized safe rotation.
2. `T009` — Investigate and implement an explicit DPAPI backend adapter.

- Selection basis: Persistent intended-group configuration and audit are complete; rotation research is next.
- Last reviewed: 2026-10-13

## Active work

- Task: `T008`
- Current step: Research and validate a GCM-supported mutation path before designing rotation behavior.
- Waiting on: none
- Required action: None.

## Tasks

### T001 — Project scaffolding and template instantiation

- Status: completed
- Objective: Create a buildable Python/uv project with self-contained operating and task instructions.
- Scope:
  - Instantiate the requested base templates and Python/uv appendix.
  - Add package layout, documentation, ignore rules, and provenance.
- Acceptance criteria:
  - No template placeholders remain; uv can sync and execute the CLI.
- Implemented:
  - Added `pyproject.toml`, `.python-version`, package layout, README, `.gitignore`, `AGENTS.md`, `TASKS.md`, and `.agentic-template.yml`.
- Verification:
  - `uv sync`, placeholder scan, and CLI help smoke test passed on 2026-10-11.
- Remaining:
  - None.
- Notes:
  - Template release 2026-09-27 at revision `b68d62c7a62bf7428144fb64f76700f403c7e26b` was adopted.

### T002 — Research GCM wincredman credential representation

- Status: completed
- Objective: Establish source-backed target naming, credential type, and blob encoding rules.
- Scope:
  - Inspect current GCM documentation and source plus Microsoft Credential API documentation.
- Acceptance criteria:
  - Findings and implementation consequences are documented with source links and revisions.
- Implemented:
  - Documented namespace, target forms, legacy prefix, Generic type, UTF-16LE encoding, API ownership, and store limitations in `docs/gcm-wincredman-research.md`.
- Verification:
  - Cross-checked against GCM revision `91d6da2f699d60802cdd5d339ba2b91b38dce549` on 2026-10-11.
- Remaining:
  - None for Milestone 1; mutation behavior belongs to T008.
- Notes:
  - GCM uses the `git` namespace and documents path-specific GitHub targets when `credential.useHttpPath=true`.

### T003 — Implement read-only Windows credential enumeration

- Status: completed
- Objective: Enumerate the current user's credential vault without any mutation API.
- Scope:
  - Bind `CredEnumerateW` and `CredFree` using `ctypes`.
  - Handle empty vaults, platform mismatch, and Windows errors.
- Acceptance criteria:
  - Synthetic tests cover platform-safe behavior and the implementation exposes no write/delete binding.
- Implemented:
  - Added read-only Windows API adapter and explicit `wincredman` backend CLI selection.
- Verification:
  - Unit suite and source compilation passed on 2026-10-11.
- Remaining:
  - Live behavior is tracked by T006.
- Notes:
  - No live inventory command was run by the agent.

### T004 — Implement duplicate-token grouping and safe CLI output

- Status: completed
- Objective: Group exact duplicate secrets and report targets without exposing secret-derived values.
- Scope:
  - Recognize supported GitHub GCM targets, report malformed GitHub-shaped entries, ignore unrelated credentials, and assign per-run ordinal group labels.
- Acceptance criteria:
  - Output contains targets and temporary group IDs but no token, token fragment, hash, or fingerprint.
- Implemented:
  - Added classification, exact in-memory byte grouping, stable-in-run ordering, safe text output, and explicit unrecognized reasons.
- Verification:
  - Synthetic output-secrecy, duplicate, malformed, host-level, path-level, and empty-inventory tests passed on 2026-10-11.
- Remaining:
  - None for synthetic behavior; live behavior is tracked by T006.
- Notes:
  - Group labels are intentionally unsuitable for persistent configuration.

### T005 — Unit tests with synthetic credentials

- Status: completed
- Objective: Verify Milestone 1 without accessing real credentials.
- Scope:
  - Use only synthetic target names and secret byte strings.
- Acceptance criteria:
  - Tests cover grouping, classification, malformed data, no entries, platform guard, and output secrecy.
- Implemented:
  - Added standard-library unittest coverage with a mocked enumeration boundary.
- Verification:
  - `uv run python -m unittest discover -s tests -v` passed on 2026-10-11.
- Remaining:
  - None.
- Notes:
  - No test invokes Windows credential enumeration.

### T006 — Windows integration verification

- Status: completed
- Objective: Confirm the read-only prototype matches actual GCM wincredman entries on Windows.
- Scope:
  - User-run inventory comparison, duplicate grouping check, secrecy check, and error/exit-code observation.
- Acceptance criteria:
  - User confirms targets match Credential Manager, known duplicates group together, no secret material appears, and the command exits successfully.
- Implemented:
  - Added a concrete user-side verification procedure to `README.md`.
- Verification:
  - Automated checks passed on 2026-10-11.
  - User-run inventory on three Windows hosts on 2026-10-12 reported 2, 2, and 30 supported entries respectively, zero unrecognized GitHub entries, no exposed secret material, and exit code 0.
  - Live results included both host-level and path-specific targets, optional `LegacyGeneric:target=` prefixes, singleton groups, and multi-entry exact-secret groups.
  - User confirmed on 2026-10-13 that targets reported in the same temporary group share the same Credential Manager credential in practice.
  - User identified the nine-group result as expected drift caused by credentials fetched at different times; the intended managed state has two credential groups, with one SSO-enabled GitHub token shared across orgA, orgB, and orgD.
- Remaining:
  - None.
- Notes:
  - Different groups mean the stored credential blobs differ byte-for-byte; they do not by themselves establish whether the operational account-to-credential assignment is intended.
  - The third host's split across nine secret groups is confirmed credential drift relative to the intended two-group policy. Detecting that policy mismatch belongs to T007's persistent configuration and audit design.

### T007 — Design group configuration and audit

- Status: completed
- Objective: Define persistent repository-to-credential-group mapping and consistency audit behavior without storing secret-derived identifiers.
- Scope:
  - Configuration schema, repository identity rules, drift detection, validation, and safe report design.
- Acceptance criteria:
  - Design covers malformed configuration, missing members, split secrets, and backend-explicit operation with synthetic tests.
- Implemented:
  - Added a versioned, backend-explicit TOML schema with stable user-chosen group names and case-insensitive `owner/repository` identities.
  - Added strict configuration validation and read-only audit findings for missing members and groups split across different credential blobs.
  - Added a secret-safe `audit` CLI with distinct success, drift, and error exit statuses and documented its behavior and limitations.
- Verification:
  - Full synthetic unit suite, source compilation, and diff whitespace check passed on 2026-10-13.
- Remaining:
  - None.
- Notes:
  - Persistent group identity must be user-configured and independent of token content.

### T008 — Design and implement safe rotation

- Status: in progress
- Objective: Replace a token for an explicitly selected group with dry-run, verification, recovery, and partial-failure reporting.
- Scope:
  - Research GCM-supported mutation interfaces, authorization boundary, recovery journal design, and synthetic failure tests.
- Acceptance criteria:
  - Rotation requires explicit live authorization, defaults safely, verifies every intended member, and reports recoverable partial outcomes without leaking secrets.
- Implemented:
  - None.
- Verification:
  - Not run.
- Remaining:
  - Validate GCM mutation behavior, define authorization and recovery behavior, then implement and test rotation.
- Notes:
  - No live mutation is authorized by the current project bootstrap request.

### T009 — Investigate DPAPI support

- Status: pending
- Objective: Add an explicit adapter for GCM's DPAPI protected-file credential store.
- Scope:
  - Confirm file naming/layout, DPAPI protection semantics, configuration paths, read-only enumeration, and later mutation behavior.
- Acceptance criteria:
  - Backend is explicitly selected, tested synthetically where possible, and never performs automatic migration.
- Implemented:
  - None.
- Verification:
  - Not run.
- Remaining:
  - Perform source research and design after wincredman milestone work.
- Notes:
  - GCM documents the default path as `%USERPROFILE%\.gcm\dpapi_store`.

## Decisions

### D001 — Standard-library Windows API binding

- Date: 2026-10-11
- Status: accepted
- Decision: Use `ctypes` for read-only `CredEnumerateW`/`CredFree` access in Milestone 1.
- Rationale: Python ships the required FFI, the API surface is small, and no third-party dependency is justified.
- Consequences:
  - Windows structures and ownership rules are maintained locally and require live integration verification.
- Related tasks: `T002`, `T003`, `T005`, `T006`

### D002 — Ephemeral grouping labels

- Date: 2026-10-11
- Status: accepted
- Decision: Compare exact secret bytes in memory and expose only per-invocation ordinal labels.
- Rationale: Persistent hashes would create reusable token fingerprints and violate the security objective.
- Consequences:
  - Labels can change when inventory membership or ordering changes and cannot serve as configuration keys.
- Related tasks: `T004`, `T007`

### D003 — Strict initial target support

- Date: 2026-10-11
- Status: accepted
- Decision: Support only Generic credentials in the `git` namespace whose parsed HTTPS host is exactly `github.com`; report malformed GitHub-shaped entries and ignore unrelated targets.
- Rationale: This follows observed GCM conventions while avoiding guesses about enterprise hosts or unknown layouts.
- Consequences:
  - GitHub Enterprise support would require a separately accepted configuration and task.
- Related tasks: `T002`, `T004`

### D004 — Rotation gate

- Date: 2026-10-11
- Status: accepted
- Decision: Do not implement rotation until T006 live read-only inventory verification is complete.
- Rationale: Mutation must not build on an unverified interpretation of live credential storage.
- Consequences:
  - The live inventory gate and T007 configuration prerequisite are satisfied.
- Related tasks: `T006`, `T008`

## Blocked items

- None.

## Cancelled items

- None.

## Candidate items

- None.
