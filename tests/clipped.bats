#!/usr/bin/env bats

# ------------------------------------------------------------------------------
# clipped test suite
#
# Requires: bats-core
#   brew install bats-core        # macOS
#   sudo apt install bats         # Ubuntu/Debian
#
# Run:
#   bats tests/clipped.bats
# ------------------------------------------------------------------------------

setup() {
    export TEST_TMPDIR
    TEST_TMPDIR="$(mktemp -d)"
    export TMPDIR="$TEST_TMPDIR"
    export CLIPPED="$BATS_TEST_DIRNAME/../clipped"
    export PATH="$TEST_TMPDIR:$PATH"

    # Fake pbpaste: always returns a known string
    cat > "$TEST_TMPDIR/pbpaste" << 'SH'
#!/usr/bin/env bash
printf '%s' "clipboard-content"
SH
    chmod +x "$TEST_TMPDIR/pbpaste"

    # Fake pbcopy: captures stdin to a file we can inspect
    cat > "$TEST_TMPDIR/pbcopy" << 'SH'
#!/usr/bin/env bash
cat > "${TMPDIR:-/tmp}/clipped-copy-capture"
SH
    chmod +x "$TEST_TMPDIR/pbcopy"

    # Fake uname: reports Darwin so OS detection is deterministic
    cat > "$TEST_TMPDIR/uname" << 'SH'
#!/usr/bin/env bash
printf '%s\n' Darwin
SH
    chmod +x "$TEST_TMPDIR/uname"

    # Sample files for file-arg tests
    printf 'file one content' > "$TEST_TMPDIR/file1.txt"
    printf 'file two content' > "$TEST_TMPDIR/file2.txt"
}

teardown() {
    rm -rf "$TEST_TMPDIR"
}

# Helper: run clipped in a subprocess that preserves the mocked PATH
run_clipped() {
    run bash -c "export PATH='$TEST_TMPDIR:$PATH'; export TMPDIR='$TEST_TMPDIR'; $CLIPPED $*"
}

# Helper: read the copy-capture file after a copy operation
captured() {
    cat "$TEST_TMPDIR/clipped-copy-capture" 2>/dev/null || echo ""
}

# ------------------------------------------------------------------------------
# Help and version
# ------------------------------------------------------------------------------

@test "--help exits 0 and documents auto mode" {
    run_clipped --help
    [ "$status" -eq 0 ]
    [[ "$output" == *"Auto mode"* ]]
    [[ "$output" == *"stdin is piped"* ]]
    [[ "$output" == *"stdin is a TTY"* ]]
}

@test "-h exits 0" {
    run_clipped -h
    [ "$status" -eq 0 ]
}

@test "help exits 0" {
    run_clipped help
    [ "$status" -eq 0 ]
}

@test "--version exits 0 and shows version string" {
    run_clipped --version
    [ "$status" -eq 0 ]
    [[ "$output" == *"clipped version 1.2.0"* ]]
}

# ------------------------------------------------------------------------------
# Explicit paste
# ------------------------------------------------------------------------------

@test "paste outputs clipboard contents" {
    run bash -c "export PATH='$TEST_TMPDIR:$PATH'; $CLIPPED paste"
    [ "$status" -eq 0 ]
    [ "$output" = "clipboard-content" ]
}

@test "p outputs clipboard contents" {
    run bash -c "export PATH='$TEST_TMPDIR:$PATH'; $CLIPPED p"
    [ "$status" -eq 0 ]
    [ "$output" = "clipboard-content" ]
}

# ------------------------------------------------------------------------------
# Explicit copy — stdin
# ------------------------------------------------------------------------------

@test "copy reads stdin and copies it" {
    run bash -c "export PATH='$TEST_TMPDIR:$PATH'; export TMPDIR='$TEST_TMPDIR'; printf 'hello clipboard' | $CLIPPED copy"
    [ "$status" -eq 0 ]
    [ "$(captured)" = "hello clipboard" ]
}

@test "c reads stdin and copies it" {
    run bash -c "export PATH='$TEST_TMPDIR:$PATH'; export TMPDIR='$TEST_TMPDIR'; printf 'short copy' | $CLIPPED c"
    [ "$status" -eq 0 ]
    [ "$(captured)" = "short copy" ]
}

@test "copy without stdin fails with guidance" {
    run script -qec "env PATH='$TEST_TMPDIR:$PATH' TMPDIR='$TEST_TMPDIR' $CLIPPED copy" /dev/null
    [ "$status" -ne 0 ]
    [[ "$output" == *"copy mode expects stdin"* ]]
    [[ "$output" == *"clipped c README.md"* ]]
}

# ------------------------------------------------------------------------------
# Explicit copy — file arguments
# ------------------------------------------------------------------------------

@test "c with a single file copies its contents" {
    run bash -c "export PATH='$TEST_TMPDIR:$PATH'; export TMPDIR='$TEST_TMPDIR'; $CLIPPED c '$TEST_TMPDIR/file1.txt'"
    [ "$status" -eq 0 ]
    [ "$(captured)" = "file one content" ]
}

@test "c with multiple files concatenates and copies" {
    run bash -c "export PATH='$TEST_TMPDIR:$PATH'; export TMPDIR='$TEST_TMPDIR'; $CLIPPED c '$TEST_TMPDIR/file1.txt' '$TEST_TMPDIR/file2.txt'"
    [ "$status" -eq 0 ]
    [ "$(captured)" = "file one contentfile two content" ]
}

@test "copy with a single file copies its contents" {
    run bash -c "export PATH='$TEST_TMPDIR:$PATH'; export TMPDIR='$TEST_TMPDIR'; $CLIPPED copy '$TEST_TMPDIR/file1.txt'"
    [ "$status" -eq 0 ]
    [ "$(captured)" = "file one content" ]
}

@test "c with a nonexistent file exits nonzero" {
    run bash -c "export PATH='$TEST_TMPDIR:$PATH'; export TMPDIR='$TEST_TMPDIR'; $CLIPPED c /nonexistent/file.txt"
    [ "$status" -ne 0 ]
}

# ------------------------------------------------------------------------------
# Auto mode — no arguments
# ------------------------------------------------------------------------------

@test "auto mode with piped stdin copies it" {
    run bash -c "export PATH='$TEST_TMPDIR:$PATH'; export TMPDIR='$TEST_TMPDIR'; printf 'auto copied' | $CLIPPED"
    [ "$status" -eq 0 ]
    [ "$(captured)" = "auto copied" ]
}

@test "auto mode with TTY pastes clipboard" {
    run script -qec "env PATH='$TEST_TMPDIR:$PATH' TMPDIR='$TEST_TMPDIR' $CLIPPED" /dev/null
    [ "$status" -eq 0 ]
    [[ "$output" == *"clipboard-content"* ]]
}

# ------------------------------------------------------------------------------
# Error handling
# ------------------------------------------------------------------------------

@test "unknown command exits 1 with usage hint" {
    run_clipped wat
    [ "$status" -eq 1 ]
    [[ "$output" == *"Unknown command 'wat'"* ]]
    [[ "$output" == *"clipped [copy|paste|--help|--version]"* ]]
}

@test "unknown command output mentions default auto behavior" {
    run_clipped wat
    [ "$status" -eq 1 ]
    [[ "$output" == *"Auto: copy stdin, or paste if no stdin"* ]]
}
