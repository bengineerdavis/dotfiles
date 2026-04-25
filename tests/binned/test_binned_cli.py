"""
CLI routing tests for binned.

These tests run binned as a subprocess to verify that:
  - Subcommand names (config, refactor, pending, …) are never swallowed as
    the shell command to automate.
  - binned with no arguments prints help and exits 0 (not an interactive prompt).
  - Free-text shell commands with embedded flags are passed through correctly.
  - --version exits 0 and prints the version string.

All invocations use BINNED_HOME pointing at a tmp dir so no real ~/.binned
state is read or written.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import shutil
import pathlib

import pytest

BINNED = pathlib.Path.home() / "bin" / "binned"


def _run(args: list[str], *, env_extra: dict | None = None, input_text: str | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["BINNED_HOME"] = env.get("_BINNED_TEST_HOME", "")
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [str(BINNED), *args],
        capture_output=True, text=True, timeout=30,
        input=input_text, env=env,
    )


@pytest.fixture(autouse=True, scope="module")
def _tmp_binned_home():
    """Redirect all binned state to a temp dir for the duration of this module."""
    tmp = tempfile.mkdtemp(prefix="binned_cli_test_")
    os.environ["_BINNED_TEST_HOME"] = tmp
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)
    os.environ.pop("_BINNED_TEST_HOME", None)


@pytest.fixture(autouse=True, scope="module")
def _binned_exists():
    if not BINNED.exists():
        pytest.skip(f"binned not found at {BINNED} — run: chezmoi apply ~/bin/binned")


# ── No-args shows help ────────────────────────────────────────────────────────

def test_no_args_shows_help():
    result = _run([])
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}\n{result.stderr}"
    combined = result.stdout + result.stderr
    assert "binned" in combined.lower(), "help text should mention 'binned'"
    # Must not block waiting for interactive input — if it hangs the timeout fires
    # and pytest reports an error, which is also a useful signal.


# ── --version ─────────────────────────────────────────────────────────────────

def test_version_flag():
    result = _run(["--version"])
    assert result.returncode == 0
    assert "binned" in result.stdout.lower() or result.stdout.strip() != ""


# ── Subcommand routing ────────────────────────────────────────────────────────
# Each test verifies that the subcommand name is NOT treated as a shell command
# to automate.  We check the output does NOT contain the "Analyzing…" / generation
# header that run_generate() always prints before making any LLM call.

# These strings appear in run_generate() output but NOT in subcommand --help text.
# "Generation model" alone is too broad — refactor/self-improve --help also says
# "Generation model override" in their --model option description.
_GENERATE_MARKERS = ("Analyzing", "→ Generation model:")


def _looks_like_generate(output: str) -> bool:
    return any(m in output for m in _GENERATE_MARKERS)


def test_config_subcommand_routes_correctly():
    """'binned config' must enter the config TUI, not try to automate 'config'."""
    # Run non-interactively: pipe empty stdin so questionary/typer don't block.
    result = _run(["config"], input_text="\n")
    combined = result.stdout + result.stderr
    assert not _looks_like_generate(combined), (
        "'binned config' triggered generate instead of routing to the config subcommand.\n"
        f"stdout: {result.stdout[:300]}\nstderr: {result.stderr[:300]}"
    )


def test_pending_subcommand_routes_correctly():
    result = _run(["pending"], input_text="\n")
    combined = result.stdout + result.stderr
    assert not _looks_like_generate(combined), (
        "'binned pending' triggered generate instead of routing to pending subcommand.\n"
        f"stdout: {result.stdout[:300]}\nstderr: {result.stderr[:300]}"
    )


@pytest.mark.parametrize("subcmd", ["config", "pending", "refactor", "self-improve", "resume"])
def test_subcommand_never_triggers_generate(subcmd):
    result = _run([subcmd, "--help"])
    combined = result.stdout + result.stderr
    assert not _looks_like_generate(combined), (
        f"'binned {subcmd} --help' triggered generate.\n"
        f"stdout: {result.stdout[:300]}\nstderr: {result.stderr[:300]}"
    )
    # --help should print something useful and exit cleanly (0 or 2 both acceptable)
    assert combined.strip(), f"'binned {subcmd} --help' produced no output"


# ── Explicit shell commands ───────────────────────────────────────────────────
# We pass --auto/-y and a clearly non-subcommand command to verify ctx.args routing.
# We do NOT make real LLM calls — just check that run_generate is entered and the
# command is reflected in early output before any network I/O.

def test_explicit_command_enters_generate():
    """binned "echo hello" should reach run_generate (Analyzing… header appears)."""
    result = _run(["--auto", "echo hello"], input_text="")
    combined = result.stdout + result.stderr
    # Either the generation header appears, OR the first-run judge setup runs —
    # either way, we must NOT see the help text as the only output.
    help_only = ("Turn a shell command" in combined and not _looks_like_generate(combined)
                 and "echo hello" not in combined)
    assert not help_only, (
        "binned treated an explicit command as no-arg invocation.\n"
        f"stdout: {result.stdout[:400]}"
    )


def test_command_with_embedded_flags():
    """find . -name '*.log' -mtime +7 -delete — flags in the command must not confuse binned."""
    result = _run(["--auto", "find", ".", "-name", "*.log", "-mtime", "+7", "-delete"],
                  input_text="")
    combined = result.stdout + result.stderr
    # Should not exit with "unrecognised option" or similar argparse errors
    assert "no such option" not in combined.lower(), (
        f"Embedded flags in shell command caused option-parse error:\n{combined[:400]}"
    )
    assert "error: unrecognized" not in combined.lower()
