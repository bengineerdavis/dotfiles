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
#
# The node ID can contain SPACES: a parametrize id is arbitrary text, so
# `test_x[a //// b-a //// b]` is one ID, not a truncated `test_x[a`. Capturing
# \S+ cut those at the first space, and the baseline was hand-edited to match
# the truncated form — a silent-pass shape, because a NEW test whose id shares
# that prefix would truncate to the same entry and pass unseen. The ID is
# extracted by _node_id() below rather than by the regex.
OUTCOME_LINE = re.compile(r"^(?P<kind>FAILED|ERROR) (?P<rest>\S.*)$", re.MULTILINE)
SUMMARY_LINE = re.compile(
    r"^=*\s*(?:\d+ (?:failed|passed|error)|no tests ran)",
    re.MULTILINE,
)
# `no tests ran` is pytest's exit-5 message for an empty selection. It IS a
# summary line, which is why a summary-presence check alone let it through: the
# gate reported green on a run that executed nothing.
NO_TESTS_RAN = re.compile(r"^=*\s*no tests ran", re.MULTILINE)

# The summary carries the counts that an outcome list must account for.
SUMMARY_COUNTS = re.compile(
    r"^=*\s*(?:(\d+) failed)?,?\s*(?:(\d+) error)?", re.MULTILINE
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
        # Trunk red since the 2026-11 .lore.md re-distillation rewrites: these
        # two drift-guard tests fail on a pristine origin/main checkout
        # (verified locally on main 2026-11-19, before any DOT-343 change; and
        # observed in CI run 45331112024 on 3be68f75, 2026-11-24). DOT-305's
        # guard surface moved; the owning task refreshes or fixes.
        #
        # FULL ids, including the spaces inside the parametrize text. Older
        # versions of this file carried the truncated forms because OUTCOME_LINE
        # captured \S+; that made a new id sharing the prefix indistinguishable
        # from this one (DOT-314).
        "tests/docs/test_lore_md_rules_survive.py::test_rule_survives_redistillation[requires_map undefined skips removal]",
        "tests/docs/test_lore_md_rules_survive.py::test_rule_survives_redistillation[work repos never committed]",
    }
)


def _node_id(rest: str) -> str:
    """The node ID from the text after FAILED, keeping interior spaces.

    pytest separates the ID from the explanation with " - ", so a space inside
    the ID is safe to keep. Falling back to the whole line when the separator is
    absent is deliberate: an unusual format must surface as an unexpected ID,
    not vanish from the outcome set.
    """
    return rest.split(" - ", 1)[0].rstrip()


def parse_outcomes(report: str) -> set[str]:
    """Every node ID pytest reported as FAILED or ERROR."""
    return {_node_id(m.group("rest")) for m in OUTCOME_LINE.finditer(report)}


def claimed_outcome_count(report: str) -> int:
    """How many failures+errors the summary claims.

    Used to catch the empty-run hole from the other side: pytest exiting 5 on an
    empty selection prints "no tests ran" and zero outcome lines. A summary that
    CLAIMS failures while no outcome line was parsed is incomplete evidence, not
    a clean run — and it stays distinguishable from an all-pass run, which
    claims none.

    Returns 0 when the summary claims no failures, so a legitimate all-pass run
    is not punished.
    """
    for match in SUMMARY_COUNTS.finditer(report):
        failed = int(match.group(1) or 0)
        errored = int(match.group(2) or 0)
        if failed or errored:
            return failed + errored
    return 0


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

    claimed = claimed_outcome_count(report)
    outcomes = parse_outcomes(report)
    if NO_TESTS_RAN.search(report) and not outcomes:
        print(
            "error: the suite ran no tests ('no tests ran') and reported no\n"
            "outcomes. Zero tests executed is not a green run; a selection that\n"
            "matched nothing cannot prove the code is healthy.",
            file=sys.stderr,
        )
        return 2
    if claimed > len(outcomes):
        print(
            f"error: the summary claims {claimed} failed/error test(s) but only "
            f"{len(outcomes)} outcome line(s) could be parsed. The log is\n"
            "incomplete, so the failure list cannot be compared.",
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
