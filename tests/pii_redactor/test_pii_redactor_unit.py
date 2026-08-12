"""
Unit tests for pii-redactor's pure helpers.

These have no bats equivalent — under bash the output templating could only be
exercised by running the whole CLI and looking at which file appeared. Calling
default_output() directly makes the path edge cases explicit and fast, which is
where the real subtlety lives: a dotted directory must not be mistaken for an
extension, and a dotfile must not lose its name.
"""
from __future__ import annotations

import pytest


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("mail.md",        "mail-pii-removed.md"),
        ("a/b/mail.md",    "a/b/mail-pii-removed.md"),
        ("./notes.txt",    "notes-pii-removed.txt"),
        # Dot in a directory, none in the basename — the suffix goes on the end
        # rather than being spliced into the directory name.
        ("dir.v2/mail",    "dir.v2/mail-pii-removed"),
        # A leading dot is part of the name, not an extension separator.
        (".hidden",        ".hidden-pii-removed"),
        # Multiple dots: only the last one is the extension.
        ("mail.backup.md", "mail.backup-pii-removed.md"),
        # No input at all means stdin, which has no name to reuse.
        ("",               "stdin-pii-removed.md"),
    ],
)
def test_default_output_paths(pii_module, given, expected):
    assert pii_module.default_output(given) == expected


def test_build_cmd_uses_system_and_no_log(pii_module, monkeypatch):
    monkeypatch.delenv("LLM_EXTRA_OPTS", raising=False)
    cmd = pii_module.build_cmd("some-model")
    assert cmd[:3] == ["llm", "-m", "some-model"]
    assert "-s" in cmd and "-n" in cmd
    assert "-p" not in cmd


def test_build_cmd_word_splits_extra_opts(pii_module, monkeypatch):
    monkeypatch.setenv("LLM_EXTRA_OPTS", "-o think false")
    cmd = pii_module.build_cmd("m")
    # Three separate argv entries, not one string — this is what the unquoted
    # ${LLM_EXTRA_OPTS} in the bash version did, and callers rely on it.
    assert cmd[-3:] == ["-o", "think", "false"]


def test_child_env_defaults_pymupdf_message(pii_module, monkeypatch):
    monkeypatch.delenv("PYMUPDF_MESSAGE", raising=False)
    assert pii_module.child_env()["PYMUPDF_MESSAGE"] == "fd:2"


def test_child_env_respects_an_explicit_setting(pii_module, monkeypatch):
    """setdefault, not overwrite — an operator choosing a destination keeps it."""
    monkeypatch.setenv("PYMUPDF_MESSAGE", "path:/tmp/pymupdf.log")
    assert pii_module.child_env()["PYMUPDF_MESSAGE"] == "path:/tmp/pymupdf.log"
