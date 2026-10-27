"""skill-trust must stay importable at the python floor it declares.

The floor comes from pyproject.toml's requires-python, not a number written
here — the last drift between a written-down number and the declaration left
this test enforcing 3.11 grammar while the formatter maintained 3.14
(5180319 raised the floor because the formatter targets py314 and rewrites
`except (A, B):` to the comma form). Parsing at the declared floor catches
grammar from a NEWER python than the floor — the failure that actually ships
from a host running the floor's own version.
"""

from __future__ import annotations

import ast
import pathlib
import tomllib

import pytest

PACKAGE = pathlib.Path(__file__).resolve().parents[1] / "skill_trust"


def _declared_floor() -> tuple[int, int]:
    """The lower bound of requires-python, as ast's feature_version wants it."""
    pyproject = PACKAGE.parent / "pyproject.toml"
    spec = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"][
        "requires-python"
    ]
    lower = [p.strip()[2:] for p in spec.split(",") if p.strip().startswith(">=")]
    if not lower:
        raise ValueError(f"no lower bound in requires-python: {spec!r}")
    major, minor = lower[0].split(".")
    return int(major), int(minor)


@pytest.mark.parametrize("module", sorted(PACKAGE.glob("*.py")))
def test_module_parses_at_the_declared_floor(module: pathlib.Path):
    try:
        ast.parse(module.read_text(encoding="utf-8"), feature_version=_declared_floor())
    except SyntaxError as exc:
        pytest.fail(
            f"{module.name} does not parse at python "
            f"{'.'.join(map(str, _declared_floor()))} (the declared floor): "
            f"line {exc.lineno}: {exc.msg}"
        )
