"""A fact's producer must run wherever its consumer runs.

Ansible evaluates a task's `when`, `changed_when`, `failed_when` and `loop`
only for tasks the requested tags select. A variable registered by a task whose
tags are a SUBSET of its consumer's is therefore undefined exactly when the
consumer runs alone — and Ansible reports it as
`A 'when' expression failed: Error while evaluating conditional:
'<var>' is undefined`, which names the reader and never the producer.

That is how two topics broke on `--tags upgrade`, which `update.sh` is:

    apps/dotagents: "Find the global agents manifest"      tags [install, provision]
                    read by "Initialise the global manifest" tags [... upgrade]
    apps/lima:      "Record whether the target release ..." tags [install, provision]
                    read by "Install Lima only when ..."      tags [install, upgrade]

`dotagents` was reported 2026-11-08; `lima` was found by running the same scan
over the tree, so one fix would have left the other latent. The scan is here
rather than in a reviewer's head.

Tag semantics this encodes: a task runs under tag T when T is in its tags
(every tag is OR'd; `always` aside). So a producer covers a consumer exactly
when the consumer's tags are a SUBSET of the producer's.

Not covered, deliberately: facts produced by another role reached through
`import_role` / `include_role` (guards, topic-resolution). Those carry their
own defaults and their own tags, and duplicating their tag graph here would be
a second source of truth that drifts.

Vars this reports cannot come from role defaults, `vars_files`, or the task's
own `vars:` block — a reader is only flagged when the sole producer is a task.
"""

from __future__ import annotations

import re

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT
import pytest
import yaml

DOTFILES = PAYLOAD_ROOT / "dotfiles"
ROLE_ROOTS = (DOTFILES / "apps", DOTFILES / "roles")

# Expressions that can read a variable Ansible has not defined yet. `loop` is
# templated before the task's `when`, so an undefined var there fails too.
EXPRESSION_FIELDS = ("when", "changed_when", "failed_when", "loop", "until")

# Names Ansible or the loop machinery define, never a `register:` of ours.
BUILTINS = {
    "item",
    "ansible_facts",
    "ansible_env",
    "ansible_check_mode",
    "ansible_run_tags",
    "ansible_skip_tags",
    "ansible_play_hosts",
    "hostvars",
    "play_hosts",
    "inventory_hostname",
    "role_path",
    "playbook_dir",
    "lookup",
}


def _role_dirs():
    for root in ROLE_ROOTS:
        if root.is_dir():
            yield from sorted(p for p in root.iterdir() if p.is_dir())


def _flatten(tasks, inherited, task_file):
    """Yield (task, effective_tags) walking `block:` nesting."""
    for task in tasks or []:
        if not isinstance(task, dict):
            continue
        # `never` is a suppression marker, not a lifecycle tag: a task carrying
        # it runs only when explicitly requested, so it cannot be counted as
        # covering a reader.
        own = set(task.get("tags") or []) - {"never"}
        tags = inherited | own
        yield task, tags, task_file
        if isinstance(task.get("block"), list):
            yield from _flatten(task["block"], tags, task_file)


def _collected_always_defined(role):
    """Names that are defined by role data, not by a task.

    A var declared in `defaults/` or `vars/`, or in a top-level `vars:` block
    of an imported task file, is present for every task. Reading one of those
    cannot fail, so it is never a finding.
    """
    names = set()
    for sub in ("defaults", "vars"):
        d = role / sub
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.y*ml")):
            try:
                data = yaml.safe_load(f.read_text()) or {}
            except yaml.YAMLError:
                continue
            if isinstance(data, dict):
                names |= set(data)
    return names


def _imports(role):
    """(file_name, import_tags) for each task file the role's router imports.

    Follows nested `import_tasks` too — `apps/loreai` reaches its registry
    answers through `prompts.yaml`, and a scan that stopped at `main.yaml`
    would report a clean role without reading it. Tags accumulate the way
    Ansible's do: an imported file's tasks inherit every tag on the import
    that reached them.
    """
    main = role / "tasks" / "main.yaml"
    if not main.is_file():
        return []

    found = []
    seen = set()

    def walk(path, inherited):
        try:
            tasks = yaml.safe_load(path.read_text()) or []
        except yaml.YAMLError:
            return
        if not isinstance(tasks, list):
            return
        found.append((path, inherited))
        for entry, tags, _ in _flatten(tasks, inherited, path.name):
            fname = entry.get("ansible.builtin.import_tasks") or entry.get(
                "import_tasks"
            )
            if not fname:
                continue
            nested = path.parent / fname
            if nested.is_file() and nested not in seen:
                seen.add(nested)
                walk(nested, tags)

    walk(main, set())
    return [(p, t) for p, t in found if p.name != "main.yaml"]


def _producers_and_readers(role):
    """Every registered name, and every expression that reads one."""
    producers = {}
    readers = []
    for path, import_tags in _imports(role):
        try:
            tasks = yaml.safe_load(path.read_text()) or []
        except yaml.YAMLError:
            continue
        if not isinstance(tasks, list):
            continue
        fname = path.name
        for task, tags, _ in _flatten(tasks, import_tags, fname):
            name = task.get("name") or (
                task.get("ansible.builtin.import_role") or task.get("import_role")
            )
            registered = task.get("register")
            if registered:
                producers.setdefault(registered, []).append((tags, name, fname))
            for key in ("ansible.builtin.set_fact", "set_fact"):
                for var in task.get(key) or {}:
                    producers.setdefault(var, []).append((tags, name, fname))
            # A task-level `vars:` block defines its names for that task only,
            # so it is not registered as a producer: doing so would let a
            # same-named block elsewhere silence a real finding.
            for field in EXPRESSION_FIELDS:
                if task.get(field):
                    readers.append((str(task[field]), tags, name, fname, field))
    return producers, readers


def _mentions(expression, var):
    """True when `expression` reads `var` as a name, not as an attribute."""
    if re.search(r"(?<![\w.])" + re.escape(var) + r"(?![\w])", expression) is None:
        return False
    # `{{ x | default(...) }}` relents when x is undefined, so it is not a read
    # that can fail.
    if re.search(re.escape(var) + r"\s*\|\s*default\b", expression):
        return False
    return True


def _violations(role):
    always = _collected_always_defined(role)
    producers, readers = _producers_and_readers(role)
    for expression, consumer_tags, consumer, fname, field in readers:
        for var, sites in producers.items():
            if var in always or var in BUILTINS:
                continue
            if not _mentions(expression, var):
                continue
            if any(producer_tags >= consumer_tags for producer_tags, _, _ in sites):
                continue
            missing = sorted(consumer_tags - set().union(*(s[0] for s in sites)))
            yield (
                f"{role.name}/{fname}: {consumer!r} reads {var!r} in `{field}` "
                f"with tags {sorted(consumer_tags)}, but the producing task "
                f"{sites[0][1]!r} in {sites[0][2]} carries only "
                f"{sorted(sites[0][0])} — missing {missing}. "
                f"A task run under {missing} selects the consumer and not the "
                f"producer, so {var!r} is undefined there."
            )


@pytest.mark.parametrize("role", list(_role_dirs()), ids=lambda p: p.name)
def test_every_registered_fact_is_produced_wherever_it_is_read(role):
    findings = list(_violations(role))
    assert not findings, "tag coverage is incomplete:\n\n" + "\n\n".join(findings)


def test_the_scan_finds_the_roles_it_is_meant_to_scan():
    """Keep the parametrisation honest: an empty list would pass silently."""
    names = {p.name for p in _role_dirs()}
    assert {"dotagents", "lima"} <= names, names
