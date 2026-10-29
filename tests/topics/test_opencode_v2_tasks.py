"""Static contract for the opencode v1 -> v2 brew migration tasks.

The v2 formula (`anomalyco/tap/opencode-v2`) declares
`conflicts_with "opencode"`, so brew refuses the install while any v1
`opencode` formula is present. install.yaml therefore uninstalls v1 BEFORE
installing v2, in the same run (docs/research/opencode-v2/PLAN.md
§ Brew mechanics). The decision-2 safe default also untrusts the v1 formula
on install, converging the trust residue machines that ever installed v1
carry — idempotent, harmless when absent.

Teardown mirrors the new state (spec § Layering, TOPICS.md CRUD invariant):
the uninstall and the formula untrust retarget opencode-v2, while the gated
untap/untrust-tap pair is unchanged — the tap is shared infrastructure and
`opencode_remove_tap` stays its deliberate off-by-default guard.

Files are parsed with yaml.safe_load (the approach
tests/topic_resolution uses), so task ORDER is asserted structurally rather
than by line number. Static only: nothing runs ansible or touches the
deployed tree.

Run:
    pytest tests/topics/test_opencode_v2_tasks.py -v
"""

from __future__ import annotations

import pathlib

import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
TASKS = REPO / "dotfiles" / "apps" / "opencode" / "tasks"

# The formula names, in both spellings the topic may use: via the
# opencode_tap default (the house form the plan writes) or the literal tap
# (the plan's resolved form).
V1_FORMULA = {"{{ opencode_tap }}/opencode", "anomalyco/tap/opencode"}
V2_FORMULA = {"{{ opencode_tap }}/opencode-v2", "anomalyco/tap/opencode-v2"}


def _tasks(name: str) -> list:
    tasks = yaml.safe_load((TASKS / f"{name}.yaml").read_text())
    assert isinstance(tasks, list) and tasks, (
        f"tasks/{name}.yaml did not parse to a non-empty task list"
    )
    return tasks


def _module_args(task: dict, module: str) -> dict | None:
    args = task.get(module)
    return args if isinstance(args, dict) else None


def _homebrew_tasks(tasks: list) -> list[tuple[int, dict, dict]]:
    """(index, task, module args) for every community.general.homebrew task."""
    found = []
    for i, task in enumerate(tasks):
        args = _module_args(task, "community.general.homebrew")
        if args is not None:
            found.append((i, task, args))
    return found


def _names(args: dict) -> list[str]:
    name = args.get("name", "")
    if isinstance(name, list):
        return [str(n) for n in name]
    return [str(name)]


def _cmd_text(task: dict) -> str:
    for module in ("ansible.builtin.command", "ansible.builtin.shell"):
        mod = task.get(module)
        if isinstance(mod, str):
            return mod
        if isinstance(mod, dict):
            return str(mod.get("cmd", ""))
    return ""


def _untrust_formula_name(task: dict) -> str | None:
    """The formula named by a `brew untrust --formula <name>` command task.

    Whitespace is normalised first so folded block scalars still split
    cleanly on `--formula`; everything after it on the command is the name.
    """
    cmd = " ".join(_cmd_text(task).split())
    if "brew untrust" not in cmd or "--formula" not in cmd:
        return None
    return cmd.split("--formula", 1)[1].strip()


def _v2_install_task(tasks: list) -> tuple[int, dict, dict]:
    """The v2 install task: community.general.homebrew, state present."""
    installs = [
        (i, task, args)
        for i, task, args in _homebrew_tasks(tasks)
        if set(_names(args)) & V2_FORMULA and args.get("state") == "present"
    ]
    assert installs, (
        "install.yaml has no community.general.homebrew task installing "
        '"{{ opencode_tap }}/opencode-v2" (state: present) — the v2 tap '
        "formula is the migration's install target (PLAN.md § Brew mechanics)"
    )
    return installs[0]


def test_install_targets_v2_formula():
    """The binary install task installs the v2 tap formula."""
    _, _, args = _v2_install_task(_tasks("install"))
    assert args.get("state") == "present"


def test_install_removes_v1_before_installing_v2():
    """The v1 uninstall (state: absent) precedes the v2 install.

    `conflicts_with` makes brew refuse opencode-v2 while v1 is installed, so
    the removal must run first, in the same run — not in a follow-up run the
    operator has to remember.
    """
    tasks = _tasks("install")
    v2_index, _, _ = _v2_install_task(tasks)
    removals = [
        (i, args)
        for i, _, args in _homebrew_tasks(tasks)
        if set(_names(args)) & V1_FORMULA and args.get("state") == "absent"
    ]
    assert removals, (
        "install.yaml does not uninstall the v1 formula "
        '("{{ opencode_tap }}/opencode", state: absent) — brew '
        "conflicts_with would refuse the v2 install while v1 is present "
        "(PLAN.md § Brew mechanics)"
    )
    v1_index = removals[0][0]
    assert v1_index < v2_index, (
        f"the v1 uninstall sits at task index {v1_index}, after the v2 "
        f"install at index {v2_index} — conflicts_with refuses the install "
        "while v1 is present, so the uninstall must come first"
    )


def test_install_untrusts_v1_formula():
    """Decision 2 safe default: install untrusts the v1 formula name.

    Machines that ever installed v1 keep a trust entry for
    anomalyco/tap/opencode after the topic uninstalls the formula; the
    idempotent `brew untrust --formula` on install converges both eras.
    """
    untrusted = [
        name
        for task in _tasks("install")
        if (name := _untrust_formula_name(task)) is not None
    ]
    assert untrusted, (
        "install.yaml never runs `brew untrust --formula` — decision 2's "
        "safe default cleans the v1 formula trust residue on install "
        "(PLAN.md § Open author decisions 2)"
    )
    assert any(name in V1_FORMULA for name in untrusted), (
        f"install.yaml untrusts {untrusted!r}; expected the v1 formula name "
        '"{{ opencode_tap }}/opencode" — untrusting only the v2 name would '
        "leave the v1 residue decision 2 exists to clean"
    )


def test_remove_targets_v2_and_keeps_gated_tap_pair():
    """Teardown mirrors the v2 state; the gated tap pair is unchanged.

    The uninstall and the formula untrust name opencode-v2; the untap and
    `brew untrust --tap` tasks keep their `opencode_remove_tap` gate — the
    tap is shared infrastructure and revoking trust while it is still tapped
    would break every other formula installed from it.
    """
    tasks = _tasks("remove")
    uninstalls = [
        (i, args)
        for i, _, args in _homebrew_tasks(tasks)
        if set(_names(args)) & V2_FORMULA and args.get("state") == "absent"
    ]
    assert uninstalls, (
        'remove.yaml does not uninstall "{{ opencode_tap }}/opencode-v2" '
        "(state: absent) — teardown must mirror the v2 install (TOPICS.md "
        "CRUD ownership invariant)"
    )
    untrusted = [
        (i, name)
        for i, task in enumerate(tasks)
        if (name := _untrust_formula_name(task)) is not None
    ]
    assert any(name in V2_FORMULA for _, name in untrusted), (
        f"remove.yaml's formula untrust names {[n for _, n in untrusted]!r}; "
        'expected "{{ opencode_tap }}/opencode-v2" — the v1 name leaves the '
        "v2 formula's trust entry behind"
    )
    untaps = [
        (i, task)
        for i, task in enumerate(tasks)
        if isinstance(task.get("community.general.homebrew_tap"), dict)
        and task["community.general.homebrew_tap"].get("state") == "absent"
    ]
    assert untaps, (
        "remove.yaml lost the gated untap task "
        "(community.general.homebrew_tap, state: absent)"
    )
    untrust_taps = [
        (i, task)
        for i, task in enumerate(tasks)
        if "brew untrust --tap" in _cmd_text(task)
    ]
    assert untrust_taps, (
        "remove.yaml lost the `brew untrust --tap` task — install leaves TWO "
        "trust entries (tap and formula) and teardown needs both commands"
    )
    for label, found in (("untap", untaps), ("untrust --tap", untrust_taps)):
        for i, task in found:
            when = str(task.get("when", ""))
            assert "opencode_remove_tap" in when, (
                f"remove.yaml's {label} task (index {i}) lost its "
                f"opencode_remove_tap gate (when: {when!r}) — the tap is "
                "shared infrastructure and the flag is the deliberate "
                "off-by-default guard"
            )
