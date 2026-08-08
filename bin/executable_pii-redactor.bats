#!/usr/bin/env bats
# Tests for pii-redactor

SCRIPT="$BATS_TEST_DIRNAME/pii-redactor"
# Disable thinking mode for Qwen3 models so integration tests are fast
INTEGRATION_LLM_OPTS="-o think false"

# ── unit tests (mocked llm) ───────────────────────────────────────────────

setup() {
  REAL_PATH="$PATH"
  MOCK_DIR="$(mktemp -d)"
  export PATH="$MOCK_DIR:$PATH"
  # Default mock: echo stdin back so callers can inspect piped content
  cat > "$MOCK_DIR/llm" <<'EOF'
#!/usr/bin/env bash
cat
EOF
  chmod +x "$MOCK_DIR/llm"
}

teardown() {
  export PATH="$REAL_PATH"
  rm -rf "$MOCK_DIR"
}

@test "help flag prints usage and exits 0" {
  run "$SCRIPT" --help
  [ "$status" -eq 0 ]
  [[ "$output" == *"Usage:"* ]]
  [[ "$output" == *"--input"* ]]
}

@test "short help flag -h works" {
  run "$SCRIPT" -h
  [ "$status" -eq 0 ]
  [[ "$output" == *"Usage:"* ]]
}

@test "unknown flag exits non-zero with error message" {
  run "$SCRIPT" --bogus-flag
  [ "$status" -ne 0 ]
  [[ "$output" == *"Unknown option"* ]]
}

@test "--input flag missing argument exits non-zero" {
  run "$SCRIPT" --input
  [ "$status" -ne 0 ]
}

@test "--model flag missing argument exits non-zero" {
  run "$SCRIPT" --model
  [ "$status" -ne 0 ]
}

@test "missing input file exits non-zero with error" {
  run "$SCRIPT" -i /nonexistent/path/file.txt
  [ "$status" -ne 0 ]
  [[ "$output" == *"not found"* ]]
}

@test "dry-run with input file prints action to stderr and exits 0" {
  local tmp
  tmp="$(mktemp)"
  echo "Hello John Doe" > "$tmp"
  run "$SCRIPT" --dry-run -i "$tmp"
  [ "$status" -eq 0 ]
  [[ "$output" == *"Would process"* ]]
  rm -f "$tmp"
}

@test "dry-run stdin prints action to stderr and exits 0" {
  run bash -c "echo 'test' | '$SCRIPT' --dry-run"
  [ "$status" -eq 0 ]
  [[ "$output" == *"Would process stdin"* ]]
}

@test "verbose flag emits debug output" {
  local tmp
  tmp="$(mktemp)"
  echo "content" > "$tmp"
  run bash -c "'$SCRIPT' -v --dry-run -i '$tmp' 2>&1"
  [ "$status" -eq 0 ]
  [[ "$output" == *"Processing file"* ]]
  rm -f "$tmp"
}

@test "passes -m model argument through to llm" {
  cat > "$MOCK_DIR/llm" <<'EOF'
#!/usr/bin/env bash
echo "ARGS: $*"
EOF
  chmod +x "$MOCK_DIR/llm"

  local tmp
  tmp="$(mktemp)"
  echo "hello" > "$tmp"
  run "$SCRIPT" -i "$tmp" -m my-custom-model
  [ "$status" -eq 0 ]
  [[ "$output" == *"my-custom-model"* ]]
  rm -f "$tmp"
}

@test "passes -s system flag (not -p) to llm" {
  cat > "$MOCK_DIR/llm" <<'EOF'
#!/usr/bin/env bash
echo "ARGS: $*"
EOF
  chmod +x "$MOCK_DIR/llm"

  local tmp
  tmp="$(mktemp)"
  echo "hello" > "$tmp"
  run "$SCRIPT" -i "$tmp"
  [ "$status" -eq 0 ]
  [[ "$output" == *" -s "* ]]
  [[ "$output" != *" -p "* ]]
  rm -f "$tmp"
}

@test "passes -n no-log flag to llm" {
  cat > "$MOCK_DIR/llm" <<'EOF'
#!/usr/bin/env bash
echo "ARGS: $*"
EOF
  chmod +x "$MOCK_DIR/llm"

  local tmp
  tmp="$(mktemp)"
  echo "hello" > "$tmp"
  run "$SCRIPT" -i "$tmp"
  [ "$status" -eq 0 ]
  [[ "$output" == *" -n"* ]]
  rm -f "$tmp"
}

@test "output is written to file when -o is specified" {
  local tmp_in tmp_out
  tmp_in="$(mktemp)"
  tmp_out="$(mktemp)"
  echo "Hello World" > "$tmp_in"
  run "$SCRIPT" -i "$tmp_in" -o "$tmp_out"
  [ "$status" -eq 0 ]
  [ -s "$tmp_out" ]
  rm -f "$tmp_in" "$tmp_out"
}

@test "bare -o templates the output name off the input file" {
  local tmp_dir
  tmp_dir="$(mktemp -d)"
  echo "Hello World" > "$tmp_dir/mail.md"
  run "$SCRIPT" -i "$tmp_dir/mail.md" -o
  [ "$status" -eq 0 ]
  [ -s "$tmp_dir/mail-pii-removed.md" ]
  rm -rf "$tmp_dir"
}

@test "bare -o keeps templating when -o precedes -i" {
  local tmp_dir
  tmp_dir="$(mktemp -d)"
  echo "Hello World" > "$tmp_dir/mail.md"
  run "$SCRIPT" -o -i "$tmp_dir/mail.md"
  [ "$status" -eq 0 ]
  [ -s "$tmp_dir/mail-pii-removed.md" ]
  rm -rf "$tmp_dir"
}

@test "bare -o on an extensionless input appends the suffix" {
  local tmp_dir
  tmp_dir="$(mktemp -d)"
  echo "Hello World" > "$tmp_dir/mail"
  run "$SCRIPT" -i "$tmp_dir/mail" -o
  [ "$status" -eq 0 ]
  [ -s "$tmp_dir/mail-pii-removed" ]
  rm -rf "$tmp_dir"
}

@test "bare -o with stdin input falls back to a fixed name" {
  local tmp_dir
  tmp_dir="$(mktemp -d)"
  run bash -c "cd '$tmp_dir' && echo 'Hello World' | '$SCRIPT' -o"
  [ "$status" -eq 0 ]
  [ -s "$tmp_dir/stdin-pii-removed.md" ]
  rm -rf "$tmp_dir"
}

@test "explicit -o argument still wins over the template" {
  local tmp_dir
  tmp_dir="$(mktemp -d)"
  echo "Hello World" > "$tmp_dir/mail.md"
  run "$SCRIPT" -i "$tmp_dir/mail.md" -o "$tmp_dir/custom.md"
  [ "$status" -eq 0 ]
  [ -s "$tmp_dir/custom.md" ]
  [ ! -e "$tmp_dir/mail-pii-removed.md" ]
  rm -rf "$tmp_dir"
}

@test "a failing llm leaves no output file behind" {
  cat > "$MOCK_DIR/llm" <<'EOF'
#!/usr/bin/env bash
echo "partial output"
exit 1
EOF
  chmod +x "$MOCK_DIR/llm"

  local tmp_dir
  tmp_dir="$(mktemp -d)"
  echo "Hello World" > "$tmp_dir/mail.md"
  run "$SCRIPT" -i "$tmp_dir/mail.md" -o "$tmp_dir/out.md"
  [ "$status" -ne 0 ]
  [ ! -e "$tmp_dir/out.md" ]
  # and no staging file left lying around
  [ -z "$(find "$tmp_dir" -name 'out.md.*' -print -quit)" ]
  rm -rf "$tmp_dir"
}

@test "a failing llm does not clobber a pre-existing output file" {
  cat > "$MOCK_DIR/llm" <<'EOF'
#!/usr/bin/env bash
exit 1
EOF
  chmod +x "$MOCK_DIR/llm"

  local tmp_dir
  tmp_dir="$(mktemp -d)"
  echo "Hello World" > "$tmp_dir/mail.md"
  echo "PREVIOUS GOOD OUTPUT" > "$tmp_dir/out.md"
  run "$SCRIPT" -i "$tmp_dir/mail.md" -o "$tmp_dir/out.md"
  [ "$status" -ne 0 ]
  [[ "$(cat "$tmp_dir/out.md")" == "PREVIOUS GOOD OUTPUT" ]]
  rm -rf "$tmp_dir"
}

@test "output file honours the umask rather than mktemp's 0600" {
  local tmp_dir
  tmp_dir="$(mktemp -d)"
  echo "Hello World" > "$tmp_dir/mail.md"
  run bash -c "umask 022 && '$SCRIPT' -i '$tmp_dir/mail.md' -o '$tmp_dir/out.md'"
  [ "$status" -eq 0 ]
  # GNU coreutils stat and BSD stat disagree on flags; try both.
  local mode
  mode="$(stat -c '%a' "$tmp_dir/out.md" 2>/dev/null || stat -f '%Lp' "$tmp_dir/out.md")"
  [[ "$mode" == "644" ]]
  rm -rf "$tmp_dir"
}

@test "PYMUPDF_MESSAGE is set so plugin chatter stays off stdout" {
  cat > "$MOCK_DIR/llm" <<'EOF'
#!/usr/bin/env bash
echo "PYMUPDF_MESSAGE=${PYMUPDF_MESSAGE:-unset}"
EOF
  chmod +x "$MOCK_DIR/llm"

  local tmp
  tmp="$(mktemp)"
  echo "hello" > "$tmp"
  run "$SCRIPT" -i "$tmp"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PYMUPDF_MESSAGE=fd:2"* ]]
  rm -f "$tmp"
}

@test "stdin input is processed when no -i flag given" {
  run bash -c "echo 'my name is Alice' | '$SCRIPT'"
  [ "$status" -eq 0 ]
}

@test "LLM_EXTRA_OPTS is forwarded to llm" {
  cat > "$MOCK_DIR/llm" <<'EOF'
#!/usr/bin/env bash
echo "ARGS: $*"
EOF
  chmod +x "$MOCK_DIR/llm"

  local tmp
  tmp="$(mktemp)"
  echo "hello" > "$tmp"
  run env LLM_EXTRA_OPTS="-o think false" "$SCRIPT" -i "$tmp"
  [ "$status" -eq 0 ]
  [[ "$output" == *"think"* ]]
  [[ "$output" == *"false"* ]]
  rm -f "$tmp"
}

# ── integration tests (real llm, local Ollama model) ─────────────────────
# Uses a small local model with thinking disabled for speed.

@test "integration: redacts email address from stdin" {
  export PATH="$REAL_PATH"

  local input="Please contact support at john.doe@example.com for help."
  local output
  output=$(echo "$input" | LLM_EXTRA_OPTS="$INTEGRATION_LLM_OPTS" "$SCRIPT" -m qwen3.5:4b-mlx-bf16)

  [[ "$output" != *"john.doe@example.com"* ]]
  [[ "$output" == *"["* ]]
}

@test "integration: redacts name and phone from file" {
  export PATH="$REAL_PATH"

  local tmp_in tmp_out
  tmp_in="$(mktemp)"
  tmp_out="$(mktemp)"

  cat > "$tmp_in" <<'EOF'
Hi, my name is Jane Smith and you can reach me at 555-867-5309.
I live at 123 Maple Street, Springfield.
EOF

  LLM_EXTRA_OPTS="$INTEGRATION_LLM_OPTS" run "$SCRIPT" -i "$tmp_in" -o "$tmp_out" -m qwen3.5:4b-mlx-bf16
  [ "$status" -eq 0 ]

  local result
  result=$(cat "$tmp_out")
  [[ "$result" != *"Jane Smith"* ]]
  [[ "$result" != *"555-867-5309"* ]]
  [[ "$result" == *"["* ]]

  rm -f "$tmp_in" "$tmp_out"
}
