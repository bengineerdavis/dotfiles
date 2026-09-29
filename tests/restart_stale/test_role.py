"""roles/restart-stale end to end, against stub supervisors.

tests/restart_stale/test_decision.py proves the decision. This proves the
wiring around it: that the role finds the process the way each supervisor
reports it, hands start time and ctime to the decision the right way round,
restarts only when stale, uses the restart each kind calls for, and never
force-quits an app that declines to quit.

Both directions are tested for every kind. A role that restarts always and a
role that restarts correctly look the same on a machine where everything is
stale; a role that never restarts and a correct one look the same where nothing
is. Only both directions together distinguish them.

Run:
    uv run --with pytest --with hypothesis pytest tests/restart_stale -q
"""

from __future__ import annotations

import os
import sys
import time

import pytest
from restart_stale_harness import said

darwin_only = pytest.mark.skipif(
    sys.platform != "darwin", reason="launchd and app kinds are macOS-only by design"
)
HOUR = 3600
UID = str(os.getuid())


def ok(result):
    assert result.returncode == 0, result.stdout + result.stderr
    return result


# ── launchd ──────────────────────────────────────────────────────────────────

LABEL = "com.example.server"


def launchd(machine, run_role, *, started_offset: float | None, flags=()):
    """Run the role for a launchd agent started `started_offset` seconds after
    the binary's ctime (negative: before). None: loaded but not running."""
    binary = machine.binary()
    if started_offset is None:
        machine.state["launchd"] = {LABEL: "-"}
    else:
        machine.state["launchd"] = {LABEL: 4242}
        machine.process(4242, machine.ctime(binary) + started_offset, str(binary))
    return run_role(
        *flags,
        restart_stale_kind="launchd",
        restart_stale_launchd_label=LABEL,
        restart_stale_binary=str(binary),
    )


@darwin_only
def test_launchd_stale_agent_is_kickstarted(machine, run_role):
    result = ok(launchd(machine, run_role, started_offset=-HOUR))

    assert machine.calls("launchctl")[-1] == [
        "launchctl",
        "kickstart",
        "-k",
        f"gui/{UID}/{LABEL}",
    ]
    assert said(result, "RESTARTED because pid 4242 started")


@darwin_only
def test_launchd_fresh_agent_is_left_alone(machine, run_role):
    result = ok(launchd(machine, run_role, started_offset=+HOUR))

    assert not [c for c in machine.calls("launchctl") if "kickstart" in c]
    assert said(result, "not restarted: pid 4242 started")
    assert said(result, "after the binary changed")


@darwin_only
def test_launchd_agent_not_running_is_left_alone(machine, run_role):
    result = ok(launchd(machine, run_role, started_offset=None))

    assert not [c for c in machine.calls("launchctl") if "kickstart" in c]
    assert not machine.calls("ps"), "looked up a start time for PID 0"
    assert said(result, "not running, so it will start on the current binary")


@darwin_only
def test_launchd_check_mode_restarts_nothing(machine, run_role):
    result = ok(launchd(machine, run_role, started_offset=-HOUR, flags=("--check",)))

    assert not [c for c in machine.calls("launchctl") if "kickstart" in c]
    assert said(result, "STALE, would restart (check mode)")


@darwin_only
def test_ctime_is_read_through_the_symlink(machine, run_role):
    """Homebrew's bin/ollama is a symlink into the Cellar. The link is made
    after the file it points at, so its own ctime is later. Judged by the link,
    a process started between the two would look stale when it is not."""
    target = machine.binary("Cellar/thing/2/thing")
    time.sleep(2.1)  # lstart has one-second resolution
    link = machine.root / "bin" / "thing"
    link.parent.mkdir()
    link.symlink_to(target)
    between = machine.ctime(target) + 1
    assert between < os.lstat(link).st_ctime

    machine.state["launchd"] = {LABEL: 4242}
    machine.process(4242, between, str(link))
    result = ok(
        run_role(
            restart_stale_kind="launchd",
            restart_stale_launchd_label=LABEL,
            restart_stale_binary=str(link),
        )
    )

    assert not [c for c in machine.calls("launchctl") if "kickstart" in c]
    assert said(result, "after the binary changed")


# ── systemd ──────────────────────────────────────────────────────────────────
# The restart goes through ansible.builtin.systemd_service, which reads the
# unit with `systemctl show <unit>` before acting; the stub answers that too.
# Only user scope runs here: system scope restarts with become, and a test must
# not reach for sudo.

UNIT = "example.service"


def systemd(machine, run_role, *, started_offset: float | None, flags=()):
    binary = machine.binary()
    if started_offset is None:
        machine.state["systemd"] = {UNIT: 0}
    else:
        machine.state["systemd"] = {UNIT: 4343}
        machine.process(4343, machine.ctime(binary) + started_offset, "thing")
    return run_role(
        *flags,
        restart_stale_kind="systemd",
        restart_stale_systemd_unit=UNIT,
        restart_stale_binary=str(binary),
    )


def restarts(machine):
    return [c for c in machine.calls("systemctl") if "restart" in c]


def test_systemd_stale_unit_is_restarted(machine, run_role):
    result = ok(systemd(machine, run_role, started_offset=-HOUR))

    assert restarts(machine) == [["systemctl", "--user", "restart", UNIT]]
    assert said(result, "user unit example.service — RESTARTED because pid 4343")


def test_systemd_fresh_unit_is_left_alone(machine, run_role):
    result = ok(systemd(machine, run_role, started_offset=+HOUR))

    assert not restarts(machine)
    assert said(result, "user unit example.service — not restarted: pid 4343")


def test_systemd_stopped_unit_is_left_alone(machine, run_role):
    result = ok(systemd(machine, run_role, started_offset=None))

    assert not restarts(machine)
    assert not machine.calls("ps"), "looked up a start time for MainPID 0"
    assert said(result, "not running")


def test_systemd_check_mode_restarts_nothing(machine, run_role):
    result = ok(systemd(machine, run_role, started_offset=-HOUR, flags=("--check",)))

    assert not restarts(machine)
    assert said(result, "STALE, would restart (check mode)")


def test_a_bottle_dated_mtime_does_not_hide_a_stale_process(machine, run_role):
    """The 2026-09-22 incident at the wiring level. The binary's mtime is four
    days old, as a bottle's is; the process started two days ago, after that
    mtime but before the install. Judged by mtime it looks fresh."""
    binary = machine.binary(bottle_age=4 * 86400)
    started = machine.ctime(binary) - 2 * 86400
    assert os.stat(binary).st_mtime < started < machine.ctime(binary)

    machine.state["systemd"] = {UNIT: 4343}
    machine.process(4343, started, "thing")
    result = ok(
        run_role(
            restart_stale_kind="systemd",
            restart_stale_systemd_unit=UNIT,
            restart_stale_binary=str(binary),
        )
    )

    assert restarts(machine), "judged the process by mtime, not ctime"
    assert said(result, "RESTARTED")


# ── app ──────────────────────────────────────────────────────────────────────

APP_PID = 5151


def app(machine, run_role, *, started_offset: float, quits=True, quit_rc=0, flags=()):
    binary = machine.binary("Apps/Thing.app/Contents/MacOS/Thing")
    start = machine.ctime(binary) + started_offset
    machine.process(APP_PID, start, str(binary))
    # A helper that shares the bundle and is older than anything — if the
    # match were by prefix, its age would decide.
    machine.process(5150, start - 30 * 86400, str(binary) + " Helper")
    machine.state["exits_on_quit"] = [APP_PID] if quits else []
    machine.state["quit_rc"] = quit_rc
    machine.state["quit_stderr"] = "Not authorised to send Apple events (-1743)"
    return run_role(
        *flags,
        restart_stale_kind="app",
        restart_stale_app_name="Thing",
        restart_stale_binary=str(binary),
        restart_stale_quit_timeout=2,
    )


@darwin_only
def test_app_stale_is_quit_gracefully_then_reopened(machine, run_role):
    result = ok(app(machine, run_role, started_offset=-HOUR))

    quit = machine.calls("osascript")
    bundle = str(machine.root / "Apps" / "Thing.app")
    assert quit and f'quit app "{bundle}"' in quit[0]
    assert machine.calls("open") == [["open", "-a", bundle]]
    assert said(result, "RESTARTED (quit and reopened)")


@darwin_only
def test_app_fresh_is_left_alone_even_with_an_old_helper(machine, run_role):
    result = ok(app(machine, run_role, started_offset=+HOUR))

    assert not machine.calls("osascript")
    assert not machine.calls("open")
    assert said(result, f"pid {APP_PID} started")


@darwin_only
def test_app_that_will_not_quit_is_left_running(machine, run_role):
    """The quit was accepted and ignored. Never escalate to a kill."""
    result = ok(app(machine, run_role, started_offset=-HOUR, quits=False))

    assert not machine.calls("open"), "reopened an app that never closed"
    assert not [c for c in machine.calls() if c[0] in ("kill", "pkill", "killall")]
    assert said(result, "STALE but NOT restarted: asked to quit, still running")


@darwin_only
def test_app_whose_quit_is_refused_is_left_running(machine, run_role):
    """osascript itself failed — here the Automation permission was denied."""
    result = ok(app(machine, run_role, started_offset=-HOUR, quit_rc=1))

    assert not machine.calls("open")
    assert all("pid=" not in c for c in machine.calls("ps")), (
        "waited for an exit that was never requested"
    )
    assert said(result, "STALE but NOT restarted: the graceful quit failed")
    assert said(result, "-1743")


@darwin_only
@pytest.mark.parametrize("rc", [1, 2])
def test_an_exit_probe_error_cannot_authorize_reopening(machine, run_role, rc):
    machine.state["exit_probe_error"] = {
        "rc": rc,
        "stderr": "process probe unavailable",
    }
    result = app(machine, run_role, started_offset=-HOUR)

    assert result.returncode != 0, result.stdout + result.stderr
    assert said(result, "process probe unavailable")
    assert not machine.calls("open")
    assert not said(result, "RESTARTED (quit and reopened)")


@darwin_only
def test_an_unreadable_process_table_is_not_a_stopped_app(machine, run_role):
    machine.state["process_probe_error"] = {
        "rc": 1,
        "stderr": "process table unavailable",
    }
    result = app(machine, run_role, started_offset=-HOUR)

    assert result.returncode != 0, result.stdout + result.stderr
    assert said(result, "process table unavailable")
    assert not machine.calls("osascript")
    assert not machine.calls("open")


@darwin_only
def test_app_check_mode_quits_nothing(machine, run_role):
    result = ok(app(machine, run_role, started_offset=-HOUR, flags=("--check",)))

    assert not machine.calls("osascript")
    assert not machine.calls("open")
    assert said(result, "STALE, would restart (check mode)")


# ── parameters ───────────────────────────────────────────────────────────────


def test_a_missing_kind_fails_before_anything_runs(machine, run_role):
    result = run_role(restart_stale_binary=str(machine.binary()))

    assert result.returncode != 0
    assert said(result, "Nothing has been restarted")
    assert not machine.calls()


def test_the_defaults_leave_the_role_inert(run_role, machine):
    """No parameters at all must fail the check, not check nothing and pass."""
    result = run_role()
    assert result.returncode != 0
    assert not machine.calls()
