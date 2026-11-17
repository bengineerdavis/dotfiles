"""apps/backlog's daemon service wiring into roles/services.

The convergence order itself — the DOT-343 bug — is tested once, in
`tests/topics/test_services_role.py`, against the role that now owns it. What
is left to pin here is the *wiring*: that this topic hands the role the right
label, argv, log path and health probe, and tears down through the same role.

That split is deliberate. Duplicating the convergence tests here would mean two
places to update and two places to be wrong about the same rule; leaving the
wiring untested would let a refactor quietly point the service at the wrong
binary or drop the health check.
"""

from __future__ import annotations

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT
import pytest
import yaml

TOPIC = PAYLOAD_ROOT / "dotfiles" / "apps" / "backlog"
INSTALL = TOPIC / "tasks" / "install.yaml"
REMOVE = TOPIC / "tasks" / "remove.yaml"
DEFAULTS = TOPIC / "defaults" / "main.yaml"


def role_call(path, name_fragment: str) -> dict:
    tasks = yaml.safe_load(path.read_text())
    return next(task for task in tasks if name_fragment in task["name"])


def test_install_converges_through_the_shared_role():
    """The topic must not re-implement the unit or the restart sequence.

    DOT-343 was that logic being written per topic, and written wrong. One
    implementation, tested, is the fix.
    """
    task = role_call(INSTALL, "install and converge the daemon service")
    assert task["ansible.builtin.import_role"]["name"] == "roles/services"
    # import_role (static), not include_role: tag selection needs the role's
    # tasks visible at parse time.
    assert "ansible.builtin.include_role" not in task


def test_install_hands_the_role_the_real_argv():
    variables = role_call(INSTALL, "install and converge the daemon service")["vars"]
    argv = variables["service_program_arguments"]
    assert argv[0] == "{{ backlog_bin }}"
    assert "daemon" in argv
    assert "run" in argv
    assert "--foreground" in argv, (
        "the daemon must run in its documented foreground mode so the service "
        "manager owns the lifecycle"
    )
    assert "{{ backlog_daemon_host }}" in argv
    assert "{{ backlog_daemon_port }}" in argv


def test_install_probes_the_daemon_itself_for_health():
    """A bootstrap can return 0 and leave nothing listening, so the health
    command must be the daemon's own status, not a bare port check.
    """
    variables = role_call(INSTALL, "install and converge the daemon service")["vars"]
    assert (
        variables["service_health_command"] == "{{ backlog_bin }} daemon status --json"
    )


def test_install_and_remove_use_the_same_label_and_paths():
    """Teardown must target exactly what install created."""
    install = role_call(INSTALL, "install and converge the daemon service")["vars"]
    remove = role_call(REMOVE, "stop and remove the daemon unit")["vars"]
    for key in (
        "service_label",
        "service_unit_path",
        "service_systemd_name",
        "service_systemd_unit_path",
        "service_log_path",
    ):
        assert install[key] == remove[key], f"{key} drifts between install and remove"


def test_remove_tears_down_through_the_same_role():
    task = role_call(REMOVE, "stop and remove the daemon unit")
    assert task["ansible.builtin.import_role"]["name"] == "roles/services"


def test_the_launchd_and_systemd_names_share_a_stem():
    """One label, both init systems: a divergence here is how the two drift."""
    defaults = yaml.safe_load(DEFAULTS.read_text())
    label = defaults["backlog_daemon_label"]
    assert "{{ backlog_daemon_label }}.service" in defaults["backlog_unit_path"]
    assert "{{ backlog_daemon_label }}.plist" in defaults["backlog_plist_path"]
    assert label == "com.backlog-py.daemon"


def test_the_topic_no_longer_carries_its_own_unit_templates():
    """The superseded per-topic templates must be gone, not merely unused.

    A leftover template is the copy a future edit updates by mistake — the
    exact duplication this migration removed.
    """
    templates = TOPIC / "templates"
    leftovers = (
        sorted(p.name for p in templates.glob("*daemon*")) if templates.exists() else []
    )
    assert leftovers == [], f"superseded unit templates remain: {leftovers}"


@pytest.mark.parametrize("path", [INSTALL, REMOVE])
def test_task_files_still_parse(path):
    assert yaml.safe_load(path.read_text())
