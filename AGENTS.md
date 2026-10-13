# AGENTS.md

Operating instructions for coding agents working in GitHub Credential Group Manager. Read this file and `TASKS.md` before changing the repository.

## 1. Non-negotiable rules

1. Do not fabricate repository facts, file paths, APIs, commands, test results, or completion claims. Inspect or run them.
2. Make the smallest change that satisfies the requested outcome. Do not perform unrelated cleanup, refactoring, reformatting, or feature work.
3. Match existing repository structure, conventions, and patterns unless the task explicitly changes them.
4. Do not add, remove, replace, or upgrade dependencies without prior user approval.
5. Do not create commits, rewrite history, push, or publish without explicit user authorization.
6. Keep `TASKS.md` synchronized with meaningful implementation progress in the same work cycle.
7. Never display, log, persist in reports, transmit, or commit credential secrets, token fragments, private keys, or persistent token fingerprints.
8. Never modify live credentials without explicit user authorization. Enumeration and modification are separate permission boundaries.

## 2. Project context

- Project: GitHub Credential Group Manager
- Objective: Inventory, group, audit, and eventually rotate GitHub credentials managed by GCM on Windows without exposing secrets.
- Primary language: Python
- Frameworks: Python standard library; uv project management
- Runtime and deployment target: Local Windows CLI
- Supported host platforms: Windows; non-Windows execution is supported only for synthetic unit tests
- External runtime requirements: Windows Credential APIs and, for live use, Git Credential Manager

## 3. Repository orientation

Before editing, read `TASKS.md`, inspect affected source and tests, inspect manifests and lockfiles, check the worktree, and define observable success criteria.

- Source: `github_credential_groups/`
- Tests: `tests/`
- Configuration: `pyproject.toml`, `.python-version`, `.agentic-template.yml`
- Documentation: `README.md`, `docs/`
- Generated paths not to edit manually: `.venv/`, `dist/`, `build/`, `*.egg-info/`, `uv.lock`

## 4. Implementation policy

- Implement only accepted task scope and work required for correctness.
- Prefer direct standard-library code and handle failures at Windows API and parsing boundaries.
- Keep inventory operations strictly read-only.
- Treat unknown target or blob layouts as unrecognized; do not guess or silently reinterpret them.
- Update documentation when behavior changes.
- Do not begin rotation until T006 live inventory verification is complete.

## 5. Dependency policy

Prefer the standard library and existing dependencies. Prior user approval is required before any dependency addition, removal, replacement, or version change. Before requesting approval, document the need, standard-library alternatives, operational impact, and affected manifest and lock files. Synchronizing already declared dependencies is allowed.

## 6. Verification policy

Success requires observable checks. Run configured tests and executable checks, read their output, and record results in `TASKS.md`. Use synthetic secrets for automated tests. Do not run live inventory as an automated test or capture live output. Windows Credential Manager integration remains `in progress` with `Awaiting user verification` until the user performs the documented checks.

Objective non-integration work may be marked `completed` after relevant checks pass. Documentation-only work may be completed after consistency review. Do not equate code written with task completion.

## 7. Task management

`TASKS.md` is authoritative. Classify new work as part of an existing task, a new accepted task with the next unused `T###`, a candidate with the next unused `C###`, or no action. Stable IDs are never renumbered or reused. `Current plan` defines execution order; only one task is active.

Allowed statuses are `pending`, `in progress`, `blocked`, `completed`, and `cancelled`. When status, plan, or active work changes, update the related fields together. A completed or cancelled task cannot be active. `Waiting on: none` requires `Required action: None.` Keep implementation, verification, remaining work, and blockers factual and concise.

## 8. Git and workspace safety

- Inspect the worktree before and after work and preserve unrelated changes.
- Do not discard, overwrite, stage, or modify unrelated work.
- Do not commit or push without explicit authorization.
- Avoid destructive Git commands.
- Do not add AI attribution.

## 9. Commands

- Install or synchronize: `uv sync`
- Run locally: `uv run python -m github_credential_groups.cli inventory --backend wincredman`
- Build: N/A
- Test all: `uv run python -m unittest discover -s tests -v`
- Test focused: `uv run python -m unittest tests.test_inventory -v`
- Lint: N/A
- Format check: N/A
- Type or static check: N/A
- Package or release check: N/A

## 10. Repository-specific constraints

- Never send credential material to an LLM or external service; live verification output stays with the user.
- Never use real credentials in automated tests.
- Do not persist secret-derived hashes or other stable fingerprints.
- Keep backend selection explicit and never migrate between credential stores automatically.
- Prefer GCM-supported mutation interfaces for future rotation after their behavior is validated.

## 11. Python with uv

- Treat `pyproject.toml` and `uv.lock` as project and resolution sources.
- Use the Python version declared in `.python-version` and `requires-python`; do not silently broaden compatibility.
- Run project commands through `uv run` and synchronize with `uv sync`.
- Add dependencies only after approval with `uv add`; update the manifest and lockfile together.
- Prefer importable modules and package entry points over path-dependent scripts.
- Do not use `uv pip install` as the normal project workflow.
- Run the configured unittest suite and at least compile source files for relevant changes.

## 12. Project learnings

- GCM's wincredman targets can be returned with or without `LegacyGeneric:target=`; classification must support both forms.

## 13. User handoff and action requests

Use exactly one outcome: `No user action required`, `Permission required`, `Decision required`, `User verification required`, or `Blocked`. If user action is required, end with a clearly labelled `User action required` section containing concrete steps and expected feedback.

## 14. Final response checklist

Review changed files, run relevant checks, confirm `TASKS.md` consistency, distinguish verified behavior from live integration claims, mention risks and unfinished work, and state whether user action is required.
