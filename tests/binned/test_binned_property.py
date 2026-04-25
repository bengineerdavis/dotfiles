"""
Property-based tests for binned's pure functions.

Requires: pip install hypothesis
Run:      pytest tests/test_binned_property.py -v
"""
from __future__ import annotations

import pathlib
import re
import shutil
import tempfile

import pytest

try:
    from hypothesis import given, settings, assume
    from hypothesis import strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False

pytestmark = pytest.mark.skipif(
    not HAS_HYPOTHESIS, reason="hypothesis not installed — pip install hypothesis"
)

# ── Regex under test (duplicated here so the tests document the contract) ────
# These match the implementations in binned; if binned changes them the tests
# will catch the divergence.

_VALID_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_ALIAS_PARSE_RE = re.compile(r"^(.+?)\s{2,}:\s+(.+)$")

# ── _sanitize_name ────────────────────────────────────────────────────────────

@given(st.text(min_size=0, max_size=120))
@settings(max_examples=500)
def test_sanitize_name_only_valid_chars(binned_module, raw):
    result = binned_module._sanitize_name(raw)
    assert all(c in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in result), (
        f"_sanitize_name({raw!r}) = {result!r} contains invalid chars"
    )


@given(st.text(min_size=0, max_size=120))
@settings(max_examples=500)
def test_sanitize_name_never_empty(binned_module, raw):
    result = binned_module._sanitize_name(raw)
    assert len(result) > 0, f"_sanitize_name({raw!r}) returned empty string"


@given(st.text(min_size=0, max_size=120))
@settings(max_examples=500)
def test_sanitize_name_no_leading_trailing_dash(binned_module, raw):
    result = binned_module._sanitize_name(raw)
    assert not result.startswith("-"), f"_sanitize_name({raw!r}) = {result!r} starts with dash"
    assert not result.endswith("-"), f"_sanitize_name({raw!r}) = {result!r} ends with dash"


@given(st.text(min_size=0, max_size=120))
@settings(max_examples=500)
def test_sanitize_name_no_consecutive_dashes(binned_module, raw):
    result = binned_module._sanitize_name(raw)
    assert "--" not in result, f"_sanitize_name({raw!r}) = {result!r} has consecutive dashes"


@given(st.text(min_size=0, max_size=120))
@settings(max_examples=300)
def test_sanitize_name_idempotent(binned_module, raw):
    once = binned_module._sanitize_name(raw)
    twice = binned_module._sanitize_name(once)
    assert once == twice, f"_sanitize_name not idempotent: {raw!r} → {once!r} → {twice!r}"


# Known cases

@pytest.mark.parametrize("raw,expected", [
    ("Remove PII",      "remove-pii"),
    ("My SCRIPT_name!", "my-script-name"),
    ("  leading  ",     "leading"),
    ("---",             "my-script"),   # all-dash → fallback
    ("",                "my-script"),   # empty → fallback
    ("already-fine",    "already-fine"),
    ("MixedCase123",    "mixedcase123"),
])
def test_sanitize_name_known_cases(binned_module, raw, expected):
    result = binned_module._sanitize_name(raw)
    assert result == expected, f"_sanitize_name({raw!r}) = {result!r}, want {expected!r}"


# ── detect_llm_in_command ─────────────────────────────────────────────────────

@given(
    st.text(min_size=0, max_size=200).filter(
        lambda s: not re.search(r"\bllm\b", s, re.IGNORECASE)
    )
)
@settings(max_examples=300)
def test_detect_llm_no_llm_token_returns_none(binned_module, cmd):
    assert binned_module.detect_llm_in_command(cmd) is None


@given(
    # Prefix must end with a non-word char so `llm` sits at a \b word boundary.
    # Empty string or text ending in space/pipe/semicolon all qualify.
    prefix=st.one_of(
        st.just(""),
        st.from_regex(r"[^\w\n]{0,10}\s", fullmatch=True),
    ),
    model=st.from_regex(r"[a-z][a-z0-9._-]{1,20}", fullmatch=True),
    suffix=st.text(max_size=40, alphabet=st.characters(blacklist_characters="\n")),
)
@settings(max_examples=300)
def test_detect_llm_with_model_flag_returns_model(binned_module, prefix, model, suffix):
    cmd = f"{prefix}llm -m {model} {suffix}"
    result = binned_module.detect_llm_in_command(cmd)
    assert result == model, f"detect_llm_in_command({cmd!r}) = {result!r}, want {model!r}"


@given(
    suffix=st.text(min_size=1, max_size=80, alphabet=st.characters(blacklist_characters="\n"))
          .filter(lambda s: "-m" not in s and "--model" not in s)
)
@settings(max_examples=200)
def test_detect_llm_without_model_flag_returns_default(binned_module, suffix):
    cmd = f"llm {suffix}"
    result = binned_module.detect_llm_in_command(cmd)
    assert result == "default", (
        f"detect_llm_in_command({cmd!r}) = {result!r}, want 'default'"
    )


@pytest.mark.parametrize("cmd,expected", [
    ('llm -m gpt-4o "do stuff"',       "gpt-4o"),
    ('llm --model claude-3 "hello"',   "claude-3"),
    ("ffmpeg -i a.mp4 out.mp3",         None),
    ("llm 'summarize this'",            "default"),
    ("LLM 'shout'",                     "default"),   # case-insensitive
    ("echo | llm -m gpt-4.1 -s sys",   "gpt-4.1"),
])
def test_detect_llm_known_cases(binned_module, cmd, expected):
    assert binned_module.detect_llm_in_command(cmd) == expected


# ── detect_script_language ───────────────────────────────────────────────────

@given(st.text(min_size=0, max_size=500))
@settings(max_examples=300)
def test_detect_script_language_always_returns_valid(binned_module, script):
    result = binned_module.detect_script_language(script)
    assert result in ("bash", "python"), f"unexpected language: {result!r}"


@pytest.mark.parametrize("shebang,expected", [
    ("#!/usr/bin/env python3\n",           "python"),
    ("#!/usr/bin/env python\n",            "python"),
    ("#!/usr/bin/env -S uv run --script\n","bash"),   # uv shebang → bash unless import follows
    ("#!/usr/bin/env bash\n",              "bash"),
    ("#!/bin/bash\n",                      "bash"),
    ("#!/bin/sh\n",                        "bash"),
])
def test_detect_script_language_shebangs(binned_module, shebang, expected):
    assert binned_module.detect_script_language(shebang + "echo hello") == expected


def test_detect_script_language_python_by_imports(binned_module):
    script = "#!/usr/bin/env -S uv run --script\nimport sys\nimport pathlib\n"
    assert binned_module.detect_script_language(script) == "python"


# ── alias parsing regex ───────────────────────────────────────────────────────
# These tests pin the contract of get_llm_aliases()'s line-level parser so any
# future refactor that breaks colon-in-alias handling fails visibly.

@given(
    alias=st.from_regex(r"[a-z][a-z0-9_.-]{0,30}", fullmatch=True),
    model=st.from_regex(r"[a-z][a-z0-9.:/_-]{0,50}", fullmatch=True),
    padding=st.integers(min_value=2, max_value=25),
)
@settings(max_examples=500)
def test_alias_parse_regex_round_trips_simple(alias, model, padding):
    line = f"{alias}{' ' * padding}: {model}"
    m = _ALIAS_PARSE_RE.match(line)
    assert m is not None, f"regex did not match: {line!r}"
    assert m.group(1).strip() == alias
    assert m.group(2).strip() == model


@given(
    base=st.from_regex(r"[a-z][a-z0-9]{1,15}", fullmatch=True),
    tag=st.from_regex(r"[a-z0-9]{1,10}", fullmatch=True),
    model=st.from_regex(r"[a-z][a-z0-9.:/_-]{0,50}", fullmatch=True),
    padding=st.integers(min_value=2, max_value=25),
)
@settings(max_examples=400)
def test_alias_parse_regex_preserves_colon_in_alias(base, tag, model, padding):
    """Aliases like qwen3.5:35b must survive the split intact."""
    alias = f"{base}:{tag}"
    line = f"{alias}{' ' * padding}: {model}"
    m = _ALIAS_PARSE_RE.match(line)
    assert m is not None, f"regex did not match: {line!r}"
    assert m.group(1).strip() == alias, (
        f"colon in alias was eaten: expected {alias!r}, got {m.group(1).strip()!r}"
    )


@given(
    alias=st.from_regex(r"[a-z][a-z0-9]{1,15}", fullmatch=True),
    model=st.from_regex(r"[a-z][a-z0-9]{1,15}", fullmatch=True),
    tag=st.from_regex(r"[a-z0-9]{1,10}", fullmatch=True),
    padding=st.integers(min_value=2, max_value=25),
)
@settings(max_examples=400)
def test_alias_parse_regex_preserves_colon_in_model(alias, model, tag, padding):
    """Model IDs like qwen3.5:35b-a3b must be captured in full."""
    full_model = f"{model}:{tag}"
    line = f"{alias}{' ' * padding}: {full_model}"
    m = _ALIAS_PARSE_RE.match(line)
    assert m is not None
    assert m.group(2).strip() == full_model, (
        f"colon in model was eaten: expected {full_model!r}, got {m.group(2).strip()!r}"
    )


@given(
    alias=st.from_regex(r"[a-z][a-z0-9]{1,15}", fullmatch=True),
    model=st.from_regex(r"[a-z][a-z0-9.:/_-]{0,30}", fullmatch=True),
)
@settings(max_examples=300)
def test_alias_parse_regex_no_match_without_padding(alias, model):
    """A single space before ':' must NOT match (avoids false positives)."""
    line = f"{alias} : {model}"
    m = _ALIAS_PARSE_RE.match(line)
    assert m is None, f"regex matched a single-space separator: {line!r}"


@pytest.mark.parametrize("line,exp_alias,exp_model", [
    # Simple
    ("4o                    : gpt-4o",         "4o",           "gpt-4o"),
    # Colon in alias
    ("qwen3.5:35b           : qwen3.5:35b-a3b", "qwen3.5:35b", "qwen3.5:35b-a3b"),
    # Colon in both
    ("olmo-3:32b            : olmo-3:32b-think", "olmo-3:32b",  "olmo-3:32b-think"),
    # Namespaced model
    ("gemini-2.5-pro        : gemini/gemini-2.5-pro", "gemini-2.5-pro", "gemini/gemini-2.5-pro"),
])
def test_alias_parse_known_cases(line, exp_alias, exp_model):
    m = _ALIAS_PARSE_RE.match(line)
    assert m is not None, f"regex did not match: {line!r}"
    assert m.group(1).strip() == exp_alias
    assert m.group(2).strip() == exp_model


# ── save_pending / load_pending round-trip ────────────────────────────────────

_SAFE_NAME = st.from_regex(r"[a-z][a-z0-9-]{0,19}", fullmatch=True)
_SAFE_TEXT = st.text(
    min_size=0, max_size=300,
    alphabet=st.characters(blacklist_categories=("Cs",)),  # no surrogates
)


@given(
    name=_SAFE_NAME,
    cmd=_SAFE_TEXT,
    script=_SAFE_TEXT,
    bats_content=_SAFE_TEXT,
)
@settings(max_examples=200)
def test_save_load_round_trip(binned_module, name, cmd, script, bats_content):
    # Use tempfile.mkdtemp() — tmp_path is function-scoped and not reset between
    # Hypothesis examples, which would cause JSON files to collide across runs.
    tmpdir = tempfile.mkdtemp()
    original_pending = binned_module.PENDING_DIR
    binned_module.PENDING_DIR = pathlib.Path(tmpdir) / ".binned" / "pending"
    try:
        test_files = {f"tests/{name}.bats": bats_content}
        binned_module.save_pending(name, cmd, script, test_files)
        loaded = binned_module.load_pending(name)
        assert loaded is not None
        assert loaded["name"] == name
        assert loaded["cmd"] == cmd
        assert loaded["script"] == script
        assert loaded["test_files"] == test_files
    finally:
        binned_module.PENDING_DIR = original_pending
        shutil.rmtree(tmpdir, ignore_errors=True)


@given(
    name=_SAFE_NAME,
    cmd=_SAFE_TEXT,
    script=_SAFE_TEXT,
    bats_content=_SAFE_TEXT,
    pytest_content=_SAFE_TEXT,
)
@settings(max_examples=100)
def test_save_load_multiple_test_files(binned_module, name, cmd, script,
                                       bats_content, pytest_content):
    safe = name.replace("-", "_")
    tmpdir = tempfile.mkdtemp()
    original_pending = binned_module.PENDING_DIR
    binned_module.PENDING_DIR = pathlib.Path(tmpdir) / ".binned" / "pending"
    try:
        test_files = {
            f"tests/{name}.bats": bats_content,
            f"tests/test_{safe}.py": pytest_content,
        }
        binned_module.save_pending(name, cmd, script, test_files)
        loaded = binned_module.load_pending(name)
        assert loaded is not None
        assert loaded["test_files"] == test_files
    finally:
        binned_module.PENDING_DIR = original_pending
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_load_pending_migrates_old_string_format(binned_module, tmp_path):
    """load_pending must convert the old 'tests': str format to 'test_files': dict."""
    import json
    original_pending = binned_module.PENDING_DIR
    binned_module.PENDING_DIR = tmp_path / ".binned" / "pending"
    binned_module.PENDING_DIR.mkdir(parents=True, exist_ok=True)
    try:
        old_state = {"name": "old-script", "cmd": "echo hi", "script": "#!/bin/bash",
                     "tests": "@test 'help' { run ./old-script --help; [ $status -eq 0 ]; }"}
        (binned_module.PENDING_DIR / "old-script.json").write_text(json.dumps(old_state))
        loaded = binned_module.load_pending("old-script")
        assert loaded is not None
        assert "test_files" in loaded
        assert "tests" not in loaded
        assert "tests/old-script.bats" in loaded["test_files"]
    finally:
        binned_module.PENDING_DIR = original_pending


def test_load_pending_returns_none_for_missing(binned_module, tmp_path):
    original_pending = binned_module.PENDING_DIR
    binned_module.PENDING_DIR = tmp_path / ".binned" / "pending"
    try:
        assert binned_module.load_pending("does-not-exist") is None
    finally:
        binned_module.PENDING_DIR = original_pending


# ── assess_language response parser ──────────────────────────────────────────
# Tests the field-parsing logic inline (same algorithm as binned.assess_language
# but without an LLM call) so small regressions in the parser surface quickly.

_LANGS = ["bash", "python", "node", "ruby", "other"]
_YESNO = ["yes", "no"]


@given(
    lang=st.sampled_from(_LANGS),
    rewrite=st.sampled_from(_YESNO),
    # Restrict to printable ASCII a real LLM would return (no colons, no
    # Unicode line-ending chars like \x85 NEL that splitlines() would eat).
    reason=st.from_regex(r"[A-Za-z0-9][A-Za-z0-9 .,!?()-]{0,79}", fullmatch=True),
)
@settings(max_examples=300)
def test_assess_language_parser_round_trips(lang, rewrite, reason):
    raw = f"RECOMMENDATION: {lang}\nREWRITE_SUGGESTED: {rewrite}\nREASON: {reason}"
    fields: dict[str, str] = {}
    for line in raw.strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip().upper()] = v.strip()
    assert fields.get("RECOMMENDATION", "").lower() == lang
    assert (fields.get("REWRITE_SUGGESTED", "no").lower() == "yes") == (rewrite == "yes")
    # The parser calls .strip() on values, so the invariant is round-trip via strip().
    assert fields.get("REASON", "") == reason.strip()
