"""Harness for the run-molecule.sh argument-handling tests.

Deliberately not conftest.py: every conftest is imported as a top-level
module named `conftest`, so `from conftest import ...` resolves to
whichever one pytest imported first (tests/restart_stale records the
trap). Helpers live here under their own name.

The tests run the wrapper against a throwaway repo layout in tmp: the
script is copied in, a placeholder scenario is created for a fake topic,
and a fake `uv` on PATH logs every invocation (argv, cwd, the env the
wrapper exports) and exits 0. No VM, no molecule, no uv — these tests
own only the wrapper's argument handling and setup. The molecule run
itself is the scenario's verify phase, a live VM test.
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "run-molecule.sh"

FAKE_UV = r"""#!/bin/sh
# The separator avoids a leading dash on purpose: dash's printf parses
# '---' as an option ("Illegal option --") and the separator vanishes,
# silently merging every invocation into one log record.
{
  printf 'cwd=%s\n' "$PWD"
  for arg in "$@"; do printf 'arg=%s\n' "$arg"; done
  printf 'env-mpd=%s\n' "${MOLECULE_PROJECT_DIRECTORY-}"
  printf 'env-acp=%s\n' "${ANSIBLE_COLLECTIONS_PATH-}"
  printf '===END===\n'
} >> "$UV_LOG"
exit 0
"""


def parse_log(log: pathlib.Path) -> list[dict[str, list[str]]]:
    """Parse the fake uv's log into one record per invocation.

    Each record: {"cwd": [..], "args": [...], "env-mpd": [...], ...} —
    values are lists because the raw log repeats every key.
    """
    blocks = [b for b in log.read_text().split("===END===\n") if b.strip()]
    records = []
    for block in blocks:
        record: dict[str, list[str]] = {}
        for line in block.strip().splitlines():
            key, _, value = line.partition("=")
            record.setdefault(key, []).append(value)
        records.append(record)
    return records


def make_scenario_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    """A throwaway repo: the script, a scenario, a fake uv on PATH."""
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    shutil.copy2(SCRIPT, repo / "scripts" / "run-molecule.sh")

    scenario = repo / "dotfiles" / "apps" / "faketopic" / "molecule" / "default"
    scenario.mkdir(parents=True)
    (scenario / "molecule.yml").touch()

    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    uv = fake_bin / "uv"
    uv.write_text(FAKE_UV)
    uv.chmod(0o755)

    (repo / "uv.log").touch()
    return repo


def run_wrapper(
    scenario_repo: pathlib.Path, *args: str, cwd: pathlib.Path | None = None
) -> subprocess.CompletedProcess[str]:
    """Run the copied wrapper with the fake uv first on PATH."""
    env = dict(os.environ)
    env["PATH"] = f"{scenario_repo.parent / 'fake-bin'}:{env['PATH']}"
    env["UV_LOG"] = str(scenario_repo / "uv.log")
    return subprocess.run(
        [str(scenario_repo / "scripts" / "run-molecule.sh"), *args],
        cwd=str(cwd or scenario_repo),
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )


def molecule_invocations(scenario_repo: pathlib.Path) -> list[list[str]]:
    """The argv lists of every uv call that ran molecule.

    Tolerates an empty log: the negative tests assert no invocation
    happened and need [] back. Positive tests unpack the result, so an
    empty log still fails them — after their rc assertion, with context.
    """
    return [
        r["arg"] for r in parse_log(scenario_repo / "uv.log") if "molecule" in r["arg"]
    ]


def molecule_records(scenario_repo: pathlib.Path) -> list[dict[str, list[str]]]:
    """The full log records of every uv call that ran molecule.

    Raises when the log is empty so a positive-path failure is not a
    cryptic unpack error; the negative paths expect [] and get it.
    """
    records = [r for r in parse_log(scenario_repo / "uv.log") if "molecule" in r["arg"]]
    assert records, "fake uv log is empty — the wrapper never invoked uv"
    return records
