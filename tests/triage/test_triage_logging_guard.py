"""Both directions for the `logging_permitted()` policy guard.

A guard that fails closed and a guard that never runs look identical: both
refuse, and both pass a smoke test. `tests/policy/test_logging_guards.py` proves
the predicate against the REAL resolver; this file proves it against a stub
`policy` on a PATH-only directory, so it can also assert WHICH key was asked —
the contract with the policy layers, independent of the script's own constant.

The behavioural half is the one that would have caught `ask-research`: a helper
defined after its call site fails closed forever, and only a test that sets the
policy to PERMIT and asserts the `-n` flag disappears can tell that corpse from
a working guard. See `tests/policy/test_policy_callers.py` for the incident.
"""

from __future__ import annotations

LOG_KEY = "boundaries.llm_processing.log_bodies_allowed"


# --- the predicate: fail closed in every non-permit shape ---------------------


def test_guard_relents_when_policy_allows(triage_module, shim_env, shims):
    """The direction that distinguishes a working guard from a corpse.

    If this fails while every deny test passes, the guard is refusing
    unconditionally and the resolver is never consulted.
    """
    shims.install_policy(exit_code=0)
    assert triage_module.logging_permitted() is True
    assert shims.read_policy_args() == ["check", LOG_KEY]


def test_guard_denies_when_policy_denies(triage_module, shim_env, shims):
    shims.install_policy(exit_code=1)
    assert triage_module.logging_permitted() is False


def test_guard_denies_when_policy_unknown(triage_module, shim_env, shims):
    """Exit 2 (unknown) is a denial, not an error state: the layers are
    restrictions-only, so 'unknown' cannot mean 'permitted'.
    """
    shims.install_policy(exit_code=2)
    assert triage_module.logging_permitted() is False


def test_guard_denies_when_policy_missing(triage_module, shim_env):
    """Deleting one script must not turn body logging back on for customer
    data — the ask-research shape exactly (helper not found, 127, refuses).
    """
    assert triage_module.logging_permitted() is False


def test_guard_denies_when_policy_not_executable(triage_module, shim_env, shims):
    shims.install_policy_broken()
    assert triage_module.logging_permitted() is False


def test_policy_is_asked_the_log_bodies_key(triage_module, shim_env, shims):
    """The key is the contract with the policy layers, so it is hardcoded here
    on purpose — asserting against the script's own LOG_BODIES_KEY would pass
    even if the script asked a key no layer defines.
    """
    shims.install_policy(exit_code=1)
    triage_module.logging_permitted()
    assert shims.read_policy_args() == ["check", LOG_KEY]


# --- behaviour: the guard must change the llm invocation ----------------------


def test_cli_passes_no_log_flag_when_policy_denies(cli, shims):
    proc = cli(input_text="the battery swells", policy_exit=1)
    assert proc.returncode == 0, proc.stderr
    args = shims.read_llm_args()
    assert "-n" in args, f"logging denied but the llm cmd had no -n: {args[:4]}"
    assert "prompt bodies not logged" in proc.stderr
    assert shims.read_policy_args() == ["check", LOG_KEY]


def test_cli_omits_no_log_flag_when_policy_allows(cli, shims):
    """The relent, end to end: policy says permit and the invocation CHANGES.

    A guard that never relents passes every deny test and fails only here.
    """
    proc = cli(input_text="the battery swells", policy_exit=0)
    assert proc.returncode == 0, proc.stderr
    args = shims.read_llm_args()
    assert "-n" not in args, f"logging permitted but -n was passed anyway: {args[:4]}"
    assert "prompt bodies not logged" not in proc.stderr
    assert shims.read_policy_args() == ["check", LOG_KEY]


def test_cli_fails_closed_when_policy_missing(cli, shims):
    proc = cli(input_text="the battery swells", policy_exit=None)
    assert proc.returncode == 0, proc.stderr
    args = shims.read_llm_args()
    assert "-n" in args, f"policy missing but logging was not suppressed: {args[:4]}"
