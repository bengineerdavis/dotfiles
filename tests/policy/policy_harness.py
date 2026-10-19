"""Constants shared by the policy resolver fixtures and tests.

Deliberately not conftest.py: every conftest is imported as a top-level
module named `conftest`, so `from conftest import ...` resolves to whichever
one pytest imported first. See tests/guards/guard_harness.py.
"""

from __future__ import annotations

import os
import pathlib

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

SCRIPT = PAYLOAD_ROOT / "bin" / "executable_policy"

# Exit codes, mirrored from the script so a silent change to either shows up
# as a failing test rather than as a test that quietly asserts nothing.
PERMITTED, DENIED, UNKNOWN, ERROR = 0, 1, 2, 3


def uv_dir() -> str:
    """Directory of a real `uv` binary, or "" when PATH has only a shim.

    A mise shim re-enters mise, which resolves its tool config against the
    test's stripped HOME, finds the real global config untrusted (fresh
    trust database), and exits 1 — the 2026-10-03 cwd-sensitivity, where
    tests/policy passed from `~/code` but failed from the main checkout.
    Exit 1 is also DENIED, so a broken resolver read as a policy denial and
    the deny-direction tests passed while proving nothing. Fixtures prepend
    this directory to PATH so the subprocesses run uv directly. Whether a
    real binary is reachable depends on how pytest was launched and mise's
    per-directory activation, so every PATH entry is scanned. A machine
    whose only `uv` is a mise shim falls back to empty; the failure there
    is mise's own error, visible rather than silent.
    """
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry:
            continue
        p = pathlib.Path(entry) / "uv"
        if p.exists() and p.resolve().name == "uv":
            return str(p.parent)
    return ""
