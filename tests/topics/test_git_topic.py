"""Git is one fleet prerequisite, not a package installed by every OS path.

The removal tests execute the role's actual remove.yaml. The refusal checks
leave package-manager modules skipped. The relenting check replaces only those
modules in a temporary copy with a fail-if-called marker, proving the guard
opens without changing packages or touching the live machine.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess

import pytest
import yaml

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

DOTFILES = PAYLOAD_ROOT / "dotfiles"
ROLE = DOTFILES / "apps" / "git"


def _tasks(path: pathlib.Path) -> list[dict]:
    loaded = yaml.safe_load(path.read_text())
    assert loaded is None or isinstance(loaded, list), f"invalid task file {path}"
    return loaded or []


def test_git_package_has_one_topic_owner_and_no_duplicate_prerequisite():
    metadata = yaml.safe_load((ROLE / "topic.yml").read_text())
    assert metadata == {
        "topic_name": "git",
        "topic_provides": ["git"],
        "topic_requires": [],
        "topic_os": ["Darwin", "Debian"],
        "topic_tier": "app",
    }
    for manager in ("homebrew", "apt"):
        tasks = _tasks(DOTFILES / "apps" / manager / "tasks" / "prerequisites.yaml")
        packages = {
            package
            for task in tasks
            for module in ("community.general.homebrew", "ansible.builtin.apt")
            for package in (task.get(module, {}).get("name") or [])
            if isinstance(task.get(module, {}).get("name"), list)
        }
        assert "git" not in packages, f"{manager} still owns the Git package"

    consumers = {
        path.parent.name
        for path in (DOTFILES / "apps").glob("*/topic.yml")
        if "git" in (yaml.safe_load(path.read_text()).get("topic_requires") or [])
    }
    assert {"chrome", "gita"} <= consumers


def test_git_package_is_a_fleet_prerequisite_with_os_guards():
    tasks = _tasks(ROLE / "tasks" / "prerequisites.yaml")
    expected = {
        "community.general.homebrew": "ansible_facts['os_family'] == 'Darwin'",
        "ansible.builtin.apt": "ansible_facts['os_family'] == 'Debian'",
    }
    assert len(tasks) == 2
    for module, condition in expected.items():
        task = next(task for task in tasks if module in task)
        assert task[module]["name"] == "git"
        assert task[module]["state"] == "present"
        assert task["when"] == condition
    assert _tasks(ROLE / "tasks" / "install.yaml") == []


def test_lifecycle_routes_remove_only_when_explicit():
    expected = {
        "bootstrap.yaml": ["bootstrap", "provision"],
        "prerequisites.yaml": ["prerequisites", "provision"],
        "upgrade.yaml": ["upgrade", "provision"],
        "install.yaml": ["install", "provision"],
        "remove.yaml": ["remove", "never"],
    }
    imports = {
        task["ansible.builtin.import_tasks"]: task["tags"]
        for task in _tasks(ROLE / "tasks" / "main.yaml")
    }
    assert imports == expected
    for filename in ("bootstrap.yaml", "upgrade.yaml", "install.yaml"):
        assert _tasks(ROLE / "tasks" / filename) == []


def _run_remove(
    tmp_path, extra: dict, *, replacement_module: str | None = None
) -> subprocess.CompletedProcess:
    remove_tasks = _tasks(ROLE / "tasks" / "remove.yaml")
    task_file = ROLE / "tasks" / "remove.yaml"
    if replacement_module:
        task_file = tmp_path / "remove-tasks.yaml"
        for task in remove_tasks:
            for module in ("community.general.homebrew", "ansible.builtin.apt"):
                if module in task:
                    task[replacement_module] = {
                        "msg": "remove-git-package-proof: the guard relented"
                    }
                    del task[module]
        task_file.write_text(yaml.safe_dump(remove_tasks, sort_keys=False))
    harness = tmp_path / "remove.yaml"
    harness.write_text(
        yaml.safe_dump(
            [
                {
                    "hosts": "localhost",
                    "connection": "local",
                    "gather_facts": False,
                    "vars": {
                        "role_path": str(ROLE),
                        "ansible_facts": {"os_family": "Darwin"},
                    },
                    "vars_files": [str(ROLE / "defaults" / "main.yaml")],
                    "tasks": [
                        {"ansible.builtin.import_tasks": str(task_file)},
                        {
                            "name": "Assert no package manager was invoked",
                            "ansible.builtin.assert": {
                                "that": [
                                    "git_remove_report is not defined "
                                    "or git_remove_report.skipped"
                                ]
                            },
                        },
                    ],
                }
            ],
            sort_keys=False,
        )
    )
    env = {
        **os.environ,
        "ANSIBLE_BECOME": "false",
        "ANSIBLE_NOCOLOR": "1",
        "ANSIBLE_LOCALHOST_WARNING": "false",
    }
    return subprocess.run(
        [
            "ansible-playbook",
            "-i",
            "localhost,",
            str(harness),
            "-e",
            json.dumps(extra),
            "-e",
            '{"ansible_become": false}',
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
        check=False,
    )


@pytest.mark.skipif(
    shutil.which("ansible-playbook") is None, reason="ansible-playbook not on PATH"
)
@pytest.mark.parametrize(
    ("extra", "reason"),
    [
        ({"git_remove_package": False}, "opt-in"),
        (
            {
                "git_remove_package": True,
                "ansible_facts": {"os_family": "Darwin"},
            },
            "requires_map",
        ),
        (
            {
                "git_remove_package": True,
                "requires_map": {"git": ["gita"]},
                "ansible_facts": {"os_family": "Darwin"},
            },
            "gita",
        ),
    ],
    ids=["default-off", "missing-index", "required-by-another-topic"],
)
def test_remove_declines_safely(tmp_path, extra, reason):
    result = _run_remove(tmp_path, extra)
    assert result.returncode == 0, result.stdout + result.stderr
    assert reason in result.stdout, result.stdout
    assert "changed=0" in result.stdout


@pytest.mark.skipif(
    shutil.which("ansible-playbook") is None, reason="ansible-playbook not on PATH"
)
def test_remove_keeps_git_on_an_unsupported_os(tmp_path):
    result = _run_remove(
        tmp_path,
        {
            "git_remove_package": True,
            "requires_map": {},
            "ansible_facts": {"os_family": "Unsupported"},
        },
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "changed=0" in result.stdout


@pytest.mark.skipif(
    shutil.which("ansible-playbook") is None, reason="ansible-playbook not on PATH"
)
def test_remove_relents_only_with_opt_in_and_an_empty_dependency_index(tmp_path):
    result = _run_remove(
        tmp_path,
        {
            "git_remove_package": True,
            "requires_map": {},
            "ansible_facts": {"os_family": "Darwin"},
        },
        replacement_module="ansible.builtin.fail",
    )
    assert result.returncode != 0, "the guarded package removal did not relent"
    assert "remove-git-package-proof" in result.stdout + result.stderr
    assert "not os_family" not in result.stdout + result.stderr


def test_dot134_retains_only_git_ai_and_shell_integration():
    task = next((PAYLOAD_ROOT.parent / "backlog" / "tasks").glob("dot-134 -*"))
    description = task.read_text()
    assert "git-ai" in description
    assert "shell integration" in description
    assert "Git config is not managed at all today" not in description
    assert "no `dot_gitconfig` in the source" not in description
