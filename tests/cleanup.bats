#!/usr/bin/env bats
# cleanup.bats — BATS tests for cleanup.sh
# Submodule-based setup — no system bats-core install required.
#
# Run from repo root:
#   .bats/bats-core/bin/bats tests/cleanup.bats

# Resolve repo root regardless of where bats is invoked from
REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"

load "$REPO_ROOT/.bats/bats-support/load"
load "$REPO_ROOT/.bats/bats-assert/load"

setup() {
  # Temp home so we never touch real Desktop/Downloads
  export HOME="$(mktemp -d)"
  mkdir -p "$HOME/Desktop" "$HOME/Downloads"

  # Point to the script under test
  SCRIPT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)/cleanup.sh"

  # Stub tp: succeeds and logs what it received
  export TP_LOG="$HOME/tp.log"
  export PATH="$HOME/bin:$PATH"
  mkdir -p "$HOME/bin"
  cat > "$HOME/bin/tp" <<'EOF'
#!/usr/bin/env bash
echo "tp called with: $*" >> "$TP_LOG"
exit 0
EOF
  chmod +x "$HOME/bin/tp"
}

teardown() {
  rm -rf "$HOME"
}

# ── Existence checks ────────────────────────────────────────────────────────

@test "exits 1 and prints install hint when tp is not in PATH" {
  # Shadow tp with nothing
  export PATH="/usr/bin:/bin"
  run bash "$SCRIPT"
  [ "$status" -eq 1 ]
  [[ "$output" == *"trash-put (tp) not found"* ]]
  [[ "$output" == *"brew install trash-cli"* ]]
}

# ── Empty directories ────────────────────────────────────────────────────────

@test "reports no screenshots when Desktop has none" {
  run bash "$SCRIPT"
  [ "$status" -eq 0 ]
  [[ "$output" == *"No screenshots to trash."* ]]
}

@test "reports no downloads when Downloads is empty" {
  run bash "$SCRIPT"
  [ "$status" -eq 0 ]
  [[ "$output" == *"No downloads to trash."* ]]
}

@test "tp is never called when both directories are empty" {
  run bash "$SCRIPT"
  [ ! -f "$TP_LOG" ]
}

# ── Files present ────────────────────────────────────────────────────────────

@test "trashes screenshot files matching the glob" {
  touch "$HOME/Desktop/Screenshot 2025-01-01.png"
  touch "$HOME/Desktop/Screenshot 2025-01-02.png"
  run bash "$SCRIPT"
  [ "$status" -eq 0 ]
  [[ "$output" == *"Trashing 2 screenshots"* ]]
  [[ "$output" == *"Done — screenshots sent to Trash."* ]]
}

@test "trashes all files in Downloads" {
  touch "$HOME/Downloads/file1.zip"
  touch "$HOME/Downloads/file2.pdf"
  run bash "$SCRIPT"
  [ "$status" -eq 0 ]
  [[ "$output" == *"Trashing 2 downloads"* ]]
  [[ "$output" == *"Done — downloads sent to Trash."* ]]
}

@test "non-screenshot files on Desktop are not trashed" {
  touch "$HOME/Desktop/notes.txt"
  run bash "$SCRIPT"
  [ "$status" -eq 0 ]
  [[ "$output" == *"No screenshots to trash."* ]]
  # tp should still be called for Downloads glob if empty too — it shouldn't
  [ ! -f "$TP_LOG" ]
}

@test "passes correct file paths to tp" {
  touch "$HOME/Desktop/Screenshot 2025-03-01.png"
  run bash "$SCRIPT"
  grep -q "Screenshot 2025-03-01.png" "$TP_LOG"
}

# ── tp failure ───────────────────────────────────────────────────────────────

@test "reports error and exits non-zero when tp fails" {
  # Override stub with a failing one
  cat > "$HOME/bin/tp" <<'EOF'
#!/usr/bin/env bash
exit 2
EOF
  touch "$HOME/Desktop/Screenshot 2025-01-01.png"
  run bash "$SCRIPT"
  [ "$status" -ne 0 ]
  [[ "$output" == *"ERROR: failed to trash screenshots"* ]]
}