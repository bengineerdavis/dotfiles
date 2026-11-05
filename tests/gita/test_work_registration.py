"""Exercise gita registration with isolated HOME and mise state."""

import csv
import json
import os
from pathlib import Path
import shutil
import subprocess

import yaml


REPO_ROOT = Path(__file__).parents[2]
TOPIC = REPO_ROOT / "dotfiles" / "apps" / "gita"
ANSIBLE_PLAYBOOK = shutil.which("ansible-playbook")
assert ANSIBLE_PLAYBOOK is not None, "run the suite with --with ansible-core"


def load_tasks(name):
    return yaml.safe_load((TOPIC / "tasks" / name).read_text())


def test_registration_read_is_context_independent_and_ghost_prune_is_gone():
    tasks = load_tasks("install.yaml")
    slurps = [task for task in tasks if "ansible.builtin.slurp" in task]
    assert len(slurps) == 1
    slurp = slurps[0]
    assert "repos.csv" in slurp["ansible.builtin.slurp"]["src"]
    assert slurp.get("check_mode") is False
    assert slurp["ansible.builtin.slurp"].get("src", "").startswith("{{")
    text = (TOPIC / "tasks" / "install.yaml").read_text()
    assert "b64decode" in text
    assert "splitlines" in text
    assert "gita freeze" not in text
    assert "gita_work_ghost_stats" not in text
    assert "cmd: gita rm" not in text


def test_teardown_drops_the_group_before_uninstalling_gita():
    tasks = load_tasks("remove.yaml")
    commands = [
        task["ansible.builtin.command"]["cmd"]
        for task in tasks
        if "ansible.builtin.command" in task
    ]
    assert commands.count("gita group rm {{ gita_work_group }}") == 1
    assert commands.index("gita group rm {{ gita_work_group }}") < commands.index(
        "mise unuse --global pipx:gita"
    )


def run_isolated_install(
    home: Path,
    check: bool = False,
    fake_bin: Path | None = None,
    seed_repo: bool = True,
):
    code = home / "code"
    work = code / "work"
    repo = work / "local-only"
    repo.mkdir(parents=True)
    if seed_repo:
        subprocess.run(["git", "init", "--quiet"], cwd=repo, check=True)
    catalogue = code / "config" / "repos.yaml"
    catalogue.parent.mkdir()
    catalogue.write_text("repos: []\n")
    (home / ".config" / "mise").mkdir(parents=True)
    (home / ".config" / "gita").mkdir(exist_ok=True)
    (home / ".config" / "gita" / "unrelated.context").write_text("")
    (home / ".config" / "gita" / "groups.csv").write_text("unrelated::\n")
    (home / ".config" / "mise" / "config.toml").write_text(
        '[tools]\n"pipx:gita" = "0.16.8.2"\n'
    )

    env = os.environ.copy()
    env["HOME"] = str(home)
    env["XDG_CONFIG_HOME"] = str(home / ".config")
    env["MISE_TRUSTED_CONFIG_PATHS"] = str(home / ".config" / "mise" / "config.toml")
    if fake_bin is not None:
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
    command = [
        ANSIBLE_PLAYBOOK,
        "apps/gita/playbook.yaml",
        "--tags",
        "install",
        "-e",
        f"gita_catalogue_path={catalogue}",
    ]
    if check:
        command.append("--check")
    return subprocess.run(
        command,
        cwd=REPO_ROOT / "dotfiles",
        env=env,
        capture_output=True,
        text=True,
    )


def read_isolated_groups(home: Path):
    with (home / ".config" / "gita" / "groups.csv").open(newline="") as stream:
        return {
            row["name"]: row["repos"].split()
            for row in csv.DictReader(stream, ["name", "repos", "path"], delimiter=":")
        }


def test_registration_includes_local_only_repos_and_preserves_ghosts(tmp_path):
    work = tmp_path / "code" / "work"
    repo = work / "local-only"
    ghost = work / "removed-repo"
    (tmp_path / ".config" / "gita").mkdir(parents=True)
    with (tmp_path / ".config" / "gita" / "repos.csv").open("a", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow([str(ghost), "removed-repo", "", ""])
        writer.writerow([str(repo), "local-only", "", ""])
    proc = run_isolated_install(tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "local-only" in read_isolated_groups(tmp_path)["work"]
    assert "gita rm" not in proc.stdout
    with (tmp_path / ".config" / "gita" / "repos.csv").open(newline="") as stream:
        registrations = list(csv.reader(stream))
    assert {repo, ghost} == {Path(row[0]) for row in registrations}


def test_check_mode_writes_no_registration_state(tmp_path):
    check = run_isolated_install(tmp_path, check=True)
    assert check.returncode == 0, check.stdout + check.stderr
    assert not (tmp_path / ".config" / "gita" / "repos.csv").exists()
    assert read_isolated_groups(tmp_path) == {"unrelated": []}


def test_spaced_repo_name_reaches_gita_as_one_argument(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    log = tmp_path / "group-arguments.json"
    script = fake_bin / "gita"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        f"with open({str(log)!r}, 'a') as stream:\n"
        "    stream.write(json.dumps(sys.argv[1:]) + '\\n')\n"
    )
    script.chmod(0o755)
    home = tmp_path / "home"
    repo = home / "code" / "work" / "local only"
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "--quiet"], cwd=repo, check=True)
    (home / ".config" / "gita").mkdir(parents=True)
    (home / ".config" / "gita" / "repos.csv").write_text(f"{repo},local only,,\n")
    assert (repo / ".git").is_dir()
    proc = run_isolated_install(home, fake_bin=fake_bin, seed_repo=False)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    calls = [json.loads(line) for line in log.read_text().splitlines()]
    group_add = next(call for call in calls if call[:2] == ["group", "add"])
    assert group_add == ["group", "add", "-n", "work", "local only"], calls


def test_teardown_removes_work_group_before_fake_mise_unuse(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    marker = tmp_path / "mise-called"
    script = fake_bin / "mise"
    script.write_text(
        "#!/bin/sh\n"
        f"test ! -e {tmp_path}/.config/gita/groups.csv || "
        "! grep -q '^work:' "
        f"{tmp_path}/.config/gita/groups.csv || exit 41\n"
        f"touch {marker}\n"
    )
    script.chmod(0o755)
    (tmp_path / ".config" / "gita").mkdir(parents=True)
    (tmp_path / ".config" / "gita" / "groups.csv").write_text("work:local-only:\n")
    (tmp_path / ".config" / "mise").mkdir(parents=True)
    (tmp_path / ".config" / "mise" / "config.toml").write_text("pipx:gita\n")
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)
    env["XDG_CONFIG_HOME"] = str(tmp_path / ".config")
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    result = subprocess.run(
        [
            ANSIBLE_PLAYBOOK,
            "apps/gita/playbook.yaml",
            "--tags",
            "remove",
        ],
        cwd=REPO_ROOT / "dotfiles",
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert marker.exists()
    assert "work" not in read_isolated_groups(tmp_path)


def test_group_add_passes_each_name_as_one_argument():
    tasks = load_tasks("install.yaml")
    group_add = next(
        task
        for task in tasks
        if task["name"].startswith("Install: sweep every work-tree")
    )
    argv = group_add["ansible.builtin.command"]["argv"]
    assert argv == ["gita", "group", "add", "-n", "{{ gita_work_group }}", "{{ item }}"]
    assert group_add["loop"] == "{{ gita_work_names }}"
