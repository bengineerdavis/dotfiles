"""
Fixtures for the quarantine suite.

Black-box: the script is run as a subprocess with $XDG_STATE_HOME redirected, so
no test touches the real store. The `file:` identity backend is used throughout
rather than `keychain:`/`op:`/`bw:` — those depend on machine state and a
credential prompt, so a suite that used them would either skip silently or hang.

The backends are thin `subprocess.run` wrappers over one documented command
each; what needs testing is the surrounding contract — no key on disk, no paths
in the sidecar, a bad key failing cleanly.

Run:
    pytest tests/quarantine -v
"""

from __future__ import annotations

import pathlib
import re
import shutil
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "bin" / "executable_quarantine"

SECRET_RE = re.compile(r"AGE-SECRET-KEY-1[A-Z0-9]+")


def _age_dir() -> str | None:
    """age comes from mise, which may not be on a bare PATH."""
    if shutil.which("age"):
        return None
    for cand in (pathlib.Path.home() / ".local/share/mise/installs/age").glob("*/age"):
        if (cand / "age").exists():
            return str(cand)
    return None


@pytest.fixture
def quarantine(tmp_path):
    """Return (run, state_dir). `run` invokes the script with a private store."""
    state = tmp_path / "state"
    state.mkdir()
    extra = _age_dir()
    import os

    path = os.environ.get("PATH", "")
    if extra:
        path = f"{extra}:{path}"

    def run(*args: str, identity: str | None = None, stdin: str | None = None):
        env = {
            "XDG_STATE_HOME": str(state),
            "PATH": path,
            "HOME": str(tmp_path),
        }
        if identity:
            env["QUARANTINE_IDENTITY_FROM"] = identity
        return subprocess.run(
            ["python3", str(SCRIPT), *args],
            capture_output=True, text=True, env=env, input=stdin,
        )

    return run, state


@pytest.fixture
def initialised(quarantine, tmp_path):
    """An initialised store plus a key file, mimicking a password manager."""
    run, state = quarantine
    result = run("init")
    if result.returncode != 0:
        pytest.skip(f"age unavailable: {result.stderr.strip()[:80]}")
    match = SECRET_RE.search(result.stdout)
    assert match, "init did not print an identity"
    keyfile = tmp_path / "key.txt"
    keyfile.write_text(match.group(0) + "\n")
    keyfile.chmod(0o600)
    return run, state, f"file:{keyfile}"
