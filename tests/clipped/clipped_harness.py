"""Constants shared by the clipped fixtures and tests.

Deliberately not conftest.py: every conftest is imported as a top-level
module named `conftest`, so `from conftest import ...` resolves to whichever
one pytest imported first. With a second conftest anywhere else in the run —
tests/pii_redactor grew one — the clipped tests silently imported the wrong
module. See tests/guards/guard_harness.py, which made this rule explicit.
"""

from __future__ import annotations

import pathlib

SCRIPT = pathlib.Path.home() / "bin" / "clipped"

CLIPBOARD_CONTENT = "clipboard-content"
CAPTURE_NAME = "clipped-copy-capture"
