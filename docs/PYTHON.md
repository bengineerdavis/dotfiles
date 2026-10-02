# PYTHON.md

Python conventions for this repository.

`AGENTS.md` stays general so it can be reused across projects. Conventions are
pluggable and live in `docs/`, one file per subject. This is the Python
one. A repo that adds Go gets `conventions/GO.md` and changes nothing in
`AGENTS.md` except the pointer. See `docs/README.md`.

Everything here assumes `AGENTS.md` § Tests and § Prove the test fails, which are
language-neutral and stay there.

## Toolchain

Python here is 22 standalone scripts (13 PEP 723, 9 stdlib-only) plus the test
suite. A root `pyproject.toml` holds the test environment as PEP 735 dependency
groups; the repo is never built or installed (`package = false`).

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
- **ruff lints and formats, enforced on commit.** `[tool.ruff]` in
  `pyproject.toml` is the written standard: lines at 88 (ruff format, Black
  style), pycodestyle E/W, docstrings under the Google convention with their
  lines wrapped at 72 (W505; missing-docstring rules are deliberately
  unselected — that is a content campaign, not a fix). The ruff and
  ruff-format pre-commit hooks run on every commit. Paths still failing the
  doc-line rules carry per-path grandfathers in the config; each entry
  shrinks as the file is next edited and is deleted when its directory is
  clean. pycodestyle is retired — ruff implements it.
- **ty typechecks.** Not installed yet, and not referenced anywhere in the repo.
  Also queued. Treat any claim that the Python here is typechecked as false until
  that lands.
- **prek runs the hooks.** Both `prek` and `pre-commit` are installed and both
  read `.pre-commit-config.yaml`; which one is authoritative is unsettled and
  queued.
- **Log, do not print,** for anything an agent may need to read back while
  debugging.


## uv configuration and the private index

Two layers own uv's machine state, per the one-concern-per-layer rule:

- **The binary** — astral-installed at the system level (`~/.local/bin/uv`),
  deliberately not mise-managed or in Homebrew. The `apps/uv` topic installs
  and self-updates it; `dotfiles/bootstrap/bootstrap.sh` owns the first
  install on a fresh machine.
- **The user config** — `~/.config/uv/uv.toml`, rendered by chezmoi from
  `dot_config/uv/uv.toml.tmpl`. It pins `required-version` to the same floor
  as `pyproject.toml`, so an old install is refused everywhere with the fix
  named.

**The private index never enters this repo.** On work machines the private
package index is the default and public PyPI the fallback; its URL and
credentials live in the machine-local `~/.localrc`, captured from the vault
by the `apps/uv` topic. A host flagged work in `.chezmoidata/uv.yaml` refuses
to render without the captured URL. Two rules follow:

- **Never commit a re-lock done against a private mirror.** A committed
  `uv.lock` or `tools/skill-trust/uv.lock` referencing any non-public index
  fails the suite (`tests/uv/test_lock_sources.py`). Regenerate against
  public PyPI; day-to-day, always `uv run --frozen`.
- **Tokens stay env-only.** `uv.toml` never contains credentials; the
  `UV_INDEX_<NAME>_USERNAME`/`_PASSWORD` variables come from `~/.localrc`.

## Dependency classes

Four surfaces hold dependencies; each has its own add/remove rule. The root
`pyproject.toml` holds test and lint groups; use `uv add --group test LIB` or
`uv add --group lint LIB`, never a hand edit.

1. **Script deps (PEP 723).** In each script's `# /// script` block. Add with
   `uv add --script <file> <lib>`, never a hand edit; remove by deleting the
   line — uv resolves the rest per run. Scripts that shell out check their
   deps at runtime with `require()` and name the fix in the error (see
   `bin/llm-ctx`).
2. **Test-run deps.** The `test` group in `pyproject.toml` — locked in
   `uv.lock`. Add: `uv add --group test LIB` and the suite must **skip, not
   error**, without it (`pytest.importorskip` at module level — the jinja2
   pattern in `tests/herdr/test_user_acceptance.py`). Remove: `uv remove
   --group test LIB`. `pytest-xdist` is optional by design: a `fast` group or
   a `--with` overlay, since a run without it just cannot use `-n`.
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
