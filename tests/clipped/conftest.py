"""
Shared fixtures for the clipped suite.

Converted from tests/clipped.bats when clipped moved from bash to Python. Two
things the bats suite could not do are fixed here:

  * It pointed CLIPPED at $BATS_TEST_DIRNAME/../clipped — the repo root, where
    no such file exists. Every test ran against a missing binary, and the one
    that "passed" did so because a nonexistent command also exits nonzero.
  * Its two TTY tests used `script -qec`, which is GNU syntax. BSD script (so
    macOS) has no -c, so those two could never pass here whatever the code did.
    pty.openpty() gives a real terminal on both platforms.

Run:
    pytest tests/clipped -v
"""
from __future__ import annotations

import os
import pathlib
import pty
import subprocess

import pytest

SCRIPT = pathlib.Path.home() / "bin" / "clipped"

CLIPBOARD_CONTENT = "clipboard-content"
CAPTURE_NAME = "clipped-copy-capture"


@pytest.fixture(autouse=True)
def _script_exists():
    if not SCRIPT.exists():
        pytest.skip(f"clipped not found at {SCRIPT} — run: chezmoi apply ~/bin")


@pytest.fixture
def clip_env(tmp_path, monkeypatch):
    """Fake pbcopy/pbpaste on PATH, and return the sandbox directory.

    pbpaste prints a known string; pbcopy captures stdin to a file the tests
    read back. Real clipboard tools are deliberately not used — they would make
    the suite depend on, and clobber, the developer's actual clipboard.
    """
    bindir = tmp_path / "mockbin"
    bindir.mkdir()

    (bindir / "pbpaste").write_text(
        f"#!/usr/bin/env bash\nprintf '%s' \"{CLIPBOARD_CONTENT}\"\n"
    )
    (bindir / "pbcopy").write_text(
        f'#!/usr/bin/env bash\ncat > "{tmp_path}/{CAPTURE_NAME}"\n'
    )
    for tool in ("pbpaste", "pbcopy"):
        (bindir / tool).chmod(0o755)

    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.environ['PATH']}")
    return tmp_path


@pytest.fixture
def captured(clip_env):
    """Read back whatever the fake pbcopy received."""
    def _captured() -> str:
        path = clip_env / CAPTURE_NAME
        return path.read_text() if path.exists() else ""
    return _captured


@pytest.fixture
def run_clipped(clip_env):
    """Run clipped with stdin piped (or closed), stdout and stderr merged."""
    def _run(*args: str, stdin: str | None = None):
        return subprocess.run(
            [str(SCRIPT), *args],
            input=stdin if stdin is not None else "",
            capture_output=True,
            text=True,
            timeout=60,
            env=os.environ.copy(),
        )
    return _run


@pytest.fixture
def run_clipped_tty(clip_env):
    """Run clipped with a real TTY on stdin — the auto-mode and guidance paths.

    Returns (returncode, combined_output). A pty is the portable way to make
    isatty() true; the bats suite's `script -qec` only works on GNU coreutils.
    """
    def _run(*args: str) -> tuple[int, str]:
        controller, follower = pty.openpty()
        proc = subprocess.Popen(
            [str(SCRIPT), *args],
            stdin=follower,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=os.environ.copy(),
        )
        os.close(follower)
        try:
            out = proc.stdout.read()
            proc.wait(timeout=60)
        finally:
            os.close(controller)
        return proc.returncode, out.decode(errors="replace")
    return _run
