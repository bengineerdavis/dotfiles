#!/usr/bin/env bash
# scripts/run-shellharden.sh
# Runs shellharden over staged bash/sh scripts (default) or explicit files.
#
# Modes:
#   run-shellharden.sh              --check on staged bin|scripts shell files
#   run-shellharden.sh --fix        --replace those files in place, then restage hint
#   run-shellharden.sh --files a b  --check the named files only (agent habit:
#                                   `prek run --files`'s shellharden sibling)
#
# zsh is out of scope on purpose: shellharden is bash-strict, and its array
# quoting suggestions change zsh semantics (measured 2026-10-04: 4/85 zsh
# fragments fail, e.g. dotfiles/zsh/executable_fpath.zsh). zsh files are
# counted and skipped, never checked.
#
# The population census is deliberate: a hook that silently matches nothing
# is indistinguishable from a hook that passed (the identify selection gap
# found 2026-10-04 — every bin/executable_* was skipped by every hook).
# Empty populations are declared, not passed silently.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

mode=check
declare -a explicit_files=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fix)  mode=fix;  shift ;;
    --files)
      shift
      if [[ $# -eq 0 ]]; then
        echo "[shellharden] ERROR: --files needs at least one path" >&2
        exit 1
      fi
      explicit_files=("$@")
      break
      ;;
    *) echo "[shellharden] ERROR: unknown argument $1 (want --fix or --files <paths>)" >&2; exit 1 ;;
  esac
done

# --- Dependency ---------------------------------------------------------------
# Name the fix, not just the failure (AGENTS.md § Dependencies).
if ! command -v shellharden >/dev/null 2>&1; then
  echo "[shellharden] ERROR: shellharden is not on PATH." >&2
  echo "  fix: mise install shellharden  (topic-managed in dotfiles/apps/mise," >&2
  echo "       or run update.sh to apply the topic)" >&2
  exit 1
fi

# --- Selection ----------------------------------------------------------------
declare -a candidates=()
if [[ ${#explicit_files[@]} -gt 0 ]]; then
  candidates=("${explicit_files[@]}")
else
  mapfile -t candidates < <(
    git -C "$REPO_ROOT" diff --cached --name-only --diff-filter=ACM \
      | grep -E '^(bin|scripts)/' \
      | grep -vE '^scripts/run-(bats|shellharden)\.sh$'
  )
fi

# --- Classify: bash/sh in, zsh and everything else out ------------------------
checked=()
skipped_zsh=0
skipped_other=0

for f in "${candidates[@]}"; do
  # Staged paths are repo-relative; --files paths may be absolute.
  if [[ "$f" = /* ]]; then path="$f"; else path="$REPO_ROOT/$f"; fi
  [[ -f "$path" ]] || { skipped_other=$((skipped_other + 1)); continue; }
  shebang=$(head -1 "$path" 2>/dev/null || true)
  if [[ "$shebang" == *zsh* || "$f" == *.zsh ]]; then
    skipped_zsh=$((skipped_zsh + 1))
  elif [[ "$shebang" == *bash* || "$shebang" == *sh* || "$f" == *.sh ]]; then
    checked+=("$path")
  else
    skipped_other=$((skipped_other + 1))
  fi
done

total=${#candidates[@]}
echo "[shellharden] population: ${total} staged, ${#checked[@]} bash/sh checked, ${skipped_zsh} zsh skipped, ${skipped_other} other skipped"

if [[ ${#checked[@]} -eq 0 ]]; then
  echo "[shellharden] nothing to check (declared empty set)."
  exit 0
fi

# --- Run ----------------------------------------------------------------------
failures=0
for f in "${checked[@]}"; do
  if [[ "$mode" == fix ]]; then
    echo "[shellharden] --replace $f"
    shellharden --replace "$f"
  else
    if ! shellharden --check "$f"; then
      echo "[shellharden] FAIL: $f — quoting hardening suggested"
      echo "  fix: scripts/run-shellharden.sh --fix --files $f  (review the diff before staging)"
      failures=$((failures + 1))
    fi
  fi
done

if [[ "$mode" == fix ]]; then
  echo "[shellharden] done — ${#checked[@]} file(s) rewritten; review with git diff, then restage."
  exit 0
fi

if [[ $failures -gt 0 ]]; then
  echo "[shellharden] ${failures} of ${#checked[@]} file(s) failed --check."
  exit 1
fi
echo "[shellharden] all ${#checked[@]} checked file(s) pass."
