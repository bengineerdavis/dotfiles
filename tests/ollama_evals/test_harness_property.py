"""Property and fuzz tests for the eval harness's pure functions.

These complement the example-based suites rather than replacing them. The
division is by what the test knows: a property knows a RULE that holds for all
inputs, an example knows an INCIDENT. `test_whitespace_retry.py` remembers that
`rfind("\n\n")` landed inside the prompt; the property here says content is
never altered, for any seam. Both are worth having, and neither implies the
other.

Nothing here restates an implementation. A property that recomputes the function
under test proves only that the code equals itself — so `deep_merge` is checked
against key-presence and override rules, not against a second merge.

Requires: hypothesis. Run with
    uv run --with pytest --with hypothesis --with pyyaml pytest tests/ollama_evals/
"""

from __future__ import annotations

import copy
import re
import string

import pytest

# importorskip, NOT a try/except plus skipif: the @given decorators below are
# evaluated at import time, so a skipif marker never gets the chance to fire and
# the module raises NameError during collection instead of skipping. That is the
# bug this line replaces — it made the documented fallback test command, which
# omits --with hypothesis, fail rather than skip.
pytest.importorskip("hypothesis", reason="hypothesis not installed")

from hypothesis import given, settings, assume, HealthCheck  # noqa: E402
from hypothesis import strategies as st                      # noqa: E402

# Small scalars keep generated dicts readable when a property fails; the shrunk
# counterexample is meant to be pasted into a regression test by hand.
scalars = st.one_of(st.integers(), st.booleans(), st.text(max_size=8), st.none())
keys = st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=4)
nested = st.recursive(
    scalars, lambda inner: st.dictionaries(keys, inner, max_size=4), max_leaves=8
)
dicts = st.dictionaries(keys, nested, max_size=5)


# ── deep_merge ───────────────────────────────────────────────────────────────

@given(base=dicts, over=dicts)
def test_deep_merge_does_not_mutate_its_inputs(ev, base, over):
    """Sweep levels merge onto a shared base case. Mutating it would make level
    N+1 inherit level N's overrides — the ladder would stop being independent
    rungs and no failure would be attributable to its own level."""
    b, o = copy.deepcopy(base), copy.deepcopy(over)
    ev.deep_merge(base, over)
    assert base == b, "deep_merge mutated base"
    assert over == o, "deep_merge mutated over"


@given(base=dicts, over=dicts)
def test_deep_merge_loses_no_keys(ev, base, over):
    out = ev.deep_merge(base, over)
    assert set(out) == set(base) | set(over)


@given(base=dicts, over=dicts)
def test_deep_merge_override_wins_for_non_dicts(ev, base, over):
    out = ev.deep_merge(base, over)
    for k, v in over.items():
        if not isinstance(v, dict):
            assert out[k] == v, f"key {k!r} was not overridden"


@given(d=dicts)
def test_deep_merge_empty_is_identity(ev, d):
    assert ev.deep_merge(d, {}) == d
    assert ev.deep_merge({}, d) == d


# ── set_path ─────────────────────────────────────────────────────────────────

@given(
    path=st.lists(keys, min_size=1, max_size=4).map(".".join),
    value=scalars,
    start=dicts,
)
def test_set_path_value_is_readable_back(ev, path, value, start):
    d = copy.deepcopy(start)
    try:
        ev.set_path(d, path, value)
    except ValueError:
        # a prefix of the path already holds a scalar — rejected by contract,
        # and covered explicitly by the regression test below
        assume(False)
    cur = d
    for part in path.split("."):
        cur = cur[part]
    assert cur == value


@given(path=st.lists(keys, min_size=1, max_size=3).map(".".join), value=scalars, d=dicts)
def test_set_path_leaves_unrelated_top_level_keys_alone(ev, path, value, d):
    head = path.split(".")[0]
    before = {k: copy.deepcopy(v) for k, v in d.items() if k != head}
    try:
        ev.set_path(d, path, value)
    except ValueError:
        assume(False)
    for k, v in before.items():
        assert d[k] == v, f"unrelated key {k!r} changed"


def test_set_path_names_the_path_when_a_segment_is_not_a_mapping(ev):
    """Hypothesis's shrunk counterexample, pinned as its own test.

    The generator found `set_path({"a": 0}, "a.a", None)` dying with a bare
    "'int' object does not support item assignment" — a case-authoring typo
    surfacing as a harness crash. Kept as an explicit example because it is the
    cheapest regression test that will ever exist for it, and because the
    generator is under no obligation to produce it again.
    """
    with pytest.raises(ValueError) as e:
        ev.set_path({"a": 0}, "a.a", None)
    assert "a.a" in str(e.value), "the error must name the offending path"
    assert "int" in str(e.value), "the error must say what it found instead"


def test_set_path_still_creates_missing_intermediate_dicts(ev):
    """The relenting direction: rejecting scalars must not stop it building
    the nested path a sweep normally needs."""
    d = {}
    ev.set_path(d, "filler.words", 3000)
    assert d == {"filler": {"words": 3000}}


# ── nudge_whitespace ─────────────────────────────────────────────────────────

@given(text=st.text(max_size=200), seam=st.integers(min_value=-50, max_value=250))
def test_nudge_whitespace_preserves_content(ev, text, seam):
    """The retry exists to re-ask the SAME question with different spacing. If
    the nudge could alter non-whitespace content it would be asking a different
    question, and a passing retry would prove nothing."""
    out = ev.nudge_whitespace(text, seam)
    strip = lambda s: re.sub(r"\s+", "", s)
    assert strip(out) == strip(text)


@given(text=st.text(min_size=2, max_size=200), seam=st.integers(min_value=-50, max_value=250))
def test_nudge_whitespace_adds_one_char_or_nothing(ev, text, seam):
    out = ev.nudge_whitespace(text, seam)
    if 0 < seam < len(text):
        assert len(out) == len(text) + 1
        assert out[seam] == "\n"
    else:
        assert out == text, "out-of-range seam must leave the prompt untouched"


# ── unmet_capabilities ───────────────────────────────────────────────────────

caps_st = st.sets(st.sampled_from(["vision", "tools", "thinking", "embedding"]), max_size=4)


@given(caps=caps_st, need=caps_st)
def test_unmet_capabilities_relents_whenever_it_can(ev, caps, need):
    """The relenting direction, as a rule rather than an example. A gate that
    skips everything and a gate that skips correctly both produce a clean run;
    only this direction tells them apart."""
    if need <= caps:
        assert ev.unmet_capabilities(caps, need) is None


@given(caps=caps_st, need=caps_st)
def test_unmet_capabilities_refuses_whenever_it_must(ev, caps, need):
    if need - caps:
        assert ev.unmet_capabilities(caps, need) == sorted(need - caps)


@given(need=caps_st)
def test_unmet_capabilities_never_gates_undeterminable_models(ev, need):
    """caps is None means "could not determine" — remote models report nothing.
    Gating on that would silently mark every requiring case n/a."""
    assert ev.unmet_capabilities(None, need) is None


@given(caps=caps_st, need=caps_st)
def test_unmet_capabilities_result_is_a_subset_of_need(ev, caps, need):
    out = ev.unmet_capabilities(caps, need)
    if out is not None:
        assert out, "an empty list would read as 'gated on nothing'"
        assert set(out) <= need
        assert not (set(out) & caps)


# ── build_filler ─────────────────────────────────────────────────────────────

@given(n=st.integers(min_value=1, max_value=200), seed=st.integers(0, 1000))
def test_build_filler_is_deterministic(ev, n, seed):
    """Reproducible haystacks are what make a long-context result comparable
    across runs and hosts."""
    assert ev.build_filler(n, seed) == ev.build_filler(n, seed)


@given(n=st.integers(min_value=1, max_value=200), seed=st.integers(0, 1000))
def test_build_filler_uses_only_the_fixed_vocabulary(ev, n, seed):
    """spec.md § Data — eval cases are synthesised, enforced mechanically: no
    token can reach a haystack unless it was written into FILLER_VOCAB."""
    vocab = {w.lower() for w in ev.FILLER_VOCAB}
    words = re.findall(r"[A-Za-z]+", ev.build_filler(n, seed))
    assert words, "produced no words"
    assert {w.lower() for w in words} <= vocab


@given(n=st.integers(min_value=1, max_value=200), seed=st.integers(0, 1000))
def test_build_filler_meets_the_requested_length(ev, n, seed):
    """Overshoot is by design — whole sentences — but undershoot would mean a
    needle sitting at a different relative depth than the case declares."""
    assert len(re.findall(r"[A-Za-z]+", ev.build_filler(n, seed))) >= n


# ── cosine ───────────────────────────────────────────────────────────────────

vec = st.lists(st.floats(-1e3, 1e3, allow_nan=False, allow_infinity=False),
               min_size=1, max_size=8)


@given(a=vec, b=vec)
def test_cosine_is_bounded(ev, a, b):
    n = min(len(a), len(b))
    out = ev.cosine(a[:n], b[:n])
    assert -1.0000001 <= out <= 1.0000001, f"cosine out of range: {out}"


@given(a=vec, b=vec)
def test_cosine_is_symmetric(ev, a, b):
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    assert ev.cosine(a, b) == pytest.approx(ev.cosine(b, a), abs=1e-9)


@given(a=vec)
def test_cosine_of_zero_vector_is_zero_not_an_error(ev, a):
    """An all-zero embedding is what a failed embed call returns. Dividing by
    its norm would raise inside the coverage report."""
    assert ev.cosine([0.0] * len(a), a) == 0.0


# ── run_check: the untrusted boundary ────────────────────────────────────────
# Model output is the input most likely to be malformed, because the producer is
# a sampling process and not a program. A harness defect here reports itself as
# a MODEL failure, which is the worst outcome a discriminator can have.

# Shapes drawn from real cases in evals/cases/.
CHECKS = [
    "import re\nm = re.search(r'ANSWER:\\s*([a-z]+)', response, re.I)\nassert m, 'no answer'\nassert m.group(1).lower() == 'bravo'",
    "assert 'QF-8831-KX' in response.upper().replace(' ', '')",
    "import re\nn = re.findall(r'\\d+', response)\nassert n and int(n[-1]) == 48",
    "assert 'NOT FOUND' not in response.upper()",
]

# Adversarial shapes a model actually emits: empty, truncated mid-token, pure
# whitespace, the prompt echoed back, control characters, enormous output.
HOSTILE = st.one_of(
    st.just(""),
    st.just("   \n\n\t  "),
    st.just("ANSWER:"),
    st.just("ANSWER: ​"),
    st.just("\x00\x01\x02"),
    st.just("ANSWER: " + "x" * 10000),
    st.text(max_size=300),
    st.text(alphabet=st.characters(categories=["Cc", "Cf", "Zs"]), max_size=50),
)


@given(src=st.sampled_from(CHECKS), response=HOSTILE)
@settings(max_examples=300)
def test_run_check_never_raises_on_model_output(ev, src, response):
    ok, msg = ev.run_check(src, response)
    assert isinstance(ok, bool)
    assert isinstance(msg, str)


@given(src=st.sampled_from(CHECKS), response=HOSTILE)
@settings(max_examples=300)
def test_run_check_failures_are_always_explainable(ev, src, response):
    """A silent False is unactionable — the failures table would show a blank
    reason and the run could not be triaged."""
    ok, msg = ev.run_check(src, response)
    if not ok:
        assert msg.strip(), "check failed with an empty message"


# Broken sources are curated, never generated: run_check exec()s what it is
# given, so fuzzing the source itself would be executing arbitrary text.
BROKEN = [
    "assert (",                      # SyntaxError
    "assert undefined_name == 1",    # NameError
    "assert int('nope') == 1",       # ValueError
    "assert 1 / 0",                  # ZeroDivisionError
    "raise KeyboardInterrupt",       # not an Exception subclass in the usual sense
    "",                              # empty check
]


@pytest.mark.parametrize("src", BROKEN)
def test_run_check_converts_authoring_errors_into_failures(ev, src):
    """A malformed check is a case-authoring bug. It must surface as a named
    failure, not as a traceback that aborts the run for every later case."""
    try:
        ok, msg = ev.run_check(src, "ANSWER: bravo")
    except KeyboardInterrupt:
        pytest.skip("KeyboardInterrupt intentionally propagates")
    if src == "":
        assert ok, "an empty check vacuously passes; that is the current contract"
    else:
        assert not ok and msg.strip(), f"{src!r} did not produce a named failure"
