"""The llm_judge filter must decline by default and relent on request.

`spec.md` § Verification: a guard that can decline needs both directions
proven. `addopts = -m "not llm_judge"` keeps model-calling tests out of a bare
run — they load local models (a cold load can kill the shared Ollama daemon),
cost tokens on hosted judges, and append to the shared `llm` log — so the
default must exclude them and `-m llm_judge` must bring them back. A filter
that only ever declined would look identical to one that had quietly deleted
the tests, which is why the relent direction gets asserted too.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]

# Both files carry a module-level `pytestmark = pytest.mark.llm_judge`, so a
# default run must collect nothing from them and an explicit `-m llm_judge`
# must collect some. Sourcing them by path keeps the nested run fast.
MODEL_TEST_FILES = [
    "tests/binned/test_binned_llm_judge.py",
    "tests/pii_redactor/test_pii_redactor_llm.py",
]


def _collect(extra: list[str]) -> list[str]:
    """Node ids a run would execute. Exit 5 (nothing collected) is a valid
    empty answer, not a failure — the declines case expects exactly that."""
    proc = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "--collect-only", "-q", "-p", "no:cacheprovider",
            *extra, *MODEL_TEST_FILES,
        ],
        capture_output=True, text=True, cwd=str(REPO), timeout=120,
    )
    # 2=interrupted 3=internal error 4=usage error. Those are defects here, not
    # a decline — assert them away so a broken import cannot masquerade as
    # "the filter declined".
    assert proc.returncode not in (2, 3, 4), (
        f"collection failed (rc={proc.returncode}):\n{proc.stdout}\n{proc.stderr}"
    )
    return [line for line in proc.stdout.splitlines() if "::" in line]


def test_default_run_declines_the_model_tests():
    assert _collect([]) == [], (
        "a bare pytest run must not collect model-calling tests"
    )


def test_explicit_marker_relights_the_model_tests():
    assert _collect(["-m", "llm_judge"]), (
        "pytest -m llm_judge must collect the model-calling tests"
    )
