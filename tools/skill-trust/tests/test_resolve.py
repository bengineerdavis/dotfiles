"""The interactive resolver.

First detection asks; a recorded decision is never re-asked. The mechanics
under test: the no-terminal refusal, each choice persisting to the store,
"leave" writing nothing, an interruption keeping what was already answered,
and the re-judge at the end agreeing with what the guard will say next run.
"""

from __future__ import annotations

import json
import textwrap

import pytest

# pyrefly: ignore [missing-import]
from skill_trust.cli import DENIED, ERROR, PERMITTED, main

# pyrefly: ignore [missing-import]
from skill_trust.store import read_store


def _config(tmp_path, body: str, name: str = "rules.yaml"):
    d = tmp_path.parent / f"cfg-{tmp_path.name}"
    d.mkdir(exist_ok=True)
    p = d / name
    p.write_text(textwrap.dedent(body))
    return str(p)


def _skill(tmp_path, name: str, frontmatter: str | None = None):
    d = tmp_path / name
    d.mkdir(parents=True)
    body = f"---\nname: {name}\ndescription: x\n"
    if frontmatter:
        body += f"{frontmatter}\n"
    (d / "SKILL.md").write_text(body + "---\n\n# x\n")
    return d


def _declared(tmp_path, name: str, source: str):
    d = tmp_path.parent / f"cfg-{tmp_path.name}"
    d.mkdir(exist_ok=True)
    p = d / "declared.json"
    p.write_text(json.dumps({"skills": [{"name": name, "source": source}]}))
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


def _resolve(tmp_path, *extra: str):
    return main(
        [
            "--offline",
            "--config",
            _config(tmp_path, "approved_sources: []\n"),
            "--store",
            str(tmp_path / "store.yaml"),
            "resolve",
            "--skills-dir",
            str(tmp_path),
            *extra,
        ]
    )


def test_without_a_terminal_it_refuses_and_names_the_fix(tmp_path, monkeypatch, capsys):
    _skill(tmp_path, "mystery")
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert _resolve(tmp_path) == ERROR
    assert "needs a terminal" in capsys.readouterr().err


def test_nothing_undecided_is_a_pass(tmp_path, monkeypatch, capsys):
    _tty(monkeypatch)
    _skill(tmp_path, "fine", frontmatter="license: MIT")
    assert _resolve(tmp_path) == PERMITTED
    assert "nothing to resolve" in capsys.readouterr().out


def test_vendoring_an_undeclared_directory_relents(tmp_path, monkeypatch, capsys):
    _tty(monkeypatch)
    _skill(tmp_path, "hand-placed")
    _answers(monkeypatch, "v", "carries LICENSE and PROVENANCE")
    assert _resolve(tmp_path) == PERMITTED
    store = read_store(tmp_path / "store.yaml")
    assert store["vendored"][0]["name"] == "hand-placed"
    assert store["vendored"][0]["why"] == "carries LICENSE and PROVENANCE"
    assert "PERMITTED" in capsys.readouterr().out


def test_denying_an_undeclared_directory_keeps_failing(tmp_path, monkeypatch, capsys):
    """Reject persists the denial rather than going quiet: the re-judge still
    fails, now as a recorded decision, until the directory is removed.
    """
    _tty(monkeypatch)
    _skill(tmp_path, "unwanted")
    _answers(monkeypatch, "d", "do not want this on the machine")
    assert _resolve(tmp_path) == DENIED
    store = read_store(tmp_path / "store.yaml")
    assert store["deny_skills"][0]["name"] == "unwanted"
    out = capsys.readouterr().out
    assert "[deny_skills] unwanted" in out
    assert "finding(s) remain" in out


def test_approving_a_declared_source_relents(tmp_path, monkeypatch):
    _tty(monkeypatch)
    _skill(tmp_path, "cool-skill")
    declared = _declared(tmp_path, "cool-skill", "thirdparty/skills")
    _answers(monkeypatch, "a", "MIT, reviewed the repo")
    assert _resolve(tmp_path, "--declared-json", declared) == PERMITTED
    store = read_store(tmp_path / "store.yaml")
    assert store["approved_sources"][0]["source"] == "thirdparty/skills"


def test_leave_writes_nothing_and_stays_denied(tmp_path, monkeypatch):
    _tty(monkeypatch)
    _skill(tmp_path, "mystery")
    _answers(monkeypatch, "l")
    assert _resolve(tmp_path) == DENIED
    assert read_store(tmp_path / "store.yaml") == {}


def test_an_empty_why_is_asked_again(tmp_path, monkeypatch):
    _tty(monkeypatch)
    _skill(tmp_path, "hand-placed")
    _answers(monkeypatch, "v", "", "   ", "the real reason")
    assert _resolve(tmp_path) == PERMITTED
    assert (
        read_store(tmp_path / "store.yaml")["vendored"][0]["why"] == "the real reason"
    )


def test_an_interruption_keeps_the_decisions_already_made(
    tmp_path, monkeypatch, capsys
):
    _tty(monkeypatch)
    _skill(tmp_path, "one")
    _skill(tmp_path, "two")
    _answers(monkeypatch, "v", "first decided")  # then EOF on "two"
    assert _resolve(tmp_path) == DENIED
    store = read_store(tmp_path / "store.yaml")
    assert [e["name"] for e in store["vendored"]] == ["one"]
    assert "interrupted" in capsys.readouterr().out


def test_already_decided_findings_are_reported_not_asked(tmp_path, monkeypatch, capsys):
    """A recorded denial is never re-asked — that is what makes first
    detection the only question a human ever answers twice.
    """
    _tty(monkeypatch)
    _skill(tmp_path, "banned-thing")
    _answers(monkeypatch)  # no answers available; any prompt would EOF
    code = main(
        [
            "--offline",
            "--config",
            _config(tmp_path, "deny_skills: [banned-thing]\n"),
            "--store",
            str(tmp_path / "store.yaml"),
            "resolve",
            "--skills-dir",
            str(tmp_path),
        ]
    )
    assert code == DENIED
    assert "already decided" in capsys.readouterr().out
