"""The machine-local decision store.

The store is a hand-editable YAML boundary, so the malformed-input cases are
the expected state during editing, not exotic ones — every one must name the
file, kind and entry rather than reading as "no decisions".
"""

from __future__ import annotations

import pytest

# pyrefly: ignore [missing-import]
from skill_trust.store import (
    StoreError,
    add_entry,
    normalised,
    read_store,
    remove_entry,
    save_store,
)


def test_an_absent_store_reads_as_empty_not_an_error(tmp_path):
    """Nobody has decided anything yet on a fresh machine; that is normal."""
    assert read_store(tmp_path / "trust.yaml") == {}


def test_bare_strings_and_rich_entries_both_read(tmp_path):
    p = tmp_path / "trust.yaml"
    p.write_text(
        "approved_sources:\n"
        "  - owner/lib\n"
        "  - source: other/repo\n"
        "    why: checked the licence by hand\n"
        "    decided: 2026-10-21\n"
    )
    store = read_store(p)
    assert store["approved_sources"] == [
        {"source": "owner/lib"},
        {
            "source": "other/repo",
            "why": "checked the licence by hand",
            "decided": "2026-10-21",
        },
    ]


def test_normalised_drops_metadata_into_bare_lists(tmp_path):
    store = {
        "approved_sources": [{"source": "a/b", "why": "w", "decided": "d"}],
        "deny_skills": [{"name": ".trash"}],
        "exclude": [{"source": "a/b", "name": "skill-x"}],
    }
    assert normalised(store) == {
        "approved_sources": ["a/b"],
        "deny_skills": [".trash"],
        "exclude": {"a/b": ["skill-x"]},
    }


def test_a_mistyped_kind_is_an_error_not_a_skip(tmp_path):
    """`approved_soruces` silently ignored would leave the human believing a
    decision stands that the tool never read.
    """
    p = tmp_path / "trust.yaml"
    p.write_text("approved_soruces: [owner/lib]\n")
    with pytest.raises(StoreError, match="approved_soruces"):
        read_store(p)


def test_an_unknown_entry_field_is_an_error_naming_the_entry(tmp_path):
    p = tmp_path / "trust.yaml"
    p.write_text("vendored:\n  - name: foo\n    souce: a/b\n")
    with pytest.raises(StoreError, match=r"vendored\[0\].*souce"):
        read_store(p)


def test_an_entry_missing_its_value_field_is_named(tmp_path):
    p = tmp_path / "trust.yaml"
    p.write_text("deny_sources:\n  - why: forgot the source\n")
    with pytest.raises(StoreError, match=r'deny_sources\[0\].*"source"'):
        read_store(p)


def test_unparseable_yaml_is_an_error(tmp_path):
    p = tmp_path / "trust.yaml"
    p.write_text("approved_sources: [unclosed\n")
    with pytest.raises(StoreError, match="unreadable store"):
        read_store(p)


def test_add_appends_a_decision_with_why_and_date():
    store = add_entry({}, "approved_sources", source="a/b", why="reviewed")
    (entry,) = store["approved_sources"]
    assert entry["source"] == "a/b"
    assert entry["why"] == "reviewed"
    assert entry["decided"]  # defaulted to today; the value is the point


def test_add_requires_a_why():
    """A decision without a reason is a forgettable one — the vendored list's
    PROVENANCE discipline applies to the store too.
    """
    with pytest.raises(StoreError, match="why"):
        add_entry({}, "approved_sources", source="a/b", why="  ")


def test_add_replaces_rather_than_duplicates():
    store = add_entry({}, "approved_sources", source="a/b", why="first")
    store = add_entry(store, "approved_sources", source="a/b", why="second")
    assert [e["why"] for e in store["approved_sources"]] == ["second"]


def test_exclude_entries_match_on_source_and_name():
    store = add_entry({}, "exclude", source="a/b", name="skill-x", why="veto")
    assert normalised(store) == {"exclude": {"a/b": ["skill-x"]}}


def test_remove_reports_whether_anything_matched():
    store = add_entry({}, "deny_skills", name=".trash", why="my trash")
    store, removed = remove_entry(store, "deny_skills", ".trash")
    assert removed and store["deny_skills"] == []
    _, removed = remove_entry(store, "deny_skills", ".trash")
    assert not removed


def test_save_round_trips_and_locks_permissions(tmp_path):
    p = tmp_path / "nested" / "trust.yaml"
    store = add_entry({}, "vendored", name="foo", why="carries LICENSE")
    save_store(p, store)
    assert read_store(p) == store
    assert (p.stat().st_mode & 0o777) == 0o600
