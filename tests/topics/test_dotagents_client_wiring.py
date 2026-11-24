"""dotagents client wiring tolerates an absent CLI and still fails loudly.

The topic wires the dotagents-local marketplace into each agent CLI. The clients
are machine-local: `claude` comes from apps/claude-code, which is Darwin-only
(Debian is DOT-141, open), and codex has no topic at all. Before this, the
wiring assumed every client was installed, so a Debian run died at
`claude plugin marketplace add` and then reported "nothing on stderr" — because
`ansible.builtin.command` reports a MISSING BINARY as rc 2 with empty stderr and
the reason in `msg` (measured 2026-11-09).

Both directions are pinned here, because a guard that only declines passes a
smoke test exactly like one that never runs:

- absent client  -> wiring skipped, the run completes, the report names it
- installed client failing for a real reason -> the run FAILS, and the message
  carries what the client actually said
- installed client with its flag off -> reported as declined, and not invoked

The task text is read from the real install.yaml and sliced to the wiring block,
so these tests run the shipped code rather than a copy of it. A copy would keep
passing after the real file was changed back.
"""

from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import shutil
import subprocess

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT
import pytest
import yaml

ROLE = PAYLOAD_ROOT / "dotfiles" / "apps" / "dotagents"
INSTALL = ROLE / "tasks" / "install.yaml"
FILTERS = ROLE / "filter_plugins"
FILTER = FILTERS / "client_said.py"

# The wiring block: from the marketplace lookup through codex's failure gate.
# Named by task, so inserting an unrelated task between them does not silently
# drop it from the slice.
BLOCK_START = "Find the dotagents plugin marketplace"
BLOCK_END = "Fail with every dotagents plugin codex could not install"

pytestmark = pytest.mark.skipif(
    shutil.which("ansible-playbook") is None, reason="ansible-playbook not on PATH"
)

# Resolved once: the harness gives the play a deliberately narrow PATH (so a
# real mise shim cannot make the probe see a client this machine has), and that
# narrow PATH would otherwise hide the interpreter's own ansible-playbook.
ANSIBLE = shutil.which("ansible-playbook") or "ansible-playbook"

MARKETPLACE = {
    "name": "dotagents-local",
    "owner": {"name": "dotagents"},
    "plugins": [{"name": "mattpocock-skills", "source": "./mattpocock-skills"}],
}


def wiring_tasks() -> list[dict]:
    """The shipped client-wiring tasks, read from the real task file."""
    tasks = yaml.safe_load(INSTALL.read_text()) or []
    names = [t.get("name") for t in tasks]
    assert BLOCK_START in names, f"{BLOCK_START!r} not in install.yaml — renamed?"
    assert BLOCK_END in names, f"{BLOCK_END!r} not in install.yaml — renamed?"
    return tasks[names.index(BLOCK_START) : names.index(BLOCK_END) + 1]


def fake_cli(path: pathlib.Path, *, install_stdout: str, install_rc: int) -> None:
    """A client binary that records its invocations and answers as told."""
    path.write_text(
        "#!/bin/sh\n"
        f'marker="{path}.calls"\n'
        'echo "$*" >> "$marker"\n'
        'if [ "$1" = plugin ] && [ "$2" = marketplace ]; then\n'
        '  echo "Successfully added marketplace: dotagents-local"\n'
        "  exit 0\n"
        "fi\n"
        f'echo "{install_stdout}"\n'
        f"exit {install_rc}\n"
    )
    path.chmod(0o755)


@pytest.fixture
def harness(tmp_path):
    """Build a throwaway HOME plus a play holding the shipped wiring tasks."""
    home = tmp_path / "home"
    (home / ".agents" / "plugins").mkdir(parents=True)
    (home / ".agents" / "plugins" / "marketplace.json").write_text(
        json.dumps(MARKETPLACE)
    )
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    play = tmp_path / "play.yaml"
    play.write_text(
        yaml.safe_dump(
            [
                {
                    "hosts": "localhost",
                    "connection": "local",
                    "gather_facts": True,
                    "become": False,
                    "vars_files": [str(ROLE / "defaults" / "main.yaml")],
                    "tasks": wiring_tasks(),
                }
            ],
            sort_keys=False,
        )
    )

    def run(**vars_):
        env = {
            "HOME": str(home),
            # Only the fakes and the core utilities: a real mise shim would
            # make the probe see a client this machine happens to have.
            "PATH": f"{bin_dir}:/usr/bin:/bin",
            "ANSIBLE_FILTER_PLUGINS": str(FILTERS),
            "ANSIBLE_NOCOLOR": "1",
            "ANSIBLE_LOCALHOST_WARNING": "False",
            "ANSIBLE_INVENTORY_UNPARSED_WARNING": "False",
        }
        extra = []
        for key, value in vars_.items():
            extra += ["-e", f"{key}={value}"]
        return subprocess.run(
            [ANSIBLE, "-i", "localhost,", str(play), *extra],
            capture_output=True,
            text=True,
            env={**os.environ, **env},
            cwd=tmp_path,
        )

    return home, bin_dir, run


def test_absent_clients_are_skipped_and_the_run_completes(harness):
    """The Debian case: neither CLI installed, and the topic still succeeds."""
    home, bin_dir, run = harness
    result = run()

    assert result.returncode == 0, result.stdout + result.stderr
    assert "claude is absent" in result.stdout
    assert "codex is absent" in result.stdout
    # Nothing was half-invoked: the report must match what ran.
    assert not (bin_dir / "claude.calls").exists()


def test_a_present_client_is_wired(harness):
    """The relenting direction: an installed client still gets its plugin."""
    home, bin_dir, run = harness
    fake_cli(
        bin_dir / "claude",
        install_stdout="Successfully installed plugin",
        install_rc=0,
    )
    result = run()

    assert result.returncode == 0, result.stdout + result.stderr
    assert "claude is wired" in result.stdout
    calls = (bin_dir / "claude.calls").read_text()
    assert "plugin marketplace add" in calls
    assert "plugin install mattpocock-skills@dotagents-local" in calls


def test_a_present_client_failing_on_stdout_fails_the_run_and_says_why(harness):
    """`claude plugin install` reports a refusal on STDOUT, not stderr.

    This is the assertion the old stderr-only message could not satisfy: it
    would have printed the generic "nothing on stderr" and hidden "Aborted.".
    """
    home, bin_dir, run = harness
    fake_cli(bin_dir / "claude", install_stdout="Aborted.", install_rc=1)
    result = run()

    assert result.returncode != 0, result.stdout
    assert "Aborted." in result.stdout
    assert "nothing on stderr" not in result.stdout


def test_a_missing_binary_is_reported_by_msg_not_stderr(tmp_path):
    """Rename defence: a vanished binary names itself instead of saying nothing.

    This is the exact shape that produced the original bug: the command module
    answers a missing binary with rc 2, EMPTY stderr, and the reason in `msg`.
    The old stderr-only message printed "nothing on stderr" here.
    """
    play = tmp_path / "missing.yaml"
    play.write_text(
        yaml.safe_dump(
            [
                {
                    "hosts": "localhost",
                    "connection": "local",
                    "gather_facts": False,
                    "become": False,
                    "tasks": [
                        {
                            "name": "call a binary that does not exist",
                            "ansible.builtin.command": {
                                "cmd": (
                                    "dotagents-absent-client plugin"
                                    " marketplace add /nope"
                                ),
                            },
                            "register": "probe_result",
                            "failed_when": False,
                        },
                        {
                            "name": "render the message the way install.yaml does",
                            "ansible.builtin.fail": {
                                "msg": "{{ [probe_result]"
                                " | map('client_said', 'FALLBACK')"
                                " | join(' | ') }}"
                            },
                        },
                    ],
                }
            ],
            sort_keys=False,
        )
    )
    result = subprocess.run(
        [ANSIBLE, "-i", "localhost,", str(play)],
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "ANSIBLE_FILTER_PLUGINS": str(FILTERS),
            "ANSIBLE_NOCOLOR": "1",
            "ANSIBLE_LOCALHOST_WARNING": "False",
        },
        cwd=tmp_path,
    )

    assert result.returncode != 0
    assert "Error executing command." in result.stdout
    assert "FALLBACK" not in result.stdout


def test_declining_an_installed_client_is_reported_as_declined_not_absent(harness):
    """A deliberate opt-out must not read as 'not installed'."""
    home, bin_dir, run = harness
    fake_cli(
        bin_dir / "claude",
        install_stdout="Successfully installed plugin",
        install_rc=0,
    )
    result = run(dotagents_wire_claude="false")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "claude is declined" in result.stdout
    assert not (bin_dir / "claude.calls").exists(), "declined client was invoked"


# ── The message filter ───────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def client_said():
    spec = importlib.util.spec_from_file_location("client_said", FILTER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load client_said.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.client_said


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        # A missing binary: stderr is empty, the reason is in msg.
        (
            {"rc": 2, "stderr": "", "stdout": "", "msg": "Error executing command."},
            "Error executing command.",
        ),
        # A refusal explained on stdout.
        (
            {
                "rc": 1,
                "stderr": "",
                "stdout": "Aborted.",
                "msg": "non-zero return code",
            },
            "Aborted.",
        ),
        # A real stderr line wins over both.
        ({"rc": 1, "stderr": "boom", "stdout": "noise", "msg": "non-zero"}, "boom"),
        # Whitespace-only fields are not an explanation.
        ({"rc": 1, "stderr": "  \n", "stdout": "\t", "msg": ""}, None),
    ],
)
def test_client_said_prefers_the_field_that_explains(client_said, result, expected):
    fallback = "FALLBACK"
    said = client_said(result, fallback)
    assert said == (fallback if expected is None else expected)
