"""Unit tests for pii-redactor's pure helpers.

These have no bats equivalent — under bash the output templating could only be
exercised by running the whole CLI and looking at which file appeared. Calling
default_output() directly makes the path edge cases explicit and fast, which is
where the real subtlety lives: a dotted directory must not be mistaken for an
extension, and a dotfile must not lose its name.
"""

from __future__ import annotations

import os

import pytest


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("mail.md", "mail-pii-removed.md"),
        ("a/b/mail.md", "a/b/mail-pii-removed.md"),
        ("./notes.txt", "notes-pii-removed.txt"),
        # Dot in a directory, none in the basename — the suffix goes on the end
        # rather than being spliced into the directory name.
        ("dir.v2/mail", "dir.v2/mail-pii-removed"),
        # A leading dot is part of the name, not an extension separator.
        (".hidden", ".hidden-pii-removed"),
        # Multiple dots: only the last one is the extension.
        ("mail.backup.md", "mail.backup-pii-removed.md"),
        # No input at all means stdin, which has no name to reuse.
        ("", "stdin-pii-removed.md"),
    ],
)
def test_default_output_paths(pii_module, given, expected):
    assert pii_module.default_output(given) == expected


def test_build_cmd_uses_system_and_no_log(pii_module, monkeypatch):
    monkeypatch.delenv("LLM_EXTRA_OPTS", raising=False)
    cmd = pii_module.build_cmd("ollama/some-model")
    assert cmd[:3] == ["llm", "-m", "ollama/some-model"]
    assert "-s" in cmd and "-n" in cmd
    assert "-p" not in cmd


def test_build_cmd_hides_reasoning(pii_module, monkeypatch):
    """-R keeps the model's chain-of-thought off stderr.

    A reasoning model narrates what it is removing and quotes the values, so
    without -R the PII lands on stderr — which outlives the run in logs and
    scrollback. Measured before the flag: 7 occurrences of a name the released
    output had replaced. The flag belongs in the base command, not in
    LLM_EXTRA_OPTS, so a caller cannot drop it by setting that variable.
    """
    monkeypatch.delenv("LLM_EXTRA_OPTS", raising=False)
    assert "-R" in pii_module.build_cmd("ollama/some-model")


def test_build_cmd_hides_reasoning_even_with_extra_opts(pii_module, monkeypatch):
    monkeypatch.setenv("LLM_EXTRA_OPTS", "-o think false")
    assert "-R" in pii_module.build_cmd("ollama/some-model")


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        # A bare ollama tag is what `ollama list` prints, and `llm` cannot
        # resolve it — "Unknown model" even though the model is installed.
        ("qwen3.8:27b-mlx", "ollama/qwen3.8:27b-mlx"),
        # An already-qualified name passes through untouched.
        ("ollama/qwen3.8:27b-mlx", "ollama/qwen3.8:27b-mlx"),
        # Hosted providers keep their own routing.
        ("openrouter/qwen/qwen3.5-9b", "openrouter/qwen/qwen3.5-9b"),
    ],
)
def test_build_cmd_qualifies_a_bare_model_with_its_provider(
    pii_module, monkeypatch, given, expected
):
    monkeypatch.delenv("LLM_EXTRA_OPTS", raising=False)
    cmd = pii_module.build_cmd(given)
    assert cmd[2] == expected


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


def test_the_script_resolves_without_a_deployed_copy(monkeypatch, tmp_path):
    """The suite must run on a fresh clone, not only on an applied machine.

    Measured 2026-11-05: CI failed 55 pii_redactor tests with
    `FileNotFoundError: /home/runner/bin/pii-redactor`. `SCRIPT` was
    `Path.home()/"bin"/"pii-redactor"`, which exists only after
    `chezmoi apply` — so the suite tested a deployed machine and
    errored everywhere else.

    The tests need the script's source, which is always in the repo.
    This pins the property that matters: with no deployed copy, the
    resolver returns something that exists and can actually run. An
    earlier version of this test asserted a path shape (`home` or
    `bin` in the parts), which broke as soon as the resolver staged
    an executable copy into a temp directory — the shape was never
    the property, the runnability is.
    """
    # pyrefly: ignore [missing-import]
    from pii_redactor_harness import _resolve_script

    # A home with no ~/bin at all, which is what a runner has.
    empty_home = tmp_path / "home"
    empty_home.mkdir()
    monkeypatch.setenv("HOME", str(empty_home))

    resolved = _resolve_script()
    assert resolved.is_file(), f"resolved to a missing file: {resolved}"
    assert resolved.name == "pii-redactor", (
        f"resolved to {resolved}, which is not the pii-redactor script"
    )
    assert os.access(resolved, os.X_OK), (
        f"{resolved} is not executable — chezmoi stores the source mode 644 "
        "and applies the bit at deploy time, so the fallback must stage a "
        "runnable copy"
    )
