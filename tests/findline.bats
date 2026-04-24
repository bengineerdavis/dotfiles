#!/usr/bin/env bats
# findline.bats — BATS tests for executable_findline
#
# Run from repo root:
#   .bats/bats-core/bin/bats tests/findline.bats

REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"
SCRIPT="$REPO_ROOT/bin/executable_findline"

load "$REPO_ROOT/.bats/bats-support/load"
load "$REPO_ROOT/.bats/bats-assert/load"

setup() {
    export TEST_DIR
    TEST_DIR="$(mktemp -d)"
    mkdir -p "$TEST_DIR/bin" "$TEST_DIR/src/sub"
    export PATH="$TEST_DIR/bin:$PATH"

    # Stub rg: log each argument on its own line, then emit a fake match
    export RG_ARGS_LOG="$TEST_DIR/rg_args.log"
    cat > "$TEST_DIR/bin/rg" <<'STUB'
#!/usr/bin/env bash
printf '%s\n' "$@" >> "$RG_ARGS_LOG"
printf 'path/to/file.py:10:1:def hello(): pass\n'
STUB
    chmod +x "$TEST_DIR/bin/rg"

    # Stub fzf: pass through first line of stdin (simulates selecting first result)
    cat > "$TEST_DIR/bin/fzf" <<'STUB'
#!/usr/bin/env bash
head -1
STUB
    chmod +x "$TEST_DIR/bin/fzf"

    # Stub bat: no-op so the script doesn't warn "bat not found"
    cat > "$TEST_DIR/bin/bat" <<'STUB'
#!/usr/bin/env bash
exit 0
STUB
    chmod +x "$TEST_DIR/bin/bat"

    # Stub code (VSCode): echo what it received
    cat > "$TEST_DIR/bin/code" <<'STUB'
#!/usr/bin/env bash
echo "code: $*"
STUB
    chmod +x "$TEST_DIR/bin/code"
}

teardown() {
    rm -rf "$TEST_DIR"
}

# ─── parse_arguments unit tests (source the script) ──────────────────────────

@test "parse_arguments: --files sets glob variable" {
    source "$SCRIPT"
    local subdir path_only use_vscode use_windsurf use_cursor debug args glob
    parse_arguments subdir path_only use_vscode use_windsurf use_cursor debug args glob \
        --files '**/*.py' 'hello'
    [ "$glob" = '**/*.py' ]
}

@test "parse_arguments: without --files, glob is empty" {
    source "$SCRIPT"
    local subdir path_only use_vscode use_windsurf use_cursor debug args glob
    parse_arguments subdir path_only use_vscode use_windsurf use_cursor debug args glob \
        'hello'
    [ -z "$glob" ]
}

@test "parse_arguments: --files captures glob, remaining arg goes to args" {
    source "$SCRIPT"
    local subdir path_only use_vscode use_windsurf use_cursor debug args glob
    parse_arguments subdir path_only use_vscode use_windsurf use_cursor debug args glob \
        --files '*.js' 'mypattern'
    [ "$glob" = '*.js' ]
    [ "${args[0]}" = 'mypattern' ]
}

@test "parse_arguments: --subdir and --files can be combined" {
    source "$SCRIPT"
    local subdir path_only use_vscode use_windsurf use_cursor debug args glob
    parse_arguments subdir path_only use_vscode use_windsurf use_cursor debug args glob \
        --subdir /tmp --files '**/*.py' 'hello'
    [ "$subdir" = '/tmp' ]
    [ "$glob" = '**/*.py' ]
}

@test "parse_arguments: --files after --subdir works" {
    source "$SCRIPT"
    local subdir path_only use_vscode use_windsurf use_cursor debug args glob
    parse_arguments subdir path_only use_vscode use_windsurf use_cursor debug args glob \
        --subdir /tmp --files '*.py' 'hello'
    [ "$glob" = '*.py' ]
}

# ─── integration tests: rg receives --glob ───────────────────────────────────

@test "--files passes --glob flag to rg" {
    run bash "$SCRIPT" --path-only --subdir "$TEST_DIR/src" --files '**/*.py' 'hello'
    assert_success
    run grep -Fxq -- '--glob' "$RG_ARGS_LOG"
    assert_success
}

@test "--files passes the glob value to rg" {
    run bash "$SCRIPT" --path-only --subdir "$TEST_DIR/src" --files '**/*.py' 'hello'
    assert_success
    run grep -Fxq -- '**/*.py' "$RG_ARGS_LOG"
    assert_success
}

@test "without --files, rg receives no --glob flag" {
    run bash "$SCRIPT" --path-only --subdir "$TEST_DIR/src" 'hello'
    assert_success
    run grep -Fxq -- '--glob' "$RG_ARGS_LOG"
    assert_failure
}

@test "--files works with simple *.ext glob" {
    run bash "$SCRIPT" --path-only --subdir "$TEST_DIR/src" --files '*.js' 'hello'
    assert_success
    run grep -Fxq -- '*.js' "$RG_ARGS_LOG"
    assert_success
}

@test "--files and --subdir both reach rg" {
    run bash "$SCRIPT" --path-only --subdir "$TEST_DIR/src" --files '**/*.py' 'hello'
    assert_success
    run grep -Fxq -- '--glob' "$RG_ARGS_LOG"
    assert_success
    run grep -Fxq -- "$TEST_DIR/src" "$RG_ARGS_LOG"
    assert_success
}

@test "--files before --subdir also works" {
    run bash "$SCRIPT" --path-only --files '**/*.py' --subdir "$TEST_DIR/src" 'hello'
    assert_success
    run grep -Fxq -- '--glob' "$RG_ARGS_LOG"
    assert_success
    run grep -Fxq -- '**/*.py' "$RG_ARGS_LOG"
    assert_success
}

# ─── integration tests: --path-only output ───────────────────────────────────

@test "--path-only outputs the matched file path" {
    run bash "$SCRIPT" --path-only --subdir "$TEST_DIR/src" 'hello'
    assert_success
    assert_output 'path/to/file.py'
}

@test "--path-only with --files outputs the matched file path" {
    run bash "$SCRIPT" --path-only --subdir "$TEST_DIR/src" --files '**/*.py' 'hello'
    assert_success
    assert_output 'path/to/file.py'
}

# ─── edge cases ──────────────────────────────────────────────────────────────

@test "pattern after --files is still passed to rg as search term" {
    run bash "$SCRIPT" --path-only --subdir "$TEST_DIR/src" --files '*.py' 'myterm'
    assert_success
    run grep -Fxq -- 'myterm' "$RG_ARGS_LOG"
    assert_success
}

@test "empty --files value disables glob filtering" {
    # An empty glob should not add --glob to the rg call
    source "$SCRIPT"
    local subdir path_only use_vscode use_windsurf use_cursor debug args glob
    parse_arguments subdir path_only use_vscode use_windsurf use_cursor debug args glob \
        'hello'
    [ -z "$glob" ]
}
