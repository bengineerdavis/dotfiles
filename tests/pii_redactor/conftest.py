"""
Shared fixtures for the pii-redactor suite.

Converted from bin/pii-redactor.bats when the script moved from bash to Python.
The bats suite could only drive the CLI as a black box; now that the script is
Python, pure helpers like default_output() are imported and tested directly,
and only behaviour that genuinely involves the process — exit codes, streams,
file permissions, argv passed to llm — goes through a subprocess.

Run everything except the real-model tests:
    pytest tests/pii_redactor -v

Run the real-model tests (slow, loads a local model):
    pytest -m llm_judge tests/pii_redactor -v -s
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import pathlib
import subprocess

import pytest

SCRIPT = pathlib.Path.home() / "bin" / "pii-redactor"

# Small local model with thinking disabled, so the real-model tests stay quick.
INTEGRATION_MODEL = "qwen3.5:4b-mlx-bf16"
INTEGRATION_LLM_OPTS = "-o think false"


@pytest.fixture(scope="session")
def pii_module():
    """Import pii-redactor as a module so its helpers can be called directly."""
    if not SCRIPT.exists():
        pytest.skip(f"pii-redactor not found at {SCRIPT} — run: chezmoi apply ~/bin")
    # No .py extension, so spec_from_file_location returns None; SourceFileLoader
    # tells Python to treat it as source anyway. Same trick as tests/binned.
    loader = importlib.machinery.SourceFileLoader("pii_redactor", str(SCRIPT))
    spec = importlib.util.spec_from_loader("pii_redactor", loader, origin=str(SCRIPT))
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    loader.exec_module(mod)
    return mod


@pytest.fixture
def mock_llm(tmp_path, monkeypatch):
    """Put a fake `llm` at the front of PATH and return a function to redefine it.

    Defaults to echoing stdin back, so callers can inspect what was piped in.
    Tests that care about argv or the child environment install their own body.
    """
    bindir = tmp_path / "mockbin"
    bindir.mkdir()
    script = bindir / "llm"

    def install(body: str = "cat") -> pathlib.Path:
        script.write_text(f"#!/usr/bin/env bash\n{body}\n")
        script.chmod(0o755)
        return script

    install()
    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.environ['PATH']}")
    return install


@pytest.fixture
def run_script():
    """Run pii-redactor and return the CompletedProcess, stdout and stderr merged.

    Merged because the bats suite asserted against combined output, and several
    cases care that a message reaches the user without caring which stream.
    """
    def _run(*args: str, stdin: str | None = None, cwd=None, env=None):
        return subprocess.run(
            [str(SCRIPT), *args],
            input=stdin,
            capture_output=True,
            text=True,
            cwd=str(cwd) if cwd else None,
            env=env,
            timeout=300,
        )
    return _run
