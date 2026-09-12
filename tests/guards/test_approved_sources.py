"""Contract tests for the approved-source guard.

~/.agents/skills is user-global: claude, cursor, codex, opencode and copilot all
auto-load it, so a directory dropped there is read into context on every session
on the machine, including ones working on unrelated personal repositories. On
2026-09-12 that path held an unlicensed internal work tool, and it was loaded
into a session working on this repo before anyone noticed.

The guard therefore answers a question dotagents cannot. `list --json` reports
declared dependencies, so it can say "what I declared is installed" but never
"something is installed that I never declared" — the undeclared directory is
invisible to the very tool that manages the declared ones. Both halves are under
test, and so is the relenting direction:

    A guard that flags everything and a guard that flags the right things look
    identical on a machine that has a problem.

Run:
    pytest tests/guards -v
"""

from __future__ import annotations

import json

import pytest

from guard_harness import said

APPROVED = ["owner/approved-lib"]
GUARD = "dotagents-approved-sources.yaml"


def declared(*pairs) -> str:
    """A fake `dotagents list --json` payload."""
    return json.dumps(
        {"skills": [{"name": n, "source": s, "status": "ok"} for n, s in pairs],
         "plugins": []}
    )


@pytest.fixture
def approved_scope(tmp_path):
    """A skills dir plus a stub inventory command.

    The guard takes `guard_dotagents_list_cmd` as a parameter precisely so it can
    be pointed at a scripted payload. Overriding PATH does not work: the guard's
    own `environment:` prepends the mise shims, so a stub placed on PATH loses to
    the real npx and the test silently asserts against whatever this machine has
    installed. That is how the first version of these tests failed.
    """

    class Scope:
        def __init__(self) -> None:
            self.skills_dir = tmp_path / "skills"
            self.skills_dir.mkdir()
            self.bin = tmp_path / "bin"
            self.bin.mkdir()

        def on_disk(self, *names: str) -> None:
            for n in names:
                (self.skills_dir / n).mkdir(exist_ok=True)

        def dotagents_says(self, payload: str, rc: int = 0) -> None:
            stub = self.bin / "fake-dotagents"
            stub.write_text(
                "#!/bin/sh\n"
                f"cat <<'JSON'\n{payload}\nJSON\n"
                f"exit {rc}\n"
            )
            stub.chmod(0o755)
            self.list_cmd = str(stub)

        def vars(self, **over) -> dict:
            base = {
                "guard_agents_skills_dir": str(self.skills_dir),
                "guard_approved_sources": APPROVED,
                "guard_vendored_skills": [],
                "guard_caller": "tests/guards",
                "guard_dotagents_list_cmd": self.list_cmd,
            }
            base.update(over)
            return base

    return Scope()


@pytest.fixture
def run_approved(run_guard, approved_scope):
    def _run(**over):
        return run_guard(tasks_from=GUARD, gather_facts=True,
                         **approved_scope.vars(**over))
    return _run


# --- it fires -----------------------------------------------------------------


def test_fails_on_a_declared_skill_from_an_unapproved_source(approved_scope, run_approved):
    approved_scope.dotagents_says(declared(("rogue", "someone-else/lib")))
    approved_scope.on_disk("rogue")

    result = run_approved()

    assert result.returncode != 0, result.stdout
    assert said(result, "rogue") and "someone-else/lib" in result.stdout


def test_fails_on_a_directory_nothing_declared(approved_scope, run_approved):
    """The case `dotagents list` cannot see, and the one that caught the
    unlicensed internal tool."""
    approved_scope.dotagents_says(declared(("good", "owner/approved-lib")))
    approved_scope.on_disk("good", "mystery-skill")

    result = run_approved()

    assert result.returncode != 0, result.stdout
    assert said(result, "mystery-skill")


def test_the_undeclared_failure_routes_work_material_to_project_scope(approved_scope, run_approved):
    """Naming the fix is the point: 'move it to project scope' is what stops an
    employer's tool being loaded into personal sessions."""
    approved_scope.dotagents_says(declared())
    approved_scope.on_disk("internal-tool")

    result = run_approved()

    assert said(result, "project scope")
    assert said(result, "Nothing has been installed, moved or deleted")


def test_refuses_to_treat_an_unreadable_inventory_as_empty(approved_scope, run_approved):
    """Fail closed. If dotagents cannot be asked, an empty list would silently
    approve whatever is actually on disk."""
    approved_scope.dotagents_says("not json at all", rc=1)
    approved_scope.on_disk("anything")

    result = run_approved()

    assert result.returncode != 0
    assert said(result, "unreadable inventory is not an empty one")


# --- it relents ---------------------------------------------------------------


def test_relents_when_everything_is_declared_and_approved(approved_scope, run_approved):
    approved_scope.dotagents_says(
        declared(("a", "owner/approved-lib"), ("b", "owner/approved-lib"))
    )
    approved_scope.on_disk("a", "b")

    result = run_approved()

    assert result.returncode == 0, result.stdout


def test_relents_for_a_vendored_skill_on_the_exception_list(approved_scope, run_approved):
    approved_scope.dotagents_says(declared(("a", "owner/approved-lib")))
    approved_scope.on_disk("a", "no-ai-slop")

    result = run_approved(guard_vendored_skills=["no-ai-slop"])

    assert result.returncode == 0, result.stdout


def test_the_override_lets_the_run_continue(approved_scope, run_approved):
    approved_scope.dotagents_says(declared(("rogue", "someone-else/lib")))
    approved_scope.on_disk("rogue")

    result = run_approved(guard_allow_unapproved_skills=True)

    assert result.returncode == 0, result.stdout


def test_an_empty_approved_list_flags_everything(approved_scope, run_approved):
    """The default is an empty list, so a caller that forgets to pass one must
    get a loud wrong answer rather than a silent permissive one."""
    approved_scope.dotagents_says(declared(("a", "owner/approved-lib")))
    approved_scope.on_disk("a")

    result = run_approved(guard_approved_sources=[])

    assert result.returncode != 0, result.stdout
