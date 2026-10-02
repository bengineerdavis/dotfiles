"""Harness for exercising roles/topic-resolution in isolation.

The role is imported on its own into a throwaway play under `tmp_path`, with
`cwd` set to the dotfiles root so the path `roles/topic-resolution` resolves
exactly as the parent playbook names it. Nothing outside `tmp_path` is read or
written, and the real `playbook.yaml` is never invoked — the role's inputs
(`resolution_topic_metadata`, `resolution_os_family`) are supplied directly,
synthetic or real.

Run:
    pytest tests/topic_resolution -v
"""

from __future__ import annotations

import json
import shutil
import subprocess

import pytest

from topic_resolution_harness import DISCOVERY_HARNESS, DOTFILES, HARNESS


@pytest.fixture(scope="session")
def ansible_playbook() -> str:
    exe = shutil.which("ansible-playbook")
    if not exe:
        pytest.skip("ansible-playbook not on PATH — run: mise install")
    return exe


def _invoke(
    ansible_playbook, tmp_path, harness, extra_vars
) -> subprocess.CompletedProcess:
    play = tmp_path / "harness.yaml"
    play.write_text(harness, encoding="utf-8")
    return subprocess.run(
        [
            ansible_playbook,
            "-i",
            "localhost,",
            str(play),
            "-e",
            json.dumps(extra_vars),
        ],
        cwd=DOTFILES,
        capture_output=True,
        text=True,
        timeout=180,
    )


@pytest.fixture
def run_role(ansible_playbook, tmp_path):
    """Run the resolver with synthetic host facts; return the CompletedProcess.

    `resolution_topic_metadata` (a list of topic dicts) and
    `resolution_os_family` (a string) are passed straight through as extra vars.
    """

    def _run(**extra_vars) -> subprocess.CompletedProcess:
        return _invoke(ansible_playbook, tmp_path, HARNESS, extra_vars)

    return _run


@pytest.fixture
def run_real(ansible_playbook, tmp_path):
    """Run the resolver against the real apps/*/topic.yml metadata.

    The play performs the same discovery the parent playbook does, then imports
    the role with `resolution_os_family` supplied via -e.
    """

    def _run(os_family: str) -> subprocess.CompletedProcess:
        return _invoke(
            ansible_playbook,
            tmp_path,
            DISCOVERY_HARNESS,
            {"topic_apps_dir": str(DOTFILES), "resolution_os_family": os_family},
        )

    return _run
