"""Harness for exercising a shared guard in isolation.

A guard is imported by a topic, but testing it *through* a topic would run that
topic's real work — `apps/opencode` would shell out to `npx @sentry/dotagents`,
hit the network, and rewrite `~/.agents`. So these tests import the guard role
on its own, into a throwaway play, pointed at synthetic directories under
`tmp_path`. Nothing outside `tmp_path` is read or written.

Run:
    pytest tests/guards -v
"""

from __future__ import annotations

import json
import shutil
import subprocess

import pytest

from guard_harness import DOTFILES, GUARDS, HARNESS, said  # noqa: F401

@pytest.fixture(scope="session")
def ansible_playbook() -> str:
    exe = shutil.which("ansible-playbook")
    if not exe:
        pytest.skip("ansible-playbook not on PATH — run: mise install")
    return exe


@pytest.fixture
def run_guard(ansible_playbook, tmp_path):
    """Run one guard file with the given vars; return the CompletedProcess.

    `cwd` is the dotfiles root deliberately: the role is named by the path
    `roles/guards`, exactly as the parent playbook names topics `apps/<topic>`,
    and both resolve relative to the working directory. Running from anywhere
    else is the failure this reproduces rather than papers over.
    """

    def _run(tasks_from: str = "dotagents-skills-migration.yaml",
             gather_facts: bool = False,
             **extra_vars) -> subprocess.CompletedProcess:
        play = tmp_path / "harness.yaml"
        play.write_text(
            HARNESS.format(
                gather=str(gather_facts).lower(), tasks_from=tasks_from
            ),
            encoding="utf-8",
        )
        return subprocess.run(
            [
                ansible_playbook,
                "-i", "localhost,",
                str(play),
                "-e", json.dumps(extra_vars),
            ],
            cwd=DOTFILES,
            capture_output=True,
            text=True,
            timeout=180,
        )

    return _run


@pytest.fixture
def scope(tmp_path):
    """A synthetic dotagents user scope: an install dir and one agent home.

    Mirrors the real shape — `<agent home>/skills` is what dotagents relocates
    into `<home>/.agents/skills` — without needing either to exist on this
    machine.
    """

    class Scope:
        def __init__(self) -> None:
            self.root = tmp_path / "scope"
            self.agents_skills = self.root / ".agents" / "skills"
            self.agent_home = self.root / ".claude"
            self.agent_skills = self.agent_home / "skills"

        def install(self, *names: str) -> None:
            """Names dotagents has already put in ~/.agents/skills."""
            for name in names:
                (self.agents_skills / name).mkdir(parents=True, exist_ok=True)

        def agent_dir(self, *names: str) -> None:
            """An agent skills/ that is still a REAL directory."""
            self.agent_skills.mkdir(parents=True, exist_ok=True)
            for name in names:
                (self.agent_skills / name).mkdir(exist_ok=True)

        def agent_symlink(self) -> None:
            """The managed state: agent skills/ already points at the install dir."""
            self.agents_skills.mkdir(parents=True, exist_ok=True)
            self.agent_home.mkdir(parents=True, exist_ok=True)
            self.agent_skills.symlink_to(self.agents_skills)

        @property
        def vars(self) -> dict:
            return {
                "guard_agents_skills_dir": str(self.agents_skills),
                "guard_agent_homes": [str(self.agent_home)],
                "guard_caller": "tests/guards",
            }

        def snapshot(self) -> list[tuple[str, str]]:
            """Every entry under the scope, as (relative path, kind)."""
            out = []
            for p in sorted(self.root.rglob("*")):
                kind = "link->" + str(p.readlink()) if p.is_symlink() else (
                    "dir" if p.is_dir() else "file"
                )
                out.append((str(p.relative_to(self.root)), kind))
            return out

    return Scope()
