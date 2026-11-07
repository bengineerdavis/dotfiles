"""The pre-push branch-sync check.

The hook must do two things and never a third: bring local `main` up to
`origin/main`, report whether the pushed branch still merges, and
leave the branch alone. A hook that quietly "fixes" the branch is worse
than no hook, so most of these tests are about what it refuses to do.

Run:
    pytest tests/scripts/test_check_branch_sync.py -v
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[2] / "scripts" / "check-branch-sync.py"

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 10), reason="the helper uses PEP 604 unions"
)


def git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(cwd), *args],
        text=True,
        stderr=subprocess.DEVNULL,
    ).strip()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def commit(cwd: Path, message: str) -> str:
    git(cwd, "add", "-A")
    git(
        cwd,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@local",
        "commit",
        "-m",
        message,
    )
    return git(cwd, "rev-parse", "HEAD")


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("MISE_CONFIG_FILE", None)
    env.update(
        GIT_AUTHOR_NAME="Fixture",
        GIT_AUTHOR_EMAIL="fixture@local",
        GIT_COMMITTER_NAME="Fixture",
        GIT_COMMITTER_EMAIL="fixture@local",
    )
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        env=env,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A repository with `origin`, a main checkout, and a task worktree.

    Mirrors the real shape: `main` is checked out in one directory and
    the branch under test in another, so the hook cannot assume it runs
    in the branch it is checking.
    """
    origin = tmp_path / "origin.git"
    subprocess.check_call(["git", "init", "--bare", "-q", str(origin)])

    main = tmp_path / "main"
    subprocess.check_call(["git", "init", "-q", "-b", "main", str(main)])
    write(main / "shared.txt", "base\n")
    commit(main, "base")
    git(main, "remote", "add", "origin", str(origin))
    git(main, "push", "-q", "-u", "origin", "main")

    task = tmp_path / "task"
    git(main, "worktree", "add", "-q", "-b", "feature", str(task))
    return main


def test_a_clean_branch_passes(repo: Path) -> None:
    task = repo.parent / "task"
    write(task / "feature.txt", "feature work\n")
    commit(task, "feature")

    result = run(cwd=task)

    assert result.returncode == 0, result.stderr
    assert "merges cleanly" in result.stdout


def test_a_conflicting_branch_fails_and_names_the_file(repo: Path) -> None:
    """The conflict is the reason the hook exists; it must be loud."""
    # Both sides change the same line of the same file.
    write(repo / "shared.txt", "main side\n")
    commit(repo, "main change")
    git(repo, "push", "-q", "origin", "main")

    task = repo.parent / "task"
    write(task / "shared.txt", "feature side\n")
    commit(task, "feature change")

    result = run(cwd=task)

    assert result.returncode == 1
    assert "shared.txt" in result.stderr
    assert "needs to be resolved" in result.stderr


def test_the_conflicting_branch_is_not_merged_for_you(repo: Path) -> None:
    """A clean simulation still leaves the branch byte-identical."""
    task = repo.parent / "task"
    write(task / "feature.txt", "feature work\n")
    commit(task, "feature")
    before = git(task, "rev-parse", "HEAD")

    run(cwd=task)

    assert git(task, "rev-parse", "HEAD") == before
    assert git(task, "status", "--porcelain") == ""


def test_local_main_is_fast_forwarded_to_origin(repo: Path) -> None:
    """The hook updates main, the first half of what was asked."""
    upstream = repo.parent / "upstream"
    git(
        repo.parent,
        "clone",
        "-q",
        str(repo / ".." / "origin.git"),
        str(upstream),
    )
    write(upstream / "shared.txt", "advanced\n")
    commit(upstream, "advance main")
    git(upstream, "push", "-q", "origin", "main")

    task = repo.parent / "task"
    run(cwd=task)

    assert (repo / "shared.txt").read_text() == "advanced\n"


def test_a_dirty_main_checkout_refuses(repo: Path) -> None:
    """Refusing beats discarding work nobody asked it to touch."""
    write(repo / "shared.txt", "uncommitted\n")
    task = repo.parent / "task"

    result = run(cwd=task)

    assert result.returncode == 1
    assert "dirty" in result.stderr
    assert (repo / "shared.txt").read_text() == "uncommitted\n"


def test_a_diverged_main_refuses_instead_of_rewriting(repo: Path) -> None:
    """Local commits that origin lacks are the author's to reconcile."""
    write(repo / "local-only.txt", "local work\n")
    commit(repo, "local only commit")
    task = repo.parent / "task"

    result = run(cwd=task)

    assert result.returncode == 1
    assert "local commit" in result.stderr
    assert (repo / "local-only.txt").exists()


def test_a_missing_main_checkout_refuses(tmp_path: Path) -> None:
    """No main checkout means no way to fast-forward; say so."""
    lonely = tmp_path / "lonely"
    subprocess.check_call(["git", "init", "-q", "-b", "feature", str(lonely)])
    write(lonely / "f.txt", "x\n")
    commit(lonely, "only branch")

    result = run(cwd=lonely)

    assert result.returncode == 1
    assert "must have its own checkout" in result.stderr
