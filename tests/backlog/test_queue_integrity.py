"""Queue integrity: the backlog/ directory must always be machine-readable.

Replaces tests/tasks_doc, which enforced TASKS.md conventions. The failure
this exists to catch is the same class: the queue passing review while being
structurally broken — a task file no command can read, a duplicated id
(which shadows one task silently, core/repository.py), or a config that no
longer parses.

backlog-py is probed for viability, not presence: a mise shim can exist with
no version installed ("No version is set for shim"), which errors exactly
like a working probe until run. The probe falls back to uvx, which resolves
the pinned package from the uv cache or the network.
"""

import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def _backlog_cmd() -> list[str]:
    exe = shutil.which("backlog-py")
    if exe:
        probe = subprocess.run([exe, "--version"], capture_output=True)
        if probe.returncode == 0:
            return [exe]
    uvx = shutil.which("uvx")
    if uvx:
        return [uvx, "--from", "backlog-md-py", "backlog-py"]
    pytest.fail(
        "backlog-py unavailable: no working binary on PATH and no uvx. "
        "Fix: apply apps/backlog (mise installs pipx:backlog-md-py)."
    )


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [*_backlog_cmd(), "--cwd", str(REPO_ROOT), *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_backlog_directory_exists():
    assert (REPO_ROOT / "backlog" / "config.yml").is_file()


def test_config_parses_with_expected_defaults():
    config = yaml.safe_load((REPO_ROOT / "backlog" / "config.yml").read_text())
    assert config["projectName"]
    # House decisions (docs/BACKLOG-MIGRATION.md): the tool never commits and
    # never reaches the network on its own.
    assert config["autoCommit"] is False
    assert config["remoteOperations"] is False


def test_doctor_reports_no_problems():
    result = _run("doctor")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip(), "doctor printed nothing — no evidence"
    assert "No problems found" in result.stdout, result.stdout


def test_board_renders_every_task_once():
    """No duplicate ids: a shadowed task is one nobody can see."""
    result = _run("task", "list", "--plain")
    assert result.returncode == 0, result.stderr
    ids = [
        line.split()[0]
        for line in result.stdout.splitlines()
        if line.startswith("TASK-")
    ]
    assert ids, "task list printed nothing — no evidence"
    assert len(ids) == len(set(ids)), (
        f"duplicate task ids: {sorted(i for i in set(ids) if ids.count(i) > 1)}"
    )
