"""Shared fixture for the ollama-evals suite.

Loads the chezmoi SOURCE as a module. The script has no .py extension and a PEP
723 shebang, so it needs SourceFileLoader — but it guards its entry point, so
importing runs no work.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "dotfiles" / "apps" / "ollama" / "files" / "executable_ollama-evals"


@pytest.fixture(scope="session")
def ev():
    loader = importlib.machinery.SourceFileLoader("ollama_evals", str(SCRIPT))
    spec = importlib.util.spec_from_loader("ollama_evals", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod
