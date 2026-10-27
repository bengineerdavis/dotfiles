"""The guard exists, is called, and still covers what it claims to cover.

tests/guards/test_dotagents_skills_migration.py proves the guard behaves. It
cannot prove anything CALLS it, and an uncalled guard is indistinguishable from
a working one on a healthy machine — the same gap tests/policy/test_policy_callers.py
was written for after `ask-research` shipped a guard that never ran.

Two further kinds of rot are covered here, both of which caused the 2026-09-12
incident rather than merely resembling it:

  1. A task that shells out to dotagents while reading only `.stdout`. dotagents
     writes its errors to stderr and leaves stdout empty, so such a task reports
     "non-zero return code" and discards the explanation. That is the original
     bug, and it is one careless copy-paste away from returning.
  2. The guard's default list of agent homes going stale. It is a transcription
     of `userSkillsParentDirs` from the dotagents target registry. If an upgrade
     gives another agent a relocation target, the guard silently under-covers and
     everything here stays green.

Run:
    pytest tests/guards -v
"""

from __future__ import annotations

import pathlib
import re

import pytest

# pyrefly: ignore [missing-import]
from guard_harness import DOTFILES, GUARDS

APPS = DOTFILES / "apps"
GUARD_DEFAULTS = GUARDS / "defaults" / "main.yaml"


def _task_files() -> list[pathlib.Path]:
    return sorted(APPS.glob("*/tasks/*.yaml")) + sorted(GUARDS.glob("tasks/*.yaml"))


def _code(path: pathlib.Path) -> str:
    """The file with full-line comments removed.

    Not cosmetic. Both checks below first passed against a mutated source
    because the word they look for — "stderr", "COPILOT_HOME" — also appeared in
    a comment explaining the rule. A test satisfied by its own documentation
    certifies nothing.
    """
    return "\n".join(
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith("#")
    )


# --- the guard is wired in ----------------------------------------------------


def test_the_guard_role_is_callable():
    """`tasks_from` needs the file at exactly this path, and `defaults_from`
    needs main.yaml beside it, or the import fails at parse time.
    """
    assert (GUARDS / "tasks" / "dotagents-skills-migration.yaml").is_file()
    assert GUARD_DEFAULTS.is_file()
    assert (GUARDS / "README.md").is_file()


def test_dotagents_imports_the_guard_before_syncing_skills():
    """Order is the whole point: guarding after the sync guards nothing."""
    text = _code(APPS / "dotagents" / "tasks" / "install.yaml")

    guard_at = text.find("dotagents-skills-migration.yaml")
    sync_at = text.find("add {{ item.source }}")

    assert guard_at != -1, "apps/dotagents no longer imports the migration guard"
    assert sync_at != -1, "the skill sync task moved; this test needs updating"
    assert guard_at < sync_at, "the guard is imported AFTER the sync it guards"


def test_guard_callers_use_a_static_import():
    """`import_role` keeps the guard's tasks visible at parse time, so the
    lifecycle tags in tasks/main.yaml still select them. `include_role` would
    need an `apply:` block and silently drops out of tag-filtered runs.
    """
    for path in _task_files():
        text = _code(path)
        if "roles/guards" not in text:
            continue
        assert "include_role" not in text, (
            f"{path.relative_to(DOTFILES)} calls the guards role with "
            "include_role; use import_role (see docs/TOPICS.md § Shared guards)"
        )


def test_the_foreign_bucket_flag_is_plumbed_end_to_end():
    """`dotagents_skill_foreign` -> `guard_foreign_buckets` -> the trust rules,
    and on by default. A break anywhere along that chain silently turns 'not
    mine to rule on' back into a denial that fails provisioning.
    """
    topic_defaults = _code(APPS / "dotagents" / "defaults" / "main.yaml")
    install = _code(APPS / "dotagents" / "tasks" / "install.yaml")
    guard_defaults = _code(GUARD_DEFAULTS)
    guard_task = _code(GUARDS / "tasks" / "dotagents-approved-sources.yaml")

    assert "dotagents_skill_foreign: true" in topic_defaults
    assert 'guard_foreign_buckets: "{{ dotagents_skill_foreign }}"' in install
    assert "guard_foreign_buckets: true" in guard_defaults
    assert "'foreign_buckets': guard_foreign_buckets | bool" in guard_task


def test_the_approved_sources_guard_is_the_last_task():
    """The gate must not block unrelated topics from finishing. Running last is
    the direct fix for 'one undeclared skill blocks my whole install' — every
    other task converges before the gate can fail.
    """
    text = _code(APPS / "dotagents" / "tasks" / "install.yaml")

    report_at = text.find("Report skill sync results")
    guard_at = text.find("tasks_from: dotagents-approved-sources.yaml")

    assert guard_at != -1, "apps/dotagents no longer imports the approved-sources guard"
    assert report_at != -1, "the report task moved; this test needs updating"
    assert guard_at > report_at, "the approved-sources guard runs before the report"


def test_opencode_carries_no_skill_manifest():
    """The skill set is user-global; it belongs to apps/dotagents, not to one
    coding tool's topic. A second manifest would declare sources twice and
    drift the moment either is edited.

    Only declaration files are checked. The molecule scenario's README runs
    `dotagents` to verify the sync on a test box, which is a consumer, not a
    second manifest.
    """
    candidates = sorted((APPS / "opencode" / "defaults").glob("*.yaml")) + sorted(
        (APPS / "opencode" / "tasks").glob("*.yaml")
    )
    offenders = []
    for path in candidates:
        text = _code(path)
        if (
            "opencode_skill_sources" in text
            or "dotagents add" in text
            or "dotagents --user add" in text
        ):
            offenders.append(path.relative_to(DOTFILES))

    assert not offenders, (
        "apps/opencode still declares or syncs skills; those belong to "
        "apps/dotagents:\n  " + "\n  ".join(str(p) for p in offenders)
    )


def test_no_root_guard_is_wired_only_to_intended_topics():
    """The guard is shared, so the caller list is the control.

    Exactly one topic here runs tools that own a user-scoped tree. A new caller
    must be added to this list on purpose, and removing the mise import must
    fail rather than silently leaving mise unguarded.
    """
    callers = set()
    for path in _task_files():
        if "no-root-authority.yaml" not in _code(path):
            continue
        rel = path.relative_to(DOTFILES)
        callers.add(f"apps/{rel.parts[1]}" if rel.parts[0] == "apps" else str(rel))

    assert callers == {"apps/mise"}, (
        "no-root-authority.yaml is imported by an unintended topic, or the "
        f"intended caller stopped importing it: {sorted(callers)}. Update this "
        "list only when the new caller really owns user-scoped tools."
    )


def test_no_root_guard_survives_tag_filtering():
    """`always` is the point: a tag-filtered run must not skip the check that
    stops it running as root.
    """
    text = _code(APPS / "mise" / "tasks" / "main.yaml")
    at = text.find("no-root-authority.yaml")
    assert at != -1, "apps/mise no longer imports the no-root guard"
    assert "tags: [always]" in text[at : at + 200], (
        "the no-root-authority import lost its `always` tag, so --tags install "
        "and --tags upgrade skip it"
    )


# --- the original bug cannot come back ----------------------------------------


def test_every_dotagents_caller_reports_stderr():
    """The 2026-09-12 regression, stated as a rule.

    dotagents exits 1 with its message on stderr and nothing on stdout. A task
    that neither defers the failure nor reads `.stderr` converts every dotagents
    error into "The command exited with a non-zero return code."
    """
    offenders = []
    for path in _task_files():
        text = _code(path)
        if "dotagents" not in text or "ansible.builtin.command" not in text:
            continue
        # Any reference counts: `.stderr`, `map(attribute='stderr')`, …
        if "failed_when: false" not in text or "stderr" not in text:
            offenders.append(path.relative_to(DOTFILES))

    assert not offenders, (
        "these task files run dotagents but would discard its error message; "
        "each needs `failed_when: false` on the command plus a following task "
        "that reports `.stderr`:\n  " + "\n  ".join(str(p) for p in offenders)
    )


def test_the_rule_has_something_to_check():
    """Guards against the test above passing vacuously if the tasks are renamed
    or the topic is removed.
    """
    callers = [
        p
        for p in _task_files()
        if "dotagents" in _code(p) and "ansible.builtin.command" in _code(p)
    ]
    assert callers, "no task file shells out to dotagents — did the topic move?"


# --- the agent-home list has not gone stale -----------------------------------

# Maps a `userSkillsParentDirs` expression in the dotagents registry to the
# marker that must appear in the guard's defaults for that target to be covered.
KNOWN_RELOCATION_TARGETS = {
    '[join(homedir(), ".claude")]': "/.claude",
    "[copilotHome]": "COPILOT_HOME",
}

DEFINITIONS_GLOB = (
    ".npm/_npx/*/node_modules/@sentry/dotagents/dist/targets/definitions/*.js"
)


def _installed_definitions() -> list[pathlib.Path]:
    return sorted(pathlib.Path.home().glob(DEFINITIONS_GLOB))


def test_guard_covers_every_agent_dotagents_relocates():
    """Drift detector against the real installed dotagents.

    Skips rather than guesses when no copy is cached — an absent package is not
    evidence that the list is right.
    """
    definitions = _installed_definitions()
    if not definitions:
        pytest.skip(
            "no cached @sentry/dotagents to compare against; populated by any "
            "`npx @sentry/dotagents` run"
        )

    pattern = re.compile(r"userSkillsParentDirs:\s*(.+?),\n")
    found: dict[str, str] = {}
    for path in definitions:
        for expr in pattern.findall(path.read_text(encoding="utf-8")):
            if expr.strip() == "undefined":
                continue
            found[expr.strip()] = path.name

    assert found, (
        "no agent in the cached dotagents declares userSkillsParentDirs. Either "
        "the registry changed shape or this parse is wrong — do not treat it as "
        "'nothing to guard'."
    )

    unknown = {e: f for e, f in found.items() if e not in KNOWN_RELOCATION_TARGETS}
    assert not unknown, (
        "dotagents now relocates skills directories this guard does not know "
        "about, so it would wave the collision through:\n  "
        + "\n  ".join(f"{f}: {e}" for e, f in unknown.items())
        + f"\nAdd the target to {GUARD_DEFAULTS.relative_to(DOTFILES)} "
        "(guard_agent_homes) and to KNOWN_RELOCATION_TARGETS here."
    )

    defaults = _code(GUARD_DEFAULTS)
    for expr in found:
        marker = KNOWN_RELOCATION_TARGETS[expr]
        assert marker in defaults, (
            f"dotagents relocates {expr} but guard_agent_homes has no entry "
            f"containing {marker!r}"
        )
