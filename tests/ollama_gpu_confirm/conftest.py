"""Fixtures for the per-GPU confirm tests."""

from __future__ import annotations

import pathlib

import pytest

import confirm_harness as harness


@pytest.fixture
def run_confirm(tmp_path):
    """Run the rendered confirm script against a stubbed journalctl."""

    def run(journal_log: str, item_name: str = "ollama-rocm"):
        return harness.run_confirm(
            harness.confirm_script(item_name), journal_log, pathlib.Path(tmp_path)
        )

    return run
