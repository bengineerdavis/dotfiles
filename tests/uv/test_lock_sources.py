"""Committed uv lock files must reference public PyPI only.

A work machine that re-locks against its private mirror would leak the
employer-identifying index URL into git (spec.md § Data; the 2026-09-24
skill-trust re-lock incident is the precedent). Fail-closed: any other host
fails the suite and names the fix.
"""

from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]
LOCKS = [REPO / "uv.lock", REPO / "tools" / "skill-trust" / "uv.lock"]
ALLOWED = {"pypi.org", "files.pythonhosted.org"}


def test_committed_locks_reference_public_pypi_only():
    offenders: list[str] = []
    for lock in LOCKS:
        if not lock.exists():  # a renamed or moved lock is not a pass
            offenders.append(f"{lock.relative_to(REPO)}: MISSING")
            continue
        # Every URL in the file, not one key's format: uv.lock writes indexes
        # as `registry = "..."` and artifacts as bare wheel/sdist URLs. A
        # format-specific regex here grepped nothing and passed meaninglessly
        # (caught 2026-10-01 by injecting a leak the old regex never saw).
        for m in re.finditer(
            r'https?://([^"\'\s)]+)', lock.read_text(encoding="utf-8")
        ):
            host = m.group(1).split("/")[0]
            if host not in ALLOWED:
                offenders.append(f"{lock.relative_to(REPO)}: {host}")
    assert not offenders, (
        "a committed uv lock references a non-public index — never commit a "
        "work-machine re-lock; regenerate against public PyPI (uv lock with "
        "the private env unset, or always `uv run --frozen`):\n" + "\n".join(offenders)
    )
