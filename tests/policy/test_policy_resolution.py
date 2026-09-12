"""
Resolution order and the fail-closed guarantee.

The whole point of the resolver is that no failure mode grants permission. Every
test below is a way the thing could break open: a layer that is missing, one that
is corrupt, a key nobody wrote, a field left as TODO. All of them must deny.
"""

from __future__ import annotations

from conftest import DENIED, ERROR, PERMITTED, UNKNOWN

FORBIDS = """
    boundaries:
      thing:
        may_happen: false
    """
PERMITS = """
    boundaries:
      thing:
        may_happen: true
    """
KEY = "boundaries.thing.may_happen"


# --- precedence ------------------------------------------------------------


def test_ethics_outranks_company_and_personal(policy_env):
    run = policy_env(ethics=FORBIDS, company=PERMITS, personal=PERMITS)
    assert run("check", KEY).returncode == DENIED
    assert "denied by ethics" in run("check", KEY).stdout


def test_company_outranks_personal(policy_env):
    run = policy_env(company=FORBIDS, personal=PERMITS)
    assert run("check", KEY).returncode == DENIED
    assert "denied by company" in run("check", KEY).stdout


def test_personal_applies_when_nothing_above_speaks(policy_env):
    run = policy_env(personal=PERMITS)
    result = run("check", KEY)
    assert result.returncode == PERMITTED
    assert "permitted by personal" in result.stdout


# --- fail closed -----------------------------------------------------------


def test_no_layer_speaks_denies(policy_env):
    run = policy_env(ethics="meta: {layer: ethics}")
    assert run("check", KEY).returncode == UNKNOWN


def test_all_layers_absent_denies(policy_env):
    """The bare-checkout case: nothing configured must not mean anything goes."""
    run = policy_env()
    assert run("check", KEY).returncode == UNKNOWN


def test_unparseable_layer_is_silent_not_permissive(policy_env):
    """Corrupting a file must not be a way to buy permission."""
    run = policy_env(ethics="boundaries: [broken: [[[", company=FORBIDS)
    result = run("check", KEY)
    assert result.returncode == DENIED
    assert "denied by company" in result.stdout


def test_unparseable_layer_alone_still_denies(policy_env):
    run = policy_env(ethics="boundaries: [broken: [[[")
    assert run("check", KEY).returncode == UNKNOWN


def test_layer_that_is_not_a_mapping_is_silent(policy_env):
    run = policy_env(ethics="- just\n- a\n- list\n")
    assert run("check", KEY).returncode == UNKNOWN


def test_todo_placeholder_is_silent(policy_env):
    """company.yaml ships full of TODOs; an unfilled field is not an answer."""
    run = policy_env(company='boundaries: {thing: {may_happen: "TODO"}}')
    assert run("check", KEY).returncode == UNKNOWN


def test_todo_in_a_higher_layer_defers_to_a_real_rule_below(policy_env):
    run = policy_env(
        ethics='boundaries: {thing: {may_happen: "TODO"}}', company=FORBIDS
    )
    result = run("check", KEY)
    assert result.returncode == DENIED
    assert "denied by company" in result.stdout


def test_null_value_is_silent(policy_env):
    run = policy_env(company="boundaries: {thing: {may_happen: }}")
    assert run("check", KEY).returncode == UNKNOWN


# --- settings vs permissions ------------------------------------------------


def test_get_returns_value_and_deciding_layer(policy_env):
    run = policy_env(personal="retention: {local_logs_days: 90}")
    result = run("get", "retention.local_logs_days")
    assert result.returncode == 0
    assert "90" in result.stdout and "personal" in result.stdout


def test_get_on_an_unresolved_key_fails(policy_env):
    run = policy_env()
    assert run("get", "nothing.here").returncode == UNKNOWN


def test_check_on_a_non_boolean_is_a_caller_error(policy_env):
    """Denying a setting would imply a rule nobody wrote; say so instead."""
    run = policy_env(personal="retention: {local_logs_days: 90}")
    result = run("check", "retention.local_logs_days")
    assert result.returncode == ERROR
    assert "policy get" in result.stderr


# --- explain ----------------------------------------------------------------


def test_explain_distinguishes_absent_from_unset(policy_env):
    run = policy_env(ethics='boundaries: {thing: {may_happen: "TODO"}}')
    out = run("explain", KEY).stdout
    assert "present but unset" in out
    assert "company: absent" in out or "company:" in out
    assert "fail_closed" in out
