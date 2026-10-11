"""Shared fixtures for the ollama-models suite.

Loads the chezmoi SOURCE as a module, the same way tests/ollama_evals
does: the script has no .py extension and a PEP 723 shebang, so it
needs SourceFileLoader — but it guards its entry point, so importing
runs no work.

`real_manifest` is the actual defaults/main.yaml. It is READ ONLY here;
every test that writes works on a copy in tmp_path. That is the point
of the suite: the thing being protected is that specific file, and a
synthetic fixture would prove nothing about it.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TOPIC = REPO / "dotfiles" / "apps" / "ollama"
SCRIPT = TOPIC / "files" / "executable_ollama-models"
MANIFEST = TOPIC / "defaults" / "main.yaml"


@pytest.fixture(scope="session")
def om():
    loader = importlib.machinery.SourceFileLoader("ollama_models", str(SCRIPT))
    spec = importlib.util.spec_from_loader("ollama_models", loader)
    # pyrefly: ignore [bad-argument-type]
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def real_manifest() -> str:
    return MANIFEST.read_text()


@pytest.fixture
def manifest_copy(tmp_path) -> pathlib.Path:
    """A writable copy of the real manifest, so tests never touch it."""
    dest = tmp_path / "main.yaml"
    dest.write_text(MANIFEST.read_text())
    return dest
