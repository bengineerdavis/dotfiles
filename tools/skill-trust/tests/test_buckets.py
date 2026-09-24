"""Foreign bucket detection, by evidence rather than name.

A foreign bucket is a directory another program owns inside the skills store —
Claude Code's cloud sync writes `synced/<id>/`. Detection rests on three pieces
of evidence that all must hold, so a directory merely *named* like a bucket
cannot buy an exemption: the path `synced/<id>/`, a sibling `.bucket-<id>`
marker, and a `manifest.json` that parses to a `skills[]` array.

Run:
    uv run --project tools/skill-trust pytest tools/skill-trust
"""

from __future__ import annotations

import json

from skill_trust.buckets import ForeignBucket, classify, deduce_aliases, find_buckets


def _bucket(root, bucket_id: str, *, marker: bool = True, manifest: bool = True,
            skills: tuple[str, ...] = ("one", "two")):
    """Build a bucket-shaped directory under `root/synced/`."""
    synced = root / "synced"
    synced.mkdir(parents=True, exist_ok=True)
    bucket = synced / bucket_id
    bucket.mkdir(parents=True, exist_ok=True)
    if marker:
        (synced / f".bucket-{bucket_id}").write_text("")
    if manifest:
        (bucket / "manifest.json").write_text(
            json.dumps({"skills": [{"name": s} for s in skills]}))
    return bucket


# --- classify: every piece of evidence is required ---------------------------


def test_classify_requires_all_three_pieces_of_evidence():
    manifest = json.dumps({"skills": [{"name": "x"}]})
    assert classify("id", marker_exists=True, manifest_text=manifest)
    assert not classify("id", marker_exists=False, manifest_text=manifest)
    assert not classify("id", marker_exists=True, manifest_text=None)
    assert not classify("", marker_exists=True, manifest_text=manifest)


def test_a_manifest_that_does_not_parse_is_not_evidence():
    assert not classify("id", marker_exists=True, manifest_text="not json")
    assert not classify("id", marker_exists=True, manifest_text="[]")
    assert not classify("id", marker_exists=True,
                        manifest_text=json.dumps({"skills": "nope"}))


# --- aliases -----------------------------------------------------------------


def test_a_lone_bucket_gets_the_default_alias():
    assert deduce_aliases(["a"]) == {"a": "claude-sync"}


def test_several_buckets_are_disambiguated_by_id_prefix():
    assert deduce_aliases(["abcdefgh-1234", "ijklmnop-5678"]) == {
        "abcdefgh-1234": "claude-sync@abcdefgh",
        "ijklmnop-5678": "claude-sync@ijklmnop",
    }


def test_no_ids_no_aliases():
    assert deduce_aliases([]) == {}
    assert deduce_aliases(None) == {}


# --- find_buckets ------------------------------------------------------------


def test_no_synced_directory_no_buckets(tmp_path):
    assert find_buckets(tmp_path) == []


def test_an_evidenced_bucket_is_found(tmp_path):
    _bucket(tmp_path, "org_user")
    assert find_buckets(tmp_path) == [
        ForeignBucket(id="org_user", alias="claude-sync")]


def test_a_dir_without_evidence_is_not_a_bucket(tmp_path):
    _bucket(tmp_path, "org_user", marker=False)
    assert find_buckets(tmp_path) == []


def test_a_rogue_dir_does_not_disambiguate_the_real_bucket(tmp_path):
    """A directory merely named like a bucket must not inflate the alias count
    and graduate a lone bucket to a disambiguated alias."""
    _bucket(tmp_path, "real_bucket")
    _bucket(tmp_path, "rogue", marker=False)
    assert find_buckets(tmp_path) == [
        ForeignBucket(id="real_bucket", alias="claude-sync")]