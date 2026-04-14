#!/usr/bin/env bash
# OIS discovery: git-grounded status + behind/ahead + (optional) monorepo submodule gitlink.
# Override roots with env vars if your layout differs.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

OIS_PYTHON_CRAFT_ROOT="${OIS_PYTHON_CRAFT_ROOT:-${REPO_ROOT}}"
# Monorepo root: prefer ecosystem-standard CASCADE_WORKSPACE_ROOT; OIS_CASCADE_ROOT overrides if set alone.
_DEFAULT_CASCADE="/home/caraxes/CascadeProjects"
CASCADE_WORKSPACE="${CASCADE_WORKSPACE_ROOT:-${OIS_CASCADE_ROOT:-${_DEFAULT_CASCADE}}}"
OIS_GRID_ROOT="${OIS_GRID_ROOT:-${CASCADE_WORKSPACE}/Projects/GRID-main}"
OIS_VISION_ROOT="${OIS_VISION_ROOT:-${CASCADE_WORKSPACE}/Projects/Vision}"

print_repo() {
  local R="$1"
  local label="$2"
  echo "=== ${label} ==="
  echo "path: ${R}"
  if ! git -C "${R}" rev-parse --git-dir >/dev/null 2>&1; then
    echo "(not a git repository)"
    echo
    return 0
  fi
  git -C "${R}" status -sb 2>/dev/null || true
  local upstream
  upstream="$(git -C "${R}" rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || true)"
  if [[ -n "${upstream}" ]]; then
    git -C "${R}" rev-list --left-right --count "${upstream}...HEAD" 2>/dev/null \
      | awk -v u="${upstream}" '{print "upstream:", u, "behind ahead:", $1, $2}' || true
  else
    echo "upstream: (none)"
  fi
  echo
}

echo "OIS snapshot (git-grounded). Precedence: local git > submodule gitlink > OIS Part 2.1 > dashboards."
echo "python-craft root: ${OIS_PYTHON_CRAFT_ROOT}"
echo "CascadeProjects root: ${CASCADE_WORKSPACE}  (CASCADE_WORKSPACE_ROOT=${CASCADE_WORKSPACE_ROOT:-<unset>}, OIS_CASCADE_ROOT=${OIS_CASCADE_ROOT:-<unset>})"
echo

print_repo "${CASCADE_WORKSPACE}" "CascadeProjects (hogsmade)"
print_repo "${OIS_GRID_ROOT}" "GRID-main (nested checkout)"
print_repo "${OIS_VISION_ROOT}" "Vision"
print_repo "${OIS_PYTHON_CRAFT_ROOT}" "python-craft (this repo)"

if git -C "${CASCADE_WORKSPACE}" rev-parse --git-dir >/dev/null 2>&1; then
  echo "--- Submodule gitlink (CascadeProjects) ---"
  git -C "${CASCADE_WORKSPACE}" ls-tree HEAD Projects/GRID-main 2>/dev/null || echo "(path not in HEAD tree)"
  git -C "${CASCADE_WORKSPACE}" submodule status Projects/GRID-main 2>/dev/null || true
  echo
fi

echo "Next: if behind/ahead or gitlink drift vs docs/INTEGRITY_SYNC_BATCH_ALGORITHM.md Part 2.1, refresh that table."
