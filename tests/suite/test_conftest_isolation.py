"""No test module may import a sibling as `conftest`.

pytest imports every conftest.py as the flat top-level module name `conftest`,
so `from conftest import X` resolves to whichever directory pytest imported
first — a second conftest anywhere in the run silently breaks it. Shared
constants belong in a named `<suite>_harness.py` (tests/guards/guard_harness.py
made that rule explicit).

This was a real bug, not a hypothetical: `SCRIPT` is defined by both
tests/clipped and tests/pii_redactor with different values, so a shared
conftest slot let the pii-redactor release-gate tests run against
~/bin/clipped without raising. The AST is parsed rather than grepped so the
rule's own mention of `from conftest import` in prose cannot trip it.
"""

from __future__ import annotations

import ast
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
SCAN_ROOTS = (REPO / "tests", REPO / "tools")


def _python_files():
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        yield from sorted(root.rglob("*.py"))


def _imports_of_conftest(path: pathlib.Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if (node.module or "").rsplit(".", 1)[-1] == "conftest":
                found.append(f"{path.relative_to(REPO)}:{node.lineno}: from {node.module} import ...")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.rsplit(".", 1)[-1] == "conftest":
                    found.append(f"{path.relative_to(REPO)}:{node.lineno}: import {alias.name}")
    return found


def test_no_module_imports_conftest():
    offenders = [hit for path in _python_files() for hit in _imports_of_conftest(path)]
    assert not offenders, (
        "these import a module named `conftest`, which collides with every "
        "other conftest.py in the run — move shared constants into a named "
        "*_harness.py instead:\n" + "\n".join(offenders)
    )
