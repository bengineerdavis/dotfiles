"""The committed provisioning-answers registry, as data.

These read the real `dotfiles/machines.yml` rather than a fixture, because what
they pin is the data itself: that this machine's answers are the ones the box is
actually provisioned with, and that no machine key is a hardware serial.

They live apart from the loader tests deliberately. A change to `machines.yml`
should be reviewable and revertible without the topic's code, and a change to
the topic's code should not be gated on the fleet's answers.
"""

from __future__ import annotations

import re

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT
import pytest
import yaml

REGISTRY = PAYLOAD_ROOT / "dotfiles" / "machines.yml"

pytestmark = pytest.mark.skipif(
    not REGISTRY.is_file(), reason="dotfiles/machines.yml not present"
)


def test_committed_registry_gives_pop_os_the_installed_answers() -> None:
    """The real registry, resolved for pop-os, matches this box's env.zsh.

    A machine entry beats the shared tier, and pop-os's effective answers equal
    the values the machine is actually running with.
    """
    registry = yaml.safe_load(REGISTRY.read_text())
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

    Deliberately narrow: it rejects the serial shape rather than allowlisting
    names, so a new machine can be added without editing the test.
    """
    registry = yaml.safe_load(REGISTRY.read_text())
    serial_shape = re.compile(r"^[A-Z0-9]{10,}$")
    for key in registry.get("machines", {}):
        assert not serial_shape.match(key), (
            f"machine key {key!r} looks like a hardware serial; a hostname "
            "that fails spec.md § Data's string test must not be committed "
            "(use the local overlay instead)"
        )


def test_the_registry_carries_no_repo_membership() -> None:
    """Membership lives in config/repos.yaml, not here.

    machines.yml held a per-machine `repos:` block until 2026-11-04. It had no
    consumer and was keyed by a hardware serial. A reader who finds repo
    membership creeping back into this file has found the shape that removal
    existed to delete.
    """
    registry = yaml.safe_load(REGISTRY.read_text())
    assert "repos" not in registry, (
        "repo membership belongs in config/repos.yaml (the shared catalogue); "
        "machines.yml carries provisioning answers only"
    )
    for host, entry in (registry.get("machines") or {}).items():
        assert "repos" not in (entry or {}), (
            f"machines.{host}.repos is the per-machine membership block that "
            "2026-11-04 removed (no consumer, serial-keyed). Repo membership "
            "belongs in config/repos.yaml"
        )
