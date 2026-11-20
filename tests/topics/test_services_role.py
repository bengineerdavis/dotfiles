"""roles/services — the shared per-user service unit machinery.

Two kinds of test, because the role has two kinds of claim:

1. **Rendering** — the launchd and systemd templates produce documents that the
   real tools accept, under both `os_family` values, with StrictUndefined so a
   missing variable fails loudly instead of rendering blank.
2. **Convergence** — the launchd order really converges from a *disabled*
   label. That is the DOT-343 bug, and it is pinned by running the role's own
   shell command against throwaway labels. Rendering tests cannot catch it: the
   old buggy command rendered perfectly.

The convergence tests are macOS-only and skip elsewhere; the rendering tests
run anywhere.
"""

from __future__ import annotations

import os
import pathlib
import plistlib
import re
import shutil
import subprocess
import time

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT
import jinja2
import pytest
import yaml

ROLE = PAYLOAD_ROOT / "dotfiles" / "roles" / "services"
JINJA = jinja2.Environment(undefined=jinja2.StrictUndefined, autoescape=False)

UID_NUM = os.getuid()


def render(template_name: str, **variables) -> str:
    template = JINJA.from_string((ROLE / "templates" / template_name).read_text())
    return template.render(**variables)


def base_variables(**overrides):
    """The minimum a caller must supply, plus the defaults the role fills in."""
    variables = {
        "service_label": "com.example.widget",
        "service_description": "example widget daemon",
        "service_program_arguments": [
            "/bin/sleep",
            "300",
        ],
        "service_environment": {},
        "service_log_path": "/tmp/widget/service.log",
        "service_run_at_load": True,
        "service_keep_alive": True,
        "service_process_type": "",
        "service_bootout_wait_ticks": 50,
        "service_bootout_wait_seconds": "0.1",
        "service_health_attempts": 5,
        "service_health_interval_seconds": "1",
        "service_health_command": "",
        "service_systemd_restart": "always",
        "service_systemd_restart_sec": 3,
        "service_systemd_name": "com.example.widget.service",
        "service_unit_path": "/tmp/widget.plist",
    }
    variables.update(overrides)
    return variables


# ── Rendering: launchd ───────────────────────────────────────────────────────


def test_plist_is_valid_and_carries_the_program():
    document = render("launchd-agent.plist.j2", **base_variables())
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE'
        + document.split("<!DOCTYPE", 1)[1]
    )
    plist = plistlib.loads(body.encode())

    assert plist["Label"] == "com.example.widget"
    assert plist["ProgramArguments"] == ["/bin/sleep", "300"]
    assert plist["RunAtLoad"] is True
    assert plist["KeepAlive"] is True
    assert plist["StandardOutPath"] == "/tmp/widget/service.log"
    assert plist["StandardErrorPath"] == "/tmp/widget/service.log"


def test_plist_escapes_arguments():
    """A literal & or < in an argument must not corrupt the document.

    A service that passes a URL or a shell fragment as an argv element is
    ordinary; an unescaped ampersand makes the plist unparseable, which launchd
    reports only as a failed load.
    """
    document = render(
        "launchd-agent.plist.j2",
        **base_variables(service_program_arguments=["/bin/sh", "-c", "a & b < c"]),
    )
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE'
        + document.split("<!DOCTYPE", 1)[1]
    )
    plist = plistlib.loads(body.encode())
    assert plist["ProgramArguments"][2] == "a & b < c"


def test_plist_omits_optional_keys_when_unset():
    document = render("launchd-agent.plist.j2", **base_variables())
    assert "ProcessType" not in document
    assert "EnvironmentVariables" not in document


def test_plist_includes_environment_when_given():
    document = render(
        "launchd-agent.plist.j2",
        **base_variables(service_environment={"PATH": "/usr/bin:/bin"}),
    )
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE'
        + document.split("<!DOCTYPE", 1)[1]
    )
    plist = plistlib.loads(body.encode())
    assert plist["EnvironmentVariables"] == {"PATH": "/usr/bin:/bin"}


def test_plist_renders_a_scheduled_job_shape():
    """KeepAlive and RunAtLoad are caller-controlled, so a one-shot shape is
    expressible without editing the template.
    """
    document = render(
        "launchd-agent.plist.j2",
        **base_variables(service_keep_alive=False, service_run_at_load=False),
    )
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE'
        + document.split("<!DOCTYPE", 1)[1]
    )
    plist = plistlib.loads(body.encode())
    assert plist["KeepAlive"] is False
    assert plist["RunAtLoad"] is False


# ── Rendering: systemd ───────────────────────────────────────────────────────


def test_systemd_unit_carries_the_program_and_restart_policy():
    document = render("systemd-user.service.j2", **base_variables())
    assert "ExecStart=/bin/sleep 300" in document
    assert "Restart=always" in document
    assert "RestartSec=3" in document
    assert "WantedBy=default.target" in document
    assert "Description=example widget daemon" in document


def test_systemd_unit_emits_environment_when_given():
    document = render(
        "systemd-user.service.j2",
        **base_variables(service_environment={"PATH": "/usr/bin:/bin"}),
    )
    assert 'Environment="PATH=/usr/bin:/bin"' in document


def test_systemd_unit_omits_environment_when_unset():
    document = render("systemd-user.service.j2", **base_variables())
    assert "Environment=" not in document


def test_systemd_unit_never_asks_for_a_system_scope():
    """A per-user unit: no User=, no system paths, no root."""
    document = render("systemd-user.service.j2", **base_variables())
    assert "User=" not in document
    assert "WantedBy=multi-user.target" not in document


# ── Both templates: undefined variables fail loudly ──────────────────────────


@pytest.mark.parametrize(
    "template_name",
    ["launchd-agent.plist.j2", "systemd-user.service.j2"],
)
def test_a_missing_variable_fails_loudly(template_name):
    """StrictUndefined: a forgotten variable must raise, never render blank.

    A blank ProgramArguments or Description produces a unit that loads and does
    nothing, which is the failure mode this role exists to remove.
    """
    variables = base_variables()
    del variables["service_program_arguments"]
    with pytest.raises(jinja2.UndefinedError):
        render(template_name, **variables)


# ── Routing: a tagged install must never select teardown ────────────────────
#
# These run the REAL playbook through `--list-tasks`, because the bug they pin
# is a tag-inheritance consequence that no amount of reading the YAML reveals.
# `--list-tasks` prints each selected task with its effective tag set, which is
# exactly the question: "does `--tags install` select a remove task?"

PLAYBOOK = PAYLOAD_ROOT / "dotfiles" / "apps" / "backlog" / "playbook.yaml"


def list_tasks(*tags: str) -> list[str]:
    """The tasks `ansible-playbook --list-tasks` selects, one per line."""
    ansible = shutil.which("ansible-playbook")
    if not ansible:
        pytest.skip("ansible-playbook is not on PATH")
    command = [ansible, "-i", "localhost,", str(PLAYBOOK), "--list-tasks"]
    if tags:
        command += ["--tags", ",".join(tags)]
    completed = subprocess.run(
        command, capture_output=True, text=True, cwd=PAYLOAD_ROOT / "dotfiles"
    )
    # A non-zero exit is a real failure, not an unavailable tool: ansible is
    # installed. Skipping here would report the suite green while the routing
    # this file exists to pin was never examined.
    assert completed.returncode == 0, (
        f"ansible-playbook --list-tasks failed ({completed.returncode}):\n"
        f"{completed.stderr[-2000:]}"
    )
    return [line.strip() for line in completed.stdout.splitlines() if "TAGS:" in line]


def test_install_tag_does_not_select_teardown():
    """`--tags install` must not select a remove task.

    Measured 2026-11-20 (the live failure): a tagged install run stopped the
    daemon and deleted its plist. The cause is tag inheritance, not a missing
    `never`: the topic's install phase imports the WHOLE role, so the role's
    remove phase sits underneath and inherits `install` from the importing
    task. `never` only skips a task when nothing else selects it, and the
    inherited tag does select it.

    The fix is structural — callers import one phase via `tasks_from` — so
    this pins the outcome rather than the spelling.
    """
    selected = list_tasks("install")
    assert selected, "the install tag selected nothing at all"
    teardown = [
        line for line in selected if "remove the unit" in line or "stop " in line
    ]
    assert not teardown, (
        "`--tags install` selected teardown:\n  "
        + "\n  ".join(teardown)
        + "\n\nThe install phase imports the whole role, so the remove phase "
        "inherits the install tag. Import one phase with tasks_from instead."
    )


def test_a_bare_run_does_not_select_teardown():
    """A bare run converges and stops; it must not tear the service down."""
    selected = list_tasks()
    assert selected, "the bare run selected nothing at all"
    teardown = [
        line for line in selected if "remove the unit" in line or "stop " in line
    ]
    assert not teardown, "a bare run selected teardown:\n  " + "\n  ".join(teardown)


def test_remove_tag_still_selects_teardown():
    """The fix must not make teardown unreachable — `--tags remove` still runs it."""
    selected = list_tasks("remove")
    teardown = [line for line in selected if "remove the unit" in line]
    assert teardown, "`--tags remove` selected no teardown task"


def test_remove_tag_does_not_select_install():
    """`--tags remove` must not re-install as a side effect."""
    selected = list_tasks("remove")
    install = [line for line in selected if "install the unit" in line]
    assert not install, "`--tags remove` selected install:\n  " + "\n  ".join(install)


def test_whole_role_import_is_refused_loudly():
    """A whole-role import must fail, not silently run both phases.

    Ansible treats a role with no `tasks/main.yaml` as having no tasks, so
    deleting the router would turn the bug into a silent no-op — the opposite
    of failing closed. The router stays, and fails.
    """
    router = ROLE / "tasks" / "main.yaml"
    assert router.exists(), "the router must exist so a whole-role import fails loudly"
    parsed = yaml.safe_load(router.read_text())
    assert parsed, "the router must carry the guard task"
    fails = [task for task in parsed if "ansible.builtin.fail" in task]
    assert fails, "the router must fail, rather than route both phases"
    for task in fails:
        assert "always" in (task.get("tags") or []), (
            "the guard must be tagged `always`, or a tag-limited run skips it"
        )


# ── Convergence: the DOT-343 bug, pinned ────────────────────────────────────


def darwin_converge_command() -> str:
    """The Darwin converge command, read out of the role rather than restated."""
    tasks = yaml.safe_load((ROLE / "tasks" / "converge.yaml").read_text())
    task = next(
        candidate
        for candidate in tasks
        if "converge" in candidate["name"] and "Darwin" in candidate["name"]
    )
    return task["ansible.builtin.shell"]["cmd"]


def render_converge(label: str, plist: pathlib.Path) -> str:
    return (
        darwin_converge_command()
        .replace("{{ service_label }}", label)
        .replace("{{ service_unit_path }}", str(plist))
        .replace("{{ service_bootout_wait_ticks }}", "50")
        .replace("{{ service_bootout_wait_seconds }}", "0.1")
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
    result = subprocess.run(
        ["launchctl", "print", f"gui/{UID_NUM}/{label}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return "pid = " in result.stdout


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


def clean(label: str, plist: pathlib.Path) -> None:
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


def settle(label: str, seconds: float = 8.0) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if running(label):
            return
        time.sleep(0.1)


def converge(label: str, plist: pathlib.Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", render_converge(label, plist)],
        capture_output=True,
        text=True,
        check=False,
    )


launchd_only = pytest.mark.skipif(
    not shutil.which("launchctl"), reason="launchctl is macOS-only"
)


def fresh(tmp_path, name: str) -> tuple[str, pathlib.Path]:
    label = f"com.example.role-test-{os.getpid()}-{name}"
    plist = tmp_path / f"{label}.plist"
    clean(label, plist)
    write_plist(label, plist)
    return label, plist


@launchd_only
def test_converges_from_absent(tmp_path):
    label, plist = fresh(tmp_path, "absent")
    try:
        result = converge(label, plist)
        settle(label)
        assert result.returncode == 0, result.stdout + result.stderr
        assert running(label)
    finally:
        clean(label, plist)


@launchd_only
def test_converges_from_a_disabled_label(tmp_path):
    """DOT-343: `launchctl disable` is persistent, so a label left disabled
    made every later bootstrap fail rc 5 with the service down.
    """
    label, plist = fresh(tmp_path, "disabled")
    try:
        subprocess.run(
            ["launchctl", "disable", f"gui/{UID_NUM}/{label}"],
            capture_output=True,
            check=False,
        )
        result = converge(label, plist)
        settle(label)
        assert running(label), (
            "the service did not converge from a disabled label: "
            + result.stdout
            + result.stderr
        )
    finally:
        clean(label, plist)


@launchd_only
def test_converges_from_a_loaded_and_disabled_label(tmp_path):
    label, plist = fresh(tmp_path, "loaded-disabled")
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
        clean(label, plist)


@launchd_only
def test_two_runs_in_a_row_stay_converged(tmp_path):
    label, plist = fresh(tmp_path, "twice")
    try:
        first = converge(label, plist)
        settle(label)
        second = converge(label, plist)
        settle(label)
        assert first.returncode == 0, first.stdout + first.stderr
        assert second.returncode == 0, second.stdout + second.stderr
        assert running(label)
    finally:
        clean(label, plist)


# ── The order itself is the contract ────────────────────────────────────────


def test_enable_precedes_bootstrap_in_the_darwin_command():
    """The whole DOT-343 fix, stated as a property of the command.

    `enable` is the only step that clears a persistent disabled override, so it
    must run unconditionally and before any bootstrap that could fail. If a
    future edit reorders it behind `&&`, this fails without needing launchd.
    """
    command = darwin_converge_command()
    enable_at = command.index("launchctl enable")
    bootstrap_at = command.index("launchctl bootstrap")
    assert enable_at < bootstrap_at, "enable must come before bootstrap"

    # It must not be chained behind a command with `&&`, or a failing bootstrap
    # makes it unreachable again.
    enable_line = (
        command[:enable_at].rsplit("\n", 1)[-1] + command[enable_at:].split("\n", 1)[0]
    )
    assert "&&" not in enable_line, (
        "enable must not be gated behind another command with &&"
    )


def test_presence_is_tested_with_print_not_bootout():
    """`bootout` of a missing label exits 3, so it is the wrong presence test.

    The command must ask `launchctl print` whether the label is loaded, and
    guard the bootout with that answer.
    """
    command = darwin_converge_command()
    assert re.search(r'if launchctl print "\$target"', command), (
        "bootout must be guarded by a launchctl print presence check"
    )
