"""
Unit tests for llm_call and llm_continue_call.
Patches subprocess to avoid real LLM calls.
"""
from __future__ import annotations

import pytest


class _FakeResult:
    def __init__(self, stdout="output\n", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


# ── llm_continue_call ─────────────────────────────────────────────────────────

class TestLlmContinueCall:
    def test_uses_cid_when_conv_id_provided(self, binned_module, monkeypatch):
        captured = []
        monkeypatch.setattr(
            binned_module.subprocess, "run",
            lambda cmd, **kw: captured.append(cmd) or _FakeResult(),
        )
        binned_module.llm_continue_call("hello", conv_id="abc123", stream=False)
        assert captured, "subprocess.run was not called"
        cmd = captured[0]
        assert "--cid" in cmd
        assert cmd[cmd.index("--cid") + 1] == "abc123"

    def test_does_not_use_uppercase_c(self, binned_module, monkeypatch):
        captured = []
        monkeypatch.setattr(
            binned_module.subprocess, "run",
            lambda cmd, **kw: captured.append(cmd) or _FakeResult(),
        )
        binned_module.llm_continue_call("hello", conv_id="abc123", stream=False)
        assert "-C" not in captured[0], "-C is not a valid llm flag; must use --cid"

    def test_uses_continue_when_no_conv_id(self, binned_module, monkeypatch):
        captured = []
        monkeypatch.setattr(
            binned_module.subprocess, "run",
            lambda cmd, **kw: captured.append(cmd) or _FakeResult(),
        )
        binned_module.llm_continue_call("hello", conv_id=None, stream=False)
        cmd = captured[0]
        assert "--continue" in cmd
        assert "--cid" not in cmd

    def test_passes_model_flag(self, binned_module, monkeypatch):
        captured = []
        monkeypatch.setattr(
            binned_module.subprocess, "run",
            lambda cmd, **kw: captured.append(cmd) or _FakeResult(),
        )
        binned_module.llm_continue_call("hello", model="gpt-4o", stream=False)
        cmd = captured[0]
        assert "-m" in cmd
        assert cmd[cmd.index("-m") + 1] == "gpt-4o"

    def test_omits_model_flag_when_none(self, binned_module, monkeypatch):
        captured = []
        monkeypatch.setattr(
            binned_module.subprocess, "run",
            lambda cmd, **kw: captured.append(cmd) or _FakeResult(),
        )
        binned_module.llm_continue_call("hello", model=None, stream=False)
        assert "-m" not in captured[0]

    def test_raises_on_nonzero_exit(self, binned_module, monkeypatch):
        monkeypatch.setattr(
            binned_module.subprocess, "run",
            lambda *a, **kw: _FakeResult(returncode=1, stderr="llm error text"),
        )
        with pytest.raises(RuntimeError, match="llm error text"):
            binned_module.llm_continue_call("hello", stream=False)

    def test_returns_stdout_on_success(self, binned_module, monkeypatch):
        monkeypatch.setattr(
            binned_module.subprocess, "run",
            lambda *a, **kw: _FakeResult(stdout="improved script\n"),
        )
        result = binned_module.llm_continue_call("hello", stream=False)
        assert result == "improved script\n"


# ── llm_call ──────────────────────────────────────────────────────────────────

class TestLlmCall:
    def test_returns_stdout_on_success(self, binned_module, monkeypatch):
        monkeypatch.setattr(
            binned_module.subprocess, "run",
            lambda *a, **kw: _FakeResult(stdout="generated script\n"),
        )
        result = binned_module.llm_call("prompt text", stream=False)
        assert result == "generated script\n"

    def test_raises_on_nonzero_exit(self, binned_module, monkeypatch):
        monkeypatch.setattr(
            binned_module.subprocess, "run",
            lambda *a, **kw: _FakeResult(returncode=1, stderr="model error"),
        )
        with pytest.raises(RuntimeError, match="model error"):
            binned_module.llm_call("prompt", stream=False)

    def test_passes_system_prompt(self, binned_module, monkeypatch):
        captured = []
        monkeypatch.setattr(
            binned_module.subprocess, "run",
            lambda cmd, **kw: captured.append(cmd) or _FakeResult(),
        )
        binned_module.llm_call("prompt", system="be concise", stream=False)
        cmd = captured[0]
        assert "-s" in cmd
        assert cmd[cmd.index("-s") + 1] == "be concise"

    def test_omits_system_flag_when_none(self, binned_module, monkeypatch):
        captured = []
        monkeypatch.setattr(
            binned_module.subprocess, "run",
            lambda cmd, **kw: captured.append(cmd) or _FakeResult(),
        )
        binned_module.llm_call("prompt", system=None, stream=False)
        assert "-s" not in captured[0]

    def test_passes_model_flag(self, binned_module, monkeypatch):
        captured = []
        monkeypatch.setattr(
            binned_module.subprocess, "run",
            lambda cmd, **kw: captured.append(cmd) or _FakeResult(),
        )
        binned_module.llm_call("prompt", model="claude-4-sonnet", stream=False)
        cmd = captured[0]
        assert "-m" in cmd
        assert cmd[cmd.index("-m") + 1] == "claude-4-sonnet"
