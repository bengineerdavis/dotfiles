"""Constants shared by the policy resolver fixtures and tests.

Deliberately not conftest.py: every conftest is imported as a top-level
module named `conftest`, so `from conftest import ...` resolves to whichever
one pytest imported first. See tests/guards/guard_harness.py.
"""

from __future__ import annotations

import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "bin" / "executable_policy"

# Exit codes, mirrored from the script so a silent change to either shows up
# as a failing test rather than as a test that quietly asserts nothing.
PERMITTED, DENIED, UNKNOWN, ERROR = 0, 1, 2, 3
