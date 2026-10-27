"""The sudo guard refuses user-scoped tools; the rest passes.

`dot_functions` is sourced by both shells, so the guard is tested
through zsh here: `sudo` is a shell function, not a binary, and the
only way to prove it captures the call is to run it in a shell that
sourced the file.

Both directions matter. A guard that refuses every sudo looks like one
that works when only the refusal is tested, so the passthrough cases
are as load-bearing as the refusals.
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess

import pytest

FUNCTIONS = pathlib.Path(__file__).resolve().parents[2] / "dot_functions"

pytestmark = pytest.mark.skipif(
    shutil.which("zsh") is None, reason="zsh is not installed"
)


def _source_and_run(script: str, fake_sudo: pathlib.Path | None = None):
    env = None
    if fake_sudo is not None:
        env = {
            **__import__("os").environ,
            "PATH": f"{fake_sudo.parent}:{__import__('os').environ['PATH']}",
        }
    return subprocess.run(
        ["zsh", "-c", f"source {str(FUNCTIONS)!r}; {script}"],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )


@pytest.fixture
def fake_sudo(tmp_path):
    """A stand-in for the real sudo, so passthrough is observable."""
    path = tmp_path / "sudo"
    path.write_text('#!/bin/sh\nprintf "PASSTHROUGH %s\\n" "$*"\n', encoding="utf-8")
    path.chmod(0o755)
    return path


@pytest.mark.parametrize("command", ["mise install", "ansible-playbook site.yml"])
def test_refuses_user_scoped_tools(command):
    result = _source_and_run(f"sudo {command}")
    assert result.returncode == 1
    assert "refusing to run" in result.stderr


def test_refuses_mise_behind_sudo_options():
    result = _source_and_run("sudo -E -u root mise install")
    assert result.returncode == 1
    assert "refusing to run 'mise'" in result.stderr


def test_passes_an_unrelated_command_through(fake_sudo):
    result = _source_and_run("sudo apt install mise", fake_sudo)
    assert result.returncode == 0, result.stderr
    assert "PASSTHROUGH apt install mise" in result.stdout


def test_passes_a_command_that_merely_mentions_mise(fake_sudo):
    result = _source_and_run("sudo systemctl restart mise", fake_sudo)
    assert result.returncode == 0, result.stderr
    assert "PASSTHROUGH systemctl restart mise" in result.stdout


def test_command_sudo_bypasses_on_purpose(fake_sudo):
    result = _source_and_run("command sudo mise install", fake_sudo)
    assert result.returncode == 0, result.stderr
    assert "PASSTHROUGH mise install" in result.stdout
