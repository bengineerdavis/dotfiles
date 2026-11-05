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

import re
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
        if re.match(r"^(TASK|DOT)-", line)
    ]
    assert ids, "task list printed nothing — no evidence"
    assert len(ids) == len(set(ids)), (
        f"duplicate task ids: {sorted(i for i in set(ids) if ids.count(i) > 1)}"
    )


SHADOW_WARNING = "Duplicate task id"


def test_decision_ids_are_unique():
    """Two decision files sharing an id make every citation ambiguous.

    Task ids are guarded above, and `doctor` catches a duplicated task id. No
    equivalent exists for `backlog/decisions/`: nothing scans it, and
    `backlog-py decision create` cannot notice either, because `_next_decision_id`
    takes `max(id) + 1` over ids it can parse — two files both reading
    `decision-1` still yield `decision-2` for the next allocation.

    Measured 2026-11-04: two files declared `id: decision-1`, and five task files
    cite that id in `references:`. A reader following any of those citations
    cannot tell which record it means. `doctor` reported "No problems found".

    The cost of the collision outlives the fix: a `references:` entry names a
    path, but prose that writes "decision-1 §3" keeps pointing at both files
    until it is rewritten.
    """
    decisions = sorted((REPO_ROOT / "backlog" / "decisions").glob("*.md"))
    assert decisions, "no decision files found — the scan is looking in the wrong place"

    ids: dict[str, list[str]] = {}
    for path in decisions:
        front_matter = path.read_text(encoding="utf-8").split("---")[1]
        declared = yaml.safe_load(front_matter).get("id")
        assert declared, f"{path.name} declares no id"
        ids.setdefault(declared, []).append(path.name)

    collisions = {i: names for i, names in ids.items() if len(names) > 1}
    assert not collisions, (
        "Two decision files share an id, so every citation of it is ambiguous.\n"
        + "\n".join(
            f"  {decision_id}:\n" + "\n".join(f"    {n}" for n in names)
            for decision_id, names in sorted(collisions.items())
        )
        + "\nRenumber one file and its `id:` together (`backlog-py decision` has "
        "no renumber command; edit the file and move the id in the same commit)."
    )


def test_no_shadowed_task_ids():
    """A shadowed id is a task file invisible everywhere, and only a warning says so.

    `checkActiveBranches` makes the reader also load task files from other local
    branches. A stale branch holding an older copy of a task therefore competes
    with the on-disk one: both carry the same id, the newer commit wins, and the
    loser is skipped silently apart from this warning. `doctor` never scans branch
    snapshots, so it reports clean while `task` and `board` disagree with it —
    measured 2026-11-02, when a retired branch shadowed DOT-108 for hours.
    """
    for args in (("task", "list", "--plain"), ("board",)):
        result = _run(*args)
        assert result.returncode == 0, result.stderr
        assert SHADOW_WARNING not in result.stderr, (
            f"`{' '.join(args)}` reports a shadowed task id, so one task file is "
            f"invisible everywhere. Find the branch holding the older copy and "
            f"retire it.\n{result.stderr}"
        )
