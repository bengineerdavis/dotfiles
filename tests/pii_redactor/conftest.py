"""Shared fixtures for the pii-redactor suite.

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

from pii_redactor_harness import (
    INTEGRATION_LLM_OPTS,
    INTEGRATION_MODEL,
    SCRIPT,
    WORKING_MODEL,
)


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

    Defaults to a model that redacts name-shaped text. Tests that care about
    argv, the child environment, or a specific failure mode install their own
    body — `mock_llm("cat")` for a pass-through, for instance.
    """
    bindir = tmp_path / "mockbin"
    bindir.mkdir()
    script = bindir / "llm"

    def install(body: str = WORKING_MODEL) -> pathlib.Path:
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

    def _run(
        *args: str, stdin: str | None = None, cwd=None, env=None, gated: bool = False
    ):
        # Capturing output means stdout is not a terminal, which is exactly what
        # arms the pre-release review gate — so without this every success-path
        # case would fail on a prompt it cannot answer. `gated=True` leaves the
        # gate armed for the tests that are about the gate itself; everything
        # else waives it, because a test asserting on redaction behaviour is not
        # a test of review.
        #
        # --help and --dry-run never reach the gate, and adding an unknown-looking
        # flag to an argument-error case would change what it is testing, so both
        # are left alone.
        # Prepended, never appended: `--input` with no value is a real test
        # case, and a flag added after it would be consumed as its argument,
        # quietly turning a "missing argument" test into something else.
        skip_gate = not gated and not any(
            a in ("--help", "-h", "--dry-run") for a in args
        )
        extra = ("--assume-reviewed",) if skip_gate else ()
        return subprocess.run(
            [str(SCRIPT), *extra, *args],
            input=stdin,
            capture_output=True,
            text=True,
            cwd=str(cwd) if cwd else None,
            env=env,
            timeout=300,
        )

    return _run
