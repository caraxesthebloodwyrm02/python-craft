# Ops routine — cloud, PR, CI/CD, packaging, publishing

This repo keeps **human rituals** and **GitHub Actions** aligned: predictable cadence, reproducible commands, and **posted run summaries** on the scheduled workflow (see `.github/workflows/security-audit-strict.yml`).

## Authority map (external references)

Use these as the “max signal” stack for workflow design — prefer official docs first, curated lists second, vendor patterns third.

| Layer | Source | Why it matters |
|--------|--------|----------------|
| **Role-shaped workflows** | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | Anthropic’s open Cowork plugins: same *shape* we mirror here — **manifest + commands + skills**, file-based, no infra. Useful for thinking in **roles** (security, release, repo hygiene) rather than ad-hoc tasks. |
| **Actions catalog** | [sdras/awesome-actions](https://github.com/sdras/awesome-actions) | Curated GitHub Actions patterns (setup, deploy, security). Use to pick **maintained** actions (`actions/*`, `astral-sh/*`) and avoid orphaned third-party steps. |
| **Actions hardening** | [GitHub — Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions) | `permissions: contents: read`, pinning, secret hygiene, **fork PR** behavior. |
| **Reproducible Python CI** | [Astral — Continuous integration](https://docs.astral.sh/uv/guides/integration/) | `setup-uv`, cache, `uv export` / lockfile-first installs. |
| **Supply chain** | [OpenSSF Scorecard](https://github.com/ossf/scorecard) (optional) | Periodic **policy** view on org/repo settings (branch protection, dependency review, signed releases). |
| **Python deps** | [pip-audit](https://github.com/pypa/pip-audit) + [OSV](https://google.github.io/osv-schema/) | What this repo already runs in CI; strict vs PR ignore posture is in [SECURITY_CONTINUITY.md](./SECURITY_CONTINUITY.md). |

## Role mapping (Cowork-style, for *this* repo)

No Cowork install required — this table is how **you** split recurring work:

| Plugin analogue | Repo responsibility | Primary automation |
|-----------------|---------------------|--------------------|
| **productivity** | OIS / constellation drift | `make orbit-snapshot` locally; CI cannot see private monorepo paths without a self-hosted runner. |
| **finance / legal** (risk) | Supply chain + static analysis | PR: `security-audit.yml`; weekly: `security-audit-strict.yml` + job summary. |
| **cowork-plugin-management** | Workflow + doc edits | PR review; keep this file and workflows in sync when rituals change. |

## Cadence — step by step

### Every PR and push to `main`

1. **GitHub** runs `security-audit.yml` (`uv export` → `pip-audit` with documented ignore → Bandit advisory).
2. **Human** — skim Files changed for `uv.lock`, `pyproject.toml`, `.github/workflows/*`.
3. **If lockfile changed** — run locally: `make audit` and skim [SECURITY_CONTINUITY.md](./SECURITY_CONTINUITY.md) “When to refresh”.

### Weekly (scheduled — executed + posted)

1. **GitHub** runs `security-audit-strict.yml` (Mondays **06:00 UTC** by default):
   - **Strict** `pip-audit` (no CVE ignore) → artifact `pip-audit-strict`.
   - **Bandit** (advisory) → still runs for digest even if strict audit fails; see workflow `if: always()` chain.
   - **Job summary** on the Actions run page (markdown): timestamp, links to this doc and security continuity, excerpt of the strict report when present.
2. **Human** — open the latest successful or failed run → read **Summary** → download artifact if `pip-audit` failed.
3. **Human** — if strict surfaced new CVEs: triage, patch `uv.lock` or document interim posture in `SECURITY_CONTINUITY.md`, then adjust `security-audit.yml` ignores only with justification.

### Before tagging or publishing templates

1. `make audit-strict` locally (same shape as strict CI).
2. `make orbit-snapshot` with `CASCADE_WORKSPACE_ROOT` set (if you use the four-root OIS story).
3. Confirm README / `AGENTS.md` match current Makefile and workflow names.
4. Tag → GitHub **Release** with notes pointing at strict audit artifact from a green weekly run (optional but good hygiene).

### Monthly (calendar reminder — not automated)

1. Review **Dependabot** / upstream security advisories for `torch`, `transformers`, `langchain`, `llama-cpp-python`.
2. Optional: run [OpenSSF Scorecard](https://github.com/ossf/scorecard) on the GitHub org/repo and file issues for gaps (branch protection, pinned Actions, etc.).

## Where “updates posted” appears

| Surface | What gets posted |
|---------|------------------|
| **GitHub Actions — Summary** | Weekly digest from `security-audit-strict.yml` (markdown). |
| **Artifacts** | `pip-audit-strict` (markdown) and `bandit-weekly` (text digest) from the same workflow. |
| **This doc + SECURITY_CONTINUITY** | Human-edited margin and interim CVE narrative. |

To add Slack or email: introduce a guarded step (e.g. `if: failure()`) with a repository secret and a maintained notifier action from the awesome-actions catalog; keep `permissions` minimal.

## Changing the schedule

Edit `cron` under `on.schedule` in `.github/workflows/security-audit-strict.yml`. [Cron syntax](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule) is UTC.
