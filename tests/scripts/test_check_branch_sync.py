"""The pre-push branch-sync check.

The hook must do two things and never a third: bring local `main` up to
`origin/main`, report whether the pushed branch still merges, and leave
the branch alone. A hook that quietly "fixes" the branch is worse than
no hook, so most of these tests are about what it refuses to do.
Run: pytest tests/scripts/test_check_branch_sync.py -v
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
    subprocess.check_call(
        ["git", "-c", "init.templateDir=", "init", "--bare", "-q", str(origin)]
    )

    main = tmp_path / "main"
    subprocess.check_call(
        ["git", "-c", "init.templateDir=", "init", "-q", "-b", "main", str(main)]
    )
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
        "-c",
        "init.templateDir=",
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


def test_a_dirty_main_checkout_with_unrelated_edits_still_syncs(
    repo: Path,
) -> None:
    """Concurrent sessions share main; uncommitted work must not block.

    This is the common case here: a background process rewrites
    `.lore.md` in the main checkout while a session pushes from its
    worktree. Refusing on any dirt would make every push depend on
    another session's working state.
    """
    write(repo / "unrelated.txt", "work in progress\n")
    upstream = repo.parent / "upstream"
    git(
        repo.parent,
        "-c",
        "init.templateDir=",
        "clone",
        "-q",
        str(repo / ".." / "origin.git"),
        str(upstream),
    )
    write(upstream / "shared.txt", "advanced\n")
    commit(upstream, "advance main")
    git(upstream, "push", "-q", "origin", "main")

    task = repo.parent / "task"
    result = run(cwd=task)

    assert result.returncode == 0, result.stderr
    assert (repo / "shared.txt").read_text() == "advanced\n"
    # The unrelated edit survives untouched.
    assert (repo / "unrelated.txt").read_text() == "work in progress\n"


def test_a_dirty_main_checkout_never_loses_work_and_never_blocks(
    repo: Path,
) -> None:
    """Uncommitted work in the shared checkout is left exactly as found.

    The hook used to fail here, which meant one session's half-typed
    edit stopped every other session from pushing. It now leaves `main`
    alone: the edit stays byte-identical, and the push is judged on
    mergeability.
    """
    write(repo / "shared.txt", "uncommitted\n")
    upstream = repo.parent / "upstream"
    git(
        repo.parent,
        "-c",
        "init.templateDir=",
        "clone",
        "-q",
        str(repo / ".." / "origin.git"),
        str(upstream),
    )
    write(upstream / "shared.txt", "advanced\n")
    commit(upstream, "advance main")
    git(upstream, "push", "-q", "origin", "main")

    task = repo.parent / "task"
    result = run(cwd=task)

    assert result.returncode == 0, result.stderr
    assert (repo / "shared.txt").read_text() == "uncommitted\n"


def test_local_commits_ahead_of_origin_do_not_block(repo: Path) -> None:
    """Committing to local main without pushing is normal here.

    Sessions commit to local main; the author pushes later. Ahead of
    origin with nothing behind it, the fast-forward is a no-op, so
    refusing would gate every push on a push that has not happened yet.
    """
    write(repo / "local-work.txt", "unpushed session work\n")
    commit(repo, "a session's commit, not yet pushed")

    task = repo.parent / "task"
    result = run(cwd=task)

    assert result.returncode == 0, result.stderr
    assert "merges cleanly" in result.stdout


def test_a_diverged_local_main_does_not_block_someone_elses_push(
    repo: Path,
) -> None:
    """Local main diverging is another session's problem, not yours.

    Every session shares the main checkout. One session committing to
    local main while origin advances makes it diverge for minutes at a
    time — and a rebase in progress is the same shape. Gating a push on
    that state blocks work in every worktree for a reason the pusher
    cannot fix, which is what happened three times on 2026-11-08.
    The branch merges into origin/main, so that is what decides.
    """
    write(repo / "local-work.txt", "unpushed\n")
    commit(repo, "local commit")

    upstream = repo.parent / "upstream"
    git(
        repo.parent,
        "-c",
        "init.templateDir=",
        "clone",
        "-q",
        str(repo / ".." / "origin.git"),
        str(upstream),
    )
    write(upstream / "upstream.txt", "origin moved on\n")
    commit(upstream, "origin advances")
    git(upstream, "push", "-q", "origin", "main")

    task = repo.parent / "task"
    result = run(cwd=task)

    assert result.returncode == 0, result.stderr
    assert "merges cleanly" in result.stdout
    # The hook still must not touch anyone's work.
    assert (repo / "local-work.txt").exists()


def test_a_branch_that_conflicts_with_origin_main_still_refuses(
    repo: Path,
) -> None:
    """Checking origin/main must still catch a real conflict.

    Dropping the local-main gate cannot turn the check into a rubber
    stamp: a branch that genuinely conflicts with the merge target is
    still refused, and the local checkout is still left alone.
    """
    upstream = repo.parent / "upstream"
    git(
        repo.parent,
        "-c",
        "init.templateDir=",
        "clone",
        "-q",
        str(repo / ".." / "origin.git"),
        str(upstream),
    )
    write(upstream / "shared.txt", "origin edit\n")
    commit(upstream, "origin edits the shared file")
    git(upstream, "push", "-q", "origin", "main")

    task = repo.parent / "task"
    write(task / "shared.txt", "branch edit\n")
    commit(task, "branch edits the shared file")

    result = run(cwd=task)

    assert result.returncode == 1
    assert "shared.txt" in result.stderr


def test_a_missing_main_checkout_does_not_block(tmp_path: Path) -> None:
    """No base checkout is fine: merges are checked against origin.

    A session working in a clone that never checked out `main` can still
    push a branch. The old refusal made the local checkout a hard
    requirement, which it never was — the remote is what the push merges
    into.
    """
    lonely = tmp_path / "lonely"
    subprocess.check_call(
        ["git", "-c", "init.templateDir=", "init", "-q", "-b", "feature", str(lonely)]
    )
    write(lonely / "f.txt", "x\n")
    commit(lonely, "only branch")
    git(lonely, "remote", "add", "origin", str(tmp_path / "nonexistent.git"))

    result = run(cwd=lonely)

    # The remote does not exist, so it cannot be checked — but the
    # answer is an unknown (2), never a claim that it merges cleanly.
    assert result.returncode == 2, result.stderr
    assert "no origin/main" in result.stderr


def test_the_merge_target_is_origin_main_not_the_shared_checkout(
    repo: Path,
) -> None:
    """A branch merges into origin/main; that is what to check.

    A push lands on the remote. The local `main` checkout is a different
    thing: every session shares it, and another session's unpushed
    commit — or a rebase in progress — makes it diverge for minutes at a
    time. Gating a push on that state blocks work in every worktree for
    a reason the pusher cannot fix and did not cause.
    This test leaves local main ahead of origin and asserts the push is
    judged on the branch's mergeability alone.
    """
    write(repo / "unpushed.txt", "another session's commit\n")
    commit(repo, "a session's commit, not yet pushed")

    task = repo.parent / "task"
    result = run(cwd=task)

    assert result.returncode == 0, result.stderr
    assert "merges cleanly" in result.stdout
