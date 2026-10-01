"""Both directions for the logging guards in `triage` and `llm-ctx`.

`ask-research` already had this coverage; these two did not, while carrying the
same guard. spec.md § Verification requires any mechanism that can decline to be
proven to relent, and two of the three callers were unproven in both directions
at once — a guard that always denied and a guard that was never consulted would
have looked identical.

These run the guard against the REAL `policy` resolver over a synthetic company
layer, rather than stubbing the subprocess. Stubbing would test that the code
reads a return code, which is not the thing that can be wrong. What can be wrong
is the resolver being consulted with the wrong key, or not found on PATH, or
answering 2 where the caller expected 1.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import pathlib
import shutil
import subprocess
import textwrap

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
LOG_KEY = "boundaries.llm_processing.log_bodies_allowed"

CALLERS = {
    "triage": (REPO / "bin" / "executable_triage", "logging_permitted"),
    "llm-ctx": (REPO / "bin" / "executable_llm-ctx", "policy_permits_logging"),
}


def _company(**rules: bool) -> str:
    body = "\n".join(f"    {k}: {str(v).lower()}" for k, v in rules.items())
    return (
        textwrap.dedent("""
        meta:
          layer: company
          precedence: 2
        boundaries:
          llm_processing:
        """).lstrip("\n")
        + body
        + "\n"
    )


def _load(path: pathlib.Path):
    loader = importlib.machinery.SourceFileLoader(path.stem, str(path))
    spec = importlib.util.spec_from_loader(path.stem, loader)
    mod = importlib.util.module_from_spec(spec)
    try:
        loader.exec_module(mod)
    except ImportError as exc:
        pytest.skip(f"{path.name} dependencies unavailable: {exc}")
    return mod


@pytest.fixture
def policy_env(tmp_path, monkeypatch):
    """Put a real `policy` on PATH, reading a company layer we control."""
    state = tmp_path / "state"
    (state / "ai-policy").mkdir(parents=True)
    shim = tmp_path / "shim"
    shim.mkdir()
    shutil.copy2(REPO / "bin" / "executable_policy", shim / "policy")
    (shim / "policy").chmod(0o755)

    def configure(company: str | None, *, resolver_on_path: bool = True):
        if company is not None:
            (state / "ai-policy" / "company.yaml").write_text(company)
        monkeypatch.setenv("XDG_STATE_HOME", str(state))
        monkeypatch.setenv("HOME", str(tmp_path))
        base = os.environ.get("PATH", "")
        monkeypatch.setenv(
            "PATH", f"{shim}:{base}" if resolver_on_path else "/usr/bin:/bin"
        )
        # sanity: the resolver must actually answer, or every assertion below is vacuous
        if resolver_on_path:
            probe = subprocess.run(
                ["policy", "check", LOG_KEY],
                capture_output=True,
                text=True,
                env={
                    **os.environ,
                    "XDG_STATE_HOME": str(state),
                    "HOME": str(tmp_path),
                    "PATH": f"{shim}:{base}",
                },
            )
            assert probe.returncode in (0, 1, 2), (
                f"resolver not answering: {probe.stderr}"
            )

    return configure


@pytest.mark.parametrize("caller", sorted(CALLERS))
def test_guard_denies_when_policy_denies(policy_env, caller):
    path, fn = CALLERS[caller]
    policy_env(_company(log_bodies_allowed=False))
    assert getattr(_load(path), fn)() is False


@pytest.mark.parametrize("caller", sorted(CALLERS))
def test_guard_denies_when_policy_is_unknown(policy_env, caller):
    """Exit 2 must be treated exactly like exit 1. The layers are
    restrictions-only, so unknown is the normal answer, not an error state.
    """
    path, fn = CALLERS[caller]
    policy_env(_company())  # key absent entirely -> unknown
    assert getattr(_load(path), fn)() is False


@pytest.mark.parametrize("caller", sorted(CALLERS))
def test_guard_denies_when_the_resolver_is_missing(policy_env, caller):
    """Deleting one script must not turn logging back on for customer data."""
    path, fn = CALLERS[caller]
    policy_env(_company(log_bodies_allowed=True), resolver_on_path=False)
    assert getattr(_load(path), fn)() is False


@pytest.mark.parametrize("caller", sorted(CALLERS))
def test_guard_relents_when_policy_permits(policy_env, caller):
    """The direction that distinguishes a working guard from one that always
    refuses. Both look identical from a smoke test.
    """
    path, fn = CALLERS[caller]
    policy_env(_company(log_bodies_allowed=True))
    assert getattr(_load(path), fn)() is True


def test_llm_ctx_translates_the_guard_into_an_actual_flag():
    """The predicate being right is not the point; passing -n is. `-n` is the
    short form of --no-log, which is why grepping bin/ for the long form finds
    nothing.
    """
    mod = _load(CALLERS["llm-ctx"][0])
    mod._suppress_log = True
    assert mod.no_log_flags() == ["-n"]
    mod._suppress_log = False
    assert mod.no_log_flags() == []
