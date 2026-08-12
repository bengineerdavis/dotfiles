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

import json
import os
import subprocess
import pathlib

import pytest

BINNED = pathlib.Path.home() / "bin" / "binned"


def _run(args: list[str], *, env_extra: dict | None = None, input_text: str | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [str(BINNED), *args],
        capture_output=True, text=True, timeout=30,
        input=input_text, env=env,
    )


@pytest.fixture(autouse=True)
def _tmp_binned_home(tmp_path, monkeypatch):
    """Isolate each test's binned state in its own temp dir."""
    monkeypatch.setenv("BINNED_HOME", str(tmp_path))
    return tmp_path


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
    assert "binned" in result.stdout.lower(), f"expected 'binned' in version output, got: {result.stdout!r}"


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


# ── Cases carried over from tests/binned.bats ─────────────────────────────────
# The bats suite covered these four and the pytest suite did not. Ported here so
# binned.bats can be retired; everything else it asserted was already covered,
# usually more thoroughly (its single _sanitize_name case is five property tests
# in test_binned_property.py).

def test_help_flag_exits_zero():
    """--help is distinct from the no-args path and must also succeed."""
    result = _run(["--help"])
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}\n{result.stderr}"
    combined = result.stdout + result.stderr
    assert "binned" in combined.lower()


def test_pending_with_no_deferred_scripts_reports_empty():
    """BINNED_HOME is a fresh tmp dir, so nothing is deferred yet."""
    result = _run(["pending"])
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}\n{result.stderr}"
    combined = (result.stdout + result.stderr).lower()
    # Must say there is nothing rather than printing a bare empty listing.
    assert any(word in combined for word in ("no ", "empty", "nothing")), combined[:300]


def test_resume_with_unknown_name_exits_nonzero():
    result = _run(["resume", "definitely-not-a-real-deferred-script"])
    assert result.returncode != 0, (
        "resuming a script that was never deferred should fail, "
        f"got exit 0\n{result.stdout[:300]}"
    )


def test_list_pending_returns_deferred_scripts(_tmp_binned_home):
    """Round-trip through the real on-disk layout: save one, then list it."""
    pending = _tmp_binned_home / "pending"
    pending.mkdir(parents=True, exist_ok=True)
    # Schema must match save_pending() exactly — list_pending() parses each file
    # and silently drops anything that fails, so a drifted fixture would make
    # this pass or fail for the wrong reason.
    (pending / "my-deferred-script.json").write_text(json.dumps({
        "name": "my-deferred-script",
        "cmd": "echo deferred-marker",
        "script": "#!/usr/bin/env bash\necho hi\n",
        "test_files": {},
        "saved_at": "2026-08-12T09:00:00",
    }))
    result = _run(["pending"])
    assert result.returncode == 0, result.stderr
    combined = result.stdout + result.stderr
    assert "my-deferred-script" in combined, combined[:300]
    # The rendered date comes from saved_at, so its presence proves the file was
    # parsed rather than the directory merely globbed for names.
    assert "2026-08-12" in combined, combined[:300]
