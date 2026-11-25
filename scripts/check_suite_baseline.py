"""Fail a test run whose outcome differs from the known-failure baseline.

`AGENTS.md` § Known failures names the tests that fail on a clean checkout for
reasons outside the code, and states the rule this script enforces: *a change is
green when the failure LIST matches, not when the count does.*

The baseline is a list of exact node IDs, not a list of directories. An earlier
version matched whole suites, which meant a brand-new regression inside a
known-failing suite passed silently — the same silent-pass shape the script
exists to prevent. A regression is a new node ID wherever it lives.

## Why this reads JUnit XML and not the pytest log

An earlier version parsed pytest's human-readable output. That format has no
reliable delimiter between a node ID and its explanation, and no unambiguous way
to pick the summary line, so it produced four defects (roborev job 853, measured
2026-11-24):

- A parametrize id containing `" - "` was split at that sequence, truncating it
  to a baseline entry and passing unseen.
- `1 failed, 10 passed, 1 error` reported only the failure count, hiding errors.
- A test failing in its body and erroring in teardown produced two outcome lines
  for one id, so a valid log was rejected as incomplete.
- Captured output resembling `=== 999 failed` claimed 999 outcomes.

`--junitxml` (built in, no plugin) reports each of those exactly, so the gate
reads structure instead of guessing at prose. `junit_family=xunit1` is required:
it is the family that emits a `file` attribute, which is what turns a testcase
back into the repository-relative node ID without inferring paths from dotted
classnames.

Three outcomes are treated as failures, because all three look green in a CI job:

- **Unexpected failures or errors.** Not in the baseline, so the change broke
  something.
- **No results at all.** A report whose suites ran zero tests proves nothing.
  An empty selection is not a healthy run.
- **A stale baseline.** Expected node IDs that did not fail mean the list
  describes a suite that no longer exists. It is reported so the list gets
  corrected, but it does not fail the build: a baseline that is too generous is
  a lesser fault than a gate nobody can run.
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Suites that fail on a clean checkout, by exact node ID. Keep in step with
# `AGENTS.md` § Known failures — that table is the readable copy, this is the
# enforced one. A node ID here that stops failing is reported as stale.
EXPECTED_FAILURES = frozenset(
    {
        "tests/clipped/test_clipped_cli.py::test_paste_outputs_clipboard[paste]",
        "tests/clipped/test_clipped_cli.py::test_paste_outputs_clipboard[p]",
        "tests/clipped/test_clipped_cli.py::test_copy_reads_stdin[copy]",
        "tests/clipped/test_clipped_cli.py::test_copy_reads_stdin[c]",
        "tests/clipped/test_clipped_cli.py::test_copy_single_file[copy]",
        "tests/clipped/test_clipped_cli.py::test_copy_single_file[c]",
        "tests/clipped/test_clipped_cli.py::test_copy_multiple_files_concatenates",
        "tests/clipped/test_clipped_cli.py::test_auto_mode_with_piped_stdin_copies",
        "tests/clipped/test_clipped_cli.py::test_auto_mode_with_tty_pastes",
        "tests/clipped/test_clipped_cli.py::test_copy_handles_non_utf8_bytes",
        "tests/restart_stale/test_role.py::test_a_missing_kind_fails_before_anything_runs",
        "tests/restart_stale/test_role.py::test_the_defaults_leave_the_role_inert",
        # Trunk red since the 2026-11 .lore.md re-distillation rewrites: these
        # two drift-guard tests fail on a pristine origin/main checkout
        # (verified locally on main 2026-11-19, before any DOT-343 change; and
        # observed in CI run 45331112024 on 3be68f75, 2026-11-24). DOT-305's
        # guard surface moved; the owning task refreshes or fixes.
        "tests/docs/test_lore_md_rules_survive.py::test_rule_survives_redistillation[requires_map undefined skips removal]",
        "tests/docs/test_lore_md_rules_survive.py::test_rule_survives_redistillation[work repos never committed]",
    }
)


class ReportError(Exception):
    """The report does not describe a completed run."""


def node_id(case: ET.Element) -> str:
    """The repository-relative pytest node ID for one testcase element.

    xunit1 carries `file`, so the path is read rather than inferred by turning
    dots back into slashes — an inference that would break on a test file with a
    dot in its name.

    The CLASS must be kept. pytest reports a class method as
    `file.py::TestClass::test_method`, and `classname` carries it as
    `<dotted module>.<TestClass>`. Dropping it collapsed `TestOne.test_same`,
    `TestTwo.test_same` and a module-level `test_same` into one id — which would
    let a class-based regression alias a module-level baseline entry and pass
    (measured 2026-11-24, roborev job 856).

    The class is derived from `classname` by stripping the module path implied
    by `file`, never by guessing: a `classname` that is neither the module path
    nor an extension of it is reported as unidentifiable.
    """
    path = case.get("file")
    name = case.get("name")
    classname = case.get("classname")
    if not path or not name or not classname:
        raise ReportError(
            "a testcase has no file/name/classname attribute, so it cannot be "
            "identified. Run pytest with -o junit_family=xunit1."
        )
    module = path.removesuffix(".py").replace("/", ".")
    if classname == module:
        return f"{path}::{name}"
    prefix = f"{module}."
    if not classname.startswith(prefix):
        raise ReportError(
            f"testcase {name!r} in {path} reports classname {classname!r}, which "
            f"is neither {module!r} nor an extension of it. Its class cannot be "
            "determined without guessing."
        )
    # pytest separates nesting levels of a class with "::", and `classname`
    # carries them as dots: TestOuter > TestInner is
    # `file.py::TestOuter::TestInner::test_method`. Emitting
    # `TestOuter.TestInner` instead produced an id pytest never prints, so a
    # correct baseline entry failed to match (measured 2026-11-24, job 864).
    classes = classname.removeprefix(prefix).replace(".", "::")
    return f"{path}::{classes}::{name}"


def failed_ids(root: ET.Element) -> set[str]:
    """Node IDs whose testcase carries <failure> or <error>.

    A test that fails in its body and errors in teardown appears as two
    testcase elements with the same name; both are failure events and both are
    recorded, so the count matches the suite's own tallies.
    """
    return {
        node_id(case)
        for case in root.iter("testcase")
        if case.find("failure") is not None or case.find("error") is not None
    }


def total_tests(root: ET.Element) -> int:
    """How many test cases the report claims to have run."""
    return sum(int(suite.get("tests") or 0) for suite in root.iter("testsuite"))


def claimed_outcomes(root: ET.Element) -> int:
    """How many failures plus errors the report's own tallies claim.

    `--junitxml` writes the failing testcases, so this normally equals the count
    of failure/error children. Comparing the two is what catches a report that
    was written but did not describe the whole run.
    """
    return sum(
        int(suite.get("failures") or 0) + int(suite.get("errors") or 0)
        for suite in root.iter("testsuite")
    )


def failure_events(root: ET.Element) -> int:
    """How many failure/error children the report actually carries.

    Counted as events, not distinct ids: a test that fails in its body and
    errors in teardown legitimately contributes two.
    """
    return sum(
        1
        for case in root.iter("testcase")
        for child in case
        if child.tag in {"failure", "error"}
    )


def judge(root: ET.Element) -> tuple[set[str], frozenset[str]]:
    """Return (unexpected, expected_but_absent)."""
    outcomes = failed_ids(root)
    return outcomes - EXPECTED_FAILURES, EXPECTED_FAILURES - outcomes


def load_report(path: Path) -> ET.Element:
    """Parse the JUnit XML report, or explain why it cannot be judged."""
    if not path.is_file():
        raise ReportError(
            f"{path} does not exist, so no test ever ran.\n"
            "A gate that cannot read its input has not passed; it has not run."
        )
    try:
        return ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ReportError(
            f"{path} is not valid XML ({exc}). pytest writes this file as it "
            "finishes; a truncated or absent file means the run did not complete."
        ) from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "report",
        type=Path,
        help="JUnit XML file written by `pytest --junitxml`.",
    )
    parser.add_argument(
        "--pytest-exit-code",
        type=int,
        required=True,
        help=(
            "pytest's own exit status. 0 (all passed) and 1 (some failed) mean "
            "the run finished; anything else means it was interrupted. REQUIRED, "
            "not optional: a report from an interrupted run is well-formed and "
            "partial, so an omitted status cannot be read as 'probably fine'. A "
            "gate whose safety depends on the caller remembering a flag fails "
            "open exactly when someone runs it by hand."
        ),
    )
    args = parser.parse_args(argv)

    if args.pytest_exit_code not in (0, 1):
        print(
            f"error: pytest exited {args.pytest_exit_code}, which is not a "
            "completed run (0 = passed, 1 = tests failed). It was interrupted or "
            "aborted, so tests that never ran are missing from the report\n"
            "entirely — a regression among them would go unseen.",
            file=sys.stderr,
        )
        return 2

    try:
        root = load_report(args.report)
        ran = total_tests(root)
        unexpected, absent = judge(root)
    except ReportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if ran == 0:
        print(
            "error: the report holds no test cases. Zero tests executed is not a\n"
            "green run — a selection that matched nothing cannot prove the code\n"
            "is healthy.",
            file=sys.stderr,
        )
        return 2

    claimed = claimed_outcomes(root)
    observed = failure_events(root)
    if claimed != observed:
        print(
            f"error: the report's own tallies claim {claimed} failure(s)/error(s) "
            f"but it carries {observed}. The file was written\n"
            "without the detail it promises, so the failure list cannot be "
            "trusted.",
            file=sys.stderr,
        )
        return 2

    unexpected, absent = judge(root)

    if absent:
        # Not fatal: the change may have fixed a known failure, which is the
        # outcome everyone wants. Say so loudly enough that the list gets
        # corrected in the same commit.
        print(
            f"note: {len(absent)} baseline entr(ies) did not fail. If this change "
            "fixed them, remove them here and from AGENTS.md § Known failures:",
            file=sys.stderr,
        )
        for nodeid in sorted(absent):
            print(f"  {nodeid}", file=sys.stderr)

    if unexpected:
        print(
            f"{len(unexpected)} outcome(s) outside the known-failure baseline:",
            file=sys.stderr,
        )
        for nodeid in sorted(unexpected):
            print(f"  {nodeid}", file=sys.stderr)
        print(
            "\nEither fix it, or add the exact node ID to EXPECTED_FAILURES here "
            "and to AGENTS.md § Known failures in the same commit.",
            file=sys.stderr,
        )
        return 1

    print(
        f"Every failing or erroring test is one the baseline already knows about "
        f"({ran} test cases read)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
