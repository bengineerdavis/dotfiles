"""Constants shared by the quarantine fixtures and tests.

Deliberately not conftest.py: every conftest is imported as a top-level
module named `conftest`, so `from conftest import ...` resolves to whichever
one pytest imported first. See tests/guards/guard_harness.py.
"""

from __future__ import annotations

import re

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

SCRIPT = PAYLOAD_ROOT / "bin" / "executable_quarantine"

SECRET_RE = re.compile(r"AGE-SECRET-KEY-1[A-Z0-9]+")
