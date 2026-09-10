# PYTHON.md

Python conventions for this repository.

`AGENTS.md` stays general so it can be reused across projects. Conventions are
pluggable and live in `conventions/`, one file per subject. This is the Python
one. A repo that adds Go gets `conventions/GO.md` and changes nothing in
`AGENTS.md` except the pointer. See `conventions/README.md`.

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
- **Do not hide or wrap errors.** Swallowing an exception turns a fixable failure
  into a mystery. Where an error genuinely must not escape, convert it
  deliberately at a boundary and keep the message: `run_check` turns any raise
  into a named failure rather than discarding it, which is why a broken check
  reports itself instead of aborting the run.

## Choosing Python at all

`AGENTS.md` § Languages holds the bash-versus-Python rule, because deciding
which language to use is a repository-level question rather than a Python one.
