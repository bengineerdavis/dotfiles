"""The approved-source guard is wiring; `skill-trust` is the decision.

Precedence, licence tiers and the fail-closed rules are tested exhaustively in
tools/skill-trust/tests/ — as a program, not through a play. Duplicating them
here would mean two statements of the same rule drifting apart, and the YAML copy
would be the one nobody ran by hand.

So this tests only what collapsing the guard onto the tool can get wrong: that
the tool is actually invoked, that every non-zero exit is treated as a refusal,
that a missing tool is reported rather than skipped, and that the override works.

The last one is not pedantry. `skill-trust` distinguishes denied (1) from
"nothing examined" (2) and "rules unreadable" (3). A guard that checked only for
1 would let a mistyped config read as a clean pass — an audit that silently stops
auditing.

Run:
    pytest tests/guards -v
"""

from __future__ import annotations

import pytest

# pyrefly: ignore [missing-import]
from guard_harness import said

GUARD = "dotagents-approved-sources.yaml"


@pytest.fixture
def trust_scope(tmp_path):
    class Scope:
        def __init__(self) -> None:
            self.skills = tmp_path / "skills"
            self.skills.mkdir()
            self.bin = tmp_path / "bin"
            self.bin.mkdir()
            self.list_cmd = "true"

        def skill_trust(
            self, *, rc: int, stdout: str = "", present: bool = True
        ) -> str:
            """A stand-in for the real program, so the guard's handling of each
            exit code is testable without building a skill tree per case.
            """
            if not present:
                return str(self.bin / "definitely-not-installed")
            stub = self.bin / "fake-skill-trust"
            stub.write_text(
                "#!/bin/sh\n"
                'if [ "$1" = "--help" ]; then exit 0; fi\n'
                f"cat <<'OUT'\n{stdout}\nOUT\n"
                f"exit {rc}\n"
            )
            stub.chmod(0o755)
            return str(stub)

        def vars(self, cmd: str, **over) -> dict:
            base = {
                "guard_agents_skills_dir": str(self.skills),
                "guard_approved_sources": ["owner/lib"],
                "guard_skill_trust_cmd": cmd,
                "guard_dotagents_list_cmd": self.list_cmd,
                "guard_caller": "tests/guards",
            }
            base.update(over)
            return base

    return Scope()


def _run(run_guard, scope, cmd, **over):
    return run_guard(tasks_from=GUARD, gather_facts=True, **scope.vars(cmd, **over))


# --- every non-zero exit is a refusal -----------------------------------------


@pytest.mark.parametrize(
    "rc,meaning",
    [(1, "denied"), (2, "nothing examined"), (3, "rules unreadable")],
)
def test_any_non_zero_exit_fails_the_run(run_guard, trust_scope, rc, meaning):
    cmd = trust_scope.skill_trust(rc=rc, stdout=f"DENIED something ({meaning})")
    result = _run(run_guard, trust_scope, cmd)
    assert result.returncode != 0, f"exit {rc} ({meaning}) was treated as a pass"


def test_the_failure_repeats_what_the_tool_said(run_guard, trust_scope):
    """The operator needs the tool's own words, not a summary of them."""
    cmd = trust_scope.skill_trust(rc=1, stdout="DENIED [undeclared] mystery-skill")
    result = _run(run_guard, trust_scope, cmd)
    assert said(result, "mystery-skill")
    assert said(result, "Nothing has been installed, moved or deleted")


# --- it relents ---------------------------------------------------------------


def test_relents_when_the_tool_permits(run_guard, trust_scope):
    cmd = trust_scope.skill_trust(rc=0, stdout="PERMITTED all 3 skill(s)")
    assert _run(run_guard, trust_scope, cmd).returncode == 0


def test_the_override_lets_the_run_continue(run_guard, trust_scope):
    cmd = trust_scope.skill_trust(rc=1, stdout="DENIED something")
    result = _run(run_guard, trust_scope, cmd, guard_allow_unapproved_skills=True)
    assert result.returncode == 0, result.stdout


# --- the dependency is named, not assumed -------------------------------------


def test_a_missing_tool_is_reported_rather_than_skipped(run_guard, trust_scope):
    """An absent checker must not look like a clean audit — the failure mode the
    whole guard exists to prevent, one level up.
    """
    cmd = trust_scope.skill_trust(rc=0, present=False)
    result = _run(run_guard, trust_scope, cmd)
    assert result.returncode != 0
    assert said(result, "uv tool install")
    assert said(result, "this run proves nothing")
