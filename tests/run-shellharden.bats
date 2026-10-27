#!/usr/bin/env bats
# tests/run-shellharden.bats
# Suites for scripts/run-shellharden.sh. Uses --files everywhere: the
# git-staged selection path is thin glue mirroring scripts/run-bats.sh and
# staging into the shared index from a test is not safe.

setup() {
  RUNNER="$BATS_TEST_DIRNAME/../scripts/run-shellharden.sh"
  TMP="$BATS_TEST_TMPDIR"
}

# A file shellharden --check accepts: every expansion quoted.
good_script() {
  cat > "$TMP/good.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
name="$1"
echo "hello ${name}"
EOF
}

# A file shellharden --check rejects: unquoted expansions.
bad_script() {
  cat > "$TMP/bad.sh" <<'EOF'
#!/usr/bin/env bash
name=$1
echo hello $name
EOF
}

@test "check mode passes a compliant script and declares the population" {
  good_script
  run "$RUNNER" --files "$TMP/good.sh"
  [ "$status" -eq 0 ]
  [[ "$output" == *"1 bash/sh checked, 0 zsh skipped, 0 other skipped"* ]]
  [[ "$output" == *"all 1 checked file(s) pass"* ]]
}

@test "check mode fails a non-compliant script and names it" {
  bad_script
  run "$RUNNER" --files "$TMP/bad.sh"
  [ "$status" -ne 0 ]
  [[ "$output" == *"FAIL: $TMP/bad.sh"* ]]
  [[ "$output" == *"1 of 1 file(s) failed"* ]]
}

@test "check mode skips zsh by shebang and says so" {
  cat > "$TMP/frag.zsh" <<'EOF'
#!/usr/bin/env zsh
fpath=("$1" $fpath)
EOF
  run "$RUNNER" --files "$TMP/frag.zsh"
  [ "$status" -eq 0 ]
  [[ "$output" == *"0 bash/sh checked, 1 zsh skipped"* ]]
  [[ "$output" == *"nothing to check (declared empty set)"* ]]
}

@test "zsh extension is skipped even without a zsh shebang" {
  # No shebang: still .zsh by extension — must not be checked.
  # The $1/$fpath are fixture content; they must NOT expand in this test.
  # shellcheck disable=SC2016
  printf 'fpath=($1 $fpath)\n' > "$TMP/nohash.zsh"
  run "$RUNNER" --files "$TMP/nohash.zsh"
  [ "$status" -eq 0 ]
  [[ "$output" == *"1 zsh skipped"* ]]
}

@test "empty population is declared, not passed silently" {
  printf '#!/usr/bin/env python3\nprint(1)\n' > "$TMP/prog.py"
  run "$RUNNER" --files "$TMP/prog.py"
  [ "$status" -eq 0 ]
  [[ "$output" == *"1 staged, 0 bash/sh checked, 0 zsh skipped, 1 other skipped"* ]]
  [[ "$output" == *"declared empty set"* ]]
}

@test "fix mode rewrites a non-compliant script in place" {
  bad_script
  run "$RUNNER" --fix --files "$TMP/bad.sh"
  [ "$status" -eq 0 ]
  # shellharden hardens expansion sites that word-split; an assignment RHS
  # like name=$1 does not word-split, so it legitimately stays unquoted.
  # Matching the literal fixed text: the backslash-dollar must survive
  # verbatim, so single quotes are intentional (SC2016 is a false positive
  # here — the expression must not expand).
  # shellcheck disable=SC2016
  grep -q 'echo hello "\$name"' "$TMP/bad.sh"
  # The rewritten file must now pass check mode.
  run "$RUNNER" --files "$TMP/bad.sh"
  [ "$status" -eq 0 ]
}

@test "missing shellharden fails loudly and names the fix" {
  good_script
  # /usr/bin and /bin keep the shebang's env(1) and bash itself working;
  # shellharden is deliberately absent.
  run env PATH="$TMP:/usr/bin:/bin" "$RUNNER" --files "$TMP/good.sh"
  [ "$status" -eq 1 ]
  [[ "$output" == *"shellharden is not on PATH"* ]]
  [[ "$output" == *"mise install shellharden"* ]]
}

@test "unknown argument is rejected" {
  run "$RUNNER" --nonsense
  [ "$status" -eq 1 ]
  [[ "$output" == *"unknown argument"* ]]
}

@test "--files with no paths is rejected, not a silent fallback" {
  run "$RUNNER" --files
  [ "$status" -eq 1 ]
  [[ "$output" == *"needs at least one path"* ]]
}
