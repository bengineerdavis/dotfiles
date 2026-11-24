"""The change-of-mind resolver: `resolve --revisit`.

Recorded store denials are walked, shown with why and date, and offered keep /
retract / approve-instead. Repo-level denials are reported read-only, never
retracted from the store. Scope deliberately excludes `exclude`, which stays
retractable via `trust remove --exclude`.
"""

from __future__ import annotations

import textwrap

# pyrefly: ignore [missing-import]
from skill_trust.cli import PERMITTED, main

# pyrefly: ignore [missing-import]
from skill_trust.store import read_store


def _config(tmp_path, body: str, name: str = "rules.yaml"):
    d = tmp_path.parent / f"cfg-{tmp_path.name}"
    d.mkdir(exist_ok=True)
    p = d / name
    p.write_text(textwrap.dedent(body))
    return str(p)


def _tty(monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)


def _answers(monkeypatch, *answers: str):
    it = iter(answers)

    def _input(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration as exc:
            raise EOFError from exc

    monkeypatch.setattr("builtins.input", _input)


def _revisit(tmp_path, *extra: str):
    """Run `resolve --revisit` hermetically: no manager inventory by default."""
    return main(
        [
            "--config",
            _config(tmp_path, "approved_sources: []\n"),
            "--store",
            str(tmp_path / "store.yaml"),
            "resolve",
            "--revisit",
            "--skills-dir",
            str(tmp_path),
            "--no-inventory",
            *extra,
        ]
    )


def test_nothing_to_revisit_is_a_pass(tmp_path, monkeypatch, capsys):
    _tty(monkeypatch)
    assert _revisit(tmp_path) == PERMITTED
    assert "nothing to revisit" in capsys.readouterr().out


def _store(tmp_path, body: str):
    p = tmp_path / "store.yaml"
    p.write_text(textwrap.dedent(body))
    return str(p)


def test_retract_removes_the_denial(tmp_path, monkeypatch, capsys):
    _tty(monkeypatch)
    _store(tmp_path, "deny_skills:\n  - name: mystery\n    why: wanted it gone\n")
    _answers(monkeypatch, "r")
    assert _revisit(tmp_path) == PERMITTED
    out = capsys.readouterr().out
    assert "deny_skills: mystery" in out
    assert "wanted it gone" in out
    assert read_store(tmp_path / "store.yaml").get("deny_skills", []) == []


def test_approve_instead_on_a_source_lifts_the_ban(tmp_path, monkeypatch, capsys):
    _tty(monkeypatch)
    _store(tmp_path, "deny_sources:\n  - source: bad/repo\n    why: no licence\n")
    _answers(monkeypatch, "a", "reviewed again, it carries MIT now")
    assert _revisit(tmp_path) == PERMITTED
    capsys.readouterr()
    store = read_store(tmp_path / "store.yaml")
    assert store.get("deny_sources", []) == []
    assert store["approved_sources"][0]["source"] == "bad/repo"
    assert store["approved_sources"][0]["why"] == "reviewed again, it carries MIT now"


def test_approve_instead_on_a_skill_vendors_it(tmp_path, monkeypatch, capsys):
    _tty(monkeypatch)
    _store(tmp_path, "deny_skills:\n  - name: hand-placed\n    why: untrusted\n")
    _answers(monkeypatch, "a", "it carries LICENSE now")
    assert _revisit(tmp_path) == PERMITTED
    capsys.readouterr()
    store = read_store(tmp_path / "store.yaml")
    assert store.get("deny_skills", []) == []
    assert store["vendored"][0]["name"] == "hand-placed"
    assert store["vendored"][0]["why"] == "it carries LICENSE now"


def test_gone_skill_is_marked(tmp_path, monkeypatch, capsys):
    _tty(monkeypatch)
    _store(tmp_path, "deny_skills:\n  - name: no-longer-here\n    why: removed it\n")
    _answers(monkeypatch, "k")
    assert _revisit(tmp_path) == PERMITTED
    assert "gone from disk" in capsys.readouterr().out


def test_repo_denials_are_reported_read_only(tmp_path, monkeypatch, capsys):
    _tty(monkeypatch)
    _answers(monkeypatch)  # no prompts: repo denials are never asked about
    code = main(
        [
            "--config",
            _config(tmp_path, "deny_sources: [evil/org]\n"),
            "--store",
            str(tmp_path / "store.yaml"),
            "resolve",
            "--revisit",
            "--skills-dir",
            str(tmp_path),
            "--no-inventory",
        ]
    )
    assert code == PERMITTED
    out = capsys.readouterr().out
    assert "(repo rule) deny_sources: evil/org" in out


def test_a_denied_source_still_declared_is_not_marked_gone(
    tmp_path, monkeypatch, capsys
):
    """A deny_source whose pattern still matches a declared skill stays. None
    of the other sources match, so none is marked gone either.
    """
    _tty(monkeypatch)
    _store(tmp_path, "deny_sources:\n  - source: present/repo\n    why: banned\n")
    declared = tmp_path.parent / "declared.json"
    declared.write_text('{"skills": [{"name": "cool", "source": "present/repo"}]}')
    _answers(monkeypatch, "k")
    code = main(
        [
            "--config",
            _config(tmp_path, "approved_sources: []\n"),
            "--store",
            str(tmp_path / "store.yaml"),
            "resolve",
            "--revisit",
            "--skills-dir",
            str(tmp_path),
            "--declared-json",
            str(declared),
        ]
    )
    assert code == PERMITTED
    assert "gone from disk" not in capsys.readouterr().out


def test_a_denied_source_with_no_declared_match_is_marked_gone(
    tmp_path, monkeypatch, capsys
):
    _tty(monkeypatch)
    _store(tmp_path, "deny_sources:\n  - source: old/repo\n    why: banned\n")
    declared = tmp_path.parent / "declared.json"
    declared.write_text('{"skills": [{"name": "cool", "source": "other/repo"}]}')
    _answers(monkeypatch, "k")
    code = main(
        [
            "--config",
            _config(tmp_path, "approved_sources: []\n"),
            "--store",
            str(tmp_path / "store.yaml"),
            "resolve",
            "--revisit",
            "--skills-dir",
            str(tmp_path),
            "--declared-json",
            str(declared),
        ]
    )
    assert code == PERMITTED
    assert "gone from disk" in capsys.readouterr().out


def test_with_no_inventory_a_source_is_never_marked_gone(tmp_path, monkeypatch, capsys):
    """Unknown: without an inventory (and nothing installed) a denied source is
    not assertably gone, so it is shown with no mark, still retractable.
    """
    _tty(monkeypatch)
    _store(tmp_path, "deny_sources:\n  - source: maybe/repo\n    why: banned\n")
    _answers(monkeypatch, "k")
    assert _revisit(tmp_path) == PERMITTED
    assert "gone from disk" not in capsys.readouterr().out


def test_an_interruption_keeps_the_decisions_already_made(
    tmp_path, monkeypatch, capsys
):
    _tty(monkeypatch)
    _store(
        tmp_path,
        "deny_skills:\n  - name: one\n    why: w\n  - name: two\n    why: w\n",
    )
    _answers(monkeypatch, "r")  # then EOF on "two"
    assert _revisit(tmp_path) == PERMITTED
    out = capsys.readouterr().out
    assert "interrupted" in out
    store = read_store(tmp_path / "store.yaml")
    assert "two" in [e["name"] for e in store.get("deny_skills", [])]
    assert "one" not in [e["name"] for e in store.get("deny_skills", [])]


def test_without_a_terminal_it_refuses(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    _store(tmp_path, "deny_skills:\n  - name: mystery\n    why: w\n")
    assert _revisit(tmp_path) == 3  # ERROR
    assert "needs a terminal" in capsys.readouterr().err
