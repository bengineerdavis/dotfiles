"""Fail a test run whose outcome differs from the known-failure baseline.

`AGENTS.md` § Known failures names the tests that fail on a clean checkout for
reasons outside the code, and states the rule this script enforces: *a change is
green when the failure LIST matches, not when the count does.*

The baseline is a list of exact node IDs, not a list of directories. An earlier
version matched whole suites, which meant a brand-new regression inside a
known-failing suite passed silently — the same silent-pass shape the script
exists to prevent. A regression is a new node ID wherever it lives.

Three outcomes are treated as failures, because all three look green in a CI log:

- **Unexpected failures or errors.** Not in the baseline, so the change broke
  something.
- **No results at all.** A run that collected nothing, or a pytest that died
  before printing a summary, produces zero failures. Requiring the summary line
  is what stops that reading as success.
- **A stale baseline.** Expected node IDs that did not fail mean the list
  describes a suite that no longer exists. It is reported so the list gets
  corrected, but it does not fail the build: a baseline that is too generous is
  a lesser fault than a gate nobody can run.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# pytest prints one line per abnormal outcome, then a summary:
#   FAILED tests/x.py::test_y - AssertionError: ...
#   ERROR tests/x.py::test_y - RuntimeError: ...
# Errors are collection and fixture failures. They are not failures in the
# summary's "N failed" count, so they must be parsed separately or they vanish.
OUTCOME_LINE = re.compile(r"^(?P<kind>FAILED|ERROR) (?P<nodeid>\S+)", re.MULTILINE)
SUMMARY_LINE = re.compile(
    r"^=*\s*(?:\d+ (?:failed|passed|error)|no tests ran)",
    re.MULTILINE,
)

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
    }
)


def parse_outcomes(report: str) -> set[str]:
    """Every node ID pytest reported as FAILED or ERROR."""
    return {match.group("nodeid") for match in OUTCOME_LINE.finditer(report)}


def judge(report: str) -> tuple[set[str], frozenset[str], bool]:
    """Return (unexpected, expected_but_absent, saw_a_summary)."""
    if not SUMMARY_LINE.search(report):
        return set(), frozenset(), False
    outcomes = parse_outcomes(report)
    unexpected = outcomes - EXPECTED_FAILURES
    absent = EXPECTED_FAILURES - outcomes
    return unexpected, absent, True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "report",
        type=Path,
        help="File holding the captured pytest output.",
    )
    args = parser.parse_args(argv)

    if not args.report.is_file():
        print(
            f"error: {args.report} does not exist, so no test ever ran.\n"
            "A gate that cannot read its input has not passed; it has not run.",
            file=sys.stderr,
        )
        return 2

    report = args.report.read_text(encoding="utf-8", errors="replace")
    unexpected, absent, saw_summary = judge(report)

    if not saw_summary:
        print(
            "error: the captured output has no pytest summary line. The suite\n"
            "did not complete, so its result is unknown rather than green.",
            file=sys.stderr,
        )
        return 2

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

    print("Every failing or erroring test is one the baseline already knows about.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
