#!/usr/bin/env bash
set -euo pipefail

# Usage: update.sh [full|minimal]
#   full     upgrade apps AND heavy attachments (ollama models, large data)
#   minimal  upgrade apps only
#   (omit)   use your saved default; first run prompts and saves it
#
# ansible is mise-managed; `mise exec` guarantees it's on PATH.

here="$(cd "$(dirname "$0")" && pwd)"
# The pre-commit hook runs shellcheck without -x, so it cannot follow the
# source; profile.sh is linted on its own.
# shellcheck source=bootstrap/profile.sh disable=SC1091
. "$here/bootstrap/profile.sh"

# Resolve minimal/full (precedence: arg > saved default > first-run prompt /
# minimal). Passed to ansible as a tag; attachment tasks gate on it via
# ansible_run_tags (see playbook.yaml post_tasks).
profile="$(resolve_profile "${1:-}")"
echo "› upgrade profile: ${profile}" >&2

# Ask-first skill resolution. The playbook's approved-sources guard only fails
# at the very END of the run; if an unexpected skill already sits in the store,
# offer the interactive resolver NOW, while a terminal answers. Decisions land
# in ~/.config/skill-trust/trust.yaml and the guard honours them. Unresolved
# findings never block here — the guard stays the enforcement of record. The
# rules file is composed by the guard each run, so on the first run ever (or
# after the approved-sources list changed) this probe can lag one run; the
# guard's failure message names `skill-trust resolve` in that case. The
# dotagents inventory command mirrors guard_dotagents_list_cmd in
# roles/guards/defaults/main.yaml.
rules="${XDG_CONFIG_HOME:-$HOME/.config}/skill-trust/rules.yaml"
skills_dir="$HOME/.agents/skills"
export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$PATH"
if command -v skill-trust >/dev/null 2>&1 && [ -f "$rules" ] && [ -d "$skills_dir" ]; then
  # The inventory goes to a FILE, not a pipe: resolve prompts on stdin, and
  # piping the inventory in would take the terminal away with it.
  # Explicit X-template: `mktemp -t prefix` needs X's appended on GNU and is
  # a different flag shape on BSD; the long form is identical on both.
  inventory_file="$(mktemp "${TMPDIR:-/tmp}/skill-trust-inventory.XXXXXXXX")"
  if npx -y @sentry/dotagents@latest --user list --json >"$inventory_file" 2>/dev/null; then
    rc=0
    skill-trust --offline --config "$rules" audit \
      --skills-dir "$skills_dir" --declared-json "$inventory_file" >/dev/null 2>&1 || rc=$?
    if [ "$rc" -eq 1 ]; then
      if [ -t 0 ]; then
        echo "› unexpected skills detected — resolving interactively" >&2
        resolve_rc=0
        skill-trust --offline --config "$rules" resolve \
          --skills-dir "$skills_dir" --declared-json "$inventory_file" || resolve_rc=$?
        if [ "$resolve_rc" -ne 0 ]; then
          echo "› findings remain unresolved; the play's guard will report them" >&2
        fi
      else
        echo "› unexpected skills detected, no terminal to resolve them — run \`skill-trust resolve\`" >&2
      fi
    fi
  fi
  rm -f "$inventory_file"
fi

# Upgrade ansible FIRST, out-of-band, before it becomes the controller for the
# playbook below. ansible cannot safely upgrade itself mid-run (swapping its own
# venv causes ansible-core module_utils skew → "Unknown profile name"), so the
# in-playbook mise upgrade excludes it (see apps/mise/tasks/upgrade.yaml).
mise upgrade --yes pipx:ansible

# `-i localhost,` (trailing comma) is an inline host list, not an inventory file.
mise exec -- ansible-playbook -i localhost, playbook.yaml --tags "upgrade,${profile}"