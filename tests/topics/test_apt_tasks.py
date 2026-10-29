"""apps/apt task files, run for real against a throwaway /etc/apt.

retired.yaml and keyrings.yaml are imported into a play under tmp_path with
become forced off and every path redirected into tmp_path, so the tasks run
exactly as written without root and without touching the machine. What this
pins down is the part the Python unit tests cannot: that the regex really
comments a source out, that a second run changes nothing, and that the loop's
changed_when reads each item's own JSON.

The apt purge is skipped (apt_retired_packages: []); purging needs root and is
the apt module's behaviour, not ours.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT
import pytest

ROLE = PAYLOAD_ROOT / "dotfiles" / "apps" / "apt"

pytestmark = pytest.mark.skipif(
    shutil.which("ansible-playbook") is None, reason="ansible-playbook not on PATH"
)

LIST_LINE = (
    "deb [arch=all,amd64 signed-by={kr}] "
    "https://proget.makedeb.org prebuilt-mpr jammy\n"
)


def play(task_file: str) -> str:
    return f"""\
- hosts: localhost
  connection: local
  gather_facts: false
  become: false
  vars:
    role_path: "{ROLE}"
  vars_files:
    - "{ROLE}/defaults/main.yaml"
  tasks:
    - ansible.builtin.import_tasks: "{ROLE}/tasks/{task_file}"
"""


def run(tmp_path, task_file, extra, *flags):
    harness = tmp_path / "harness.yaml"
    harness.write_text(play(task_file))
    env = {**os.environ, "ANSIBLE_BECOME": "false", "ANSIBLE_NOCOLOR": "1"}
    result = subprocess.run(
        [
            "ansible-playbook",
            "-i",
            "localhost,",
            str(harness),
            "-e",
            json.dumps(extra),
            "-e",
            '{"ansible_become": false}',
            *flags,
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=180,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


def recap_changed(output: str) -> int:
    line = next(raw for raw in output.splitlines() if raw.startswith("localhost"))
    return int(line.split("changed=")[1].split()[0])


@pytest.fixture
def retired(tmp_path):
    kr = tmp_path / "prebuilt-mpr-archive-keyring.gpg"
    kr.write_bytes(b"key")
    src = tmp_path / "prebuilt-mpr.list"
    src.write_text(LIST_LINE.format(kr=kr))
    extra = {
        "apt_retired_sources": [
            {"file": str(src), "keyring": str(kr), "reason": "archived upstream"}
        ],
        "apt_retired_packages": [],
    }
    return src, kr, extra


def test_retired_source_is_commented_not_deleted(tmp_path, retired):
    src, kr, extra = retired
    run(tmp_path, "retired.yaml", extra)
    text = src.read_text()
    assert src.exists()
    assert not kr.exists()
    assert text.startswith("# Retired: archived upstream\n")
    assert all(line.startswith("#") for line in text.splitlines() if line.strip())
    assert "https://proget.makedeb.org prebuilt-mpr jammy" in text


def test_retirement_is_idempotent(tmp_path, retired):
    src, _, extra = retired
    run(tmp_path, "retired.yaml", extra)
    first = src.read_text()
    out = run(tmp_path, "retired.yaml", extra)
    assert src.read_text() == first
    assert recap_changed(out) == 0


def test_missing_retired_source_is_not_an_error(tmp_path):
    extra = {
        "apt_retired_sources": [
            {"file": str(tmp_path / "gone.list"), "reason": "never configured here"}
        ],
        "apt_retired_packages": [],
    }
    run(tmp_path, "retired.yaml", extra)
    assert not (tmp_path / "gone.list").exists()


def test_check_mode_retires_nothing(tmp_path, retired):
    src, kr, extra = retired
    before = src.read_text()
    run(tmp_path, "retired.yaml", extra, "--check")
    assert src.read_text() == before
    assert kr.exists()


def test_keyrings_with_no_configured_source_are_ok_and_unchanged(tmp_path):
    # The real apt_keyrings entries, but this box has no such sources configured
    # under tmp_path: the helper reports no-source and must not download.
    # apt_gpg_path points the task's gpg check at a stub so the repair loop
    # runs on machines whose gpg is not at /usr/bin/gpg (macOS).
    stub = tmp_path / "gpg-stub"
    stub.write_text("")
    extra = {
        "apt_gpg_path": str(stub),
        "apt_keyrings": [
            {
                "name": "t",
                "repo_host": "repo.example.invalid",
                "url": "https://repo.example.invalid/key",
            }
        ],
    }
    out = run(tmp_path, "keyrings.yaml", extra)
    assert recap_changed(out) == 0
    # The report task (a debug loop, not the command-module repair loop)
    # prints the helper-derived fields, so "t: no-source" proves the loop
    # ran and the helper saw no configured source — a skipped loop would
    # print only "(item=t)" with no status line. The no-source JSON itself
    # is pinned at helper level by test_apt_source_audit.
    assert "(item=t)" in out
    assert "t: no-source" in out
