"""The enforced baseline and the readable table are one list.

`AGENTS.md` § Known failures is the readable copy of which suites fail on a
clean checkout; `scripts/check_suite_baseline.py` EXPECTED_FAILURES is the
enforced one. Two hand-maintained copies of one meaning drift — DOT-73 fixed
every clipped failure and left both stale at once, each waiting for its own
editor. This test makes the drift a red suite instead of a landmine: edit the
table in a PR, and this fails until EXPECTED_FAILURES follows.
"""

from __future__ import annotations

import importlib.util
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]
AGENTS = REPO / "AGENTS.md"
BASELINE = REPO / "scripts" / "check_suite_baseline.py"

TABLE_ROW = re.compile(r"^\| `(?P<suite>[^`]+)` \| (?P<count>[~\d]+) \|", re.MULTILINE)


def load_baseline() -> frozenset[str]:
    spec = importlib.util.spec_from_file_location("check_suite_baseline", BASELINE)
    assert spec is not None, f"{BASELINE} did not yield an import spec"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module.EXPECTED_FAILURES  # type: ignore[attr-defined]


def tabled_suites() -> dict[str, str]:
    """The AGENTS.md § Known failures table: suite -> its claimed count.

    The table is the readable copy — a suite name and a count, not a full
    node-ID inventory. The enforced list holds the node IDs; this holds the
    claims the enforced tally must reproduce.
    """
    text = AGENTS.read_text()
    section = re.search(
        r"^### Known failures(.*?)(?=^### |\Z)", text, re.MULTILINE | re.DOTALL
    )
    assert section, "AGENTS.md has no § Known failures section"
    return dict(TABLE_ROW.findall(section.group(1)))


def test_every_expected_failure_lives_in_a_tabled_suite() -> None:
    """A node ID in a suite the table does not name is a silent baseline."""
    tabled = set(tabled_suites())
    for nodeid in load_baseline():
        suite = "/".join(pathlib.PurePosixPath(nodeid).parts[:2])
        assert suite in tabled, (
            f"{nodeid} is enforced but its suite {suite} is not in the "
            "AGENTS.md § Known failures table — add the suite to the table "
            "or remove the node ID from EXPECTED_FAILURES"
        )


def test_the_tables_counts_match_the_enforced_tally() -> None:
    """The table's per-suite count is the enforced list's per-suite tally."""
    tally: dict[str, int] = {}
    for nodeid in load_baseline():
        suite = "/".join(pathlib.PurePosixPath(nodeid).parts[:2])
        tally[suite] = tally.get(suite, 0) + 1
    for suite, count in tabled_suites().items():
        claimed = count.lstrip("~")
        enforced = tally.get(suite, 0)
        assert str(enforced) == claimed, (
            f"AGENTS.md § Known failures says {suite} has {claimed} failures; "
            f"EXPECTED_FAILURES holds {enforced}. The two copies drifted — "
            "update them together in the same change"
        )
