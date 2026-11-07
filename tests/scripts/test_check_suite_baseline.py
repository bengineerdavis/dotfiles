"""Reject regressions, and refuse to pass on no evidence.

The script exists because a CI job cannot assert "12 failed" — that
number stays 12 while one suite is fixed and another regresses.
These tests pin the properties that make it worth running:

1. A node ID outside the baseline is reported, whichever suite it
   lives in. The first version matched whole directories, so a new
   failure inside `tests/clipped/` passed silently.
2. An ERROR is reported. Collection and fixture errors do not appear
   in the summary's "N failed" count, so a run can report
   "1 passed, 1 error" and be green under a failures-only check.
3. A run with no summary line is an error, not a pass.
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


KNOWN = sorted(check.EXPECTED_FAILURES)


def _report(failed: list[str], total: int = 13) -> str:
    lines = [f"FAILED {nodeid} - AssertionError: x" for nodeid in failed]
    lines.append(f"{total} failed, 1206 passed, 21 skipped in 646.24s")
    return "\n".join(lines) + "\n"


def test_known_failures_alone_pass():
    unexpected, absent, saw = check.judge(_report(KNOWN))
    assert saw
    assert unexpected == set()
    assert absent == set()


def test_a_failure_outside_the_baseline_is_reported():
    report = _report([*KNOWN, "tests/chezmoi/test_czd.py::test_something"])
    unexpected, _, saw = check.judge(report)
    assert saw
    assert unexpected == {"tests/chezmoi/test_czd.py::test_something"}


def test_a_new_failure_inside_a_known_suite_is_reported():
    """Matching directories hid a regression beside a known failure."""
    report = _report([*KNOWN, "tests/clipped/test_new.py::test_regression"])
    unexpected, _, _ = check.judge(report)
    assert unexpected == {"tests/clipped/test_new.py::test_regression"}


def test_an_error_is_reported():
    """An ERROR is not a failed count, so failures-only checks miss."""
    report = (
        "1 passed, 1 error in 2.0s\nERROR tests/x/test_y.py::test_z - RuntimeError\n"
    )
    unexpected, _, saw = check.judge(report)
    assert saw
    assert unexpected == {"tests/x/test_y.py::test_z"}


def test_a_stale_baseline_entry_is_reported_but_not_fatal(tmp_path, capsys):
    partial = KNOWN[:-1]
    report = tmp_path / "r.txt"
    report.write_text(_report(partial, total=12))
    assert check.main([str(report)]) == 0
    assert KNOWN[-1] in capsys.readouterr().err


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


def test_a_regression_exits_one(tmp_path, capsys):
    report = tmp_path / "r.txt"
    report.write_text(
        "1 failed, 10 passed\nFAILED tests/things/test_thing.py::test_x\n"
    )
    assert check.main([str(report)]) == 1
    assert "tests/things/test_thing.py::test_x" in capsys.readouterr().err
