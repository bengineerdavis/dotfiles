"""The restart-stale role is called, by the topics that own the processes.

tests/restart_stale/test_role.py proves the role behaves. It cannot prove any
topic CALLS it, and an uncalled check is indistinguishable from a working one
on a machine where nothing happens to be stale — the same gap
tests/guards/test_guard_wiring.py covers for the guards.

Run:
    uv run --with pytest --with pyyaml pytest tests/restart_stale -q
"""

from __future__ import annotations

import pathlib
import re

import pytest

yaml = pytest.importorskip("yaml", reason="pyyaml not installed")

from restart_stale_harness import DOTFILES  # noqa: E402

APPS = DOTFILES / "apps"
ROLE = "roles/restart-stale"


def tasks(path: pathlib.Path) -> list[dict]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or []


def calls(path: pathlib.Path) -> list[tuple[int, dict]]:
    """(position, task) for every import of the role in a task file."""
    return [
        (i, t)
        for i, t in enumerate(tasks(path))
        if (t.get("ansible.builtin.import_role") or {}).get("name") == ROLE
    ]


def only_call(path: pathlib.Path, **match) -> tuple[int, dict]:
    found = [
        (i, t)
        for i, t in calls(path)
        if all(t.get("vars", {}).get(k) == v for k, v in match.items())
    ]
    assert len(found) == 1, f"expected one {match} call in {path}, found {len(found)}"
    return found[0]


def position_of(path: pathlib.Path, name: str) -> int:
    names = [t.get("name") for t in tasks(path)]
    assert name in names, f"{path} no longer has the task {name!r}; update this test"
    return names.index(name)


def test_every_caller_uses_a_static_import():
    """include_role would drop out of tag-filtered runs without an apply:
    block, and --tags upgrade is exactly the run that has to reach it."""
    for path in sorted(APPS.glob("*/tasks/*.yaml")):
        for task in tasks(path):
            for key in ("ansible.builtin.include_role", "include_role"):
                assert (task.get(key) or {}).get("name") != ROLE, (
                    f"{path.relative_to(DOTFILES)} includes {ROLE} dynamically"
                )


def test_every_call_runs_under_upgrade():
    """The binary changes during an upgrade run; a check tagged only
    `install` would miss the run that causes staleness."""
    for path in sorted(APPS.glob("*/tasks/*.yaml")):
        for _, task in calls(path):
            assert "upgrade" in (task.get("tags") or []), (
                f"{path.relative_to(DOTFILES)}: {task.get('name')!r} is not tagged upgrade"
            )


# ── apps/ollama ──────────────────────────────────────────────────────────────

OLLAMA = APPS / "ollama" / "tasks" / "install.yaml"


def test_ollama_checks_its_launchd_agent_last():
    at, call = only_call(OLLAMA, restart_stale_kind="launchd")

    assert call["vars"]["restart_stale_launchd_label"] == "com.ollama.server"
    assert call["when"] == "ansible_facts['os_family'] == 'Darwin'"
    # After the topic's own reload, so a plist change and an upgrade in the
    # same run cost one restart, not two.
    assert at > position_of(OLLAMA, "macOS: (re)load the ollama server agent")


def test_ollama_checks_the_binary_its_agent_runs():
    """The agent's Program and the checked binary must be one expression, or
    the check can judge a file the server never runs."""
    plist = (APPS / "ollama" / "templates" / "com.ollama.server.plist.j2").read_text()
    program = re.search(
        r"<key>ProgramArguments</key>\s*<array>\s*<string>\{\{(.+?)\}\}", plist
    )
    assert program is not None, "the plist lost its ProgramArguments template"
    _, call = only_call(OLLAMA, restart_stale_kind="launchd")

    assert (
        call["vars"]["restart_stale_binary"] == "{{ " + program.group(1).strip() + " }}"
    )


def test_ollama_checks_its_systemd_unit_last():
    at, call = only_call(OLLAMA, restart_stale_kind="systemd")

    assert call["vars"]["restart_stale_systemd_unit"] == "ollama"
    # /etc/systemd/system/ollama.service: a system unit, not a user one.
    assert call["vars"]["restart_stale_systemd_scope"] == "system"
    assert call["vars"]["restart_stale_binary"] == "/usr/bin/ollama"
    assert at > position_of(
        OLLAMA, "ollama (Debian): enable + (re)start ollama service"
    )


def test_ollama_checks_the_binary_its_unit_runs():
    unit = (APPS / "ollama" / "templates" / "ollama.service.j2").read_text()
    exec_start = re.search(r"^ExecStart=(\S+)", unit, re.M)
    assert exec_start is not None, "the unit lost its ExecStart"
    _, call = only_call(OLLAMA, restart_stale_kind="systemd")

    assert call["vars"]["restart_stale_binary"] == exec_start.group(1)


# ── apps/1password ───────────────────────────────────────────────────────────

OP_TASKS = APPS / "1password" / "tasks"
OP_INSTALL = OP_TASKS / "install.yaml"
OP_DEFAULTS = APPS / "1password" / "defaults" / "main.yaml"
CASK = "community.general.homebrew_cask"


def cask_tasks(path: pathlib.Path) -> list[tuple[int, dict]]:
    return [(i, t) for i, t in enumerate(tasks(path)) if CASK in t]


def test_1password_app_lives_in_slash_applications():
    """1Password's own support article requires the app in /Applications for
    browser integration — the documented exception to ~/Applications."""
    assert (
        yaml.safe_load(OP_DEFAULTS.read_text())["onepassword_appdir"] == "/Applications"
    )


def test_1password_cask_adopts_the_existing_app_in_place():
    """Without --adopt, brew refuses because the app is already there; with
    ~/Applications from HOMEBREW_CASK_OPTS it would install a second copy."""
    [(_, task)] = [
        (i, t) for i, t in cask_tasks(OP_INSTALL) if t[CASK]["name"] == "1password"
    ]
    options = task[CASK]["install_options"]

    assert task[CASK]["state"] == "present"
    assert "adopt" in options
    assert "appdir={{ onepassword_appdir }}" in options
    assert "force" not in options, (
        "force would overwrite the app instead of adopting it"
    )


def test_1password_checks_the_app_it_installed():
    at, call = only_call(OP_INSTALL, restart_stale_kind="app")
    [(cask_at, _)] = cask_tasks(OP_INSTALL)

    assert call["vars"]["restart_stale_app_name"] == "1Password"
    assert call["vars"]["restart_stale_binary"] == (
        "{{ onepassword_appdir }}/1Password.app/Contents/MacOS/1Password"
    )
    assert call["when"] == "ansible_facts['os_family'] == 'Darwin'"
    assert at > cask_at


def test_1password_is_not_upgraded_greedily():
    """The cask is auto_updates: 1Password's own updater keeps it current.
    Neither this topic nor the homebrew tier may add brew as a second updater;
    the restart check catches a self-update that left the old process up."""
    for path in [
        *OP_TASKS.glob("*.yaml"),
        APPS / "homebrew" / "tasks" / "upgrade.yaml",
    ]:
        for _, task in cask_tasks(path):
            assert not task[CASK].get("greedy"), (
                f"{path.relative_to(DOTFILES)} upgrades greedily"
            )
        assert "--greedy" not in path.read_text(), (
            f"{path.relative_to(DOTFILES)} passes --greedy"
        )


def test_1password_removes_the_app_only_when_asked():
    defaults = yaml.safe_load(OP_DEFAULTS.read_text())
    [(_, task)] = cask_tasks(OP_TASKS / "remove.yaml")

    assert defaults["onepassword_remove_app"] is False
    assert task[CASK]["state"] == "absent"
    assert "onepassword_remove_app | bool" in task["when"]
    assert "zap" not in str(task[CASK].get("install_options", "")), (
        "zap would delete the vault data under ~/Library"
    )
