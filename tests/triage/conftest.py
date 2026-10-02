"""Shared fixtures for the triage suite.

Tests target the chezmoi SOURCE (`bin/executable_triage`), not the deployed
`~/bin/triage`. Source and deployed drift in both directions, and testing the
deployed copy lets a bad commit pass against the previous version — the
vacuous-pass failure tests/binned/conftest.py describes.

Nothing here calls a model or the real policy resolver. `llm` and `policy` are
stubs installed on a PATH that contains nothing else, so the script cannot
silently find the real toolchain and no prompt leaves the test process. The
stubs record their argv, so tests can assert what the script WOULD have sent.

Run:
    pytest tests/triage -v
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "bin" / "executable_triage"

STUB_MEMO = "STUB MEMO — no model was called."


@pytest.fixture(scope="session")
def triage_module():
    """Import the triage source as a module so pure helpers are callable.

    Same SourceFileLoader trick as tests/binned: the file has no .py
    extension, so spec_from_file_location alone returns None.
    """
    if not SCRIPT.exists():
        pytest.skip(f"triage source not found at {SCRIPT}")
    loader = importlib.machinery.SourceFileLoader("triage", str(SCRIPT))
    spec = importlib.util.spec_from_loader("triage", loader, origin=str(SCRIPT))
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    loader.exec_module(mod)
    return mod


@pytest.fixture
def stub_memo() -> str:
    return STUB_MEMO


class Shims:
    """Stub `llm` and `policy` binaries in a private directory."""

    def __init__(self, root: pathlib.Path, tmp_path: pathlib.Path):
        self.root = root
        self.root.mkdir()
        self.tmp_path = tmp_path
        self.llm_capture = tmp_path / "llm-capture.json"
        self.policy_capture = tmp_path / "policy-capture.txt"

    def install_llm(self) -> None:
        stub = self.root / "llm"
        stub.write_text(
            f"#!{sys.executable}\n"
            "import json, os, sys\n"
            "path = os.environ.get('TRIAGE_TEST_LLM_CAPTURE', '')\n"
            "if path:\n"
            "    with open(path, 'w') as fh:\n"
            "        json.dump(sys.argv[1:], fh)\n"
            f"print({STUB_MEMO!r})\n"
        )
        stub.chmod(0o755)

    def install_policy(self, exit_code: int) -> None:
        stub = self.root / "policy"
        stub.write_text(
            "#!/bin/sh\n"
            'if [ -n "$TRIAGE_TEST_POLICY_CAPTURE" ]; then\n'
            '    printf \'%s\\n\' "$@" > "$TRIAGE_TEST_POLICY_CAPTURE"\n'
            "fi\n"
            f"exit {exit_code}\n"
        )
        stub.chmod(0o755)

    def install_policy_broken(self) -> None:
        stub = self.root / "policy"
        stub.write_text("this file is deliberately not executable\n")
        stub.chmod(0o000)

    def read_llm_args(self) -> list[str]:
        raw = self.llm_capture.read_text()
        assert raw.strip(), "llm stub recorded nothing — the model was never consulted"
        args = json.loads(raw)
        assert args, "llm stub recorded an empty argv — the invocation is untested"
        return args

    def read_policy_args(self) -> list[str]:
        raw = self.policy_capture.read_text()
        assert raw.strip(), (
            "policy stub recorded nothing — the resolver was never consulted"
        )
        return raw.splitlines()


@pytest.fixture
def shims(tmp_path):
    return Shims(tmp_path / "shim", tmp_path)


@pytest.fixture
def shim_env(shims, monkeypatch):
    """Shims with THIS process's PATH pointed at them alone.

    PATH holds only the shim directory, so a real `policy` or `llm` elsewhere on
    the host PATH cannot stand in for a missing stub — the "resolver missing"
    case is real rather than accidental.
    """
    monkeypatch.setenv("PATH", str(shims.root))
    monkeypatch.setenv("TRIAGE_TEST_LLM_CAPTURE", str(shims.llm_capture))
    monkeypatch.setenv("TRIAGE_TEST_POLICY_CAPTURE", str(shims.policy_capture))
    monkeypatch.delenv("TRIAGE_PLATFORM", raising=False)
    monkeypatch.delenv("TRIAGE_DOCS", raising=False)
    return shims


@pytest.fixture
def cli(tmp_path, shims):
    """Run the triage source as a subprocess against the stub toolchain.

    The child environment is built from scratch, so host TRIAGE_* or API-key
    variables cannot leak into a result.
    """

    def run(
        *args: str,
        input_text: str = "an email body",
        env_extra: dict | None = None,
        policy_exit: int | None = 1,
        with_llm: bool = True,
    ) -> subprocess.CompletedProcess:
        if with_llm:
            shims.install_llm()
        if policy_exit is not None:
            shims.install_policy(policy_exit)
        env = {
            "PATH": str(shims.root),
            "HOME": str(tmp_path),
            "TRIAGE_TEST_LLM_CAPTURE": str(shims.llm_capture),
            "TRIAGE_TEST_POLICY_CAPTURE": str(shims.policy_capture),
        }
        if env_extra:
            env.update(env_extra)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            input=input_text,
            env=env,
        )

    return run
