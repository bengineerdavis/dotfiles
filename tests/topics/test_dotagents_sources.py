"""The global ADHD sources and their measured projection boundary.

Run:
    uv run --frozen pytest tests/topics/test_dotagents_sources.py -q
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import tomllib

import pytest

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT
import yaml

REPO = PAYLOAD_ROOT.parent
TOPIC = PAYLOAD_ROOT / "dotfiles" / "apps" / "dotagents"

# The manifest-projection tests shell out to ansible-playbook, which CI does not
# install (`uv sync --frozen --group test` carries no ansible). Skip there rather
# than fail, matching tests/topics/test_apt_tasks.py. A machine that *has* a
# broken ansible still fails these, on purpose: that is a real signal, not a skip.
needs_ansible = pytest.mark.skipif(
    shutil.which("ansible-playbook") is None,
    reason="ansible-playbook not on PATH",
)


def _defaults() -> dict:
    return yaml.safe_load((TOPIC / "defaults" / "main.yaml").read_text())


def _source(source: str) -> dict:
    matches = [s for s in _defaults()["dotagents_sources"] if s["source"] == source]
    assert len(matches) == 1, f"expected one declaration for {source}"
    return matches[0]


def _plugins() -> list[dict]:
    return _defaults().get("dotagents_plugin_targets", [])


def _tasks(name: str) -> list[dict]:
    tasks = yaml.safe_load((TOPIC / "tasks" / f"{name}.yaml").read_text())
    assert isinstance(tasks, list)
    return tasks


@pytest.mark.parametrize("source", ["UditAkhourii/adhd", "ayghri/i-have-adhd"])
def test_adhd_source_is_approved_with_verifiable_evidence(source: str):
    entry = _source(source)
    assert entry["exclude"] == []
    for phrase in ("MIT", "verified", "canonical"):
        assert phrase in entry["why"]
    if source.startswith("Udit"):
        assert "parallel Agent calls" in entry["why"]


def test_plugin_targets_exclude_copilot_without_disabling_it_globally():
    assert "copilot" in _defaults()["dotagents_agents"]
    entries = _plugins()
    assert len(entries) == 1
    entry = entries[0]
    assert entry["name"] == "i-have-adhd"
    assert entry["source"] == "ayghri/i-have-adhd"
    assert entry["targets"] == ["claude", "cursor", "codex", "opencode"]


def test_install_declares_targets_before_refreshing_the_sources():
    tasks = _tasks("install")
    declarations = [
        i
        for i, task in enumerate(tasks)
        if task.get("ansible.builtin.import_tasks") == "plugin-targets.yaml"
    ]
    sync = [
        i
        for i, task in enumerate(tasks)
        if task.get("name") == "Sync every skill and plugin from each approved source"
    ]
    assert len(declarations) == 1, "install must declare only the named target lists"
    assert len(sync) == 1
    assert declarations[0] < sync[0]
    projection = _tasks("plugin-targets")
    edits = [
        task["ansible.builtin.blockinfile"]
        for task in projection
        if isinstance(task.get("ansible.builtin.blockinfile"), dict)
    ]
    assert len(edits) == 1
    assert edits[0]["path"] == "{{ ansible_facts['env']['HOME'] }}/.agents/agents.toml"
    assert edits[0]["marker"] == "# {mark} ANSIBLE MANAGED PLUGIN TARGETS"
    assert "[[plugins]]" in edits[0]["block"]
    assert "for plugin in dotagents_plugin_targets" in edits[0]["block"]
    assert "name = {{ plugin.name | to_json }}" in edits[0]["block"]
    assert edits[0]["create"] == (
        "{{ dotagents_plugin_target_state == 'present' "
        "and dotagents_plugin_targets | length > 0 }}"
    )
    assert _defaults()["dotagents_plugin_target_state"] == "present"


def test_teardown_covers_the_targeted_declaration():
    tasks = _tasks("remove")
    imports = [
        task
        for task in tasks
        if task.get("ansible.builtin.import_tasks") == "plugin-targets.yaml"
    ]
    assert len(imports) == 1
    assert imports[0]["vars"]["dotagents_plugin_target_state"] == "absent"
    assert "dotagents_remove_skills | bool" in imports[0]["when"]
    assert imports[0]["vars"] == {"dotagents_plugin_target_state": "absent"}
    assert "dotagents_plugin_target_state" in str(_tasks("plugin-targets"))


def test_documentation_records_the_measured_boundary():
    readme = (TOPIC / "README.md").read_text()
    assert "opencode-only" not in readme
    for phrase in (
        "targets",
        "hooks/hooks.json",
        ".opencode/plugins",
        "always-on",
        "2026-11-15",
    ):
        assert phrase in readme
    assert "does not link" in " ".join(readme.split())


def test_topics_keep_corrections_and_authoritative_references():
    text = (REPO / "docs" / "TOPICS.md").read_text()
    assert "Keep topic knowledge current" in text
    assert "verified correction" in text
    assert "upstream" in text
    assert "skill" in text


@needs_ansible
@pytest.mark.parametrize("ansible_playbook", ["ansible-playbook"])
def test_manifest_projection_preserves_foreign_declarations(
    ansible_playbook: str, tmp_path: pathlib.Path
):
    """Exercise the real projection against synthetic dotagents-owned TOML."""
    executable = shutil.which(ansible_playbook)
    if executable is None:
        raise AssertionError("ansible-playbook is required; run mise install")

    home = tmp_path / "home"
    agents = home / ".agents"
    agents.mkdir(parents=True)
    manifest = agents / "agents.toml"
    original = """version = 1
agents = [ "claude", "cursor", "codex", "vscode", "opencode", "copilot" ]

[trust]
github_repos = [ "owner/other" ]

[[plugins]]
name = "foreign-plugin"
source = "owner/other"
targets = [ "copilot" ]

[[skills]]
name = "foreign-skill"
source = "owner/other"
"""
    manifest.write_text(original)
    play = tmp_path / "projection.yaml"
    play.write_text(
        """- hosts: localhost
  connection: local
  gather_facts: true
  tasks:
    - name: use the real role defaults
      ansible.builtin.include_vars: DEFAULTS
    - name: include the real projection
      ansible.builtin.include_tasks: TASKS
""".replace("TASKS", str(TOPIC / "tasks" / "plugin-targets.yaml")).replace(
            "DEFAULTS", str(TOPIC / "defaults" / "main.yaml")
        )
    )

    def run_play() -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [executable, "-i", "localhost,", str(play)],
            cwd=PAYLOAD_ROOT / "dotfiles",
            env={**os.environ, "HOME": str(home)},
            capture_output=True,
            text=True,
            timeout=120,
        )

    result = run_play()
    assert result.returncode == 0, result.stdout + result.stderr
    projected = manifest.read_text()
    assert 'name = "foreign-plugin"' in projected
    assert 'name = "foreign-skill"' in projected
    assert 'targets = [ "copilot" ]' in projected
    assert [p["name"] for p in tomllib.loads(projected)["plugins"]].count(
        "i-have-adhd"
    ) == 1

    second = run_play()
    assert second.returncode == 0, second.stdout + second.stderr
    assert manifest.read_text() == projected
    assert "changed=0" in second.stdout, second.stdout

    parsed = tomllib.loads(projected)
    plugin = next(p for p in parsed["plugins"] if p["name"] == "i-have-adhd")
    assert plugin["targets"] == ["claude", "cursor", "codex", "opencode"]
    assert "copilot" not in plugin["targets"]

    removal = play.read_text().replace(
        "    - name: include the real projection",
        "    - name: include the real projection\n"
        "      vars:\n"
        "        dotagents_plugin_target_state: absent",
    )
    play.write_text(removal)
    removed = run_play()
    assert removed.returncode == 0, removed.stdout + removed.stderr
    final = tomllib.loads(manifest.read_text())
    assert "i-have-adhd" not in [p["name"] for p in final["plugins"]]
    assert "foreign-plugin" in [p["name"] for p in final["plugins"]]
    assert "foreign-skill" in [s["name"] for s in final["skills"]]


@needs_ansible
@pytest.mark.parametrize("ansible_playbook", ["ansible-playbook"])
def test_empty_projection_cannot_create_a_manifest(
    tmp_path: pathlib.Path, ansible_playbook: str
):
    executable = shutil.which(ansible_playbook)
    if executable is None:
        raise AssertionError("ansible-playbook is required; run mise install")

    home = tmp_path / "home"
    home.mkdir()
    manifest = home / ".agents" / "agents.toml"
    play = tmp_path / "empty.yaml"
    play.write_text(
        f"""- hosts: localhost
  connection: local
  gather_facts: true
  vars:
    dotagents_plugin_targets: []
    dotagents_plugin_target_state: present
  tasks:
    - ansible.builtin.include_tasks: {TOPIC / "tasks" / "plugin-targets.yaml"}
"""
    )
    result = subprocess.run(
        [executable, "-i", "localhost,", str(play)],
        cwd=PAYLOAD_ROOT / "dotfiles",
        env={**os.environ, "HOME": str(home)},
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert not manifest.exists()
