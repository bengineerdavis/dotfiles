"""The no-root-authority guard fires for root and relents for a normal user.

The incident: mise was run under sudo, which installed a second tool tree under
/root and left stale locks in the temp directory. Ansible's own mise tasks never
elevated, so the guard's job is the process-level case a `become: false` setting
cannot cover.

Both directions are load-bearing. A guard that fires always and a guard that
fires correctly are indistinguishable on a machine that happens to run as root,
which is why the relenting case is here and not left to the happy path.

Run:
    pytest tests/guards -v
"""

from __future__ import annotations

# pyrefly: ignore [missing-import]
from guard_harness import said


def test_fails_when_the_run_is_root(run_guard):
    result = run_guard(
        "no-root-authority.yaml",
        guard_caller="tests/guards",
        guard_no_root_user_id="root",
        guard_no_root_sudo_user="",
    )
    assert result.returncode != 0
    assert said(result, "must run as the invoking user")


def test_fails_when_the_run_started_through_sudo(run_guard):
    result = run_guard(
        "no-root-authority.yaml",
        guard_caller="tests/guards",
        guard_no_root_user_id="bdavis",
        guard_no_root_sudo_user="bdavis",
    )
    assert result.returncode != 0
    assert said(result, "started with sudo")


def test_relents_for_a_normal_user(run_guard):
    result = run_guard(
        "no-root-authority.yaml",
        guard_caller="tests/guards",
        guard_no_root_user_id="bdavis",
        guard_no_root_sudo_user="",
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_the_message_names_the_caller(run_guard):
    result = run_guard(
        "no-root-authority.yaml",
        guard_caller="apps/mise",
        guard_no_root_user_id="root",
        guard_no_root_sudo_user="",
    )
    assert result.returncode != 0
    assert said(result, "apps/mise")
