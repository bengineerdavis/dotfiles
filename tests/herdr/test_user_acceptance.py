"""
User-acceptance tests for the herdr topic (test-first; the topic does not
exist yet — only dotfiles/apps/herdr/README.md does).

Dimension: what a user of this repo would check before trusting the topic.
Deduced from the written artifacts only:

- dotfiles/apps/herdr/README.md (the design record — THE contract)
- dotfiles/docs/TOPIC-RECIPES.md (install-mechanism chooser, service
  ownership, never self-update a manager-installed tool)
- spec.md § Verification (render under both os_family values with
  StrictUndefined; a missing variable must raise, not render blank)
- AGENTS.md § Cross-platform / § Machine-specific values are resolved,
  never written out
- TASKS.md § Now, the two herdr task lines (2026-09-19)
- ollama templates (structural convention evidence only)
- herdr upstream docs: install (mise method, `herdr update` caveat),
  cli-reference (`herdr server`, `herdr completion zsh`), config-reference
  (`update.channel`, `session.resume_agents_on_restore`)

Static and render-only. Never runs ansible, never applies chezmoi, never
touches the deployed tree. No conftest.py: every helper is hu_-prefixed.

Run:
    cd /Users/ben.davis/.local/share/chezmoi && \
    uv run --with pytest --with pyyaml --with jinja2 pytest \
    tests/herdr/test_user_acceptance.py -q
"""

from __future__ import annotations

import pathlib
import re
import subprocess

import pytest
import yaml

# jinja2 is a run-env dependency, not an artifact gate: importorskip so the
# documented six-dep suite command skips this module instead of erroring at
# collection (the queued conftest-resilience doctrine). Run the herdr suite
# with --with jinja2 to exercise it.
pytest.importorskip("jinja2", reason="jinja2 not installed")
import jinja2  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[2]
TOPIC = REPO / "dotfiles" / "apps" / "herdr"
CATALOGUE = REPO / "dotfiles" / "config" / "agents.yaml"
MISE_CONFIG = REPO / "dotfiles" / "apps" / "mise" / "files" / "config.toml"
ZSH_TREE = REPO / "dotfiles" / "zsh"

# Every path the README § Structure tree names. A missing one is a named
# failure, never a skip.
STRUCTURE_FILES = (
    "topic.yml",
    "README.md",
    "CHANGELOG.md",
    "playbook.yaml",
    "defaults/main.yaml",
    "tasks/main.yaml",
    "tasks/install.yaml",
    "tasks/upgrade.yaml",
    "tasks/remove.yaml",
    "templates/com.herdr.server.plist.j2",
    "templates/herdr-server.service.j2",
)

OS_FAMILIES = ("Darwin", "Debian")

# Machine-specific literals that must never be written out (AGENTS.md
# resolved-never-written rule; the /home/bdavis precedent in the README).
EMPLOYER_LITERALS = (
    "/Users/ben.davis",
    "/home/bdavis",
    "ben.davis",
    "bdavis",
)


# ---------------------------------------------------------------- helpers


def hu_fail_named(path: pathlib.Path, what: str) -> None:
    """Named failure for a missing artifact — never a skip, never a bare None."""
    pytest.fail(f"MISSING: {path} — {what} does not exist yet", pytrace=False)


def hu_read(path: pathlib.Path, what: str) -> str:
    if not path.is_file():
        hu_fail_named(path, what)
    return path.read_text()


def hu_topic_file(rel: str, what: str) -> str:
    return hu_read(TOPIC / rel, what)


def hu_code_lines(text: str) -> str:
    """Full-line comments dropped, so a comment *naming* a forbidden thing
    (e.g. 'never call herdr update') does not trip a substring check."""
    return "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )


def hu_template(rel: str) -> str:
    path = TOPIC / rel
    if not path.is_file():
        hu_fail_named(path, f"template named in the README structure ({rel})")
    return path.read_text()


def hu_topic_vars() -> dict:
    """Variables the topic's defaults/vars would provide. Derived from the
    topic's own files, never invented here; ansible always supplies the
    ansible_* facts, which are stubbed."""
    ctx: dict = {}
    for rel in ("defaults/main.yaml", "vars/main.yaml"):
        path = TOPIC / rel
        if path.is_file():
            data = yaml.safe_load(path.read_text()) or {}
            if isinstance(data, dict):
                ctx.update(data)
    if not ctx:
        pytest.fail(
            "MISSING: neither defaults/main.yaml nor vars/main.yaml under "
            f"{TOPIC} — no variable set to feed the templates",
            pytrace=False,
        )
    # ansible_facts semantics MEASURED on the deployed run 2026-09-19: user_id
    # is the USERNAME (the converge pass resolved gui/<user_id> to
    # gui/ben.davis, which launchd rejects — the bug that moved launchd
    # management to community.general.launchd); user_uid is the numeric id.
    facts = {
        "os_family": "stub",
        "env": {"HOME": "/Users/testuser", "PATH": "/usr/bin:/bin"},
        "user_id": "testuser",
        "user_uid": 501,
        "user_dir": "/Users/testuser",
        "username": "testuser",
        "architecture": "arm64",
        "hostname": "testhost",
    }
    ctx["ansible_facts"] = facts
    ctx["ansible_env"] = facts["env"]
    ctx["ansible_user_id"] = facts["user_id"]
    ctx["ansible_user_dir"] = facts["user_dir"]
    ctx["ansible_hostname"] = facts["hostname"]
    return ctx


def hu_render(rel: str, os_family: str) -> str:
    """Render a template with StrictUndefined. A missing variable must raise,
    not render blank (spec.md § Verification)."""
    env = jinja2.Environment(
        undefined=jinja2.StrictUndefined, keep_trailing_newline=True
    )
    ctx = hu_topic_vars()
    ctx["ansible_facts"]["os_family"] = os_family
    try:
        return env.from_string(hu_template(rel)).render(**ctx)
    except jinja2.exceptions.UndefinedError as exc:
        pytest.fail(
            f"StrictUndefined render of {rel} under os_family={os_family} "
            f"raised for a missing variable: {exc.message} — a missing var "
            "must raise, not render blank",
            pytrace=False,
        )


def hu_install_text() -> str:
    return hu_topic_file("tasks/install.yaml", "install tasks")


def hu_upgrade_text() -> str:
    return hu_topic_file("tasks/upgrade.yaml", "upgrade tasks")


def hu_remove_text() -> str:
    return hu_topic_file("tasks/remove.yaml", "remove tasks")


def hu_line_index(text: str, pattern: str) -> int:
    """First line index matching pattern, or -1."""
    for i, line in enumerate(text.splitlines()):
        if re.search(pattern, line):
            return i
    return -1


def hu_bash_scripts() -> list[pathlib.Path]:
    """Shell scripts the topic ships, if any."""
    files_dir = TOPIC / "files"
    if not files_dir.is_dir():
        return []
    out = []
    for p in sorted(files_dir.rglob("*")):
        if not p.is_file():
            continue
        text = p.read_text(errors="replace")
        if p.suffix == ".sh" or text.startswith("#!/bin/bash") or text.startswith(
            "#!/usr/bin/env bash"
        ):
            out.append(p)
    return out


def hu_config_template() -> pathlib.Path:
    """The chezmoi source for ~/.config/herdr/config.toml. The README says it
    'deploys as a chezmoi template'; chezmoi source naming is
    dot_config/herdr/config.toml.tmpl at the repo (source) root."""
    d = REPO / "dot_config" / "herdr"
    return d / "config.toml.tmpl"


def hu_topic_tree_files() -> list[pathlib.Path]:
    """Code files only — prose (.md) may legitimately *name* a forbidden
    literal as an anti-pattern example, and the rule is about code."""
    return [
        p
        for p in TOPIC.rglob("*")
        if p.is_file()
        and "__pycache__" not in p.parts
        and p.suffix not in (".md",)
    ]


# ---------------------------------------------------------------- tests


def test_structure_files_exist():
    """Every file the README § Structure tree names exists, by that name."""
    # mutation: rename/drop any structure file (e.g. delete upgrade.yaml) —
    # the failure must name the missing path.
    missing = [rel for rel in STRUCTURE_FILES if not (TOPIC / rel).is_file()]
    if missing:
        pytest.fail(
            "MISSING: " + ", ".join(missing)
            + " — named in dotfiles/apps/herdr/README.md § Structure",
            pytrace=False,
        )
    templates = TOPIC / "templates"
    if not templates.is_dir():
        pytest.fail(
            f"MISSING: {templates} — templates dir is a named failure, not a skip",
            pytrace=False,
        )


def test_agents_yaml_catalogue_exists_with_wired_entries():
    """dotfiles/config/agents.yaml exists (editors.yaml pattern) and carries
    the wired integration ids herdr spells them (cli-reference): opencode,
    claude, cursor; codex listed as a not-wired candidate."""
    # mutation: delete agents.yaml, or drop the claude entry / the codex
    # why-not row — each must fail here by name.
    text = hu_read(CATALOGUE, "shared agent-integration catalogue")
    data = yaml.safe_load(text) or {}

    def hu_ids(node, acc):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "id" and isinstance(v, str):
                    acc.add(v)
                hu_ids(v, acc)
        elif isinstance(node, list):
            for item in node:
                hu_ids(item, acc)

    ids: set[str] = set()
    hu_ids(data, ids)
    for want in ("opencode", "claude", "cursor"):
        assert want in ids, (
            f"{CATALOGUE}: wired herdr integration id '{want}' missing "
            f"(ids found: {sorted(ids)})"
        )
    assert "codex" in text, (
        f"{CATALOGUE}: codex must be listed as a candidate with a why-not, "
        "not omitted silently (README: candidates listed but not wired)"
    )


@pytest.mark.parametrize("os_family", OS_FAMILIES)
@pytest.mark.parametrize(
    "template", ["templates/com.herdr.server.plist.j2", "templates/herdr-server.service.j2"]
)
def test_templates_render_under_both_os_families(template, os_family):
    """Every topic template renders under BOTH os_family values with
    StrictUndefined; a missing variable raises (never renders blank)."""
    # mutation: reference an undefined var in a template, or delete a default
    # from defaults/main.yaml — the render must raise naming the variable.
    out = hu_render(template, os_family)
    assert out.strip(), (
        f"{template} under {os_family} rendered empty — a blank render is a "
        "silent failure, not a success"
    )


def test_launchd_plist_shim_runatload_keepalive():
    """Rendered Darwin plist: Label com.herdr.server, ProgramArguments[0] at
    the stable mise shim path with 'server' as the subcommand, RunAtLoad and
    KeepAlive both true (README service-unit decisions)."""
    # mutation: point ProgramArguments at a version-pinned install path, drop
    # RunAtLoad/KeepAlive, or rename the label — each must fail here.
    out = hu_render("templates/com.herdr.server.plist.j2", "Darwin")
    assert "com.herdr.server" in out, "plist Label must be com.herdr.server"
    assert "<key>RunAtLoad</key>" in out and "<true/>" in out, (
        "launchd agent must have RunAtLoad per the README"
    )
    assert "<key>KeepAlive</key>" in out, (
        "launchd agent must have KeepAlive per the README"
    )
    args = re.search(
        r"<key>ProgramArguments</key>\s*<array>(.*?)</array>", out, re.S
    )
    assert args, "rendered plist has no ProgramArguments array"
    strings = re.findall(r"<string>(.*?)</string>", args.group(1))
    assert strings, "ProgramArguments array is empty"
    assert re.search(r"mise/shims/herdr", strings[0]), (
        f"ProgramArguments[0]={strings[0]!r} is not the stable mise shim "
        "(~/.local/share/mise/shims/herdr) — a version-pinned or "
        "version-manager-agnostic path breaks across upgrades"
    )
    assert "mise/installs/" not in strings[0], (
        "ProgramArguments[0] points into a version-pinned mise install "
        "(mise/installs/...) — breaks on the first upgrade"
    )
    assert any(s.strip() == "server" for s in strings[1:]), (
        "ProgramArguments must invoke the explicit `herdr server` headless "
        "subcommand (cli-reference: for service-style setups)"
    )


def test_systemd_user_unit_shim_and_no_system_unit_markers():
    """Rendered Debian unit: ExecStart at the stable mise shim with the
    `server` subcommand, no version-pinned install path, and no system-unit
    markers (a per-user unit under ~/.config/systemd/user/ is
    WantedBy=default.target, not multi-user.target, and takes no User=)."""
    # mutation: swap ExecStart to a mise/installs/ path or copy a system unit
    # (User=/multi-user.target) — the per-OS distinction must hold.
    out = hu_render("templates/herdr-server.service.j2", "Debian")
    execstart = hu_line_index(out, r"^ExecStart=")
    assert execstart != -1, "systemd unit has no ExecStart"
    line = out.splitlines()[execstart]
    assert re.search(r"mise/shims/herdr", line), (
        f"ExecStart={line!r} does not point at the stable mise shim "
        "(~/.local/share/mise/shims/herdr)"
    )
    assert "mise/installs/" not in line, (
        "ExecStart points into a version-pinned mise install — breaks on upgrade"
    )
    assert re.search(r"\bserver\b", line), (
        "ExecStart must run the `herdr server` headless subcommand"
    )
    assert "WantedBy=multi-user.target" not in out, (
        "unit is a per-user systemd unit, not a system one — "
        "multi-user.target belongs to system units"
    )


def test_never_herdr_update_and_upgrade_routes_through_mise():
    """No topic task/template invokes `herdr update` (valid for self-installs
    only; mise installs upgrade via mise — TOPIC-RECIPES, README). Positive
    counterpart: upgrade.yaml routes through `mise upgrade`."""
    # mutation: replace `mise upgrade` with `herdr update` in upgrade.yaml —
    # this test must go red.
    scan_files = list((TOPIC / "tasks").glob("*.yaml")) + list(
        (TOPIC / "templates").glob("*.j2")
    ) + [TOPIC / "playbook.yaml"]
    for p in scan_files:
        if not p.is_file():
            continue
        code = hu_code_lines(p.read_text())
        hit = re.search(r"\bherdr\s+update(?![\w-])", code)
        assert hit is None, (
            f"{p} invokes `herdr update` — forbidden: it is valid for direct "
            "installs only; mise installs are upgraded by `mise upgrade`"
        )
    up = hu_code_lines(hu_upgrade_text())
    assert hu_line_index(up, r"\bmise\s+upgrade\b") != -1, (
        "tasks/upgrade.yaml does not route upgrades through `mise upgrade`"
    )


def test_install_contains_exact_mise_use_invocation():
    """install.yaml contains the documented `mise use -g herdr` invocation."""
    # mutation: drop the mise use task (leaving only brew/curl) — named red.
    code = hu_code_lines(hu_install_text())
    assert re.search(r"\bmise\s+use\s+(-g|--global)\s+herdr\b", code), (
        "tasks/install.yaml has no `mise use -g herdr` — the topic owns its "
        "mise entry via first-party commands (README, TOPIC-RECIPES)"
    )


def test_entry_probe_precedes_mise_use():
    """The entry-probe comes FIRST in install.yaml so `mise use` is a no-op
    once converged: something is registered (probed) before the `mise use`
    task, and the `mise use` task is guarded on that probe with `when:`."""
    # mutation: reorder — move the mise use task above the probe, or delete
    # the `when:` guard — idempotence is lost and this goes red.
    code = hu_code_lines(hu_install_text())
    use_i = hu_line_index(code, r"\bmise\s+use\s+(-g|--global)\s+herdr\b")
    assert use_i != -1, "no `mise use -g herdr` line to order against"
    before = "\n".join(code.splitlines()[:use_i])
    assert re.search(r"register:", before), (
        "tasks/install.yaml: no probe registering a result BEFORE "
        "`mise use -g herdr` — without the probe the command is not a no-op "
        "once converged (idempotence contract)"
    )
    block = "\n".join(code.splitlines()[use_i : use_i + 12])
    assert re.search(r"\bwhen:", block), (
        "the `mise use -g herdr` task has no `when:` guard on the probe — "
        "it would fire unconditionally every converge"
    )


def test_remove_contains_mise_unuse():
    """remove.yaml runs `mise unuse --global herdr`, which prunes the install."""
    # mutation: replace unuse with a bare `herdr uninstall` or drop the task.
    code = hu_code_lines(hu_remove_text())
    assert re.search(r"\bmise\s+unuse\s+(--global|-g)\s+herdr\b", code), (
        "tasks/remove.yaml has no `mise unuse --global herdr`"
    )


def test_remove_ordered_and_gated():
    """remove.yaml is gated and ordered: integrations → service → entry.
    Integration teardown is gated by herdr_remove_integrations (default off)."""
    # mutation: reorder teardown (entry before service) or delete the
    # herdr_remove_integrations gate — either must go red here.
    code = hu_code_lines(hu_remove_text())
    integ_i = hu_line_index(code, r"herdr_remove_integrations|integration\s+uninstall")
    service_i = hu_line_index(code, r"bootout|launchctl|launchd|systemctl|herdr-server")
    entry_i = hu_line_index(code, r"\bmise\s+unuse\b")
    assert integ_i != -1, "remove.yaml: no integration teardown step"
    assert service_i != -1, "remove.yaml: no service teardown (bootout/systemctl)"
    assert entry_i != -1, "remove.yaml: no mise entry teardown"
    assert integ_i < service_i < entry_i, (
        "remove.yaml teardown out of README order "
        f"(integrations@{integ_i}, service@{service_i}, entry@{entry_i}) — "
        "must be integrations → service → entry"
    )
    assert "herdr_remove_integrations" in code, (
        "remove.yaml: integration teardown is not gated by "
        "herdr_remove_integrations (default off, vscode_remove_extensions pattern)"
    )


def test_config_template_minimal_and_clean():
    """~/.config/herdr/config.toml is captured as a chezmoi template
    (dot_config/herdr/config.toml.tmpl) with exactly the opinionated keys:
    update.channel = "stable" and [session] resume_agents_on_restore = true.
    No secrets, no employer-identifying strings."""
    # mutation: drop update.channel, or add a secret/employer literal to the
    # config template — each direction must fail here.
    path = hu_config_template()
    text = hu_read(
        path,
        "chezmoi template for ~/.config/herdr/config.toml (README: config is "
        "captured, minimally)",
    )
    assert re.search(r'update\.channel\s*=\s*"stable"', text), (
        f"{path}: update.channel = \"stable\" missing"
    )
    assert re.search(r"\[session\]", text) and re.search(
        r"resume_agents_on_restore\s*=\s*true", text
    ), f"{path}: [session] resume_agents_on_restore = true missing"
    for literal in EMPLOYER_LITERALS:
        assert literal not in text, (
            f"{path} contains employer-identifying literal {literal!r}"
        )
    secret_hit = re.search(
        r"(?i)[A-Za-z_-]*(api_?key|token|password|secret)[A-Za-z_-]*\s*=", text
    )
    assert secret_hit is None, (
        f"{path} looks like it embeds a secret ({secret_hit.group(0)!r}) — "
        "the minimal config must contain no secrets"
    )


def test_zsh_completion_topic_owned_not_zsh_tree_owned():
    """install writes `herdr completion zsh` output to the completions dir the
    repo's zsh runtime already puts on fpath
    (~/.local/share/zsh/completions/_herdr, dot_zshrc.tmpl:96) and nothing
    lands in the chezmoi-managed zsh tree (the _ollama_zsh_completion
    dual-ownership trap); remove takes the file back out. Deliberately NOT
    herdr's documented ~/.zfunc recipe — nothing here puts ~/.zfunc on
    fpath, so that completion would be generated and never loaded (found
    post-report 2026-09-19; the README and the topic moved together)."""
    # mutation: write the completion into dotfiles/zsh/ instead of the
    # on-fpath completions dir, or drop the remove-side cleanup — either
    # must go red.
    install = hu_install_text()
    assert re.search(r"completion\s+zsh", install), (
        "install.yaml never runs `herdr completion zsh`"
    )
    assert re.search(r"\.local/share/zsh/completions", install), (
        "install.yaml does not write the completion to the on-fpath "
        "completions dir (~/.local/share/zsh/completions)"
    )
    assert ".zfunc" not in install, (
        "install.yaml still targets ~/.zfunc — on nobody's fpath in this "
        "repo; the completion would be generated and never loaded"
    )
    remove = hu_remove_text()
    assert re.search(r"herdr_completion_path", remove), (
        "remove.yaml does not remove the generated completion (it must tear "
        "down herdr_completion_path; the lifecycle test pins defaults to "
        "completions/_herdr)"
    )
    assert ".zfunc" not in remove, "remove.yaml still references ~/.zfunc"
    stray = [p for p in ZSH_TREE.rglob("*") if p.is_file() and "herdr" in p.name]
    assert not stray, (
        f"completion leaked into the chezmoi zsh tree: {stray} — it is "
        "topic-owned, generated at install time, never vendored"
    )


def test_no_machine_specific_literals_in_topic_tree():
    """No /home/bdavis-style or employer-identifying literal anywhere in the
    topic tree (AGENTS.md: machine-specific values are resolved, never
    written out; the silent-allow-list failure mode)."""
    # mutation: hardcode /Users/ben.davis or the shim path with a literal
    # home dir in a template — this scan goes red.
    offenders = []
    for p in hu_topic_tree_files() + list(
        (REPO / "dot_config" / "herdr").glob("*") if (REPO / "dot_config" / "herdr").is_dir() else []
    ):
        text = hu_code_lines(p.read_text(errors="replace"))
        for literal in EMPLOYER_LITERALS:
            if literal in text:
                offenders.append(f"{p}: {literal}")
    assert not offenders, (
        "machine-specific literals written out (must resolve via "
        f"ansible_facts/chezmoi): {offenders}"
    )


def test_bash_scripts_render_and_pass_bash_n_or_absence_is_recorded():
    """If the topic ships files/ shell scripts, each passes `bash -n`. The
    design ships none, so absence is only accepted when the README structure
    section lists no files/ dir — a script added without the README recording
    it fails here rather than escaping review."""
    # mutation: add a files/ script with a syntax error, or add files/ to the
    # README structure without shipping it — both go red.
    scripts = hu_bash_scripts()
    if not scripts:
        readme = hu_read(TOPIC / "README.md", "the design record")
        assert "files/" not in readme.split("## Structure")[-1].split("##")[
            0
        ], (
            "README § Structure lists a files/ dir but none is shipped — "
            "the decision must be explicit either way"
        )
        return
    for script in scripts:
        proc = subprocess.run(
            ["bash", "-n", str(script)], capture_output=True, text=True
        )
        assert proc.returncode == 0, (
            f"bash -n failed for {script} (rc={proc.returncode}, read "
            f"directly, not through a pipe): {proc.stderr.strip()}"
        )


def test_readme_cross_links_and_named_paths():
    """The README links to the TOPIC-RECIPES.md rows it instantiates and to
    TOPICS.md, and names the catalogue path (dotfiles/config/agents.yaml) —
    the cross-links the design record promises."""
    # mutation: strip the TOPICS.md/TOPIC-RECIPES.md references from the
    # README — the design record stops linking its authority.
    readme = hu_read(TOPIC / "README.md", "the design record")
    assert "TOPIC-RECIPES.md" in readme, "README does not link TOPIC-RECIPES.md"
    assert "TOPICS.md" in readme, "README does not link TOPICS.md (the binding rules)"
    assert str(CATALOGUE.relative_to(REPO)) in readme, (
        f"README does not name the catalogue path {CATALOGUE.relative_to(REPO)}"
    )
