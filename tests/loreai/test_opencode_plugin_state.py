"""Execute LoreAI's OpenCode task with isolated plugin fixtures.

The structured plugin API distinguishes active and failed plugins.
A config grep or CLI table cannot reliably make that distinction.
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest
import yaml

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

DEFAULT_TASKS = (
    PAYLOAD_ROOT / "dotfiles" / "apps" / "loreai" / "tasks" / "agents" / "opencode.yaml"
)
TASKS = Path(os.environ.get("LOREAI_PLUGIN_TASKS", DEFAULT_TASKS))
ANSIBLE = shutil.which("ansible-playbook")
LOCAL_ANSIBLE = Path(__file__).parents[2] / ".venv" / "bin" / "ansible-playbook"
if ANSIBLE is None and LOCAL_ANSIBLE.is_file():
    ANSIBLE = str(LOCAL_ANSIBLE)
FILTER = Path(
    os.environ.get(
        "LOREAI_PLUGIN_FILTER",
        PAYLOAD_ROOT
        / "dotfiles"
        / "apps"
        / "loreai"
        / "filter_plugins"
        / "json_or_empty.py",
    )
)
FILTER_PATH = str(FILTER.parent)


def test_json_filter_relents_on_malformed_input():
    spec = spec_from_file_location("loreai_json_filter", FILTER)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    parse = module.FilterModule().filters()["json_or_empty"]
    assert parse('{"data": [{"state": {"status": "active"}}]}')["data"]
    for malformed in ("{not-json", "", "<html></html>", None):
        assert parse(malformed) == {}


def test_probe_commands_use_structured_api_and_preserve_install():
    tasks = yaml.safe_load(TASKS.read_text())
    commands = [
        task["ansible.builtin.command"]
        for task in tasks
        if "ansible.builtin.command" in task
    ]
    assert "opencode api get /api/plugin" in commands
    assert "opencode plugin add @loreai/opencode" in commands
    assert not any("opencode plugin list" in command for command in commands)


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _run_state(tmp_path: Path, state: str) -> subprocess.CompletedProcess:
    if ANSIBLE is None:
        raise RuntimeError("ansible-playbook is required for this fixture")
    home = tmp_path / "home"
    config = home / ".config" / "opencode"
    log = home / ".local" / "share" / "opencode" / "log"
    config.mkdir(parents=True)
    log.mkdir(parents=True)
    (config / "opencode.jsonc").write_text('{"plugins":["@loreai/opencode"]}\n')
    (log / "opencode.log").write_text("")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_executable(bin_dir / "npm", "#!/bin/sh\nexit 0\n")

    rows = {
        "active": [
            {
                "id": "lore",
                "source": {"type": "package", "target": "@loreai/opencode"},
                "state": {"status": "active"},
            }
        ],
        "failed": [
            {
                "source": {"type": "package", "target": "@loreai/opencode"},
                "state": {
                    "status": "failed",
                    "error": "Plugin must export a default definition",
                },
            }
        ],
        "unknown": [],
    }
    _write_executable(
        bin_dir / "opencode",
        "#!/bin/sh\n"
        "printf '%s\\n' '"
        + json.dumps({"data": rows.get(state, [])}).replace("'", "'\\''")
        + "'\n",
    )
    if state == "api-error":
        _write_executable(
            bin_dir / "opencode",
            "#!/bin/sh\nprintf 'server unavailable\\n' >&2\nexit 1\n",
        )
    if state == "api-malformed":
        _write_executable(
            bin_dir / "opencode",
            "#!/bin/sh\nprintf '{not-json\\n'\n",
        )
    if state == "install-error":
        (log / "opencode.log").write_text(
            "target=@loreai/opencode NpmInstallFailedError\n"
        )

    playbook = tmp_path / "playbook.yaml"
    playbook.write_text(
        "- hosts: localhost\n"
        "  gather_facts: false\n"
        "  vars:\n"
        "    ansible_env:\n"
        f"      HOME: {home}\n"
        f"      TEST_EXPECT_LOADED: {'1' if state == 'active' else '0'}\n"
        "  tasks:\n"
        f"    - include_tasks: {TASKS}\n"
        "    - assert:\n"
        "        that:\n"
        "          - loreai_opencode_plugin_loaded\n"
        "      when: ansible_env.TEST_EXPECT_LOADED == '1'\n"
        "    - debug: var=loreai_opencode_plugin_cause\n"
    )
    env = os.environ.copy()
    env.update(
        {
            "ANSIBLE_LOCALHOST_WARNING": "0",
            "ANSIBLE_NOCOLOR": "1",
            "ANSIBLE_PYTHON_INTERPRETER": shutil.which("python3") or "python3",
            "ANSIBLE_FILTER_PLUGINS": FILTER_PATH,
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "TEST_EXPECT_LOADED": "1" if state == "active" else "0",
        }
    )
    return subprocess.run(
        [ANSIBLE, str(playbook)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=45,
    )


@pytest.mark.skipif(ANSIBLE is None, reason="ansible-playbook not installed")
@pytest.mark.parametrize(
    "state", ["active", "failed", "unknown", "api-error", "api-malformed"]
)
def test_task_distinguishes_loaded_rejected_and_unknown_states(tmp_path, state):
    result = _run_state(tmp_path, state)
    output = result.stdout + result.stderr
    assert output
    assert result.returncode == 0, output
    if state == "active":
        assert "registered, installed, and loading" in output
        assert "ignored=0" in output
    else:
        assert "ignored=1" in output
    if state == "failed":
        assert "upstream BYK/loreai release" in output
    if state in ["unknown", "api-malformed"]:
        assert "load state could not be determined" in output
    if state == "api-error":
        assert "server unavailable" in output


@pytest.mark.skipif(ANSIBLE is None, reason="ansible-playbook not installed")
def test_task_blocks_on_a_locally_fixable_install_failure(tmp_path):
    result = _run_state(tmp_path, "install-error")
    output = result.stdout + result.stderr
    assert output
    assert result.returncode != 0
    assert "opencode service restart" in output
    assert "failed=1" in output
