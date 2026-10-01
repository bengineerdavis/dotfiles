"""The judge-panel gates must decline a degraded panel and accept a healthy one.

`spec.md` § Verification: a gate that can decline needs both directions proven
— a panel that skips everything and a panel that scores anything would both
report a clean run. The quorum rule and the concurrency bound are logic, so
they are tested with a fake judge rather than behind a real model.
"""

from __future__ import annotations

import threading
import time

from judge_panel_harness import MAX_CONCURRENT_JUDGES, panel_is_trustworthy, run_panel


def test_degraded_panel_declines():
    assert not panel_is_trustworthy(survivors=1, requested=3)
    assert not panel_is_trustworthy(survivors=0, requested=3)
    assert not panel_is_trustworthy(survivors=1, requested=2)
    assert not panel_is_trustworthy(survivors=0, requested=1)


def test_healthy_panel_proceeds():
    assert panel_is_trustworthy(survivors=3, requested=3)
    assert panel_is_trustworthy(survivors=2, requested=3)
    assert panel_is_trustworthy(survivors=1, requested=1)


def test_no_requested_judges_is_never_trustworthy():
    assert not panel_is_trustworthy(survivors=0, requested=0)


def test_run_panel_reports_failures_instead_of_swallowing_them():
    def judge(model, command, script):
        if model == "dead":
            raise RuntimeError("Unknown model")
        return f"score-from-{model}"

    scores, failures = run_panel("cmd", "script", ["live", "dead", "also-live"], judge)
    assert sorted(scores) == ["score-from-also-live", "score-from-live"]
    assert [m for m, _ in failures] == ["dead"]


def test_run_panel_bounds_concurrent_judges():
    """Two local models loading at once can kill the shared Ollama daemon, so
    the fan-out must never exceed MAX_CONCURRENT_JUDGES in flight.
    """
    lock = threading.Lock()
    in_flight = 0
    peak = 0

    def judge(model, command, script):
        nonlocal in_flight, peak
        with lock:
            in_flight += 1
            peak = max(peak, in_flight)
        time.sleep(0.05)
        with lock:
            in_flight -= 1
        return model

    models = [f"m{i}" for i in range(6)]
    scores, failures = run_panel("cmd", "script", models, judge)
    assert len(scores) == 6 and not failures
    assert peak <= MAX_CONCURRENT_JUDGES, (
        f"{peak} judges ran at once — the shared Ollama daemon cannot take "
        f"more than {MAX_CONCURRENT_JUDGES} concurrent local model loads"
    )
