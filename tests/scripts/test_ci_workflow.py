"""The CI gate must keep doing the things that make it a gate.

A workflow file is easy to edit into silence. These tests hold the
properties that decide whether it catches anything:

1. A test job exists at all. The repo's other checks are pre-commit
   hooks, which run only on a machine where `prek install` was done.
   Without a CI job a contributor with no hooks, or one who bypassed
   them, merges untested.
2. The suite is judged by `check_suite_baseline.py`, not by pytest's
   exit status. Twelve known failures make a bare `pytest` exit
   nonzero, so a job keyed on the exit code is either always red or
   silenced with `|| true`.
3. The compare step reads the captured log. Judging a file that was
   never written is the silent-pass shape this repo keeps hitting.
"""

from __future__ import annotations

import pathlib

import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "tests.yml"


def _workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _runs(job: dict) -> str:
    return "\n".join(str(step.get("run", "")) for step in job["steps"] if "run" in step)


def test_a_test_job_exists():
    workflow = _workflow()
    assert "tests" in workflow["jobs"], (
        "no test job in CI: every check is a local pre-commit hook, so a "
        "fresh clone has none of them"
    )


def test_the_suite_runs():
    job = _workflow()["jobs"]["tests"]
    assert "pytest tests tools" in _runs(job), (
        "the CI job does not run the suite AGENTS.md documents"
    )


def test_the_result_is_judged_against_the_baseline():
    """Pytest exits nonzero here, so its status is not the gate."""
    job = _workflow()["jobs"]["tests"]
    assert "check_suite_baseline.py" in _runs(job), (
        "the job does not compare failures against the known-failure "
        "baseline, so it is either always red or silenced"
    )


def test_the_baseline_reads_the_captured_log():
    """Judging a log never written is a pass with no evidence."""
    job = _workflow()["jobs"]["tests"]
    runs = _runs(job)
    assert "tee " in runs, "pytest output is not captured to a file"
    assert "pytest.log" in runs, "the compare does not read the captured log"


def test_the_baseline_script_exists_where_the_workflow_calls_it():
    job = _workflow()["jobs"]["tests"]
    assert (REPO / "scripts" / "check_suite_baseline.py").is_file(), (
        "the workflow calls a script that is not in the repo"
    )
    assert pathlib.Path("scripts/check_suite_baseline.py").as_posix() in _runs(job)
