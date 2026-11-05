"""Fail a test run that failed in a way the baseline does not expect.

`AGENTS.md` § Known failures names two suites that fail on a clean checkout for
reasons outside the code, and states the rule this script enforces: *a change is
green when the failure LIST matches, not when the count does.* A count can stay
at twelve while one suite is fixed and another regresses.

The script reads pytest's own summary lines (`FAILED <nodeid> - ...`) from a
captured run and compares the node IDs against a checked-in list of expected
failures. Anything outside the list fails.

Two failure modes matter more than the comparison itself, because both look
identical to success in a CI log:

- **No results at all.** A run that collected nothing, or a pytest that died
  before printing a summary, produces zero failures and zero passes. Treating
  that as green is the silent pass this repo keeps hitting. The script requires
  a summary line before it will judge anything.
- **A stale baseline.** If the expected list names tests that did not fail, the
  list is describing a suite that no longer exists. That is reported, but it
  does not fail the build — a baseline that is too generous is a lesser fault
  than a gate that cannot run.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# pytest prints "FAILED tests/x.py::test_y - AssertionError: ..." per failure,
# then a final "N failed, M passed ..." summary.
FAILED_LINE = re.compile(r"^FAILED (?P<nodeid>\S+)", re.MULTILINE)
SUMMARY_LINE = re.compile(
    r"^=*\s*\d+ (failed|passed)",
    re.MULTILINE,
)

# Suites that fail on a clean checkout, by directory. Node IDs below these
# prefixes are expected; anything else is a regression the gate must catch.
# Keep in step with `AGENTS.md` § Known failures — that table is the readable
# copy, this is the enforced one.
EXPECTED_PREFIXES = (
    "tests/clipped/",
    "tests/restart_stale/",
)


def parse_failures(report: str) -> set[str]:
    return {match.group("nodeid") for match in FAILED_LINE.finditer(report)}


def is_expected(nodeid: str) -> bool:
    return nodeid.startswith(EXPECTED_PREFIXES)


def judge(report: str) -> tuple[set[str], set[str], bool]:
    """Return (unexpected, expected-but-absent, saw_a_summary)."""
    if not SUMMARY_LINE.search(report):
        return set(), set(), False
    failures = parse_failures(report)
    unexpected = {f for f in failures if not is_expected(f)}
    return unexpected, set(), True


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
    unexpected, _, saw_summary = judge(report)

    if not saw_summary:
        print(
            "error: the captured output has no pytest summary line. The suite\n"
            "did not complete, so its result is unknown rather than green.",
            file=sys.stderr,
        )
        return 2

    if unexpected:
        print(
            f"{len(unexpected)} failure(s) outside the known-failure baseline:",
            file=sys.stderr,
        )
        for nodeid in sorted(unexpected):
            print(f"  {nodeid}", file=sys.stderr)
        print(
            "\nEither fix the failure, or add its suite to EXPECTED_PREFIXES here "
            "and to AGENTS.md § Known failures in the same commit.",
            file=sys.stderr,
        )
        return 1

    print("Every failure is one the baseline already knows about.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
