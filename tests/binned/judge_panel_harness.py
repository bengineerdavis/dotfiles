"""Reliability rules for the LLM judge panel.

Deliberately not conftest.py (see tests/guards/guard_harness.py): shared logic
lives in a named module so it cannot collide with another suite's conftest.

`run_panel` takes its judge as a function so the fan-out can be tested without
calling a model at all — the quorum and concurrency rules are the thing under
test, and they must not be exercised only when a model happens to be installed.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable

# One Ollama daemon serves every local model and its memory is global, so two
# cold loads at once can kill it — and the death surfaces later as a misleading
# timeout rather than as contention. The panel is 2 local + 1 cloud judges;
# keep local concurrency at 2 and let the cloud one overlap network latency.
# Threads, not asyncio: the model work is already a subprocess, so there is no
# GIL wait to free and asyncio would add a second concurrency model for nothing.
MAX_CONCURRENT_JUDGES = 2


def panel_is_trustworthy(survivors: int, requested: int) -> bool:
    """A strict majority of the requested judges must actually answer.

    Scoring on the survivors is how a cold-load timeout turns into a passing
    grade: one lenient judge out of three still yields a mean. Declining is the
    honest answer, and the caller names which judges died so the cause is
    legible instead of being averaged away.
    """
    if requested <= 0:
        return False
    return survivors > requested // 2


def run_panel(
    command: str,
    script: str,
    judge_models: list[str],
    judge_fn: Callable[[str, str, str], Any],
) -> tuple[list[Any], list[tuple[str, BaseException]]]:
    """Fan out over judges, bounded by MAX_CONCURRENT_JUDGES.

    Returns (scores, failures). A judge failure is data, not an exception: the
    caller decides whether the surviving panel is still evidence, via
    panel_is_trustworthy. Silently returning only the survivors would make a
    three-judge panel and a one-judge panel look identical.
    """
    scores: list[Any] = []
    failures: list[tuple[str, BaseException]] = []
    workers = max(1, min(len(judge_models), MAX_CONCURRENT_JUDGES))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(judge_fn, m, command, script): m for m in judge_models}
        for fut in as_completed(futures):
            model = futures[fut]
            try:
                scores.append(fut.result())
            except BaseException as exc:  # noqa: BLE001 — a judge crash is data
                failures.append((model, exc))
    return scores, failures
