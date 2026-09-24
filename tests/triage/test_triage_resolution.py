"""
Resolution precedence: flag beats environment beats fallback.

The queue named this the obvious first case for bin/triage coverage: platform
and docs resolve flag -> $TRIAGE_PLATFORM / $TRIAGE_DOCS -> default, and nothing
pinned that order or the empty-docs warning that follows from it.
"""
from __future__ import annotations


def test_platform_flag_beats_env(triage_module, monkeypatch):
    monkeypatch.setenv("TRIAGE_PLATFORM", "EnvCorp")
    assert triage_module.resolve_platform("FlagCorp") == "FlagCorp"


def test_platform_env_beats_default(triage_module, monkeypatch):
    monkeypatch.setenv("TRIAGE_PLATFORM", "EnvCorp")
    assert triage_module.resolve_platform(None) == "EnvCorp"


def test_platform_falls_back_to_default(triage_module, monkeypatch):
    monkeypatch.delenv("TRIAGE_PLATFORM", raising=False)
    assert triage_module.resolve_platform(None) == triage_module.DEFAULT_PLATFORM


def test_platform_empty_flag_falls_through_to_env(triage_module, monkeypatch):
    """A falsy flag is not a value: `--platform ''` falls through the `or`
    chain rather than stamping an empty label."""
    monkeypatch.setenv("TRIAGE_PLATFORM", "EnvCorp")
    assert triage_module.resolve_platform("") == "EnvCorp"


def test_docs_flag_beats_env(triage_module, monkeypatch):
    monkeypatch.setenv("TRIAGE_DOCS", "https://env.example")
    assert triage_module.resolve_docs(["https://flag.example"]) == [
        "https://flag.example"
    ]


def test_docs_env_split_when_no_flag(triage_module, monkeypatch):
    monkeypatch.setenv("TRIAGE_DOCS", "https://a.example https://b.example")
    assert triage_module.resolve_docs(None) == [
        "https://a.example",
        "https://b.example",
    ]


def test_docs_unconfigured_is_empty(triage_module, monkeypatch):
    monkeypatch.delenv("TRIAGE_DOCS", raising=False)
    assert triage_module.resolve_docs(None) == []


def test_docs_empty_env_is_empty(triage_module, monkeypatch):
    monkeypatch.setenv("TRIAGE_DOCS", "")
    assert triage_module.resolve_docs(None) == []


def test_empty_docs_warning_fires_when_unconfigured(cli):
    proc = cli()
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr, "expected a warning on stderr"
    assert "no doc sources configured" in proc.stderr


def test_empty_docs_warning_silent_when_flag_configured(cli):
    proc = cli("--docs", "https://docs.example.io")
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr, "expected status output; a silent run proves nothing"
    assert "no doc sources configured" not in proc.stderr


def test_empty_docs_warning_silent_when_env_configured(cli):
    proc = cli(env_extra={"TRIAGE_DOCS": "https://docs.example.io"})
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr, "expected status output; a silent run proves nothing"
    assert "no doc sources configured" not in proc.stderr
