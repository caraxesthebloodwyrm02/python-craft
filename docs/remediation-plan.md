# Portfolio health remediation plan

Follow-up to the methodology contract in
[PORTFOLIO_HEALTH_METHODOLOGY_REMEDIATION.md](PORTFOLIO_HEALTH_METHODOLOGY_REMEDIATION.md)
(merged via PR #2). This plan applies the methodology's rubrics and dimensions to the
**observable current state** of the `python-craft` repo and proposes a prioritized,
sequenced backlog of fixes.

## Data source note

No pre-existing portfolio-health report artifact (JSON, CSV, or markdown) was found in
the repo or as a CI artifact. The private portfolio repos (`hogsmade`, `gruff`) referenced
in the methodology were not accessible from this session's Git scope. The signals below
were extracted directly from `python-craft`'s Git history, CI configuration, and project
files on 2026-04-29.

**Step 0 recommendation:** before scoring the full portfolio, generate the raw CSV
extracts specified in the methodology (`repos.csv`, `weekly_activity.csv`,
`pull_requests.csv`) from the GitHub API. Until those exist, this plan uses the
single-repo signals available today.

---

## Current-state signal summary (python-craft)

| Signal | Observed value | Methodology reference |
|--------|---------------|----------------------|
| Total commits (main, all time) | 11 | Delivery velocity |
| Human-directed PRs merged (12 weeks) | 1 (#2) | `net_human_directed_prs_per_week_12w` |
| PR merge rate on default branch | ~9% (1 of 11 first-parent commits via PR) | Governance: `default_branch_pr_percent` |
| Commit authors (90 days) | 1 human (caraxesthebloodwyrm02), 1 bot (devin-ai-integration) | Team resilience / bus factor |
| Bus factor (50%) | 1 | Team resilience |
| Tags / releases | None | Maintainability: release cadence |
| Test files | 0 | Quality signal: test volume ratio |
| Source SLOC | 3,537 (15 modules in `src/craft/`) | Quality signal: test SLOC / source SLOC |
| CI workflows | `security-audit.yml` (pip-audit + Bandit), `security-audit-strict.yml` (scheduled) | Quality signal: CI maturity |
| Unit/integration tests in CI | None | Quality signal: CI tests |
| Lint/typecheck in CI | None (Ruff config exists in `pyproject.toml` but not wired to CI) | Quality signal: lint/types |
| CI pass rate (30 days) | ~100% for security-audit jobs | Quality signal: CI health |
| Branch protection | Not observed (direct pushes dominate history) | Governance |
| CODEOWNERS | Absent | Governance |
| Pre-commit hooks | Absent | Quality signal |
| README quality | Good (tier map, install, security, module docs) | Maintainability |
| Lockfile | Present (`uv.lock`) | Maintainability |
| Dockerfile / devcontainer | Absent | Maintainability |
| Weekly commit distribution (12 weeks) | 10 commits in week of 2026-04-15, 1 in week of 2026-04-29, 0 in remaining 10 weeks | Momentum |
| 90-day human-directed commits | <20 | Momentum gate: `n/a` |
| Dormancy state | **Warming** — low history but clear recent work | Dormancy state machine |
| Repo class (inferred) | **Library** — reusable LSP templates consumed by ecosystem repos | Class-aware weights |

---

## Prioritized issue list

Issues are ordered by methodology severity and quick-win potential. Severity uses
the methodology's absolute rubrics.

### Severity: Critical

| # | Issue | Dimension | Current score | Target score | Owner suggestion | Effort |
|---|-------|-----------|--------------|-------------|-----------------|--------|
| C1 | **Zero test coverage** — no test files exist for 3,537 SLOC | Quality signal (CI tests) | 0 / 3 | ≥2 (unit/integration tests) | Repo owner + AI-assisted session | **M** (2–4 days) |
| C2 | **Governance: 91% direct pushes** — only 1 of 11 commits merged via PR | Governance (`default_branch_pr_percent`) | ~1 / 5 | ≥4 (≥90% via PR) | Repo owner (branch protection settings) | **S** (1 hour config) |
| C3 | **No lint or typecheck in CI** — Ruff config present but not enforced | Quality signal (lint/types) | 1 / 3 (config only) | 3 (required and passing) | Repo owner or AI session | **S** (1–2 hours) |

### Severity: High

| # | Issue | Dimension | Current score | Target score | Owner suggestion | Effort |
|---|-------|-----------|--------------|-------------|-----------------|--------|
| H1 | **Single-owner bus factor** — one human owns 100% of code | Team resilience (bus factor 50%) | 1 / — (single contributor) | ≥2 contributors at 50% threshold | Org-level decision | **L** (ongoing) |
| H2 | **No branch protection on `main`** | Governance (branch protection) | 0 / 3 | 3 (enabled with required checks) | Repo owner (GitHub settings) | **S** (30 min) |
| H3 | **No required reviews before merge** | Governance (reviews required) | 0 / 2 | 2 | Repo owner (GitHub settings) | **S** (30 min, combine with H2) |

### Severity: Medium

| # | Issue | Dimension | Current score | Target score | Owner suggestion | Effort |
|---|-------|-----------|--------------|-------------|-----------------|--------|
| M1 | **No releases or tags** — library repos need version cadence | Maintainability (release cadence) | 0 | ≥1 tagged release | Repo owner | **S** (1 hour) |
| M2 | **No CODEOWNERS** — no review routing | Governance (owner review routing) | 0 / 2 | 2 | Repo owner | **S** (30 min) |
| M3 | **No pre-commit hooks** — formatting and lint not enforced locally | Quality signal | 0 | Ruff + basic hooks | Repo owner or AI session | **S** (1 hour) |
| M4 | **CI limited to security audit** — no build verification step | Quality signal (CI workflow maturity) | 1 / 3 (exists but minimal) | 3 (required on default branch) | Repo owner or AI session | **S** (1–2 hours) |

### Severity: Low

| # | Issue | Dimension | Current score | Target score | Owner suggestion | Effort |
|---|-------|-----------|--------------|-------------|-----------------|--------|
| L1 | **No Dockerfile or devcontainer** — setup reproducibility gap | Maintainability | 0 | 1 (devcontainer or Dockerfile) | AI-assisted session | **S** (2–3 hours) |
| L2 | **Escape-hatch audit not tracked** — `# type: ignore`, `Any` usage per KLOC unknown | Maintainability | unknown | Baselined | AI-assisted session | **S** (1 hour) |
| L3 | **Momentum not evaluable** — <20 human-directed commits in 90 days | Delivery velocity | `n/a` | Establish baseline after next quarter | N/A (volume gate) | — |

---

## Suggested sequencing

The plan is grouped into three waves: **quick wins** (configuration-only, no code
changes), **foundation** (test and CI infrastructure), and **sustained improvements**
(ongoing ownership and process).

### Wave 1 — Quick wins (week 1)

Target: governance and CI configuration. No production code changes required.

| Order | Item | Dependencies | Estimated time |
|-------|------|-------------|---------------|
| 1.1 | Enable branch protection on `main`: require PR, require status checks, require 1 review | None | 30 min |
| 1.2 | Add `CODEOWNERS` file mapping `src/craft/**` and `docs/**` to repo owner | None | 30 min |
| 1.3 | Add Ruff lint + format check CI job; make it a required status check | 1.1 (to enforce as required) | 1–2 hours |
| 1.4 | Add pre-commit config with Ruff hooks | None | 1 hour |
| 1.5 | Tag `v0.1.0` from current `main` as initial release baseline | None | 15 min |
| 1.6 | Add merge-method policy note to `CONTRIBUTING.md` or `AGENTS.md` | None | 30 min |

**Depends on:** repo owner has GitHub admin access for branch protection.

### Wave 2 — Test and CI foundation (weeks 2–3)

Target: quality signal infrastructure. Code changes required.

| Order | Item | Dependencies | Estimated time |
|-------|------|-------------|---------------|
| 2.1 | Add `pytest` to dev dependency group and wire `make test` target | None | 1 hour |
| 2.2 | Write smoke tests for tier modules (`t1`–`t6`): import checks, basic invocation | 2.1 | 1 day |
| 2.3 | Write unit tests for `gruff_geometric_sketch`, `sylveon_heatmap`, `atlas_polar_field` render paths | 2.1 | 2 days |
| 2.4 | Add pytest CI job; make it a required status check | 2.1, 1.1 | 1–2 hours |
| 2.5 | Add `basepyright` or `mypy` type checking — start with `src/craft/` modules | None | 1 day |
| 2.6 | Track test SLOC / source SLOC ratio; target ≥5% initially, ≥20% long-term | 2.2, 2.3 | Ongoing |
| 2.7 | Add a build-verification CI job (`uv sync --group all` + `python -c "import craft"`) | None | 1 hour |

### Wave 3 — Sustained improvements (weeks 4+)

Target: bus factor, reporting infrastructure, and cross-portfolio tooling.

| Order | Item | Dependencies | Estimated time |
|-------|------|-------------|---------------|
| 3.1 | Onboard a second contributor or establish paired review for critical modules | Org decision | Ongoing |
| 3.2 | Create scoring workspace: `scoring_config.yml`, data directories, extraction script per methodology Phase 0 | None | 1–2 days |
| 3.3 | Implement GitHub API extraction for `repos.csv`, `weekly_activity.csv`, `pull_requests.csv` (methodology Phase 1) | 3.2 | 2–3 days |
| 3.4 | Implement automation classifier (dependency-bot, CI commit-back, AI-assisted, pure human) per methodology Phase 2 | 3.3 | 1–2 days |
| 3.5 | Score python-craft against absolute rubrics as a dry run (methodology Phase 4) | 3.3, 3.4 | 1 day |
| 3.6 | Extend extraction to `hogsmade` and `gruff` when access is available | 3.3 | 1 day |
| 3.7 | Publish first full portfolio report with class-aware leaderboards (methodology Phase 5) | 3.5, 3.6 | 2 days |
| 3.8 | Add devcontainer or Dockerfile for environment reproducibility | None | 2–3 hours |
| 3.9 | Baseline escape-hatch density (`# type: ignore`, `Any`, `# noqa` per KLOC) | 2.5 | 1 hour |

---

## Success metrics for re-evaluation

Re-evaluate after completing Waves 1 and 2 (target: 4 weeks from plan adoption).

| Metric | Current | Target | How to measure |
|--------|---------|--------|---------------|
| `default_branch_pr_percent` | ~9% | ≥90% | `git log --first-parent` on new commits only |
| Branch protection enabled | No | Yes (PRs + checks + review required) | GitHub API / settings page |
| CI jobs covering quality | 0 (security only) | ≥3 (lint, typecheck, test) | Workflow file count + required checks |
| Test SLOC / source SLOC | 0% | ≥5% | `find` + `wc -l` on test vs. source dirs |
| CI pass rate (30 days) | ~100% (security only) | ≥90% across all quality jobs | GitHub check-run API |
| Bus factor (50%) | 1 | ≥2 (Wave 3 target) | File ownership analysis |
| Governance dimension score | ~3 / 20 | ≥14 / 20 | Rubric from methodology |
| Quality signal dimension score | ~2 / 30 (library weight) | ≥18 / 30 | Rubric from methodology |
| Tagged releases | 0 | ≥1 | `git tag -l` |
| Dormancy state | Warming | Active | Dormancy state machine inputs |
| Scoring infrastructure exists | No | Yes (methodology Phase 0–1 complete) | Presence of `scoring_config.yml` + extraction script |
| Full portfolio report generated | No | Yes (methodology Phase 5) | Presence of report artifacts |

---

## Appendix: methodology-to-issue traceability

Each issue above maps to a specific methodology section and rubric:

| Issue | Methodology section | Rubric cell |
|-------|-------------------|------------|
| C1 | Quality signal → CI tests | Ordinal 0 (None) → target 2 (Unit/integration) |
| C2 | Governance → `default_branch_pr_percent` | <90% → target ≥90% (5 pts) |
| C3 | Quality signal → Lint/types in CI | Ordinal 1 (Config only) → target 3 (Required and passing) |
| H1 | Team resilience → bus factor | Single human at 50% threshold |
| H2 | Governance → Branch protection | 0 pts → target 3 pts |
| H3 | Governance → Reviews required | 0 pts → target 2 pts |
| M1 | Maintainability → Release/tag cadence | No releases for library-class repo |
| M2 | Governance → CODEOWNERS | 0 pts → target 2 pts |
| M3 | Quality signal → local enforcement | No pre-commit hooks |
| M4 | Quality signal → CI workflow maturity | Ordinal 1 (Exists) → target 3 (Required on default branch) |
| L1 | Maintainability → setup reproducibility | No Dockerfile or devcontainer |
| L2 | Maintainability → escape-hatch density | Not baselined |
| L3 | Delivery velocity → momentum gate | <20 commits; `n/a` per methodology |
