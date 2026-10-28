"""The global opencode template renders a valid, correctly layered config.

Models, providers and agents come from .chezmoidata/opencode.yaml, merged as
common -> os.<os> -> hosts.<hostname>. The permission rules stay literal in
the template because they are order-sensitive (v2 takes the LAST matching
rule) and a data merge would reorder them. These tests render the template
with chezmoi under overridden host/os data, so they exercise the real merge,
not a copy.

The v2 migration (dotfiles/docs/research/opencode-v2/PLAN.md) retargets the
config at opencode v2: the v1 `permission` map becomes a `permissions` array,
`autoupdate` becomes `update`, `bash` rules are renamed `shell`, the trailing
shell catch-all is dropped (author ruling 1), v2's `.env` read protection is
kept after the global read allow (ruling 2), and the trivial-model roles pin
ollama/qwen3.5:9b (ruling 3). The v2-targeted tests here were first seen
failing against the un-migrated v1 tree; they go green with the migration.

Run:
    pytest tests/topics/test_opencode_config_layers.py -v
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess

import pytest
import yaml

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

TEMPLATE = PAYLOAD_ROOT / "dot_config" / "opencode" / "opencode.jsonc.tmpl"
CHEZMOIDATA = PAYLOAD_ROOT / ".chezmoidata" / "opencode.yaml"

pytestmark = pytest.mark.skipif(
    shutil.which("chezmoi") is None, reason="chezmoi not on PATH"
)

TARGET_SCHEMA = "https://opencode.ai/config.json"
SMALL_MODEL = "ollama/qwen3.5:9b"  # author ruling 3, 2026-10-06

# The action set of the migrated array (PLAN.md § The exact v1->v2 permission
# mapping). v1's `list` is not a v2 action and is deliberately dropped.
TARGET_ACTIONS = {
    "shell",
    "read",
    "glob",
    "grep",
    "edit",
    "webfetch",
    "websearch",
    "external_directory",
}

# The shell allow-list, in the plan's spelling. Order among these is not
# load-bearing (disjoint patterns); their presence and their position AFTER
# the catch-all are.
SHELL_ALLOWS = [
    "git *",
    "mise *",
    "cat *",
    "head *",
    "wc *",
    "sort *",
    "comm *",
    "uniq *",
    "echo *",
    "printf *",
    "grep *",
    "gita ls*",
    "gita status*",
    "find *",
]

# The find carve-outs; each must come AFTER the `find *` allow so last-match
# denies destructive finds.
FIND_DENIES = ["find *-delete*", "find *-exec*", "find *-execdir*"]

HOME_SENTINEL = "/HOME-SENTINEL"


def _strip_jsonc(text: str) -> str:
    """Drop // line comments outside strings, then trailing commas."""
    out = []
    for line in text.splitlines():
        in_str = False
        cut = len(line)
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == "\\" and in_str:
                i += 2
                continue
            if ch == '"':
                in_str = not in_str
            elif not in_str and line.startswith("//", i):
                cut = i
                break
            i += 1
        out.append(line[:cut])
    return re.sub(r",(\s*[}\]])", r"\1", "\n".join(out))


def render(hostname: str, os_name: str, extra: dict | None = None) -> dict:
    data = {"chezmoi": {"hostname": hostname, "os": os_name}}
    if extra:
        data.update(extra)
    result = subprocess.run(
        [
            "chezmoi",
            "-S",
            str(PAYLOAD_ROOT),
            "execute-template",
            "--override-data",
            json.dumps(data),
        ],
        input=TEMPLATE.read_text(),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(_strip_jsonc(result.stdout))


def render_with_home_sentinel(hostname: str, os_name: str) -> dict:
    """Render with .chezmoi.homeDir pointed at a sentinel value.

    The v2 permissions array must carry literal `$HOME/...` globs — v2 expands
    $HOME itself when the config loads (PLAN.md; AGENTS.md rule 1: resolve at
    the consuming tool). A rule that still templates `{{ .chezmoi.homeDir }}`
    renders the sentinel here and is caught; rendered against the real home
    directory it would work on exactly one machine and fail silently on every
    other — the bug this repo's permission history is about.
    """
    return render(
        hostname,
        os_name,
        extra={
            "chezmoi": {
                "hostname": hostname,
                "os": os_name,
                "homeDir": HOME_SENTINEL,
            }
        },
    )


def _permissions(cfg: dict) -> list:
    """The v2 permissions array, asserted present and non-empty first."""
    perms = cfg.get("permissions")
    assert isinstance(perms, list), (
        "dot_config/opencode/opencode.jsonc.tmpl: expected the v2 "
        f"'permissions' array, got {type(perms).__name__} — the v1 "
        "'permission' map has not been migrated to the native v2 form "
        "(dotfiles/docs/research/opencode-v2/PLAN.md)"
    )
    assert perms, (
        "the permissions array is empty — every action would fall through "
        "to v2's built-in base policy instead of this repo's rules"
    )
    return perms


def _rules(cfg: dict, action: str) -> list[dict]:
    """The array's rules for one action, asserted non-empty first."""
    rules = [r for r in _permissions(cfg) if r.get("action") == action]
    assert rules, (
        f"no {action!r} rules in the permissions array — the migration "
        "dropped a whole action group"
    )
    return rules


def _chezmoidata_common() -> dict:
    """The common layer of .chezmoidata/opencode.yaml, loaded directly."""
    data = yaml.safe_load(CHEZMOIDATA.read_text())
    assert isinstance(data, dict) and isinstance(data.get("opencode"), dict), (
        f"{CHEZMOIDATA}: expected an 'opencode:' top-level mapping"
    )
    common = data["opencode"].get("common")
    assert isinstance(common, dict) and common, (
        f"{CHEZMOIDATA}: the 'common' layer is missing or empty"
    )
    return common


@pytest.mark.parametrize(
    "hostname,os_name", [("L37V3P6GQ3", "darwin"), ("unlisted-box", "linux")]
)
def test_renders_deep_agent_on_both_oses(hostname, os_name):
    cfg = render(hostname, os_name)
    deep = cfg["agent"]["deep"]
    assert deep["model"] == "openrouter/anthropic/claude-opus-5"
    assert deep["variant"] == "max"
    variants = cfg["provider"]["openrouter"]["models"]["anthropic/claude-opus-5"][
        "variants"
    ]
    assert variants["max"] == {"reasoning": {"effort": "max"}}
    assert cfg["model"] == "openrouter/z-ai/glm-5.3-flash"


def test_loreai_setup_merges_with_model_overrides():
    cfg = render("L37V3P6GQ3", "darwin")
    assert "@loreai/opencode" in cfg["plugin"]
    assert cfg["compaction"]["auto"] is False
    fragment = json.loads(
        (
            PAYLOAD_ROOT
            / "dotfiles"
            / "apps"
            / "loreai"
            / "files"
            / "opencode"
            / "lore-plugin.jsonc"
        ).read_text()
    )
    assert set(cfg["provider"]) == set(fragment["provider"]), (
        "model overlays must not discard the other captured providers"
    )
    for name, provider in fragment["provider"].items():
        if name != "openrouter":
            assert cfg["provider"][name] == provider
    openrouter = cfg["provider"]["openrouter"]
    assert openrouter["options"]["baseURL"] == "http://127.0.0.1:3207/v1"
    variants = openrouter["models"]["anthropic/claude-opus-5"]["variants"]
    assert variants["max"] == {"reasoning": {"effort": "max"}}


def test_os_then_host_layers_override_common():
    overlay = {
        "opencode": {
            "os": {"linux": {"small_model": "ollama/os-layer"}},
            "hosts": {"box": {"agent": {"deep": {"variant": "xhigh"}}}},
        }
    }
    box = render("box", "linux", overlay)
    assert box["small_model"] == "ollama/os-layer"
    assert box["agent"]["deep"]["variant"] == "xhigh"
    # Deep merge: the host override keeps the sibling keys from common.
    assert box["agent"]["deep"]["model"] == "openrouter/anthropic/claude-opus-5"

    other = render("other", "linux", overlay)
    assert other["agent"]["deep"]["variant"] == "max"

    mac = render("box", "darwin", overlay)
    # The darwin leg has no overlay, so small_model is common's value —
    # whatever chezmoidata currently pins (author ruling 3 moved it to
    # ollama/qwen3.5:9b). What this test pins is the merge mechanic: an
    # untouched layer must inherit common intact.
    assert mac["small_model"] == _chezmoidata_common()["small_model"], (
        "the darwin leg did not inherit common's small_model — the os/hosts "
        "merge must leave layers the overlay does not name intact"
    )


def test_permissions_array_replaces_map():
    """The v1 `permission` map becomes the native v2 `permissions` array.

    v2 still parses v1's map through its maintained legacy layer, but this
    topic ships the documented native contract (author decision; PLAN.md §
    Headline answers 1). `$schema` and `share` are unchanged by the migration
    and pinned here so the rewrite cannot quietly alter them.
    """
    cfg = render("L37V3P6GQ3", "darwin")
    perms = _permissions(cfg)
    assert "permission" not in cfg, (
        "the v1 'permission' map is still emitted alongside 'permissions' — "
        "shipping both invites the legacy layer to disagree with the array"
    )
    actions = {r.get("action") for r in perms}
    assert actions == TARGET_ACTIONS, (
        f"permissions actions are {sorted(actions)}, expected "
        f"{sorted(TARGET_ACTIONS)} — v1's 'list' rule is not a v2 action "
        "and must be dropped, and no expected action group may be missing "
        "(PLAN.md § The exact v1->v2 permission mapping)"
    )
    assert cfg["$schema"] == TARGET_SCHEMA
    assert cfg["share"] == "disabled"


def test_update_replaces_autoupdate():
    """`autoupdate` is a legacy key; v2's native key is `update`."""
    cfg = render("L37V3P6GQ3", "darwin")
    assert cfg.get("update") == "notify", (
        f"rendered 'update' is {cfg.get('update')!r}, expected 'notify' — "
        "v2 renames autoupdate to update (enum disable|notify|auto); 'notify' "
        "is v1 parity and v2's default (PLAN.md open decision 8), and brew "
        "stays the upgrade path so 'auto' stays off"
    )
    assert "autoupdate" not in cfg, (
        "the legacy 'autoupdate' key is still emitted beside 'update'"
    )


def test_shell_catch_all_stays_first():
    """Ruling 1 (2026-10-06): the trailing v1 `"*": "ask"` was a leftover —
    dropped; the shell allow-list is in force after migration.

    v2 takes the LAST matching rule, so the catch-all stays FIRST and must
    appear exactly once: a second, trailing `*` rule shadows every allow
    again — the exact bug this block's 2026-09-16 comment describes.
    """
    cfg = render("L37V3P6GQ3", "darwin")
    shell = _rules(cfg, "shell")
    first = (shell[0].get("resource"), shell[0].get("effect"))
    assert first == ("*", "ask"), (
        f"the first shell rule is {shell[0]!r}; the catch-all ask must come "
        "FIRST so the specific rules after it win by last-match"
    )
    catch_alls = [i for i, r in enumerate(shell) if r.get("resource") == "*"]
    assert catch_alls == [0], (
        f"shell catch-all(s) found at indices {catch_alls}, expected only [0] "
        "— a second (trailing) '*' rule shadows every allow in front of it; "
        "author ruling 1 drops it"
    )


def test_shell_allows_follow_catch_all_and_find_carveouts_come_last():
    """The migrated shell rules keep the 2026-09-16 allow-list in force.

    The plan's allow entries must survive the bash->shell rename, sit AFTER
    the catch-all (last-match), and the destructive-find denies must come
    AFTER the broad `find *` allow or they never fire.
    """
    cfg = render("L37V3P6GQ3", "darwin")
    shell = _rules(cfg, "shell")
    pairs = [(r.get("resource"), r.get("effect")) for r in shell]
    allow_at = {}
    for i, (resource, effect) in enumerate(pairs):
        if effect == "allow":
            allow_at.setdefault(resource, i)
    missing = [res for res in SHELL_ALLOWS if res not in allow_at]
    assert not missing, (
        f"shell allow rule(s) missing from the migrated array: {missing} — "
        "the 2026-09-16 allow-list must survive the bash->shell rename "
        "(PLAN.md § The exact v1->v2 permission mapping)"
    )
    first_allow = min(allow_at.values())
    assert first_allow > 0, (
        f"a shell allow sits at index {first_allow}, ahead of the catch-all "
        "at index 0 — last-match would let the catch-all shadow it"
    )
    find_allow = allow_at["find *"]
    for deny_resource in FIND_DENIES:
        deny_at = next(
            (
                i
                for i, (resource, effect) in enumerate(pairs)
                if resource == deny_resource and effect == "deny"
            ),
            None,
        )
        assert deny_at is not None, (
            f"missing shell deny carve-out {deny_resource!r} — destructive "
            "finds must be denied after the broad 'find *' allow"
        )
        assert deny_at > find_allow, (
            f"{deny_resource!r} sits at index {deny_at}, not after the "
            f"'find *' allow (index {find_allow}) — last-match means the "
            "carve-outs must FOLLOW the broad allow or they never fire"
        )


def test_read_allow_then_env_ask_comes_after():
    """Ruling 2 (2026-10-06): reads stay free except .env files, which ask.

    The global read allow comes first; a later read rule with effect 'ask'
    matching .env files follows it, so last-match makes .env reads ask. The
    .env pattern is asserted loosely (contains 'env') and by position, not
    by hard-coding the exact pattern string — the implement agent mirrors
    whatever v2's base policy actually uses on implementation day (PLAN.md
    author ruling 2).
    """
    cfg = render("L37V3P6GQ3", "darwin")
    read_rules = _rules(cfg, "read")
    allow_at = next(
        (
            i
            for i, r in enumerate(read_rules)
            if r.get("resource") == "*" and r.get("effect") == "allow"
        ),
        None,
    )
    assert allow_at is not None, (
        "no {read, *, allow} rule — without it every read falls through to "
        "v2's base policy instead of staying free (ruling 2 keeps the global "
        "read allow)"
    )
    env_asks = [
        (i, r)
        for i, r in enumerate(read_rules)
        if r.get("effect") == "ask" and "env" in str(r.get("resource", ""))
    ]
    assert env_asks, (
        f"no read rule with effect 'ask' matching .env files among "
        f"{read_rules!r} — ruling 2 keeps v2's .env protection: an ask rule "
        "for .env must follow the global read allow"
    )
    late = [i for i, _ in env_asks if i > allow_at]
    assert late, (
        f"the .env ask rule(s) at {[i for i, _ in env_asks]} precede the "
        f"read allow at index {allow_at} — last-match would let the allow "
        "win and .env files would be read without asking (ruling 2: the ask "
        "comes AFTER the allow)"
    )


def test_external_directory_deny_first_allows_last_literal_home():
    """The external_directory set keeps deny-first/allow-last, with literal
    $HOME globs v2 expands itself.

    The home directory must NOT be templated: a `{{ .chezmoi.homeDir }}` left
    in the array renders to one machine's home and silently never matches
    anywhere else — the exact bug that sat in this file until 2026-09-14.
    The sentinel render makes such a leftover visible.

    The allows are the chezmoi source, ~/code (2026-09-12), the agent temp
    roots (2026-10-27, commit 23909ea: the runtime's scratch and tool-output
    directories sit outside the project), and the two external-skill trees
    (2026-10-16): agent-installed skills are readable even when the runtime's
    own per-skill auto-allow has not fired.
    """
    cfg = render_with_home_sentinel("L37V3P6GQ3", "darwin")
    perms = _permissions(cfg)
    for rule in perms:
        resource = str(rule.get("resource", ""))
        assert HOME_SENTINEL not in resource, (
            f"permission resource {resource!r} still templates "
            ".chezmoi.homeDir — the v2 array carries literal '$HOME/...' "
            "globs because v2 expands $HOME itself (AGENTS.md rule 1)"
        )
        assert "{" not in resource, (
            f"permission resource {resource!r} contains '{{' — template "
            "residue inside the permissions array"
        )
    ext = _rules(cfg, "external_directory")
    assert len(ext) == 6, (
        f"expected exactly the external_directory set (deny + five allows), "
        f"got {len(ext)}: {ext!r}"
    )
    first = (ext[0].get("resource"), ext[0].get("effect"))
    assert first == ("*", "deny"), (
        f"the first external_directory rule is {ext[0]!r}; the deny comes "
        "FIRST and the specific allows LAST (last-match; the original "
        "allows-then-deny order was caught live on 2026-09-12)"
    )
    assert all(r.get("effect") == "allow" for r in ext[1:]), (
        f"the external_directory rules after the deny are {ext[1:]!r}; all "
        "must be allows"
    )
    allow_resources = [str(r.get("resource", "")) for r in ext[1:]]
    for want in (
        "$HOME/.local/share/chezmoi",
        "$HOME/code",
        "$HOME/.agents/skills",
        "$HOME/.claude/skills",
    ):
        assert any(res.startswith(want) for res in allow_resources), (
            f"no external_directory allow starting with {want!r} among "
            f"{allow_resources!r} — the v2 boundary form is a literal $HOME "
            "glob (PLAN.md mapping notes: '/*' and v1's '/**' are equivalent)"
        )


def test_permissions_identical_across_os_legs():
    """The permissions array is literal in the template and identical on
    every OS — the data merge must never touch it.
    """
    darwin = _permissions(render("L37V3P6GQ3", "darwin"))
    linux = _permissions(render("unlisted-box", "linux"))
    assert darwin == linux, (
        "the permissions array differs between the darwin and linux legs — "
        "the rules are order-sensitive and literal in the template; an "
        "os-specific array would make one OS's policy silently different "
        "(the external_directory trio included)"
    )


def test_chezmoidata_pins_qwen35_for_trivial_roles():
    """Ruling 3 (2026-10-06): titles, summaries and compaction stay local.

    small_model moves to ollama/qwen3.5:9b and agents.summary.model /
    agents.compaction.model are pinned at the same tag, so trivial calls
    never leave the box. Loaded directly from .chezmoidata/opencode.yaml —
    the data file is the source, the template just renders it.
    """
    common = _chezmoidata_common()
    assert common.get("small_model") == SMALL_MODEL, (
        f"chezmoidata small_model is {common.get('small_model')!r}, expected "
        f"{SMALL_MODEL!r} (author ruling 3, 2026-10-06)"
    )
    agents = common.get("agents")
    assert isinstance(agents, dict) and agents, (
        f"chezmoidata common has no 'agents' block — agents.summary.model "
        f"and agents.compaction.model must be pinned at {SMALL_MODEL!r} "
        "(ruling 3)"
    )
    for role in ("summary", "compaction"):
        model = (agents.get(role) or {}).get("model")
        assert model == SMALL_MODEL, (
            f"chezmoidata agents.{role}.model is {model!r}, expected "
            f"{SMALL_MODEL!r} (author ruling 3: titles, summaries and "
            "compaction all stay local)"
        )


def test_ruling3_small_model_and_trivial_agents_render():
    """The ruling-3 chezmoidata values survive the merge and render."""
    cfg = render("L37V3P6GQ3", "darwin")
    assert cfg.get("small_model") == SMALL_MODEL, (
        f"rendered small_model is {cfg.get('small_model')!r}, expected "
        f"{SMALL_MODEL!r} — the chezmoidata pin did not survive the merge"
    )
    agents = cfg.get("agents")
    assert isinstance(agents, dict) and agents, (
        "the chezmoidata 'agents' block did not render into the config"
    )
    for role in ("summary", "compaction"):
        model = (agents.get(role) or {}).get("model")
        assert model == SMALL_MODEL, (
            f"rendered agents.{role}.model is {model!r}, expected {SMALL_MODEL!r}"
        )
