"""The store wired into check/audit, and the `trust` subcommand.

The wiring is what makes an interactive decision stick: the same audit the
Ansible guard runs must relent when the human approves, keep refusing when
the human denies, and never let the store overturn a repo ban.
"""

from __future__ import annotations

import textwrap

# pyrefly: ignore [missing-import]
from skill_trust.cli import DENIED, ERROR, PERMITTED, main


def _config(tmp_path, body: str, name: str = "rules.yaml"):
    # Distinct filenames per call: config and store often coexist in one test,
    # and one path for both would have each write silently overwrite the other.
    d = tmp_path.parent / f"cfg-{tmp_path.name}"
    d.mkdir(exist_ok=True)
    p = d / name
    p.write_text(textwrap.dedent(body))
    return str(p)


def _skill(tmp_path, name: str):
    d = tmp_path / name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(f"---\nname: {name}\ndescription: x\n---\n\n# x\n")
    return d


def test_check_relents_when_the_store_approves(tmp_path):
    cfg = _config(tmp_path, "approved_sources: []\n")
    store = _config(tmp_path, "approved_sources: [owner/lib]\n", name="store.yaml")
    code = main(["--offline", "--config", cfg, "--store", store, "check", "owner/lib"])
    assert code == PERMITTED


def test_check_tightens_when_the_store_denies(tmp_path):
    """The repo approves; the human said no on this machine. No wins."""
    cfg = _config(tmp_path, "approved_sources: [owner/lib]\n")
    store = _config(tmp_path, "deny_sources: [owner/lib]\n", name="store.yaml")
    code = main(["--offline", "--config", cfg, "--store", store, "check", "owner/lib"])
    assert code == DENIED


def test_a_store_approval_cannot_overturn_a_repo_ban(tmp_path):
    cfg = _config(tmp_path, "deny_sources: [bad/repo]\n")
    store = _config(tmp_path, "approved_sources: [bad/repo]\n", name="store.yaml")
    code = main(["--offline", "--config", cfg, "--store", store, "check", "bad/repo"])
    assert code == DENIED


def test_an_absent_store_changes_nothing(tmp_path, capsys):
    """The default state of a fresh machine: no decisions, no error."""
    _skill(tmp_path, "mystery")
    cfg = _config(tmp_path, "approved_sources: []\n")
    code = main(
        [
            "--offline",
            "--config",
            cfg,
            "--store",
            str(tmp_path / "never-written.yaml"),
            "audit",
            "--skills-dir",
            str(tmp_path),
        ]
    )
    assert code == DENIED
    assert "mystery" in capsys.readouterr().out


def test_a_malformed_store_is_an_error_not_a_denial(tmp_path):
    cfg = _config(tmp_path, "{}\n")
    store = _config(tmp_path, "approved_soruces: [owner/lib]\n", name="store.yaml")
    code = main(["--offline", "--config", cfg, "--store", store, "check", "owner/lib"])
    assert code == ERROR


def test_audit_denies_a_store_denied_skill_by_name(tmp_path, capsys):
    _skill(tmp_path, "mystery")
    cfg = _config(tmp_path, "approved_sources: []\n")
    store = _config(tmp_path, "deny_skills: [mystery]\n", name="store.yaml")
    code = main(
        [
            "--offline",
            "--config",
            cfg,
            "--store",
            store,
            "audit",
            "--skills-dir",
            str(tmp_path),
        ]
    )
    assert code == DENIED
    assert "[deny_skills] mystery" in capsys.readouterr().out


def test_trust_add_list_remove_round_trip(tmp_path, capsys):
    store = str(tmp_path / "trust.yaml")
    assert (
        main(
            [
                "--store",
                store,
                "trust",
                "add",
                "--source",
                "owner/lib",
                "--why",
                "licence checked by hand",
            ]
        )
        == PERMITTED
    )
    assert main(["--store", store, "trust", "list"]) == PERMITTED
    out = capsys.readouterr().out
    assert "owner/lib" in out and "licence checked by hand" in out
    assert (
        main(["--store", store, "trust", "remove", "--source", "owner/lib"])
        == PERMITTED
    )
    assert main(["--store", store, "trust", "list"]) == PERMITTED
    assert "no decisions recorded" in capsys.readouterr().out


def test_trust_add_then_check_uses_the_decision(tmp_path):
    """The add is not decorative: the very next check honours it."""
    store = str(tmp_path / "trust.yaml")
    cfg = _config(tmp_path, "approved_sources: []\n")
    main(["--store", store, "trust", "add", "--source", "owner/lib", "--why", "w"])
    assert (
        main(["--offline", "--config", cfg, "--store", store, "check", "owner/lib"])
        == PERMITTED
    )


def test_trust_remove_without_a_match_says_so(tmp_path, capsys):
    store = str(tmp_path / "trust.yaml")
    code = main(["--store", store, "trust", "remove", "--source", "ghost/lib"])
    assert code == ERROR
    assert "no approved_sources entry" in capsys.readouterr().err


def test_trust_add_exclude_needs_its_source(tmp_path, capsys):
    store = str(tmp_path / "trust.yaml")
    code = main(
        ["--store", store, "trust", "add", "--exclude", "skill-x", "--why", "w"]
    )
    assert code == ERROR
    assert "--from" in capsys.readouterr().err
