# Portfolio health methodology remediation

This runbook turns the portfolio-health methodology critique into an implementation plan. It is
design-first: the original appendix and raw data were not available in this session, and the
private portfolio repos were not visible to the current Git access. Treat this as the next-run
methodology contract, not as a correction of any already-published numbers.

## Objective

Make the next portfolio health report reproducible, comparable across quarters, and less sensitive
to rank-normalization, bot noise, low-volume momentum artifacts, and repo-purpose mismatch.

The revised report should produce:

1. A raw per-repo data export.
2. A deterministic scoring script or notebook.
3. Published absolute scoring thresholds.
4. Separate human-directed delivery, automation, governance, infrastructure, and dormancy signals.
5. Class-aware leaderboards for unlike repo types.

## Stop-ship problems to fix before using the leaderboard

| Problem | Why it matters | Required change |
| --- | --- | --- |
| Cohort max-normalization creates `100/100` leaders | The top repo cannot show absolute improvement and cross-quarter comparisons drift | Replace with absolute rubrics per sub-metric |
| Raw commits inflate velocity | Dependabot, CI commit-back, and AI-assisted work have different delivery meanings | Split automation classes and score net human-directed PRs/week |
| Momentum ratio overstates tiny repos | `30d/90d = 3.0` is a ceiling when all few commits happened recently | Gate momentum behind a minimum 90-day activity volume |
| Binary CI/test heatmap is too coarse | A placeholder workflow and a robust green test suite look identical | Use ordinal infrastructure maturity and CI pass-rate evidence |
| Governance is buried | PR/branch-protection risk was a headline finding but not a headline score axis | Add Governance as a first-class dimension |
| Dormancy conflates abandoned and stable | Low commit volume can mean either no owner or healthy maintenance mode | Use a composite dormancy state machine |
| Repo purpose is ignored | Prototype, product, library, infra, and research repos should not share one weighting | Classify repos and present class-aware scores |

## Revised dimensions

Use five headline dimensions instead of four:

| Dimension | Default weight | Purpose |
| --- | ---: | --- |
| Delivery velocity | 20 | Human-directed shipping throughput |
| Quality signal | 20 | Tests, CI health, lint/typecheck enforcement |
| Maintainability | 20 | Docs, dependency hygiene, release posture, codebase shape |
| Governance | 20 | PR usage, branch protection, review/check requirements |
| Team resilience | 20 | Human ownership distribution and bus-factor risk |

Weights above are only the default for product repos. Apply class-aware weights below.

## Repo classes and weights

Class each repo before scoring. The report may still include an all-up table, but decision-making
should use the class-specific leaderboard.

| Class | Velocity | Quality | Maintainability | Governance | Team resilience | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Product | 20 | 25 | 20 | 20 | 15 | User-facing or operationally important apps |
| Library | 10 | 30 | 25 | 20 | 15 | Published or reused by other repos |
| Prototype | 30 | 15 | 15 | 10 | 30 | Experimental/internal tools; speed and owner clarity matter |
| Research | 15 | 15 | 25 | 10 | 35 | Reproducibility and ownership over throughput |
| Infra | 15 | 30 | 20 | 25 | 10 | CI/CD, deployment, shared automation, security tooling |

Classification sources, in priority order:

1. Explicit repo metadata file or appendix override.
2. Repository description and README.
3. Package/deployment signals (`pyproject.toml`, `package.json`, Dockerfile, workflows).
4. Manual reviewer override recorded in the raw CSV.

## Data model

Export one row per repo plus supporting weekly and PR tables. Minimum columns:

### `repos.csv`

| Column | Description |
| --- | --- |
| `repo` | `owner/name` |
| `default_branch` | Default branch at extraction time |
| `repo_class` | `product`, `library`, `prototype`, `research`, or `infra` |
| `last_commit_at` | Timestamp of latest default-branch commit |
| `last_release_at` | Latest tag or release timestamp, if any |
| `open_issues` | Open issues excluding PRs |
| `oldest_open_issue_days` | Age of oldest open issue |
| `has_readme` | Boolean |
| `has_lockfile` | Boolean |
| `has_dockerfile` | Boolean |
| `ci_maturity` | Ordinal described below |
| `test_maturity` | Ordinal described below |
| `lint_type_maturity` | Ordinal described below |
| `ci_pass_rate_30d` | Successful checks / total checks over 30 days |
| `branch_protection_score` | Governance rubric subtotal |
| `default_branch_pr_percent` | Percent of first-parent default-branch commits merged via PR |
| `bus_factor_50` | Smallest human set owning 50% of file/line ownership |
| `bus_factor_80` | Smallest human set owning 80% of file/line ownership |
| `dormancy_state` | `active`, `warming`, `maintenance`, `stale`, `abandoned`, `insufficient_data` |
| `score_total` | Final class-weighted score |

### `weekly_activity.csv`

| Column | Description |
| --- | --- |
| `repo` | `owner/name` |
| `week_start` | ISO week start |
| `pure_human_commits` | Commits by non-bot human authors |
| `ai_assisted_commits` | Human-prompted agent commits |
| `dependency_bot_commits` | Dependabot/Renovate/etc. |
| `ci_commit_back_commits` | Formatting, lockfile, or generated commits made by CI |
| `other_automation_commits` | Automation not otherwise classified |
| `merged_prs` | Merged PR count |
| `human_directed_prs` | Human + AI-assisted PR count |

### `pull_requests.csv`

| Column | Description |
| --- | --- |
| `repo` | `owner/name` |
| `pr_number` | PR number |
| `merged_at` | Merge timestamp |
| `author_login` | PR author |
| `automation_class` | `pure_human`, `ai_assisted`, `dependency_bot`, `ci_commit_back`, `other_automation` |
| `human_prompt_id` | Optional Devin/session/work item identifier for AI-assisted work |
| `checks_passed` | Boolean at merge time, if available |
| `review_count` | Review count before merge |
| `changed_files` | Changed files |
| `additions` | Added lines |
| `deletions` | Deleted lines |

## Automation classification

Do not collapse all non-human activity into one `bot` bucket.

| Class | Examples | Velocity weight | Rule |
| --- | --- | ---: | --- |
| Pure human | Direct author or normal PR author | `1.0` | Not matched by bot/automation rules |
| AI-assisted | Devin or other agent from a human prompt/session | `1.0` | Agent metadata ties work to a human request |
| Dependency bot | Dependabot, Renovate, security update bots | `0.1` | Login/name/email or PR labels match dependency-bot rules |
| CI commit-back | Format-on-commit, lockfile refresh, generated snapshots | `0.0` | Commit author is CI and message/path pattern is generated |
| Other automation | Scheduled scripts, sync bots | `0.2` by default | Automation without a human prompt or dependency classification |

Required implementation details:

- Keep the exact classifier regexes in the scoring repo.
- Record the matched rule in the raw data for auditability.
- For Devin work, join PRs/commits to session metadata when available and classify as
  `ai_assisted` only when a human prompt initiated the session.
- If metadata is unavailable, classify as `other_automation` and include a warning count.

## Absolute scoring rubrics

All scores should use published thresholds. Do not scale any score so that the best repo in the
portfolio automatically receives full credit.

### Delivery velocity

Headline metric: `net_human_directed_prs_per_week_12w`.

Suggested product thresholds:

| Score band | Threshold |
| --- | --- |
| 0 | No human-directed PRs in 12 weeks |
| 5 | `<0.25` PR/week |
| 10 | `0.25–0.99` PR/week |
| 15 | `1–2.49` PR/week |
| 20 | `2.5–4.99` PR/week |
| 25 | `>=5` PR/week sustained in at least 8 of 12 weeks |

Also publish raw commits, but never use gross commit count as the headline velocity number.

### Momentum

Momentum is a supporting signal, not a headline score.

Rules:

1. If total 90-day human-directed commits `<20`, set `momentum = n/a`.
2. Otherwise compute `momentum = 30d_rate / 90d_rate`.
3. Use weekly EWMA smoothing before charting.
4. Label any chart cap explicitly, e.g. `>=3.0`, rather than plotting clipped values as exact.

### Quality signal

Replace binary checks with ordinal maturity:

| Signal | Weight | 0 | 1 | 2 | 3 |
| --- | ---: | --- | --- | --- | --- |
| CI workflow | 1 | None | Exists | Runs meaningful jobs | Required on default branch |
| CI tests | 2 | None | Smoke only | Unit/integration tests | Tests plus matrix or coverage proxy |
| CI health | 3 | No data/red | `<70%` pass | `70–89%` pass | `>=90%` pass over 30d |
| Test volume ratio | 2 | None | `<5%` | `5–20%` | `>20%` test SLOC/source SLOC |
| Lint/types in CI | 2 | None | Config only | Runs in CI | Required and passing |

The report should show both the weighted score and the underlying ordinal cells.

### Maintainability

Suggested signals:

- README quality: absent, stub, setup-only, setup + operation + troubleshooting.
- Lockfile/dependency reproducibility.
- Release/tag cadence for library/product repos.
- Docker/devcontainer/setup reproducibility where relevant.
- Dependency freshness and security-audit posture.
- Escape-hatch density: `# type: ignore`, `# noqa`, `Any`, disabled lint rules per KLOC.

### Governance

Use GitHub branch protection and observed default-branch history.

| Signal | Points |
| --- | ---: |
| Branch protection enabled on default branch | 3 |
| PRs required before merge | 3 |
| Status checks required before merge | 2 |
| Reviews required before merge | 2 |
| `>=90%` of default-branch changes merged via PR | 5 |
| Merge method policy documented | 1 |
| CODEOWNERS or equivalent owner review routing | 2 |
| Stale branch / direct-push exceptions documented | 2 |

Scale the subtotal to the Governance dimension after class weighting.

### Team resilience and bus factor

Commit count alone is not a bus-factor model. Use file or line ownership.

Procedure:

1. Exclude dependency bots and CI commit-back authors.
2. Attribute files to human owners using recent meaningful touches and/or line authorship.
3. Compute the smallest contributor set whose cumulative ownership reaches 50%.
4. Also compute an 80% variant for conservative risk.
5. Publish the selected threshold and the ownership method.

Flag a repo only when a single human owns the threshold share and the repo is not explicitly a
single-owner prototype/research repo.

## Dormancy state machine

Do not label every low-commit repo as an archive candidate.

| State | Definition | Recommendation |
| --- | --- | --- |
| Active | Recent human-directed work and healthy checks | Keep normal cadence |
| Warming | Low history but clear recent work | Reassess after next reporting window |
| Maintenance | Low commits, green CI, few/no aged issues, recent release/tag or clear README status | Keep, document maintenance mode |
| Stale | No recent work plus weak CI/docs or aged issues | Create owner decision issue |
| Abandoned | No recent work, failing/no CI, aged issues, no release signal, no active owner | Archive or transfer |
| Insufficient data | Repo too small/new/private to classify | Exclude from archive recommendations |

Suggested inputs:

- Days since last human-directed commit.
- Open issue count and oldest issue age.
- CI status on default branch.
- Last tag/release age.
- Dependency/security staleness.
- Explicit repo class and owner override.

## Chart changes

1. **Score leaderboard:** show class-specific leaderboard first; all-up table second.
2. **Score dimensions:** remove cohort-max flatlines; show absolute rubrics and remaining gap to next threshold.
3. **Bot/human attribution:** stacked bars with five automation classes.
4. **PR throughput:** split `0` from `n/a (no PR workflow)` so non-PR repos are not visually treated as failed PR users.
5. **Momentum bubble:** show only repos meeting the volume gate; list low-volume repos separately.
6. **Infrastructure heatmap:** use ordinal colors (`none`, `minimal`, `partial`, `proper`) and include CI pass-rate labels.
7. **Weekly commits:** annotate large spikes with PR/merge/source context so generated dumps do not dominate interpretation.

## Reproducibility requirements

Every report run should commit or attach:

- `repos.csv`
- `weekly_activity.csv`
- `pull_requests.csv`
- `scoring_config.yml` with weights, thresholds, and classifier rules
- `score.py` or notebook that regenerates every score and chart
- `README.md` appendix explaining extraction permissions and unavailable fields
- A run log containing extraction timestamp, API scopes, and repos skipped

The next-quarter report should compare absolute metrics, not percentile ranks from the prior cohort.

## Structured implementation todos

### Phase 0 — Prepare the scoring workspace

- [ ] Choose the canonical repo for the scoring script and report appendix.
- [ ] Add `scoring_config.yml` with repo classes, weights, thresholds, and bot classifier rules.
- [ ] Add `data/raw/`, `data/processed/`, and `charts/` output directories or equivalent artifact paths.
- [ ] Document required GitHub scopes and any Devin metadata export requirements.

### Phase 1 — Extract reproducible inputs

- [ ] Export repo metadata: default branch, description, topics, README/lockfile/Dockerfile presence.
- [ ] Export commits by week for the last 90 days and last 12 weeks.
- [ ] Export merged PRs, authors, reviews, changed files, additions/deletions, and check state.
- [ ] Export branch protection for each default branch.
- [ ] Export workflow files and recent check-run conclusions for CI pass-rate calculation.
- [ ] Export issues, oldest issue age, tags, and releases.
- [ ] Join Devin session metadata where available to identify human-prompted AI-assisted work.
- [ ] Write raw CSVs before computing any scores.

### Phase 2 — Classify activity

- [ ] Implement dependency-bot detection with explicit login/name/email regexes.
- [ ] Implement CI commit-back detection from author plus message/path patterns.
- [ ] Implement AI-assisted detection from human prompt/session metadata.
- [ ] Store the matched classifier rule per commit/PR.
- [ ] Report unknown automation separately instead of folding it into human or bot totals.

### Phase 3 — Replace fragile metrics

- [ ] Replace gross commit velocity with `net_human_directed_prs_per_week_12w`.
- [ ] Apply automation weights only after preserving raw class counts.
- [ ] Gate momentum on `>=20` 90-day human-directed commits.
- [ ] Add EWMA-smoothed weekly activity for momentum charts.
- [ ] Convert CI/test/lint cells from binary to ordinal maturity.
- [ ] Add 30-day CI pass-rate.
- [ ] Add Governance as a first-class dimension.
- [ ] Compute bus factor from ownership rather than commit count.
- [ ] Replace dormancy threshold with the dormancy state machine.

### Phase 4 — Score and validate

- [ ] Score every sub-metric against absolute thresholds.
- [ ] Apply class-aware weights.
- [ ] Produce both raw and scaled dimension scores.
- [ ] Add invariant checks: no repo can score perfect velocity from bot-only work; low-volume momentum cannot chart as `3.0`.
- [ ] Add a warning when required data is unavailable rather than silently treating missing data as zero.
- [ ] Generate a diff report showing which recommendations changed under the revised rubric.

### Phase 5 — Publish the next report

- [ ] Include raw CSVs or links to artifacts.
- [ ] Include scoring formula and thresholds in the appendix.
- [ ] Include classifier rules and counts by automation class.
- [ ] Include class-specific leaderboards.
- [ ] Label stable low-activity repos as `Maintenance mode`, not archive candidates.
- [ ] Keep qualitative recommendations separate from leaderboard-driven recommendations.

## Acceptance criteria

The methodology update is ready when:

- A reviewer can regenerate all charts from one documented command.
- Every score can be traced to raw data and a published threshold.
- AI-assisted, dependency-bot, CI commit-back, and pure-human work are separated.
- Governance appears as a first-class score.
- Momentum is `n/a` for low-volume repos.
- Dormant recommendations distinguish abandoned repos from maintenance-mode repos.
- The report can be compared to the next quarter without changing interpretation when the cohort changes.
