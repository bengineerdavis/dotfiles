"""Lifecycle-contract tests for the herdr topic (dimension 1 of the swarm).

Deduced contract, from written artifacts only: dotfiles/apps/herdr/README.md
(the design record), dotfiles/docs/TOPICS.md (topic format source of truth),
dotfiles/docs/TOPIC-RECIPES.md (generalized recipes), root spec.md (§ Layering,
§ Verification), TASKS.md § Now herdr lines, the apps/ollama topic as
structural precedent, and herdr upstream docs (install + integrations).

Artifacts under test:

- apps/herdr/topic.yml — five convention keys (TOPICS.md § topic.yml schema):
  topic_name == 'herdr' matching the directory; topic_provides == ['herdr'];
  topic_requires == ['mise']; topic_os covering both Darwin and Debian;
  topic_tier == 'app'. The 'mise' requirement must resolve because
  apps/mise/topic.yml declares 'mise' in its topic_provides (TOPICS.md
  § Dependency resolution).
- tasks/main.yaml — the lifecycle router: imports of bootstrap,
  prerequisites, upgrade, install and remove, the first four tagged
  [lifecycle-tag, provision] and remove tagged [remove, never] (TOPICS.md
  § Lifecycle tags). A bare run never tears down; --tags remove is the
  deliberate opt-in.
- CRUD/teardown invariant (TOPICS.md § CRUD ownership invariant; spec.md
  § Layering — teardown changes with the thing it creates): whatever
  install.yaml creates has a counterpart in remove.yaml, derived from the
  manifest rather than a hand-copied list (the ollama launchctl-unsetenv
  lesson). README-named created state: the mise entry, agent-integration
  installs, the Darwin launchd plist
  ~/Library/LaunchAgents/com.herdr.server.plist, the Debian systemd user
  unit ~/.config/systemd/user/herdr-server.service, the zsh completion
  ~/.zfunc/_herdr — and, if install.yaml were to create it, the config file.
- Teardown ordering per the README structure note: integrations, then the
  service, then the mise entry (the entry removal prunes the binary the
  other two teardowns still need).
- The integration-uninstall gate herdr_remove_integrations defaults OFF
  (defaults/main.yaml) and every uninstall task relents through it
  (spec.md § Verification — a mechanism that can decline is proven to
  relent in both directions).
- Upgrade routes through `mise upgrade`; the topic never calls
  `herdr update`, which is valid for direct installs only (README;
  TOPICS.md § Currency for anything brew and apt do not install).
- playbook.yaml at the topic root is the standalone runner pointing at the
  role (ollama precedent).
- The topic changes other topics' files only through the sanctioned
  first-party command (`mise use` / `mise unuse` writing through the
  deployed symlink), never by a direct file write into the mise topic's
  tracked config.toml (TOPIC-RECIPES.md, tool-entry ownership recipe).

Authored failing-first: the topic does not exist yet, so every test fails
now naming the missing artifact, and turns green when the topic lands
without further edits.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
TOPIC = REPO / "dotfiles" / "apps" / "herdr"
MISE_TOPIC = REPO / "dotfiles" / "apps" / "mise"

TOPIC_NAME = "herdr"

# README-named created state and its teardown counterparts.
PLIST_LABEL = "com.herdr.server.plist"
PLIST_PATH_SUFFIX = "Library/LaunchAgents/com.herdr.server.plist"
UNIT_LABEL = "herdr-server.service"
UNIT_PATH_SUFFIX = ".config/systemd/user/herdr-server.service"
COMPLETION_TOKEN = "_herdr"
ENTRY_INSTALL = r"mise\s+use\s+-g\s+(?:herdr|github:herdrdev/herdr)\b"
ENTRY_REMOVE = r"mise\s+unuse\s+--global\s+herdr"
INTEGRATION_INSTALL = r"herdr\s+integration\s+install\b"
INTEGRATION_UNINSTALL = r"herdr\s+integration\s+uninstall\b"
COMPLETION_INSTALL = r"herdr\s+completion\s+zsh\b"
SERVICE_STOP = r"bootout|bootctl|launchctl\s+disable|state:\s*stopped"
GATE_VAR = "herdr_remove_integrations"

# Modules that create file state (counterpart teardown required).
FILE_CREATING_MODULES = {
    "ansible.builtin.template",
    "ansible.builtin.copy",
    "ansible.builtin.get_url",
    "ansible.builtin.blockinfile",
    "ansible.builtin.file",
}

_RESERVED_KEYS = {
    "name", "when", "tags", "register", "vars", "loop", "become",
    "become_user", "become_method", "become_flags", "changed_when",
    "failed_when", "args", "loop_control", "until", "retries", "delay",
    "notify", "ignore_errors", "delegate_to", "environment", "no_log",
    "check_mode", "block", "rescue", "always", "any_errors_fatal",
    "run_once", "connection", "listen", "throttle", "order",
    "vars_files", "module_defaults",
}


# ── helpers (hl_ prefix; self-contained, no conftest.py) ────────────────────

def hl_load_yaml(relpath: str):
    """Load a topic YAML file, failing with the artifact named if absent."""
    path = TOPIC / relpath
    if not path.is_file():
        pytest.fail(f"{TOPIC.relative_to(REPO) / relpath} missing — herdr topic not implemented")
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        pytest.fail(f"{TOPIC.relative_to(REPO) / relpath} is not valid YAML: {exc}")
    if data is None:
        pytest.fail(f"{TOPIC.relative_to(REPO) / relpath} is empty — herdr topic not implemented")
    return data


def hl_text(relpath: str) -> str:
    """Raw text of a topic file, failing with the artifact named if absent."""
    path = TOPIC / relpath
    if not path.is_file():
        pytest.fail(f"{TOPIC.relative_to(REPO) / relpath} missing — herdr topic not implemented")
    return path.read_text()


def hl_when_str(when) -> str:
    if when is None:
        return ""
    if isinstance(when, (list, tuple)):
        return " and ".join(hl_when_str(w) for w in when)
    return str(when)


def hl_tags(task: dict) -> list:
    tags = task.get("tags", [])
    if isinstance(tags, str):
        return [tags]
    return [str(t) for t in (tags or [])]


def hl_module(task: dict):
    """The task's module key — FQCN per TOPICS.md § Fully qualified module names."""
    for key in task:
        if key in _RESERVED_KEYS:
            continue
        if "." in key:
            return key
    for key in task:
        if key in _RESERVED_KEYS:
            continue
        return key
    return None


def hl_tasks(doc):
    """Flatten a task file into its tasks, recursing into block/rescue/always."""
    flat = []

    def walk(items):
        if not isinstance(items, list):
            return
        for item in items:
            if not isinstance(item, dict):
                continue
            if "block" in item:
                walk(item["block"])
                walk(item.get("rescue", []))
                walk(item.get("always", []))
            else:
                flat.append(item)

    walk(doc if isinstance(doc, list) else [doc])
    return flat


def hl_tasks_with_gates(doc):
    """Flatten a task file into (task, [effective when-strings from parents])."""
    out = []

    def walk(items, gates):
        if not isinstance(items, list):
            return
        for item in items:
            if not isinstance(item, dict):
                continue
            gates_here = list(gates)
            when = item.get("when")
            if when is not None:
                gates_here.append(hl_when_str(when))
            if "block" in item:
                walk(item["block"], gates_here)
                walk(item.get("rescue", []), gates_here)
                walk(item.get("always", []), gates_here)
            else:
                out.append((item, gates_here))

    walk(doc if isinstance(doc, list) else [doc], [])
    return out


def hl_task_text(task: dict) -> str:
    return yaml.safe_dump(task, default_flow_style=False)


def hl_first_index(tasks, pattern: str):
    """Index of the first task whose serialized text matches, else None."""
    for i, task in enumerate(tasks):
        if re.search(pattern, hl_task_text(task)):
            return i
    return None


def hl_all_indices(tasks, pattern: str):
    return [i for i, t in enumerate(tasks) if re.search(pattern, hl_task_text(t))]


def hl_created_paths(install_tasks):
    """Derive created file paths from install.yaml (never a hand-copied list).

    Only file-creating modules and non-directory/absent states count: a
    created directory is infrastructure, not state the CRUD invariant pins
    (ollama precedent: teardown removes links and files, not the dirs).
    Paths without a literal slash (pure-variable dests) are skipped — a var
    cannot be resolved statically; the command-marker tests cover the
    README-named state regardless.
    """
    paths = []
    for task in install_tasks:
        mod = hl_module(task)
        if mod not in FILE_CREATING_MODULES:
            continue
        state = str(task.get("state", "file"))
        if state in ("directory", "absent"):
            continue
        # Module args may be nested under the module key (the house's standard
        # dict form — ollama/vscode precedent) or flat at task level; read both.
        # (First red run: only top-level keys were read, so nested-args tasks
        # derived nothing and the CRUD check could not proceed; fixed
        # 2026-09-19.)
        module_args = task.get(mod)
        args = module_args if isinstance(module_args, dict) else {}
        raw = task.get("dest") or task.get("path") or args.get("dest") or args.get("path")
        if not raw:
            continue
        raw = str(raw)
        if "/" not in raw:
            continue
        name = Path(raw.split("}}")[-1] if "{{" in raw else raw).name
        if name and "{{" not in name:
            paths.append(name)
    return sorted(set(paths))


def hl_command_arg_lines(task: dict):
    """Raw argument lines of a command/shell task, full-line comments stripped."""
    mod = hl_module(task)
    val = task.get(mod) if mod else None
    if isinstance(val, dict):
        if "cmd" in val:
            lines = str(val["cmd"]).splitlines()
        elif "argv" in val:
            lines = [" ".join(str(a) for a in val["argv"])]
        else:
            lines = hl_task_text(task).splitlines()
    elif isinstance(val, str):
        lines = val.splitlines()
    else:
        lines = hl_task_text(task).splitlines()
    return [ln for ln in lines if not ln.lstrip().startswith("#")]


# ── tests ───────────────────────────────────────────────────────────────────

def test_topic_yml_exists_with_five_convention_fields():
    # mutation: drop any one of the five keys from topic.yml
    meta = hl_load_yaml("topic.yml")
    fields = ("topic_name", "topic_provides", "topic_requires", "topic_os", "topic_tier")
    for field in fields:
        assert field in meta, (
            f"topic.yml is missing '{field}' — TOPICS.md § topic.yml schema "
            f"requires all five convention keys"
        )
    assert isinstance(meta["topic_name"], str), "topic_name must be a string"
    for field in ("topic_provides", "topic_requires", "topic_os"):
        assert isinstance(meta[field], list) and meta[field], (
            f"topic.yml '{field}' must be a non-empty list"
        )
    assert meta["topic_tier"] in ("pkg-manager", "runtime-manager", "app"), (
        f"topic_tier '{meta['topic_tier']}' is not a valid tier"
    )


def test_topic_yml_values_match_the_written_contract():
    # mutation: change topic_tier to runtime-manager, drop Debian from
    # topic_os, or put homebrew in topic_requires (README: Debian stays
    # schedulable precisely because homebrew is not required)
    meta = hl_load_yaml("topic.yml")
    assert meta["topic_name"] == TOPIC_NAME, (
        f"topic_name '{meta['topic_name']}' must equal the directory name 'herdr'"
    )
    assert TOPIC_NAME in meta["topic_provides"], (
        f"topic_provides must include '{TOPIC_NAME}' (README: topic_provides: [herdr])"
    )
    assert "mise" in meta["topic_requires"], (
        "topic_requires must include 'mise' — the binary installs through mise"
    )
    assert "homebrew" not in meta["topic_requires"], (
        "topic_requires must not declare 'homebrew' — it would make the topic "
        "unschedulable on Debian (README § Both OSes)"
    )
    assert "Darwin" in meta["topic_os"] and "Debian" in meta["topic_os"], (
        f"topic_os {meta['topic_os']} must cover both Darwin and Debian"
    )
    assert meta["topic_tier"] == "app", (
        f"topic_tier must be 'app' (README: topic_tier: app), got '{meta['topic_tier']}'"
    )


def test_topic_requires_resolve_against_the_mise_topic():
    # mutation: change topic_requires to a dep no topic provides (NO_TOPIC),
    # or remove 'mise' from apps/mise/topic.yml's topic_provides
    mise_meta = hl_load_yaml_reldir(MISE_TOPIC, "topic.yml")
    assert "mise" in mise_meta.get("topic_provides", []), (
        "apps/mise/topic.yml must declare 'mise' in topic_provides — that is "
        "what resolves herdr's requirement in provides_map"
    )
    meta = hl_load_yaml("topic.yml")
    for dep in meta["topic_requires"]:
        provided = any(
            dep in other.get("topic_provides", [])
            for other in _all_topic_meta()
        )
        assert provided, (
            f"topic_requires entry '{dep}' resolves as NO_TOPIC: no topic in "
            f"apps/ declares it in topic_provides"
        )


def hl_load_yaml_reldir(base: Path, relpath: str):
    path = base / relpath
    if not path.is_file():
        pytest.fail(f"{base.relative_to(REPO) / relpath} missing — required for dependency resolution")
    data = yaml.safe_load(path.read_text())
    if data is None:
        pytest.fail(f"{base.relative_to(REPO) / relpath} is empty")
    return data


def _all_topic_meta():
    apps = REPO / "dotfiles" / "apps"
    metas = []
    for topic_yml in sorted(apps.glob("*/topic.yml")):
        data = yaml.safe_load(topic_yml.read_text())
        if isinstance(data, dict):
            metas.append(data)
    return metas


def test_router_imports_all_five_lifecycle_files_with_lifecycle_tags():
    # mutation: delete one of the five imports, or drop a lifecycle tag
    main = hl_load_yaml("tasks/main.yaml")
    expected = {
        "bootstrap.yaml": {"bootstrap", "provision"},
        "prerequisites.yaml": {"prerequisites", "provision"},
        "upgrade.yaml": {"upgrade", "provision"},
        "install.yaml": {"install", "provision"},
        "remove.yaml": {"remove", "never"},
    }
    found = {}
    for task in hl_tasks(main):
        imp = task.get("ansible.builtin.import_tasks") or task.get("import_tasks")
        if not imp:
            continue
        fname = Path(str(imp)).name
        if fname in expected:
            found[fname] = set(hl_tags(task))
    for fname, want in expected.items():
        assert fname in found, (
            f"tasks/main.yaml has no import_tasks of {fname} — the lifecycle "
            f"router must wire all five files"
        )
        missing = want - found[fname]
        assert not missing, (
            f"import of {fname} is tagged {sorted(found[fname])}; missing "
            f"required tags {sorted(missing)}"
        )


def test_bare_run_declines_to_remove():
    # mutation: drop the 'never' tag from the remove import so a bare
    # provision run tears the topic down
    main = hl_load_yaml("tasks/main.yaml")
    for task in hl_tasks(main):
        imp = task.get("ansible.builtin.import_tasks") or task.get("import_tasks")
        if imp and Path(str(imp)).name == "remove.yaml":
            assert "never" in hl_tags(task), (
                "the remove import must carry the 'never' tag — without it a "
                "bare run (no --tags) tears the topic down, violating TOPICS.md "
                "§ Lifecycle tags"
            )
            return
    pytest.fail(
        "tasks/main.yaml has no import of remove.yaml — the teardown is "
        "unreachable, so a bare run cannot be proven safe"
    )


def test_explicit_remove_tag_relents():
    # mutation: drop the 'remove' tag from the remove import so even
    # --tags remove cannot reach the teardown
    main = hl_load_yaml("tasks/main.yaml")
    for task in hl_tasks(main):
        imp = task.get("ansible.builtin.import_tasks") or task.get("import_tasks")
        if imp and Path(str(imp)).name == "remove.yaml":
            assert "remove" in hl_tags(task), (
                "the remove import must also carry the 'remove' tag — "
                "--tags remove must select it, or uninstall is unreachable"
            )
            return
    pytest.fail(
        "tasks/main.yaml has no import of remove.yaml — --tags remove has "
        "nothing to select"
    )


def test_standalone_playbook_targets_the_role():
    # mutation: point playbook.yaml at another role, or delete it
    play = hl_load_yaml("playbook.yaml")
    assert isinstance(play, list) and play, "playbook.yaml must contain a play"
    play = play[0]
    assert str(play.get("hosts", "")) == "localhost", (
        "playbook.yaml must run on localhost (standalone runner, ollama precedent)"
    )
    roles = play.get("roles", [])
    role_names = [
        r if isinstance(r, str) else str(r.get("role", ""))
        for r in roles
    ]
    assert any("apps/herdr" in name for name in role_names), (
        f"playbook.yaml roles {role_names} must include the herdr role "
        f"'apps/herdr' (README § Structure: standalone runner)"
    )


def test_install_creates_the_readme_named_state():
    # mutation: drop the launchd plist task, the systemd unit task, the
    # completion task or the mise entry from install.yaml
    install_text = hl_text("tasks/install.yaml")
    for artifact, token in [
        ("the mise entry (README: mise use -g herdr)", ENTRY_INSTALL),
        ("the Darwin launchd plist path", PLIST_PATH_SUFFIX),
        ("the Darwin plist template", None),
        ("the Debian systemd user unit path", UNIT_PATH_SUFFIX),
        ("the Debian unit template", None),
        ("the zsh completion install (herdr completion zsh)", COMPLETION_INSTALL),
    ]:
        if token is None:
            template = (
                "templates/com.herdr.server.plist.j2"
                if "plist" in artifact
                else "templates/herdr-server.service.j2"
            )
            assert (TOPIC / template).is_file(), (
                f"{template} missing — README § Structure requires the service "
                f"unit templates"
            )
            continue
        assert re.search(token, install_text), (
            f"tasks/install.yaml does not create {artifact} — README § "
            f"Decisions names it as topic-owned state"
        )


def test_every_created_state_has_a_teardown_counterpart():
    # mutation: delete any single teardown task from remove.yaml so created
    # state loses its counterpart (the ollama launchctl-unsetenv lesson:
    # derive from the manifest, never a hand-copied list)
    install_tasks = hl_tasks(hl_load_yaml("tasks/install.yaml"))
    remove_text = hl_text("tasks/remove.yaml")

    created_paths = hl_created_paths(install_tasks)
    assert created_paths, (
        "derived no created file paths from tasks/install.yaml — cannot check "
        "the CRUD invariant; install.yaml should create the README-named state"
    )
    for name in created_paths:
        assert name in remove_text, (
            f"install.yaml creates '{name}' but tasks/remove.yaml has no "
            f"counterpart for it — TOPICS.md § CRUD ownership invariant"
        )

    counterpart_of = [
        (ENTRY_INSTALL, ENTRY_REMOVE, "mise use -g herdr", "mise unuse --global herdr"),
        (INTEGRATION_INSTALL, INTEGRATION_UNINSTALL,
         "herdr integration install", "herdr integration uninstall"),
        (COMPLETION_INSTALL, COMPLETION_TOKEN,
         "herdr completion zsh", "removal of the ~/.zfunc/_herdr file"),
    ]
    for install_pat, remove_pat, what, counterpart in counterpart_of:
        assert re.search(install_pat, hl_task_texts_join(install_tasks)), (
            f"tasks/install.yaml does not run {what} — README names it as "
            f"install state; the CRUD check cannot proceed without it"
        )
        assert re.search(remove_pat, remove_text), (
            f"install.yaml runs {what} but remove.yaml has no counterpart "
            f"({counterpart})"
        )


def hl_task_texts_join(tasks) -> str:
    return "\n".join(hl_task_text(t) for t in tasks)


def test_teardown_order_integrations_then_service_then_entry():
    # mutation: reorder remove.yaml so the mise entry is removed before the
    # integrations or the service are torn down (the entry removal prunes
    # the binary the other two teardowns need)
    remove_tasks = hl_tasks(hl_load_yaml("tasks/remove.yaml"))
    idx_integrations = hl_first_index(remove_tasks, INTEGRATION_UNINSTALL)
    idx_service = hl_first_index(remove_tasks, SERVICE_STOP)
    idx_entry = hl_first_index(remove_tasks, ENTRY_REMOVE)
    for label, idx in [
        ("an integration uninstall task", idx_integrations),
        ("a service stop/bootout task", idx_service),
        ("the mise unuse entry removal", idx_entry),
    ]:
        assert idx is not None, (
            f"tasks/remove.yaml has no {label} — teardown cannot be ordered "
            f"without it"
        )
    assert idx_integrations < idx_service < idx_entry, (
        f"remove.yaml teardown order is wrong: integrations at index "
        f"{idx_integrations}, service at {idx_service}, mise entry at "
        f"{idx_entry} — README § Structure: 'gated, ordered: integrations → "
        f"service → entry'"
    )


def test_service_stopped_before_unit_files_removed():
    # mutation: move the plist/unit removal ahead of the stop/bootout
    remove_tasks = hl_tasks(hl_load_yaml("tasks/remove.yaml"))
    idx_stop = hl_first_index(remove_tasks, SERVICE_STOP)
    unit_removal = [i for i, t in enumerate(remove_tasks)
                    if ("com.herdr.server.plist" in hl_task_text(t)
                        or "herdr-server.service" in hl_task_text(t))
                    and ("absent" in hl_task_text(t) or "rm " in hl_task_text(t))]
    assert idx_stop is not None, (
        "tasks/remove.yaml never stops the service (no bootout/bootctl/"
        "stopped task)"
    )
    assert unit_removal, (
        "tasks/remove.yaml never removes the service unit files "
        "(plist or herdr-server.service)"
    )
    first_unit = unit_removal[0]
    assert idx_stop <= first_unit, (
        f"remove.yaml removes the unit files (first at index {first_unit}) "
        f"before stopping the service (first stop at index {idx_stop}) — "
        f"stop the service first"
    )


def test_remove_uninstall_set_is_the_claimed_intersection():
    # mutation: replace the intersection with the whole installed set (or the
    # whole claimed list) — remove would then uninstall integrations the
    # topic does not own, or phantom-call uninstalls for absent claims. The
    # contract module pins the RULE; this pins the YAML to compute it.
    remove_text = hl_text("tasks/remove.yaml")
    intersection = re.search(
        r"herdr_claimed_ids\s*\|\s*select\('in',\s*herdr_installed_ids\)",
        remove_text,
    )
    assert intersection, (
        "tasks/remove.yaml does not compute the uninstall set as the "
        "claimed ∩ installed intersection — TOPIC-RECIPES.md shared-catalogue "
        "recipe: never everything installed, never phantom claims"
    )
    assert re.search(r"loop:\s*\"?\s*\{\{.*herdr_uninstall_ids", remove_text), (
        "tasks/remove.yaml's uninstall loop does not consume the resolved "
        "intersection set (herdr_uninstall_ids)"
    )


def test_no_orphan_teardown_state_in_remove():
    # mutation: add a remove.yaml teardown for state install.yaml never
    # creates (e.g. deleting a config file the topic does not own) — the
    # reverse direction of the CRUD invariant, added after judge round 1
    # (dotfiles/docs/JUDGE-SELECTION.md) flagged the check as one-way.
    install_text = hl_text("tasks/install.yaml")
    remove_tasks = hl_tasks(hl_load_yaml("tasks/remove.yaml"))
    removed_paths = []
    for task in remove_tasks:
        mod = hl_module(task)
        module_args = task.get(mod)
        args = module_args if isinstance(module_args, dict) else {}
        raw = task.get("dest") or task.get("path") or args.get("dest") or args.get("path")
        if not raw:
            continue
        raw = str(raw)
        if "/" not in raw:
            continue
        name = Path(raw.split("}}")[-1] if "{{" in raw else raw).name
        if name and "{{" not in name:
            removed_paths.append(name)
    orphans = [name for name in sorted(set(removed_paths)) if name not in install_text]
    assert not orphans, (
        f"remove.yaml tears down {orphans} but install.yaml never creates "
        "them — orphaned teardown state (CRUD invariant, reverse direction)"
    )


def test_playbook_passes_ansible_syntax_check():
    # mutation: a task-structure error (bad module arg, malformed block, a
    # Jinja block left unclosed at the YAML level) — static greps do not
    # execute Ansible, so the real syntax checker is the only structural
    # proof. Needs ansible-core in the run env:
    #   uv run --with pytest --with pyyaml --with jinja2 --with ansible-core \
    #     pytest tests/herdr -q
    # (Judge round 1, gap 3 — the cheap, real half of "expand the task graph".
    # Scope note: this validates the SOURCE tree. Nothing runs from the repo —
    # chezmoi copies dotfiles/ into the environment and ansible executes the
    # DEPLOYED tree, so the author's converge pass is the deployed-tree proof
    # (and `chezmoi status` must be clean first).)
    import subprocess

    ansible = None
    for candidate in ("ansible-playbook", "ansible"):
        probe = subprocess.run(["uv", "run", "--with", "ansible-core", candidate,
                                "--version"], capture_output=True, text=True)
        if probe.returncode == 0:
            ansible = candidate
            break
    assert ansible == "ansible-playbook", (
        "ansible-playbook unavailable via `uv run --with ansible-core` — the "
        "syntax check cannot run; run the suite with --with ansible-core"
    )
    proc = subprocess.run(
        ["uv", "run", "--with", "ansible-core", "ansible-playbook",
         "--syntax-check", "apps/herdr/playbook.yaml"],
        cwd=REPO / "dotfiles",  # roles path is the dotfiles root, as run-role.sh
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, (
        f"ansible-playbook --syntax-check failed (rc={proc.returncode}, read "
        f"directly): {proc.stderr.strip() or proc.stdout.strip()}"
    )


def test_remove_integrations_gate_defaults_off():
    # mutation: flip the herdr_remove_integrations default to true so a
    # plain --tags remove uninstalls integrations the topic does not own
    defaults = hl_load_yaml("defaults/main.yaml")
    assert GATE_VAR in defaults, (
        f"defaults/main.yaml must define '{GATE_VAR}' (README: gate pattern "
        f"as vscode_remove_extensions)"
    )
    assert not defaults[GATE_VAR], (
        f"{GATE_VAR} must default to false (off) — README: teardown gate, "
        f"default off, got {defaults[GATE_VAR]!r}"
    )
    remove_tasks = hl_tasks(hl_load_yaml("tasks/remove.yaml"))
    assert any(
        GATE_VAR in hl_task_text(t) for t in remove_tasks
    ), f"tasks/remove.yaml never references '{GATE_VAR}' — the gate gates nothing"


def test_every_integration_uninstall_task_relents_through_the_gate():
    # mutation: add an ungated herdr integration uninstall task to
    # remove.yaml (or hardcode its when to false so the gate can never relent)
    remove_doc = hl_load_yaml("tasks/remove.yaml")
    gated = hl_tasks_with_gates(remove_doc)
    uninstall = [
        (task, gates) for task, gates in gated
        if re.search(INTEGRATION_UNINSTALL, hl_task_text(task))
    ]
    assert uninstall, (
        "tasks/remove.yaml has no integration uninstall tasks — the gated "
        "teardown the README requires does not exist"
    )
    for task, gates in uninstall:
        gate_text = " ".join(gates)
        assert GATE_VAR in gate_text, (
            f"integration uninstall task '{task.get('name')}' is not gated by "
            f"'{GATE_VAR}' (own when: {hl_when_str(task.get('when'))!r}) — "
            f"every uninstall task must relent through the gate"
        )
        assert gate_text.strip().lower() != "false", (
            f"integration uninstall task '{task.get('name')}' is hardcoded "
            f"to never run (when: false) — the gate could never relent"
        )


def test_upgrade_routes_through_mise_and_never_self_updates():
    # mutation: make upgrade.yaml call `herdr update` (valid for direct
    # installs only), or leave it an empty stub with no mise upgrade path
    for relpath in ("tasks/upgrade.yaml", "tasks/install.yaml", "tasks/main.yaml"):
        tasks = hl_tasks(hl_load_yaml(relpath))
        for task in tasks:
            mod = hl_module(task)
            if mod in ("ansible.builtin.command", "ansible.builtin.shell",
                       "ansible.builtin.script", "command", "shell"):
                body = "\n".join(hl_command_arg_lines(task))
                assert not re.search(r"\bherdr\s+update\b", body), (
                    f"{relpath} task '{task.get('name')}' calls 'herdr update' — "
                    f"never self-update a mise-managed install (README; "
                    f"TOPIC-RECIPES.md: mise installs are upgraded by "
                    f"'mise upgrade')"
                )
    upgrade_text = hl_text("tasks/upgrade.yaml")
    assert re.search(r"mise\s+upgrade\b", upgrade_text), (
        "tasks/upgrade.yaml does not route through 'mise upgrade' — a "
        "mise-managed tool has no other currency path (TOPICS.md § Currency "
        "for anything brew and apt do not install)"
    )


def test_install_wires_integrations_only_after_the_mise_entry():
    # mutation: move the integration loop ahead of the mise entry in
    # install.yaml — the integrations need the herdr binary that the entry
    # installs
    install_tasks = hl_tasks(hl_load_yaml("tasks/install.yaml"))
    idx_entry = hl_first_index(install_tasks, ENTRY_INSTALL)
    idx_integrations = hl_first_index(install_tasks, INTEGRATION_INSTALL)
    assert idx_entry is not None, (
        "tasks/install.yaml has no mise entry task (mise use -g herdr)"
    )
    assert idx_integrations is not None, (
        "tasks/install.yaml has no integration install tasks"
    )
    assert idx_entry < idx_integrations, (
        f"install.yaml wires integrations (index {idx_integrations}) before "
        f"the mise entry (index {idx_entry}) — README: the integration loop "
        f"runs only after install; the entry installs the binary it needs"
    )


def test_topic_never_writes_another_topics_files_directly():
    # mutation: replace the sanctioned `mise use -g herdr` with a direct
    # template/copy write into apps/mise/files/config.toml — the entry may
    # only change through mise's own first-party command (TOPIC-RECIPES.md
    # tool-entry ownership)
    for relpath in (
        "tasks/install.yaml", "tasks/remove.yaml",
        "tasks/upgrade.yaml", "tasks/bootstrap.yaml",
        "tasks/prerequisites.yaml",
    ):
        tasks = hl_tasks(hl_load_yaml(relpath))
        for task in tasks:
            if hl_module(task) not in FILE_CREATING_MODULES:
                continue
            text = hl_task_text(task)
            for raw in (task.get("dest"), task.get("path")):
                if raw and "mise" in str(raw) and "config.toml" in str(raw):
                    assert False, (
                        f"{relpath} task '{task.get('name')}' writes the mise "
                        f"config directly ({raw}) — entry changes go through "
                        f"'mise use'/'mise unuse', never a file write into "
                        f"another topic's tracked file"
                    )
