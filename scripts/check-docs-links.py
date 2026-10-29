#!/usr/bin/env python3
"""Run Lychee on selected local Markdown files.

The file selector is separate from Lychee's URL exclusions: `exclude` in
lychee.toml filters destinations, not documents. This distinction keeps
machine-owned and generated files out of the checker entirely.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys

REPO = Path(__file__).resolve().parent.parent
CONFIG = REPO / "lychee.toml"
EXCLUDED_PATHS = (
    PurePosixPath(".lore.md"),
    PurePosixPath("backlog"),
    PurePosixPath("changelog.d"),
    PurePosixPath("CHANGELOG.md"),
    PurePosixPath("home/dotfiles/apps/ollama/docs"),
)
EXCLUDED_FILES = {
    PurePosixPath("home/bin/executable_READMD.archive.md"),
    PurePosixPath("home/bin/READMD.archive.md"),
}
USAGE = "usage: python3 scripts/check-docs-links.py [--changed] [--external] [FILE ...]"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument(
        "--changed", action="store_true", help="check only the supplied changed files"
    )
    parser.add_argument(
        "--external",
        action="store_true",
        help="check public HTTP(S) links; requires author review of this run",
    )
    parser.add_argument("files", nargs="*")
    args = parser.parse_args(argv)
    if args.changed and not args.files:
        parser.error("--changed requires at least one file")
    return args


def is_selected(path: str) -> bool:
    candidate = PurePosixPath(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        return False
    if candidate.suffix.lower() not in {".md", ".mdx"}:
        return False
    if candidate in EXCLUDED_FILES:
        return False
    return not any(
        candidate == root or root in candidate.parents for root in EXCLUDED_PATHS
    )


def tracked_markdown(repo: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-z", "--", "*.md", "*.mdx"],
        check=True,
        capture_output=True,
    )
    paths = result.stdout.decode().split("\0")
    return sorted(path for path in paths if path and is_selected(path))


def lychee_command(paths: list[str], external: bool) -> list[str]:
    command = [
        "mise",
        "exec",
        "aqua:lycheeverse/lychee@0.24.2",
        "--",
        "lychee",
        "--config",
        str(CONFIG),
        "--no-progress",
    ]
    if external:
        command.append("--offline=false")
    else:
        command.append("--offline")
    return [*command, "--files-from", "-"]


def main(argv: list[str], repo: Path = REPO) -> int:
    args = parse_args(argv)
    if not CONFIG.is_file():
        print(
            "Lychee configuration is missing; install the repository tools.",
            file=sys.stderr,
        )
        return 2
    if shutil.which("mise") is None:
        print(
            "mise is required; run the mise topic to install Lychee.", file=sys.stderr
        )
        return 2
    if args.external and os.environ.get("LYCHEE_EXTERNAL_APPROVED") != "1":
        print(
            "External link checks require author review of this revision. "
            "After approval, rerun with LYCHEE_EXTERNAL_APPROVED=1.",
            file=sys.stderr,
        )
        return 2

    paths = args.files if args.changed else tracked_markdown(repo)
    if args.changed:
        result = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "-z", "--", *paths],
            check=True,
            capture_output=True,
        )
        paths = [path for path in result.stdout.decode().split("\0") if path]
    selected = sorted({path for path in paths if is_selected(path)})
    if not selected:
        print("No documentation links selected.")
        return 0
    command = lychee_command(selected, args.external)
    return subprocess.run(
        command,
        cwd=repo,
        input="\n".join(selected) + "\n",
        text=True,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
