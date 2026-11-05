"""Every Python file must parse at the interpreter that runs it.

The bug this catches: `ruff format` at a py314 target strips the
parentheses off `except (A, B):` into `except A, B:`. PEP 758 makes
that legal in Python 3.14 and a SyntaxError everywhere older. The
failure is invisible on a 3.14 machine and fatal on any host running
the floor the file declares.

Not hypothetical here. Measured 2026-11-04:

    /usr/bin/python3        -> 3.10.12
    python3 on PATH (mise)  -> 3.14.8

`home/dotfiles/apps/apt/tasks/keyrings.yaml` and `upgrade.yaml` call
`/usr/bin/python3` by absolute path, on purpose: under `become` a
mise or venv python on PATH is not the system one. A deployed Ansible
script formatted on this machine can therefore be unrunnable on this
machine.

Five files carried the form when this test was written:
scripts/check-docs-links.py, scripts/check_merge_gates.py, three
sites in smartparts/python/interactive_setup.py,
tests/merge_gates/test_real_managed.py, and
tools/skill-trust/skill_trust/cli.py.

The floor comes from each file's own declaration, in the convention
the repo already uses (a `# requires-python = ">=X.Y"` header), then
its nearest pyproject, then the lowest deployed floor. A file with
neither is held to the weakest guarantee rather than the strongest.

`tools/skill-trust/tests/test_python_floor.py` already does this for
its own package, proven against incident 5180319. This applies the
same technique to the whole tree instead of reinventing it.
"""

from __future__ import annotations

import ast
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]

# The lowest floor any *deployed* script declares. A deployed file
# with no header is held to this, because an undeclared floor is the
# weakest guarantee, not a licence to use the newest syntax.
FALLBACK_FLOOR = (3, 10)

DECLARATION = re.compile(r'#\s*requires-python\s*=\s*">=\s*(\d+)\.(\d+)')

# Vendored bundles and environments are not our source.
EXCLUDED_PARTS = {
    ".venv",
    ".worktrees",
    "node_modules",
    "__pycache__",
    "site-packages",
    "zim",
}


def _python_files() -> list[pathlib.Path]:
    return [
        path
        for path in sorted(REPO.rglob("*.py"))
        if not EXCLUDED_PARTS & set(path.parts)
    ]


def _nearest_pyproject_floor(
    path: pathlib.Path,
) -> tuple[int, int] | None:
    """requires-python from the nearest pyproject, if it declares one.

    A subproject states its own floor (tools/skill-trust declares
    3.14), and that is the one its code runs under. Judging a 3.14
    tool by a 3.10 script's standard would report a violation no
    interpreter ever hits.

    Files under `home/` get no pyproject floor. They are the deployed
    payload, not project code: Ansible runs them with an absolute
    `/usr/bin/python3`, so the root pyproject's `>=3.14` says nothing
    about the interpreter that executes them. Inheriting it would hide
    exactly the bug this test exists to catch.
    """
    if path.relative_to(REPO).parts[0] == "home":
        return None
    for parent in path.parents:
        candidate = parent / "pyproject.toml"
        if not candidate.is_file():
            continue
        text = candidate.read_text(encoding="utf-8", errors="replace")
        match = re.search(r'requires-python\s*=\s*">=\s*(\d+)\.(\d+)', text)
        if match:
            return int(match.group(1)), int(match.group(2))
        return None
    return None


def _declared_floor(path: pathlib.Path) -> tuple[int, int]:
    """The floor this file runs under.

    Priority: the file's own header, then its nearest pyproject, then
    the lowest deployed floor. The header wins because that is the
    convention `home/bin` scripts already use; they run as whatever
    `python3` the caller has, not under a project environment.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    head = "\n".join(text.splitlines()[:15])
    match = DECLARATION.search(head)
    if match is not None:
        return int(match.group(1)), int(match.group(2))
    project_floor = _nearest_pyproject_floor(path)
    if project_floor is not None:
        return project_floor
    return FALLBACK_FLOOR


def _test_id(path: pathlib.Path) -> str:
    return str(path.relative_to(REPO))


PYTHON_FILES = _python_files()


def test_the_sweep_finds_real_files():
    """A sweep that finds nothing reports clean while checking nothing.

    Two files known to carry the hazard must be in scope, or the
    property below is vacuous.
    """
    known = {
        pathlib.Path("scripts/check-docs-links.py"),
        pathlib.Path("smartparts/python/interactive_setup.py"),
    }
    found = {path.relative_to(REPO) for path in PYTHON_FILES}
    assert known <= found, f"sweep missed {known - found}"
    assert len(PYTHON_FILES) > 50, f"suspiciously few files: {len(PYTHON_FILES)}"


@pytest.mark.parametrize("path", PYTHON_FILES, ids=_test_id)
def test_file_parses_at_its_declared_floor(path: pathlib.Path):
    """Grammar newer than the floor is the failure that ships."""
    floor = _declared_floor(path)
    source = path.read_text(encoding="utf-8", errors="replace")
    try:
        ast.parse(source, feature_version=floor)
    except SyntaxError as exc:
        hint = ""
        if "except" in (exc.text or ""):
            hint = (
                "\nThis is PEP 758 syntax (3.14+). Write it as "
                "`except (A, B):` — the parentheses are required "
                "below 3.14, and `ruff format` strips them when the "
                "target is py314."
            )
        pytest.fail(
            f"{_test_id(path)} does not parse at its declared floor "
            f"{floor[0]}.{floor[1]}: line {exc.lineno}: {exc.msg}{hint}",
            pytrace=False,
        )


def test_feature_version_is_actually_enforced():
    """`ast.parse` without `feature_version` accepts 3.14 anywhere.

    Mutation measured 2026-11-04: dropping the argument left the whole
    sweep green while a payload script carried PEP 758 syntax. The
    parameter is the entire mechanism, so it gets its own assertion
    rather than trusting that the sweep still passes.
    """
    newer = "try:\n    pass\nexcept OSError, ValueError:\n    pass\n"
    with pytest.raises(SyntaxError):
        ast.parse(newer, feature_version=(3, 10))
    ast.parse(newer, feature_version=(3, 14))
