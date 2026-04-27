#!/usr/bin/env bash
# scripts/run-bats.sh
# Runs BATS suites for staged shell scripts in bin/ and scripts/.
# Convention: <subdir>/foo.sh → tests/foo.bats
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BATS="$REPO_ROOT/.bats/bats-core/bin/bats"
TESTS_DIR="$REPO_ROOT/tests"

# --- Helpers -----------------------------------------------------------------

log()  { echo "[bats] $*"; }
err()  { echo "[bats] ERROR: $*" >&2; }
skip() { log "Skipping $1 — $2."; }

is_shell_script() {
  local shebang
  shebang=$(head -1 "$REPO_ROOT/$1" 2>/dev/null || true)
  [[ "$shebang" == *bash* || "$shebang" == *sh* ]]
}

is_chezmoi_managed() { [[ $(basename "$1") == executable_* ]]; }

test_file_for()  { echo "$TESTS_DIR/$(basename "${1%.sh}").bats"; }

# --- Staged files ------------------------------------------------------------

mapfile -t staged < <(
  git -C "$REPO_ROOT" diff --cached --name-only --diff-filter=ACM \
    | grep -E '^(bin|scripts)/[^/]+\.sh$' \
    | grep -vE '^scripts/run-(bats|shellharden)\.sh$'
)

[[ ${#staged[@]} -gt 0 ]] || { log "No staged shell scripts to test."; exit 0; }

# --- Process each staged script ----------------------------------------------

not_executable=()
to_run=()

for script in "${staged[@]}"; do
  is_shell_script "$script"    || { skip "$script" "not a bash/sh script";  continue; }
  is_chezmoi_managed "$script" || [[ -x "$REPO_ROOT/$script" ]] || not_executable+=("$script")

  test_file=$(test_file_for "$script")
  if [[ -f "$test_file" ]]; then
    to_run+=("$test_file")
  else
    skip "$script" "no test file found ($(basename "$test_file"))"
  fi
done

# --- Gate on executable check ------------------------------------------------

if [[ ${#not_executable[@]} -gt 0 ]]; then
  err "The following scripts are not executable:"
  printf '  chmod +x %s\n' "${not_executable[@]}" >&2
  exit 1
fi

# --- Run ---------------------------------------------------------------------

[[ ${#to_run[@]} -gt 0 ]] || { log "No BATS suites to run."; exit 0; }

mapfile -t to_run < <(printf '%s\n' "${to_run[@]}" | sort -u)

log "Running ${#to_run[@]} suite(s):"
printf '  → %s\n' "${to_run[@]}"

"$BATS" --print-output-on-failure "${to_run[@]}"