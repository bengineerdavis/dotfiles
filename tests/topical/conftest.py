"""Fixtures for the topical generator suite.

The subject is `tools/topical/topical` — no .py extension, so it loads
through SourceFileLoader, the same pattern as tests/binned/conftest.py.
The scaffold source (`--repo`) is the worktree's `dotfiles/`, routed
through the payload_seam PAYLOAD_ROOT binding; the destination
is tmp_path.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
from pathlib import Path

import pytest

# tools/ is repo-only (it does not move with the payload), so a plain
# checkout-relative path is correct here — see tests/conftest.py.
REPO = Path(__file__).resolve().parents[2]
TOPICAL_PATH = REPO / "tools" / "topical" / "topical"


@pytest.fixture(scope="session")
def topical_module():
    """Import tools/topical/topical as a module to drive its app.

    Skips the whole suite if typer/pyyaml are not in this environment —
    the root test dependency group carries both.
    """
    if not TOPICAL_PATH.exists():
        pytest.skip(f"topical source not found at {TOPICAL_PATH}")
    try:
        loader = importlib.machinery.SourceFileLoader("topical", str(TOPICAL_PATH))
        spec = importlib.util.spec_from_loader(
            "topical", loader, origin=str(TOPICAL_PATH)
        )
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        loader.exec_module(mod)
        return mod
    except ImportError as exc:
        pytest.skip(f"topical deps not installed ({exc})")


@pytest.fixture()
def runner(topical_module):
    from typer.testing import CliRunner

    return CliRunner()


@pytest.fixture()
def repo_root():
    """The checkout to scaffold FROM — the worktree's own dotfiles/."""
    # pyrefly: ignore [missing-import]
    from payload_seam import PAYLOAD_ROOT

    return PAYLOAD_ROOT


@pytest.fixture()
def scaffold(runner, repo_root, topical_module, tmp_path):
    """Invoke `topical new` into tmp_path; return (result, into)."""

    def _scaffold(*args: str) -> tuple:
        result = runner.invoke(
            topical_module.app,
            ["new", *args, "--repo", str(repo_root), "--into", str(tmp_path)],
        )
        return result, tmp_path

    return _scaffold
