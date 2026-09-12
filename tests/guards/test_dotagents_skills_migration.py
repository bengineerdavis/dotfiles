"""Contract tests for the dotagents skills-migration guard.

The incident, 2026-09-12. `apps/opencode` failed on three of five skills with:

    [ERROR]: Task failed: Module failed: The command exited with a non-zero
    return code.

and nothing else. The cause was two layers deep. dotagents points each agent's
`skills/` at `~/.agents/skills`; where that path is still a real directory it
migrates the contents first, and `migrateDirectory` aborts on any name present
on both sides. It raises `SymlinkError`, which the CLI's own catch does not
handle — it knows only TrustError, GitError and InstallError — so the process
exits 1 with the sentence on **stderr** and nothing on stdout. The Ansible task
inspected only `.stdout`, so the one line that explained everything was thrown
away.

Two things are therefore under test here, and the second matters more than the
first: that the guard fires, and that it RELENTS.

    A guard that fires correctly and a guard that fires always look identical
    on a machine that has the problem.

The real Mac healed itself mid-incident — the 4th skill installed because a
rollback happened to empty the conflict set — so "the play is green" proves
nothing about this guard. Only the relenting direction does. Same reason as
tests/policy/test_policy_callers.py and tests/ollama_evals/test_capability_gate.py.

Run:
    pytest tests/guards -v
"""

from __future__ import annotations

import pathlib
import re

import pytest

from guard_harness import DOTFILES, GUARDS, said

APPS = DOTFILES / "apps"
CONFLICT_MARKER = "exist on both sides"


# --- it fires -----------------------------------------------------------------


def test_fails_when_a_name_exists_on_both_sides(run_guard, scope):
    scope.install("commit-hygiene")
    scope.agent_dir("commit-hygiene")

    result = run_guard(**scope.vars)

    assert result.returncode != 0, result.stdout
    assert said(result, CONFLICT_MARKER)
    assert said(result, "commit-hygiene")


def test_every_conflict_is_named_not_just_the_first(run_guard, scope):
    """One run reports all of it — docs/TOPICS.md § Script dependency guards.

    Reporting one conflict per run turns a four-name collision into four
    failed provisioning runs, which is how the original incident felt.
    """
    names = ["commit-hygiene", "pii-redaction", "review-best-practices"]
    scope.install(*names)
    scope.agent_dir(*names)

    result = run_guard(**scope.vars)

    assert result.returncode != 0
    missing = [n for n in names if n not in result.stdout]
    assert not missing, f"guard named only some conflicts; missing {missing}"


def test_hidden_entries_are_conflicts_too(run_guard, scope):
    """dotagents' readdir does not skip dotfiles, so neither may the guard.

    `~/.codex/skills/.system` is a real directory of this shape on this Mac. It
    is harmless today only because codex declares no userSkillsParentDir — if
    that changes, a guard that globbed `*` would wave the collision through.
    """
    scope.install(".system")
    scope.agent_dir(".system")

    result = run_guard(**scope.vars)

    assert result.returncode != 0
    assert said(result, ".system")


# --- it relents ---------------------------------------------------------------
# The direction that distinguishes a working guard from one that always fails.


def test_relents_when_no_name_overlaps(run_guard, scope):
    scope.install("commit-hygiene")
    scope.agent_dir("something-else")

    result = run_guard(**scope.vars)

    assert result.returncode == 0, result.stdout


def test_relents_when_the_agent_skills_dir_is_already_a_symlink(run_guard, scope):
    """The managed steady state, and the one every provisioned machine is in.

    Every name overlaps by definition once `skills/` points at the install dir.
    A guard that compared names without checking for the symlink would fail
    every run forever — the most likely way to get this wrong.
    """
    scope.agent_symlink()
    scope.install("commit-hygiene", "pii-redaction")

    result = run_guard(**scope.vars)

    assert result.returncode == 0, result.stdout


def test_relents_when_the_agent_has_no_skills_dir(run_guard, scope):
    scope.install("commit-hygiene")
    scope.agent_home.mkdir(parents=True, exist_ok=True)

    result = run_guard(**scope.vars)

    assert result.returncode == 0, result.stdout


def test_relents_when_nothing_is_installed_yet(run_guard, scope):
    """A fresh machine: ~/.agents/skills does not exist, so nothing can collide."""
    scope.agent_dir("commit-hygiene")

    result = run_guard(**scope.vars)

    assert result.returncode == 0, result.stdout


def test_override_lets_the_run_continue(run_guard, scope):
    """The documented escape hatch, which must actually open."""
    scope.install("commit-hygiene")
    scope.agent_dir("commit-hygiene")

    result = run_guard(guard_allow_skill_dir_conflicts=True, **scope.vars)

    assert result.returncode == 0, result.stdout


# --- it never repairs ---------------------------------------------------------


def test_the_guard_deletes_nothing(run_guard, scope):
    """"Nothing has been installed or moved" has to be true when it says so.

    The two sides are two copies of a skill — typically a hand-made symlink into
    a working clone against a pinned upstream checkout — and picking one is a
    judgement, not a cleanup.
    """
    scope.install("commit-hygiene")
    scope.agent_dir("commit-hygiene")
    before = scope.snapshot()

    result = run_guard(**scope.vars)

    assert result.returncode != 0
    assert scope.snapshot() == before


def test_the_failure_names_a_next_action(run_guard, scope):
    """The whole point. The incident's message named none, which is why it cost
    an afternoon."""
    scope.install("commit-hygiene")
    scope.agent_dir("commit-hygiene")

    result = run_guard(**scope.vars)

    assert said(result, "path:.agents/skills"), "no adopt-in-place fix offered"
    assert said(result, "guard_allow_skill_dir_conflicts=true"), "no override named"
    assert said(result, "Nothing has been installed or moved")


# --- the defaults are real ----------------------------------------------------


def test_defaults_resolve_against_real_facts(run_guard, scope):
    """Every other test overrides the defaults, so none of them evaluates the
    Jinja in defaults/main.yaml. A typo there would pass the entire suite above
    and fail only on a real machine."""
    result = run_guard(gather_facts=True)

    assert result.returncode == 0, result.stdout
