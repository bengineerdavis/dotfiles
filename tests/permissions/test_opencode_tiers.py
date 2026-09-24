"""The committed opencode.jsonc bash tiers must mean what they say.

Same limit as test_permission_tiers.py, stated first: this models opencode's
matcher — rules in file order, LAST match wins, `*` matches any run of
characters — rather than running opencode. The model was checked against
opencode's own log (`message=evaluated ... action.pattern=...`), which names
the rule that decided each real command; a divergence would make this pass
while reality differs.

It reads only this repo's file. At runtime the global config is merged
underneath, but every project block starts with `"*": "ask"`, so nothing
global can decide a command this file covers.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
CONFIG = REPO / "opencode.jsonc"


def _strip_jsonc(text: str) -> str:
    """Drop // comments outside strings and trailing commas."""
    out, i, in_str = [], 0, False
    while i < len(text):
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\":
                out.append(text[i + 1])
                i += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
            out.append(c)
        elif text.startswith("//", i):
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        else:
            out.append(c)
        i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


@pytest.fixture(scope="module")
def config() -> dict:
    return json.loads(_strip_jsonc(CONFIG.read_text(encoding="utf-8")))


def _tier(rules: dict, cmd: str) -> str:
    decided = "unmatched"
    for pattern, action in rules.items():  # dicts keep file order
        if re.fullmatch(re.escape(pattern).replace(r"\*", ".*"), cmd, re.S):
            decided = action
    return decided


def _blocks(config: dict) -> dict[str, dict]:
    return {
        "top-level": config["permission"]["bash"],
        "autonomous": config["agent"]["autonomous"]["permission"]["bash"],
    }


# (command, required tier in BOTH blocks, why)
BOTH = [
    ("git worktree add .worktrees/x -b x", "allow", "creating a worktree is additive and undoable"),
    ("git worktree list --porcelain", "allow", "read-only"),
    ("git worktree remove .worktrees/x", "ask", "deletion asks"),
    ("git worktree prune", "ask", "prunes admin state"),
    ("git worktree move a b", "ask", "relocates a checkout"),
    ("git push --force-with-lease=main:abc123 origin main", "deny",
     "the = form slipped past `--force-with-lease *` on 2026-09-24"),
    ("git push --force-with-lease origin main", "deny", "spec.md § Change records"),
    ("git push --force origin main", "deny", "spec.md § Change records"),
    ("chezmoi apply ~/dotfiles", "deny", "AGENTS.md § Applying is main-only"),
]

# (command, required tier in the TOP-LEVEL block, why). The autonomous agent
# allows all of gh by design and is not narrowed here.
TOP = [
    ("gh pr view 5 --json state", "allow", "read-only"),
    ("gh pr create --fill", "ask", "writes to GitHub"),
    ("gh pr merge 5", "ask", "writes to GitHub"),
    ("gh issue create --title x", "ask", "writes to GitHub"),
    ("gh repo clone x/y", "ask", "writes to disk"),
    ("gh run rerun 123", "ask", "triggers CI"),
    ("gh release download v1", "ask", "writes to disk"),
    ("gh workflow run ci.yml", "ask", "triggers CI"),
    ("gh api repos/o/r/issues -X POST", "ask", "explicit method"),
    ("gh api -XPOST repos/o/r/issues", "ask", "method glued to the flag"),
    ("gh api repos/o/r --method PATCH", "ask", "explicit method"),
    ("gh api repos/o/r/issues -f title=x", "ask", "a field makes gh POST"),
    ("gh api -F title=x repos/o/r/issues", "ask", "a typed field makes gh POST"),
    ("gh api repos/o/r/issues --raw-field title=x", "ask", "a field makes gh POST"),
    ("gh api repos/o/r/issues --input body.json", "ask", "a body makes gh POST"),
    ("gh api graphql -f query=x", "ask", "graphql can mutate"),
    ("gh auth status --show-token", "ask", "prints a credential"),
    ("gh auth token", "ask", "prints a credential"),
]


@pytest.mark.parametrize("block", ["top-level", "autonomous"])
@pytest.mark.parametrize("cmd,want,why", BOTH, ids=[c[0][:40] for c in BOTH])
def test_both_blocks(config, block, cmd, want, why):
    got = _tier(_blocks(config)[block], cmd)
    assert got == want, f"[{block}] {cmd!r} -> {got}, expected {want} — {why}"


@pytest.mark.parametrize("cmd,want,why", TOP, ids=[c[0][:40] for c in TOP])
def test_top_level_block(config, cmd, want, why):
    got = _tier(_blocks(config)["top-level"], cmd)
    assert got == want, f"{cmd!r} -> {got}, expected {want} — {why}"


def test_every_block_starts_with_a_catch_all_ask(config):
    """The file-order model above only holds if nothing global can decide a
    command: a leading `"*": "ask"` is what guarantees that."""
    for name, rules in _blocks(config).items():
        first = next(iter(rules.items()))
        assert first == ("*", "ask"), f"{name} starts with {first}"
