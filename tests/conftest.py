"""The payload-root seam for every test suite.

The chezmoi payload — bin/, dotfiles/, dot_config/ and the chezmoi
special files — lives at the repo root today and moves under home/ via
.chezmoiroot (TASKS.md § Planned, payload move). PAYLOAD_ROOT is the one
binding that names where that content lives, so the move repoints a
single line instead of ~25 divergent patches.

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
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

# The payload root. Today the repo root itself; the move repoints ONLY
# this line, to REPO / "home".
PAYLOAD_ROOT = REPO

sys.modules.setdefault("payload_seam", sys.modules[__name__])
