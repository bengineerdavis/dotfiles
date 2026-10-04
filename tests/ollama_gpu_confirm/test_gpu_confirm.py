"""The per-GPU confirm: a backend fallback must be loud, health quiet.

Journal lines are shaped like ollama's startup log: the latest
inference-compute line carries `library=<backend>` - which backend the
server actually bound.
"""

from __future__ import annotations

import confirm_harness as harness

ROCM = "inference compute id=0 library=rocm compute=gfx1030 name=RX_6900_XT"
CUDA = "inference compute id=0 library=cuda compute=8.6 name=RTX_3090"
VULKAN = "inference compute id=0 library=vulkan compute=0.0 name=llvmpipe"
CPU = "inference compute id=0 library=cpu"


def stamped(log: str) -> str:
    return f"2026-10-03T18:00:00.000000-07:00 host ollama-rocm[421]: {log}\n"


def test_rocm_binding_succeeds_and_reports_the_line(run_confirm):
    r = run_confirm(stamped(ROCM))
    assert r.returncode == 0
    assert "library=rocm" in r.stdout
    assert "FELL BACK" not in r.stdout


def test_cuda_binding_succeeds(run_confirm):
    r = run_confirm(stamped(CUDA))
    assert r.returncode == 0


def test_vulkan_fallback_fails(run_confirm):
    r = run_confirm(stamped(VULKAN))
    assert r.returncode == 1
    assert "FELL BACK" in r.stdout


def test_cpu_binding_fails(run_confirm):
    r = run_confirm(stamped(CPU))
    assert r.returncode == 1
    assert "FELL BACK" in r.stdout


def test_no_compatible_gpus_fails(run_confirm):
    r = run_confirm(stamped('level=WARN msg="no compatible GPUs discovered"'))
    assert r.returncode == 1
    assert "FELL BACK" in r.stdout


def test_an_unreadable_backend_line_fails(run_confirm):
    r = run_confirm(stamped("inference compute id=0 (format drift: no library field)"))
    assert r.returncode == 1
    assert "UNREAD" in r.stdout


def test_a_missing_gpu_line_stays_report_only(run_confirm):
    r = run_confirm(stamped('msg="Listening on http://0.0.0.0:11435"'))
    assert r.returncode == 0
    assert "no GPU line in recent logs" in r.stdout


def test_an_empty_journal_stays_report_only(run_confirm):
    r = run_confirm("")
    assert r.returncode == 0
    assert "no GPU line in recent logs" in r.stdout


def test_the_latest_inference_line_decides(run_confirm):
    older = "2026-10-03T17:59:59.000000-07:00 host ollama-rocm[421]: " + VULKAN + "\n"
    newer = "2026-10-03T18:00:00.000000-07:00 host ollama-rocm[421]: " + ROCM + "\n"
    assert run_confirm(older + newer).returncode == 0
    assert run_confirm(newer + older).returncode == 1


def test_backend_match_is_case_insensitive(run_confirm):
    r = run_confirm(stamped("Inference Compute id=0 library=VULKAN"))
    assert r.returncode == 1


def test_the_task_fails_loudly_without_stopping_the_run():
    task = harness.confirm_task()
    assert task.get("ignore_errors") is True
    assert "failed_when" not in task


def test_the_report_still_follows_the_confirm():
    tasks = harness.load_tasks()
    i = next(
        i for i, t in enumerate(tasks) if harness.CONFIRM_NAME in (t.get("name") or "")
    )
    assert harness.REPORT_NAME in (tasks[i + 1].get("name") or "")
