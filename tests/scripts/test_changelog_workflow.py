"""The changelog collector must keep its two failure paths closed.

A workflow is easy to edit into silence. These tests hold the properties
that decide whether a collection can be recovered and whether a rejected
push loses the fragment forever.

The failure this file exists for, measured 2026-10-30: PR #106's
collector built its commit on its own merge commit and pushed fifteen
seconds later. PR #107 merged onto that commit in between, so the push
was rejected as a non-fast-forward. The run went red, the commit died
with the runner, and the fragment sat on `main` with no changelog entry
for a week. Nothing retried, and nothing could be re-run by hand.

So the two properties:

1. A rejected push is replayed onto the new base and retried, a bounded
   number of times. A collector that gives up on the first rejection
   loses the entry.
2. A failed collection can be re-run by a human. A workflow with no
   dispatch trigger is unrecoverable once it goes red.
"""

from __future__ import annotations

import pathlib

import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "changelog.yml"


def _workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _triggers() -> dict:
    workflow = _workflow()
    # YAML 1.1 parses a bare `on:` key as boolean True.
    return workflow.get("on") or workflow.get(True) or {}


def _collect_step() -> dict:
    job = _workflow()["jobs"]["collect"]
    steps = [s for s in job["steps"] if "run" in s]
    assert steps, "the collect job runs no script — this guard would pass vacuously"
    return steps[0]


def _runs() -> str:
    return _collect_step()["run"]


def _collect_env() -> dict:
    return _collect_step().get("env", {})


# Reviewed action pins. Moving one needs the new value confirmed
# upstream, so the change lands here in the same commit. Shape is not
# evidence: a hallucinated SHA is well-formed and this repo merged one.
REVIEWED_PINS = {
    "actions/checkout": "11d5960a326750d5838078e36cf38b85af677262",
    "astral-sh/setup-uv": "d0cc045d04ccac9d8b7881df0226f9e82c39688e",
}


def test_it_still_runs_when_a_pr_merges():
    triggers = _triggers()
    pull_request = triggers.get("pull_request", {})
    assert "closed" in pull_request.get("types", []), (
        "the collector no longer runs on a merged PR, so nothing is collected"
    )
    assert "main" in pull_request.get("branches", []), (
        "the collector no longer scopes to main, so per-topic changelogs could "
        "be collected into the repository changelog"
    )


def test_it_does_not_run_on_a_closed_unmerged_pr():
    """A closed-without-merge PR has no main commit to collect into."""
    condition = str(_workflow()["jobs"]["collect"]["if"])
    assert "merged == true" in condition, (
        "the job does not gate on merged == true; a PR closed without merging "
        "would try to collect into a main it never reached"
    )


def test_collections_are_serialized():
    concurrency = _workflow().get("concurrency", {})
    assert concurrency.get("group") == "changelog-main", (
        "the collector is not serialized; two collections can rewrite "
        "CHANGELOG.md and one push loses"
    )
    assert concurrency.get("cancel-in-progress") is False, (
        "cancel-in-progress would abandon a collection mid-run and strand its fragment"
    )


def test_a_failed_collection_can_be_retried():
    """The only recovery path for a red run. Without it, stuck."""
    dispatch = _triggers().get("workflow_dispatch")
    assert dispatch is not None, (
        "no workflow_dispatch trigger; a failed collection cannot be re-run "
        "from the Actions tab, so its fragment needs a hand-built commit"
    )
    inputs = dispatch.get("inputs", {})
    assert "pr_number" in inputs, (
        "the manual trigger takes no PR number, so a re-run cannot know which "
        "PR's fragments to collect"
    )
    assert inputs["pr_number"].get("required") is True, (
        "pr_number is optional, so a manual run can start without saying which "
        "fragment to collect"
    )
    assert "inputs.pr_number" in _collect_env().get("PR_NUMBER", ""), (
        "the collect step reads only the event payload; a manual run has no "
        "pull_request, so it would fail or collect the wrong PR"
    )


def test_it_checks_out_the_merge_commit_not_the_pr_head():
    """The PR head is untrusted and is not what main now contains."""
    workflow = _workflow()
    checkout = [
        s
        for s in workflow["jobs"]["collect"]["steps"]
        if str(s.get("uses", "")).startswith("actions/checkout@")
    ]
    assert checkout, "no checkout step — this guard would pass vacuously"
    ref = str(checkout[0].get("with", {}).get("ref", ""))
    assert "pull_request.merge_commit_sha" in ref, (
        "the checkout no longer uses the merged commit; collecting from the PR "
        "head would build the entry on a tree main never had"
    )


def test_a_rejected_push_is_replayed_onto_the_new_base():
    runs = _runs()
    assert "git fetch origin main" in runs, (
        "the push is never retried against a fresh main, so any merge that "
        "lands during the run loses the entry"
    )
    assert "git rebase origin/main" in runs, (
        "a retry without rebasing would push the same stale base and be rejected again"
    )
    assert "while :; do" in runs or "while true" in runs, (
        "there is no retry loop; a single push attempt is the 2026-10-30 defect"
    )


def test_the_retry_is_bounded():
    """A loop that never gives up hides a failure as a transient."""
    runs = _runs()
    assert "attempts" in runs, "the retry does not count its attempts"
    assert "-ge 3" in runs, (
        "the retry has no attempt ceiling; a persistently rejected push would "
        "spin until the job timeout instead of failing loudly"
    )
    assert "::error::" in runs, (
        "giving up does not emit an error annotation, so the reason a fragment "
        "stayed uncollected is buried in the log"
    )


def test_the_guard_holds_after_the_replay():
    """A rebase must not be able to smuggle in an unrelated change."""
    runs = _runs()
    assert "git diff --exit-code HEAD^ HEAD" in runs, (
        "the retry replay has no guard, so a rebase could commit a change "
        "outside the changelog and its fragments"
    )


def test_a_fragment_less_pr_still_exits_clean():
    """The common case must not enter the retry path."""
    runs = _runs()
    assert "nothing to collect" in runs, (
        "the no-fragment path is gone; most merged PRs carry no fragment and "
        "must exit 0 without pushing"
    )


def _loop_body(runs: str, marker: str) -> str:
    """The body of the first while-loop containing `marker`."""
    start = runs.index(marker)
    loop_start = runs.rindex("while IFS= read -r fragment; do", 0, start)
    return runs[loop_start : runs.index("done <", loop_start)]


def test_a_repeated_collection_is_a_no_op():
    """A second manual re-run must not fail on a deleted fragment.

    Pressing Re-run twice is the natural response to not knowing
    whether the first one worked. Under `set -euo pipefail` a bare
    `test -f` on the already-deleted fragment exits 1, so the second
    press reports failure for a PR whose entry is already correct —
    which teaches that a red collection run is noise.

    Assert the branch, not the message: "already collected" also
    appears in the nothing-left-to-move block below the loop, so a
    grep for it stays green against the unfixed loop.
    """
    body = _loop_body(_runs(), 'mv -- "$fragment"')

    assert "! -f" in body, (
        "the fragment loop assumes every fragment still exists; a re-run after "
        "a successful collection finds it deleted and exits 1"
    )
    assert "continue" in body, (
        "a missing fragment must skip to the next one, not abort the loop"
    )


def test_a_fully_collected_rerun_exits_clean():
    """Nothing left to move must end green, not fall through.

    Falling through would reach `scriv collect` with an empty
    directory, which exits 2, and then the retry loop, which would
    report a rejected push for a collection it never had to make.
    """
    runs = _runs()
    body = _loop_body(runs, 'mv -- "$fragment"')
    after_loop = runs[runs.index("done <", runs.index('mv -- "$fragment"')) :]

    assert "already collected" in body, (
        "a re-run with nothing left to collect must say so inside the loop"
    )
    assert "ls -A" in after_loop and "exit 0" in after_loop, (
        "the empty-directory check must exit 0 before scriv runs; falling "
        "through collects nothing and reports a failure for a finished PR"
    )


def test_a_partially_collected_pr_still_collects_the_rest():
    """One fragment already gone must not stop the remaining ones.

    Skipping per fragment rather than aborting the loop is what
    keeps a PR with two fragments converging when only one was
    collected.
    """
    runs = _runs()
    body = _loop_body(runs, 'mv -- "$fragment"')

    assert "continue" in body, (
        "a missing fragment must not abort the loop; a partially-collected PR "
        "would never collect its remaining fragments"
    )

    rm_loop = _loop_body(runs, 'git rm -- "$fragment"')
    assert "if [[ -f" in rm_loop, (
        "the cleanup loop removes every listed fragment unconditionally, which "
        "fails on one that a previous run already deleted"
    )


def test_every_action_pin_is_the_reviewed_one():
    workflow = _workflow()
    uses = [
        step["uses"] for step in workflow["jobs"]["collect"]["steps"] if "uses" in step
    ]
    assert uses, "the job uses no actions — this guard would pass vacuously"

    for ref in uses:
        action, _, pinned = ref.partition("@")
        owner_repo = "/".join(action.split("/")[:2])
        assert owner_repo in REVIEWED_PINS, (
            f"{owner_repo} is pinned but not reviewed; add its SHA to "
            f"REVIEWED_PINS after confirming it upstream"
        )
        assert pinned == REVIEWED_PINS[owner_repo], (
            f"{owner_repo} is pinned to {pinned}, not the reviewed "
            f"{REVIEWED_PINS[owner_repo]}"
        )
