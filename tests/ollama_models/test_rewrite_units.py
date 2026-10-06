"""Unit tests for the pieces of the rewrite, at the level each can actually fail.

The real-manifest suite in test_comment_preservation.py proves the whole thing
end to end against the file that matters. These cover the value
transformations, where a bug is cheaper to catch and where the real file
happens not to contain the shape that would expose it — a tag that is a strict
prefix of another is entirely possible under the manifest's own precision rules
(`4b` alongside `4b-bf16`) and simply does not occur today.

What mutation testing actually found, recorded because the tidier story would
be false: the regex boundary in `rewrite_family` is INERT. Deleting either half
leaves every test here passing, and no case can be written that changes that —
every planned substitution is the same `family:` -> `newfamily:` prefix swap,
so matching at the wrong offset still lands on the right answer. The mutants
are equivalent, not uncaught. An earlier draft also sorted the substitutions
longest-first; that genuinely was redundant and was removed. The guard with
teeth is `verify_rewrite`, and the mutations that kill it are in the other file.

What these tests DO pin is the observable behaviour: prefix tags come out
right, and the result does not depend on the order the pairs arrive in.
"""

from __future__ import annotations

import textwrap

import pytest

yaml = pytest.importorskip("yaml")


PREFIXED = textwrap.dedent("""\
    # header comment
    ollama_ram_reserve_pct: 33

    ollama_models:

      # ── a family whose tags are prefixes of one another ──
      foo:                      # inline note mentioning foo
        - { darwin: "foo:4b", linux: "foo:4b", size_gb: 1 }
        - darwin:  "foo:4b-bf16"
          linux:   "foo:4b-bf16-extra"
          size_gb: 2

      bar:
        - { darwin: "bar:1b", linux: "bar:1b", size_gb: 1 }
    """)


def plan_and_apply(om, text, family, new_family):
    families = yaml.safe_load(text)["ollama_models"]
    pairs = om.retag_plan(families[family], family, new_family)
    return om.rewrite_family(text, family, new_family, pairs), pairs


# ── the boundary: a short tag must not match inside a long one ──────────────


def test_a_tag_is_not_rewritten_inside_a_longer_tag(om):
    after, pairs = plan_and_apply(om, PREFIXED, "foo", "qux")
    doc = yaml.safe_load(after)["ollama_models"]["qux"]
    assert [m.get("darwin") for m in doc] == ["qux:4b", "qux:4b-bf16"]
    assert [m.get("linux") for m in doc] == ["qux:4b", "qux:4b-bf16-extra"]
    assert "qux:4b-bf16" in dict(pairs).values()
    assert om.verify_rewrite(PREFIXED, after, "foo", "qux", pairs) == []


def test_the_result_is_the_same_whatever_order_the_pairs_arrive_in(om):
    """Order-independence is the property that lets `rewrite_family` drop the
    longest-first sort it used to carry."""
    families = yaml.safe_load(PREFIXED)["ollama_models"]
    pairs = om.retag_plan(families["foo"], "foo", "qux")
    forward = om.rewrite_family(PREFIXED, "foo", "qux", pairs)
    reverse = om.rewrite_family(PREFIXED, "foo", "qux", list(reversed(pairs)))
    assert forward == reverse


def test_a_sibling_family_is_untouched(om):
    after, _ = plan_and_apply(om, PREFIXED, "foo", "qux")
    assert '"bar:1b"' in after
    assert yaml.safe_load(after)["ollama_models"]["bar"] == \
        yaml.safe_load(PREFIXED)["ollama_models"]["bar"]


def test_comments_naming_the_family_are_untouched(om):
    after, _ = plan_and_apply(om, PREFIXED, "foo", "qux")
    assert "# ── a family whose tags are prefixes of one another ──" in after
    assert "# inline note mentioning foo" in after
    assert "# inline note mentioning qux" not in after


# ── split_code_comment ──────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "line,code,comment",
    [
        ('  linux: "a:b"  # why', '  linux: "a:b"  ', "# why"),
        ("# whole line", "", "# whole line"),
        ('  name: "has # inside"', '  name: "has # inside"', ""),
        ("  name: 'single # inside'", "  name: 'single # inside'", ""),
        ("  plain: value", "  plain: value", ""),
        ("", "", ""),
        ("  tag: a#b", "  tag: a#b", ""),  # no space before # — not a comment
    ],
)
def test_split_code_comment(om, line, code, comment):
    assert om.split_code_comment(line) == (code, comment)


# ── family_block ────────────────────────────────────────────────────────────


def test_family_block_stops_at_the_next_family(om):
    lines = PREFIXED.splitlines(keepends=True)
    start, end = om.family_block(lines, "foo")
    assert lines[start].startswith("  foo:")
    assert lines[end].startswith("  bar:")


def test_family_block_is_none_for_an_absent_family(om):
    assert om.family_block(PREFIXED.splitlines(keepends=True), "nope") is None


def test_family_block_ignores_a_matching_key_outside_ollama_models(om):
    """A top-level `foo:` before the section must not be mistaken for the
    family — the search starts after `ollama_models:` for that reason."""
    text = "foo: 1\n" + PREFIXED
    lines = text.splitlines(keepends=True)
    start, _ = om.family_block(lines, "foo")
    assert lines[start] == "  foo:                      # inline note mentioning foo\n"


# ── retag_plan ──────────────────────────────────────────────────────────────


def test_retag_plan_skips_a_tag_that_is_not_this_family(om):
    """The manifest asserts every member's tag starts with its family key. This
    enforces it rather than trusting it, so a stray shows up in the diff a human
    reads instead of being silently rewritten."""
    members = [{"darwin": "foo:1b", "linux": "elsewhere:1b"}]
    assert om.retag_plan(members, "foo", "qux") == [("foo:1b", "qux:1b")]


def test_retag_plan_deduplicates_a_tag_shared_by_two_os_keys(om):
    members = [{"darwin": "foo:1b", "linux_nvidia": "foo:1b", "linux": "foo:1b-gguf"}]
    assert om.retag_plan(members, "foo", "qux") == [
        ("foo:1b", "qux:1b"), ("foo:1b-gguf", "qux:1b-gguf"),
    ]


def test_retag_plan_is_empty_for_a_family_with_no_members(om):
    assert om.retag_plan([], "foo", "qux") == []
    assert om.retag_plan(None, "foo", "qux") == []
