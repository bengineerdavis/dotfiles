#!/usr/bin/env bash
set -euo pipefail

# Usage: update.sh [full|minimal]
#   full     upgrade apps AND heavy attachments (ollama models, large data)
#   minimal  upgrade apps only
#   (omit)   use your saved default; first run prompts and saves it
#
# ansible is mise-managed; `mise exec` guarantees it's on PATH.

here="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=bootstrap/profile.sh
. "$here/bootstrap/profile.sh"

# Resolve minimal/full (precedence: arg > saved default > first-run prompt /
# minimal). Passed to ansible as a tag; attachment tasks gate on it via
# ansible_run_tags (see playbook.yaml post_tasks).
profile="$(resolve_profile "${1:-}")"
echo "› upgrade profile: ${profile}" >&2

# Upgrade ansible FIRST, out-of-band, before it becomes the controller for the
# playbook below. ansible cannot safely upgrade itself mid-run (swapping its own
# venv causes ansible-core module_utils skew → "Unknown profile name"), so the
# in-playbook mise upgrade excludes it (see apps/mise/tasks/upgrade.yaml).
mise upgrade --yes pipx:ansible

mise exec -- ansible-playbook -i localhost playbook.yaml --tags "upgrade,${profile}"