"""Locate and run the per-GPU confirm task from apps/ollama.

Deliberately not conftest.py: every conftest is imported as a top-level
module named `conftest`, so `from conftest import ...` resolves to
whichever one pytest imported first. See the note in
tests/restart_stale/restart_stale_harness.py.
"""

from __future__ import annotations

import os
import pathlib
import subprocess

import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
INSTALL_YAML = REPO / "dotfiles" / "apps" / "ollama" / "tasks" / "install.yaml"
CONFIRM_NAME = "confirm each instance bound the GPU"
REPORT_NAME = "report per-GPU instance state"


def load_tasks() -> list[dict]:
    """The Debian install task list, as Ansible would see it."""
    return yaml.safe_load(INSTALL_YAML.read_text(encoding="utf-8"))


def confirm_task() -> dict:
    """The one confirm task, by name; assert the name is unambiguous."""
    found = [t for t in load_tasks() if CONFIRM_NAME in (t.get("name") or "")]
    assert len(found) == 1, f"expected one {CONFIRM_NAME!r} task, found {len(found)}"
    return found[0]


def confirm_script(item_name: str = "ollama-rocm") -> str:
    """The task's shell script with {{ item.name }} substituted.

    The rendered script is plain bash, so tests run it as-is against a
    stubbed journalctl: the classification lives in this script.
    """
    raw = confirm_task()["ansible.builtin.shell"]
    assert "{{ item.name }}" in raw, "confirm script lost its per-instance substitution"
    return raw.replace("{{ item.name }}", item_name)


def run_confirm(
    script_text: str, journal_log: str, tmp_path: pathlib.Path
) -> subprocess.CompletedProcess:
    """Run the confirm script with journalctl stubbed to journal_log."""
    stubs = tmp_path / "stubs"
    stubs.mkdir(exist_ok=True)
    stub = stubs / "journalctl"
    stub.write_text('#!/bin/sh\nexec cat "$OLLAMA_JOURNAL_FIXTURE"\n', encoding="utf-8")
    stub.chmod(0o755)
    fixture = tmp_path / "journal.log"
    fixture.write_text(journal_log, encoding="utf-8")
    env = dict(os.environ)
    env["PATH"] = f"{stubs}{os.pathsep}{env['PATH']}"
    env["OLLAMA_JOURNAL_FIXTURE"] = str(fixture)
    return subprocess.run(
        ["/bin/bash", "-c", script_text],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
