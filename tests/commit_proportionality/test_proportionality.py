"""The commit-message proportionality check.

The rule is commit-hygiene's: message length tracks change size, and a message
longer than its change warrants means the commit should have been two. A fixed
word limit cannot express that, which is why this reads the diff.

The thresholds were derived from that skill's prose, NOT fitted to this
repository's history. An earlier draft was fitted to the corpus and had to be
discarded: a body of long messages is evidence of habit, not of correct length.
These tests pin the shape of the curve so a future adjustment has to be
deliberate rather than a quiet widening.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "check_commit_proportionality.py"


@pytest.fixture(scope="module")
def m():
    spec = importlib.util.spec_from_file_location("prop", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def msg(body: str, subject: str = "scope: do a thing") -> str:
    return f"{subject}\n\n{body}\n"


# ── the curve ────────────────────────────────────────────────────────────────

def test_budget_grows_with_the_change(m):
    assert m.allowed_words(1) < m.allowed_words(100) < m.allowed_words(1000)


def test_budget_grows_sublinearly(m):
    """A thousand-line change is not ten times harder to explain than a
    hundred-line one. Linear growth would license an essay for any large commit,
    which is what this exists to prevent.

    Sublinear means the words-per-line ALLOWANCE shrinks as the change grows —
    not that each decade earns fewer words than the last. A log curve earns a
    constant amount per decade by definition, and an earlier version of this
    test asserted otherwise and failed against correct code."""
    ratios = [m.allowed_words(n) / n for n in (10, 100, 1000, 10000)]
    assert ratios == sorted(ratios, reverse=True), ratios


def test_budget_is_capped(m):
    assert m.allowed_words(10**6) == m.CEILING


def test_budget_matches_the_standard_it_came_from(m):
    """commit-hygiene: a sentence or two for a mechanical edit, one to two short
    paragraphs for ordinary work. If someone widens these, this test says what
    the numbers were supposed to mean."""
    assert 40 <= m.allowed_words(1) <= 70        # a sentence or two
    assert 130 <= m.allowed_words(100) <= 190    # one to two short paragraphs
    assert 200 <= m.allowed_words(1000) <= 250   # two to three


# ── both directions ──────────────────────────────────────────────────────────

def test_rejects_a_long_message_on_a_small_change(m):
    ok, why = m.verdict(msg("word " * 300), changed_lines=5)
    assert ok is False
    assert "should be two" in why or "should have been two" in why


def test_accepts_the_same_message_on_a_large_change(m):
    """The relenting direction. A check that only ever refuses is
    indistinguishable from one that never runs."""
    assert m.verdict(msg("word " * 200), changed_lines=20000)[0] is True


def test_accepts_a_subject_only_commit(m):
    assert m.verdict("scope: rename a variable\n", changed_lines=2)[0] is True


# ── things that must not spend the budget ────────────────────────────────────

def test_trailers_do_not_count(m):
    """The trailer block must be long enough that counting it would blow the
    budget. A first version used a trailer small enough to fit either way, so
    removing the exclusion changed nothing and the mutation survived — a test
    that cannot fail is not evidence."""
    prose = "word " * 40
    trailers = "\n".join(f"Co-Authored-By: Person Number{i} <p{i}@example.com>" for i in range(60))
    assert m.body_words(msg(prose)) < m.allowed_words(50)                  # prose alone fits
    assert len((prose + " " + trailers).split()) > m.allowed_words(50)     # with trailers it would not
    assert m.verdict(msg(prose + "\n\n" + trailers), changed_lines=50)[0] is True


def test_comment_lines_do_not_count(m):
    """git leaves its own commentary in the message file; charging for it would
    make the limit depend on how verbose git is feeling."""
    body = "word " * 20 + "\n" + "\n".join("# " + "x " * 40 for _ in range(20))
    assert m.verdict(msg(body), changed_lines=10)[0] is True


def test_the_escape_hatch_works_and_is_recorded(m):
    """Deliberately a trailer rather than a flag: it lands in the commit, so an
    exception is visible in the log instead of being invisible in someone's
    shell history."""
    long_body = "word " * 300 + "\n\nProportionality: a rewrite needing its rationale preserved"
    ok, why = m.verdict(msg(long_body), changed_lines=5)
    assert ok is True
    assert "Proportionality" in why


def test_the_escape_hatch_needs_a_reason(m):
    """A bare trailer with no reason is not an exception, it is a bypass."""
    assert m.verdict(msg("word " * 300 + "\n\nProportionality:"), changed_lines=5)[0] is False
