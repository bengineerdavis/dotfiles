"""The payload-root seam for every test suite.

The chezmoi payload — bin/, dotfiles/, dot_config/ and the chezmoi
special files — lives under home/ via .chezmoiroot. PAYLOAD_ROOT is the
single binding for that content; repository-only tooling stays at the
checkout root.

What goes through it: fixture paths to bin/, dotfiles/ and the chezmoi
special files, built here or in a suite harness. What does not:
repo-only trees — tests/, docs/, scripts/, tools/, uv.lock — which keep
a plain repo root, because they do not move.

Harnesses cannot import this file by name: pytest imports every
conftest as the flat top-level module `conftest`, so `from conftest`
import ...` resolves to whichever conftest loaded first
(tests/suite/test_conftest_isolation.py). Instead this module registers
itself under the unique alias `payload_seam`, and consumers do
`from payload_seam import PAYLOAD_ROOT`. The import system resolves that
name from sys.modules, where it was placed here, before any harness or
test module loads — pytest loads this conftest first for every tests/
run, including a run of a single subdirectory.
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

# The chezmoi source root; repository-only tooling stays above it.
PAYLOAD_ROOT = REPO / "home"

sys.modules.setdefault("payload_seam", sys.modules[__name__])


def payload_census(source: pathlib.Path) -> list[str]:
    """Read managed source paths, failing if chezmoi cannot answer.

    Callers must assert the expected inventory, not just this command's
    success: an empty source root can exit zero while planning deletion.
    """
    if shutil.which("chezmoi") is None:
        raise RuntimeError("chezmoi is required for the payload census")
    result = subprocess.run(
        ["chezmoi", "-S", str(source), "managed", "--path-style=source-relative"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    managed = result.stdout.split()
    if not managed:
        raise RuntimeError(f"empty chezmoi source state at {source}")
    return managed
