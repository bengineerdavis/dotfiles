"""The daemonizing-backend regression: a copy backend that forks and holds
inherited descriptors open must not hang clipped's caller.

Bought by DOT-73 on 2026-11-01: real xclip forks a daemon to serve the X
selection, and the child keeps every inherited stdout/stderr open. When a
caller captures clipped's output (pytest, a CI pipe) it never sees EOF and
blocks until its timeout. The fix sends the copy backend's stdout to DEVNULL
and its stderr to a temp file — a pipe on either would reintroduce the hang,
since the daemon holds the write-end open — so no inherited pipe is left for
the daemon to hold and a failing backend's diagnostic still reaches the user.
"""

from __future__ import annotations

import pathlib
import subprocess

import pytest

# pyrefly: ignore [missing-import]
from clipped_harness import CLIPBOARD_CONTENT  # noqa: F401 — same fake-clipboard content the CLI suite asserts

SOURCE = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "home"
    / "bin"
    / "executable_clipped"
)


def _skip_if_source_missing():
    """The regression runs the REPO source copy, not the deployed ~/bin one.

    The CLI suite tests the deployed binary as a black box; this regression is
    about the fix itself, so it targets home/bin/executable_clipped directly
    and needs no apply to be meaningful. Deployed-vs-source drift is chezmoi
    status's job, not this test's.
    """
    if not SOURCE.exists():
        pytest.skip(f"clipped source not found at {SOURCE}")


def test_copy_survives_a_daemonizing_backend(clip_env):
    """A backend that forks and sleeps still holds no pipe clipped's caller
    waits on: the copy completes instead of hanging to its timeout.
    """
    _skip_if_source_missing()

    # clip_env installed well-behaved fakes. Replace the copy fakes with
    # hostile ones that mimic real xclip's fork-to-background behaviour: the
    # parent does its work and exits, while a forked child lingers holding
    # the inherited stdout/stderr open. Without the DEVNULL fix, that lingering
    # child keeps the caller's capture pipes open past any timeout. Both first
    # candidates (xclip on Linux, pbcopy on Darwin) go hostile, so whichever
    # table the host platform picks, the daemonizing backend is chosen.
    for tool in ("xclip", "pbcopy"):
        hostile = clip_env / "mockbin" / tool
        hostile.write_text(
            "#!/usr/bin/env bash\n"
            "sleep 30 &\n"  # forked child: holds inherited fds, like xclip's daemon
            f'cat > "{clip_env}/daemon-capture"\n'  # parent works and exits
        )
        hostile.chmod(0o755)

    try:
        result = subprocess.run(
            [str(SOURCE), "copy"],
            input="hello clipboard",
            capture_output=True,
            text=True,
            timeout=20,
        )
    except subprocess.TimeoutExpired:
        pytest.fail(
            "clipped copy hung on a daemonizing backend: the copy subprocess "
            "still inherits stdout/stderr, so the forked child holds the "
            "caller's pipes open (DOT-73)"
        )
    assert result.returncode == 0
    captured = (clip_env / "daemon-capture").read_text()
    assert captured == "hello clipboard"


def test_copy_failure_keeps_the_backend_diagnostic(clip_env):
    """A failing backend's own stderr text reaches the user: it goes to a
    temp file, not DEVNULL, and rides along in the die() message.
    """
    _skip_if_source_missing()

    # A copy backend that fails with a diagnostic on stderr, the shape a
    # user actually hits when the backend is broken (xclip with no display).
    # Both first candidates go hostile — xclip on Linux, pbcopy on Darwin —
    # so whichever table the host platform picks, the failing backend is
    # chosen. Replacing only xclip lets a Darwin host fall through to the
    # well-behaved pbcopy fake, where the copy succeeds and the
    # nonzero-returncode assertion below fails for the wrong reason.
    for tool in ("xclip", "pbcopy"):
        hostile = clip_env / "mockbin" / tool
        hostile.write_text(
            "#!/usr/bin/env bash\n"
            f"echo '{tool}: cannot open display (fake)' >&2\n"
            "exit 1\n"
        )
        hostile.chmod(0o755)

    result = subprocess.run(
        [str(SOURCE), "copy"],
        input="hello clipboard",
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode != 0
    # Backend name in the diagnostic varies by platform (xclip on Linux,
    # pbcopy on Darwin); the message body is what both fakes share.
    assert "cannot open display (fake)" in result.stderr
