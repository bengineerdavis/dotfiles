import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[2] / "scripts" / "sync-task-base.py"


def git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(cwd), *args], text=True, stderr=subprocess.DEVNULL
    ).strip()


def commit(cwd: Path, name: str) -> str:
    (cwd / "tracked.txt").write_text(name)
    git(cwd, "add", "tracked.txt")
    git(
        cwd,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@local",
        "commit",
        "-m",
        name,
    )
    return git(cwd, "rev-parse", "HEAD")


def run_helper(
    cwd: Path, *, base: str = "main", target: str = "feature"
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("MISE_CONFIG_FILE", None)
    env.update(
        GIT_AUTHOR_NAME="Fixture",
        GIT_AUTHOR_EMAIL="fixture@local",
        GIT_COMMITTER_NAME="Fixture",
        GIT_COMMITTER_EMAIL="fixture@local",
    )
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--target", target],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.fixture
def main_clone(tmp_path: Path) -> Path:
    remote = tmp_path / "remote.git"
    subprocess.run(
        ["git", "init", "--bare", str(remote)], check=True, capture_output=True
    )
    seed = tmp_path / "seed"
    subprocess.run(
        ["git", "init", "-b", "main", str(seed)], check=True, capture_output=True
    )
    commit(seed, "base")
    git(seed, "remote", "add", "origin", str(remote))
    git(seed, "push", "-u", "origin", "main")
    subprocess.run(
        ["git", "-C", str(remote), "symbolic-ref", "HEAD", "refs/heads/main"],
        check=True,
    )

    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "clone", str(remote), str(clone)], check=True, capture_output=True
    )
    commit(seed, "remote change")
    git(seed, "push", "origin", "main")
    assert git(clone, "rev-parse", "HEAD") != git(seed, "rev-parse", "HEAD")
    return clone


def test_new_task_fast_forwards_clean_main(main_clone: Path) -> None:
    before = git(main_clone, "rev-parse", "HEAD")
    result = run_helper(main_clone)
    after = git(main_clone, "rev-parse", "HEAD")

    assert result.returncode == 0, result.stderr
    assert after != before
    assert after == git(main_clone, "rev-parse", "origin/main")
    assert "synchronized" in result.stdout
    assert git(main_clone, "status", "--porcelain") == ""
    assert (
        subprocess.run(
            [
                "git",
                "-C",
                str(main_clone),
                "show-ref",
                "--verify",
                "--quiet",
                "refs/heads/feature",
            ],
            check=False,
        ).returncode
        != 0
    ), "the helper must not create the task branch itself"


def test_diverged_main_is_not_rewritten(main_clone: Path) -> None:
    commit(main_clone, "local change")
    before = git(main_clone, "rev-parse", "HEAD")

    result = run_helper(main_clone)

    assert result.returncode != 0
    assert git(main_clone, "rev-parse", "HEAD") == before


def test_dirty_main_blocks_creation_before_fast_forward(main_clone: Path) -> None:
    before = git(main_clone, "rev-parse", "HEAD")
    (main_clone / "tracked.txt").write_text("uncommitted")

    result = run_helper(main_clone)

    assert result.returncode != 0
    assert "dirty" in result.stderr
    assert git(main_clone, "rev-parse", "HEAD") == before
    assert (main_clone / "tracked.txt").read_text() == "uncommitted"


def test_existing_branch_does_not_require_touching_main(main_clone: Path) -> None:
    git(main_clone, "branch", "feature")
    before = git(main_clone, "rev-parse", "HEAD")

    result = run_helper(main_clone)

    assert result.returncode == 0
    assert "existing" in result.stdout
    assert git(main_clone, "rev-parse", "HEAD") == before


def test_stacked_branch_syncs_main_without_resetting_its_parent(
    main_clone: Path,
) -> None:
    git(main_clone, "branch", "parent-feature")
    before = git(main_clone, "rev-parse", "HEAD")
    parent = git(main_clone, "rev-parse", "parent-feature")

    result = run_helper(main_clone, base="parent-feature")

    assert result.returncode == 0
    assert git(main_clone, "rev-parse", "HEAD") != before
    assert git(main_clone, "rev-parse", "HEAD") == git(
        main_clone, "rev-parse", "origin/main"
    )
    assert git(main_clone, "rev-parse", "parent-feature") == parent


def test_worktrunk_new_worktree_starts_from_fetched_main(main_clone: Path) -> None:
    wt = shutil.which("wt")
    if not wt:
        pytest.skip("worktrunk not installed")
    scripts = main_clone / "scripts"
    scripts.mkdir()
    shutil.copy2(SCRIPT, scripts / SCRIPT.name)
    config = main_clone / ".config"
    config.mkdir()
    (config / "wt.toml").write_text(
        'pre-switch = "python3 scripts/sync-task-base.py '
        '--default-branch {{ default_branch }} --target {{ branch }}"\n'
    )
    git(main_clone, "add", ".")
    git(
        main_clone,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@local",
        "commit",
        "-m",
        "hook",
    )
    git(main_clone, "reset", "--hard", "origin/main")
    user_config = main_clone.parent / "worktrunk.toml"
    user_config.write_text(
        'worktree-path = "{{ repo_path }}/.worktrees/{{ branch | sanitize }}"\n'
    )
    env = os.environ.copy()
    env.pop("MISE_CONFIG_FILE", None)

    result = subprocess.run(
        [
            wt,
            "--config",
            str(user_config),
            "switch",
            "--create",
            "feature",
            "--no-cd",
            "--yes",
        ],
        cwd=main_clone,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert git(main_clone, "rev-parse", "feature") == git(
        main_clone, "rev-parse", "origin/main"
    )
