"""Contract tests for the whitespace retry.

Measured 2026-09-10: one blank line at the context/prompt seam flips
glm-4.7-flash between looping to the token cap with an empty reply and answering
correctly, deterministically in both directions — and gemma4:12b-mlx breaks the
opposite way on the same case. There is no safe spacing to normalise to, so the
harness retries once on a cap hit and reports the cell as whitespace-sensitive
rather than simply failed.

The hazard is sharper here than anywhere else in the harness, because the retry's
ONLY output is a distinction:

    A retry that never fires and a retry that fires and fails are identical in
    the results table. Both leave the cell reading FAIL.

So a test that merely checks "the cell failed" certifies nothing. The signal is
the `*` — the case being marked ws_sensitive when the nudge works — and that is
the direction these tests target.

Run:
    pytest tests/ollama_evals/test_whitespace_retry.py -v
"""

from __future__ import annotations

import pytest

CHECK = "assert response == 'ok', f'got {response!r}'"
# The prompt carries an internal blank line, as every real case does
# ("question\n\nReply with only: ..."). Without one, rfind("\n\n") lands on the
# seam by accident and the seam-targeting test passes even when the nudge is
# searching rather than being told where to cut — verified by injecting exactly
# that regression and watching an earlier version of this suite stay green.
CASE = {
    "name": "fake",
    "role": "r",
    "property": "p",
    "context": "some context",
    "prompt": "the question\n\nReply with only: ANSWER: <x>",
    "check": CHECK,
}


def _nudged(text: str) -> bool:
    """The nudge adds a blank line at the seam, so three newlines appear."""
    return "\n\n\n" in text


@pytest.fixture
def capped(ev, monkeypatch):
    """First call hits the cap; the nudged retry returns `retry_answer`."""

    def install(retry_answer: str | None):
        calls = {"n": 0, "nudged": 0}

        def fake(model, text, images, num_ctx, timeout, max_tokens=8192):
            calls["n"] += 1
            if _nudged(text):
                calls["nudged"] += 1
                if retry_answer is None:
                    return "", {"in": 1, "out": max_tokens, "done_reason": "length"}
                return retry_answer, {"in": 1, "out": 5, "done_reason": "stop"}
            return "", {"in": 1, "out": max_tokens, "done_reason": "length"}

        monkeypatch.setattr(ev, "generate", fake)
        return calls

    return install


def test_marks_whitespace_sensitive_when_the_nudge_works(ev, capped):
    """The relenting direction — and the only thing that distinguishes brittle
    from incapable.
    """
    calls = capped("ok")
    out = ev.eval_one("m", [CASE], 8192, 1, 60)
    case = out["cases"][0]
    assert calls["nudged"] == 1, "the retry never fired"
    assert case["ws_sensitive"] is True, "converged on retry but was not flagged"
    assert case["passed"] == 0, "the original attempt still failed and must be recorded"


def test_not_flagged_when_the_retry_also_hits_the_cap(ev, capped):
    """A genuine non-terminator must not be excused as merely brittle."""
    calls = capped(None)
    out = ev.eval_one("m", [CASE], 8192, 1, 60)
    case = out["cases"][0]
    assert calls["nudged"] == 1, "the retry should still have been attempted"
    assert case["ws_sensitive"] is False


def test_not_flagged_when_the_retry_returns_a_wrong_answer(ev, capped):
    """Converging is not enough; it has to converge on something correct."""
    capped("wrong")
    out = ev.eval_one("m", [CASE], 8192, 1, 60)
    assert out["cases"][0]["ws_sensitive"] is False


def test_no_retry_when_the_first_attempt_did_not_hit_the_cap(ev, monkeypatch):
    """A wrong-but-terminating answer is a capability result, not a format one."""
    calls = {"n": 0}

    def fake(model, text, images, num_ctx, timeout, max_tokens=8192):
        calls["n"] += 1
        return "wrong", {"in": 1, "out": 3, "done_reason": "stop"}

    monkeypatch.setattr(ev, "generate", fake)
    out = ev.eval_one("m", [CASE], 8192, 1, 60)
    assert calls["n"] == 1, "retried a run that terminated normally"
    assert out["cases"][0]["ws_sensitive"] is False


def test_no_retry_when_the_first_attempt_passed(ev, monkeypatch):
    calls = {"n": 0}

    def fake(model, text, images, num_ctx, timeout, max_tokens=8192):
        calls["n"] += 1
        return "ok", {"in": 1, "out": 3, "done_reason": "stop"}

    monkeypatch.setattr(ev, "generate", fake)
    out = ev.eval_one("m", [CASE], 8192, 1, 60)
    assert calls["n"] == 1
    assert out["cases"][0]["ws_sensitive"] is False


def test_no_ws_retry_flag_disables_it(ev, capped):
    calls = capped("ok")
    out = ev.eval_one("m", [CASE], 8192, 1, 60, no_ws_retry=True)
    assert calls["nudged"] == 0, "retry fired despite --no-ws-retry"
    assert out["cases"][0]["ws_sensitive"] is False


def test_the_nudge_targets_the_seam_not_the_last_blank_line(ev):
    r"""The bug this had once: rfind('\\n\\n') lands inside the prompt, so the
    retry perturbed something irrelevant and proved nothing.
    """
    text, _images, seam = ev.build_input(CASE)
    alt = ev.nudge_whitespace(text, seam)
    assert len(alt) == len(text) + 1
    assert alt[seam : seam + 3] == "\n\n\n", "the extra newline is not at the seam"
    assert alt[:seam] == text[:seam], "content before the seam changed"
