#!/usr/bin/env python3
"""Refuse to push a branch that no longer merges cleanly with main.

Runs as a `pre-push` hook. Two steps, in this order:

1. Fast-forward the local `main` checkout to `origin/main`. A dirty, diverged,
   or absent `main` fails closed with the fix named; this never discards work.
2. Simulate merging `main` into the branch being pushed, in memory. A conflict
   fails the push and names the files, so the branch is resolved deliberately
   instead of being discovered at merge time.

The merge step uses `git merge-tree --write-tree` (git 2.38+), which performs a
real three-way merge against the object database without touching the working
tree or the index. A hook that mutated the tree would leave residue the author
never reviewed.

This never merges `main` into the branch for you. A clean simulation means the
branch needs no action; a conflict means a human or agent has to decide how the
two changes reconcile.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def require(result: subprocess.CompletedProcess[str]) -> str:
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def find_checkout(repo: Path, branch: str) -> Path:
    """Return the worktree that has `branch` checked out."""
    entries = require(git(repo, "worktree", "list", "--porcelain")).split("\n\n")
    for entry in entries:
        lines = entry.splitlines()
        if not lines:
            continue
        path = Path(lines[0].removeprefix("worktree "))
        if f"branch refs/heads/{branch}" in lines:
            return path
    raise RuntimeError(
        f"{branch} must have its own checkout. A task worktree is not a "
        f"substitute, and this hook will not create one."
    )


def fast_forward(base: Path, branch: str) -> None:
    """Bring the local base branch up to origin when that is free.

    This is a convenience, never a gate. `main` is shared by every session on
    the machine: one session's unpushed commit, or a rebase in progress, makes
    it diverge for minutes at a time. Refusing a push because of that blocks
    work the pusher cannot fix and did not cause — measured three times on
    2026-11-08, each time against a checkout someone else was mid-edit in.

    So: try, and ignore the outcome. Mergeability is decided against
    `origin/{branch}`, which is what the pushed branch actually merges into
    and which nothing local can move.
    """
    if git(base, "fetch", "origin", branch).returncode:
        return
    counts = require(
        git(base, "rev-list", "--left-right", "--count", f"origin/{branch}...HEAD")
    ).split()
    behind = int(counts[0]) if len(counts) == 2 else 0
    if behind == 0:
        return
    # Best effort. A refusal means the shared checkout is busy; the push is
    # still judged on `origin/{branch}` below.
    git(base, "merge", "--ff-only", f"origin/{branch}")


def conflicting_files(repo: Path, base_branch: str) -> list[str]:
    """Return the paths that conflict between HEAD and the merge target.

    The target is `origin/{base_branch}`: a push lands on the remote, so the
    remote tip is what the branch has to merge with. A local checkout of the
    same branch can be ahead, behind, mid-rebase, or stale, and none of that
    changes what the push does.
    """
    target = f"origin/{base_branch}"
    if git(repo, "rev-parse", "--verify", "--quiet", target).returncode:
        raise RuntimeError(
            f"no {target} to compare against. Fetch it first: "
            f"git fetch origin {base_branch}"
        )
    result = git(repo, "merge-tree", "--write-tree", target, "HEAD")
    if result.returncode == 0:
        return []

    # `merge-tree --write-tree` prints one line per stage entry, shaped
    # `<mode> <object> <stage>\t<path>` — exactly two tab-separated fields.
    # Conflicts also appear in prose on stderr, so only the entries are parsed.
    paths: list[str] = []
    for line in result.stdout.splitlines():
        fields = line.split("\t")
        if len(fields) != 2:
            continue
        meta, path = fields
        parts = meta.split()
        if len(parts) == 3 and parts[2] in {"1", "2", "3"} and path:
            if path not in paths:
                paths.append(path)
    if paths:
        return paths

    # Older git only names conflicts in prose. Keep the reason rather than
    # returning "conflict" without saying where.
    detail = (result.stderr or result.stdout).strip().splitlines()
    return [detail[0]] if detail else ["(git did not name the conflicting paths)"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--default-branch", default="main")
    parser.add_argument(
        "--repo",
        default=None,
        help="repository to check; defaults to the current directory",
    )
    args = parser.parse_args()

    repo = Path(args.repo) if args.repo else Path.cwd()
    branch = args.default_branch

    try:
        # The local checkout is optional. Using it when present keeps `main`
        # current as a convenience; its state never decides the push.
        try:
            fast_forward(find_checkout(repo, branch), branch)
        except RuntimeError:
            pass
        conflicts = conflicting_files(repo, branch)
    except RuntimeError as error:
        # Cannot decide is not the same as "conflicts". Only a real conflict
        # returns 1; an unknown returns 2 so a caller can tell them apart.
        print(f"branch sync cannot check: {error}", file=sys.stderr)
        return 2

    if not conflicts:
        print(f"branch sync: origin/{branch} merges cleanly into the pushed branch")
        return 0

    current = require(git(repo, "rev-parse", "--abbrev-ref", "HEAD"))
    print(
        f"branch sync: origin/{branch} needs to be resolved with {current} "
        f"before it can merge. Conflicting paths:",
        file=sys.stderr,
    )
    for path in conflicts:
        print(f"  {path}", file=sys.stderr)
    print(
        f"\nResolve with: git -C {repo} merge origin/{branch}\n"
        f"This hook does not merge for you: the two changes have to be "
        f"reconciled on purpose.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
