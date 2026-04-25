"""
Unit tests for binned's judge panel internals.
Does NOT make real LLM calls.

Covers:
  - Session failure tracking (_record_session_failure, _SESSION_SKIP)
  - Auth error detection (_is_auth_error)
  - Auth disqualification state persistence (_disqualify_saas, _get_disqualified_saas)
  - Fallback model selection (_get_judge_fallback)
  - Judge prefs assembly (_ensure_judge_prefs: disabled, no models, minimum-3 top-up)
"""
from __future__ import annotations

import json

import pytest


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _reset_session_state(binned_module):
    """Clear module-level session tracking dicts before and after each test."""
    binned_module._SESSION_FAILURE_COUNTS.clear()
    binned_module._SESSION_SKIP.clear()
    yield
    binned_module._SESSION_FAILURE_COUNTS.clear()
    binned_module._SESSION_SKIP.clear()


@pytest.fixture()
def state_dir(binned_module, tmp_path):
    """Redirect BINNED_DIR and STATE_FILE to a temp dir for state isolation."""
    orig_binned_dir = binned_module.BINNED_DIR
    orig_state_file = binned_module.STATE_FILE
    binned_module.BINNED_DIR = tmp_path
    binned_module.STATE_FILE = tmp_path / "state.json"
    yield tmp_path
    binned_module.BINNED_DIR = orig_binned_dir
    binned_module.STATE_FILE = orig_state_file


# ── Session failure tracking ──────────────────────────────────────────────────

class TestSessionFailureTracking:
    def test_single_failure_below_threshold(self, binned_module):
        binned_module._record_session_failure("model-x")
        assert "model-x" not in binned_module._SESSION_SKIP
        assert binned_module._SESSION_FAILURE_COUNTS["model-x"] == 1

    def test_threshold_triggers_skip(self, binned_module):
        threshold = binned_module._SESSION_FAIL_THRESHOLD
        for _ in range(threshold):
            binned_module._record_session_failure("model-x")
        assert "model-x" in binned_module._SESSION_SKIP

    def test_models_tracked_independently(self, binned_module):
        binned_module._record_session_failure("model-a")
        binned_module._record_session_failure("model-b")
        assert "model-a" not in binned_module._SESSION_SKIP
        assert "model-b" not in binned_module._SESSION_SKIP
        # Push model-a to threshold while model-b stays below
        for _ in range(binned_module._SESSION_FAIL_THRESHOLD - 1):
            binned_module._record_session_failure("model-a")
        assert "model-a" in binned_module._SESSION_SKIP
        assert "model-b" not in binned_module._SESSION_SKIP

    def test_count_exceeds_threshold_still_skipped(self, binned_module):
        threshold = binned_module._SESSION_FAIL_THRESHOLD
        for _ in range(threshold + 3):
            binned_module._record_session_failure("model-x")
        assert "model-x" in binned_module._SESSION_SKIP


# ── Auth error detection ──────────────────────────────────────────────────────

@pytest.mark.parametrize("text", [
    "Error: no api key configured",
    "no key found",
    "HTTP 401 Unauthorized",
    "403 Forbidden",
    "authentication failed",
    "authentication error",
    "invalid token provided",
    "invalid key",
    "access denied",
    "key not found",
    "api key missing",
])
def test_is_auth_error_matches(binned_module, text):
    assert binned_module._is_auth_error(text), f"expected auth error match for: {text!r}"


@pytest.mark.parametrize("text", [
    "RuntimeError: model not found",
    "timeout after 30s",
    "ollama: connection refused",
    "JSON decode error",
    "invalid JSON response",
    "",
])
def test_is_auth_error_no_match(binned_module, text):
    assert not binned_module._is_auth_error(text), f"unexpected auth match for: {text!r}"


# ── Auth disqualification state persistence ───────────────────────────────────

class TestDisqualification:
    def test_disqualify_writes_state_file(self, binned_module, state_dir, capsys):
        binned_module._disqualify_saas("bad-model", "no api key")
        state = json.loads((state_dir / "state.json").read_text())
        assert "bad-model" in state["disqualified_saas"]
        entry = state["disqualified_saas"]["bad-model"]
        assert "reason" in entry
        assert "disqualified_at" in entry

    def test_disqualify_stores_reason(self, binned_module, state_dir, capsys):
        binned_module._disqualify_saas("bad-model", "HTTP 401")
        state = json.loads((state_dir / "state.json").read_text())
        assert "HTTP 401" in state["disqualified_saas"]["bad-model"]["reason"]

    def test_disqualify_accumulates_multiple(self, binned_module, state_dir, capsys):
        binned_module._disqualify_saas("model-a", "401")
        binned_module._disqualify_saas("model-b", "no api key")
        banned = binned_module._get_disqualified_saas()
        assert "model-a" in banned
        assert "model-b" in banned

    def test_get_disqualified_reads_existing_state(self, binned_module, state_dir):
        (state_dir / "state.json").write_text(json.dumps({
            "disqualified_saas": {
                "model-x": {"reason": "403", "disqualified_at": "2026-01-01T00:00:00+00:00"}
            }
        }))
        assert "model-x" in binned_module._get_disqualified_saas()

    def test_get_disqualified_empty_when_no_state(self, binned_module, state_dir):
        assert binned_module._get_disqualified_saas() == set()

    def test_get_disqualified_empty_when_key_absent(self, binned_module, state_dir):
        (state_dir / "state.json").write_text(json.dumps({"other_key": "value"}))
        assert binned_module._get_disqualified_saas() == set()


# ── _get_judge_fallback ───────────────────────────────────────────────────────
# Use fake model names not in _RECOMMENDED_MODELS to avoid RAM filtering.
# _judge_model_category() classifies unknown names as "local" (no SaaS pattern match).
# Models containing "claude" or "gpt-" are classified as "saas" via heuristic.

class TestGetJudgeFallback:
    _POOL = "pool-a,pool-b,pool-c"

    def test_returns_first_available_pool_model(self, binned_module):
        cfg = {"local_judge_pool": self._POOL}
        result = binned_module._get_judge_fallback("failed-local", cfg, exclude={"failed-local"})
        assert result == "pool-a"

    def test_skips_excluded_models(self, binned_module):
        cfg = {"local_judge_pool": self._POOL}
        result = binned_module._get_judge_fallback(
            "failed-local", cfg, exclude={"failed-local", "pool-a"}
        )
        assert result == "pool-b"

    def test_skips_all_excluded_returns_third(self, binned_module):
        cfg = {"local_judge_pool": self._POOL}
        result = binned_module._get_judge_fallback(
            "failed-local", cfg, exclude={"failed-local", "pool-a", "pool-b"}
        )
        assert result == "pool-c"

    def test_skips_session_skipped_models(self, binned_module):
        binned_module._SESSION_SKIP.add("pool-a")
        cfg = {"local_judge_pool": self._POOL}
        result = binned_module._get_judge_fallback("failed-local", cfg, exclude={"failed-local"})
        assert result == "pool-b"

    def test_empty_pool_returns_none_or_installed(self, binned_module):
        cfg = {"local_judge_pool": ""}
        result = binned_module._get_judge_fallback("failed-local", cfg, exclude={"failed-local"})
        assert result is None or isinstance(result, str)

    def test_pool_fully_exhausted_returns_none_or_installed(self, binned_module):
        cfg = {"local_judge_pool": "pool-a"}
        result = binned_module._get_judge_fallback(
            "failed-local", cfg, exclude={"failed-local", "pool-a"}
        )
        assert result is None or isinstance(result, str)

    def test_saas_skips_disqualified(self, binned_module, state_dir, capsys):
        binned_module._disqualify_saas("saas-first", "no api key")
        # "claude-" prefix → saas category via heuristic
        cfg = {"saas_judge_fallbacks": "saas-first,saas-second"}
        result = binned_module._get_judge_fallback(
            "claude-primary", cfg, exclude={"claude-primary"}
        )
        assert result == "saas-second"

    def test_saas_returns_none_when_all_disqualified(self, binned_module, state_dir, capsys):
        binned_module._disqualify_saas("saas-first", "401")
        binned_module._disqualify_saas("saas-second", "403")
        cfg = {"saas_judge_fallbacks": "saas-first,saas-second"}
        result = binned_module._get_judge_fallback(
            "claude-primary", cfg, exclude={"claude-primary"}
        )
        assert result is None

    def test_saas_skips_session_skipped(self, binned_module, state_dir):
        binned_module._SESSION_SKIP.add("saas-first")
        cfg = {"saas_judge_fallbacks": "saas-first,saas-second"}
        result = binned_module._get_judge_fallback(
            "claude-primary", cfg, exclude={"claude-primary"}
        )
        assert result == "saas-second"


# ── _ensure_judge_prefs ───────────────────────────────────────────────────────

class TestEnsureJudgePrefs:
    def test_disabled_returns_false_and_empty_lists(self, binned_module):
        cfg = {"run_judges": False}
        should_run, local, saas = binned_module._ensure_judge_prefs(cfg)
        assert should_run is False
        assert local == []
        assert saas == []

    def test_empty_judge_models_returns_false(self, binned_module):
        cfg = {"run_judges": True, "judge_models": ""}
        should_run, local, saas = binned_module._ensure_judge_prefs(cfg)
        assert should_run is False

    def test_whitespace_only_judge_models_returns_false(self, binned_module):
        cfg = {"run_judges": True, "judge_models": "  ,  "}
        should_run, local, saas = binned_module._ensure_judge_prefs(cfg)
        assert should_run is False

    def test_single_judge_tops_up_to_three(self, binned_module):
        cfg = {
            "run_judges": True,
            "judge_models": "test-judge-a",
            "local_judge_pool": "test-pool-x,test-pool-y,test-pool-z",
        }
        should_run, local, saas = binned_module._ensure_judge_prefs(cfg)
        assert should_run is True
        assert len(local) + len(saas) >= 3
        assert "test-judge-a" in local

    def test_two_judges_tops_up_to_three(self, binned_module):
        cfg = {
            "run_judges": True,
            "judge_models": "test-judge-a,test-judge-b",
            "local_judge_pool": "test-pool-x,test-pool-y",
        }
        should_run, local, saas = binned_module._ensure_judge_prefs(cfg)
        assert should_run is True
        assert len(local) + len(saas) >= 3

    def test_three_judges_no_extra_topup(self, binned_module):
        cfg = {
            "run_judges": True,
            "judge_models": "test-judge-a,test-judge-b,test-judge-c",
            "local_judge_pool": "test-pool-x,test-pool-y",
        }
        should_run, local, saas = binned_module._ensure_judge_prefs(cfg)
        assert should_run is True
        total = len(local) + len(saas)
        assert total == 3
        pool_models = {"test-pool-x", "test-pool-y"}
        assert not (set(local) | set(saas)) & pool_models

    def test_topup_does_not_duplicate_existing_panel_models(self, binned_module):
        cfg = {
            "run_judges": True,
            "judge_models": "test-judge-a",
            "local_judge_pool": "test-judge-a,test-pool-x,test-pool-y",
        }
        should_run, local, saas = binned_module._ensure_judge_prefs(cfg)
        assert should_run is True
        all_models = local + saas
        assert all_models.count("test-judge-a") == 1

    def test_returns_true_with_valid_config(self, binned_module):
        cfg = {
            "run_judges": True,
            "judge_models": "test-judge-a,test-judge-b,test-judge-c",
        }
        should_run, local, saas = binned_module._ensure_judge_prefs(cfg)
        assert should_run is True
        assert len(local) + len(saas) > 0
