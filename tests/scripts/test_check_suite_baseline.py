"""Reject regressions, and refuse to pass on no evidence.

The script exists because a CI job cannot assert "12 failed" — that
number stays 12 while one suite is fixed and another regresses.
These tests pin the two properties that make it worth running:

1. A failure outside the known-failure baseline is reported.
2. A run with no summary line is an error, not a pass. That is the
   shape this repo has been bitten by repeatedly: a check that
   silently matches nothing looks exactly like a check that passed.
"""

from __future__ import annotations

import importlib.util
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location(
    "check_suite_baseline", REPO / "scripts" / "check_suite_baseline.py"
)
assert _spec is not None and _spec.loader is not None
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)


CLEAN = """
FAILED tests/clipped/test_clipped_cli.py::test_copy_multiple_files - AssertionError: x
FAILED tests/restart_stale/test_role.py::test_a_missing_kind - AssertionError: y
13 failed, 1206 passed, 21 skipped in 646.24s
"""


def test_known_failures_alone_pass():
    unexpected, _, saw = check.judge(CLEAN)
    assert saw
    assert unexpected == set()


def test_a_failure_outside_the_baseline_is_reported():
    report = (
        CLEAN + "FAILED tests/chezmoi/test_czd.py::test_something - AssertionError\n"
    )
    unexpected, _, saw = check.judge(report)
    assert saw
    assert unexpected == {"tests/chezmoi/test_czd.py::test_something"}


def test_no_summary_line_is_not_a_pass():
    """A run that died early has an unknown result, never a pass."""
    _, _, saw = check.judge("collection error: no tests ran\n")
    assert not saw


def test_empty_output_is_not_a_pass():
    _, _, saw = check.judge("")
    assert not saw


def test_a_missing_report_file_is_an_error(tmp_path, capsys):
    code = check.main([str(tmp_path / "absent.txt")])
    assert code == 2
    assert "no test ever ran" in capsys.readouterr().err


def test_the_summary_line_alone_is_enough(tmp_path, capsys):
    report = tmp_path / "r.txt"
    report.write_text("13 failed, 1206 passed in 1s\n")
    assert check.main([str(report)]) == 0


def test_a_regression_exits_one(tmp_path, capsys):
    report = tmp_path / "r.txt"
    report.write_text(
        "1 failed, 10 passed\nFAILED tests/things/test_thing.py::test_x\n"
    )
    assert check.main([str(report)]) == 1
    assert "tests/things/test_thing.py::test_x" in capsys.readouterr().err
