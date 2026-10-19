"""Shared fixture for the ollama-evals suite.

Loads the chezmoi SOURCE as a module. The script has no .py extension and a PEP
723 shebang, so it needs SourceFileLoader — but it guards its entry point, so
importing runs no work.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util

import pytest

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

SCRIPT = (
    PAYLOAD_ROOT / "dotfiles" / "apps" / "ollama" / "files" / "executable_ollama-evals"
)


@pytest.fixture(scope="session")
def ev():
    loader = importlib.machinery.SourceFileLoader("ollama_evals", str(SCRIPT))
    spec = importlib.util.spec_from_loader("ollama_evals", loader)
    # pyrefly: ignore [bad-argument-type]
    mod = importlib.util.module_from_spec(spec)
    try:
        loader.exec_module(mod)
    except ImportError as exc:
        # The script imports Pillow at module level, so a run without
        # `--with pillow` used to abort with 53 setup errors and take the rest
        # of the directory with it. A missing test-run dependency is a skip
        # with a named reason, not a failure — docs/PYTHON.md, Dependency
        # classes. Both directions are asserted in tests/suite.
        pytest.skip(f"ollama-evals dependencies unavailable: {exc}")
    return mod
