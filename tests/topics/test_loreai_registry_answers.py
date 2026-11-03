"""The loreai provisioning-answers registry: decision-1 wired into the topic.

Two harnesses:

- Loader tests import apps/loreai/tasks/registry-answers.yaml directly against
  a fake machines.yml under a fake registry root. The loader is keyed on
  ansible_hostname: absent file = empty merge, malformed YAML fails loud.
- Chain tests include_role the topic's prompts.yaml (role context, so the
  env template resolves) with the registry present and TERM=dumb, asserting
  the full precedence — -e > machine answer > shared answer > prompt >
  probe default — by the rendered env file and by which settle tasks skip.

The registry suppressing prompts without a TTY is itself an assertion: with
both tiers populated the fail-fast guard must not fire and the env file must
render from registry values alone.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import textwrap

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT
import pytest

ROLE = PAYLOAD_ROOT / "dotfiles" / "apps" / "loreai"
TASKS = ROLE / "tasks"
APPS = PAYLOAD_ROOT / "dotfiles" / "apps"

pytestmark = pytest.mark.skipif(
    shutil.which("ansible-playbook") is None, reason="ansible-playbook not on PATH"
)


def write_registry(root: pathlib.Path, body: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "machines.yml").write_text(textwrap.dedent(body))


def loader_play(registry_root: pathlib.Path) -> str:
    return f"""\
- hosts: localhost
  connection: local
  gather_facts: false
  become: false
  vars:
    role_path: "{ROLE}"
    loreai_registry_dir: "{registry_root}"
    ansible_hostname: pop-os
  tasks:
    - ansible.builtin.import_tasks: "{TASKS}/registry-answers.yaml"
"""


def chain_play(registry_root: pathlib.Path, env_file: pathlib.Path) -> str:
    """prompts.yaml under full role context; the registry dir is overridden."""
    return f"""\
- hosts: localhost
  connection: local
  gather_facts: true
  become: false
  vars:
    loreai_registry_dir: "{registry_root}"
    ansible_hostname: pop-os
    loreai_env_file: "{env_file}"
  tasks:
    - ansible.builtin.include_role:
        name: loreai
        tasks_from: prompts.yaml
"""


def run(
    tmp_path: pathlib.Path,
    play_text: str,
    extra: dict | None = None,
) -> subprocess.CompletedProcess:
    harness = tmp_path / "harness.yaml"
    harness.write_text(play_text)
    env = {**os.environ, "ANSIBLE_NOCOLOR": "1", "TERM": "dumb"}
    env["ANSIBLE_ROLES_PATH"] = str(APPS)
    return subprocess.run(
        [
            "ansible-playbook",
            "-i",
            "localhost,",
            str(harness),
            "-e",
            json.dumps(extra or {}),
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=180,
        check=False,
    )


def task_skipped(output: str, task_name: str) -> bool:
    """True when the named task reported skipping.

    task_name is the full name as written in the tasks file, e.g.
    "loreai: ask about operational telemetry" — rendered output prefixes
    it with the role name ("TASK [loreai : loreai: ...]").
    """
    lines = output.splitlines()
    for i, line in enumerate(lines):
        if f"loreai : {task_name}" in line:
            tail = "\n".join(lines[i + 1 : i + 4])
            return "skipping:" in tail
    raise AssertionError(f"task not found in output: {task_name}")


SHARED_REGISTRY = """\
    provisioning:
      shared:
        loreai:
          telemetry: 1
          inference: openrouter
          worker_model: openrouter/z-ai/glm-5.3-flash
"""

# ── Loader: absent registry = empty merge ────────────────────────────────────


def test_absent_registry_leaves_facts_unset(tmp_path) -> None:
    root = tmp_path / "registry-root"
    result = run(tmp_path, loader_play(root))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Registry answers in force" not in result.stdout


# ── Loader: shared answers populate the facts ────────────────────────────────


def test_shared_answers_set_the_facts(tmp_path) -> None:
    root = tmp_path / "registry-root"
    write_registry(root, SHARED_REGISTRY)
    result = run(tmp_path, loader_play(root))
    assert result.returncode == 0, result.stdout + result.stderr
    out = result.stdout
    assert "effective" in out
    assert "telemetry=1" in out
    assert "inference=openrouter" in out
    assert "worker_model=openrouter/z-ai/glm-5.3-flash" in out


# ── Loader: machine answer overrides shared ──────────────────────────────────


def test_machine_answer_beats_shared(tmp_path) -> None:
    root = tmp_path / "registry-root"
    write_registry(
        root,
        SHARED_REGISTRY
        + """\
    machines:
      pop-os:
        provisioning:
          loreai:
            worker_model: ollama/qwen3.6:35b
""",
    )
    result = run(tmp_path, loader_play(root))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "worker_model=ollama/qwen3.6:35b" in result.stdout
    # The divergence is reported loudly (decision-1).
    assert "overrides the shared answer" in result.stdout


# ── Loader: unknown machine gets shared only ─────────────────────────────────


def test_unknown_machine_gets_shared_only(tmp_path) -> None:
    root = tmp_path / "registry-root"
    write_registry(
        root,
        """\
    provisioning:
      shared:
        loreai:
          telemetry: 1
          inference: openrouter
    machines:
      other-box: {}
""",
    )
    result = run(tmp_path, loader_play(root))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "telemetry=1" in result.stdout
    assert "inference=openrouter" in result.stdout


# ── Loader: malformed registry fails loud ────────────────────────────────────


def test_malformed_registry_fails_loud(tmp_path) -> None:
    root = tmp_path / "registry-root"
    write_registry(root, "provisioning: [unclosed\n")
    result = run(tmp_path, loader_play(root))
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "machines.yml" in combined
    assert "fix" in combined.lower()


# ── Chain: registry alone answers everything, no prompts, env rendered ──────


def test_registry_answers_suppress_prompts_and_render(tmp_path) -> None:
    root = tmp_path / "registry-root"
    write_registry(root, SHARED_REGISTRY)
    env_file = tmp_path / "home" / "env.zsh"
    env_file.parent.mkdir(parents=True, exist_ok=True)
    result = run(tmp_path, chain_play(root, env_file))
    assert result.returncode == 0, result.stdout + result.stderr
    # TERM=dumb and env absent: without the registry this run fails fast.
    assert "needs first-install answers" not in result.stdout
    assert task_skipped(result.stdout, "loreai: ask about operational telemetry")
    assert task_skipped(
        result.stdout, "loreai: ask where background workers should run"
    )
    # The rendered artifact carries the registry values.
    rendered = env_file.read_text()
    assert "SENTRY_ENABLED=1" in rendered
    assert 'LORE_WORKER_MODEL="openrouter/z-ai/glm-5.3-flash"' in rendered


# ── Chain: -e beats the registry ─────────────────────────────────────────────


def test_explicit_extra_vars_beat_the_registry(tmp_path) -> None:
    root = tmp_path / "registry-root"
    write_registry(root, SHARED_REGISTRY)
    env_file = tmp_path / "home" / "env.zsh"
    env_file.parent.mkdir(parents=True, exist_ok=True)
    result = run(
        tmp_path,
        chain_play(root, env_file),
        {"loreai_telemetry": 0},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    # The registry settle skipped (its var was already set by -e)…
    assert task_skipped(result.stdout, "loreai: settle telemetry from the registry")
    # …and the rendered artifact carries the -e value, not the registry's.
    assert "SENTRY_ENABLED=0" in env_file.read_text()
