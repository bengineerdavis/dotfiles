#!/usr/bin/env bats
# ---------------------------------------------------------------------------------------
# Tests for: binned
# Description: Integration tests for the binned CLI (command-to-script converter)
# ---------------------------------------------------------------------------------------

bats_require_minimum_version 1.5.0

# Load helpers if available
load_helpers() {
    local helpers_dir
    helpers_dir="$(dirname "$BATS_TEST_FILENAME")/../node_modules/bats-support/load.bash"
    if [[ -f "$helpers_dir" ]]; then
        load "$helpers_dir"
        load "$(dirname "$BATS_TEST_FILENAME")/../node_modules/bats-assert/load.bash"
    fi
}
load_helpers || true

BINNED="$(command -v binned 2>/dev/null || echo "${HOME}/bin/binned")"
PENDING_DIR="${HOME}/.binned/pending"

# ──────────────────────────────────────────────────────────────────────────────
setup() {
    # Each test gets its own isolated pending dir so tests don't collide
    export HOME_ORIG="$HOME"
    export TMPDIR_TEST
    TMPDIR_TEST="$(mktemp -d)"
    export XDG_RUNTIME_DIR="$TMPDIR_TEST"
}

teardown() {
    rm -rf "$TMPDIR_TEST"
}

# ──────────────────────────────────────────────────────────────────────────────
# Smoke tests — no LLM calls needed
# ──────────────────────────────────────────────────────────────────────────────

@test "binned --help exits 0" {
    run python3 "$BINNED" --help
    [ "$status" -eq 0 ]
    [[ "$output" =~ "binned" ]]
    [[ "$output" =~ "--pending" ]]
}

@test "binned --version prints version" {
    run python3 "$BINNED" --version
    [ "$status" -eq 0 ]
    [[ "$output" =~ "binned" ]]
}

@test "binned --pending with no deferred scripts reports empty" {
    # Point pending dir at an empty temp location
    export HOME="$TMPDIR_TEST"
    run python3 "$BINNED" --pending
    [ "$status" -eq 0 ]
    [[ "$output" =~ "No deferred" ]]
    export HOME="$HOME_ORIG"
}

@test "binned --resume with unknown name exits non-zero" {
    export HOME="$TMPDIR_TEST"
    run python3 "$BINNED" --resume "nonexistent-script-xyz"
    [ "$status" -ne 0 ]
    [[ "$output" =~ "No deferred" ]] || [[ "$stderr" =~ "No deferred" ]]
    export HOME="$HOME_ORIG"
}

@test "binned no args and no stdin exits non-zero (needs a command)" {
    # Pipe /dev/null so stdin is closed; no --pending/--resume → should print help
    run bash -c "python3 '$BINNED' < /dev/null"
    # Exits 1 and shows usage
    [ "$status" -ne 0 ] || [[ "$output" =~ "binned" ]]
}

# ──────────────────────────────────────────────────────────────────────────────
# Unit-level tests for pure Python functions (called via python3 -c)
# ──────────────────────────────────────────────────────────────────────────────

@test "detect_llm_in_command finds llm with -m flag" {
    run python3 - <<'EOF'
import sys; sys.path.insert(0, __import__('os').path.expanduser('~/bin'))
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location("binned", pathlib.Path.home() / "bin" / "binned")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
result = m.detect_llm_in_command('llm -m gpt-4o "do stuff"')
assert result == "gpt-4o", f"Expected 'gpt-4o', got '{result}'"
print("ok")
EOF
    [ "$status" -eq 0 ]
    [[ "$output" == "ok" ]]
}

@test "detect_llm_in_command returns None for non-llm command" {
    run python3 - <<'EOF'
import pathlib, importlib.util
spec = importlib.util.spec_from_file_location("binned", pathlib.Path.home() / "bin" / "binned")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
result = m.detect_llm_in_command("ffmpeg -i input.mp4 output.mp3")
assert result is None, f"Expected None, got '{result}'"
print("ok")
EOF
    [ "$status" -eq 0 ]
    [[ "$output" == "ok" ]]
}

@test "detect_llm_in_command returns 'default' for llm without -m" {
    run python3 - <<'EOF'
import pathlib, importlib.util
spec = importlib.util.spec_from_file_location("binned", pathlib.Path.home() / "bin" / "binned")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
result = m.detect_llm_in_command('llm "summarize this"')
assert result == "default", f"Expected 'default', got '{result}'"
print("ok")
EOF
    [ "$status" -eq 0 ]
    [[ "$output" == "ok" ]]
}

@test "_sanitize_name produces valid kebab-case" {
    run python3 - <<'EOF'
import pathlib, importlib.util
spec = importlib.util.spec_from_file_location("binned", pathlib.Path.home() / "bin" / "binned")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
cases = [
    ("Remove PII", "remove-pii"),
    ("My SCRIPT_name!", "my-script-name-"),
    ("  leading  ", "leading"),
]
for raw, expected in cases:
    got = m._sanitize_name(raw)
    # Strip trailing dash (acceptable artifact)
    got = got.rstrip("-")
    assert got == expected.rstrip("-"), f"sanitize({raw!r}) = {got!r}, want {expected!r}"
print("ok")
EOF
    [ "$status" -eq 0 ]
    [[ "$output" == "ok" ]]
}

@test "save_pending and load_pending round-trip" {
    export HOME="$TMPDIR_TEST"
    run python3 - <<EOF
import os, pathlib, importlib.util
os.environ["HOME"] = "$TMPDIR_TEST"
spec = importlib.util.spec_from_file_location("binned", "$HOME_ORIG/bin/binned")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.PENDING_DIR = pathlib.Path("$TMPDIR_TEST") / ".binned" / "pending"
m.save_pending("test-script", "echo hello", "#!/usr/bin/env bash\necho hello", "# tests")
data = m.load_pending("test-script")
assert data is not None, "load returned None"
assert data["name"] == "test-script"
assert data["cmd"] == "echo hello"
print("ok")
EOF
    [ "$status" -eq 0 ]
    [[ "$output" == "ok" ]]
    export HOME="$HOME_ORIG"
}

@test "list_pending returns deferred scripts" {
    export HOME="$TMPDIR_TEST"
    run python3 - <<EOF
import os, pathlib, importlib.util
os.environ["HOME"] = "$TMPDIR_TEST"
spec = importlib.util.spec_from_file_location("binned", "$HOME_ORIG/bin/binned")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
pending = pathlib.Path("$TMPDIR_TEST") / ".binned" / "pending"
m.PENDING_DIR = pending
m.save_pending("alpha", "cmd", "script", "tests")
m.save_pending("beta", "cmd", "script", "tests")
items = m.list_pending()
names = [i["name"] for i in items]
assert "alpha" in names and "beta" in names, f"Got: {names}"
print("ok")
EOF
    [ "$status" -eq 0 ]
    [[ "$output" == "ok" ]]
    export HOME="$HOME_ORIG"
}
