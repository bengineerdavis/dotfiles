"""apps/gita's work-tree reconciliation, run for real in a throwaway HOME.

The work-tree block is the part of the topic that discovery drives rather than
a declared catalogue, so the failures worth pinning are the ones a reader of
the YAML cannot see:

- the recursive walk must skip vendored dot-directories (`.venv`,
  `node_modules`) — `gita add -r` globs `**/`, which does not match a leading
  dot, and that claim is easy to "fix" by accident;
- the group sweep must be what completes the group, because the walk reports
  "No new repos found!" for a repo that is already registered without a group;
- a machine with no work tree must skip the whole block without failing.

Everything runs against a real `gita` in a temporary HOME, so gita's own CSVs
are written to a throwaway directory. Nothing touches the author's `~/code`.

`gita` is required; the test skips with the install command when it is absent,
because a silent skip is how a broken check stays broken.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import textwrap

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT
import pytest

ROLE = PAYLOAD_ROOT / "dotfiles" / "apps" / "gita"

pytestmark = [
    pytest.mark.skipif(
        shutil.which("ansible-playbook") is None,
        reason="ansible-playbook not on PATH — run: mise install",
    ),
    pytest.mark.skipif(
        shutil.which("gita") is None,
        reason="gita not on PATH — run: mise use -g pipx:gita && mise install",
    ),
]


def _play(extra_vars: dict) -> str:
    """A play that imports install.yaml's work-tree tasks in a throwaway HOME."""
    return textwrap.dedent(
        f"""\
        - hosts: localhost
          connection: local
          gather_facts: false
          become: false
          vars:
            role_path: "{ROLE}"
            ansible_facts:
              env:
                HOME: "{{{{ lookup('env', 'HOME') }}}}"
          vars_files:
            - "{ROLE}/defaults/main.yaml"
          tasks:
            - ansible.builtin.import_tasks: "{ROLE}/tasks/work-tree.yaml"
              vars: {json.dumps(extra_vars)}
        """
    )
    """A throwaway HOME with gita's config dir, so no real state is touched."""
    home = tmp_path / "home"
    (home / ".config").mkdir(parents=True)
    return home


def _home(tmp_path):
    """A throwaway HOME with gita's config dir, so no real state is touched."""
    home = tmp_path / "home"
    (home / ".config").mkdir(parents=True)
    return home


def _git_repo(path, remote):
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(
        ["git", "-C", str(path), "remote", "add", "origin", remote], check=True
    )
    return path


def _run(tmp_path, home, extra_vars):
    harness = tmp_path / "harness.yaml"
    harness.write_text(_play(extra_vars))
    env = {
        **os.environ,
        "HOME": str(home),
        "ANSIBLE_BECOME": "false",
        "ANSIBLE_NOCOLOR": "1",
    }
    return subprocess.run(
        ["ansible-playbook", "-i", "localhost,", str(harness)],
        capture_output=True,
        text=True,
        env=env,
        timeout=240,
        check=False,
    )


def _task_block(stdout: str, task_name: str) -> str:
    """The lines a single task printed, from its TASK header to the next one.

    Slicing between two named tasks is not enough: the range picks up the skip
    markers of every task that follows, so a guard removed from the walk still
    looked skipped. The block ends at the next TASK header, which is the only
    reliable boundary.
    """
    lines = stdout.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("TASK [") and task_name in line:
            block: list[str] = []
            for following in lines[index + 1 :]:
                if following.startswith("TASK ["):
                    break
                block.append(following)
            return "\n".join(block)
    raise AssertionError(f"task not found in output: {task_name}")


def _gita_names(home) -> list[str]:
    result = subprocess.run(
        ["gita", "ls"],
        capture_output=True,
        text=True,
        env={**os.environ, "HOME": str(home)},
        check=False,
    )
    return result.stdout.split()


def _group_members(home) -> set[str]:
    freeze = subprocess.run(
        ["gita", "freeze"],
        capture_output=True,
        text=True,
        env={**os.environ, "HOME": str(home)},
        check=False,
    ).stdout
    for line in freeze.splitlines():
        fields = line.split(",")
        # Group rows are `,<group>,,<name> <name>`.
        if fields[:1] == [""] and len(fields) >= 4 and fields[3]:
            # gita writes group members pipe-separated (`,work,,proj-a|proj-b`);
            # older versions space-separated them, so accept both.
            return set(fields[3].replace("|", " ").split())
    return set()


@pytest.fixture
def work_tree(tmp_path):
    """A work root with two real repos and one vendored repo inside a dot-dir."""
    home = _home(tmp_path)
    root = home / "code" / "work"
    _git_repo(root / "proj-a", "https://example.com/proj-a.git")
    _git_repo(root / "proj-b", "https://example.com/proj-b.git")
    _git_repo(
        root / "proj-a" / ".venv" / "lib" / "vendored",
        "https://example.com/vendored.git",
    )
    return home, root


def test_the_walk_registers_repos_and_skips_vendored_trees(tmp_path, work_tree):
    home, root = work_tree
    result = _run(
        tmp_path, home, {"gita_work_root": str(root), "gita_work_group": "work"}
    )
    assert result.returncode == 0, result.stdout + result.stderr

    names = _gita_names(home)
    assert "proj-a" in names
    assert "proj-b" in names
    # A leading-dot directory is not matched by `**/`, so a vendored tree
    # inside .venv is never registered.
    assert "vendored" not in names


def test_the_sweep_completes_the_group_for_a_pre_registered_repo(tmp_path, work_tree):
    """The walk skips an already-registered repo; only the sweep groups it.

    This is the case that makes step 2 load-bearing. A repo added by hand
    without a group makes the walk report "No new repos found!", so nothing
    but the sweep puts it in the group.
    """
    home, root = work_tree
    subprocess.run(
        ["gita", "add", str(root / "proj-b")],
        check=True,
        env={**os.environ, "HOME": str(home)},
        capture_output=True,
    )
    assert _group_members(home) == set(), "proj-b should start ungrouped"

    result = _run(
        tmp_path, home, {"gita_work_root": str(root), "gita_work_group": "work"}
    )
    assert result.returncode == 0, result.stdout + result.stderr

    members = _group_members(home)
    assert {"proj-a", "proj-b"} <= members, members


def test_reconciling_twice_is_stable(tmp_path, work_tree):
    home, root = work_tree
    extra = {"gita_work_root": str(root), "gita_work_group": "work"}

    assert _run(tmp_path, home, extra).returncode == 0
    first = sorted(_gita_names(home))
    assert _run(tmp_path, home, extra).returncode == 0
    assert sorted(_gita_names(home)) == first


def test_a_machine_with_no_work_tree_skips_without_failing(tmp_path):
    """A personal-only machine has no ~/code/work and must not error.

    The guard matters beyond avoidance of an error: without it the walk runs
    against a path that does not exist, and `gita add -r` fails with
    `failed_when: false`, so the failure is swallowed and the run looks
    identical. Asserting the skip marker is what distinguishes "declined on
    purpose" from "ran and quietly failed".
    """
    home = _home(tmp_path)
    result = _run(
        tmp_path,
        home,
        {
            "gita_work_root": str(home / "code" / "work"),
            "gita_work_group": "work",
        },
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "work reconciliation is skipped" in result.stdout
    # The walk must be skipped, not attempted-and-swallowed: with the guard
    # removed, `gita add -r` fails against a missing path and `failed_when:
    # false` hides it, so the recap looks identical.
    walk = _task_block(
        result.stdout, "Install: register repos that appeared under the work root"
    )
    assert "skipping: [localhost]" in walk, walk
    assert _gita_names(home) == []
