"""The workflow's test step must survive pytest exiting nonzero.

GitHub runs every `run:` block under `bash -e` with pipefail. pytest exits
1 on the NORMAL path here — that is what a known failure does — so a step
that pipes pytest into `tee` without disabling errexit dies at the pipeline
and never reaches the baseline comparison.

Measured 2026-11-24 (job 871): with `set -o pipefail` and errexit on, the
step exited 1 and wrote neither the status file nor anything after the pipe.
The job went red for a reason nobody could read. These tests execute the
step body, because the bug was invisible to every test of the Python gate.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "tests.yml"


def _step_script(name: str) -> str:
    """The `run:` body of a named workflow step.

    Read by hand rather than with a YAML parser: this suite already depends on
    pyyaml only where the repo does, and a missing parse library must not turn
    a CI guard into a skip.
    """
    text = WORKFLOW.read_text()
    marker = f"- name: {name}"
    start = text.index(marker)
    body = text[start:]
    run_at = body.index("run: |")
    block = body[run_at:].splitlines()[1:]
    lines = []
    for line in block:
        if line.strip() and not line.startswith(" " * 10):
            break
        lines.append(line[10:] if len(line) >= 10 else "")
    return "\n".join(lines).rstrip() + "\n"


def _run_step(
    tmp_path: Path, pytest_exit: int, *, tee_fails: bool = False
) -> subprocess.CompletedProcess:
    """Execute the Tests step against a stub pytest that exits `pytest_exit`."""
    stub = tmp_path / "bin"
    stub.mkdir()
    if tee_fails:
        broken = stub / "tee"
        broken.write_text("#!/bin/sh\nexit 1\n")
        broken.chmod(0o755)
    fake_uv = stub / "uv"
    fake_uv.write_text(
        "#!/bin/sh\n"
        "# Stub: `uv run ... pytest` exits with the status the test chose.\n"
        f"exit {pytest_exit}\n"
    )
    fake_uv.chmod(0o755)

    script = tmp_path / "step.sh"
    script.write_text(_step_script("Tests").replace("$RUNNER_TEMP", str(tmp_path)))

    return subprocess.run(
        ["bash", "-e", "-o", "pipefail", str(script)],
        env={"PATH": f"{stub}:/usr/bin:/bin", "RUNNER_TEMP": str(tmp_path)},
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("pytest_exit", [0, 1])
def test_the_step_records_the_status_and_stays_green(tmp_path, pytest_exit):
    """Exit 0 and the repo's normal exit 1 both reach the comparison step."""
    result = _run_step(tmp_path, pytest_exit)
    assert result.returncode == 0, result.stderr
    recorded = (tmp_path / "pytest.status").read_text().strip()
    assert recorded == str(pytest_exit)


def test_the_tests_step_disables_errexit_around_the_pipeline():
    """The step keeps errexit off while pytest and tee run."""
    body = _step_script("Tests")
    assert "set +e" in body, "errexit must be off while pytest and tee run"
    assert "PIPESTATUS[@]" in body, "both statuses, not just pytest's"
    set_plus_e = body.index("set +e")
    capture = body.index("PIPESTATUS[@]")
    set_minus_e = body.index("set -e", capture)
    assert set_plus_e < capture < set_minus_e


def test_the_comparison_step_passes_the_recorded_status():
    """The gate requires the flag, so the step must supply it."""
    body = _step_script("Compare failures against the known-failure baseline")
    assert "--pytest-exit-code" in body
    assert re.search(r"pytest\.status", body)


def test_a_lost_log_fails_the_step(tmp_path):
    """Disabling errexit must not also swallow tee's failure.

    With only PIPESTATUS[0] kept, a tee that cannot write the log exited 0 from
    the step while the run's output was gone — the job would then be judged on
    XML alone and be undiagnosable if anything went wrong (job 878).
    """
    result = _run_step(tmp_path, 0, tee_fails=True)
    assert result.returncode == 1
    assert "could not write" in result.stdout
    assert not (tmp_path / "pytest.status").exists()
