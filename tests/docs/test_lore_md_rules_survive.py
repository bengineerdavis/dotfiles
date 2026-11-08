"""Load-bearing rules in .lore.md must survive every Lore re-distillation.

`.lore.md` is a managed projection (the Lore daemon rewrites it on its own
schedule), and that rewrite has repeatedly corrupted entries — DOT-305 records
three defects from 2026-11-07: a title/body swap that deleted the uv --frozen
safety rule, a heal that deleted a correct entry and wrote a false trap in its
place, and a wrong decision pointer. The interim guard is the drift-test
pattern applied to known rule text: after every rewrite, grep each
load-bearing rule's anchor and fail loudly when one vanishes, instead of
discovering the loss in a review.

The file is captures-only (never hand-edited), so this test only reads it.
Each anchor is a distinctive substring, not a whole entry, so a re-location or
re-wording that keeps the rule text still passes — survival is the bar, not
placement. A guard that demanded exact entry placement would go red on every
legitimate re-distillation; this one goes red only when a rule's content is
actually gone.
"""

from __future__ import annotations

import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
LORE_MD = REPO / ".lore.md"

# (rule name, anchor substring, what the rule protects). The anchor is the
# text whose disappearance means the rule was corrupted out of the file.
RULES: list[tuple[str, str, str]] = [
    (
        "uv --frozen",
        "re-locks uv.lock",
        "bare `uv run` re-locks uv.lock to the employer PyPI mirror — a "
        "spec.md § Data violation (employer URLs in a committed file)",
    ),
    (
        "requires_map undefined skips removal",
        "skip the removal rather than assume it is harmless",
        "remove.yaml gates uninstall on requires_map being defined; undefined "
        "means unproven, not unshared (docs/TOPICS.md:146-149)",
    ),
    (
        "work repos never committed",
        "work repos NEVER enter the committed catalogue",
        "employer-identifying strings stay machine-local (spec.md § Data)",
    ),
]


def lore_text() -> str:
    return LORE_MD.read_text(encoding="utf-8")


def test_rule_anchors_are_declared() -> None:
    """Guards against the whole suite passing vacuously if RULES is emptied."""
    assert RULES, "RULES is empty — the guard would pass vacuously"
    for name, anchor, why in RULES:
        assert name and anchor and why, f"rule {name!r} has an empty field"


def test_lore_md_exists_and_is_nonempty() -> None:
    """A missing or empty .lore.md cannot be distinguished from a green pass."""
    assert LORE_MD.is_file(), ".lore.md is missing — the check would pass vacuously"
    assert lore_text().strip(), ".lore.md is empty — the check would pass vacuously"


@pytest.mark.parametrize("name,anchor,why", RULES, ids=[r[0] for r in RULES])
def test_rule_survives_redistillation(name: str, anchor: str, why: str) -> None:
    """Each load-bearing rule's anchor is still present after the last rewrite."""
    text = lore_text()
    assert anchor in text, (
        f"The {name!r} rule is gone from .lore.md — its anchor {anchor!r} "
        f"does not appear. Lore's re-distillation deleted or swapped it. "
        f"This rule protected: {why}. Treat .lore.md as captures-only; report "
        f"the corruption upstream (DOT-305, DOT-298 pattern) rather than "
        f"hand-editing the content back."
    )
