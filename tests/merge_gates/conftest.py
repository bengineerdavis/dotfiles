"""Fixtures for the merge-gate checker tests.

Module loader, git sandbox, fake chezmoi.
"""

from __future__ import annotations

import importlib.util
import os
import pathlib
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "check_merge_gates.py"


@pytest.fixture(scope="session")
def m():
    spec = importlib.util.spec_from_file_location("merge_gates", SCRIPT)
    # pyrefly: ignore [bad-argument-type]
    mod = importlib.util.module_from_spec(spec)
    # pyrefly: ignore [missing-attribute]
    spec.loader.exec_module(mod)
    return mod


def _git(repo: pathlib.Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def git_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    """A git repo with one commit on main, on branch side."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "base.txt").write_text("base\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    _git(repo, "checkout", "-q", "-b", "side")
    return repo


@pytest.fixture
def fake_chezmoi(tmp_path: pathlib.Path):
    """A fake `chezmoi` whose `managed` prints configured paths."""

    def make(paths: list[str], fail: bool = False) -> str:
        bindir = tmp_path / f"fakebin{len(paths)}{fail}"
        bindir.mkdir(exist_ok=True)
        body = "#!/bin/sh\n"
        if fail:
            body += "echo 'boom' >&2\nexit 1\n"
        else:
            body += "".join(f"echo '{p}'\n" for p in paths)
        (bindir / "chezmoi").write_text(body)
        (bindir / "chezmoi").chmod(0o755)
        return str(bindir)

    return make


@pytest.fixture
def env_with(monkeypatch: pytest.MonkeyPatch):
    """Return a callable setting PATH (and other vars) for a run."""

    def _apply(extra_bin: str | None) -> dict[str, str]:
        env = dict(os.environ)
        if extra_bin:
            env["PATH"] = extra_bin + os.pathsep + env["PATH"]
        return env

    return _apply


def run_script(
    repo: pathlib.Path,
    env: dict[str, str],
    *args: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT), "--repo", str(repo), *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(repo),
    )
