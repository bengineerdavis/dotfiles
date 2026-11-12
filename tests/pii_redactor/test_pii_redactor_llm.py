"""Real-model tests for pii-redactor.

Marked llm_judge so they stay out of the default run: they load a local model
and cost real time. Run them with:

    pytest -m llm_judge tests/pii_redactor -v -s

These are the two integration cases from the bats suite. They assert the PII is
gone and a placeholder appeared, deliberately without pinning the exact wording
— the model chooses the placeholder, and asserting on its phrasing would make
the test fail on a model change rather than on a regression.
"""

from __future__ import annotations

import os
import shutil
import subprocess

import pytest

# pyrefly: ignore [missing-import]
from pii_redactor_harness import INTEGRATION_LLM_OPTS, INTEGRATION_MODEL

pytestmark = pytest.mark.llm_judge


@pytest.fixture
def real_env():
    if shutil.which("llm") is None:
        pytest.skip("llm not on PATH")
    # The integration model is a real local Ollama tag. It is absent on
    # machines that never pulled it (the second machine, DOT-73 2026-09-14),
    # and `llm -m <absent>` fails inside the test with an error that looks
    # like a redactor bug. Name the absence and skip instead — a capable
    # machine still exercises these tests.
    if shutil.which("ollama") is None:
        # Guard the binary before probing it: without this a missing ollama
        # raises FileNotFoundError from subprocess.run instead of skipping
        # with a reason — the environmental-failure shape DOT-73 closes out.
        pytest.skip("ollama not on PATH — cannot confirm the integration model")
    try:
        probe = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        pytest.skip("ollama not on PATH — cannot confirm the integration model")
    if probe.returncode != 0:
        pytest.skip("ollama not reachable — cannot confirm the integration model")
    installed = {line.split()[0] for line in probe.stdout.splitlines() if line.strip()}
    if INTEGRATION_MODEL not in installed:
        pytest.skip(
            f"integration model {INTEGRATION_MODEL} not installed "
            "— run: ollama pull " + INTEGRATION_MODEL
        )
    return {**os.environ, "LLM_EXTRA_OPTS": INTEGRATION_LLM_OPTS}


def test_redacts_email_from_stdin(run_script, real_env):
    r = run_script(
        "-m",
        INTEGRATION_MODEL,
        stdin="Please contact support at john.doe@example.com for help.\n",
        env=real_env,
    )
    assert r.returncode == 0, r.stderr
    assert "john.doe@example.com" not in r.stdout
    assert "[" in r.stdout


def test_redacts_name_and_phone_from_file(run_script, real_env, tmp_path):
    src, dst = tmp_path / "in.md", tmp_path / "out.md"
    src.write_text(
        "Hi, my name is Jane Smith and you can reach me at 555-867-5309.\n"
        "I live at 123 Maple Street, Springfield.\n"
    )
    r = run_script(
        "-i", str(src), "-o", str(dst), "-m", INTEGRATION_MODEL, env=real_env
    )
    assert r.returncode == 0, r.stderr

    result = dst.read_text()
    assert "Jane Smith" not in result
    assert "555-867-5309" not in result
    assert "[" in result


def test_the_models_reasoning_never_reaches_stderr(run_script, real_env, tmp_path):
    """The PII must not survive in stderr either.

    A reasoning model narrates the redaction and quotes the values it removes,
    so its chain-of-thought on stderr carries the same PII the output had
    replaced — into logs and scrollback, which outlast the run. Asserting only
    on the output file is how that leak stayed invisible: the released artifact
    was clean while every run wrote the raw name to stderr.

    This test deliberately does NOT use INTEGRATION_LLM_OPTS. That sets
    `-o think false`, which suppresses reasoning at the model, so stderr stays
    clean whether or not the tool passes -R — the test would pass for the wrong
    reason. Measured: with reasoning on, the raw name appears 13 times on
    stderr without -R and 0 times with it. Slow by design; it is the only case
    that exercises the flag's actual purpose.
    """
    src, dst = tmp_path / "in.md", tmp_path / "out.md"
    src.write_text("Hi, my name is Jane Smith and my number is 555-867-5309.\n")
    r = run_script(
        "-i",
        str(src),
        "-o",
        str(dst),
        "-m",
        INTEGRATION_MODEL,
        env={**os.environ},  # no `-o think false`: reasoning must be possible
    )
    assert r.returncode == 0, r.stderr

    # The output is redacted...
    assert "Jane Smith" not in dst.read_text()
    # ...and so is everything the run said about itself.
    assert "Jane Smith" not in r.stderr
    assert "555-867-5309" not in r.stderr
