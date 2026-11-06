"""Constants shared by the pii-redactor fixtures and tests.

Deliberately not conftest.py: every conftest is imported as a top-level
module named `conftest`, so `from conftest import ...` resolves to whichever
one pytest imported first. `SCRIPT` in particular is defined by both this
suite and tests/clipped, so a shared conftest slot resolves it to the wrong
binary without raising. See tests/guards/guard_harness.py.
"""

from __future__ import annotations

import atexit
import pathlib
import shutil
import tempfile


def _resolve_script() -> pathlib.Path:
    """The pii-redactor source, whether or not it has been deployed.

    The suite used to hardcode `~/bin/pii-redactor`. That file exists only
    after `chezmoi apply`, so on a fresh clone — and in CI — the whole suite
    failed on `FileNotFoundError`, which was 55 of CI's 64 failures.

    The tests need the script's SOURCE, which is always present in the repo.
    Prefer the deployed copy when it exists, because that is what a user runs.

    The source is stored mode 644: chezmoi records `executable_` in the name
    and applies the bit at deploy time. Running it in place therefore fails
    with `PermissionError`, so the fallback copies it to a temp directory and
    marks that copy executable rather than chmod-ing a tracked file (which
    would dirty the working tree and fight the chezmoi state).
    """
    deployed = pathlib.Path.home() / "bin" / "pii-redactor"
    if deployed.is_file():
        return deployed

    # tests/pii_redactor/pii_redactor_harness.py -> repo root
    repo = pathlib.Path(__file__).resolve().parents[2]
    source = repo / "home" / "bin" / "executable_pii-redactor"
    staging = pathlib.Path(tempfile.mkdtemp(prefix="pii-redactor-source-"))
    atexit.register(shutil.rmtree, staging, ignore_errors=True)
    runnable = staging / "pii-redactor"
    shutil.copyfile(source, runnable)
    runnable.chmod(0o755)
    return runnable


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
