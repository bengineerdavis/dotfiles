"""Declared dependencies order topics without changing tier precedence.

The parent playbook consumes topics_in_run directly. These tests run the same
role interface and assert the resulting execution order, not a separate helper.
"""

from __future__ import annotations

# pyrefly: ignore [missing-import]
from topic_resolution_harness import ORDER_HARNESS, said

# pyrefly: ignore [missing-import]
from test_states import topic
import yaml
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT


def _order(result) -> list[str]:
    assert result.stdout
    marker = "msg: TOPIC_EXECUTION_ORDER="
    start = result.stdout.index(marker) + len(marker)
    text = result.stdout[start:].splitlines()[0].strip()
    return text.split(",") if text else []


def test_dependency_order_is_recursive_and_stable_for_ties(run_role):
    result = run_role(
        harness=ORDER_HARNESS,
        resolution_os_family="Darwin",
        resolution_topic_metadata=[
            topic("alpha", ["Darwin"]),
            topic("consumer", ["Darwin"], requires=["second"]),
            topic("zeta", ["Darwin"]),
            topic("middle", ["Darwin"], provides=["second"], requires=["first"]),
            topic("provider", ["Darwin"], provides=["first"]),
        ],
    )
    assert result.returncode == 0, result.stdout
    assert _order(result) == ["alpha", "provider", "zeta", "middle", "consumer"]


def test_unrelated_topics_keep_their_relative_alphabetical_order(run_role):
    result = run_role(
        harness=ORDER_HARNESS,
        resolution_os_family="Darwin",
        resolution_topic_metadata=[
            topic("chrome", ["Darwin"], requires=["git"]),
            topic("firefox", ["Darwin"]),
            topic("git", ["Darwin"], provides=["git"]),
        ],
    )
    assert result.returncode == 0, result.stdout
    order = _order(result)
    assert order == ["firefox", "git", "chrome"]


def test_tier_precedence_still_wins_over_topic_dependencies(run_role):
    result = run_role(
        harness=ORDER_HARNESS,
        resolution_os_family="Darwin",
        resolution_topic_metadata=[
            topic("consumer", ["Darwin"], requires=["runtime"]),
            topic("runtime", ["Darwin"], provides=["runtime"], tier="runtime-manager"),
            topic("manager", ["Darwin"], tier="pkg-manager"),
        ],
    )
    assert result.returncode == 0, result.stdout
    assert set(_order(result)) == {"manager", "runtime", "consumer"}
    play = yaml.safe_load((PAYLOAD_ROOT / "dotfiles" / "playbook.yaml").read_text())[0]
    tiers = [
        task["loop"].split("selectattr('topic_tier', 'eq', '")[1].split("'", 1)[0]
        for task in play["tasks"]
        if "ansible.builtin.include_role" in task
    ]
    assert tiers == ["pkg-manager", "runtime-manager", "app"]


def test_unprovided_dependency_remains_the_existing_probe(run_role):
    result = run_role(
        harness=ORDER_HARNESS,
        resolution_os_family="Darwin",
        resolution_topic_metadata=[
            topic("lima", ["Darwin"], requires=["no-such-binary-xyzzy"]),
        ],
    )
    assert result.returncode != 0
    assert said(result, "[NO_TOPIC]")
    assert not said(result, "Dependency cycle among topics: lima")


def test_empty_inventory_has_an_empty_order(run_role):
    result = run_role(
        harness=ORDER_HARNESS,
        resolution_os_family="Darwin",
        resolution_topic_metadata=[],
    )
    assert result.returncode == 0, result.stdout
    assert _order(result) == []


def test_dependency_cycle_fails_with_every_remaining_topic(run_role):
    result = run_role(
        harness=ORDER_HARNESS,
        resolution_os_family="Darwin",
        resolution_topic_metadata=[
            topic("first", ["Darwin"], provides=["first"], requires=["second"]),
            topic("second", ["Darwin"], provides=["second"], requires=["first"]),
        ],
    )
    assert result.returncode != 0, result.stdout
    assert said(result, "Dependency cycle among topics: first, second")


@settings(
    max_examples=6,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    st.permutations(
        [
            topic("git", ["Darwin"], provides=["git"]),
            topic("chrome", ["Darwin"], requires=["git"]),
            topic("firefox", ["Darwin"]),
        ]
    )
)
def test_order_is_stable_and_complete_for_every_input_order(run_role, metadata):
    result = run_role(
        harness=ORDER_HARNESS,
        resolution_os_family="Darwin",
        resolution_topic_metadata=metadata,
    )
    assert result.returncode == 0, result.stdout
    order = _order(result)
    assert order == ["firefox", "git", "chrome"]


def test_real_git_topic_precedes_its_consumers(run_role):
    metadata = [
        yaml.safe_load(
            (PAYLOAD_ROOT / "dotfiles" / "apps" / name / "topic.yml").read_text()
        )
        for name in ("git", "chrome", "gita", "homebrew", "mise")
    ]
    result = run_role(
        harness=ORDER_HARNESS,
        resolution_os_family="Darwin",
        resolution_topic_metadata=metadata,
    )
    assert result.returncode == 0, result.stdout
    order = _order(result)
    assert order.index("git") < order.index("chrome")
    assert order.index("git") < order.index("gita")
