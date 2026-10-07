"""The BATS hooks fire on staged shell scripts at either payload root.

The payload moves from the repo root (`bin/`) under `home/` via
`.chezmoiroot` (TASKS.md § Planned, payload move, step 3). Both gate
surfaces must accept the script root in either layout, or a staged
script silently skips its tests in whichever layout the regex misses:
the bats hook's `files` pattern in .pre-commit-config.yaml, and the
staged-file grep in scripts/run-bats.sh.
"""

from __future__ import annotations

import pathlib
import re

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
PRE_COMMIT = REPO / ".pre-commit-config.yaml"
RUN_BATS = REPO / "scripts" / "run-bats.sh"

# A staged script at the script root in today's layout, in the post-move
# layout, and a repo-tooling script (scripts/ is root-level in both).
FIRES = ["bin/triage.sh", "home/bin/triage.sh", "scripts/check.sh"]


def pre_commit_files_pattern() -> re.Pattern[str]:
    """The bats hook's `files` regex, parsed from the real config."""
    config = yaml.safe_load(PRE_COMMIT.read_text(encoding="utf-8"))
    hooks = [h for repo in config["repos"] for h in repo.get("hooks", [])]
    assert hooks, "no hooks parsed from .pre-commit-config.yaml"
    bats = [h for h in hooks if h.get("id") == "bats"]
    assert len(bats) == 1, "expected exactly one bats hook"
    assert "files" in bats[0], "bats hook lost its files pattern"
    return re.compile(bats[0]["files"])


def run_bats_greps() -> tuple[re.Pattern[str], re.Pattern[str]]:
    """The staged-file filter and runner exclusion greps, in order."""
    text = RUN_BATS.read_text(encoding="utf-8")
    found = re.findall(r"grep -(?:v)?E '([^']+)'", text)
    assert len(found) == 2, f"expected filter + exclude greps, saw {found}"
    return re.compile(found[0]), re.compile(found[1])


def staged_by_run_bats(path: str) -> bool:
    """Mirror scripts/run-bats.sh's two-grep staged-file decision."""
    filt, exclude = run_bats_greps()
    return bool(filt.search(path)) and not exclude.search(path)


@pytest.mark.parametrize("path", FIRES, ids=["bin", "home-bin", "scripts"])
def test_bats_hook_files_pattern_matches_script_roots(path):
    """Staged scripts at either root pass the hook's files gate."""
    assert pre_commit_files_pattern().search(path)


@pytest.mark.parametrize(
    "path",
    ["binfoo/triage.sh", "home/dot_zshrc", "tests/foo.bats"],
    ids=["bin-prefix", "non-bin-payload", "tests"],
)
def test_bats_hook_files_pattern_ignores_other_paths(path):
    """Paths outside bin/, home/bin/ and scripts/ stay out."""
    assert not pre_commit_files_pattern().search(path)


@pytest.mark.parametrize("path", FIRES, ids=["bin", "home-bin", "scripts"])
def test_run_bats_staged_grep_matches_script_roots(path):
    """The staged-file grep picks up both layouts' script roots."""
    assert staged_by_run_bats(path)


@pytest.mark.parametrize(
    "path",
    [
        "scripts/run-bats.sh",
        "scripts/run-shellharden.sh",
        "home/bin/subdir/deep.sh",
    ],
    ids=["runner", "shellharden", "nested"],
)
def test_run_bats_staged_grep_ignores_other_paths(path):
    """Never tests itself, its helper, or nested payload dirs.

    The nested case pins the pre-existing one-level shape (`[^/]+`
    in the grep) — unchanged by this step, but a conscious change
    if it goes.
    """
    assert not staged_by_run_bats(path)
