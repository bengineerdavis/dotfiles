"""The governance documents must never deploy into $HOME.

Written because this trap sprang five times in a single session: spec.md,
PRD.md, ROADMAP.md, PYTHON.md and then conventions/ each had to be added to
.chezmoiignore by hand, and each was caught only because someone happened to
read `chezmoi status` before applying. Nothing enforced it.

The failure is quiet in the worst way. chezmoi would write AGENTS.md, PRD.md and
the rest into the home directory, where they are meaningless — and an apply that
does it reports success. There is no error to notice.

This asks chezmoi what it MANAGES rather than what it ignores. The first
version of this test used `chezmoi ignored` and failed on docs/PYTHON.md
— wrongly. An ignored directory is pruned whole, so `chezmoi ignored` reports
`conventions` and never enumerates the files under it. Managed is the property
that actually matters anyway: a path chezmoi does not manage is a path it cannot
write to $HOME, whatever the ignore syntax happens to look like.

Parsing .chezmoiignore directly would be worse still — a test that reimplemented
the matcher would agree with itself while chezmoi disagreed.
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

# The five documents that govern the project, plus the conventions directory.
# RESOURCES.md is deliberately absent: it IS a deployed dotfile. TASKS.md was
# the fifth until the backlog-md-py cutover deleted it (2026-10-26); the
# queue now lives in backlog/, which IS committed but must still never
# deploy — it is covered by the dot-prefix rule like .worktrees/, asserted
# in tests/backlog.
GOVERNANCE = ["AGENTS.md", "PRD.md", "ROADMAP.md", "spec.md"]
# Not a whole directory any more: docs/ mixes repository conventions (which must
# not deploy) with dotfiles documentation (which must). Named files only.
GOVERNANCE_FILES_IN_DOCS = [
    "docs/PERMISSIONS.md",
    "docs/PYTHON.md",
    "docs/REFERENCES.md",
    "docs/README.md",
    "docs/LANGUAGES.md",
    "docs/GLOSSARY.md",
    "docs/WORKTREES.md",
    # A changelog is a governance artefact, not a dotfile. Both of these were
    # managed when first added and would have landed in $HOME.
    "CHANGELOG.md",
]
GOVERNANCE_DIRS = ["scripts/", "tools/"]

# Project files at the root — not governance docs, but must not deploy either.
PROJECT_FILES = ["pyproject.toml", "uv.lock"]

pytestmark = pytest.mark.skipif(
    shutil.which("chezmoi") is None, reason="chezmoi not installed"
)


@pytest.fixture(scope="module")
def managed() -> set[str]:
    # -S targets the source dir, which is the payload seam; the docs probed
    # below are repo-only trees and stay on REPO.
    out = subprocess.run(
        ["chezmoi", "-S", str(PAYLOAD_ROOT), "managed"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert out.returncode == 0, f"chezmoi managed failed: {out.stderr}"
    paths = {ln.strip() for ln in out.stdout.splitlines() if ln.strip()}
    assert len(paths) > 100, (
        f"chezmoi managed returned only {len(paths)} paths — too few to be real, "
        "and the checks below would pass vacuously"
    )
    return paths


@pytest.mark.parametrize("doc", GOVERNANCE)
def test_governance_doc_is_not_deployed(managed, doc):
    assert (REPO / doc).exists(), f"{doc} is missing from the repo entirely"
    assert doc not in managed, (
        f"{doc} would be written to $HOME by `chezmoi apply`. "
        f"Add it to .chezmoiignore under the dev-tooling block."
    )


@pytest.mark.parametrize("d", GOVERNANCE_DIRS)
def test_governance_dir_contents_are_not_deployed(managed, d):
    files = [p for p in (REPO / d).rglob("*") if p.is_file()]
    assert files, f"{d}/ is empty — the check would pass vacuously"
    for f in files:
        rel = str(f.relative_to(REPO))
        assert rel not in managed, (
            f"{rel} would be written to $HOME. Note a bare '{d}/' in "
            f".chezmoiignore does not cover contents; '{d}/**' is also needed."
        )


@pytest.mark.parametrize("path", GOVERNANCE_FILES_IN_DOCS)
def test_convention_in_docs_is_not_deployed(managed, path):
    """docs/ is a deployed tree, so moving conventions into it put them one
    .chezmoiignore line away from landing in $HOME.
    """
    assert (REPO / path).exists(), f"{path} is missing from the repo"
    assert path not in managed, f"{path} would be written to $HOME"


def test_dotfiles_documentation_still_deploys(managed):
    """The relenting direction for the same directory: ignoring docs/ wholesale
    would have been the easy fix and would have stopped shipping the docs that
    are meant to ship.
    """
    assert "docs/ARCHITECTURE.md" in managed, (
        "docs/ARCHITECTURE.md stopped deploying — the ignore rules are too broad"
    )


def test_a_real_dotfile_is_still_deployed(managed):
    """The relenting direction. Ignore rules broad enough to catch everything
    would make the tests above pass while deploying nothing at all.
    """
    assert "dotfiles/zsh/aliases.zsh" in managed, (
        "a genuinely deployed file is not managed — the ignore rules are too broad"
    )


@pytest.mark.parametrize("path", PROJECT_FILES)
def test_project_files_are_not_deployed(managed, path):
    """Root project files would be found by uv and pytest from anywhere under
    $HOME if deployed. The failure is silent — no error, just wrong config.
    """
    assert (REPO / path).exists(), f"{path} is missing from the repo"
    assert path not in managed, f"{path} would be written to $HOME"
