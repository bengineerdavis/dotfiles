"""
Real-model tests for pii-redactor.

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

import pytest

from conftest import INTEGRATION_LLM_OPTS, INTEGRATION_MODEL

pytestmark = pytest.mark.llm_judge


@pytest.fixture
def real_env():
    if shutil.which("llm") is None:
        pytest.skip("llm not on PATH")
    return {**os.environ, "LLM_EXTRA_OPTS": INTEGRATION_LLM_OPTS}


def test_redacts_email_from_stdin(run_script, real_env):
    r = run_script(
        "-m", INTEGRATION_MODEL,
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
    r = run_script("-i", str(src), "-o", str(dst), "-m", INTEGRATION_MODEL, env=real_env)
    assert r.returncode == 0, r.stderr

    result = dst.read_text()
    assert "Jane Smith" not in result
    assert "555-867-5309" not in result
    assert "[" in result
