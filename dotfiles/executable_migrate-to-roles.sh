#!/usr/bin/env bash
# migrate-to-roles.sh
# Migrates apps/topic structure to full Ansible role structure.
# Uses local LLM for content comparison and conformance checking.
# template_dir/ is the canonical source of truth for all topics.
# Safe to re-run — skips steps that are already complete.
#
# Usage:
#   ./migrate-to-roles.sh [--dry-run] [--verbose] [topic1 topic2 ...]

set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)"
APPS_DIR="$DOTFILES_DIR/apps"
TEMPLATE_DIR="$DOTFILES_DIR/template_dir"
BACKUP_DIR="$DOTFILES_DIR/migration-backups"

DRY_RUN=false
VERBOSE=false

# System roles — same structure as topics but with additional subtasks
SYSTEM_ROLES=("homebrew" "apt" "docker")

# Files treated as remove task sources if found at topic root
REMOVE_SOURCES=("uninstall.yaml" "cleanup.yaml" "teardown.yaml" "remove.yaml")

# Extensions that belong at topic root (everything else → files/)
ROOT_EXTENSIONS=("yaml" "yml" "md" "sh" "toml" "txt" "zsh" "cfg" "conf" "ini")

# Known Ansible role dirs — never moved to files/
ROLE_DIRS=("tasks" "defaults" "vars" "files" "templates" "handlers" "meta")

# ── Model config ──────────────────────────────────────────────────────────────
CODE_MODELS=("devstral-small-2:24b" "qwen3.5:9b")
REASON_MODELS=("deepseek-r1:32b" "qwen3:30b" "phi4:14b")

# ── CLI flags ─────────────────────────────────────────────────────────────────
usage() {
  cat <<EOF
Usage: $0 [--dry-run] [--verbose] [topic1 topic2 ...]

  --dry-run   Show what would happen without making changes
  --verbose   Print each step
  topic...    Only migrate named topics (default: all)
EOF
  exit 0
}

TOPICS=()
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --verbose) VERBOSE=true ;;
    --help|-h) usage ;;
    *) TOPICS+=("$arg") ;;
  esac
done

# ── Logging ───────────────────────────────────────────────────────────────────
log()     { $VERBOSE && echo "    $*" || true; }
info()    { echo "▶ $*"; }
skip()    { echo "  ⏭  $*"; }
success() { echo "  ✅ $*"; }
warn()    { echo "  ⚠️  $*"; }
flag()    { echo "  🚩 $*"; FLAGGED_TOPICS+=("${CURRENT_TOPIC:-unknown}: $*"); }

dryrun()  { $DRY_RUN && echo "  [dry-run] $*" || true; }

llmlog() {
  if $DRY_RUN; then
    echo ""
    echo "  🤖 [LLM CALL — cost incurred if run for real]"
    echo "     reason      : $1"
    echo "     model chain : $2"
    echo ""
  else
    echo "  🤖 $1"
  fi
}

llm_dry_prompt() {
  local reason="$1" model_chain="$2" prompt="$3"
  local char_count=${#prompt}
  local token_est=$(( char_count / 4 ))
  echo "  ┌─ LLM prompt preview ───────────────────────────────────────────"
  echo "  │ reason      : $reason"
  echo "  │ model chain : $model_chain"
  echo "  │ est. tokens : ~${token_est} input"
  echo "  │ command     : llm -m ${model_chain%% *} \"<prompt>\""
  echo "  │"
  local line_count=0
  while IFS= read -r line && (( line_count < 20 )); do
    echo "  │   $line"
    (( line_count++ )) || true
  done <<< "$prompt"
  local total_lines
  total_lines=$(echo "$prompt" | wc -l)
  (( total_lines > 20 )) && echo "  │   ... (truncated — ${total_lines} lines total)"
  echo "  └────────────────────────────────────────────────────────────────"
  echo ""
}

# ── Dry-run aware fs ops ──────────────────────────────────────────────────────
fs_mkdir() { $DRY_RUN && dryrun "mkdir -p $1"  || mkdir -p "$1"; }
fs_mv()    { $DRY_RUN && dryrun "mv $1 → $2"   || mv "$1" "$2"; }
fs_cp()    { $DRY_RUN && dryrun "cp $1 → $2"   || cp "$1" "$2"; }
fs_rm()    { $DRY_RUN && dryrun "rm $1"         || rm -f "$1"; }
fs_write() { $DRY_RUN && dryrun "write $1"      || printf '%s\n' "$2" > "$1"; }

# ── Backup helper ─────────────────────────────────────────────────────────────
backup_file() {
  local src="$1" topic="$2" label="$3"
  local dest="$BACKUP_DIR/$topic/$label"
  fs_mkdir "$BACKUP_DIR/$topic"
  fs_cp "$src" "$dest"
  log "backed up $src → $dest"
}

# ── Empty file detection ──────────────────────────────────────────────────────
is_empty_file() {
  local file="$1"
  [[ ! -f "$file" ]] && return 0
  [[ ! -s "$file" ]] && return 0
  local content
  content=$(grep -v '^\s*#' "$file" | grep -v '^\s*$' || true)
  [[ -z "$content" ]]
}

# ── LLM helpers ───────────────────────────────────────────────────────────────
llm_run() {
  local -n _models=$1
  local prompt="$2"
  local reason="${3:-LLM call}"
  local model_chain
  model_chain=$(IFS=' → '; echo "${_models[*]}")

  if $DRY_RUN; then
    llm_dry_prompt "$reason" "$model_chain" "$prompt"
    echo "[dry-run placeholder]"
    return 0
  fi

  llmlog "$reason" "$model_chain"

  local output
  for model in "${_models[@]}"; do
    llmlog "trying: $model"
    if output=$(llm -m "$model" "$prompt" 2>/dev/null); then
      llmlog "✅ success: $model"
      echo "$output"
      return 0
    else
      llmlog "❌ failed: $model, trying next..."
    fi
  done

  warn "all LLM models failed for: $reason"
  return 1
}

# ── Template loader ───────────────────────────────────────────────────────────
template_content() {
  # Returns content of a template_dir file, or empty string if not found
  local rel_path="$1"
  local tpl="$TEMPLATE_DIR/$rel_path"
  [[ -f "$tpl" ]] && cat "$tpl" || echo ""
}

# ── LLM: assess file conformance against template ─────────────────────────────
llm_assess_conformance() {
  local topic="$1"
  local file_path="$2"        # actual file path
  local template_path="$3"    # relative path within template_dir
  local extra_context="${4:-}" # any extra context to pass

  local file_content template_content_str
  file_content=$(cat "$file_path" 2>/dev/null || echo "")
  template_content_str=$(template_content "$template_path")

  local prompt
  prompt="You are an Ansible expert reviewing a dotfiles repo migration.

Topic: ${topic}
File: ${file_path}

TEMPLATE (canonical structure from template_dir/${template_path}):
---
${template_content_str}
---

ACTUAL FILE:
---
${file_content}
---

${extra_context}

Assess whether the actual file conforms to the template structure and intent.
Reply EXACTLY in this format:
CONFORMANT: <yes|no|partial>
CONFIDENCE: <high|medium|low>
ISSUES: <comma-separated list of issues, or 'none'>
PRESERVE: <comma-separated list of content worth keeping from actual file, or 'none'>
ACTION: <keep|rewrite|flag-for-manual-review>
REASON: <one sentence>"

  llm_run REASON_MODELS "$prompt" "assess conformance: $file_path vs template_dir/$template_path"
}

# ── LLM: rewrite file to conform to template ─────────────────────────────────
llm_rewrite_to_template() {
  local topic="$1"
  local template_path="$2"
  local current_content="$3"
  local preserve_notes="$4"
  local file_label="$5"

  local template_content_str
  template_content_str=$(template_content "$template_path")

  local prompt
  prompt="You are an Ansible expert rewriting a dotfiles role file to match the canonical template.

Topic: ${topic}
Target file: apps/${topic}/${file_label}

TEMPLATE (apps/${topic}/${file_label} should look like this):
---
${template_content_str}
---

CURRENT FILE (may contain content worth preserving):
---
${current_content}
---

Content worth preserving from current file:
${preserve_notes}

Rewrite the file to conform to the template structure while preserving the noted content.
Replace all <topic> placeholders with: ${topic}
Output ONLY valid YAML. No markdown, no explanation, no code fences.
First line must be a comment: # apps/${topic}/${file_label}"

  llm_run CODE_MODELS "$prompt" "rewrite to template: apps/${topic}/${file_label}"
}

# ── LLM: split flat tasks into install/remove ─────────────────────────────────
llm_split_tasks() {
  local topic="$1" content="$2"

  local install_tpl remove_tpl
  install_tpl=$(template_content "tasks/install.yaml")
  remove_tpl=$(template_content "tasks/remove.yaml")

  local prompt
  prompt="You are an Ansible expert migrating a dotfiles repo.

Split the following flat Ansible task list for topic '${topic}' into separate files.

INSTALL TEMPLATE (tasks/install.yaml should look like this):
---
${install_tpl}
---

REMOVE TEMPLATE (tasks/remove.yaml should look like this):
---
${remove_tpl}
---

RULES:
1. install.yaml  — package installation tasks (brew, apt, cask, docker pull, etc.)
2. remove.yaml   — uninstall/cleanup tasks (state: absent/removed)
3. Ambiguous tasks → install.yaml with comment: # TODO: verify placement
4. Tasks belonging in a system role (brew update, apt update, etc.) → install.yaml with comment: # TODO: belongs in system role (homebrew/apt/docker)
5. Each output must be a valid YAML task list
6. Use fully qualified module names (ansible.builtin.*, community.general.*)
7. Replace any bare module names with FQCNs
8. If no tasks for a section output exactly: # EMPTY
9. First line of each must be: # apps/${topic}/tasks/install.yaml or # apps/${topic}/tasks/remove.yaml

Respond ONLY in this format (no markdown):
=== INSTALL ===
<content>
=== REMOVE ===
<content>
=== REPORT ===
<brief summary: what went where, TODOs flagged, anything needing manual review>

SOURCE TASKS:
${content}"

  llm_run CODE_MODELS "$prompt" "split tasks into install/remove: ${topic}"
}

# ── LLM: resolve conflict between two files ───────────────────────────────────
llm_resolve_conflict() {
  local file_a="$1" file_b="$2" topic="$3" template_path="$4"

  local content_a content_b template_content_str
  content_a=$(cat "$file_a")
  content_b=$(cat "$file_b")
  template_content_str=$(template_content "$template_path")

  local prompt
  prompt="You are an Ansible expert. Two files exist for the same slot in the '${topic}' role.

TEMPLATE (what the file should look like):
---
${template_content_str}
---

FILE A: ${file_a}
---
${content_a}
---

FILE B: ${file_b}
---
${content_b}
---

Which file better conforms to the template? Consider completeness, correctness, and idiomatic Ansible.
Reply EXACTLY:
PREFER: <A or B>
CONFIDENCE: <high|medium|low>
PRESERVE_FROM_LOSER: <content worth keeping from the non-preferred file, or 'none'>
REASON: <one sentence>

If confidence is low, set PREFER to MANUAL and explain in REASON."

  llm_run REASON_MODELS "$prompt" "conflict resolution: $(basename "$file_a") vs $(basename "$file_b") for $topic"
}

# ── LLM: rewrite playbook.yaml ────────────────────────────────────────────────
llm_rewrite_playbook() {
  local topic="$1" current_content="$2" preserve_notes="$3"
  llm_rewrite_to_template "$topic" "playbook.yaml" "$current_content" "$preserve_notes" "playbook.yaml"
}

# ── LLM: generate tasks/main.yaml router ─────────────────────────────────────
llm_generate_router() {
  local topic="$1"
  local is_system_role="$2"
  local existing_subtasks=("${@:3}")

  local tpl
  tpl=$(template_content "tasks/main.yaml")

  local subtask_list
  subtask_list=$(printf '%s\n' "${existing_subtasks[@]}")

  local system_note=""
  $is_system_role && system_note="This is a system role. Include bootstrap, prerequisites, and upgrade imports in addition to install and remove."

  local prompt
  prompt="Generate a tasks/main.yaml router for the Ansible role '${topic}'.

TEMPLATE:
---
${tpl}
---

Existing subtask files found: 
${subtask_list}

${system_note}

Only import subtasks that exist in the list above.
Tags: bootstrap→[bootstrap,provision], prerequisites→[prerequisites,provision], upgrade→[upgrade,provision], install→[install,provision], remove→[remove]
Replace <topic> with: ${topic}
Output ONLY valid YAML. No markdown, no explanation, no code fences.
First line: # apps/${topic}/tasks/main.yaml"

  llm_run CODE_MODELS "$prompt" "generate tasks/main.yaml router: ${topic}"
}

# ── Stub generators ───────────────────────────────────────────────────────────
playbook_stub() {
  local topic="$1"
  sed "s|<topic>|${topic}|g" "$TEMPLATE_DIR/playbook.yaml" 2>/dev/null || cat <<YAML
# apps/${topic}/playbook.yaml
- name: "Run ${topic} role standalone"
  hosts: localhost
  connection: local
  gather_facts: true
  become: false
  vars:
    homebrew_prefix: "{{ '/opt/homebrew' if ansible_facts['architecture'] == 'arm64' else '/usr/local' }}"
    user_appdir: "{{ ansible_facts['env']['HOME'] }}/Applications"
  roles:
    - role: apps/${topic}
YAML
}

tasks_main_stub() {
  local topic="$1"; shift
  local subtasks=("$@")
  local out="# apps/${topic}/tasks/main.yaml — role task router"$'\n'
  for sub in "${subtasks[@]}"; do
    case "$sub" in
      bootstrap)     out+=$'\n- name: "Import bootstrap tasks"\n  ansible.builtin.import_tasks: bootstrap.yaml\n  tags: [bootstrap, provision]\n' ;;
      prerequisites) out+=$'\n- name: "Import prerequisites tasks"\n  ansible.builtin.import_tasks: prerequisites.yaml\n  tags: [prerequisites, provision]\n' ;;
      upgrade)       out+=$'\n- name: "Import upgrade tasks"\n  ansible.builtin.import_tasks: upgrade.yaml\n  tags: [upgrade, provision]\n' ;;
      install)       out+=$'\n- name: "Import install tasks"\n  ansible.builtin.import_tasks: install.yaml\n  tags: [install, provision]\n' ;;
      remove)        out+=$'\n- name: "Import remove tasks"\n  ansible.builtin.import_tasks: remove.yaml\n  tags: [remove]\n' ;;
    esac
  done
  echo "$out"
}

file_stub()     { sed "s|<topic>|$1|g" "$TEMPLATE_DIR/tasks/${2}.yaml"     2>/dev/null || echo "# apps/$1/tasks/${2}.yaml — TODO"; }
defaults_stub() { sed "s|<topic>|$1|g" "$TEMPLATE_DIR/defaults/main.yaml"  2>/dev/null || echo "# defaults/main.yaml"; }
vars_stub()     { sed "s|<topic>|$1|g" "$TEMPLATE_DIR/vars/main.yaml"      2>/dev/null || echo "# vars/main.yaml"; }

# ── Parse LLM split output ────────────────────────────────────────────────────
parse_split_section() {
  local raw="$1" section="$2"
  echo "$raw" | awk "/^=== ${section} ===$/{found=1; next} /^=== /{found=0} found{print}"
}

parse_llm_field() {
  local raw="$1" field="$2"
  echo "$raw" | grep "^${field}:" | sed "s/^${field}: *//"
}

# ── Write migration report ────────────────────────────────────────────────────
write_report() {
  local topic="$1" content="$2"
  local dest="$BACKUP_DIR/$topic/migration-report.md"
  fs_mkdir "$BACKUP_DIR/$topic"
  fs_write "$dest" "# Migration report: ${topic}

${content}"
  log "report → $dest"
}

# ── Assess and conditionally rewrite a file ───────────────────────────────────
assess_and_rewrite() {
  local topic="$1"
  local file_path="$2"
  local template_rel="$3"
  local file_label="$4"

  [[ ! -f "$file_path" ]] && return

  local assessment
  assessment=$(llm_assess_conformance "$topic" "$file_path" "$template_rel")

  local conformant action confidence preserve
  conformant=$(parse_llm_field "$assessment" "CONFORMANT")
  action=$(parse_llm_field "$assessment" "ACTION")
  confidence=$(parse_llm_field "$assessment" "CONFIDENCE")
  preserve=$(parse_llm_field "$assessment" "PRESERVE")
  local reason
  reason=$(parse_llm_field "$assessment" "REASON")

  log "conformance: $conformant ($confidence) → action: $action"

  case "$action" in
    keep)
      success "$file_label conforms to template"
      ;;
    rewrite)
      if [[ "$confidence" == "low" ]]; then
        flag "$file_label: low-confidence rewrite needed — $reason"
        return
      fi
      local rewritten
      rewritten=$(llm_rewrite_to_template "$topic" "$template_rel" \
        "$(cat "$file_path")" "$preserve" "$file_label")
      backup_file "$file_path" "$topic" "${file_label}.bak"
      fs_write "$file_path" "$rewritten"
      success "$file_label rewritten to conform to template"
      write_report "$topic" "## ${file_label}
Action: rewrite
Reason: ${reason}
Preserved: ${preserve}"
      ;;
    flag-for-manual-review)
      flag "$file_label: needs manual review — $reason"
      write_report "$topic" "## ${file_label}
Action: MANUAL REVIEW REQUIRED
Reason: ${reason}
Preserved: ${preserve}"
      ;;
  esac
}

# ── ZSH migration ─────────────────────────────────────────────────────────────
migrate_zsh_files() {
  local dir="$1" topic="$2"
  local files_zsh="$dir/files/zsh"

  # root-level *.zsh files
  while IFS= read -r -d '' f; do
    fs_mkdir "$files_zsh"
    fs_mv "$f" "$files_zsh/$(basename "$f")"
    success "$(basename "$f") → files/zsh/"
  done < <(find "$dir" -maxdepth 1 -name "*.zsh" -print0 2>/dev/null)

  # zsh/ subdirectory
  if [[ -d "$dir/zsh" ]]; then
    fs_mkdir "$files_zsh"
    while IFS= read -r -d '' f; do
      fs_mv "$f" "$files_zsh/$(basename "$f")"
      success "zsh/$(basename "$f") → files/zsh/"
    done < <(find "$dir/zsh" -maxdepth 1 -type f -print0 2>/dev/null)
    $DRY_RUN || rmdir "$dir/zsh" 2>/dev/null || true
  fi
}

# ── Non-role file migration ───────────────────────────────────────────────────
migrate_non_role_files() {
  local dir="$1" topic="$2"

  while IFS= read -r -d '' f; do
    local base ext
    base=$(basename "$f")
    ext="${base##*.}"

    # skip known role dirs
    local skip=false
    for role_dir in "${ROLE_DIRS[@]}"; do
      [[ "$f" == "$dir/$role_dir"* ]] && skip=true && break
    done
    $skip && continue

    # skip known root-level extensions
    local keep=false
    for ok_ext in "${ROOT_EXTENSIONS[@]}"; do
      [[ "$ext" == "$ok_ext" ]] && keep=true && break
    done
    $keep && continue

    # move everything else to files/
    fs_mkdir "$dir/files"
    fs_mv "$f" "$dir/files/$base"
    success "$base → files/"

  done < <(find "$dir" -maxdepth 1 -not -type d -print0 2>/dev/null)

  # move non-yaml dirs that aren't role dirs to files/
  while IFS= read -r -d '' d; do
    local base
    base=$(basename "$d")
    local is_role_dir=false
    for role_dir in "${ROLE_DIRS[@]}"; do
      [[ "$base" == "$role_dir" ]] && is_role_dir=true && break
    done
    $is_role_dir && continue
    fs_mkdir "$dir/files"
    fs_mv "$d" "$dir/files/$base"
    success "$base/ → files/$base/"
  done < <(find "$dir" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
}

# ── Per-topic migration ────────────────────────────────────────────────────────
CURRENT_TOPIC=""

migrate_topic() {
  local topic="$1"
  local dir="$APPS_DIR/$topic"
  CURRENT_TOPIC="$topic"

  [[ -d "$dir" ]] || { warn "$topic: not found, skipping"; return; }

  info "$topic"

  local is_system_role=false
  for sys in "${SYSTEM_ROLES[@]}"; do
    [[ "$topic" == "$sys" ]] && is_system_role=true && break
  done

  local tasks_dir="$dir/tasks"
  local tasks_main="$tasks_dir/main.yaml"
  local install_yaml="$tasks_dir/install.yaml"
  local remove_yaml="$tasks_dir/remove.yaml"
  local playbook="$dir/playbook.yaml"
  local root_main="$dir/main.yaml"
  local root_tasks="$dir/tasks.yaml"

  # ── Step 1: scaffold tasks/ dir ───────────────────────────────────────────
  fs_mkdir "$tasks_dir"

  # ── Step 2: handle remove sources at root ─────────────────────────────────
  for rsrc in "${REMOVE_SOURCES[@]}"; do
    local rsrc_path="$dir/$rsrc"
    [[ -f "$rsrc_path" ]] && ! is_empty_file "$rsrc_path" || continue
    if [[ -f "$remove_yaml" ]] && ! is_empty_file "$remove_yaml"; then
      # conflict — LLM resolves
      local result
      result=$(llm_resolve_conflict "$rsrc_path" "$remove_yaml" "$topic" "tasks/remove.yaml")
      local prefer confidence preserve_loser
      prefer=$(parse_llm_field "$result" "PREFER")
      confidence=$(parse_llm_field "$result" "CONFIDENCE")
      preserve_loser=$(parse_llm_field "$result" "PRESERVE_FROM_LOSER")
      if [[ "$prefer" == "MANUAL" || "$confidence" == "low" ]]; then
        flag "remove conflict (${rsrc} vs tasks/remove.yaml) needs manual review"
        backup_file "$rsrc_path" "$topic" "${rsrc}.bak"
      elif [[ "$prefer" == "A" ]]; then
        backup_file "$remove_yaml" "$topic" "remove.yaml.bak"
        fs_mv "$rsrc_path" "$remove_yaml"
        success "$rsrc → tasks/remove.yaml (preferred by LLM)"
        [[ "$preserve_loser" != "none" ]] && write_report "$topic" \
          "## remove.yaml conflict\nPrefer: $rsrc\nPreserve from loser: $preserve_loser"
      else
        backup_file "$rsrc_path" "$topic" "${rsrc}.bak"
        success "kept existing tasks/remove.yaml ($rsrc backed up)"
      fi
    else
      fs_mv "$rsrc_path" "$remove_yaml"
      success "$rsrc → tasks/remove.yaml"
    fi
  done

  # ── Step 3: handle root tasks.yaml / main.yaml ────────────────────────────
  local source_file=""

  if [[ -f "$root_tasks" ]] && ! is_empty_file "$root_tasks" && \
     [[ -f "$root_main" ]] && ! is_empty_file "$root_main"; then
    # both exist — LLM resolves
    local result
    result=$(llm_resolve_conflict "$root_tasks" "$root_main" "$topic" "tasks/install.yaml")
    local prefer confidence preserve_loser
    prefer=$(parse_llm_field "$result" "PREFER")
    confidence=$(parse_llm_field "$result" "CONFIDENCE")
    preserve_loser=$(parse_llm_field "$result" "PRESERVE_FROM_LOSER")

    if [[ "$prefer" == "MANUAL" || "$confidence" == "low" ]]; then
      flag "tasks.yaml vs main.yaml conflict needs manual review"
      backup_file "$root_tasks" "$topic" "tasks.yaml.bak"
      backup_file "$root_main"  "$topic" "root-main.yaml.bak"
    elif [[ "$prefer" == "A" ]]; then
      source_file="$root_tasks"
      backup_file "$root_main" "$topic" "root-main.yaml.bak"
      $DRY_RUN || fs_rm "$root_main"
      [[ "$preserve_loser" != "none" ]] && write_report "$topic" \
        "## source conflict\nPrefer: tasks.yaml\nPreserve from main.yaml: $preserve_loser"
    else
      source_file="$root_main"
      backup_file "$root_tasks" "$topic" "tasks.yaml.bak"
      $DRY_RUN || fs_rm "$root_tasks"
      [[ "$preserve_loser" != "none" ]] && write_report "$topic" \
        "## source conflict\nPrefer: main.yaml\nPreserve from tasks.yaml: $preserve_loser"
    fi

  elif [[ -f "$root_tasks" ]] && ! is_empty_file "$root_tasks"; then
    source_file="$root_tasks"

  elif [[ -f "$root_main" ]] && ! is_empty_file "$root_main"; then
    source_file="$root_main"
  fi

  # ── Step 4: split source into install/remove ──────────────────────────────
  if [[ -n "$source_file" ]]; then
    local source_content
    source_content=$(cat "$source_file")
    backup_file "$source_file" "$topic" "$(basename "$source_file").bak"

    local split_output
    if split_output=$(llm_split_tasks "$topic" "$source_content"); then
      local install_content remove_content report_content
      install_content=$(parse_split_section "$split_output" "INSTALL")
      remove_content=$(parse_split_section "$split_output" "REMOVE")
      report_content=$(parse_split_section "$split_output" "REPORT")

      if [[ -n "$install_content" ]] && \
         [[ "$(echo "$install_content" | tr -d '[:space:]')" != "#EMPTY" ]]; then
        fs_write "$install_yaml" "$install_content"
        success "created tasks/install.yaml (LLM split)"
      else
        fs_write "$install_yaml" "$(file_stub "$topic" "install")"
        success "created tasks/install.yaml (empty stub)"
      fi

      if [[ ! -f "$remove_yaml" ]] || is_empty_file "$remove_yaml"; then
        if [[ -n "$remove_content" ]] && \
           [[ "$(echo "$remove_content" | tr -d '[:space:]')" != "#EMPTY" ]]; then
          fs_write "$remove_yaml" "$remove_content"
          success "created tasks/remove.yaml (LLM split)"
        else
          fs_write "$remove_yaml" "$(file_stub "$topic" "remove")"
          success "created tasks/remove.yaml (empty stub)"
        fi
      fi

      [[ -n "$report_content" ]] && write_report "$topic" "## Task split\n$report_content"
    else
      warn "LLM split failed — dumping to install.yaml, manual review needed"
      fs_write "$install_yaml" "# apps/${topic}/tasks/install.yaml
# TODO: LLM split failed — split into install/remove manually
${source_content}"
      [[ ! -f "$remove_yaml" ]] && fs_write "$remove_yaml" "$(file_stub "$topic" "remove")"
      write_report "$topic" "## Task split\n⚠️ LLM split failed. All tasks in install.yaml. Manual review required."
      flag "LLM split failed — manual split needed"
    fi

    $DRY_RUN || fs_rm "$source_file"

  else
    # no source — create stubs if needed
    [[ ! -f "$install_yaml" ]] && {
      fs_write "$install_yaml" "$(file_stub "$topic" "install")"
      success "created tasks/install.yaml (stub)"
    }
    [[ ! -f "$remove_yaml" ]] && {
      fs_write "$remove_yaml" "$(file_stub "$topic" "remove")"
      success "created tasks/remove.yaml (stub)"
    }
  fi

  # ── Step 5: assess/rewrite existing install + remove against template ──────
  [[ -f "$install_yaml" ]] && ! is_empty_file "$install_yaml" && \
    assess_and_rewrite "$topic" "$install_yaml" "tasks/install.yaml" "tasks/install.yaml"
  [[ -f "$remove_yaml" ]] && ! is_empty_file "$remove_yaml" && \
    assess_and_rewrite "$topic" "$remove_yaml" "tasks/remove.yaml" "tasks/remove.yaml"

  # ── Step 6: generate tasks/main.yaml router ───────────────────────────────
  local existing_subtasks=()
  for sub in bootstrap prerequisites upgrade install remove; do
    [[ -f "$tasks_dir/${sub}.yaml" ]] && ! is_empty_file "$tasks_dir/${sub}.yaml" && \
      existing_subtasks+=("$sub")
  done

  if [[ ! -f "$tasks_main" ]] || is_empty_file "$tasks_main"; then
    local router
    router=$(llm_generate_router "$topic" "$is_system_role" "${existing_subtasks[@]}")
    fs_write "$tasks_main" "$router"
    success "created tasks/main.yaml router"
  else
    assess_and_rewrite "$topic" "$tasks_main" "tasks/main.yaml" "tasks/main.yaml"
  fi

  # ── Step 7: handle playbook.yaml ─────────────────────────────────────────
  if [[ ! -f "$playbook" ]]; then
    fs_write "$playbook" "$(playbook_stub "$topic")"
    success "created playbook.yaml"
  else
    assess_and_rewrite "$topic" "$playbook" "playbook.yaml" "playbook.yaml"
  fi

  # ── Step 8: migrate zsh files ────────────────────────────────────────────
  migrate_zsh_files "$dir" "$topic"

  # ── Step 9: move non-role files to files/ ────────────────────────────────
  migrate_non_role_files "$dir" "$topic"

  # ── Step 10: scaffold missing dirs/stubs ─────────────────────────────────
  for d in defaults vars templates files; do
    [[ ! -d "$dir/$d" ]] && { fs_mkdir "$dir/$d"; success "created $d/"; } || skip "$d/ exists"
  done

  [[ ! -f "$dir/defaults/main.yaml" ]] && {
    fs_write "$dir/defaults/main.yaml" "$(defaults_stub "$topic")"
    success "created defaults/main.yaml"
  } || skip "defaults/main.yaml exists"

  [[ ! -f "$dir/vars/main.yaml" ]] && {
    fs_write "$dir/vars/main.yaml" "$(vars_stub "$topic")"
    success "created vars/main.yaml"
  } || skip "vars/main.yaml exists"

  echo ""
}

# ── Summary tracking ──────────────────────────────────────────────────────────
REVIEWED_TOPICS=()
SKIPPED_TOPICS=()
FLAGGED_TOPICS=()

run_topic() {
  local topic="$1"
  if [[ ! -d "$APPS_DIR/$topic" ]]; then
    SKIPPED_TOPICS+=("$topic (not found)")
    return
  fi
  REVIEWED_TOPICS+=("$topic")
  migrate_topic "$topic" || FLAGGED_TOPICS+=("$topic (error)")
}

# ── template_dir cleanup ──────────────────────────────────────────────────────
cleanup_template_dir() {
  info "template_dir cleanup"
  for f in "tasks/bootstrap.yaml" "tasks/prerequisites.yaml"; do
    local path="$TEMPLATE_DIR/$f"
    if [[ -f "$path" ]]; then
      backup_file "$path" "template_dir" "$f"
      fs_rm "$path"
      success "removed $f from template_dir (system role only)"
    fi
  done
  echo ""
}

# ── Main ──────────────────────────────────────────────────────────────────────
$DRY_RUN && echo "🔍 DRY RUN — no changes will be made" && echo ""

fs_mkdir "$BACKUP_DIR"

cleanup_template_dir

if [[ ${#TOPICS[@]} -eq 0 ]]; then
  while IFS= read -r -d '' dir; do
    run_topic "$(basename "$dir")"
  done < <(find "$APPS_DIR" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)
else
  for topic in "${TOPICS[@]}"; do
    run_topic "$topic"
  done
fi

# ── Final summary ─────────────────────────────────────────────────────────────
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "📋 Migration summary"
echo ""
echo "  Reviewed (${#REVIEWED_TOPICS[@]}):"
for t in "${REVIEWED_TOPICS[@]}"; do echo "    ✅ $t"; done

echo ""
echo "  Skipped (${#SKIPPED_TOPICS[@]}):"
for t in "${SKIPPED_TOPICS[@]}"; do echo "    ⏭  $t"; done

if [[ ${#FLAGGED_TOPICS[@]} -gt 0 ]]; then
  echo ""
  echo "  🚩 Flagged (${#FLAGGED_TOPICS[@]}):"
  for t in "${FLAGGED_TOPICS[@]}"; do echo "    ❗ $t"; done
fi

# verify all topics accounted for
ALL_TOPICS=()
while IFS= read -r -d '' dir; do
  ALL_TOPICS+=("$(basename "$dir")")
done < <(find "$APPS_DIR" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)

ACCOUNTED=("${REVIEWED_TOPICS[@]}")
for t in "${SKIPPED_TOPICS[@]}"; do ACCOUNTED+=("${t%% *}"); done

MISSED=()
for t in "${ALL_TOPICS[@]}"; do
  local found=false
  for a in "${ACCOUNTED[@]}"; do [[ "$a" == "$t" ]] && found=true && break; done
  $found || MISSED+=("$t")
done

echo ""
if [[ ${#MISSED[@]} -gt 0 ]]; then
  echo "  ❗ NOT accounted for:"
  for t in "${MISSED[@]}"; do echo "    ⚠️  $t"; done
else
  echo "  ✅ All ${#ALL_TOPICS[@]} topics in apps/ accounted for."
fi

echo ""
echo "  Backups : $BACKUP_DIR"
echo "  Cleanup : rm -rf $BACKUP_DIR"

if compgen -G "$BACKUP_DIR/*/migration-report.md" > /dev/null 2>&1; then
  echo ""
  echo "  Migration reports:"
  find "$BACKUP_DIR" -name "migration-report.md" | sort | while read -r r; do
    echo "    📄 $r"
  done
fi
echo ""