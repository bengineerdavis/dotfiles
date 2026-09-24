"""Constants shared by the quarantine fixtures and tests.

Deliberately not conftest.py: every conftest is imported as a top-level
module named `conftest`, so `from conftest import ...` resolves to whichever
one pytest imported first. See tests/guards/guard_harness.py.
"""

from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "bin" / "executable_quarantine"

SECRET_RE = re.compile(r"AGE-SECRET-KEY-1[A-Z0-9]+")
