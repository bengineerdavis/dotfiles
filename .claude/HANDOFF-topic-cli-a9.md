# HANDOFF — A9: manager-aware topic generator (topic-cli-a9)

> **Superseded 2026-10-20, after the pause.** The author redirected the
> interim home this handoff chose (`tools/topical/` here): the generator,
> block templates and canonical skeleton moved to the topical repo
> (`~/code/personal/topical`), which the copier topic template will later
> inherit from. The design below stands apart from that one decision —
> "Interim home" and anything naming `tools/topical/` or a local
> `template_dir/` is stale.

Paused 2026-10-20, mid-build, in a clean state: three commits on the branch,
working tree clean, next step is writing the generator itself. Resume in
worktree `.worktrees/topic-cli-a9`, branch `agent/topic-cli-a9`.

Task: `TASKS.md` § Now, A9 (manager-aware `template_dir/` folded into the
`topical` CLI). Scoped this session to the **deterministic generator half**;
the `migrate-to-roles.sh` absorption and the optional agent pass stay open in
the A9 line. Author decisions on file: proof target is **firefox**; worker
budget for this machine is **2** (`.agent-budget.toml` written, gitignored).

## Done so far

| SHA | What |
|---|---|
| `113ef03` | TASKS.md: A9 claimed and promoted Planned → Now |
| `fcd46a8` | `dotfiles/managers.yaml`: added top-level `playbook_var_defs` |
| `864a277` | `template_dir`: deleted dead root `main.yaml`/`tasks.yaml`; stubs now carry splice markers |

`playbook_var_defs` holds the two cask playbook vars (`homebrew_prefix`,
`user_appdir`) with definitions verified byte-identical across every topic
playbook on 2026-10-20. The template's `tasks/install.yaml` and
`tasks/remove.yaml` now end in `# __MANAGER_BLOCKS__`; `playbook.yaml` has
`# __PLAYBOOK_VARS__` where the vars block goes. The five-way commented
manager menu (including the snap block zero topics use) is gone from the
template — it moves into the generator, fed by `managers.yaml`.

## Design — settled this session, do not re-litigate

- **Interim home: `tools/topical/topical`** — a PEP 723 Typer script
  (`uv run --script`), tested from `tests/topical/` by import (binned
  conftest pattern: `SourceFileLoader` for the extensionless file). The
  2026-09-14 amendment puts the CLI's final home in its own repo (does not
  exist yet); A9 says write it here to be carried over. `tools/` is
  chezmoi-ignored, so nothing deploys. Typer, pyyaml and hypothesis are
  already in the root test dependency group.
- **One template + data + thin generator.** `template_dir/` is the
  manager-neutral skeleton (copied verbatim, then markers substituted);
  `managers.yaml` holds the facts (module, become, os, playbook_vars,
  upgraded_by); the generator owns the block templates and the
  package-vs-outline mode map. Do not put block templates back in
  template_dir — that recreates the five near-identical scaffolds A9
  rejected.
- **Two emission modes per manager.** `package` (homebrew_formula,
  homebrew_cask, homebrew_tap, apt): a complete live block from the topic
  name alone. `outline` (apt_repository, release_artifact): a commented
  skeleton carrying the manager's traps, because URLs/keys/checksums are
  per-topic and unknowable to a generator.
- **CLI shape:** `topical new NAME [--tier] [--os]... [--requires]...
  [--manager]... [--package-name] [--repo DIR] [--into DIR]`. `--repo` =
  where managers.yaml/template_dir come from (default: discover upward from
  cwd); `--into` = destination repo root (default: same as `--repo`).
  Refuses to overwrite an existing `apps/<name>/` — no force flag.
- **Firefox proof path:** generate with `--repo` = real worktree root,
  `--into` = scratch dir, then reconcile by diffing scratch `apps/firefox`
  against the real one. The generator never edits an existing topic.
- **Validation rules:** name `^[a-z][a-z0-9-]*$` minus {new, list, doctor,
  help}; manager keys checked against managers.yaml with valid keys in the
  error; a manager whose `os` list is disjoint from the topic's `topic_os`
  is an error naming both; unknown tier/os rejected.
- **upgrade.yaml guidance:** if every chosen manager is
  `upgraded_by: system_role`, the stub names the covering role
  (homebrew_* → apps/homebrew, apt* → apps/apt); if any is
  `upgraded_by: topic`, prepend the warning that the topic must own its
  upgrade (the TOPICS.md § Presence-vs-currency case).

## Facts gathered for the remaining steps

- **`dotfiles/ansible.cfg` sets no `roles_path`** — only
  `callback_result_format`. Role `apps/<name>` resolves relative to the
  CWD, so `ansible-playbook --syntax-check` on a generated topic must run
  from the directory containing `apps/`.
- **Tap teardown (from apps/opencode, measured on Homebrew 7.0.1):**
  install order is trust → tap → install; teardown reverses and takes TWO
  commands — `brew untrust --formula <tap>/<formula>` then
  `brew untrust --tap <tap>` — both idempotent ("Not trusted" exits 0),
  `changed_when: "'Not trusted' not in <reg>.stdout"`. Copy this shape;
  do not invent a simpler one.
- **firefox today** is a template_dir copy with live cask blocks in
  install/remove, raw template README residue, **no CHANGELOG.md**, the
  root `tasks.yaml` residue, and the empty zsh stubs (stubs stay — out of
  A9 scope). The regenerated topic must add CHANGELOG.md and delete
  `tasks.yaml`; topic.yml should come out equivalent to today's
  (app tier, requires [homebrew], os [Darwin]).
- **Residue sweep list:** root `tasks.yaml` carrying 4 "put package name
  here" markers each — anki, clamav, deb-get, eza, fzf, gnu-tools,
  homebrew, lynis, mise, tmux, trash-cli, zoxide (12 topics). ollama's
  `tasks.yaml` has NO markers (check whether it is real before touching
  it). Root `main.yaml` exists in mise and ollama (ROADMAP says 6 of 26
  topics; find the rest, verify zero references, delete in the sweep
  commit).
- **Test approach:** `tests/topical/`, typer's `CliRunner`, `--repo`
  pointed at `PAYLOAD_ROOT` (from `payload_seam`, the worktree's own
  files) and `--into` at `tmp_path`. Both directions: refuse cases
  (overwrite, unknown manager, OS mismatch, bad name) and proceed cases
  (cask/formula/apt/outline/no-manager). One hypothesis property: for
  generated names + manager subsets, no `<topic>`/`{{ app_name }}` marker
  survives and every emitted YAML parses. Ansible syntax-check test
  guarded by `shutil.which`. Mutation evidence on the commit as
  `Mutation:`/`Failing-test:` trailers.

## Remaining plan

1. Write `tools/topical/topical` + `tests/topical/` (one commit, tests
   with the code).
2. Residue sweep: delete the 12 unedited root `tasks.yaml` files; verify
   and delete the dead root `main.yaml` leftovers (one commit).
3. Firefox: generate to scratch, reconcile into `apps/firefox`, verify
   `ansible-playbook apps/firefox/playbook.yaml --syntax-check` and
   `--check --tags provision` from `dotfiles/` (one commit).
4. Docs: TOPICS.md § Template Conformance and § Adding a new topic are
   stale (the first says don't add bootstrap/prerequisites to the template
   — reality and § Topic structure require all five lifecycle files; the
   second points at `meta/main.yml` — schema lives in `topic.yml` at the
   role root). Update both; root CHANGELOG.md entry (one commit).
5. Push, open the PR (deployed-tree files are touched → always PR, always
   human review), report, quiz the author.

## Gotcha worth keeping

The prek hooks stash unstaged changes during a commit. A bare `git commit`
after `git rm` committed only the staged deletions and left the three
modified template files behind — message and contents mismatched until
amended. In this worktree the index is private, so the fix is simply
`git add` the intent files before committing; verify with
`git show --stat HEAD` after, as always.
