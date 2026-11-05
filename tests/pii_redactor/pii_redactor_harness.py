"""Constants shared by the pii-redactor fixtures and tests.

Deliberately not conftest.py: every conftest is imported as a top-level
module named `conftest`, so `from conftest import ...` resolves to whichever
one pytest imported first. `SCRIPT` in particular is defined by both this
suite and tests/clipped, so a shared conftest slot resolves it to the wrong
binary without raising. See tests/guards/guard_harness.py.
"""

from __future__ import annotations

import pathlib


def _resolve_script() -> pathlib.Path:
    """The pii-redactor source, whether or not it has been deployed.

    The suite used to hardcode `~/bin/pii-redactor`. That file exists only
    after `chezmoi apply`, so on a fresh clone — and in CI — the whole suite
    silently skipped or failed on `FileNotFoundError`, depending on whether
    the fixture or the process runner got there first.

    The tests need the script's SOURCE, which is always present in the repo;
    running it from the source path exercises the same code. Prefer the
    deployed copy when it exists, because that is what a user runs.
    """
    deployed = pathlib.Path.home() / "bin" / "pii-redactor"
    if deployed.is_file():
        return deployed
    # tests/pii_redactor/pii_redactor_harness.py -> repo root
    repo = pathlib.Path(__file__).resolve().parents[2]
    return repo / "home" / "bin" / "executable_pii-redactor"


SCRIPT = _resolve_script()

# Small local model with thinking disabled, so the real-model tests stay quick.
INTEGRATION_MODEL = "qwen3.5:4b-mlx-bf16"
INTEGRATION_LLM_OPTS = "-o think false"

# A stand-in for a model that does its job: it redacts the one thing the model
# layer is actually responsible for, name-shaped capitalised pairs.
#
# The default used to be a bare `cat`. That is a model which ignores the
# instruction, and pairing it with assertions on exit status and file size meant
# the suite was green precisely when the tool leaked — the defect the three-layer
# rewrite exists to prevent. Tests about output routing should not be riding on a
# broken model, so the default is now a working one; the cases that genuinely
# want a pass-through ask for `cat` explicitly.
WORKING_MODEL = r"sed -E 's/\b[A-Z][a-z]+ [A-Z][a-z]+\b/[NAME]/g'"
