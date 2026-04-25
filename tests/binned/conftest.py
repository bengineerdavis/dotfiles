"""
Shared pytest fixtures and configuration for binned test suite.

Run property tests:
    pytest tests/test_binned_property.py -v

Run LLM judge panel (requires real API calls):
    pytest -m llm_judge tests/test_binned_llm_judge.py -v -s
    pytest -m llm_judge --gen-model claude-4-sonnet --judges "claude-4-sonnet,gpt-4.1,gemini-2.5-flash" -v -s
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import pathlib
import sys

import pytest

BINNED_PATH = pathlib.Path.home() / "bin" / "binned"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--gen-model",
        default=None,
        help="llm alias to use when generating scripts in judge tests",
    )
    parser.addoption(
        "--judges",
        default="devstral-small-2,qwen3.5,claude-4-sonnet",
        help="Comma-separated llm aliases for the judge panel (default: 2 local + 1 cloud)",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "llm_judge: tests that call real LLM APIs — slow and costs tokens. "
        "Run with: pytest -m llm_judge",
    )


@pytest.fixture(scope="session")
def binned_module():
    """
    Import binned as a Python module so tests can call its functions directly.
    Skips the entire session if typer/questionary are not installed in this
    environment (install with: pip install typer questionary).
    """
    if not BINNED_PATH.exists():
        pytest.skip(f"binned not found at {BINNED_PATH} — run: chezmoi apply ~/bin/binned")
    try:
        # binned has no .py extension so spec_from_file_location returns None;
        # SourceFileLoader tells Python to treat it as Python source regardless.
        loader = importlib.machinery.SourceFileLoader("binned", str(BINNED_PATH))
        spec = importlib.util.spec_from_loader("binned", loader, origin=str(BINNED_PATH))
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        loader.exec_module(mod)
        return mod
    except ImportError as exc:
        pytest.skip(f"binned deps not installed ({exc}). Run: pip install typer questionary")


@pytest.fixture(scope="session")
def gen_model(request: pytest.FixtureRequest) -> str | None:
    return request.config.getoption("--gen-model")  # type: ignore[return-value]


@pytest.fixture(scope="session")
def judge_models(request: pytest.FixtureRequest) -> list[str]:
    raw: str = request.config.getoption("--judges")  # type: ignore[assignment]
    return [m.strip() for m in raw.split(",") if m.strip()]
