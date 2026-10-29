"""Every convention must be reachable from AGENTS.md.

A convention an agent never reads is not a convention; it is a file. AGENTS.md
is the one document every tool loads, so it is the only reliable entry point —
which makes its list of conventions load-bearing rather than decorative.

Lists drift. This repo has already watched a hand-maintained list silently stop
covering a new entry: `apps/ollama/tasks/remove.yaml` had a hand-copied
`launchctl unsetenv` list that missed a newly added variable, which is why
`spec.md` § Layering — teardown changes with the thing it creates exists. This
is the same failure shape applied to documentation, so it gets the same
treatment.
"""

from __future__ import annotations

import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
AGENTS = REPO / "AGENTS.md"
CONVENTIONS = REPO / "docs"

# Reference, research and roadmap documents are linked from the documents
# that need them. The agent-facing conventions index stays intentionally small.
EXEMPT = {
    "AGENT-ARTIFACTS.md",
    "ARCHITECTURE.md",
    "CONTRIBUTING.md",
    "CRUD-AUDIT.md",
    "GOALS.md",
    "JUDGE-SELECTION.md",
    "MODEL-ACCESS.md",
    "MODEL-LIFECYCLE.md",
    "MULTI-MACHINE.md",
    "README.md",
    "ROADMAP-mpm-importer.md",
    "ROADMAP-topic-cli.md",
    "TOPIC-RECIPES.md",
    "USAGE.md",
}


def convention_files() -> list[pathlib.Path]:
    return sorted(p for p in CONVENTIONS.glob("*.md") if p.name not in EXEMPT)


def test_there_are_conventions_to_check():
    """Guards against the whole suite passing vacuously if the directory is
    emptied or renamed.
    """
    assert CONVENTIONS.is_dir(), "docs/ is missing"
    assert convention_files(), "docs/ holds no convention files"


@pytest.mark.parametrize("path", convention_files(), ids=lambda p: p.name)
def test_convention_is_referenced_from_agents_md(path):
    text = AGENTS.read_text(encoding="utf-8")
    assert text.strip(), "AGENTS.md is empty — the check would pass vacuously"
    rel = f"docs/{path.name}"
    assert rel in text, (
        f"{rel} is not referenced from AGENTS.md, so an agent has no path to it. "
        f"Add a bullet under § Conventions."
    )


def payload_root() -> pathlib.Path:
    """Resolve the chezmoi payload independently of pytest's import aliases."""
    return REPO / (REPO / ".chezmoiroot").read_text().strip()


def test_payload_readme_local_links_resolve():
    """Relative links resolve from the README, not the repository root."""
    import re

    readme = payload_root() / "dotfiles" / "README.md"
    targets = re.findall(r"\[[^]]+\]\(([^)]+)\)", readme.read_text())
    local_targets = [
        target.partition("#")[0]
        for target in targets
        if not target.startswith(("#", "/")) and "://" not in target
    ]
    assert local_targets, "README has no local links — the check would be vacuous"
    for target in local_targets:
        assert (readme.parent / target).is_file(), (
            f"Broken local link in {readme.relative_to(REPO)}: {target}"
        )


def test_agents_md_does_not_reference_a_missing_convention():
    """The other direction: a bullet pointing at a file that was renamed or
    deleted sends an agent to read something that is not there.
    """
    import re

    text = AGENTS.read_text(encoding="utf-8")
    # Anchored so it does not also match the tail of `docs/...`,
    # which is a different tree and legitimately holds other documents.
    referenced = set(re.findall(r"(?<![\w/])docs/([A-Za-z0-9_.-]+\.md)", text))
    assert referenced, "AGENTS.md references no conventions at all"
    for name in sorted(referenced):
        assert (CONVENTIONS / name).exists(), (
            f"AGENTS.md points at docs/{name}, which does not exist"
        )
