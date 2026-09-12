"""
Contract tests for the encrypted holding area.

Grouped by the property each one defends, because the properties are the reason
the tool exists: the key never lands on disk, the sidecar never leaks a path,
work-tagged content is refused, and a wrong key fails legibly instead of
silently producing nothing.
"""

from __future__ import annotations

import json

from conftest import SECRET_RE


# --- init: writing needs no secret ------------------------------------------


def test_init_prints_the_identity_but_never_stores_it(initialised):
    _run, state, _ident = initialised
    on_disk = list((state / "quarantine").iterdir())
    assert [p.name for p in on_disk] == ["recipients"]
    blob = (state / "quarantine" / "recipients").read_text()
    assert not SECRET_RE.search(blob), "the secret key was written to disk"
    assert blob.strip().splitlines()[-1].startswith("age1")


def test_init_refuses_to_clobber_an_existing_recipient(initialised):
    run, _state, _ident = initialised
    again = run("init")
    assert again.returncode == 1
    assert "refusing" in again.stderr


# --- put ---------------------------------------------------------------------


def test_put_archives_and_removes_the_original(initialised, tmp_path):
    run, state, _ident = initialised
    victim = tmp_path / "doomed.txt"
    victim.write_text("payload")
    result = run("put", "--reason", "test", str(victim))
    assert result.returncode == 0, result.stderr
    assert not victim.exists(), "original should be removed"
    assert len(list((state / "quarantine").glob("*.age"))) == 1


def test_put_keep_leaves_the_original(initialised, tmp_path):
    run, _state, _ident = initialised
    victim = tmp_path / "kept.txt"
    victim.write_text("payload")
    assert run("put", "--keep", str(victim)).returncode == 0
    assert victim.exists()


def test_put_refuses_work_tagged_content(initialised, tmp_path):
    """Quarantine is additive to retention, so it must not hold capped data."""
    run, state, _ident = initialised
    victim = tmp_path / "work.txt"
    victim.write_text("customer material")
    result = run("put", "--work-tagged", str(victim))
    assert result.returncode == 1
    assert "refusing" in result.stderr
    assert victim.exists(), "a refused put must not delete anything"
    assert list((state / "quarantine").glob("*.age")) == []


def test_put_is_atomic_about_missing_paths(initialised, tmp_path):
    run, state, _ident = initialised
    good = tmp_path / "good.txt"
    good.write_text("x")
    result = run("put", str(good), str(tmp_path / "nope.txt"))
    assert result.returncode == 2
    assert good.exists(), "no path should be archived if any is missing"
    assert list((state / "quarantine").glob("*.age")) == []


# --- the sidecar must not leak ----------------------------------------------


def test_sidecar_contains_no_paths_or_filenames(initialised, tmp_path):
    """A path can identify a customer as surely as file contents can."""
    run, state, _ident = initialised
    secretish = tmp_path / "tickets" / "acme-corp" / "12345"
    secretish.mkdir(parents=True)
    (secretish / "mail.md").write_text("body")
    assert run("put", str(secretish)).returncode == 0

    sidecar = next((state / "quarantine").glob("*.json"))
    raw = sidecar.read_text()
    for leak in ("acme-corp", "12345", "mail.md", "tickets"):
        assert leak not in raw, f"sidecar leaked {leak!r}"
    meta = json.loads(raw)
    assert set(meta) == {
        "id", "created", "expires", "retention_days",
        "retention_source", "items", "bytes",
    }


# --- reading -----------------------------------------------------------------


def test_peek_lists_members_without_writing(initialised, tmp_path):
    run, _state, ident = initialised
    d = tmp_path / "tree"
    d.mkdir()
    (d / "a.txt").write_text("aaa")
    (d / "b.txt").write_text("bbb")
    assert run("put", str(d)).returncode == 0
    entry = run("list").stdout.splitlines()[1].split()[0]

    out = run("peek", entry, identity=ident)
    assert out.returncode == 0, out.stderr
    assert "a.txt" in out.stdout and "b.txt" in out.stdout
    assert ".quarantine-manifest.json" not in out.stdout


def test_get_extracts_one_member_to_stdout(initialised, tmp_path):
    run, _state, ident = initialised
    d = tmp_path / "tree"
    d.mkdir()
    (d / "wanted.txt").write_text("the-right-bytes")
    (d / "other.txt").write_text("not-this")
    assert run("put", str(d)).returncode == 0
    entry = run("list").stdout.splitlines()[1].split()[0]

    out = run("get", entry, "wanted.txt", identity=ident)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "the-right-bytes"


def test_get_on_a_missing_member_is_an_error(initialised, tmp_path):
    run, _state, ident = initialised
    f = tmp_path / "solo.txt"
    f.write_text("x")
    assert run("put", str(f)).returncode == 0
    entry = run("list").stdout.splitlines()[1].split()[0]
    out = run("get", entry, "absent.txt", identity=ident)
    assert out.returncode == 2
    assert "peek" in out.stderr


def test_restore_round_trips_content(initialised, tmp_path):
    run, _state, ident = initialised
    f = tmp_path / "round.txt"
    f.write_text("survives-the-trip")
    assert run("put", str(f)).returncode == 0
    entry = run("list").stdout.splitlines()[1].split()[0]

    dest = tmp_path / "out"
    assert run("restore", entry, "--into", str(dest), identity=ident).returncode == 0
    recovered = [p for p in dest.rglob("round.txt")]
    assert recovered and recovered[0].read_text() == "survives-the-trip"


# --- failure modes -----------------------------------------------------------


def test_missing_identity_is_a_clear_refusal(initialised, tmp_path):
    run, _state, _ident = initialised
    f = tmp_path / "x.txt"
    f.write_text("x")
    run("put", str(f))
    entry = run("list").stdout.splitlines()[1].split()[0]
    out = run("peek", entry)
    assert out.returncode == 1
    assert "no identity source" in out.stderr


def test_wrong_key_fails_legibly(initialised, tmp_path):
    """A bad key yields an empty pipe; the error must not be 'empty file'."""
    run, _state, _ident = initialised
    f = tmp_path / "x.txt"
    f.write_text("x")
    run("put", str(f))
    entry = run("list").stdout.splitlines()[1].split()[0]

    bad = tmp_path / "bad.txt"
    bad.write_text("AGE-SECRET-KEY-1QQQQQQQQ\n")
    out = run("peek", entry, identity=f"file:{bad}")
    assert out.returncode == 1
    assert "wrong identity" in out.stderr
    assert "Traceback" not in out.stderr


def test_identity_from_stdin(initialised, tmp_path):
    run, _state, ident = initialised
    key = ident.split(":", 1)[1]
    f = tmp_path / "x.txt"
    f.write_text("piped")
    run("put", str(f))
    entry = run("list").stdout.splitlines()[1].split()[0]
    out = run("peek", entry, identity="-", stdin=open(key).read())
    assert out.returncode == 0, out.stderr


# --- expiry ------------------------------------------------------------------


def test_expire_respects_the_window(initialised, tmp_path):
    run, state, _ident = initialised
    f = tmp_path / "fresh.txt"
    f.write_text("x")
    run("put", "--days", "30", str(f))
    assert "nothing due" in run("expire").stdout

    sidecar = next((state / "quarantine").glob("*.json"))
    meta = json.loads(sidecar.read_text())
    meta["expires"] = "2020-01-01T00:00:00+00:00"
    sidecar.write_text(json.dumps(meta))

    assert "would delete" in run("expire", "--dry-run").stdout
    assert list((state / "quarantine").glob("*.age")), "dry-run must not delete"
    assert "deleted" in run("expire").stdout
    assert list((state / "quarantine").glob("*.age")) == []
