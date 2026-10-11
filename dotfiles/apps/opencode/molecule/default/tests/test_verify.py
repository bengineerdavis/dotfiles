"""Verify the apps/opencode v2 migration end state on the box.

Molecule's testinfra verifier runs every test_*.py under this directory
over the ansible connection. The plan's verify.yml section named a YAML
file — layout corrected at implementation: a verify.yml playbook belongs
to the ansible verifier, which this scenario does not use.

Each test names the property it proves; the migration is confirmed only
when all of them pass against a box that prepare.yml really installed v1
on first, so the v1-absent checks are not vacuous. Framing and caveats:
../README.md.

Brew-on-box PATH caveat (PLAN.md): these commands run over non-login
ssh, so brew is not on PATH — every brew-owned binary is called through
linuxbrew's documented fixed prefix, whose value prepare.yml owns. A
missing install there fails loudly here instead of passing silently.
"""

import json
import os
import re

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")

BREW_BIN = "/home/linuxbrew/.linuxbrew/bin"
TAP = "anomalyco/tap"
V2 = f"{TAP}/opencode-v2"
V1 = f"{TAP}/opencode"
# The skills the approved sources ship as of the harness landing. The
# sources are wildcard-declared, so upstream can add more without
# touching this list; a rename here is a re-grade of the recorded
# expectation, not a test bug.
EXPECTED_SKILLS = (
    "commit-hygiene",
    "interaction-questioning",
    "naming",
    "review-best-practices",
    "skillet-authoring",
)


def home(host) -> str:
    """The connection user's HOME, resolved on the box."""
    out = host.run('printf %s "$HOME"')
    assert out.rc == 0
    assert out.stdout.strip(), "empty $HOME — the ssh session env is broken"
    return out.stdout.strip()


def test_v2_formula_installed(host):
    """The tap's v2 formula is installed, and reports a 2.x build."""
    cmd = host.run(f"{BREW_BIN}/brew list --versions {V2}")
    assert cmd.rc == 0, f"v2 formula not installed: {cmd.stderr}"
    assert cmd.stdout.strip(), "brew printed nothing — cannot read a version"
    version = cmd.stdout.strip().split()[-1]
    assert re.match(r"^2\.", version), f"expected 2.x, got {version!r}"


def test_v1_formula_absent(host):
    """v1 is gone: brew exits non-zero for the removed formula."""
    cmd = host.run(f"{BREW_BIN}/brew list --formula {V1}")
    assert cmd.rc != 0, f"v1 formula still installed: {cmd.stdout!r}"


def test_opencode_resolves_to_v2(host):
    """The brew prefix's opencode is the binary, and reports 2.x."""
    cmd = host.run(f"{BREW_BIN}/opencode --version")
    assert cmd.rc == 0, cmd.stderr
    assert cmd.stdout.strip(), "opencode printed nothing"
    assert re.search(r"\b2\.\d", cmd.stdout), f"expected 2.x, got {cmd.stdout!r}"


def test_migrated_config_loads(host):
    """The migrated config loads clean, with ordered permissions."""
    cmd = host.run(f"{BREW_BIN}/opencode debug config")
    assert cmd.rc == 0, f"rc={cmd.rc} stdout={cmd.stdout!r} stderr={cmd.stderr!r}"
    # v2's normalizer reports dropped/renamed keys on stderr as
    # unsupported*/diagnostic lines; the migrated config must be clean.
    lowered = cmd.stderr.lower()
    assert "unsupported" not in lowered, cmd.stderr
    assert "diagnostic" not in lowered, cmd.stderr

    cfg = json.loads(cmd.stdout)
    perms = cfg.get("permissions")
    assert isinstance(perms, list) and perms, "permissions array missing/empty"

    # Catch-all first: v2's permissions are ordered, LAST match wins, so
    # the shell catch-all must open the array or every specific rule
    # below it is shadowed (the bug the v1 array shipped with,
    # 2026-10-06).
    catchall = {"action": "shell", "resource": "*", "effect": "ask"}
    assert perms[0] == catchall, perms[0]

    def index_of(rule):
        return perms.index(rule) if rule in perms else -1

    # `find *` allow must precede the destructive find carve-outs, or
    # last-match-wins makes the deny rules dead letters.
    find_rule = {"action": "shell", "resource": "find *", "effect": "allow"}
    find_allow = index_of(find_rule)
    assert find_allow > 0, "find * allow missing from the array"
    for suffix in ("-delete*", "-exec*", "-execdir*"):
        deny = index_of(
            {"action": "shell", "resource": f"find {suffix}", "effect": "deny"}
        )
        assert deny > find_allow, (
            f"find {suffix} deny not after find * (allow at {find_allow})"
        )

    # Reads are free except .env files, which ask, with the example
    # pattern readable again — same last-match-wins ordering.
    read_allow = index_of({"action": "read", "resource": "*", "effect": "allow"})
    assert read_allow > 0, "read * allow missing from the array"
    env_ask = index_of({"action": "read", "resource": "*.env", "effect": "ask"})
    assert env_ask > read_allow, ".env ask not after the read allow"
    example = index_of(
        {"action": "read", "resource": "*.env.example", "effect": "allow"}
    )
    assert example > env_ask, ".env.example allow not after the .env ask"


def test_skills_synced(host):
    """The dotagents sync installed the skill set user-global."""
    agents = host.file(f"{home(host)}/.agents/agents.toml")
    assert agents.exists, "~/.agents/agents.toml missing — sync never ran"
    content = agents.content_string
    assert content.strip(), "agents.toml empty — cannot read sources"
    assert "bengineerdavis/ai-prompt-library" in content
    assert "getsentry/skillet" in content

    for skill in EXPECTED_SKILLS:
        entry = host.file(f"{home(host)}/.agents/skills/{skill}")
        assert entry.is_directory, f"skill {skill} missing from ~/.agents/skills"


def test_tap_trust_present(host):
    """Tap trusted; the v1 formula's trust residue cleaned."""
    xdg = host.run('printf %s "${XDG_CONFIG_HOME:-}"')
    assert xdg.rc == 0
    if xdg.stdout.strip():
        trust_path = f"{xdg.stdout.strip()}/homebrew/trust.json"
    else:
        trust_path = f"{home(host)}/.homebrew/trust.json"

    trust = host.file(trust_path)
    assert trust.exists, f"{trust_path} missing — the tap was never trusted"
    content = trust.content_string
    assert content.strip(), "trust.json empty — cannot read entries"
    assert TAP in content, f"{TAP} not named in {trust_path}: {content!r}"

    # v1's formula trust entry — written by brew install (measured
    # 2026-09-14) and cleaned by converge's untrust — must be gone. The
    # exact-quoted form cannot false-positive on the v2 entry:
    # "anomalyco/tap/opencode-v2" does not contain
    # "anomalyco/tap/opencode" followed by a quote.
    assert f'"{V1}"' not in content, f"v1 trust residue present: {content!r}"
