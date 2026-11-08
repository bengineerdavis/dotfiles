# pre-commit ↔ prek migration strategy — handoff to python-project-template

A cross-repo handoff: what dotfiles needs from the `python-project-template`
copier template, why it needs it now, and the context a separate session in
that repo must absorb before acting.

Written 2026-11-08. The feature request is filed as a GitHub issue on
`bengineerdavis/python-project-template`; this file is the durable pointer
that survives after the issue is triaged, so the two do not drift.

## The problem, in one paragraph

dotfiles is switching its git hook runner from pipx `pre-commit` to `prek`
(DOT-59). prek already eats `.pre-commit-config.yaml` as a drop-in, and it
already ships a `prek util yaml-to-toml` converter plus a migration checklist
— so the pre-commit→prek half is mostly upstream-solved. What is *not* solved
anywhere is a **codified, template-owned recipe** that a stamped project can
run without re-deriving it, in both directions: pre-commit→prek *and*
prek→pre-commit. The template repo stamps `template/prek.toml.jinja` and is
already native-prek, so right now a project stamped from it has no migration
story at all — and there is no reverse path if a stamped project needs to go
back to pre-commit.

## Why now

Two events collided this week:

1. **DOT-59 is being executed right now.** The hook-runner switch is no longer
   a planned item; the migration is landing in dotfiles in this session. The
   dotfiles migration surfaced the gaps a template recipe would close —
   chiefly that `prek util yaml-to-toml` silently drops YAML comments (which in
   dotfiles carry durable "why" decisions), and that two dotfiles tests parse
   `.pre-commit-config.yaml` directly and had to be repointed to `prek.toml`.

2. **The template repo has no migration artifact.** Its `.github/` has only
   workflows (no issue templates, no labels), so a project switching runners
   gets no guidance. This handoff carries that gap to the template's queue.

## What dotfiles did (worked example for the recipe)

The dotfiles migration (DOT-59) is the concrete instance the recipe should
generalize from:

- **Author `prek.toml`** from `.pre-commit-config.yaml` via
  `prek util yaml-to-toml`, then hand-carry the YAML comments that encode
  *why* (ruff `types_or`, pyrefly `pass_filenames: false`, bats convention,
  commit-proportionality thresholds, queue-integrity duplicate-id rationale).
  The converter drops comments; dotfiles re-added them by hand.
- **Add `default_install_hook_types`** for every stage beyond `pre-commit`
  (dotfiles uses `pre-commit`, `pre-push`, `commit-msg`). Without it, prek
  installs only the pre-commit shim and the pre-push/commit-msg hooks silently
  never run.
- **Delete the YAML** once `prek.toml` is in place — prek prefers `prek.toml`
  over `.pre-commit-config.yaml`, so leaving both means trusting precedence
  rather than removing the ambiguity.
- **Repoint any test that reads the config file.** Two dotfiles tests parsed
  `.pre-commit-config.yaml` with `yaml.safe_load` and had to switch to
  `tomllib.loads` on `prek.toml`. The recipe must warn about this: a config
  filename is a public path, not an internal detail.
- **Reconcile against in-flight branches.** The dotfiles migration initially
  derived its `prek.toml` from the main checkout's YAML while PR #131
  (unmerged) had added two more pre-push hooks (`branch-sync`, `roborev-flush`)
  to its own YAML copy. The first attempt carried those hooks over — which
  made the branch un-pushable, because their backing script
  (`scripts/check-branch-sync.py`) lives only on PR #131. The correct rule:
  migrate only what exists on the branch you migrate from, and let an
  in-flight branch migrate its own additions when it rebases.
- **Retire the pipx entry.** The machine uninstall is author-run; the repo
  source change is removing `"pipx:pre-commit"` from the mise config.
- **Verify patch-to-cache, not stash.** Run against a tree with unstaged
  edits and confirm prek prints "Temporarily saving them to" a
  `~/.cache/prek/patches/` file while `git stash list` is unchanged. This is
  the load-bearing check dotfiles' task description names, because prek's
  mechanism was verified against `master` rather than an installed version.
- **Stage the config before running.** prek refuses to run hooks against an
  unstaged `prek.toml` ("Configuration file `prek.toml` is not staged"). `git
  add prek.toml` first — this bites immediately after authoring a fresh config.

## What the feature request asks for

A general pre-commit↔prek migration strategy, not a template-specific one:

- **pre-commit→prek**: a recipe (checked-in, runnable) that an existing
  pre-commit project follows to move to prek, generalizing the dotfiles work
  above — convert, carry comments, declare install hook types, delete YAML,
  repoint config-reading tests, retire the pipx entry.
- **prek→pre-commit**: the reverse path, which upstream does not cover. A
  `prek.toml`→`.pre-commit-config.yaml` conversion, and how prek-only features
  (globs, `priority`, `groups`, `shell`, `default_env`, `builtin` repos) map
  back or are lost.
- The recipe should live in the template repo so stamped projects inherit it,
  and should cite prek's own `https://prek.j178.dev/migration/` rather than
  re-inventing the upstream checklist.

## Destination context (for the other session)

- Repo: `bengineerdavis/python-project-template` (`git@github.com:...`), a
  copier base template with `agentic-project-template` stacking on top.
- The template is already native-prek (`template/prek.toml.jinja`, ruff-only by
  design — the agentic layer owns whitespace/merge markers/tombi).
- Absorb the GitHub issue into a task via the repo's `@askmatt` process.
- The `.github/` gap (no issue templates or labels) is a separate follow-up:
  ask about issue templates/labels when stamping new or updated templates,
  filed against `copier-template-copier-template` (a distinct repo from the
  python template).