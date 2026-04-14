# AGENTS.md — python-craft

## OIS / integrity

- Git-grounded checkpoint and automation: `docs/INTEGRITY_SYNC_BATCH_ALGORITHM.md` (Part 2.1 + Part 3).
- Supply-chain continuity (interim CVE posture, scans): `docs/SECURITY_CONTINUITY.md`.

## Wired commands

| Command | Purpose |
|--------|---------|
| `make orbit-snapshot` | Status + `behind/ahead` + submodule gitlink for the four-root constellation. Prefer **`CASCADE_WORKSPACE_ROOT`** for the monorepo path; see `scripts/oissnapshot.sh`. |
| `make audit` | `uv export` + `pip-audit` (OSV, interim ignore per doc) + Bandit on `src/craft`. |
| `make audit-strict` | `uv export` + `pip-audit` with **no** CVE ignores (margin / red-team view). |

## Precedence

If narrative docs disagree with `git` or `git ls-tree` for submodule pins, **trust git** first, then reconcile docs.

## Rhyme-and-reasons

Prose-only in this repo unless Semantic Officer source modules are actually in-tree; do not fabricate API/state names for instruction assets.
