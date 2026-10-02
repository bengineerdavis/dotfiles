"""The editors catalogue schema — the input contract the topics' install
loops depend on.

`dotfiles/config/editors.yaml` is the shared truth two topics install from.
A malformed entry fails only at provisioning time, on a machine, mid-run —
so the schema is checked here, in CI, where the failure names the entry.

The dates on verdicts are part of the contract (spec.md § Evidence —
measured numbers carry their conditions), so a missing date is a schema
violation, not a style preference.
"""

from __future__ import annotations

import pathlib

import yaml

CATALOGUE = (
    pathlib.Path(__file__).resolve().parents[2] / "dotfiles" / "config" / "editors.yaml"
)


def _load() -> dict:
    assert CATALOGUE.exists(), (
        f"{CATALOGUE} is missing — the topics' install loops have no input"
    )
    data = yaml.safe_load(CATALOGUE.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "catalogue must be a mapping"
    return data


def test_every_entry_carries_id_why_and_dated_verdicts():
    for entry in _load()["editor_extensions"]:
        assert entry.get("id"), f"entry without id: {entry}"
        assert entry.get("why"), f"{entry['id']}: why is required"
        verdicts = entry.get("verdicts") or {}
        assert verdicts, f"{entry['id']}: verdicts are required"
        for editor, verdict in verdicts.items():
            assert verdict.get("status"), (
                f"{entry['id']}: {editor} verdict has no status"
            )
            assert verdict.get("checked"), (
                f"{entry['id']}: {editor} verdict is not dated"
            )


def test_ids_are_unique():
    ids = [entry["id"] for entry in _load()["editor_extensions"]]
    assert len(ids) == len(set(ids)), (
        f"duplicate ids: {sorted(i for i in ids if ids.count(i) > 1)}"
    )


def test_not_available_verdicts_scope_the_entry_out():
    """A verdict of not-available is the dated evidence for the editors:
    scope — a shared-by-default entry with a not-available verdict for some
    editor must carry an editors list that excludes it.
    """
    for entry in _load()["editor_extensions"]:
        for editor, verdict in (entry.get("verdicts") or {}).items():
            if verdict["status"] != "not-available":
                continue
            scoped = entry.get("editors") or []
            assert editor not in scoped, (
                f"{entry['id']}: {editor} is not-available but the entry "
                f"still targets it (editors: {scoped})"
            )


def test_ignored_entries_are_dated_and_verdicted():
    for entry in _load()["editor_extensions_ignored"]:
        assert entry.get("id"), f"ignored entry without id: {entry}"
        assert entry.get("verdict"), f"{entry['id']}: ignored entry has no verdict"
        assert entry.get("checked"), f"{entry['id']}: ignored entry is not dated"
        assert entry.get("why"), f"{entry['id']}: ignored entry has no why"
