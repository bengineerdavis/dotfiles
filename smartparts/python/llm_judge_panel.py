"""
llm_judge_panel — reusable LLM judge panel with round-robin fallback,
session-level failure tracking, and persistent SaaS auth disqualification.

Used in: binned, (future scripts)

── How to load in a uv script ────────────────────────────────────────────────
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path.home() / ".local/share/chezmoi/smartparts/python"))
    from llm_judge_panel import (
        JudgeScore, run_judge_panel,
        disqualify_saas, get_disqualified_saas, recheck_disqualified_saas,
    )

── Pattern summary ────────────────────────────────────────────────────────────
1. Define a judge system prompt and build a list of model aliases (judge_models).
2. Call run_judge_panel(script, name, judges, cfg=cfg) — it handles:
     • Retries with exponential backoff per judge
     • Auth-error detection → persistent SaaS disqualification (state.json)
     • Session-level failure counting → skip thrashing models for the run
     • Round-robin fallback from local_judge_pool / saas_judge_fallbacks in cfg
     • Pre-approved fallbacks (in config) used silently; others need confirmation
3. Inspect the returned list[JudgeScore] sorted best→worst by mean score.

── Fallback config keys (read from the cfg dict passed to run_judge_panel) ───
    local_judge_pool      comma-separated ordered list of up to 8 local models
    saas_judge_fallbacks  comma-separated ordered list of up to 3 SaaS models
    judge_timeout_seconds per-judge subprocess timeout  (default 180)
    judge_recheck_hours   hours before retesting a disqualified SaaS  (default 24)

── State file ────────────────────────────────────────────────────────────────
    STATE_FILE  (~/.binned/state.json by default, override via BINNED_HOME env)
    Stores { "disqualified_saas": { model: { reason, disqualified_at } } }
"""
from __future__ import annotations

import datetime
import json
import os
import pathlib
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import NamedTuple

# ── State paths ────────────────────────────────────────────────────────────────

_BINNED_DIR = pathlib.Path(os.environ.get("BINNED_HOME", str(pathlib.Path.home() / ".binned")))
STATE_FILE  = _BINNED_DIR / "state.json"

# ── Session-level failure tracking (reset each process) ───────────────────────

_SESSION_FAILURE_COUNTS: dict[str, int] = {}
_SESSION_SKIP:           set[str]       = set()
_SESSION_FAIL_THRESHOLD: int            = 2   # failures before a model is skipped this session


def record_session_failure(alias: str) -> None:
    """Increment the session failure count; add to skip set at threshold."""
    _SESSION_FAILURE_COUNTS[alias] = _SESSION_FAILURE_COUNTS.get(alias, 0) + 1
    if _SESSION_FAILURE_COUNTS[alias] >= _SESSION_FAIL_THRESHOLD:
        _SESSION_SKIP.add(alias)
        _warn(f"Judge {alias!r} failed {_SESSION_FAILURE_COUNTS[alias]} times — "
              f"skipping for the rest of this session.")


# ── Auth disqualification (persistent) ────────────────────────────────────────

_AUTH_RE = re.compile(
    r"no (api )?key|api key|401|403|unauthorized|forbidden|invalid.*(token|key)|"
    r"authentication (failed|error)|key not found|access denied",
    re.IGNORECASE,
)


def is_auth_error(text: str) -> bool:
    return bool(_AUTH_RE.search(text))


def _load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def _save_state(state: dict) -> None:
    _BINNED_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def disqualify_saas(model: str, reason: str) -> None:
    """Persistently ban a SaaS model from the judge pool until recheck passes."""
    state = _load_state()
    state.setdefault("disqualified_saas", {})[model] = {
        "reason": reason,
        "disqualified_at": datetime.datetime.utcnow().isoformat(),
    }
    _save_state(state)
    _warn(f"SaaS judge {model!r} disqualified ({reason}). "
          f"Will recheck after judge_recheck_hours.")


def get_disqualified_saas() -> set[str]:
    return set(_load_state().get("disqualified_saas", {}).keys())


def recheck_disqualified_saas(cfg: dict) -> None:
    """
    For any SaaS model disqualified longer than cfg['judge_recheck_hours'] ago,
    probe it with a cheap 'llm -m MODEL ping'.  Re-enable if it succeeds.
    """
    state        = _load_state()
    disqualified = state.get("disqualified_saas", {})
    if not disqualified:
        return

    recheck_hours = int(cfg.get("judge_recheck_hours", 24))
    now           = datetime.datetime.utcnow()
    changed       = False

    for model, info in list(disqualified.items()):
        try:
            banned_at = datetime.datetime.fromisoformat(info["disqualified_at"])
        except Exception:
            continue
        if (now - banned_at).total_seconds() / 3600 < recheck_hours:
            continue
        try:
            r = subprocess.run(["llm", "-m", model, "ping"],
                               capture_output=True, text=True, timeout=15)
            if r.returncode == 0:
                del disqualified[model]
                changed = True
                print(f"  SaaS judge {model!r} re-enabled (auth check passed).", flush=True)
        except Exception:
            pass

    if changed:
        _save_state(state)


# ── Judge score ────────────────────────────────────────────────────────────────

class JudgeScore(NamedTuple):
    model:       str
    structure:   int
    correctness: int
    safety:      int
    style:       int
    completeness: int
    verdict:     str
    note:        str
    mean:        float


# ── Model category helpers ────────────────────────────────────────────────────

_SAAS_PREFIXES = (
    "claude", "gpt", "o1", "o3", "o4", "gemini", "mistral-",
    "codestral-", "command", "sonar", "llama-api",
)


def _judge_model_category(alias: str) -> str:
    return "saas" if any(alias.lower().startswith(p) for p in _SAAS_PREFIXES) else "local"


def _is_preapproved_fallback(model: str, cfg: dict) -> bool:
    for key in ("local_judge_pool", "saas_judge_fallbacks"):
        raw = cfg.get(key, "") or ""
        if model in [m.strip() for m in raw.split(",") if m.strip()]:
            return True
    return False


def get_judge_fallback(failed_alias: str, cfg: dict, exclude: set[str]) -> str | None:
    """
    Return the next fallback model for a failed judge, skipping session-skipped
    and persistently-disqualified models.

    Local failures   → walk local_judge_pool (ordered, up to 8)
    SaaS failures    → walk saas_judge_fallbacks (ordered, up to 3)
    """
    category     = _judge_model_category(failed_alias)
    disqualified = get_disqualified_saas()
    skip         = exclude | _SESSION_SKIP

    if category == "local":
        pool = [m.strip() for m in (cfg.get("local_judge_pool", "") or "").split(",") if m.strip()]
        for m in pool:
            if m not in skip:
                return m
        return None
    else:
        fallbacks = [m.strip() for m in (cfg.get("saas_judge_fallbacks", "") or "").split(",") if m.strip()]
        for m in fallbacks:
            if m not in skip and m not in disqualified:
                return m
        return None


# ── Single judge run ──────────────────────────────────────────────────────────

_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*", re.MULTILINE)
_FENCE_END_RE  = re.compile(r"```\s*$",          re.MULTILINE)


def run_single_judge(
    alias:       str,
    system:      str,
    prompt:      str,
    timeout_s:   int = 180,
    max_retries: int = 2,
) -> JudgeScore | None:
    """
    Ask one judge model to score a prompt.

    Auth errors on SaaS models are detected and cause immediate disqualification
    (no retries).  Other failures are retried with exponential backoff.
    Returns None on total failure.
    """
    category  = _judge_model_category(alias)
    last_exc: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            result = subprocess.run(
                ["llm", "-m", alias, "--system", system, prompt],
                capture_output=True, text=True, timeout=timeout_s,
            )
            if result.returncode != 0:
                stderr = result.stderr[:400]
                if category != "local" and is_auth_error(stderr):
                    disqualify_saas(alias, f"auth error: {stderr[:120].strip()}")
                    return None
                raise RuntimeError(stderr)

            raw     = result.stdout.strip()
            cleaned = _JSON_FENCE_RE.sub("", raw)
            cleaned = _FENCE_END_RE.sub("", cleaned).strip()
            data    = json.loads(cleaned)
            scores  = [data["structure"], data["correctness"], data["safety"],
                       data["style"], data["completeness"]]
            return JudgeScore(
                model=alias,
                structure=int(data["structure"]),
                correctness=int(data["correctness"]),
                safety=int(data["safety"]),
                style=int(data["style"]),
                completeness=int(data["completeness"]),
                verdict=data.get("verdict", "needs-work"),
                note=data.get("note", ""),
                mean=sum(scores) / len(scores),
            )
        except Exception as exc:
            last_exc = exc
            if attempt < max_retries:
                wait_s = 2 ** attempt
                _warn(f"Judge {alias!r} attempt {attempt+1}/{max_retries+1} failed "
                      f"— retrying in {wait_s}s… ({exc})")
                time.sleep(wait_s)

    _warn(f"Judge {alias!r} exhausted {max_retries+1} attempt(s): {last_exc}")
    return None


# ── Panel runner ──────────────────────────────────────────────────────────────

def run_judge_panel(
    system:            str,
    prompt:            str,
    judges:            list[str],
    name:              str  = "script",
    fallback_on_error: bool = True,
    timeout_s:         int  = 180,
    cfg:               dict | None = None,
    confirm_fallback:  bool = True,
) -> list[JudgeScore]:
    """
    Run all judges in parallel with retry, fallback, and disqualification logic.

    Parameters:
        system            LLM system prompt for the judge.
        prompt            The user prompt (script + task) to score.
        judges            Primary judge model aliases.
        name              Label used in log messages.
        fallback_on_error When a judge fails after retries, try a fallback model.
        timeout_s         Per-judge subprocess timeout.
        cfg               Config dict with local_judge_pool / saas_judge_fallbacks.
        confirm_fallback  If True and fallback is not pre-approved, ask the user.

    Returns:
        list[JudgeScore] sorted best → worst by mean score.
    """
    effective_cfg = cfg or {}

    # Recheck any aged-out disqualified SaaS models before the panel starts
    recheck_disqualified_saas(effective_cfg)

    # Drop judges that are already session-skipped or disqualified
    disqualified   = get_disqualified_saas()
    active_judges  = [m for m in judges if m not in _SESSION_SKIP and m not in disqualified]
    skipped        = set(judges) - set(active_judges)
    if skipped:
        _warn(f"Skipping judges (session-skip or disqualified): {', '.join(sorted(skipped))}")

    used:    set[str]        = set(active_judges) | skipped
    results: list[JudgeScore] = []

    if not active_judges:
        _warn("No active judges to run.")
        return results

    with ThreadPoolExecutor(max_workers=max(len(active_judges), 1)) as pool:
        futures = {
            pool.submit(run_single_judge, m, system, prompt, timeout_s): m
            for m in active_judges
        }
        for fut in as_completed(futures):
            alias = futures[fut]
            score = fut.result()
            if score is not None:
                results.append(score)
            elif fallback_on_error:
                record_session_failure(alias)
                fallback = get_judge_fallback(alias, effective_cfg, used)
                if not fallback:
                    continue
                preapproved = _is_preapproved_fallback(fallback, effective_cfg)
                if preapproved or not confirm_fallback:
                    _info(f"Judge {alias!r} failed — using fallback {fallback!r}")
                    use_it = True
                else:
                    ans = input(f"Judge {alias!r} failed. Use fallback {fallback!r}? [Y/n] ").strip().lower()
                    use_it = ans not in ("n", "no")
                if use_it:
                    used.add(fallback)
                    fb_score = run_single_judge(fallback, system, prompt, timeout_s)
                    if fb_score is not None:
                        results.append(fb_score)
                    else:
                        record_session_failure(fallback)

    if not results:
        _warn("All judges in this panel returned no scores.")

    return sorted(results, key=lambda s: s.mean, reverse=True)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _warn(msg: str) -> None:
    print(f"⚠  {msg}", file=sys.stderr, flush=True)


def _info(msg: str) -> None:
    print(f"ℹ  {msg}", flush=True)
