"""Static contract for the i-have-adhd OpenCode plugin loader.

Why this exists. `apps/dotagents` installs the plugin's full upstream tree,
including `.opencode/plugins/i-have-adhd.mjs`, but dotagents projects only skill
links into OpenCode (measured 2026-11-17, dotagents 3.4.0) — no plugin, no
`/i-have-adhd` command. This topic closes that gap with one loader file in
OpenCode's global plugin directory, which OpenCode auto-discovers.

The properties worth pinning, because each has a silent failure mode:

1. The loader re-exports upstream's implementation instead of copying it, so an
   upstream update cannot leave us running a stale fork.
2. The loader resolves its dependency from the user's home at load time, so it
   carries no machine-specific literal (AGENTS.md § Machine-specific values).
   A baked-in path fails as "plugin not loaded", which reads as "never
   installed" — the failure and the absence look identical.
3. Install probes for the dependency BEFORE writing the loader, and fails with
   the fix named (run the dotagents topic) rather than writing a loader that
   resolves to nothing.
4. Teardown removes the loader, and removes only the loader: the upstream tree
   belongs to apps/dotagents.

Static only: nothing runs ansible, nothing touches $HOME and nothing requires
the plugin to be installed. Run:

    pytest tests/topics/test_opencode_adhd_loader.py -v
"""

from __future__ import annotations

import pathlib

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT
import yaml

TOPIC = PAYLOAD_ROOT / "dotfiles" / "apps" / "opencode"
TASKS = TOPIC / "tasks"
TEMPLATE = TOPIC / "templates" / "i-have-adhd-loader.js.j2"
DEFAULTS = TOPIC / "defaults" / "main.yaml"


def _tasks(name: str) -> list:
    tasks = yaml.safe_load((TASKS / f"{name}.yaml").read_text())
    assert isinstance(tasks, list) and tasks, (
        f"tasks/{name}.yaml did not parse to a non-empty task list"
    )
    return tasks


def _named(tasks: list, fragment: str) -> dict:
    """The single task whose name contains `fragment`."""
    matches = [
        t for t in tasks if isinstance(t, dict) and fragment in str(t.get("name", ""))
    ]
    assert len(matches) == 1, (
        f"expected exactly one task whose name contains {fragment!r}, "
        f"found {len(matches)}"
    )
    return matches[0]


def _defaults() -> dict:
    data = yaml.safe_load(DEFAULTS.read_text())
    assert isinstance(data, dict), "defaults/main.yaml did not parse to a mapping"
    return data


# ── The template ────────────────────────────────────────────────────────────


def test_loader_template_exists() -> None:
    assert TEMPLATE.is_file(), (
        "templates/i-have-adhd-loader.js.j2 is missing; install.yaml templates from it"
    )


def test_loader_reexports_upstream_instead_of_copying_it() -> None:
    """A copied implementation would silently drift from upstream."""
    body = TEMPLATE.read_text()
    assert "await import(" in body, (
        "the loader must import upstream's implementation at load time; a "
        "loader that inlines the plugin logic is a fork of it"
    )
    assert "export default mod.default" in body, (
        "the loader must export upstream's default export, which is the "
        "shape OpenCode's loader requires"
    )


def test_loader_resolves_the_dependency_from_home_at_load_time() -> None:
    """No machine-specific literal: the path is built from the running user."""
    body = TEMPLATE.read_text()
    assert "os.homedir()" in body, (
        "the loader must resolve the user's home at load time; a path baked in "
        "at deploy time is silently wrong on any other machine"
    )
    # A literal home directory is the exact bug AGENTS.md § Machine-specific
    # values exists to prevent: it does not error, the rule simply never matches.
    for literal in ("/Users/", "/home/"):
        assert literal not in body, (
            f"the loader template contains the literal home path {literal!r}; "
            "resolve it from os.homedir() instead"
        )


def test_loader_targets_the_mjs_implementation_not_the_js_shim() -> None:
    """`.js` in the plugin tree is a re-export shim; `.mjs` is the source."""
    body = TEMPLATE.read_text()
    assert "{{ opencode_adhd_plugin_source }}.mjs" in body, (
        "the loader must target the .mjs implementation in the plugin tree; "
        "the .js file beside it is a shim that only re-exports the .mjs"
    )


# ── Defaults ────────────────────────────────────────────────────────────────


def test_defaults_resolve_paths_from_home_and_name_the_dependency() -> None:
    defaults = _defaults()
    for key in (
        "opencode_adhd_plugin",
        "opencode_adhd_plugin_source",
        "opencode_adhd_plugins_dir",
        "opencode_plugin_dir",
        "opencode_adhd_loader_name",
    ):
        assert key in defaults, f"defaults/main.yaml is missing {key}"

    # Both directories are resolved from the user's home by Ansible at deploy
    # time, never written out as a literal (AGENTS.md § Machine-specific values).
    for key in ("opencode_adhd_plugins_dir", "opencode_plugin_dir"):
        value = str(defaults[key])
        assert "ansible_facts['env']['HOME']" in value, (
            f"{key} must resolve from ansible_facts['env']['HOME'], got {value!r}"
        )

    assert defaults["opencode_adhd_loader_name"].endswith(".js"), (
        "OpenCode auto-discovers .js and .ts files directly; the loader name "
        "must end in .js to be discovered without a plugins array entry"
    )


# ── Install ─────────────────────────────────────────────────────────────────


def test_install_probes_for_the_dependency_before_writing_the_loader() -> None:
    """Ordering is the guard: the probe must precede the template task."""
    install = _tasks("install")
    probe_at = install.index(_named(install, "Check that dotagents installed"))
    write_at = install.index(_named(install, "Install the i-have-adhd plugin loader"))
    assert probe_at < write_at, (
        "the dependency probe must run before the loader is written; written "
        "first, a missing dependency surfaces as 'plugin not loaded' instead of "
        "as the topic that failed to install it"
    )
    # Removing the condition from the fail task would make it fire on healthy
    # machines, so the probe's result must be what the write task gates on too:
    # the loader is only written once the dependency is known present.
    write_task = _named(install, "Install the i-have-adhd plugin loader")
    when_text = " ".join(write_task.get("when") or [])
    assert "stat.exists" in when_text, (
        "the loader write must be gated on the probe's stat.exists so it never "
        f"runs against a missing dependency, got: {when_text!r}"
    )


def test_install_fails_with_the_fix_named_when_the_tree_is_absent() -> None:
    install = _tasks("install")
    task = _named(install, "Fail with the fix when the ADHD plugin tree is absent")
    msg = str(task["ansible.builtin.fail"]["msg"])
    # The fix lives in another topic, so naming it is the whole value of the
    # failure. A bare "not found" sends the operator to the wrong topic.
    assert "dotagents" in msg, (
        f"the failure must name the topic that installs the tree, got: {msg!r}"
    )
    assert "Nothing was written" in msg, (
        "the failure must state that nothing was written, so the operator knows "
        "the machine is not half-configured"
    )


def test_the_failure_is_conditional_on_the_dependency_being_absent() -> None:
    """A failure that always fires is not a guard; it is an outage.

    Pinning only the message let a mutation that dropped the `stat.exists`
    condition pass — the task then failed on every run, including the healthy
    one. The condition is the guard.
    """
    install = _tasks("install")
    task = _named(install, "Fail with the fix when the ADHD plugin tree is absent")
    when = task.get("when")
    assert when is not None, (
        "the fail task must be conditional; unconditional, it fails on healthy "
        "machines too"
    )
    when_text = " ".join(when) if isinstance(when, list) else str(when)
    assert "stat.exists" in when_text, (
        "the fail task must be conditioned on the dependency probe's "
        f"stat.exists, got: {when_text!r}"
    )
    assert "not" in when_text, (
        "the fail task must fire when the dependency is ABSENT; without the "
        f"negation it failures whenever the tree exists. Got: {when_text!r}"
    )


def test_install_and_teardown_agree_on_the_loader_path() -> None:
    """A teardown that targets a different path leaves the loader behind."""
    install = _tasks("install")
    remove = _tasks("remove")

    install_dest = str(
        _named(install, "Install the i-have-adhd plugin loader")[
            "ansible.builtin.template"
        ]["dest"]
    )
    remove_path = str(
        _named(remove, "Remove the i-have-adhd plugin loader")["ansible.builtin.file"][
            "path"
        ]
    )

    assert install_dest == remove_path, (
        "install and remove must name the same loader path, got "
        f"{install_dest!r} and {remove_path!r}"
    )


def test_teardown_removes_only_the_loader_not_the_upstream_tree() -> None:
    """The upstream tree is apps/dotagents' state, not this topic's."""
    remove = _tasks("remove")
    loader = remove.index(_named(remove, "Remove the i-have-adhd plugin loader"))

    for task in remove[loader + 1 :]:
        if not isinstance(task, dict):
            continue
        for module, spec in task.items():
            if not isinstance(spec, dict):
                continue
            path = " ".join(str(v) for k, v in spec.items() if k == "path")
            assert ".agents/plugins" not in path, (
                "teardown must not remove apps/dotagents' plugin tree; that "
                "topic owns it, and deleting it here breaks a machine that "
                "keeps dotagents but drops this topic"
            )


def test_teardown_removes_the_loader_even_with_the_install_flag_off() -> None:
    """The flag gates install. A gated teardown would strand the file."""
    remove = _tasks("remove")
    task = _named(remove, "Remove the i-have-adhd plugin loader")
    assert "when" not in task, (
        "the loader teardown must be unconditional: gating it on "
        "opencode_adhd_plugin leaves the file behind on the machine that turned "
        "the flag off after installing"
    )


# ── Always-on injection ─────────────────────────────────────────────────────


def test_defaults_offer_the_always_on_flag_path() -> None:
    defaults = _defaults()
    assert "opencode_adhd_always_on" in defaults, (
        "defaults/main.yaml must declare opencode_adhd_always_on; without it "
        "the flag file is never created and the hook stays a no-op"
    )
    flag = str(defaults.get("opencode_adhd_always_on_flag", ""))
    assert flag, "defaults/main.yaml must declare opencode_adhd_always_on_flag"
    assert ".i-have-adhd-always" in flag, (
        "the flag path must be the filename upstream's hook reads "
        f"(.i-have-adhd-always), got {flag!r}"
    )
    assert "ansible_facts['env']['HOME']" in flag, (
        f"the flag path must resolve from the user's home at deploy time, got {flag!r}"
    )


def test_always_on_is_enabled_by_default() -> None:
    """Author request 2026-11-17: agents shape output on every reply.

    Installed-but-flagless is a silent no-op — the hook is registered and
    injects nothing. Defaulting this false reintroduces exactly that state, and
    nothing else in the suite notices, so the default is pinned here.
    """
    defaults = _defaults()
    assert defaults["opencode_adhd_always_on"] is True, (
        "opencode_adhd_always_on must default to true: the author asked for the "
        "hook to shape every reply, and a false default leaves the plugin "
        "installed but injecting nothing"
    )


def test_install_creates_the_always_on_flag_the_hook_reads() -> None:
    """Installed but flagless is the failure this pins: a silent no-op."""
    install = _tasks("install")
    task = _named(install, "Enable i-have-adhd always-on injection")
    path = str(task["ansible.builtin.file"]["path"])
    assert "opencode_adhd_always_on_flag" in path, (
        f"the flag task must write the path the plugin reads, got {path!r}"
    )
    when_text = " ".join(task.get("when") or [])
    assert "opencode_adhd_always_on" in when_text, (
        "creating the flag must be gated on opencode_adhd_always_on, so the "
        f"author's off switch actually turns it off, got: {when_text!r}"
    )


def test_teardown_removes_the_always_on_flag_unconditionally() -> None:
    remove = _tasks("remove")
    task = _named(remove, "Remove the i-have-adhd always-on flag")
    assert task["ansible.builtin.file"]["state"] == "absent", (
        "teardown must remove the flag, not touch it"
    )
    assert "when" not in task, (
        "the flag teardown must be unconditional: gating it on "
        "opencode_adhd_always_on leaves the file behind after the author turns "
        "always-on off"
    )


def test_install_and_teardown_agree_on_the_flag_path() -> None:
    install = _tasks("install")
    remove = _tasks("remove")
    created = str(
        _named(install, "Enable i-have-adhd always-on injection")[
            "ansible.builtin.file"
        ]["path"]
    )
    removed = str(
        _named(remove, "Remove the i-have-adhd always-on flag")["ansible.builtin.file"][
            "path"
        ]
    )
    assert created == removed, (
        f"install creates {created!r} but teardown removes {removed!r}; a "
        "mismatch leaves the flag behind"
    )
