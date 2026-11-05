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
    loreai_local_overlay_file: "{registry_root}/answers.yaml"
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
    loreai_local_overlay_file: "{registry_root}/answers.yaml"
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


def effective(output: str) -> str:
    """The loader's effective-answers report line, and only that line.

    Asserting a bare substring over the whole run log is not enough: the
    divergence warning repeats the same `key=value` text, so a broken settle
    chain still matches it. Every answer assertion reads this line.
    """
    for line in output.splitlines():
        # "effective" also appears in the TASK header; the report binds the
        # key=value pairs, so require the telemetry token too.
        if "effective" in line and "telemetry=" in line:
            return line
    raise AssertionError("no effective-answers report in the run log")


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
    line = effective(out)
    assert "telemetry=1" in line
    assert "inference=openrouter" in line
    assert "worker_model=openrouter/z-ai/glm-5.3-flash" in line


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
    assert "worker_model=ollama/qwen3.6:35b" in effective(result.stdout)
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
    line = effective(result.stdout)
    assert "telemetry=1" in line
    assert "inference=openrouter" in line


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


# ── Chain: re-render when the registry is in force (AC #5) ───────────────────


def test_registry_rerender_is_byte_identical(tmp_path) -> None:
    """A second run with the env file present re-renders it unchanged."""
    root = tmp_path / "registry-root"
    write_registry(root, SHARED_REGISTRY)
    env_file = tmp_path / "home" / "env.zsh"
    env_file.parent.mkdir(parents=True, exist_ok=True)

    first = run(tmp_path, chain_play(root, env_file))
    assert first.returncode == 0, first.stdout + first.stderr
    before = env_file.read_text()

    second = run(tmp_path, chain_play(root, env_file))
    assert second.returncode == 0, second.stdout + second.stderr
    assert env_file.read_text() == before, "re-render changed the artifact"
    # The render task ran (it is gated on registry answers, not on absence).
    assert not task_skipped(second.stdout, "loreai: save the answers per machine")


# ── Overlay: the machine tier for a hostname that cannot be committed ───────


OVERLAY = """\
    provisioning:
      loreai:
        worker_model: ollama/qwen3.6:35b
"""


def test_local_overlay_supplies_machine_answers(tmp_path) -> None:
    """A host with no committed key takes its machine tier from the overlay."""
    root = tmp_path / "registry-root"
    write_registry(root, SHARED_REGISTRY)
    (root / "answers.yaml").write_text(textwrap.dedent(OVERLAY))
    result = run(tmp_path, loader_play(root))
    assert result.returncode == 0, result.stdout + result.stderr
    # Overlay beats shared…
    assert "worker_model=ollama/qwen3.6:35b" in effective(result.stdout)
    # …and the divergence is reported loudly.
    assert "overrides the shared answer" in result.stdout


def test_committed_machine_answer_beats_the_overlay(tmp_path) -> None:
    """The committed registry stays authoritative where it speaks."""
    root = tmp_path / "registry-root"
    write_registry(
        root,
        SHARED_REGISTRY
        + """\
    machines:
      pop-os:
        provisioning:
          loreai:
            worker_model: openrouter/z-ai/committed-choice
""",
    )
    (root / "answers.yaml").write_text(textwrap.dedent(OVERLAY))
    result = run(tmp_path, loader_play(root))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "worker_model=openrouter/z-ai/committed-choice" in effective(result.stdout)


def test_malformed_overlay_fails_loud(tmp_path) -> None:
    root = tmp_path / "registry-root"
    write_registry(root, SHARED_REGISTRY)
    (root / "answers.yaml").write_text("provisioning: [unclosed\n")
    result = run(tmp_path, loader_play(root))
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "answers.yaml" in combined
    assert "fix" in combined.lower()


# ── Unknown machine: inherit shared and say so, every run ───────────────────


def test_unknown_machine_is_reported_not_failed(tmp_path) -> None:
    """An unregistered host inherits shared and names itself in the report."""
    root = tmp_path / "registry-root"
    write_registry(
        root,
        SHARED_REGISTRY
        + """\
    machines:
      some-other-box:
        provisioning:
          loreai:
            telemetry: 0
""",
    )
    result = run(tmp_path, loader_play(root))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "No machine entry" in result.stdout
    assert "pop-os" in result.stdout
    # It inherited the shared answers rather than failing.
    assert "telemetry=1" in effective(result.stdout)


# ── The committed registry itself (AC #3/#4) ────────────────────────────────


def test_committed_registry_gives_pop_os_the_installed_answers() -> None:
    """The real machines.yml, resolved for pop-os, matches this box's env.zsh.

    Pins AC #3: a machine entry beats shared, and pop-os's effective answers
    equal the values the machine is actually running with.
    """
    import yaml  # noqa: PLC0415 — optional dep, only this test needs it

    registry = yaml.safe_load((PAYLOAD_ROOT / "dotfiles" / "machines.yml").read_text())
    shared = registry["provisioning"]["shared"]["loreai"]
    machine = registry["machines"]["pop-os"]["provisioning"]["loreai"]
    effective = shared | machine

    assert effective == {
        "telemetry": 1,
        "inference": "openrouter",
        "worker_model": "openrouter/z-ai/glm-5.3-flash",
    }


def test_no_committed_machine_key_fails_the_employer_string_test() -> None:
    """Every machine key in the registry is a plain hostname, never a serial.

    The serial-shaped identifiers this repo has published are long and
    alphanumeric; a hostname is human-readable. This guard is deliberately
    narrow: it rejects the serial shape rather than allowlisting names, so a
    new machine can be added without editing the test.
    """
    import re  # noqa: PLC0415

    import yaml  # noqa: PLC0415

    registry = yaml.safe_load((PAYLOAD_ROOT / "dotfiles" / "machines.yml").read_text())
    serial_shape = re.compile(r"^[A-Z0-9]{10,}$")
    for key in registry.get("machines", {}):
        assert not serial_shape.match(key), (
            f"machine key {key!r} looks like a hardware serial; a hostname "
            "that fails spec.md § Data's string test must not be committed "
            "(use the local overlay instead)"
        )
