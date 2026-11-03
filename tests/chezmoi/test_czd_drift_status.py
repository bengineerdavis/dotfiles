"""czd — chezmoi drift as text, and as an exit status.

The behaviour worth pinning is the exit status, not the diff text. `chezmoi
diff` exits 0 whether or not targets differ, and on this machine it is bound to
meld, which prints nothing to stdout. An agent reading that as "clean" is the
bug this script exists to remove, so each status is asserted separately:

  0  no drift
  1  drift
  2  chezmoi unavailable, or the target is not managed

The wrapper is exercised against a stand-in `chezmoi` on PATH rather than the
real binary. That keeps the contract explicit — "whatever chezmoi prints is the
diff, and its exit status is not a drift signal" — and stops the test from
depending on how far the author's machine currently drifts.
"""

from __future__ import annotations

import os
import stat
import subprocess
import textwrap
from pathlib import Path

import pytest

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

CZ_SCRIPT = PAYLOAD_ROOT / "bin" / "executable_czd"


def _fake_chezmoi(tmp_path: Path, *, stdout: str, stderr: str, rc: int) -> Path:
    """A `chezmoi` that answers every subcommand the same way."""
    bindir = tmp_path / "fakebin"
    bindir.mkdir(exist_ok=True)
    fake = bindir / "chezmoi"
    fake.write_text(
        textwrap.dedent(
            f"""\
            #!/usr/bin/env bash
            printf '%b' {stdout!r}
            printf '%b' {stderr!r} >&2
            exit {rc}
            """
        )
    )
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    return bindir


def _run(tmp_path: Path, bindir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(CZ_SCRIPT), *args],
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": f"{bindir}:{os.environ['PATH']}"},
    )


def test_drift_is_reported_and_exits_one(tmp_path: Path):
    bindir = _fake_chezmoi(
        tmp_path, stdout="--- a\n+++ b\n-old\n+new\n", stderr="", rc=0
    )
    result = _run(tmp_path, bindir, "~/.somefile")

    assert result.returncode == 1
    assert "+new" in result.stdout


def test_no_output_is_clean_and_exits_zero(tmp_path: Path):
    bindir = _fake_chezmoi(tmp_path, stdout="", stderr="", rc=0)
    result = _run(tmp_path, bindir)

    assert result.returncode == 0
    assert result.stdout == ""


def test_a_chezmoi_failure_is_an_error_not_drift(tmp_path: Path):
    bindir = _fake_chezmoi(tmp_path, stdout="", stderr="chezmoi: not managed\n", rc=1)
    result = _run(tmp_path, bindir, "~/.not-managed")

    # 2, not 1. Reporting an error as drift sends a caller looking for a
    # difference that does not exist — and 1 is what a drift checker says
    # when it found something real.
    assert result.returncode == 2
    assert "not managed" in result.stderr
    assert result.stdout == ""


def test_stderr_never_leaks_into_the_diff(tmp_path: Path):
    """A warning on stderr must not become a phantom hunk on stdout."""
    bindir = _fake_chezmoi(tmp_path, stdout="", stderr="warning: something\n", rc=0)
    result = _run(tmp_path, bindir)

    assert result.returncode == 0
    assert "warning" not in result.stdout


def test_missing_chezmoi_names_the_fix(tmp_path: Path):
    empty = tmp_path / "emptybin"
    empty.mkdir()
    result = subprocess.run(
        ["bash", str(CZ_SCRIPT)],
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
    )
    if result.returncode == 0:
        pytest.skip("a real chezmoi is on the reduced PATH")

    assert result.returncode == 2
    assert "chezmoi is not on PATH" in result.stderr
    # The error names the remedy, not just the failure.
    assert "update.sh" in result.stderr


def test_stat_mode_lists_drifted_targets_only(tmp_path: Path):
    bindir = _fake_chezmoi(
        tmp_path,
        stdout=" M .config/opencode/opencode.jsonc\n  .zshrc\n",
        stderr="",
        rc=0,
    )
    result = _run(tmp_path, bindir, "--stat")

    assert result.returncode == 1
    assert "opencode.jsonc" in result.stdout
    # The second column is blank, so .zshrc has no pending change.
    assert ".zshrc" not in result.stdout
