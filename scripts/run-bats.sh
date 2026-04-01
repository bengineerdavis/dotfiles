#!/usr/bin/env bash
# scripts/run-bats.sh
# Called by pre-commit with staged shell script paths as arguments.
# Convention: <subdir>/foo.sh → tests/foo.bats
# Covers scripts in both bin/ and scripts/.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BATS="$REPO_ROOT/.bats/bats-core/bin/bats"
TESTS_DIR="$REPO_ROOT/tests"

# missing=()
to_run=()
not_executable=()

for script in "$@"; do
  full_path="$REPO_ROOT/$script"

  # Skip files that aren't bash/sh (e.g. Python scripts in the same dirs)
  shebang=$(head -1 "$full_path" 2>/dev/null || true)
  if [[ "$shebang" != *bash* && "$shebang" != *sh* ]]; then
    echo "[bats] Skipping $script (not a bash/sh script)"
    continue
  fi

  # Check the script is executable
  if [[ ! -x "$full_path" ]]; then
    not_executable+=("$script")
  fi

  # Derive the expected test file: any/path/foo.sh → tests/foo.bats
  base=$(basename "$script" .sh)
  test_file="$TESTS_DIR/${base}.bats"

  # Commented out: missing test file is not yet a hard failure
  # if [[ ! -f "$test_file" ]]; then
  #   missing+=("$script → tests/${base}.bats")
  # else
  #   to_run+=("$test_file")
  # fi

  # Run the suite if a test file exists, silently skip if not
  if [[ -f "$test_file" ]]; then
    to_run+=("$test_file")
  else
    echo "[bats] No test file for $script (tests/${base}.bats) — skipping."
  fi
done

# Fail if any scripts are not executable
if [[ ${#not_executable[@]} -gt 0 ]]; then
  echo "[bats] ERROR: The following scripts are not executable:" >&2
  for f in "${not_executable[@]}"; do
    echo "  chmod +x $f" >&2
  done
  exit 1
fi

if [[ ${#to_run[@]} -eq 0 ]]; then
  echo "[bats] No BATS tests to run."
  exit 0
fi

# Deduplicate in case multiple staged files map to the same test
mapfile -t to_run < <(printf '%s\n' "${to_run[@]}" | sort -u)

echo "[bats] Running ${#to_run[@]} test suite(s)..."
"$BATS" "${to_run[@]}"