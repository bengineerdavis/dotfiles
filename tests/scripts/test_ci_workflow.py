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


# Reviewed action pins: every `uses:` in the test workflow.
# Moving a pin needs the new value confirmed upstream, so it
# lands here in the same commit. A hallucinated SHA is
# well-formed, which is why shape is not a check — the VALUE
# is.
#
# Measured 2026-11-05: `upload-artifact` carried
# `ea165f8d…b4889e4b46c9ffb`, which agrees with the real
# v4.6.2 commit `ea165f8d…b4886f43607fa02` for 28
# characters and invents the last twelve. GitHub could not
# resolve it, and the job failed loading the action after the
# tests had already run.
REVIEWED_PINS = {
    "actions/checkout": "11d5960a326750d5838078e36cf38b85af677262",
    "astral-sh/setup-uv": "d0cc045d04ccac9d8b7881df0226f9e82c39688e",
    "actions/upload-artifact": "ea165f8d65b6e75b540449e92b4886f43607fa02",
}


def test_every_action_pin_is_the_reviewed_one():
    """A pin must be the value someone confirmed, not just a hex string.

    Shape is not evidence: the broken SHA was 40 valid hex
    characters and passed a shape check unchanged. This
    compares the value, so an invented pin fails.
    """
    job = _workflow()["jobs"]["tests"]
    uses = [step["uses"] for step in job["steps"] if "uses" in step]
    assert uses, "the job uses no actions — this guard would pass vacuously"

    for ref in uses:
        action, _, pinned = ref.partition("@")
        # `owner/repo/path` is legal for a subdirectory action.
        owner_repo = "/".join(action.split("/")[:2])
        assert owner_repo in REVIEWED_PINS, (
            f"{owner_repo} is pinned but not reviewed; add its SHA to "
            f"REVIEWED_PINS after confirming it upstream"
        )
        expected = REVIEWED_PINS[owner_repo]
        assert pinned == expected, (
            f"{owner_repo} is pinned to {pinned}, not the reviewed {expected}. "
            f"Confirm the new value against the upstream repo before changing it."
        )
