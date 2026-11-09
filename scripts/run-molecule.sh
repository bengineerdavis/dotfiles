#!/usr/bin/env bash
# scripts/run-molecule.sh
# Run molecule for one topic's scenario, from anywhere.
#
# Usage:
#   scripts/run-molecule.sh <topic> [verb] [extra molecule args...]
#   MOLECULE_SCENARIO=debian scripts/run-molecule.sh <topic> [verb]
#
# Verbs: create | prepare | converge | idempotence | verify | login |
#        destroy | test (default). Scenario: default, or MOLECULE_SCENARIO.
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
# Contract (docs/research/topic-vm-tests/PLAN.md § Decision 4):
# - runs from any cwd; molecule's scenario discovery is cwd-relative, so this
#   chdirs to the scenario's parent (home/dotfiles/apps/<topic>) itself;
# - exports MOLECULE_PROJECT_DIRECTORY=home/dotfiles/ so the role and its guards
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
# .chezmoiroot=home moves the payload, not repository-only scripts/tests.
DOTFILES="$REPO_ROOT/home/dotfiles"

TOPIC="${1:-}"
if [[ -z "$TOPIC" ]]; then
  err "no topic given. Usage: scripts/run-molecule.sh <topic> [verb] [extra molecule args...]"
  exit 2
fi

SCENARIO="${MOLECULE_SCENARIO:-default}"
SCENARIO_PARENT="$DOTFILES/apps/$TOPIC"
if [[ ! -f "$SCENARIO_PARENT/molecule/$SCENARIO/molecule.yml" ]]; then
  err "no scenario at home/dotfiles/apps/$TOPIC/molecule/$SCENARIO/. Scenarios live inside the topic per docs/TOPICS.md; create molecule/$SCENARIO/ there first, or select another with MOLECULE_SCENARIO."
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
# safety): idempotent, skips what is present. --project pins uv to THIS
# checkout's pyproject: uv otherwise discovers the project from the caller's
# cwd, so a run from outside the worktree that has the test-vm group fails
# with "Group `test-vm` is not defined" — caught by the confirmation run
# 2026-10-19 executing from the main checkout (measured, see the commit).
uv run --frozen --project "$REPO_ROOT" --group test-vm \
  ansible-galaxy collection install -r "$DOTFILES/requirements.yml"

# molecule 26.9.0 ships the vagrant driver's `vagrant` module inside the
# molecule_plugins package and no longer wires driver modules into
# ANSIBLE_LIBRARY (the driver's modules_dir property has no caller in
# 26.9.0), so the driver's own create/destroy playbooks fail with
# "couldn't resolve module/action 'vagrant'" — measured 2026-10-11. The
# path is computed from the locked environment, never hand-written, and
# stops being needed the moment molecule fixes the wiring upstream
# (re-check at the next molecule re-lock per O2).
VAGRANT_MODULES="$(uv run --frozen --project "$REPO_ROOT" --group test-vm python -c \
  'import molecule_plugins.vagrant.modules as m, os; print(os.path.dirname(m.__file__))')"
export ANSIBLE_LIBRARY="$VAGRANT_MODULES"

export MOLECULE_PROJECT_DIRECTORY="$DOTFILES"
# Keep run state OUTSIDE the chezmoi source (DOT-303). It used to live in the
# scenario dir, which put it inside chezmoi's source walk: a run killed during
# an install left a dangling symlink there, and chezmoi resolves the whole
# symlink chain while loading source state, so `chezmoi apply` and
# `execute-template` failed for every later invocation. `managed` and `status`
# stay green on such a link, which is why it read healthy while broken
# (measured 2026-11-07).
#
# The checkout name is in the path so two worktrees of the same topic do not
# share state — worktrees share the git dir but not gitignored files, and the
# derived /tmp/lima-<sha1> name would otherwise collide across checkouts.
# Molecule's own default is keyed on the project dir's basename, which is why
# a pin is needed at all (molecule 26.9.0; re-check at the next re-lock per O2).
STATE_ROOT="${XDG_STATE_HOME:-$HOME/.local/state}"
CHECKOUT="$(basename "$REPO_ROOT")"
export MOLECULE_EPHEMERAL_DIRECTORY="$STATE_ROOT/molecule/$CHECKOUT/$TOPIC/$SCENARIO"
mkdir -p "$MOLECULE_EPHEMERAL_DIRECTORY"
export ANSIBLE_COLLECTIONS_PATH="$HOME/.ansible/collections"

# One-time sweep of the old in-source location (DOT-303). Leftover state there
# predates the relocation and still breaks chezmoi, so name it rather than
# silently ignoring it — but do not delete it: it may belong to a run another
# session has in flight, and `limactl delete` asks in the autonomous tier.
LEGACY_STATE="$SCENARIO_PARENT/molecule/$SCENARIO/.molecule"
if [[ -d "$LEGACY_STATE" ]]; then
  printf 'run-molecule: WARNING: pre-relocation state at %s\n' "$LEGACY_STATE" >&2
  printf 'run-molecule:   it sits inside the chezmoi source; a dangling symlink in it breaks chezmoi apply.\n' >&2
  printf 'run-molecule:   remove with: find %s -xtype l; rm -rf %s\n' "$LEGACY_STATE" "$LEGACY_STATE" >&2
fi

# Report leftovers before starting (DOT-309). A reaper that removes quietly is
# the same failure with a different trigger, so this names what it found and
# leaves the decision to a human. Lima roots are derivable only while the
# ephemeral dir's path is known, because the hash is of that path — so a sweep
# here can only report the ones this scenario's current location owns.
# LIMA_TMP_ROOT exists so the report can be tested without touching real /tmp.
LIMA_TMP_ROOT="${LIMA_TMP_ROOT:-/tmp}"
# Portable SHA-1: macOS has no sha1sum (GNU), only shasum (perl) and openssl.
# The hash names the Lima root, so a wrong or missing one would silently point
# the report at the wrong directory — probe instead of guessing.
if command -v sha1sum >/dev/null 2>&1; then
  SHA1="sha1sum"
elif command -v shasum >/dev/null 2>&1; then
  SHA1="shasum -a 1"
elif command -v openssl >/dev/null 2>&1; then
  SHA1="openssl dgst -sha1 -r"
else
  err "no SHA-1 tool (sha1sum, shasum, or openssl) on PATH; it names the Lima root."
  exit 1
fi
LIMA_ROOT="$LIMA_TMP_ROOT/lima-$(printf '%s' "$MOLECULE_EPHEMERAL_DIRECTORY" | $SHA1 | cut -d' ' -f1)"
if [[ -d "$LIMA_ROOT" ]]; then
  printf 'run-molecule: WARNING: leftover VM state at %s\n' "$LIMA_ROOT" >&2
  printf 'run-molecule:   the age rule in home/dot_config/user-tmpfiles.d/tmp.conf reaps it after 1d.\n' >&2
  printf 'run-molecule:   to remove it now: limactl list; then limactl delete <instance>; rm -rf %s\n' "$LIMA_ROOT" >&2
fi
# Stray roots this scenario cannot address: report count only, never remove.
# Two concurrent runs collide on the fixed platform name `lima-mol`, so a
# leftover may not be attributable — say so rather than guessing. `|| true`
# because a missing LIMA_TMP_ROOT would otherwise kill the run under
# `set -euo pipefail` with no message at all.
STRAY=$(find "$LIMA_TMP_ROOT" -maxdepth 1 -type d -name 'lima-*' ! -path "$LIMA_ROOT" 2>/dev/null | wc -l | tr -d ' ' || true)
if [[ "$STRAY" != "0" ]]; then
  printf 'run-molecule: WARNING: %s other /tmp/lima-* root(s) present; not mine to remove.\n' "$STRAY" >&2
  printf 'run-molecule:   inspect with: find %s -maxdepth 1 -type d -name "lima-*"\n' "$LIMA_TMP_ROOT" >&2
fi

cd "$SCENARIO_PARENT"
# Bound the run (DOT-309). Molecule installs no signal handlers and runs its
# destroy only inside `except ScenarioFailureError` (verified against 26.9.0 and
# upstream main), so a hung driver call neither fails nor finishes and holds its
# VM forever. A wall-clock bound turns that into a failure with an exit code.
# `login` is deliberate and human, so it is not bounded — a human closes it.
#
# Two portability constraints, both measured:
# - macOS ships bash 3.2, where `"${arr[@]}"` on an EMPTY array under `set -u`
#   is an unbound-variable error. So the unbounded path is a separate branch
#   rather than an empty array expansion.
# - macOS has no `timeout` (GNU coreutils); brew installs it as `gtimeout`.
#   Fails closed when neither exists: a silently unbounded run is the exact
#   failure DOT-309 exists to fix.
MOLECULE_TIMEOUT="${MOLECULE_TIMEOUT:-30m}"
TIMEOUT_BIN=""
if [[ "$VERB" != "login" ]]; then
  if command -v timeout >/dev/null 2>&1; then
    TIMEOUT_BIN="timeout"
  elif command -v gtimeout >/dev/null 2>&1; then
    TIMEOUT_BIN="gtimeout"
  else
    err "no timeout/gtimeout on PATH; without it a hung run holds its VM indefinitely (DOT-309)."
    err "install GNU coreutils: the gnu-tools topic (brew coreutils provides gtimeout)."
    exit 1
  fi
fi

# The driver comes from molecule.yml; no -d flag: molecule 26.9.0 accepts
# --driver-name on create/prepare/destroy/test but rejects it on
# converge/idempotence/verify/login (measured 2026-10-11), and an override
# the config already names is not worth per-verb dispatch.
if [[ -n "$TIMEOUT_BIN" ]]; then
  exec "$TIMEOUT_BIN" --signal=TERM --kill-after=2m "$MOLECULE_TIMEOUT" \
    uv run --frozen --project "$REPO_ROOT" --group test-vm molecule "$VERB" -s "$SCENARIO" "$@"
else
  exec uv run --frozen --project "$REPO_ROOT" --group test-vm molecule "$VERB" -s "$SCENARIO" "$@"
fi