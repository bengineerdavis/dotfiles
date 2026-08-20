"""
CLI behaviour for clipped — the seventeen bats cases, ported to pytest.

The bats suite was written as a specification before the behaviour existed:
auto mode, file arguments and the guidance messages were all described there and
none of them were implemented. These now pass against the Python port.
"""
from __future__ import annotations

import pytest

from conftest import CLIPBOARD_CONTENT


# ── help and version ──────────────────────────────────────────────────────────

def test_help_documents_auto_mode(run_clipped):
    r = run_clipped("--help")
    assert r.returncode == 0
    assert "Auto mode" in r.stdout
    assert "stdin is piped" in r.stdout
    assert "stdin is a TTY" in r.stdout


@pytest.mark.parametrize("flag", ["-h", "help", "--help"])
def test_help_variants_exit_zero(run_clipped, flag):
    assert run_clipped(flag).returncode == 0


def test_version_prints_version_string(run_clipped):
    r = run_clipped("--version")
    assert r.returncode == 0
    assert "clipped version 1.2.0" in r.stdout


# ── paste ─────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("cmd", ["paste", "p"])
def test_paste_outputs_clipboard(run_clipped, cmd):
    r = run_clipped(cmd)
    assert r.returncode == 0
    assert r.stdout == CLIPBOARD_CONTENT


# ── copy from stdin ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("cmd", ["copy", "c"])
def test_copy_reads_stdin(run_clipped, captured, cmd):
    r = run_clipped(cmd, stdin="hello clipboard")
    assert r.returncode == 0
    assert captured() == "hello clipboard"


def test_copy_without_stdin_fails_with_guidance(run_clipped_tty):
    """A TTY and no files means neither input source was given — say so."""
    rc, out = run_clipped_tty("copy")
    assert rc != 0
    assert "copy mode expects stdin" in out
    assert "clipped c README.md" in out


# ── copy from files ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("cmd", ["copy", "c"])
def test_copy_single_file(run_clipped, captured, clip_env, cmd):
    f = clip_env / "file1.txt"
    f.write_text("file one content")
    r = run_clipped(cmd, str(f))
    assert r.returncode == 0
    assert captured() == "file one content"


def test_copy_multiple_files_concatenates(run_clipped, captured, clip_env):
    one, two = clip_env / "file1.txt", clip_env / "file2.txt"
    one.write_text("file one content")
    two.write_text("file two content")
    r = run_clipped("c", str(one), str(two))
    assert r.returncode == 0
    # Joined with no separator — the clipboard gets exactly the bytes on disk.
    assert captured() == "file one contentfile two content"


def test_copy_nonexistent_file_exits_nonzero(run_clipped):
    r = run_clipped("c", "/nonexistent/file.txt")
    assert r.returncode != 0
    assert "not found" in r.stderr


def test_copy_directory_argument_fails_cleanly(run_clipped, clip_env):
    """No bats equivalent — a directory is the other obvious wrong argument."""
    r = run_clipped("c", str(clip_env))
    assert r.returncode != 0
    assert "not a file" in r.stderr


# ── auto mode ─────────────────────────────────────────────────────────────────

def test_auto_mode_with_piped_stdin_copies(run_clipped, captured):
    r = run_clipped(stdin="auto copied")
    assert r.returncode == 0
    assert captured() == "auto copied"


def test_auto_mode_with_tty_pastes(run_clipped_tty):
    rc, out = run_clipped_tty()
    assert rc == 0
    assert CLIPBOARD_CONTENT in out


# ── error handling ────────────────────────────────────────────────────────────

def test_unknown_command_exits_one_with_usage(run_clipped):
    r = run_clipped("wat")
    assert r.returncode == 1
    assert "Unknown command 'wat'" in r.stderr
    assert "clipped [copy|paste|--help|--version]" in r.stderr


def test_unknown_command_mentions_auto_behaviour(run_clipped):
    r = run_clipped("wat")
    assert r.returncode == 1
    assert "Auto: copy stdin, or paste if no stdin" in r.stderr


# ── binary safety ─────────────────────────────────────────────────────────────

def test_copy_handles_non_utf8_bytes(run_clipped, captured, clip_env):
    """No bats equivalent. The clipboard carries bytes, so decoding on the way
    through would fail on content that should have round-tripped."""
    f = clip_env / "latin1.txt"
    f.write_bytes(b"caf\xe9 latin-1")
    r = run_clipped("c", str(f))
    assert r.returncode == 0
    assert (clip_env / "clipped-copy-capture").read_bytes() == b"caf\xe9 latin-1"
