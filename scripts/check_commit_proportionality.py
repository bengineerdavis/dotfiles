#!/usr/bin/env python3
"""Reject commit messages out of proportion to the change they describe.

The rule this enforces is `commit-hygiene`'s: a subject line alone for
mechanical edits, a sentence or two for small single-purpose changes, one or two
short paragraphs for ordinary features and fixes. And its reasoning, which is
why this reads the diff rather than counting words alone: *a message longer than
the change warrants is not thoroughness, it is evidence the commit should have
been two.*

A fixed word limit cannot express that. Four hundred words on a large refactor is
proportionate; two hundred on a one-line fix is not. So the budget scales with
the size of the staged change.

It scales **logarithmically**, not linearly. Prose does not need to grow in step
with a diff — a thousand-line change is not ten times harder to explain than a
hundred-line one, and a linear budget would license an essay for any large
commit, which is the outcome this exists to prevent.
"""

from __future__ import annotations

import math
import re
import subprocess
import sys

# Derived from commit-hygiene's prose, NOT from this repository's history:
#   a sentence or two for a mechanical edit      ~50 words
#   one to two short paragraphs for ordinary work ~160 words
#   two to three for a large refactor             ~225 words
#
# An earlier draft fitted these to the existing history instead, and had to be
# thrown away. A corpus of long messages is evidence of habit, not of the right
# length — "adoption is not evidence of fit". Fitting the rule to the corpus
# would have encoded the problem as the standard.
#
# These reject ~39% of this repository's history. That is a statement about the
# history, not a fault in the rule, and it is deliberately not smoothed away.
# History is a record and stays as written; the rule governs what comes next.
#
#   python3 scripts/check_commit_proportionality.py --calibrate <git-range>
BASE = 30  # a sentence or two, for a one-line change
SLOPE = 65  # words earned per power-of-ten of changed lines
CEILING = 250  # past here, split the commit instead

# Trailers are metadata, not prose, and should not spend the budget.
TRAILER = re.compile(
    r"^(Co-Authored-By|Signed-off-by|Reviewed-by|Refs|Fixes|Closes|Proportionality):",
    re.I,
)
ESCAPE = re.compile(r"^Proportionality:\s*(\S.*)$", re.I | re.M)


def allowed_words(changed_lines: int) -> int:
    """Word budget for a change of this size."""
    return min(CEILING, int(BASE + SLOPE * math.log10(1 + max(0, changed_lines))))


def body_words(message: str) -> int:
    """Words in the body, excluding the subject, comments and trailers."""
    lines = message.splitlines()
    body = lines[1:] if lines else []
    kept = [
        ln
        for ln in body
        if not ln.lstrip().startswith("#") and not TRAILER.match(ln.strip())
    ]
    return len(" ".join(kept).split())


def verdict(message: str, changed_lines: int) -> tuple[bool, str]:
    """(ok, explanation). Pure, so both directions are testable without git."""
    if ESCAPE.search(message):
        return True, "exempted by a Proportionality: trailer"
    used, budget = body_words(message), allowed_words(changed_lines)
    if used <= budget:
        return True, f"{used} words for {changed_lines} changed lines (budget {budget})"
    return False, (
        f"Commit message is {used} words for a {changed_lines}-line change; "
        f"the budget is {budget}.\n\n"
        "This usually means the commit should be two, not that the prose should "
        "be trimmed — see conventions in AGENTS.md § Commits and the "
        "commit-hygiene skill.\n\n"
        "If the length is genuinely warranted, say why in a trailer:\n"
        "    Proportionality: <reason this change needs the detail>"
    )


def staged_lines() -> int:
    out = subprocess.run(
        ["git", "diff", "--cached", "--numstat"],
        capture_output=True,
        text=True,
    )
    if out.returncode != 0:
        return 0
    total = 0
    for line in out.stdout.splitlines():
        add, rem, *_ = line.split("\t")
        # "-" marks a binary file; it has no line count to judge against
        total += sum(int(n) for n in (add, rem) if n.isdigit())
    return total


def calibrate(rng: str) -> int:
    """Report what these thresholds would do to a range of real commits."""
    shas = subprocess.run(
        ["git", "log", rng, "--format=%H", "--no-merges"],
        capture_output=True,
        text=True,
    ).stdout.split()
    bad = 0
    for sha in shas:
        msg = subprocess.run(
            ["git", "log", "-1", "--format=%s%n%n%b", sha],
            capture_output=True,
            text=True,
        ).stdout
        ns = subprocess.run(
            ["git", "show", "--numstat", "--format=", sha],
            capture_output=True,
            text=True,
        ).stdout
        lines = sum(
            sum(int(x) for x in ln.split("\t")[:2] if x.isdigit())
            for ln in ns.splitlines()
            if "\t" in ln
        )
        if not verdict(msg, lines)[0]:
            bad += 1
    total = len(shas) or 1
    print(f"{bad}/{len(shas)} ({100 * bad // total}%) of {rng} would be rejected")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) >= 3 and argv[1] == "--calibrate":
        return calibrate(argv[2])
    if len(argv) < 2:
        return 0
    # A merge message is generated and summarises many commits; a fixup is
    # amended away. Neither is prose anyone chose to write here.
    if (
        subprocess.run(
            ["git", "rev-parse", "-q", "--verify", "MERGE_HEAD"], capture_output=True
        ).returncode
        == 0
    ):
        return 0
    message = open(argv[1], encoding="utf-8").read()
    if message.lstrip().startswith(("fixup!", "squash!", "Merge ", "Revert ")):
        return 0
    ok, why = verdict(message, staged_lines())
    if not ok:
        print(why, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
