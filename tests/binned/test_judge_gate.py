"""The cheap gate in front of the LLM judge panel.

Real test results are the signal. The judge panel is expensive — several model
calls — and it exists to answer "is this script any good?" when nothing cheaper
can. Generated tests answer that question directly and for free, so the panel
should only be convened when they could not.

The subtle half is what counts as "could not". A test run that did not happen is
not a pass, and the code this replaces conflated the two: run_bats returned True
when bats was not installed, so a machine without bats reported success. Wire
that into a gate and the panel is silently skipped exactly where it is needed
most — which is AGENTS.md § Prove the test fails, "turn unknown into a claim",
arriving in production rather than in a mutation.
"""

from __future__ import annotations

import pytest


# ── run_bats must distinguish "could not run" from "passed" ──────────────────


def test_run_bats_returns_none_when_bats_is_missing(
    binned_module, monkeypatch, tmp_path
):
    """None means undeterminable. True would mean the tests passed, which is a
    claim nobody made.
    """
    monkeypatch.setattr(binned_module.shutil, "which", lambda _: None)
    t = tmp_path / "x.bats"
    t.write_text("@test 'ok' { true; }\n")
    assert binned_module.run_bats(t) is None


def test_run_bats_still_reports_real_results(binned_module, monkeypatch, tmp_path):
    """The relenting direction: when bats IS present, the boolean must still be
    a real pass/fail, not swallowed by the new None path.
    """
    import subprocess

    monkeypatch.setattr(binned_module.shutil, "which", lambda _: "/usr/bin/bats")
    t = tmp_path / "x.bats"
    t.write_text("@test 'ok' { true; }\n")

    monkeypatch.setattr(
        binned_module.subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(a, 0),
    )
    assert binned_module.run_bats(t) is True

    monkeypatch.setattr(
        binned_module.subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(a, 1),
    )
    assert binned_module.run_bats(t) is False


# ── the gate decision, extracted so it is testable without running anything ──


@pytest.mark.parametrize(
    "outcome,should_judge,expected,why",
    [
        ("inconclusive", True, True, "no signal — this is what the panel is for"),
        (
            "passed",
            True,
            False,
            "tests already answered; panel adds cost, not information",
        ),
        (
            "failed",
            True,
            False,
            "tests already answered; fix the failures, do not poll models",
        ),
        (None, True, True, "no tests at all is the emptiest signal there is"),
        (
            "inconclusive",
            False,
            False,
            "the user turned judging off; the gate must not turn it back on",
        ),
        ("passed", False, False, "off is off"),
    ],
)
def test_gate_decides_when_to_escalate(
    binned_module, outcome, should_judge, expected, why
):
    result = None if outcome is None else binned_module.TestOutcome(outcome, "")
    assert binned_module.judges_needed(result, should_judge) is expected, why


def test_gate_never_escalates_on_a_lint_result(binned_module):
    """Formatting and lint are fix-as-you-go, never gate criteria. A lint
    failure must not convene a panel, and must not suppress one either.
    """
    passed = binned_module.TestOutcome(
        "passed", "3 passed; ruff reported 2 style issues"
    )
    assert binned_module.judges_needed(passed, True) is False


# ── the runner must return a real outcome ────────────────────────────────────


def test_run_tests_reports_inconclusive_when_there_are_no_tests(binned_module):
    assert (
        binned_module._run_tests_in_tmpdir("#!/bin/sh\n", "x", {}).outcome
        == "inconclusive"
    )


def test_run_tests_reports_inconclusive_when_no_runner_is_installed(
    binned_module, monkeypatch
):
    """A machine with neither bats nor pytest has learned nothing about the
    script. Reporting 'passed' here is how the panel gets skipped silently.
    """
    monkeypatch.setattr(binned_module.shutil, "which", lambda _: None)
    out = binned_module._run_tests_in_tmpdir(
        "#!/bin/sh\necho hi\n", "x", {"x.bats": "@test 'a' { true; }\n"}
    )
    assert out.outcome == "inconclusive", out
