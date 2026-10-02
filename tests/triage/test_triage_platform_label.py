"""The platform label must never render as a literal `None`.

The motivating bug: a `platform=None` reporting defect reached the deployed
script and was caught by a manual smoke test. `f"PLATFORM: {platform}"` with a
Python `None` prints the string "None", and nothing upstream complained.

FINDING — `None` is NOT reachable through the public resolution functions.
`resolve_platform` is `flag or env or DEFAULT_PLATFORM`, and every term falls
through falsy values to the non-empty `DEFAULT_PLATFORM` string, so the function
is total over non-empty strings for every reachable (flag, env) pair. The bug
therefore predates the fallback — `build_prompt` itself still has NO guard and
would render `PLATFORM: None` if handed one; the `or` chain is the only
protection. What IS reachable and of the same shape is the EMPTY stamp
(`PLATFORM: ` with no label) if the fallback were ever `""` — the "turn unknown
into a claim" trap from AGENTS.md. The tests below pin both ends: resolution
never yields `None`/`""`, and every reachable resolution renders a non-empty,
real label into the prompt — including the unconfigured run, which is the exact
case that would have caught the bug.

Not covered: `TRIAGE_PLATFORM` set to the literal string "None" stamps "None"
into the memo. That is user configuration, and asserting against it would ratify
a guard the script does not have.
"""

from __future__ import annotations

import itertools

import pytest

FLAGS = [None, "", "FlagCorp"]
ENVS = [None, "", "EnvCorp"]


def _cases():
    for flag, env in itertools.product(FLAGS, ENVS):
        id = f"flag={flag!r},env={env!r}"
        yield pytest.param(flag, env, id=id)


@pytest.mark.parametrize("flag,env", list(_cases()))
def test_resolve_platform_never_returns_none_or_empty(
    triage_module, monkeypatch, flag, env
):
    """Totality of the `or` chain: whatever goes in, a real label comes out."""
    if env is None:
        monkeypatch.delenv("TRIAGE_PLATFORM", raising=False)
    else:
        monkeypatch.setenv("TRIAGE_PLATFORM", env)
    result = triage_module.resolve_platform(flag)
    assert result is not None
    assert result != ""
    assert result != "None"


def test_platform_fallback_is_the_declared_default(triage_module, monkeypatch):
    monkeypatch.delenv("TRIAGE_PLATFORM", raising=False)
    assert triage_module.resolve_platform(None) == triage_module.DEFAULT_PLATFORM


@pytest.mark.parametrize("flag,env", list(_cases()))
def test_rendered_platform_stamp_is_never_empty_or_none(
    triage_module, monkeypatch, flag, env
):
    """Roundtrip: resolution output through the unguarded `build_prompt` must
    always produce a real label in both stamp positions — the nearest reachable
    mis-report (an empty or "None" stamp) can never appear in the prompt.
    """
    if env is None:
        monkeypatch.delenv("TRIAGE_PLATFORM", raising=False)
    else:
        monkeypatch.setenv("TRIAGE_PLATFORM", env)
    platform = triage_module.resolve_platform(flag)
    prompt = triage_module.build_prompt("email body", platform, [], "2026-01-01")
    for stamp in ("PLATFORM: ", "**Platform**: "):
        line = next(ln for ln in prompt.splitlines() if ln.startswith(stamp))
        label = line[len(stamp) :]
        assert label.strip(), f"empty platform stamp in prompt: {line!r}"
        assert label != "None", f"literal None platform stamp in prompt: {line!r}"


def test_unconfigured_run_stamps_default_platform_not_none(cli, shims, triage_module):
    """The case that would have caught the motivating bug: no flag, no env —
    exactly the configuration the defect mis-reported.
    """
    proc = cli(input_text="the battery swells", policy_exit=1)
    assert proc.returncode == 0, proc.stderr
    prompt = shims.read_llm_args()[-1]
    assert prompt.strip(), "llm received an empty prompt"
    assert f"PLATFORM: {triage_module.DEFAULT_PLATFORM}" in prompt
    assert f"**Platform**: {triage_module.DEFAULT_PLATFORM}" in prompt
    assert "PLATFORM: None" not in prompt
    assert "**Platform**: None" not in prompt
    assert "platform=None" not in proc.stderr
    assert f"platform={triage_module.DEFAULT_PLATFORM}" in proc.stderr


def test_build_prompt_stamps_the_platform_it_is_given(triage_module):
    """Faithful rendering: a "None" in the output means "None" was passed in,
    which locates the bug in resolution rather than in the template.
    """
    prompt = triage_module.build_prompt("email body", "CorpX", [], "2026-01-01")
    assert "PLATFORM: CorpX" in prompt
    assert "**Platform**: CorpX" in prompt
