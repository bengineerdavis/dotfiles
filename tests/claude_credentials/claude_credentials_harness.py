"""The zsh invocation seam for Claude profile tests."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FRAGMENT = REPO / "home/dotfiles/apps/claude-code/files/zsh/claude.zsh"


def invoke(environment, wrapper, *args):
    """Source the fragment and execute a wrapper through a real zsh."""
    zsh = shutil.which("zsh", path=environment.get("PATH") or "")
    if zsh is None:
        raise RuntimeError("zsh is required for the real-shell profile tests")

    return subprocess.run(
        [
            zsh,
            "-f",
            "-c",
            f'source "$1"; {wrapper} "${{@:2}}"',
            "claude-profile-test",
            str(FRAGMENT),
            *args,
        ],
        env=environment,
        capture_output=True,
        text=True,
        timeout=10,
    )
