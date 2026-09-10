"""
Contract tests for the sweep early-exit.

`ordered: true` means difficulty rises monotonically, so climbing stops at the
first failure — that is what makes a ladder cheap. But it carries the same
hazard as every other "declines to run" path here:

    A ladder that stops at the RIGHT rung and one that stops at the FIRST rung
    both produce a plausible-looking break-point.

If the early-exit fired unconditionally, every model would report breaking at
rung one, the ladder would look calibrated, and the numbers would be fiction.
Only the RELENTING direction — climbing past a rung that passed — proves the
mechanism works.

`ordered: false` exists for non-monotonic axes (needle position: middle is
harder than late), where early-exit would misreport a profile as a break-point.
That path must probe every rung even after one fails.

Run:
    pytest tests/ollama_evals/test_sweep_early_exit.py -v
"""

from __future__ import annotations

import pytest

CHECK = "assert response == 'ok', f'got {response!r}'"


def _case(levels, ordered=True):
    return {
        "name": "fake", "role": "r", "property": "p",
        "prompt": "q", "check": CHECK,
        "sweep": {"ordered": ordered, "levels": levels},
    }


@pytest.fixture
def scripted(ev, monkeypatch):
    """Replace generate() with a canned answer per rung label."""
    def install(by_label: dict[str, str]):
        calls: list[str] = []

        def fake(model, text, images, num_ctx, timeout, max_tokens=8192):
            label = text.strip().split("\n")[-1]
            calls.append(label)
            return by_label[label], {"in": 1, "out": 1, "done_reason": "stop"}

        monkeypatch.setattr(ev, "generate", fake)
        return calls
    return install


LEVELS = [{"label": "a", "prompt": "a"}, {"label": "b", "prompt": "b"},
          {"label": "c", "prompt": "c"}]


def test_climbs_past_a_rung_that_passed(ev, scripted):
    """The relenting direction: passing rung 1 must not stop the climb."""
    calls = scripted({"a": "ok", "b": "ok", "c": "ok"})
    out = ev.eval_one("m", [_case(LEVELS)], 8192, 1, 60, sweep=True)
    assert calls == ["a", "b", "c"], "did not climb the whole ladder"
    case = out["cases"][0]
    assert case["reached"] == "c"
    assert case["broke_at"] is None


def test_stops_at_the_first_failure_when_ordered(ev, scripted):
    calls = scripted({"a": "ok", "b": "no", "c": "ok"})
    out = ev.eval_one("m", [_case(LEVELS)], 8192, 1, 60, sweep=True)
    assert calls == ["a", "b"], "kept climbing past a failure on an ordered sweep"
    case = out["cases"][0]
    assert case["reached"] == "a"
    assert case["broke_at"] == "b"


def test_unordered_probes_every_rung_despite_a_failure(ev, scripted):
    """Non-monotonic axes must not be cut short — that is the whole point."""
    calls = scripted({"a": "ok", "b": "no", "c": "ok"})
    out = ev.eval_one("m", [_case(LEVELS, ordered=False)], 8192, 1, 60, sweep=True)
    assert calls == ["a", "b", "c"], "unordered sweep exited early"
    case = out["cases"][0]
    assert case["broke_at"] == "b"
    assert case["reached"] == "c", "later passing rung not recorded"


def test_failure_on_the_first_rung_reports_no_reach(ev, scripted):
    scripted({"a": "no", "b": "ok", "c": "ok"})
    out = ev.eval_one("m", [_case(LEVELS)], 8192, 1, 60, sweep=True)
    case = out["cases"][0]
    assert case["reached"] is None
    assert case["broke_at"] == "a"


def test_sweeps_off_runs_the_base_case_only(ev, monkeypatch):
    """Without --sweep a laddered case costs exactly one call, as before."""
    calls = []

    def fake(model, text, images, num_ctx, timeout, max_tokens=8192):
        calls.append(text)
        return "ok", {"in": 1, "out": 1, "done_reason": "stop"}

    monkeypatch.setattr(ev, "generate", fake)
    ev.eval_one("m", [_case(LEVELS)], 8192, 1, 60, sweep=False)
    assert len(calls) == 1, f"sweeps disabled but made {len(calls)} calls"
