#!/usr/bin/env python3
"""Fast-forward clean main before creating or entering a worktree.

This never changes the selected task or parent branch and never discards local
changes. A dirty, diverged, or missing main checkout fails closed.
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--default-branch", default="main")
    parser.add_argument("--target", required=True)
    args = parser.parse_args()
    source = Path.cwd()

    try:
        exists = git(
            source,
            "show-ref",
            "--verify",
            "--quiet",
            f"refs/heads/{args.target}",
        )
        if exists.returncode == 0:
            print(f"{args.target}: existing branch; left unchanged")
            return 0

        entries = require(git(source, "worktree", "list", "--porcelain")).split("\n\n")
        base_path = next(
            (
                Path(lines[0].removeprefix("worktree "))
                for entry in entries
                if (lines := entry.splitlines())
                and f"branch refs/heads/{args.default_branch}" in lines
            ),
            None,
        )
        if base_path is None:
            raise RuntimeError(
                f"{args.default_branch} must have its own checkout. "
                "The task worktree is not a substitute."
            )
        if require(git(base_path, "status", "--porcelain")):
            raise RuntimeError(
                f"{args.default_branch} checkout is dirty at {base_path}. "
                "Commit, stash, or discard its changes deliberately."
            )

        require(git(base_path, "fetch", "origin", args.default_branch))
        require(
            git(
                base_path,
                "merge",
                "--ff-only",
                f"origin/{args.default_branch}",
            )
        )
        print(f"{args.default_branch}: synchronized with origin")
        return 0
    except RuntimeError as error:
        print(f"branch sync refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
