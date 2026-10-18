"""skill-trust must stay importable at the python floor it declares.

The tool declares requires-python >=3.11, and the box it guards (Debian
bookworm) runs 3.11. The host's 3.14 accepts PEP 758's unparenthesized
except tuples, so a syntax error that only 3.11 sees parses fine here and
ships anyway — measured 2026-10-12: `uv tool install` on the box put the
tool on python 3.11 and every invocation died with "multiple exception
types must be parenthesized". This suite cannot catch that by importing
(host python is 3.14), so it parses every module at the declared floor.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

PACKAGE = pathlib.Path(__file__).resolve().parents[1] / "skill_trust"


@pytest.mark.parametrize("module", sorted(PACKAGE.glob("*.py")))
def test_module_parses_at_the_declared_floor(module: pathlib.Path):
    try:
        ast.parse(module.read_text(encoding="utf-8"), feature_version=(3, 11))
    except SyntaxError as exc:
        pytest.fail(
            f"{module.name} does not parse at python 3.11 "
            f"(the declared floor): line {exc.lineno}: {exc.msg}"
        )
