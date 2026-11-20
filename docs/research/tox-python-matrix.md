# tox + tox-uv for a Python-version matrix

Research for proving the dotfiles Python payload works across stable Python
versions, and for pre-proving an interpreter upgrade before adopting it.

Decision taken by the author (2026-11-17): use **tox with tox-uv**. This file
records the facts needed to implement that well, plus what was rejected.

## Versions verified on this machine

Measured, not recalled:

```
$ uv tool run --from tox --with tox-uv tox --version
4.67.13
registered plugins:
    tox-uv-bare-1.37.7 ... with uv==0.13.9
```

- **tox 4.67.13** (docs read at 4.38.0; the settings cited below are unchanged
  or newer, and each was checked against `tox config` where it mattered).
- **tox-uv 1.37.7**, PyPI release 2026-11-07, MIT, requires Python >=3.11
  (<https://pypi.org/project/tox-uv/>).
- `tox-uv` ships as two packages: `tox-uv` (bundles a `uv` binary) and
  `tox-uv-bare` (plugin only, uses `uv` from `PATH`). The resolved install here
  pulled **bare**, using the system `uv 0.13.9`. On this machine that is the
  right one: `uv` is deliberately not mise-managed (`docs/PYTHON.md`), so a
  second bundled copy would be a duplicate.

## The requirement, stated once

> Prove that the Python this repo ships actually **runs** on every Python
> version it claims, and prove a future interpreter bump is safe **before** the
> bump lands — not merely that the files parse.

The disqualifying gap: `tests/test_python_floors.py` already parses every file at
its declared floor, but **parsing is not running**. Proven below.

## The gap, measured

`tests/test_python_floors.py` uses `ast.parse(feature_version=floor)`. It cannot
see a missing stdlib module, a removed attribute, or a behaviour change.

```
$ uv run --python 3.10 --no-project python -c "import tomllib"
ModuleNotFoundError: No module named 'tomllib'
```

That file parses fine at a 3.10 floor and dies at import. The two payload scripts
that import `tomllib` (`home/bin/executable_binned`,
`home/bin/executable_model-bench`) both correctly declare `>=3.11`, so there is
**no live bug today** — but nothing enforces that declaration. A future edit that
adds `import tomllib` to a `>=3.10` script would pass the floors test and fail on
Debian 12's `/usr/bin/python3` (3.10.12).

The same class bit this machine on 2026-11-17: `ansible-playbook` broke with
`AttributeError: module 'dataclasses' has no attribute '_is_type'` — a 3.15
removal that no parse test can see.

## The constraint that shapes the config

`pyproject.toml` declares `requires-python = ">=3.14"`.

**This means a naive full-suite matrix cannot work.** tox creates an environment
per interpreter and installs the project into it; on 3.10 or 3.11 the *install*
fails before a single test runs, because the project itself refuses those
versions. A matrix written as "run `pytest` on 3.10, 3.11, 3.14, 3.15" produces
four env-creation failures and teaches nothing.

The matrix therefore has to test **two different things**:

| Layer         | What runs                              | Interpreters | Why                                                                               |
| ------------- | -------------------------------------- | ------------ | --------------------------------------------------------------------------------- |
| Project suite | `pytest tests tools`                   | 3.14, 3.15   | The project's own `requires-python` floor is 3.14; 3.15 is the pending bump       |
| Payload smoke | import + `--help` each deployed script | 3.10, 3.11   | The declared script floors; these run under the host interpreter, not the project |

This split is not a compromise — it reflects reality. The repo contains two
populations of Python with two different floors, and only a matrix that models
both proves anything.

Both halves were run on this machine rather than reasoned about:

```
# project env on 3.14 — works
3.14: uv-sync> uv sync --locked --python-preference system --no-default-groups --group test
RAN ON 3.14.10
  3.14: OK (1.60=setup[1.57]+cmd[0.03] seconds)

# payload env on 3.10 — works, and installs no project
payload-3.10: OK (0.59=setup[0.57]+cmd[0.02] seconds)
PAYLOAD RAN ON 3.10.22

# naive project env on 3.10 — fails at sync, before any test
error: The requested interpreter resolved to Python 3.10.22, which is
incompatible with the project's Python requirement: `>=3.14`
  3.10: FAIL code 2
```

Note the `--locked` in the 3.14 sync: the committed lock is authoritative, so a
stale `uv.lock` fails loudly instead of silently re-resolving against this
machine's employer PyPI mirror.

## Interpreter provisioning

tox-uv uses `uv venv`, so **uv provisions interpreters on demand** — the same
machinery as `uv python install`. Verified on this machine: `uv run --python 3.10` fetched and ran CPython 3.10.22 with no prior install.

Consequence: `skip_missing_interpreters` matters less than expected, because uv
can fetch what is absent. But it still should be set, for two reasons:

1. A machine with no network cannot provision, and a hard failure there is noise.
1. `skip_missing_interpreters = true` returns **success** when envs are missing.
   That is exactly the "silently reduce coverage" failure the repo forbids
   elsewhere (`docs/TOPIC-RECIPES.md`, the Molecule matrix rule).

**Recommended: leave it at the default (`config`, i.e. unset) so a missing
interpreter fails loudly**, and let uv's download fill the gap. If a genuinely
offline machine needs a pass, pass `--skip-missing-interpreters` explicitly on
that invocation — an explicit choice, not a silent default.

Docs: <https://tox.wiki/en/4.38.0/reference/config.html#skip_missing_interpreters>

## PEP 735 dependency groups — the setting this repo needs

The repo uses `[dependency-groups]` (`test`, `test-llm`, `test-vm`, `lint`,
`tools`), **not** `[project.optional-dependencies]` extras. So `extras` is the
wrong setting.

tox 4.22 added **`dependency_groups`** (PEP 735). Verified in the reference:

> A list of names of dependency groups (as defined by PEP 735) to install into
> this Python environment. The installation will happen before installing the
> package or any of its dependencies.
> — <https://tox.wiki/en/4.38.0/reference/config.html#dependency_groups>

And tox-uv documents the same name mapping to `uv sync --group`:

> `dependency_groups` — Specify PEP 735 Dependency Groups to install **in
> addition to** the project and its dependencies (maps to `uv sync --group`).
> — <https://pypi.org/project/tox-uv/>

There is also `only_groups` (maps to `uv sync --only-group`) which excludes the
project entirely. Not wanted here: the suite imports repo modules.

## uv.lock is respected

tox-uv adds `uv-venv-lock-runner`, which runs `uv sync` instead of `uv pip install`. Relevant details from the tox-uv docs:

- By default it passes **`--locked`**, so a stale `uv.lock` fails rather than
  silently re-resolving. That is the behaviour this repo wants — `uv.lock` is
  committed and `--frozen` is a standing rule.
- `UV_FROZEN=1` makes tox-uv pass `--frozen` instead, skipping
  platform-metadata validation. Useful in CI where the lock was made on macOS
  and runs on Linux.
- `uv_sync_flags` accepts extra flags; if `--frozen` appears there, tox-uv
  suppresses the implicit `--locked` automatically (they are mutually
  exclusive).

**Gotcha for this repo**: `uv run` without `--frozen` re-locks `uv.lock` against
the machine's configured index, which on this Mac is the employer's private PyPI
mirror. A tox run that re-locks would leak employer URLs into a committed file.
The `uv-venv-lock-runner` default of `--locked` prevents this; do not switch to
a runner that resolves.

## Proposed configuration

`tox.toml` (TOML is the documented recommendation for new projects;
<https://tox.wiki/en/4.38.0/reference/config.html#discovery-and-file-types>).
Placed at repo root.

```toml
# tox.toml — prove the Python payload runs on every version it claims.
#
# Two populations, two floors:
#   - the project declares requires-python >=3.14, so only 3.14+ can install it
#   - deployed payload scripts declare their own floors down to 3.10
# A single "run pytest everywhere" matrix would fail at env creation on 3.10.

requires = ["tox>=4.22", "tox-uv>=1.37"]

env_list = ["3.14", "3.15", "payload-3.10", "payload-3.11"]

[env_run_base]
runner = "uv-venv-lock-runner"
dependency_groups = ["test"]
commands = [["pytest", "tests", "tools", "-q"]]

# The pending interpreter bump: same suite, newer interpreter.
[env."3.15"]

# Payload smoke tests: the deployed scripts run under whatever interpreter the
# host provides, not under the project venv, so they are tested with --no-project.
[env."payload-3.10"]
runner = "uv-venv-runner"
skip_install = true
dependency_groups = []
commands = [
  ["python", "{tox_root}/scripts/check_payload_imports.py", "--floor", "3.10"],
]

[env."payload-3.11"]
runner = "uv-venv-runner"
skip_install = true
dependency_groups = []
commands = [
  ["python", "{tox_root}/scripts/check_payload_imports.py", "--floor", "3.11"],
]
```

Notes on each choice:

- `env_list` names use the dotted form (`3.14`), which the docs prefer over
  `py314` — clearer for versions >= 3.10.
- `runner = "uv-venv-lock-runner"` is what makes `uv.lock` authoritative.
- `dependency_groups = ["test"]` mirrors CI's `uv sync --group test`.
- `skip_install = true` on the payload envs is essential: the project cannot be
  installed on 3.10.
- The payload command is a small script (not yet written) that imports each
  deployed script at the given floor and checks it does not blow up. That script
  is the actual deliverable; the tox config is the harness around it.

### What the payload script must do

For each file under `home/bin/` and `scripts/` whose declared floor is `<=` the
target, run `python -c "import runpy; runpy.run_path(...)"` **or** at minimum
`ast.parse` + a targeted import check of its stdlib dependencies. The measured
gap is `import tomllib` on 3.10; a check that only parses would miss exactly
that, so the script must import the module's stdlib dependencies, not just parse
it.

## CI integration

The tox docs give the GitHub Actions shape:

```yaml
- uses: astral-sh/setup-uv@v5
- run: uv tool install tox --with tox-uv
- run: tox run -e ${{ matrix.python-version }}
```

— <https://tox.wiki/en/4.38.0/how-to/usage.html#use-tox-in-ci-cd-pipelines>

Two adjustments for this repo:

1. **Do not use `actions/setup-python`** as the docs' example does. tox-uv gets
   interpreters from uv, so `setup-python` is a redundant second provisioner —
   the exact "two installation channels" the repo's one-canonical-artifact rule
   forbids.
1. **`UV_FROZEN=1`** in the job env, so the lock made on macOS validates on
   `ubuntu-latest` without platform-metadata complaints.
1. Keep the existing baseline gate. tox's exit code is the suite's exit code, and
   the repo's known-failures gate reads a pytest log — so either tox writes the
   log (`commands = [["pytest", "tests", "tools", "-q", "--junitxml=..."]]` plus
   a tee) or the gate is adapted. **This is the one piece that needs a decision
   during implementation**, because the current gate parses `FAILED <nodeid>`
   lines from a pytest log file.

## Cost

The full suite is ~1548 tests, ~6 min. A 2-interpreter project matrix is
therefore ~12 min, plus two fast payload envs. That is acceptable for CI and too
slow for a commit hook; run `tox run -e 3.14` locally for the fast loop.

## Rejected alternatives

**uv-native matrix, no tox.** `for v in 3.10 3.11 3.14 3.15; do uv run --python $v pytest; done`, or a Makefile pattern rule with `UV_PROJECT_ENVIRONMENT=.venv-$*`.
This is genuinely sufficient for "same deps, same command, different
interpreter" — which is most of what this repo needs
(<https://pydevtools.com/handbook/explanation/do-you-still-need-tox-or-nox-if-you-use-uv/>).
Rejected by author decision in favour of tox+tox-uv for a single unified
configuration, per-environment reporting, and `tox -e` ergonomics. The cost is a
second toolchain; the benefit is that the matrix is declarative rather than a
shell loop that drifts.

**nox.** Python-configured sessions. Its advantage is conditional logic; this
matrix is static, so that advantage buys nothing, and INI/TOML keeps the config
in the same file family as `pyproject.toml`. Rejected.

**Extending `test_python_floors.py` into a runtime probe only, no tox.** Cheaper
and it would close the `tomllib` gap. Rejected because it hand-rolls interpreter
provisioning and drift-detection that tox+tox-uv already provides, and the author
asked for the matrix.

**`skip_missing_interpreters = true`.** Rejected: it converts "this machine
cannot test 3.10" into a green run. The repo forbids silently reduced coverage
in the Molecule matrix for the same reason.

**`extras` instead of `dependency_groups`.** Rejected: the repo has no
`[project.optional-dependencies]`; its groups are PEP 735. Using `extras` would
install nothing.

## Open items for implementation

1. **The baseline-gate interaction** (above) — the only real design question.
1. Write `scripts/check_payload_imports.py`; it is the actual proof, and the tox
   config is only the harness.
1. Decide whether `3.13`/`3.12` are worth adding. They sit between floors and
   add ~6 min each for no distinct boundary. Recommendation: skip until a
   boundary appears.
1. The global mise config pins `python = "3.15"` while the repo runs 3.14.8. The
   author has stated this was a mistake — interpreter version belongs in the
   repo's ansible/dotfiles config, not global mise. The tox matrix is the
   mechanism that pre-proves the 3.15 move; fixing the global pin is separate
   work.
