"""A missing optional dependency must skip, not error — and must not skip when
the dependency is actually there.

`docs/PYTHON.md` § Dependency classes: a test-run dependency the suite lacks is
a skip with a named reason. An error is worse than a skip because it aborts the
directory — `tests/ollama_evals` used to produce 53 setup errors without
`--with pillow` and take every test in it down. Both directions are asserted,
because a fixture that skipped unconditionally would report a clean run having
tested nothing (`spec.md` § Verification — a capability gate marks work
not-applicable, and then a test shows a CAPABLE subject is not skipped).
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
# Smallest directory whose session fixture loads the Pillow-importing harness.
TARGET = "tests/ollama_evals/test_capability_gate.py"


def _run(env_pythonpath: str | None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    if env_pythonpath is None:
        env.pop("PYTHONPATH", None)
    else:
        env["PYTHONPATH"] = env_pythonpath
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=no", "-p", "no:cacheprovider", TARGET],
        capture_output=True, text=True, cwd=str(REPO), env=env, timeout=180,
    )


def _body(proc: subprocess.CompletedProcess) -> str:
    return proc.stdout + proc.stderr


def test_missing_optional_dependency_skips_instead_of_erroring(tmp_path):
    """A stub PIL that raises on import stands in for an uninstalled Pillow."""
    (tmp_path / "PIL.py").write_text('raise ImportError("PIL blocked by tests/suite")\n')
    proc = _run(str(tmp_path))
    out = _body(proc)
    # spec.md § Verification: assert the output is non-empty before grepping it
    # — `assert "error" not in ""` passes vacuously and would read as a pass.
    assert out.strip(), "the nested pytest produced no output at all"
    assert "error" not in out.lower(), (
        f"a missing optional dependency must skip, not error:\n{out[-800:]}"
    )
    assert "skipped" in out, f"expected skips with PIL blocked:\n{out[-800:]}"


def test_present_optional_dependency_runs_the_suite():
    pytest.importorskip("PIL")
    out = _body(_run(None))
    assert out.strip(), "the nested pytest produced no output at all"
    assert "passed" in out, (
        f"a capable subject must not be skipped when its dependency is "
        f"present:\n{out[-800:]}"
    )
