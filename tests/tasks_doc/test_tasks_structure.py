"""TASKS.md must keep its sections.

Twice in one session an edit that meant to delete a single task took a whole
section with it. Both times the edit found the task's start index and sliced to
the next line beginning "- " — and both times the task was the last item in its
section, so the next such line was inside a later one.

The first occurrence removed the instructions telling other machines to hard
reset rather than pull after a history rewrite. Neither was noticed at commit
time: `git show --stat` reports that a file changed, not that a change was
larger than intended.

So this is not about tidiness. A section can vanish from a shared queue and the
commit still looks correct, which is the only reason it happened twice.
"""

from __future__ import annotations

import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TASKS = REPO / "TASKS.md"

REQUIRED = [
    "## Conventions",
    "## Claimed",
    "## Open",
    "## History was rewritten",
    "## Private tasks",
    "## Decisions waiting on the author",
    "## Cross-session hazards",
    "## Standing reminders",
]


@pytest.fixture(scope="module")
def text() -> str:
    t = TASKS.read_text(encoding="utf-8")
    assert t.strip(), "TASKS.md is empty — the checks below would be vacuous"
    return t


@pytest.mark.parametrize("heading", REQUIRED)
def test_section_is_present(text, heading):
    assert heading in text, (
        f"{heading!r} is missing from TASKS.md. If an edit removed it, the edit "
        f"was wider than intended — restore it from git rather than re-adding it "
        f"by hand, so the wording is not silently rewritten."
    )


def test_the_reset_instructions_survive(text):
    """The most costly thing to lose: a clone that pulls instead of hard
    resetting resurrects the mixed commits the rewrite existed to unscramble."""
    assert "git reset --hard origin/main" in text


def test_sections_are_in_order(text):
    """Catches a section restored into the wrong place, which a presence check
    alone would pass."""
    positions = [text.index(h) for h in REQUIRED]
    assert positions == sorted(positions), "TASKS.md sections are out of order"
