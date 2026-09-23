"""The committed permission config must mean what docs/PERMISSIONS.md says.

WHAT THIS TEST CANNOT DO, stated first so nobody trusts it further than it
deserves: it uses its own model of Claude Code's pattern matcher, not Claude
Code's. If the two disagree, this passes while reality differs. Permission
changes could not be verified from inside a session (a deny rule added for a
harmless command did not block it, and the cause was not distinguishable), so
real enforcement is confirmed by a human in a fresh session.

WHAT IT DOES DO, which is the part worth having: it catches intent regressions.
Someone adding `Bash(git *)` to allow would shadow every ask and deny rule at a
stroke, and the config would still look carefully tiered. That is exactly the
accretion that produced 177 rules with nothing denied, and it is silent.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SETTINGS = REPO / ".claude" / "settings.json"
DOC = REPO / "docs" / "PERMISSIONS.md"


@pytest.fixture(scope="module")
def perms() -> dict:
    d = json.loads(SETTINGS.read_text(encoding="utf-8"))
    p = d.get("permissions", {})
    assert p, "no permissions block — the checks below would be vacuous"
    return p


def _matches(rule: str, cmd: str) -> bool:
    m = re.match(r"Bash\((.*)\)$", rule, re.S)
    if not m:
        return False
    return re.fullmatch(re.escape(m.group(1)).replace(r"\*", ".*"), cmd) is not None


def _tier(perms: dict, cmd: str) -> str:
    for tier in ("deny", "ask", "allow"):        # deny > ask > allow
        if any(_matches(r, cmd) for r in perms.get(tier, [])):
            return tier
    return "prompt"


# (command, required tier, why it matters)
CASES = [
    ("chezmoi apply", "deny", "AGENTS.md § Applying is main-only"),
    ("chezmoi apply --dry-run", "deny", "same, with any argument"),
    ("git push --force origin main", "deny", "spec.md § Change records"),
    ("git push -f origin main", "deny", "short form of the same thing"),
    ("git filter-repo --path x", "ask", "history rewriting — irreversible but legitimate, per docs/PERMISSIONS.md"),
    ("git push origin main", "ask", "publishing is outward-facing"),
    ("git -C /tmp/x push --force", "ask", "the -C form must not bypass the tiers"),
    ("gh pr create", "ask", "writes to GitHub"),
    ("rm -rf /tmp/x", "ask", "destructive"),
    ("curl -s https://example.com", "ask", "network egress"),
    ("brew install cowsay", "ask", "mutates the machine"),
    ("./run-role.sh chrome", "ask", "applies system state"),
    ("op read op://x/y", "ask", "secret access"),
    ("git status --porcelain", "allow", "read-only"),
    ("git add TASKS.md", "allow", "local and undoable"),
    ("git commit -m x", "allow", "local and undoable"),
    ("uv run --with pytest pytest tests -q", "allow", "the documented test command"),
    ("chezmoi status", "allow", "read-only"),
    ("chezmoi add ~/dotfiles/zsh/aliases.zsh", "allow", "captures into git-tracked source"),
    ("cat README.md", "allow", "read-only"),
    ("python3 -", "allow", "interpreters allowed deliberately"),
]


@pytest.mark.parametrize("cmd,want,why", CASES, ids=[c[0][:38] for c in CASES])
def test_command_lands_in_the_intended_tier(perms, cmd, want, why):
    got = _tier(perms, cmd)
    assert got == want, f"{cmd!r} resolved to {got}, expected {want} — {why}"


def test_every_tier_is_populated(perms):
    """The config this replaced had 88 allow rules and nothing else. An empty
    deny or ask is the state that made a permission file decorative."""
    for tier in ("allow", "ask", "deny"):
        assert perms.get(tier), f"{tier} is empty"


def test_no_allow_rule_shadows_a_whole_command(perms):
    """A bare `Bash(git *)` or `Bash(chezmoi *)` in allow would swallow every
    ask and deny rule for that command while looking like one harmless line."""
    shadowing = [
        r for r in perms.get("allow", [])
        if re.fullmatch(r"Bash\((git|chezmoi|gh|rm|curl|brew|pip|npm|op|sudo) ?\*?\)", r)
    ]
    assert not shadowing, f"allow rules shadow a whole command: {shadowing}"


def test_the_doc_and_the_config_ship_together(perms):
    """settings.json is JSON and cannot hold its own reasoning, so the doc is
    the only place the reasoning lives. A config with no doc is unreviewable."""
    assert DOC.exists(), "docs/PERMISSIONS.md is missing"
    text = DOC.read_text(encoding="utf-8")
    assert "does not contain a misaligned agent" in text, (
        "the doc must state the threat model — the config's whole justification "
        "rests on what it does NOT claim to do"
    )
