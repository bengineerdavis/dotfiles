# PYTHON.md

Python conventions for this repository.

`AGENTS.md` stays general so it can be reused across projects. Conventions are
pluggable and live in `docs/`, one file per subject. This is the Python
one. A repo that adds Go gets `conventions/GO.md` and changes nothing in
`AGENTS.md` except the pointer. See `docs/README.md`.

Everything here assumes `AGENTS.md` § Tests and § Prove the test fails, which are
language-neutral and stay there.

## Toolchain

Python here is 36 standalone PEP 723 scripts plus the test suite. **There is no
`pyproject.toml` and no package**, which changes what several of the usual rules
mean.

- **uv runs everything.** Scripts start `#!/usr/bin/env -S uv run --script`. Run
  tools through `uv run` rather than installing them globally, so the version is
  the script's and not the machine's.
- **Dependencies live in each script's `# /// script` block.** Add them with
  `uv add --script <file> <lib>` instead of hand-editing the block. If a
  `pyproject.toml` is ever added, the same rule applies to it: `uv add LIB` or
  `uv add --dev LIB`, never a hand edit.
- **pytest, test first.** See § Tests and § Prove the test fails. A test that has
  not been seen to fail is not yet a test.
- **Share fixtures through `conftest.py`.** `tests/ollama_evals/conftest.py`
  loads the harness as a module so every suite in that directory gets it once.
- **ruff lints.** Installed, but not yet in `.pre-commit-config.yaml` — the hooks
  currently run shellcheck and bats only, so no Python file is linted on commit.
  Queued in `TASKS.md`.
- **ty typechecks.** Not installed yet, and not referenced anywhere in the repo.
  Also queued. Treat any claim that the Python here is typechecked as false until
  that lands.
- **prek runs the hooks.** Both `prek` and `pre-commit` are installed and both
  read `.pre-commit-config.yaml`; which one is authoritative is unsettled and
  queued.
- **Log, do not print,** for anything an agent may need to read back while
  debugging.

## Dependency classes

Four surfaces hold dependencies; each has its own add/remove rule. No
`pyproject.toml` exists and none is planned; if one ever lands, the same rules
map onto it (`uv add` / `uv add --dev`).

1. **Script deps (PEP 723).** In each script's `# /// script` block. Add with
   `uv add --script <file> <lib>`, never a hand edit; remove by deleting the
   line — uv resolves the rest per run. Scripts that shell out check their
   deps at runtime with `require()` and name the fix in the error (see
   `bin/llm-ctx`).
2. **Test-run deps.** The `uv run --with` list in `AGENTS.md` § Commands —
   ephemeral: uv resolves and caches per run, nothing installs globally.
   Add: the flag goes in the documented command AND the suite must
   **skip, not error**, without it (`pytest.importorskip` at module level —
   the jinja2 pattern in `tests/herdr/test_user_acceptance.py`). Remove:
   drop the flag; an orphaned entry costs nothing but staleness.
3. **Toolchain and tools.** `dotfiles/apps/mise/files/config.toml` — the
   captured state. Add/remove by editing the entry and committing it (the
   `github:` backend convention, never `ubi:`); upgrades come from
   `mise upgrade`, never a tool's own updater.
4. **Ansible collections.** `dotfiles/requirements.yml` (deployed beside
   `ansible.cfg`; `ansible-galaxy collection install -r requirements.yml`
   before the playbook runs). Declared but **unpinned** today — no
   `version:` — so a machine installing today may get a different
   collection than the one a support grade was recorded against
   (`dotfiles/docs/TOPIC-RECIPES.md`, module-vs-shell ladder). Pinning
   changes fleet-wide upgrade behavior, so it is queued as an author
   decision rather than done here.
- **Do not hide or wrap errors.** Swallowing an exception turns a fixable failure
  into a mystery. Where an error genuinely must not escape, convert it
  deliberately at a boundary and keep the message: `run_check` turns any raise
  into a named failure rather than discarding it, which is why a broken check
  reports itself instead of aborting the run.

## Choosing Python at all

`AGENTS.md` § Languages holds the bash-versus-Python rule, because deciding
which language to use is a repository-level question rather than a Python one.
