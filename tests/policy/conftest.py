"""
Shared fixtures for the policy resolver suite.

Runs the script as a subprocess, black-box, because that is the contract callers
actually depend on: `policy check <key>` and its exit status. The three layers
are redirected with $ZSH and $XDG_STATE_HOME, so no test reads or writes the
author's real policy files.

Tests target the chezmoi **source** (`bin/executable_policy`) rather than the
deployed `~/bin/policy`. The rest of the suite tests the deployed copy, which is
right for scripts whose behaviour depends on being installed — but this one is
pure file-reading, and testing the source means the suite passes on a checkout
that has never been applied, and fails on a bad commit rather than on stale
deployment.

Run:
    pytest tests/policy -v
"""

from __future__ import annotations

import pathlib
import subprocess
import textwrap

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "bin" / "executable_policy"

# Exit codes, mirrored from the script so a silent change to either shows up
# as a failing test rather than as a test that quietly asserts nothing.
PERMITTED, DENIED, UNKNOWN, ERROR = 0, 1, 2, 3


@pytest.fixture
def policy_env(tmp_path):
    """Build a fake three-layer environment and return a runner.

    Each layer is written only if given, so a test can omit one to exercise the
    absent-file path. Content is dedented, so tests can indent YAML naturally.
    """
    zsh = tmp_path / "dotfiles"
    state = tmp_path / "state"
    (zsh / "policy").mkdir(parents=True)
    (state / "ai-policy").mkdir(parents=True)

    def build(ethics: str | None = None, company: str | None = None,
              personal: str | None = None):
        for text, path in (
            (ethics, zsh / "policy" / "ethics.yaml"),
            (company, state / "ai-policy" / "company.yaml"),
            (personal, zsh / "policy" / "personal.yaml"),
        ):
            if text is not None:
                path.write_text(textwrap.dedent(text).lstrip("\n"))

        def run(*args: str) -> subprocess.CompletedProcess:
            return subprocess.run(
                [str(SCRIPT), *args],
                capture_output=True,
                text=True,
                env={
                    "ZSH": str(zsh),
                    "XDG_STATE_HOME": str(state),
                    "PATH": _path_with_uv(),
                    "HOME": str(tmp_path),
                },
            )

        return run

    return build


def _path_with_uv() -> str:
    """uv runs the PEP 723 shebang, so it must stay on PATH in the stripped env."""
    import os
    import shutil

    uv = shutil.which("uv")
    extra = str(pathlib.Path(uv).parent) if uv else ""
    return os.pathsep.join(p for p in (extra, "/usr/bin", "/bin") if p)
