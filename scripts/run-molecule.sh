#!/usr/bin/env bash
# scripts/run-molecule.sh
# Run molecule for one topic's scenario, from anywhere.
#
# Usage:
#   scripts/run-molecule.sh <topic> [verb] [extra molecule args...]
#
# Verbs: create | prepare | converge | idempotence | verify | login |
#        destroy | test (default)
#
# Build-ladder justification (AGENTS.md § What agents do): molecule is the
# tool; this is an interface to it — verb dispatch, one chdir, three env
# exports, no logic of its own. The raw invocation needs exactly the setup a
# human forgets (the cwd that roles resolve from, the locked uv environment,
# the installed collections, the driver's module path), and the author asked
# for a wrapper that brings the right-provisioned environment up
# automatically. The scripts/run-bats.sh precedent. Sized ~55 logic lines,
# far under the bash 80-100 line rule.
#
# Contract (dotfiles/docs/research/topic-vm-tests/PLAN.md § Decision 4):
# - runs from any cwd; molecule's scenario discovery is cwd-relative, so this
#   chdirs to the scenario's parent (dotfiles/apps/<topic>) itself;
# - exports MOLECULE_PROJECT_DIRECTORY=dotfiles/ so the role and its guards
#   resolve (molecule's Config reads this env var before falling back to
#   cwd — verified against molecule 26.9.0);
# - runs molecule through `uv run --frozen --group test-vm` so humans and
#   machines get the identical locked environment;
# - installs the pinned collections first (idempotent; skips what is present)
#   into ~/.ansible/collections and points ANSIBLE_COLLECTIONS_PATH at it;
# - exports ANSIBLE_LIBRARY for the vagrant driver's bundled module (see the
#   comment beside it);
# - `login` passes through untouched — it needs a tty and is human-only;
#   everything else is non-interactive and exits non-zero on failure.

set -euo pipefail

err() { printf 'run-molecule: ERROR: %s\n' "$*" >&2; }

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOTFILES="$REPO_ROOT/dotfiles"

TOPIC="${1:-}"
if [[ -z "$TOPIC" ]]; then
  err "no topic given. Usage: scripts/run-molecule.sh <topic> [verb] [extra molecule args...]"
  exit 2
fi

SCENARIO_PARENT="$DOTFILES/apps/$TOPIC"
if [[ ! -f "$SCENARIO_PARENT/molecule/default/molecule.yml" ]]; then
  err "no scenario at dotfiles/apps/$TOPIC/molecule/default/. Scenarios live inside the topic per docs/TOPICS.md; create molecule/default/ there first."
  exit 2
fi

VERB="${2:-test}"
case "$VERB" in
  create | prepare | converge | idempotence | verify | login | destroy | test) ;;
  *)
    err "unknown verb '$VERB'. Valid verbs: create | prepare | converge | idempotence | verify | login | destroy | test (test is the default)."
    exit 2
    ;;
esac
if [[ $# -gt 1 ]]; then
  shift 2
else
  shift "$#"
fi

if ! command -v uv >/dev/null 2>&1; then
  err "uv not found on PATH. Install it via mise (apps/mise topic, aqua:astral-sh/uv), then re-run."
  exit 1
fi

# Collections are user-level state the wrapper may write (PLAN.md § Destroy
# safety): idempotent, skips what is present.
uv run --frozen --group test-vm \
  ansible-galaxy collection install -r "$DOTFILES/requirements.yml"

# molecule 26.9.0 ships the vagrant driver's `vagrant` module inside the
# molecule_plugins package and no longer wires driver modules into
# ANSIBLE_LIBRARY (the driver's modules_dir property has no caller in
# 26.9.0), so the driver's own create/destroy playbooks fail with
# "couldn't resolve module/action 'vagrant'" — measured 2026-10-11. The
# path is computed from the locked environment, never hand-written, and
# stops being needed the moment molecule fixes the wiring upstream
# (re-check at the next molecule re-lock per O2).
VAGRANT_MODULES="$(uv run --frozen --group test-vm python -c \
  'import molecule_plugins.vagrant.modules as m, os; print(os.path.dirname(m.__file__))')"
export ANSIBLE_LIBRARY="$VAGRANT_MODULES"

export MOLECULE_PROJECT_DIRECTORY="$DOTFILES"
# Pin the state dir into the scenario: molecule 26.9.0 otherwise keys the
# ephemeral directory on the project dir's basename (molecule.<checksum>.
# <scenario> under ~/.ansible/tmp), so bare-molecule runs from another cwd
# get a different state than the wrapper's, and two topics' `default`
# scenarios would share one state dir. Env takes precedence over both
# (verified against molecule 26.9.0's scenario.ephemeral_directory); the
# vagrant driver's safe_files keep the box env intact across prunes.
export MOLECULE_EPHEMERAL_DIRECTORY="$SCENARIO_PARENT/molecule/default/.molecule"
export ANSIBLE_COLLECTIONS_PATH="$HOME/.ansible/collections"

cd "$SCENARIO_PARENT"
# The driver comes from molecule.yml; no -d flag: molecule 26.9.0 accepts
# --driver-name on create/prepare/destroy/test but rejects it on
# converge/idempotence/verify/login (measured 2026-10-11), and an override
# the config already names is not worth per-verb dispatch.
exec uv run --frozen --group test-vm molecule "$VERB" -s default "$@"