# ORBIT-INTEGRITY-SYNC (OIS) — algorithm, batched plan, and automation

This document **defines the algorithm**, **batches all related work** into one structured runbook, and specifies **patterned automation** (shell guards, conditionals). It **supersedes** ad-hoc sequences (e.g. one-off onward notes) by folding them into **one repeatable procedure**.

**Primary pin:** `integrity_and_sync` — writable Git object DB, accurate `ahead/behind`, disciplined submodule pointers, quality gates before push, post-push smoke + memo row.

---

## Part 1 — Algorithm definition

### Name

**ORBIT-INTEGRITY-SYNC (OIS)** — monorepo / multi-repo **integrity first**, then **sync**, then **integration** (push), then **verification** (reward row).

### Inputs


| Symbol | Meaning                                                             |
| ------ | ------------------------------------------------------------------- |
| `R`    | Repository root (absolute path)                                     |
| `B`    | Branch name (e.g. `hogsmade`, `main`)                               |
| `U`    | Upstream ref (e.g. `origin/hogsmade`)                               |
| `G`    | Quality gate profile: `lint_only` \| `lint_and_test` \| `lint_and_test_subset` |
| `S`    | Stash policy: `none` \| `stash_all` \| `commit_single_paths` |
| `P`    | Path filter for commits (optional list; never empty string = “all”) |


### State vector (after each phase)

`S_vec = (objects_ok, dirty_count, ahead, behind, staged_paths, conflict_flag)`

### Halting conditions (hard stops)

1. **`objects_ok == false`** — any `.git/objects` shard not owned by the repo user → **HALT** until `chown` (human-gated `sudo`).
2. **`pre_commit_fail`** on a commit that includes unintended paths → **HALT**, restore stash, narrow `P`.
3. **`transistor_stuck`** (harness) if a harness cycle is active → **HALT** harness per harness skill; do not push blindly.

### Core algorithm (control flow)

```
procedure OIS(R, B, U, G, S, P):
  PHASE_0_PRECONDITIONS(R)
  PHASE_1_FOUNDATION_DISCOVERY(R, B, U)
  PHASE_2_PROBE_QUALITY_GATES(R, G)
  PHASE_3_SILENCE_ISOLATE(R, B, U, S, P)
  PHASE_4_INTEGRATION_SYNC(R, B, U)
  PHASE_5_REWARD_VERIFY(R, B, U)
end

PHASE_0_PRECONDITIONS(R):
  objects_ok := (count files in R/.git/objects not owned by effective_uid) == 0
  if not objects_ok:
    HALT "fix object ownership"

PHASE_1_FOUNDATION_DISCOVERY(R, B, U):
  run: git -C R fetch origin
  ahead := count(git -C R log --oneline U..B)
  behind := count(git -C R log --oneline B..U)
  dirty := parse(git -C R status --porcelain)  # non-empty => dirty

PHASE_2_PROBE_QUALITY_GATES(R, G):
  if G == lint_only:
    run lint recipe for R
  else if G == lint_and_test:
    run lint + full test recipe
  else if G == lint_and_test_subset:
    run lint + documented subset tests + append note to memo

PHASE_3_SILENCE_ISOLATE(R, B, U, S, P):
  if behind > 0 and dirty and S == stash_all:
    git -C R stash push -u -m "OIS wip before rebase"
  else if behind > 0 and dirty and S == commit_single_paths:
    assert P is non-empty and paths are intentional
    git add P only
    git commit -m "chore: OIS isolated commit"   # single concern
  else if behind > 0 and dirty and S == none:
    HALT "cannot rebase with dirty tree"
  if intent is submodule_only:
    stage only submodule path(s) in P

PHASE_4_INTEGRATION_SYNC(R, B, U):
  if behind > 0:
    git -C R pull --rebase origin B   # or merge if policy forbids rebase
  if conflict_flag:
    HALT "resolve conflicts"
  if ahead > 0:
    git -C R push U B   # one push; SSH retry policy per workspace rules

PHASE_5_REWARD_VERIFY(R, B, U):
  run post-push smoke (repo-specific)
  update orbit memo row (path | branch | ahead/behind | last gate)
  optional: harness_manifest / get_scenario_insights if harness is in-loop
```

### Conditional matrix (arguments → branch)


| `behind` | `ahead` | `dirty` | `S`                   | **Chosen branch**                                                                                                   |
| -------- | ------- | ------- | --------------------- | ------------------------------------------------------------------------------------------------------------------- |
| >0       | any     | yes     | `stash_all`           | Stash → rebase → stash pop                                                                                          |
| >0       | any     | yes     | `none`                | **HALT** (educate: stash or commit)                                                                                 |
| >0       | any     | no      | any                   | Rebase (or merge) only                                                                                              |
| 0        | >0      | no      | any                   | Push only                                                                                                           |
| 0        | >0      | yes     | `commit_single_paths` | Commit with `P`, then push                                                                                          |
| >0       | >0      | yes     | `commit_single_paths` | Prefer **isolate** submodule/docs commit **before** stash+rebase if that commit should sit **under** remote commits |


---

## Part 2 — Batched plan (everything in one structure)

All batches map to **OIS phases**. Execute **in order**; do not skip Phase 0.


| Batch  | Phase | Scope              | Primary paths                                                                                                               |
| ------ | ----- | ------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| **B0** | 0     | Object DB + fetch  | `CascadeProjects`, any large git repo with prior `root` shards                                                              |
| **B1** | 1     | Discovery snapshot | `CascadeProjects` (`hogsmade`), `Projects/GRID-main`, `Projects/Vision`, `roots/python-craft`                               |
| **B2** | 2     | Quality            | GRID: `make lint`; optional `make test` or subset + memo note; Vision: `uv run pytest`; python-craft: `uv run pytest`       |
| **B3** | 3     | Isolation          | Submodule-only commits (`Projects/GRID-main` pointer), stash for unrelated WIP                                              |
| **B4** | 4     | Integration        | `git pull --rebase origin <branch>`; `git push`                                                                             |
| **B5** | 5     | Reward             | GRID: RAG `where`/hybrid note + `~/.rag-sessions` check; update `ONWARD_ORBIT_MEMO` or successor; harness manifest if armed |


### Part 2.1 — Current operational snapshot (checkpoint)

Values below are a **checkpoint** from discovery on **2026-04-15 (post-publish / hogsmade sync / submodule pin)** (`git status -sb`, `git rev-list --left-right --count '@{u}...HEAD'`). Re-run Part 3 “discovery row” before acting; numbers drift.

**Ground truth:** for these four paths, **local git** (status + `@{u}...HEAD`) overrides any external dashboard (for example seeds `ecosystem_scan` may aggregate a different root or lag submodule state).

**Integer drift:** each doc commit bumps `ahead` for that repo—numbers in the table are **frozen at edit time**. Before acting, always re-run the Part 3 discovery pattern; never treat this table as a live substitute for `git`.

| Repo | Branch / upstream | Behind / ahead | Working tree (summary) |
|------|-------------------|----------------|-------------------------|
| `CascadeProjects` | `hogsmade` → `origin/hogsmade` | **0 / 0** | **Synced** with remote; **`Projects/GRID-main` gitlink** **`f074b02`** (GRID `origin/main` at this checkpoint). Latest hogsmade submodule bump: **`7f1f493`**. **ONWARD_ORBIT_MEMO** defers duplicate SHAs to this row. Tracked tree clean; optional **untracked** GATE JSON + viz HTML remain operator choice. |
| `CascadeProjects/Projects/GRID-main` | `main` → `origin/main` | **0 / 0** | Clean; **pushed** (orbit memo / OIS alignment on `origin/main`). |
| `CascadeProjects/Projects/Vision` | `main` → `origin/main` | **0 / 0** | Dirty: modified CONTRIBUTING, README, `pyproject.toml`, `vision_ui/cli.py`, tests, `uv.lock`; untracked `docs/`, `.github/workflows/ci-ocr-smoke.yml`, `tests/test_ui_ux_surface_reference.py`. |
| `roots/python-craft` | `main` → `origin/main` | **0 / 0** | Clean; **pushed** (OIS runbook commits on `origin/main`). |

### Part 2.2 — Next OIS invocation (worked example: CascadeProjects / hogsmade)

**Typical state (historical):** `behind > 0`, `ahead ≥ 0`, `dirty = yes` — matrix row: **S = `stash_all`** (or **`commit_single_paths`** with explicit `P`). **S = `none`** → **HALT** (cannot rebase on a dirty tree).

**Sequence:** Run **B0** if object ownership was ever suspect; then **Pattern: rebase train** (Part 3): stash WIP, `git pull --rebase origin hogsmade`, `git stash pop`, resolve conflicts, `git push origin hogsmade`.

**Lock-in note (2026-04-15):** On this monorepo, `git stash push` returned **“Cannot save the current status”** (cause not pinned here); **`git pull --rebase --autostash origin hogsmade`** succeeded and preserved WIP, then **`git push origin hogsmade`** completed. Prefer manual stash when it works; use **`--autostash`** as a fallback when stash is broken.

**Guard:** Do **not** run a submodule-only commit while the index still contains unrelated paths. Always `git diff --cached --stat` and confirm **only** `P` before `git commit`.

---

## Part 3 — Patterned automation (copy-paste blocks)

### Guard: object ownership (Phase 0)

```bash
REPO=/home/caraxes/CascadeProjects
find "$REPO/.git/objects" -maxdepth 2 ! -user "$(id -un)" 2>/dev/null | head
# expect no output; else HALT and chown (human)
```

### Pattern: discovery row (Phase 1)

**Wired shortcut:** from `roots/python-craft`, run `make orbit-snapshot` (same four paths + submodule gitlink; env overrides in `scripts/oissnapshot.sh`).

```bash
for R in /home/caraxes/CascadeProjects /home/caraxes/CascadeProjects/Projects/GRID-main /home/caraxes/CascadeProjects/Projects/Vision /home/caraxes/roots/python-craft; do
  echo "=== $R ==="
  git -C "$R" status -sb 2>/dev/null || echo "(not a git repo)"
  U=$(git -C "$R" rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null) && \
    git -C "$R" rev-list --left-right --count "$U...HEAD" 2>/dev/null | awk '{print "behind ahead:", $1, $2}'
done
```

### Pattern: submodule-only commit (Phase 3 + partial 4)

```bash
cd /home/caraxes/CascadeProjects
git diff --cached --stat   # must show only intended paths
git commit -m "chore(submodule): bump Projects/GRID-main to <SHA>"
```

### Pattern: rebase train (Phase 3–4)

```bash
cd /home/caraxes/CascadeProjects
git stash push -u -m "OIS wip before rebase"
git pull --rebase origin hogsmade
git stash pop
# resolve; git rebase --continue if needed
git push origin hogsmade
```

### Pattern: rebase train — `autostash` fallback (when `git stash push` fails)

```bash
cd /home/caraxes/CascadeProjects
# If "Cannot save the current status" on stash, try:
git pull --rebase --autostash origin hogsmade
git push origin hogsmade
```

---

## Part 4 — Finishing touches and final polish (pre-implementation checklist)

1. **Single source of truth** — Link this file from Vision [`docs/JOURNEY.md`](file:///home/caraxes/CascadeProjects/Projects/Vision/docs/JOURNEY.md) (one line) and/or GRID [`docs/ONWARD_ORBIT_MEMO.md`](file:///home/caraxes/CascadeProjects/Projects/GRID-main/docs/ONWARD_ORBIT_MEMO.md) as “OIS runbook mirror”.
2. **Pre-commit contract** — Document that pre-commit may **stash unstaged** during commit; always `git diff --cached --stat` before `git commit`.
3. **SSH policy** — One SSH retry, then `gh` HTTPS fallback (workspace rule) — add to **Batch B4** operator note.
4. **Harness coupling** — If `harness_status` reports active scenario, **insert HALT** before Batch B4 push; run `agent_disarm()` first.
5. **Paris / leap UI** — Treat `[paris-helmet.html](file:///home/caraxes/paris-helmet.html)` as **human-only** review surface; automation writes **memo row**, not HTML.
6. **Cursor plugins** — Batch B5 optional: `npm audit` / plugin vendor bumps are **separate** OIS runs with `G=lint_only` at repo root of each plugin consumer (avoid mixing with `hogsmade` git train).

---

## Part 5 — Revision note (vs earlier “onward” plan)


| Old plan element      | OIS mapping                                                                                               |
| --------------------- | --------------------------------------------------------------------------------------------------------- |
| Phase A GRID push     | **B2–B4** on `GRID-main` with `U=origin/main`                                                             |
| Phase B post-push     | **B5**                                                                                                    |
| Phase C ecosystem     | **B1** discovery on multiple `R`                                                                          |
| Phase D memo          | **B5** reward row                                                                                         |
| ad-hoc `repo-hygiene` | **OIS** is the formalization; `/repo-hygiene` remains the **Claude invocation** of Batch B1–B3 heuristics |


---

## Implementation order (ready)

1. **Publish:** Leaf repos (`roots/python-craft`, `GRID-main`) — **git push** `origin/main` after verifying `origin/main..HEAD`. Monorepo **hogsmade** — `git pull --rebase` (+ stash or **`--autostash`**) then **git push** `origin/hogsmade`. After any material git event, refresh **Part 2.1** via Part 3 discovery.
2. Run **B0** once per machine after any `sudo git` incident (or if `find` on `.git/objects` shows wrong owner).
3. Execute **B1 → B5** for `CascadeProjects` on **hogsmade** until `ahead==0 && behind==0` (lock-in achieved **2026-04-15**; see **Part 2.2** for stash vs **`--autostash`**). Submodule **`Projects/GRID-main`** is pinned to **`f074b02`** on `hogsmade` (**`7f1f493`**); re-run submodule-only flow when GRID `main` advances again. **ONWARD_ORBIT_MEMO** defers duplicate SHAs here to this table. Update the orbit memo in **B5** when facts change.
4. Mirror one-line pointer in GRID/Vision docs (polish items 1–2).

