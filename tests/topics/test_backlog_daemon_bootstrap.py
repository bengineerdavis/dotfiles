"""apps/backlog's Darwin daemon bootstrap, run for real against launchd.

The task converged only when the label happened to be enabled. `launchctl
disable` writes a PERSISTENT override into the user's launchd domain, so a
label left disabled by any earlier run made every later run fail with
`Bootstrap failed: 5: Input/output error` and leave the daemon down
(DOT-343, measured 2026-11-17). The task's `enable` sat behind `&&` after a
`bootstrap` that could not succeed, so nothing ever cleared the override.

These tests run the task's own command against a throwaway label and a
throwaway plist, so the real backlog daemon is never touched. The rules they
pin:

- the label converges to RUNNING from every state an earlier run can leave
  behind: absent, loaded, disabled-and-absent, and disabled-while-loaded;
- running the command twice in a row stays converged.

The task body is read from install.yaml rather than restated here, so the
test cannot drift from the file it protects.
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import time
import yaml

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT
import pytest

ROLE = PAYLOAD_ROOT / "dotfiles" / "apps" / "backlog"
INSTALL = ROLE / "tasks" / "install.yaml"

pytestmark = pytest.mark.skipif(
    not shutil.which("launchctl"),
    reason="launchctl is macOS-only",
)

UID_NUM = os.getuid()
PLIST_DIR = pathlib.Path.home() / "Library" / "LaunchAgents"


def darwin_bootstrap_command() -> str:
    """The `cmd:` of the task that (re)bootstraps the Darwin daemon.

    Read from install.yaml rather than restated, so the test cannot drift from
    the file it protects. Parsed as YAML, not string-joined: the command is a
    multi-line shell block.
    """
    tasks = yaml.safe_load(INSTALL.read_text())
    task = next(
        candidate
        for candidate in tasks
        if "bootstrap the daemon (Darwin)" in candidate["name"]
    )
    command = task["ansible.builtin.shell"]["cmd"]
    assert command.strip(), "the Darwin bootstrap command is empty"
    return command


def render(command: str, label: str, plist: pathlib.Path) -> str:
    return (
        command.replace("{{ backlog_daemon_label }}", label)
        .replace("{{ backlog_plist_path }}", str(plist))
        .replace("{{ backlog_bin }}", "/bin/sleep")
    )


def write_plist(label: str, path: pathlib.Path) -> None:
    path.write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" \
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>{label}</string>
  <key>ProgramArguments</key><array><string>/bin/sleep</string><string>300</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
</dict></plist>
"""
    )


def loaded(label: str) -> bool:
    return (
        subprocess.run(
            ["launchctl", "print", f"gui/{UID_NUM}/{label}"],
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )


def running(label: str) -> bool:
    """A loaded label that has a pid is actually up, not merely registered."""
    result = subprocess.run(
        ["launchctl", "print", f"gui/{UID_NUM}/{label}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return "pid = " in result.stdout


def settle(label: str, seconds: float = 8.0) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if running(label):
            return
        time.sleep(0.1)


def teardown(label: str, plist: pathlib.Path) -> None:
    """Return the domain to the state a fresh machine has."""
    subprocess.run(
        ["launchctl", "bootout", f"gui/{UID_NUM}/{label}"],
        capture_output=True,
        check=False,
    )
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and loaded(label):
        time.sleep(0.1)
    subprocess.run(
        ["launchctl", "enable", f"gui/{UID_NUM}/{label}"],
        capture_output=True,
        check=False,
    )
    plist.unlink(missing_ok=True)


@pytest.fixture
def daemon(tmp_path, request):
    """A throwaway label and plist, torn down whether the test passes or not."""
    label = f"com.backlog-py.test-{os.getpid()}-{abs(hash(request.node.name)) % 10**6}"
    plist = tmp_path / f"{label}.plist"
    write_plist(label, plist)
    teardown(label, plist)
    write_plist(label, plist)
    yield label, plist
    teardown(label, plist)


def converge(label: str, plist: pathlib.Path) -> subprocess.CompletedProcess[str]:
    command = render(darwin_bootstrap_command(), label, plist)
    return subprocess.run(
        ["bash", "-c", command],
        capture_output=True,
        text=True,
        check=False,
    )


def test_absent_label_starts_the_daemon(daemon):
    label, plist = daemon
    result = converge(label, plist)
    settle(label)
    assert result.returncode == 0, result.stdout + result.stderr
    assert running(label)


def test_an_already_running_label_converges(daemon):
    label, plist = daemon
    converge(label, plist)
    settle(label)
    result = converge(label, plist)
    settle(label)
    assert result.returncode == 0, result.stdout + result.stderr
    assert running(label)


def test_a_disabled_label_converges(tmp_path, request):
    """The DOT-343 bug: `launchctl disable` is persistent, so a run that left
    the label disabled made every later run fail rc 5 with the daemon down.
    """
    label = f"com.backlog-py.test-{os.getpid()}-disabled"
    plist = tmp_path / f"{label}.plist"
    teardown(label, plist)
    write_plist(label, plist)
    try:
        subprocess.run(
            ["launchctl", "disable", f"gui/{UID_NUM}/{label}"],
            capture_output=True,
            check=False,
        )
        result = converge(label, plist)
        settle(label)
        assert running(label), (
            "the daemon did not converge from a disabled label; "
            + result.stdout
            + result.stderr
        )
    finally:
        teardown(label, plist)


def test_a_disabled_but_loaded_label_converges(tmp_path):
    label = f"com.backlog-py.test-{os.getpid()}-disloaded"
    plist = tmp_path / f"{label}.plist"
    teardown(label, plist)
    write_plist(label, plist)
    try:
        converge(label, plist)
        settle(label)
        subprocess.run(
            ["launchctl", "disable", f"gui/{UID_NUM}/{label}"],
            capture_output=True,
            check=False,
        )
        result = converge(label, plist)
        settle(label)
        assert running(label), result.stdout + result.stderr
    finally:
        teardown(label, plist)


def test_two_runs_in_a_row_stay_converged(daemon):
    label, plist = daemon
    first = converge(label, plist)
    settle(label)
    second = converge(label, plist)
    settle(label)
    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 0, second.stdout + second.stderr
    assert running(label)
