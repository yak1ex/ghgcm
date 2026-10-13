# TASKS.md

## Project objective

Build a Windows-focused Python CLI, managed with uv, that safely inventories and groups GitHub credentials stored by Git Credential Manager, then adds explicit audited rotation and DPAPI support in later verified milestones.

## Scope and constraints

- In scope: wincredman inventory, duplicate-secret grouping, safe output, synthetic tests, persistent group design, audited rotation after verification, and explicit DPAPI backend support.
- Out of scope: automatic backend migration, non-Windows credential stores, secret-bearing reports, and live credential modification without explicit authorization.
- Deployment target: Local Windows 10+ interactive sessions with Python 3.11+ and GCM.
- Important constraints: Standard library preferred; dependencies require approval; live secrets never leave the local process; rotation is gated on T006; no commits or pushes without authorization.

## Current status

The project scaffold and read-only Milestone 1 prototype are implemented with standard-library Windows API bindings and synthetic unit tests. Live Windows Credential Manager behavior has not been exercised by the agent and awaits user verification.

## Current plan

1. `T006` — Verify read-only inventory against a user-controlled Windows GCM environment.
2. `T007` — Design persistent repository-to-group configuration and consistency audits.
3. `T008` — Validate a supported GCM mutation path, then design and implement authorized safe rotation.
4. `T009` — Investigate and implement an explicit DPAPI backend adapter.

- Selection basis: Milestone 1 implementation and synthetic verification precede live verification; rotation is explicitly gated on successful inventory verification.
- Last reviewed: 2026-10-11

## Active work

- Task: `T006`
- Current step: Await user-side live Windows verification using the README procedure.
- Waiting on: `user`
- Required action: Run the documented inventory command and report the exit code and pass/fail results without sharing credential values.

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

- Status: in progress
- Objective: Confirm the read-only prototype matches actual GCM wincredman entries on Windows.
- Scope:
  - User-run inventory comparison, duplicate grouping check, secrecy check, and error/exit-code observation.
- Acceptance criteria:
  - User confirms targets match Credential Manager, known duplicates group together, no secret material appears, and the command exits successfully.
- Implemented:
  - Added a concrete user-side verification procedure to `README.md`.
- Verification:
  - Automated checks passed; awaiting user verification of live Windows integration.
- Remaining:
  - Run and report the documented live checks without pasting secrets.
- Notes:
  - This task remains in progress under the template completion policy.

### T007 — Design group configuration and audit

- Status: pending
- Objective: Define persistent repository-to-credential-group mapping and consistency audit behavior without storing secret-derived identifiers.
- Scope:
  - Configuration schema, repository identity rules, drift detection, validation, and safe report design.
- Acceptance criteria:
  - Design covers malformed configuration, missing members, split secrets, and backend-explicit operation with synthetic tests.
- Implemented:
  - None.
- Verification:
  - Not run.
- Remaining:
  - Begin after T006 verification.
- Notes:
  - Persistent group identity must be user-configured and independent of token content.

### T008 — Design and implement safe rotation

- Status: pending
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
  - T006 and T007 must complete first; validate GCM mutation behavior before implementation.
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
  - T008 remains pending even though its requirements are known.
- Related tasks: `T006`, `T008`

## Blocked items

- None. T006 is awaiting user verification rather than blocked.

## Cancelled items

- None.

## Candidate items

- None.
