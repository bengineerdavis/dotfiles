"""
CLI behaviour for pii-redactor — the bats suite's cases, ported to pytest.

Covers argument parsing, the optional-argument -o and its templating, the
staging-file write path, and what actually reaches `llm` in argv and the
environment.
"""
from __future__ import annotations

import os
import stat

import pytest


# ── help and argument errors ──────────────────────────────────────────────────

@pytest.mark.parametrize("flag", ["--help", "-h"])
def test_help_prints_usage_and_exits_zero(run_script, flag):
    r = run_script(flag)
    assert r.returncode == 0
    assert "Usage:" in r.stdout
    assert "--input" in r.stdout


def test_unknown_flag_exits_nonzero_with_message(run_script):
    r = run_script("--bogus-flag")
    assert r.returncode != 0
    assert "Unknown option" in r.stderr


@pytest.mark.parametrize("flag", ["--input", "--model"])
def test_flag_missing_argument_exits_nonzero(run_script, flag):
    r = run_script(flag)
    assert r.returncode != 0
    assert "requires an argument" in r.stderr


def test_missing_input_file_exits_nonzero(run_script):
    r = run_script("-i", "/nonexistent/path/file.txt")
    assert r.returncode != 0
    assert "not found" in r.stderr


# ── dry run and verbosity ─────────────────────────────────────────────────────

def test_dry_run_with_input_file(run_script, tmp_path):
    src = tmp_path / "in.md"
    src.write_text("Hello John Doe\n")
    r = run_script("--dry-run", "-i", str(src))
    assert r.returncode == 0
    assert "Would process" in r.stderr


def test_dry_run_stdin(run_script):
    r = run_script("--dry-run", stdin="test\n")
    assert r.returncode == 0
    assert "Would process stdin" in r.stderr


def test_verbose_emits_debug_output(run_script, tmp_path):
    src = tmp_path / "in.md"
    src.write_text("content\n")
    r = run_script("-v", "--dry-run", "-i", str(src))
    assert r.returncode == 0
    assert "Processing file" in r.stderr


# ── what reaches llm ──────────────────────────────────────────────────────────

def test_passes_model_through_to_llm(mock_llm, run_script, tmp_path):
    mock_llm('echo "ARGS: $*"')
    src = tmp_path / "in.md"
    src.write_text("hello\n")
    r = run_script("-i", str(src), "-m", "my-custom-model")
    assert r.returncode == 0
    assert "my-custom-model" in r.stdout


def test_uses_system_flag_not_prompt_flag(mock_llm, run_script, tmp_path):
    mock_llm('echo "ARGS: $*"')
    src = tmp_path / "in.md"
    src.write_text("hello\n")
    r = run_script("-i", str(src))
    assert r.returncode == 0
    assert " -s " in r.stdout
    assert " -p " not in r.stdout


def test_passes_no_log_flag(mock_llm, run_script, tmp_path):
    mock_llm('echo "ARGS: $*"')
    src = tmp_path / "in.md"
    src.write_text("hello\n")
    r = run_script("-i", str(src))
    assert r.returncode == 0
    assert " -n" in r.stdout


def test_llm_extra_opts_is_word_split_and_forwarded(mock_llm, run_script, tmp_path):
    mock_llm('echo "ARGS: $*"')
    src = tmp_path / "in.md"
    src.write_text("hello\n")
    env = {**os.environ, "LLM_EXTRA_OPTS": "-o think false"}
    r = run_script("-i", str(src), env=env)
    assert r.returncode == 0
    # Word-split, not passed as one argument — "-o think false" must arrive as three.
    assert "-o think false" in r.stdout


def test_pymupdf_message_is_set_for_the_child(mock_llm, run_script, tmp_path):
    """PyMuPDF defaults its messages to stdout, which would corrupt the output."""
    mock_llm('echo "PYMUPDF_MESSAGE=${PYMUPDF_MESSAGE:-unset}"')
    src = tmp_path / "in.md"
    src.write_text("hello\n")
    r = run_script("-i", str(src))
    assert r.returncode == 0
    assert "PYMUPDF_MESSAGE=fd:2" in r.stdout


# ── output routing ────────────────────────────────────────────────────────────

def test_stdin_is_processed_without_input_flag(mock_llm, run_script):
    r = run_script(stdin="my name is Alice\n")
    assert r.returncode == 0


def test_output_written_to_named_file(mock_llm, run_script, tmp_path):
    src, dst = tmp_path / "in.md", tmp_path / "out.md"
    src.write_text("Hello World\n")
    r = run_script("-i", str(src), "-o", str(dst))
    assert r.returncode == 0
    assert dst.exists() and dst.stat().st_size > 0


def test_bare_o_templates_off_the_input(mock_llm, run_script, tmp_path):
    src = tmp_path / "mail.md"
    src.write_text("Hello World\n")
    r = run_script("-i", str(src), "-o")
    assert r.returncode == 0
    assert (tmp_path / "mail-pii-removed.md").stat().st_size > 0


def test_bare_o_templates_when_it_precedes_input(mock_llm, run_script, tmp_path):
    src = tmp_path / "mail.md"
    src.write_text("Hello World\n")
    r = run_script("-o", "-i", str(src))
    assert r.returncode == 0
    assert (tmp_path / "mail-pii-removed.md").stat().st_size > 0


def test_bare_o_on_extensionless_input_appends_suffix(mock_llm, run_script, tmp_path):
    src = tmp_path / "mail"
    src.write_text("Hello World\n")
    r = run_script("-i", str(src), "-o")
    assert r.returncode == 0
    assert (tmp_path / "mail-pii-removed").stat().st_size > 0


def test_bare_o_with_stdin_uses_fixed_name(mock_llm, run_script, tmp_path):
    r = run_script("-o", stdin="Hello World\n", cwd=tmp_path)
    assert r.returncode == 0
    assert (tmp_path / "stdin-pii-removed.md").stat().st_size > 0


def test_explicit_output_beats_the_template(mock_llm, run_script, tmp_path):
    src, dst = tmp_path / "mail.md", tmp_path / "custom.md"
    src.write_text("Hello World\n")
    r = run_script("-i", str(src), "-o", str(dst))
    assert r.returncode == 0
    assert dst.stat().st_size > 0
    assert not (tmp_path / "mail-pii-removed.md").exists()


# ── failure handling ──────────────────────────────────────────────────────────

def test_failing_llm_leaves_no_output_or_staging_file(mock_llm, run_script, tmp_path):
    mock_llm('echo "partial output"\nexit 1')
    src, dst = tmp_path / "mail.md", tmp_path / "out.md"
    src.write_text("Hello World\n")
    r = run_script("-i", str(src), "-o", str(dst))
    assert r.returncode != 0
    assert not dst.exists()
    # The staging file is a sibling named out.md.XXXXXX — none may survive.
    assert not list(tmp_path.glob("out.md.*"))


def test_failing_llm_does_not_clobber_existing_output(mock_llm, run_script, tmp_path):
    mock_llm("exit 1")
    src, dst = tmp_path / "mail.md", tmp_path / "out.md"
    src.write_text("Hello World\n")
    dst.write_text("PREVIOUS GOOD OUTPUT")
    r = run_script("-i", str(src), "-o", str(dst))
    assert r.returncode != 0
    assert dst.read_text() == "PREVIOUS GOOD OUTPUT"


def test_output_honours_umask_not_mktemp_0600(mock_llm, run_script, tmp_path):
    """mkstemp creates 0600; a redirect used to honour the umask. Sharing the
    redacted file is the whole point, so the umask must win."""
    src, dst = tmp_path / "mail.md", tmp_path / "out.md"
    src.write_text("Hello World\n")

    old = os.umask(0o022)
    try:
        r = run_script("-i", str(src), "-o", str(dst))
    finally:
        os.umask(old)

    assert r.returncode == 0
    assert stat.S_IMODE(dst.stat().st_mode) == 0o644
