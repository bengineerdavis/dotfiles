"""Detecting foreign skill buckets, by evidence rather than name.

A foreign bucket is a directory another program owns inside the skills store.
Claude Code's cloud sync writes `synced/<id>/` into `~/.agents/skills` and
recreates a deleted skill byte-identical on the next session, so a `deny`
against it is not implementable — deletion loops forever. Recognising that is
the only honest move: the tool asserts "not mine to rule on" instead of faking a
refusal it cannot enforce.

Detection rests on three pieces of evidence, and all three must hold:

1. the directory sits at `<store>/synced/<id>/`,
2. a sibling marker `synced/.bucket-<id>` exists, and
3. `<id>/manifest.json` parses to a `skills[]` array.

A directory merely *named* like a bucket without that evidence still fails
closed, so a rogue directory cannot buy an exemption by picking the right name.
"""

from __future__ import annotations

import dataclasses
import json
import pathlib


@dataclasses.dataclass(frozen=True)
class ForeignBucket:
    id: str  # the directory name under synced/ — the match key, never the alias
    alias: str  # display-only label; renaming it changes no rule


def classify(id_: str, *, marker_exists: bool, manifest_text: str | None) -> bool:
    """Whether all three pieces of evidence hold for one bucket id.

    Kept free of filesystem I/O so every way a directory could fail the test can
    be exercised exhaustively. Any single missing piece returns False.
    """
    if not id_:
        return False
    if not marker_exists:
        return False
    if manifest_text is None:
        return False
    try:
        payload = json.loads(manifest_text)
    except json.JSONDecodeError:
        return False
    if not isinstance(payload, dict):
        return False
    return isinstance(payload.get("skills"), list)


def deduce_aliases(bucket_ids: list[str] | None) -> dict[str, str]:
    """One human label per bucket id, over the buckets that actually exist.

    The id is the match key; the alias is a display label, so renaming an alias
    can never change what a rule approves. A lone bucket gets the default label;
    several get the id's first eight characters tacked on so a human can tell
    them apart without the whole id.
    """
    ids = list(dict.fromkeys(bucket_ids or []))
    if len(ids) == 1:
        return {ids[0]: "claude-sync"}
    return {bucket_id: f"claude-sync@{bucket_id[:8]}" for bucket_id in ids}


def find_buckets(root: pathlib.Path) -> list[ForeignBucket]:
    """Every evidenced foreign bucket under `root/synced/`, in id order.

    Aliases are deduced over the buckets that pass the evidence check only — a
    rogue directory sitting beside a real bucket must not inflate the count and
    graduate the real one to a disambiguated alias it does not deserve.
    """
    synced = root / "synced"
    if not synced.is_dir():
        return []

    ids: list[str] = []
    for path in sorted(p for p in synced.iterdir() if p.is_dir()):
        bucket_id = path.name
        marker = (synced / f".bucket-{bucket_id}").is_file()
        manifest_path = path / "manifest.json"
        manifest_text = None
        if manifest_path.is_file():
            manifest_text = manifest_path.read_text(encoding="utf-8", errors="replace")
        if classify(bucket_id, marker_exists=marker, manifest_text=manifest_text):
            ids.append(bucket_id)

    aliases = deduce_aliases(ids)
    return [ForeignBucket(id=bucket_id, alias=aliases[bucket_id]) for bucket_id in ids]
