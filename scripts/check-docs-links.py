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

# Backends tried in order. The cargo build is primary because the aqua release
# binary is built against a newer glibc than this fleet's Debian 12 (2.35) and
# cannot execute there — it fails with "GLIBC_2.38 not found" before reading a
# single file. Measured 2026-11-01 and 2026-11-04; the Lima guest ships glibc
# 2.36, which is why VM runs never surfaced it.
#
# The aqua entry stays as the fallback: it is the one that works on macOS and on
# any host new enough, so removing it would break the Mac to fix Debian.
BACKENDS = (
    "cargo:lycheeverse/lychee",
    "aqua:lycheeverse/lychee@0.24.2",
)
DEFAULT_BACKEND = BACKENDS[0]

# A version probe should be instant. A cold cargo build is not (it compiles
# ~500 crates), but that build happens during provisioning, not at commit time;
# if it is missing, the probe times out and the next backend is tried.
PROBE_TIMEOUT = 120

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


def lychee_command(
    paths: list[str], external: bool, backend: str | None = None
) -> list[str]:
    """Build the Lychee invocation for one backend.

    `paths` is unused: the files go in on stdin via `--files-from -`, which keeps
    a long file list off the command line and stays under ARG_MAX.
    """
    command = [
        "mise",
        "exec",
        backend or DEFAULT_BACKEND,
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


def probe_backend(token: str) -> bool:
    """True when Lychee from this backend actually executes.

    A version probe, not a link check. That distinction is load-bearing: a
    backend that runs and finds a broken link must report the finding, never
    fall through to the next backend. Falling through on a link failure would
    turn "the docs have a broken link" into "try another binary".
    """
    try:
        result = subprocess.run(
            ["mise", "exec", token, "--", "lychee", "--version"],
            capture_output=True,
            text=True,
            timeout=PROBE_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def select_backend() -> str | None:
    """First backend whose binary executes, or None when none do."""
    for token in BACKENDS:
        if probe_backend(token):
            return token
    return None


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
    backend = select_backend()
    if backend is None:
        # Fail loudly. A skip and a pass are indistinguishable in a commit log,
        # so a checker that cannot run must not report success.
        print(
            "No Lychee backend could be executed. Tried: " + ", ".join(BACKENDS) + ".\n"
            "Run the mise topic to install Lychee from cargo "
            "(`mise install cargo:lycheeverse/lychee`), then retry. "
            "This check is not optional; fix the install rather than "
            "committing with --no-verify.",
            file=sys.stderr,
        )
        return 2
    command = lychee_command(selected, args.external, backend)
    return subprocess.run(
        command,
        cwd=repo,
        input="\n".join(selected) + "\n",
        text=True,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
