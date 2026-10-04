# Handoff: restart-stale style cleanup and design walkthrough

**Status, 2026-10-04: CLOSED — all steps done.** Step 1 chose Ruff and
step 2 landed as PR #31. Step 3, the walkthrough, completed 2026-10-04:
all five layers (staleness decision, process discovery, restart
behaviour, topic wiring, test evidence) delivered and approved by the
author. Last work under this thread: PR #43, which makes the ollama
per-GPU check fail on a Vulkan/CPU fallback (its evidence lives in
`TASKS-RESOLVED.md`). Nothing here is in flight; the sections below are
kept as history. Always pass `--frozen` to `uv run`: without it,
`--with <tool>` re-locks `uv.lock` against this machine's employer
package index.

**Author decision, 2026-09-28: continue.** The code is already on `main` (#11
`af02574`, the role and ollama; #15 `2a1d009`, the 1Password desktop app).
What remains is:

1. **Pick the style standard.** Ask the author: strict PEP 8 (pycodestyle,
   79 columns) or Ruff (88 columns plus its rule set)? The repo has no Ruff
   config, so Ruff's findings come from its effective settings, not from a
   project decision. Don't pick silently.
2. **Clean up only the six restart-stale Python files** to that standard:
   `dotfiles/roles/restart-stale/filter_plugins/restart_stale.py` and the five
   files in `tests/restart_stale/`. Not a repo-wide formatter migration. Run
   `tests/restart_stale` before and after, and the full suite before the PR.
3. **Resume the plain-English design walkthrough** at the staleness decision
   (see "Exact conversational stopping point" below), one layer at a time.

## Enter this worktree

```sh
cd "$HOME/.local/share/chezmoi/.worktrees/restart_stale_style"
git branch --show-current      # restart_stale_style, branched from main at 61c50ff
```

For agent tools, set `workdir` explicitly. This file is local and
uncommitted. Pull requests from this branch go into `main` only. The old
worktree `wt-restart` and branch `review/topic-restart-stale` are retired.

## Findings re-checked on main, 2026-09-28

The same numbers as the 2026-09-24 table further down: pycodestyle 52 (51
E501, 1 E731); Ruff lint 11 (4 RUF100, 3 I001, 2 ISC004, 1 FURB167, 1
PLW1510); Ruff format would reformat 5 of 6 files. Commands, run from the
repo root with each path written out (zsh does not split a `$VAR` holding
several paths):

```sh
uv run --with pycodestyle pycodestyle --statistics --count dotfiles/roles/restart-stale/filter_plugins/restart_stale.py tests/restart_stale
uv run --frozen ruff check --statistics dotfiles/roles/restart-stale/filter_plugins/restart_stale.py tests/restart_stale
uv run --frozen ruff format --check dotfiles/roles/restart-stale/filter_plugins/restart_stale.py tests/restart_stale
```

## History below this line

Everything below is the earlier handoff (PR #5, then the split into #11 and
#12), kept for context. Worktree paths and "do not merge" instructions in it
are superseded by the sections above.

## Exact conversational stopping point

The user said:

> Use plain technical english and some feynman explaining to illustrate
> effectively the current design -- we'll go through it starting with a 30k
> view and then digging down into the important components.
>
> The first thing is are we pep8 compliant?

The answer was **no, not yet**, based on fresh checks of the six Python files
in this PR. The user then requested this handoff. No style fixes have been
made, and no line-length convention has been chosen during this review.

The explanation already given:

- Updating a program on disk does not necessarily replace the program already
  running. It is like replacing a manual while a worker still uses an old copy.
- A topic identifies its service or app; a shared Ansible role reads process
  and executable information; small Python functions decide whether it is
  stale; Ansible restarts it or leaves it alone and reports the outcome.
- Style checks help people read the decision code. Behavior tests establish
  what that code and the surrounding tasks do. Passing one does not prove the
  other.

The next design topic proposed was **the staleness decision**: what evidence
is compared, why ctime was chosen, and where that approximation can be wrong.
Continue one layer at a time. Do not start with an implementation dump or
repeat the entire session history.

## PEP 8 and Ruff: current findings

Scope: `dotfiles/roles/restart-stale/filter_plugins/restart_stale.py` and the
five Python files in `tests/restart_stale/`.

| Check | Observed result |
|---|---|
| pycodestyle 2.15.0, default 79-character limit | 52 findings: 51 E501 long lines, one E731 named lambda |
| Ruff 0.16.2, effective local configuration | 11 findings |
| Ruff format check | 5 files would be reformatted; 1 already formatted |

The Ruff findings include import ordering, unused `noqa` comments, missing
explicit `check=` on a test subprocess, unparenthesized adjacent strings, and
the `re.M` alias. The named lambda is in `restart_stale_harness.py:45`.

Ruff's resolved line width is 88; pycodestyle used 79. PEP 8 permits an agreed
project line-length variation. Do not silently equate Ruff formatting with
strict default PEP 8 compliance. No repo-wide Ruff config was found in this
worktree; inspect the effective configuration rather than assuming its rules
are a versioned project contract.

Read `docs/PYTHON.md`: it names Ruff, but the commit hooks do not run Python
linting. Earlier test/Ansible validation claims did not establish style
compliance. That gap has been acknowledged to the user.

Commands used (non-mutating):

```sh
uv run --with pycodestyle pycodestyle --statistics --count dotfiles/roles/restart-stale/filter_plugins/restart_stale.py tests/restart_stale
uv run --with ruff ruff check dotfiles/roles/restart-stale/filter_plugins/restart_stale.py tests/restart_stale
uv run --with ruff ruff format --check dotfiles/roles/restart-stale/filter_plugins/restart_stale.py tests/restart_stale
uv run --with ruff ruff check --show-settings dotfiles/roles/restart-stale/filter_plugins/restart_stale.py
```

Recommended next step: agree on the formatting contract with the user, perform
a scoped cleanup if requested, rerun the restart tests, and update PR #5.
Do not turn this into a repository-wide formatter migration.

## What the user approved

1. Restart stale running services **and GUI apps automatically**, without an
   approval prompt on each update run.
2. Have the 1Password topic own installing the GUI app too.
3. Publish a restart-only PR, excluding other sessions' unpublished commits.
4. Resolve the PR in this conversation after creating it.

The user is now reviewing the design. The repo's author-understanding check
before merge has not been completed. Their request for an explanation is the
current review step, not approval to skip it.

## Implementation map

### Shared role

`dotfiles/roles/restart-stale/`

- `defaults/main.yaml`: interface for `launchd`, `systemd`, and `app` callers.
- `filter_plugins/restart_stale.py`: pure parsing and decision functions.
- `tasks/main.yaml`: process discovery, executable stat, decision, restart,
  and result reporting.
- `README.md`: usage and limitations.

The comparison is `process_start < executable_ctime`, with executable symlinks
followed. Process start comes from `ps` under `TZ=UTC LC_ALL=C`.

The observed Homebrew binary preserved mtime and birthtime from its bottle;
ctime reflected installation. That is the evidence for choosing ctime.
It is a heuristic, not a version comparison: chmod/chown/xattr changes can
cause extra restarts, and `ps` has whole-second precision.

Behavior:

- Not running: leave stopped.
- Running and fresh: leave alone.
- Running and stale: restart using its supervisor, or gracefully quit and
  reopen the exact GUI bundle.
- Missing executable: report it; do not restart onto a missing file.
- Failed GUI quit or an app that remains running: report; no force-quit.
- Failed process probe: fail the task; do not infer that the app stopped.

### Topic callers

- `dotfiles/apps/ollama/tasks/install.yaml`: launchd agent
  `com.ollama.server` on macOS; system-scope `ollama` unit on Debian.
- `dotfiles/apps/1password/tasks/install.yaml`: Homebrew cask with `adopt`
  and explicit `/Applications`, then the shared app check.
- Checks are at the end of install tasks and tagged `upgrade`, so they run
  after the relevant binary changes and service reloads.
- 1Password's own updater still supplies updates; brew does not upgrade it
  greedily. If self-update is disabled, this leaves an update-path gap.
- 1Password removal is opt-in and never uses `zap`.

1Password's official browser-integration guidance was the reason for using
`/Applications`. A similar requirement for Touch ID was not verified and must
not be claimed. The machine's general cask default is `~/Applications`, which
is why this topic must override it explicitly.

## Four commits in PR #5

1. `588ec91` (was `c1e2738`) — shared restart-stale role and tests.
2. `a3a2cf5` (was `1f60cfc`) — Ollama wiring.
3. `1844ff0` (was `4a13b19`) — 1Password GUI ownership and restart wiring.
4. `a8f4580` (was `302a94f`) — review fixes: exact-bundle quit and fail on
   process-probe errors.

These were cherry-picked from the original local feature branch onto published
`origin/main`. Their code matches the corresponding original four commits.
The original branch, `feat/topic-restart-stale`, remains at `79f6f0f`.

The review fixes had four red regression cases before implementation. Removing
the exit-error guard afterwards made both probe-error cases fail again.

## Verification: keep the bases separate

- Focused restart suite: **53 passed**.
- Published PR base: **690 passed, 1 failed, 7 skipped, 7 deselected** for the
  non-model repo suite. The failure is the pre-existing permissions test for
  `git filter-repo --path x`: expected `deny`, policy returns `ask`.
- That permissions test and its settings file are unchanged from remote main.
  Its correction exists only on local main as `1e7899b`; it was deliberately
  excluded from this restart-only PR.
- Local main plus the restart changes: **695 passed, 7 skipped, 7 deselected**.
  Do not advertise that result as a green run on the PR's older remote base.
- Parent and both topic playbooks passed Ansible syntax checks. 1Password
  metadata validation and `skillet validate .` passed.
- Scoped ansible-lint: **44 findings versus 42 on local main**. Three
  path-based role imports added, one lowercase task removed. Existing casing
  and shell findings remain. Lint is not green.
- Betterleaks scanned the four-commit range and PR body with no findings.
- `git diff --check` passed.
- GitHub listed no checks on PR #5. No CI result should be invented.

Useful commands, from the worktree:

```sh
uv run --with pytest --with hypothesis --with pyyaml pytest tests/restart_stale -q
uv run --with pytest --with hypothesis --with typer --with questionary --with pyyaml --with pillow --with jinja2 pytest tests -m 'not llm_judge' -q
gh pr view 5 --repo bengineerdavis/dotfiles --json state,mergeable,headRefOid,statusCheckRollup
```

For Ansible checks use the `dotfiles/` working directory, where `ansible.cfg`
resolves the roles. Run syntax/check mode first. Tests use stub supervisors;
they must not quit real apps or restart the shared Ollama server.

## Not yet demonstrated live

- Debian service restarts and privilege handling.
- Actual Homebrew adoption of the existing 1Password app.
- GUI Automation permission handling during a real quit/reopen.
- Per-GPU Ollama instances are outside this initial wiring.

Earlier implementation verification ran the real Ollama check only when the
server was known fresh; it reported no restart and changed nothing. 1Password
was checked in dry-run mode only. Do not claim either live stale-restart path
has been proven.

## Local permission changes requested during this handoff

The user requested allowances for `pwd *`, `git rev-parse *`, `git branch *`,
`git status *`, `git worktree *`, GitHub PR reads, and then explicitly
`git log *`. Mutating forms should ask rather than receive a broad allowance.

`opencode.jsonc` in **this worktree** now has local, uncommitted changes:

- Allow `pwd`, `git rev-parse`, `git status`, `git log`, with arguments.
- Keep branch creation/deletion/rename at ask; allow bare branch listing,
  `--show-current`, bare `--list`, and specific fixed listing flags.
- Keep worktree mutations at ask; allow `git worktree list` with arguments.
- Allow `gh pr list/status/view/checks/diff`; other PR operations ask.
- Ask for `git log` options `--output`, `--ext-diff`, and `--textconv`.
- The same classification is applied to the optional `autonomous` agent.
  Existing deny rules remain in place.

OpenCode 1.18.32 accepted the config through
`opencode --pure debug config`. Thirty representative commands in each of the
project and autonomous maps matched expected actions using the documented
last-matching-rule semantics. This checks the resolved configuration, not
end-to-end enforcement of every shell expression. Direct command prefixes
were covered; no blanket `git -C ...` rule was added.

These edits are **not part of PR #5** and are not committed or pushed. Keep
them separate from the restart feature. Global config and the other
repositories' project configs were not changed. Restart OpenCode from this
worktree for the new rules to load; this running session retains its old config.

Reference: <https://opencode.ai/docs/permissions/>. Do not print complete
resolved configs or environment dumps: they can contain credentials. During
validation only permission classifications were printed.

## Shared-repository coordination

- Main chezmoi checkout: `/Users/ben.davis/.local/share/chezmoi`.
- Deployed copy: `/Users/ben.davis/dotfiles` (not a Git checkout).
- At the last read, local main was `07cd1b2`, **35 commits ahead** of its
  remote. Other sessions are active. Do not push, reset, or rewrite that main
  merely to publish this PR.
- Separate worktrees include `wt-manifest` (`feat/ollama-manifest-scope`) and
  `/Users/ben.davis/code/wt-skill-trust-foreign-buckets`. Preserve them.
- Read the current main `AGENTS.md`, `spec.md`, and `TASKS.md` as well as this
  branch's copies. The remote base predates some current governance changes.
- Shared tasks belong on main; read the Claimed section before touching shared
  resources. Inspect the exact diff before any TASKS.md commit.
- Previous commit `80d8f27` accidentally captured another session's appended
  `skill-trust` task alongside the restart-review status. It is preserved and
  documented in a Git note. Do not repeat the pathspec-only mistake on a file
  actively being co-edited. Notes need an explicit refspec when pushed.
- Avoid `chezmoi apply` from a feature branch. A deployed tree cannot be
  isolated by Git worktrees. Applying requires the main-side workflow and the
  appropriate user authorization/claim.

## Background already completed; do not redo it

The original task was running the plain-english skill's evals in the separate
support/raise repo. That led to a design council, model-role fixes, worktree
isolation fixes, and this restart topic. Those support changes were merged and
pushed. The current active topic is **PR #5's restart design review**, not a new
plain-english eval run.

Coasts remains a deferred runtime-isolation tool to revisit. The user wants
mise reused for environment management rather than adding direnv. Research
references were recorded in support's
`docs/research/worktree-runtime-isolation.md`.

The earlier Ollama restart restored MLX responses, but it changed both runtime
version and process age. Do not claim the client/server mismatch proved the
cause of every failure: the morning failure predated that upgrade.

## Resume checklist

1. Confirm cwd, branch, dirty files, PR state, and inbound changes. Preserve
   the local permission edit and this handoff.
2. Continue the author's plain-English walkthrough from the PEP 8 findings.
   Address formatting before claiming merge readiness; choose the style
   contract explicitly if the author asks for the cleanup.
3. Explain the staleness decision, then process discovery, restart behavior,
   topic ordering, and test evidence. Use short concrete examples.
4. Finish human review before merging. If code changes, test the affected
   behavior and update the PR honestly, including baseline failures.
5. After approval, integrate without dropping other sessions' unpublished
   work. Treat deployment as a separate, explicit action.
