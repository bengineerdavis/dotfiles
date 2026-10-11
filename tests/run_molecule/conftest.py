"""Fixtures only — the helpers live in run_molecule_harness.py.

Every conftest is imported as a top-level module named `conftest`, so
helpers here would collide with every other suite's conftest
(tests/restart_stale records the trap).
"""

from __future__ import annotations

import pathlib

import pytest

from run_molecule_harness import make_scenario_repo


@pytest.fixture
def scenario_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    return make_scenario_repo(tmp_path)
