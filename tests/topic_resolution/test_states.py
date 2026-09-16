"""The three resolution states, on synthetic topics.

docs/TOPICS.md § "Dependency resolution" defines the states: `OK` (dep provided
by a topic in run, or on PATH), `TOPIC_NOT_RUN` (a topic provides it but is
excluded by `topic_os`), and `NO_TOPIC` (nothing provides it and it is not on
PATH). The role enforces these with an assert whose `fail_msg` is prefixed with
the state marker, so the failure mode is distinguishable in stdout.

Synthetic topics keep each test to one state. Nothing here touches the real
apps/ tree.

Run:
    pytest tests/topic_resolution/test_states.py -v
"""

from __future__ import annotations

from topic_resolution_harness import said


def _topic(name, os_family, *, provides=(), requires=(), tier="app"):
    return {
        "topic_name": name,
        "topic_os": os_family,
        "topic_provides": list(provides),
        "topic_requires": list(requires),
        "topic_tier": tier,
    }


def test_ok_when_a_topic_in_run_provides_the_dep(run_role):
    result = run_role(
        resolution_os_family="Darwin",
        resolution_topic_metadata=[
            _topic("provider", ["Darwin"], provides=["thing"]),
            _topic("consumer", ["Darwin"], requires=["thing"]),
        ],
    )
    assert result.returncode == 0, result.stdout


def test_ok_when_the_dep_is_on_path_but_provided_by_no_topic(run_role):
    # `true` is a coreutils binary on every machine; no topic provides it, so it
    # can only pass through the PATH probe (`command -v true`).
    result = run_role(
        resolution_os_family="Darwin",
        resolution_topic_metadata=[
            _topic("consumer", ["Darwin"], requires=["true"]),
        ],
    )
    assert result.returncode == 0, result.stdout


def test_topic_not_run_when_a_topic_provides_but_is_os_excluded(run_role):
    result = run_role(
        resolution_os_family="Debian",
        resolution_topic_metadata=[
            _topic("provider", ["Darwin"], provides=["thing"]),
            _topic("consumer", ["Debian"], requires=["thing"]),
        ],
    )
    assert result.returncode != 0
    assert result.stdout
    assert said(result, "[TOPIC_NOT_RUN]")
    assert not said(result, "[NO_TOPIC]")


def test_no_topic_when_nothing_provides_and_not_on_path(run_role):
    result = run_role(
        resolution_os_family="Debian",
        resolution_topic_metadata=[
            _topic("consumer", ["Debian"], requires=["no-such-binary-xyzzy"]),
        ],
    )
    assert result.returncode != 0
    assert result.stdout
    assert said(result, "[NO_TOPIC]")
    assert not said(result, "[TOPIC_NOT_RUN]")
