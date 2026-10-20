"""`topical new` — scaffold correctness, both directions.

The proceed cases prove the generator emits exactly what a manager needs
and nothing it does not; the refuse cases prove it declines loudly
(unknown manager, OS mismatch, overwrite, bad name) rather than
scaffolding something wrong. Generated files are asserted structurally
(parsed YAML) wherever possible, not only as text.
"""

from __future__ import annotations

import shutil
import subprocess

import pytest
import yaml

MARKERS = ("<topic>", "{{ app_name }}", "__MANAGER_BLOCKS__", "__PLAYBOOK_VARS__")


def all_files(dest):
    return [p for p in dest.rglob("*") if p.is_file()]


def assert_no_markers(dest):
    for path in all_files(dest):
        text = path.read_text(encoding="utf-8")
        for marker in MARKERS:
            assert marker not in text, f"{marker!r} left in {path}"


def assert_all_yaml_parses(dest):
    yaml_files = [
        p for p in all_files(dest) if p.suffix in (".yaml", ".yml") and p.stat().st_size
    ]
    assert yaml_files, "no YAML files found — the assertion would be vacuous"
    for path in yaml_files:
        yaml.safe_load(path.read_text(encoding="utf-8"))


# ── Proceed cases ─────────────────────────────────────────────────────


def test_cask_topic_scaffolds_complete(scaffold):
    result, into = scaffold(
        "firefox",
        "--tier",
        "app",
        "--os",
        "Darwin",
        "--requires",
        "homebrew",
        "--manager",
        "homebrew_cask",
    )
    assert result.exit_code == 0, result.output
    dest = into / "apps" / "firefox"

    assert_all_yaml_parses(dest)
    assert_no_markers(dest)

    meta = yaml.safe_load((dest / "topic.yml").read_text())
    assert meta == {
        "topic_name": "firefox",
        "topic_provides": [],
        "topic_requires": ["homebrew"],
        "topic_os": ["Darwin"],
        "topic_tier": "app",
    }

    # install: exactly one live task, the cask block
    tasks = yaml.safe_load((dest / "tasks" / "install.yaml").read_text())
    assert isinstance(tasks, list) and len(tasks) == 1
    assert tasks[0]["community.general.homebrew_cask"]["name"] == "firefox"
    assert tasks[0]["community.general.homebrew_cask"]["state"] == "present"

    # remove mirrors it (CRUD invariant)
    removed = yaml.safe_load((dest / "tasks" / "remove.yaml").read_text())
    assert isinstance(removed, list) and len(removed) == 1
    assert removed[0]["community.general.homebrew_cask"]["state"] == "absent"

    # no residue from the old five-way manager menu
    install_text = (dest / "tasks" / "install.yaml").read_text()
    for residue in (
        "community.general.homebrew:",
        "ansible.builtin.apt:",
        "community.general.snap",
        "community.docker",
    ):
        assert residue not in install_text

    # cask playbook vars spliced in, with the canonical definitions
    playbook = (dest / "playbook.yaml").read_text()
    assert "homebrew_prefix:" in playbook
    assert "user_appdir:" in playbook

    # upgrade guidance names the covering system role
    upgrade = (dest / "tasks" / "upgrade.yaml").read_text()
    assert "apps/homebrew" in upgrade

    # README and CHANGELOG carry the topic name
    assert "# firefox App Module" in (dest / "README.md").read_text()
    assert "# firefox — changelog" in (dest / "CHANGELOG.md").read_text()


def test_formula_topic_has_no_cask_vars_and_no_become(scaffold):
    result, into = scaffold("eza", "--os", "Darwin", "--manager", "homebrew_formula")
    assert result.exit_code == 0, result.output
    dest = into / "apps" / "eza"

    tasks = yaml.safe_load((dest / "tasks" / "install.yaml").read_text())
    assert len(tasks) == 1
    assert tasks[0]["community.general.homebrew"]["name"] == "eza"
    assert "become" not in tasks[0]

    playbook = (dest / "playbook.yaml").read_text()
    assert "user_appdir" not in playbook
    assert "homebrew_prefix" not in playbook
    assert "No playbook vars required" in playbook


def test_apt_topic_on_debian_has_become_and_debian_guard(scaffold):
    result, into = scaffold("clamav", "--os", "Debian", "--manager", "apt")
    assert result.exit_code == 0, result.output
    dest = into / "apps" / "clamav"

    tasks = yaml.safe_load((dest / "tasks" / "install.yaml").read_text())
    assert len(tasks) == 1
    assert tasks[0]["ansible.builtin.apt"]["name"] == "clamav"
    assert tasks[0]["become"] is True
    assert tasks[0]["when"] == "ansible_facts['os_family'] == 'Debian'"


def test_multi_os_topic_uses_the_in_form(scaffold):
    result, into = scaffold(
        "dual", "--os", "Darwin", "--os", "Debian", "--manager", "homebrew_formula"
    )
    assert result.exit_code == 0, result.output
    tasks = yaml.safe_load(
        (into / "apps" / "dual" / "tasks" / "install.yaml").read_text()
    )
    assert tasks[0]["when"] == "ansible_facts['os_family'] in ['Darwin', 'Debian']"


def test_outline_manager_emits_comments_and_no_live_tasks(scaffold):
    result, into = scaffold("ori", "--os", "Darwin", "--manager", "release_artifact")
    assert result.exit_code == 0, result.output
    dest = into / "apps" / "ori"

    install_text = (dest / "tasks" / "install.yaml").read_text()
    assert "OUTLINE" in install_text
    assert "upgraded_by" in install_text or "install, upgrade" in install_text
    # outline-only means comments only — the file parses to None
    assert yaml.safe_load(install_text) is None

    # upgrade guidance warns that the topic must own its upgrade
    upgrade = (dest / "tasks" / "upgrade.yaml").read_text()
    assert "upgraded_by: topic" in upgrade


def test_no_managers_scaffolds_valid_empty_stubs(scaffold):
    result, into = scaffold("ghostty", "--os", "Darwin")
    assert result.exit_code == 0, result.output
    dest = into / "apps" / "ghostty"

    install_text = (dest / "tasks" / "install.yaml").read_text()
    assert "No package managers declared" in install_text
    assert yaml.safe_load(install_text) is None
    assert_all_yaml_parses(dest)
    assert_no_markers(dest)


def test_multi_manager_unions_playbook_vars_once(scaffold):
    result, into = scaffold(
        "combo",
        "--os",
        "Darwin",
        "--manager",
        "homebrew_formula",
        "--manager",
        "homebrew_cask",
    )
    assert result.exit_code == 0, result.output
    dest = into / "apps" / "combo"

    playbook = (dest / "playbook.yaml").read_text()
    assert playbook.count("homebrew_prefix:") == 1
    assert playbook.count("user_appdir:") == 1

    tasks = yaml.safe_load((dest / "tasks" / "install.yaml").read_text())
    assert len(tasks) == 2


def test_generated_topic_passes_ansible_syntax_check(scaffold):
    if not shutil.which("ansible-playbook"):
        pytest.skip("ansible-playbook not on PATH")
    result, into = scaffold("firefox", "--os", "Darwin", "--manager", "homebrew_cask")
    assert result.exit_code == 0, result.output

    # Role paths resolve relative to the CWD (dotfiles/ansible.cfg sets
    # no roles_path), so run from the surrogate repo root holding apps/.
    check = subprocess.run(
        ["ansible-playbook", "apps/firefox/playbook.yaml", "--syntax-check"],
        cwd=into,
        capture_output=True,
        text=True,
    )
    assert check.returncode == 0, check.stderr


def test_repo_discovery_walks_upward(
    runner, topical_module, repo_root, tmp_path, monkeypatch
):
    monkeypatch.chdir(repo_root)
    result = runner.invoke(
        topical_module.app,
        ["new", "discover", "--os", "Darwin", "--into", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    assert (tmp_path / "apps" / "discover" / "topic.yml").exists()


# ── Refuse cases ──────────────────────────────────────────────────────


def test_refuses_overwrite_and_leaves_the_original(scaffold):
    first, into = scaffold("firefox", "--os", "Darwin", "--manager", "homebrew_cask")
    assert first.exit_code == 0, first.output
    marker_file = into / "apps" / "firefox" / "tasks" / "install.yaml"
    before = marker_file.read_text()

    second, _ = scaffold("firefox", "--os", "Darwin", "--manager", "homebrew_formula")
    assert second.exit_code == 1
    assert "already exists" in second.output
    assert marker_file.read_text() == before


def test_unknown_manager_lists_valid_keys(scaffold):
    result, _ = scaffold("thing", "--os", "Darwin", "--manager", "snap")
    assert result.exit_code == 1
    assert "unknown manager" in result.output
    assert "homebrew_formula" in result.output  # the valid keys are named


def test_manager_os_mismatch_names_both_sides(scaffold):
    result, _ = scaffold("thing", "--os", "Darwin", "--manager", "apt")
    assert result.exit_code == 1
    assert "apt" in result.output
    assert "Debian" in result.output  # the manager's OS coverage
    assert "Darwin" in result.output  # the topic's topic_os


def test_reserved_name_rejected(scaffold):
    result, _ = scaffold("new", "--os", "Darwin")
    assert result.exit_code != 0
    assert "reserved" in result.output


def test_bad_name_rejected(scaffold):
    result, _ = scaffold("Firefox", "--os", "Darwin")
    assert result.exit_code != 0


def test_repo_discovery_fails_closed_outside_a_checkout(
    runner, topical_module, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(topical_module.app, ["new", "nowhere", "--os", "Darwin"])
    assert result.exit_code == 1
    assert "no checkout" in result.output
