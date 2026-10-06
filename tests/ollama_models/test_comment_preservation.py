"""Proof that `adopt` does not destroy the manifest's rationale.

This suite exists because of what the file being edited is. 499 of
`defaults/main.yaml`'s 759 lines are comments, and they carry measured tok/s
figures, eval scores, dated PROVISIONAL notes, and the reasoning behind every
demotion. Nobody re-derives that. A rewrite that loses it is worse than no
rewrite at all, so the mechanism is asserted against the REAL file rather than
a toy: a fixture would only prove the tool survives a fixture.

The three claims, each checked independently, because a wrong answer can
satisfy any one of them alone:

    the comments are all still there, byte for byte
    nothing changed except the lines that had to
    the document still parses to the same thing everywhere else

And — the direction that distinguishes a working guard from one that always
says yes — `verify_rewrite` REFUSES a rewrite that is not clean.

Run:
    uv run --with pytest --with pyyaml --with hypothesis pytest tests/ollama_models -v
"""

from __future__ import annotations

import difflib

import pytest

yaml = pytest.importorskip("yaml")

# A family with four members, three OS keys each, and one tag repeated across
# two of those keys — so it exercises de-duplication as well as bulk.
FAMILY = "qwen3.6"
NEWER = "qwen3.7"


def retag(om, text, family, new_family):
    """Plan and apply a retag against `text`, the way cmd_adopt does."""
    families = yaml.safe_load(text)["ollama_models"]
    pairs = om.retag_plan(families[family], family, new_family)
    return om.rewrite_family(text, family, new_family, pairs), pairs


def comment_lines(text):
    return [ln for ln in text.splitlines() if ln.lstrip().startswith("#")]


# ── the evidence ────────────────────────────────────────────────────────────


def test_the_real_manifest_is_mostly_comments(real_manifest):
    """The premise, and the reason this tool does line surgery rather than a
    dump. Asserted as a ratio, not a count: the count moves every time a model
    lands, and a test that fails on that teaches nothing."""
    total = len(real_manifest.splitlines())
    comments = len(comment_lines(real_manifest))
    assert comments / total > 0.6, f"{comments}/{total} — is this still a documented file?"


def test_every_comment_line_survives_byte_for_byte(om, real_manifest):
    after, _ = retag(om, real_manifest, FAMILY, NEWER)
    before_c, after_c = comment_lines(real_manifest), comment_lines(after)
    assert len(before_c) == len(after_c)
    assert before_c == after_c, "a comment line was altered, not merely counted"


def test_a_comment_naming_the_family_is_left_alone(om, real_manifest):
    """The qwen3-vl note explains itself by comparison with qwen3.6. Rewriting
    prose to match a retag would silently falsify a recorded argument."""
    assert "qwen3.6 reports the SAME capabilities" in real_manifest
    after, _ = retag(om, real_manifest, FAMILY, NEWER)
    assert "qwen3.6 reports the SAME capabilities" in after
    assert "qwen3.7 reports the SAME capabilities" not in after


def test_only_the_family_key_and_its_tag_lines_change(om, real_manifest):
    after, pairs = retag(om, real_manifest, FAMILY, NEWER)
    before_l, after_l = real_manifest.splitlines(), after.splitlines()
    assert len(before_l) == len(after_l)

    members = yaml.safe_load(real_manifest)["ollama_models"][FAMILY]
    # One line per OS key that carries a tag, plus the `qwen3.6:` key itself.
    # Derived rather than pinned, so adding a member does not fail this test
    # for the wrong reason. Today: 4 members x 3 keys + 1 = 13.
    expected = 1 + sum(1 for m in members for k in om.OS_KEYS if m.get(k))
    changed = [(n, b, a) for n, (b, a) in enumerate(zip(before_l, after_l), 1) if b != a]
    assert len(changed) == expected == 13, [n for n, _, _ in changed]
    # Fewer DISTINCT tags than lines, because the coding members each name the
    # same nvfp4 build under darwin and linux_nvidia. Both numbers are pinned,
    # so neither can quietly stand in for the other.
    assert len(pairs) == 10

    key_lines = [n for n, b, _ in changed if b.startswith(f"  {FAMILY}:")]
    assert len(key_lines) == 1
    for n, b, a in changed:
        assert b.replace(FAMILY, NEWER) == a, f"line {n} changed by more than the retag"


def test_the_diff_is_small_and_is_only_that_family(om, real_manifest):
    after, _ = retag(om, real_manifest, FAMILY, NEWER)
    diff = list(difflib.unified_diff(real_manifest.splitlines(),
                                     after.splitlines(), lineterm="", n=0))
    body = [d for d in diff if d[:1] in "+-" and not d.startswith(("+++", "---"))]
    assert len(body) == 26, "13 removed + 13 added, out of a 764-line file"
    assert all(FAMILY in d or NEWER in d for d in body)


def test_the_document_reparses_identical_everywhere_else(om, real_manifest):
    after, pairs = retag(om, real_manifest, FAMILY, NEWER)
    before_doc, after_doc = yaml.safe_load(real_manifest), yaml.safe_load(after)
    want = om._intended_doc(before_doc, FAMILY, NEWER, dict(pairs))
    assert after_doc == want
    # Order too: dict equality would not notice the family moving, and the
    # order is what `status` prints in.
    assert list(after_doc["ollama_models"]) == list(want["ollama_models"])
    assert FAMILY not in after_doc["ollama_models"]
    assert NEWER in after_doc["ollama_models"]
    # Everything that is not ollama_models is untouched.
    for key in before_doc:
        if key != "ollama_models":
            assert after_doc[key] == before_doc[key], key


def test_the_measured_figures_keep_naming_the_old_tag(om, real_manifest):
    """A measurement belongs to the model it was taken on. Carrying
    ollama_model_perf across would invent data."""
    after, _ = retag(om, real_manifest, FAMILY, NEWER)
    perf = yaml.safe_load(after)["ollama_model_perf"]
    assert "qwen3.6:27b-mlx" in perf
    assert not any(k.startswith("qwen3.7") for k in perf)


@pytest.mark.parametrize("family", ["lfm2", "deepseek-r1", "glm-4.7-flash", "bge-m3"])
def test_every_shape_of_family_entry_retags_cleanly(om, real_manifest, family):
    """The manifest writes members three ways — block style, inline flow maps,
    and single-member families — and a family name may itself contain dots and
    dashes. Each must survive its own verifier."""
    after, pairs = retag(om, real_manifest, family, family + "-next")
    assert pairs, f"{family} produced no retag plan"
    assert om.verify_rewrite(real_manifest, after, family, family + "-next", pairs) == []
    assert comment_lines(after) == comment_lines(real_manifest)


# ── the guard has teeth: it must REFUSE a bad rewrite ───────────────────────


def _corrupt(text, find, replace):
    assert find in text
    return text.replace(find, replace, 1)


@pytest.mark.parametrize(
    "name,corrupt",
    [
        ("a deleted comment line",
         lambda t: t.replace("# Percent of total RAM kept free for other programs."
                             " Budget = total − this%.\n", "")),
        ("a reworded comment",
         lambda t: _corrupt(t, "# 27B dense\n", "# 27B dence\n")),
        ("an unrelated value edited",
         lambda t: _corrupt(t, "ollama_ram_reserve_pct: 33", "ollama_ram_reserve_pct: 50")),
        ("a size silently changed",
         lambda t: _corrupt(t, "size_gb:       { darwin: 20, linux_nvidia: 20, linux: 17 }",
                            "size_gb:       { darwin: 21, linux_nvidia: 20, linux: 17 }")),
        ("a tag half-renamed",
         lambda t: _corrupt(t, '"qwen3.7:27b-nvfp4"', '"qwen3.6:27b-nvfp4"')),
        ("a role repointed",
         lambda t: _corrupt(t, '["qwen3.6:27b-coding-nvfp4"]', '["qwen3.7:27b-coding-nvfp4"]')),
        ("broken YAML",
         lambda t: _corrupt(t, "ollama_models:", "ollama_models: [")),
    ],
)
def test_verify_rewrite_refuses_a_corrupted_result(om, real_manifest, name, corrupt):
    """Mutation by hand. If any of these passed, the checker would be decoration
    — and it is the only thing standing between a regex bug and a destroyed
    file, so it gets checked in both directions."""
    clean, pairs = retag(om, real_manifest, FAMILY, NEWER)
    assert om.verify_rewrite(real_manifest, clean, FAMILY, NEWER, pairs) == [], \
        "the clean rewrite must pass, or this test proves nothing"
    problems = om.verify_rewrite(real_manifest, corrupt(clean), FAMILY, NEWER, pairs)
    assert problems, f"verify_rewrite accepted {name}"


def test_verify_rewrite_catches_an_added_line(om, real_manifest):
    clean, pairs = retag(om, real_manifest, FAMILY, NEWER)
    assert om.verify_rewrite(real_manifest, clean + "\nextra: 1\n",
                             FAMILY, NEWER, pairs) != []


# ── properties ──────────────────────────────────────────────────────────────


def test_retagging_there_and_back_is_the_identity(om, real_manifest):
    """Round-trip. Losslessness is the whole claim, so it is stated as one."""
    for family in ("qwen3.6", "lfm2", "granite4.1", "qwen3-embedding"):
        there, _ = retag(om, real_manifest, family, family + "-x")
        back, _ = retag(om, there, family + "-x", family)
        assert back == real_manifest, f"{family} did not round-trip"


def test_retagging_is_idempotent_under_its_own_output(om, real_manifest):
    once, _ = retag(om, real_manifest, FAMILY, NEWER)
    twice, _ = retag(om, once, NEWER, NEWER)
    assert twice == once


def test_the_output_invents_no_new_words(om, real_manifest):
    """Provenance: every token in the result came from the input or is the one
    name we asked for."""
    after, _ = retag(om, real_manifest, FAMILY, NEWER)
    before_words = set(real_manifest.split())
    for word in set(after.split()) - before_words:
        assert NEWER in word, f"{word!r} appeared from nowhere"


try:
    from hypothesis import given, settings
    from hypothesis import strategies as st
except ImportError:  # pragma: no cover - exercised by the documented command
    pytest.skip("hypothesis not installed", allow_module_level=True)


FAMILY_NAMES = st.from_regex(r"\A[a-z][a-z0-9]{0,6}(\.[0-9]{1,2})?(-[a-z]{1,5})?\Z",
                             fullmatch=True)


@settings(max_examples=60, deadline=None)
@given(new_family=FAMILY_NAMES)
def test_any_plausible_new_name_preserves_every_comment(om, real_manifest, new_family):
    doc = yaml.safe_load(real_manifest)
    if new_family in doc["ollama_models"] or new_family == FAMILY:
        return
    after, pairs = retag(om, real_manifest, FAMILY, new_family)
    assert comment_lines(after) == comment_lines(real_manifest)
    assert om.verify_rewrite(real_manifest, after, FAMILY, new_family, pairs) == []


@settings(max_examples=60, deadline=None)
@given(new_family=FAMILY_NAMES)
def test_any_plausible_new_name_round_trips(om, real_manifest, new_family):
    doc = yaml.safe_load(real_manifest)
    if new_family in doc["ollama_models"] or new_family == FAMILY:
        return
    there, _ = retag(om, real_manifest, FAMILY, new_family)
    back, _ = retag(om, there, new_family, FAMILY)
    assert back == real_manifest
