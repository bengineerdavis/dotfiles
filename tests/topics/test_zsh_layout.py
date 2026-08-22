"""
Guard the one zsh layout that actually loads.

`.zshrc` sources exactly this glob:

    config_files=($ZSH/apps/*/files/zsh/*.zsh(N) $ZSH/zsh/*.zsh(N))

So a fragment is live only at `apps/<topic>/files/zsh/*.zsh`. Two older
layouts — flat `apps/<topic>/*.zsh` and `apps/<topic>/zsh/*.zsh` — are never
sourced. They date from when the glob was `$ZSH/**/*.zsh`, which matched all
three and sourced every fragment 2-3x (zoxide's init ran twice and warned;
PATH fragments stacked). Narrowing the glob fixed the double-sourcing but left
52 dead files behind, since removed.

Dead copies are worse than clutter: they read like configuration. Editing one
has no effect, and the silence looks like the edit was wrong rather than the
file. That is not hypothetical — 1857605 wrote the PyMuPDF fix to both
`apps/mise/env.zsh` and `apps/mise/files/zsh/env.zsh`, and only the second one
ever ran. A `trash-cli` copy also sat stale for months still aliasing `tr`,
shadowing the coreutils binary, long after the live copy renamed it `trr`.

`template_dir/` already scaffolds only `files/zsh/`, so nothing regenerates
these. They can only return by hand, which is what this test catches.

Run:
    pytest tests/topics -v
"""

from __future__ import annotations

import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
APPS = REPO / "dotfiles" / "apps"
TEMPLATE = REPO / "dotfiles" / "template_dir"

CANONICAL = "apps/<topic>/files/zsh/*.zsh"


def _dead_fragments() -> list[pathlib.Path]:
    """Every .zsh under a topic that the .zshrc glob cannot reach."""
    dead = []
    for topic in sorted(p for p in APPS.iterdir() if p.is_dir()):
        # Legacy flat: apps/<topic>/*.zsh
        dead += sorted(topic.glob("*.zsh"))
        # Legacy subdir: apps/<topic>/zsh/*.zsh  (note: NOT files/zsh)
        dead += sorted((topic / "zsh").glob("*.zsh"))
    return dead


def test_no_unsourced_zsh_fragments():
    dead = _dead_fragments()
    assert not dead, (
        f"{len(dead)} zsh fragment(s) sit outside {CANONICAL} and are never "
        "sourced. Move the content into the topic's files/zsh/ and delete the "
        "copy:\n  " + "\n  ".join(str(p.relative_to(REPO)) for p in dead)
    )


def test_no_legacy_zsh_subdirectory_at_all():
    """
    The `apps/<topic>/zsh/` layout is dead in its entirety, whatever it holds.

    Guarding only `*.zsh` was not enough. A concurrent rebase reinstated
    `homebrew/zsh/executable_install.sh` and a `.gitkeep` propping open
    `tmux/zsh/`, and the *.zsh-scoped test above passed with both present —
    a dead directory quietly refilled while the suite stayed green.

    So assert on the directory, not the extension: nothing under a topic's
    `zsh/` is reachable, so the directory should not exist.
    """
    legacy = sorted(d for d in APPS.glob("*/zsh") if d.is_dir())
    assert not legacy, (
        "legacy zsh/ directories exist; nothing inside them is reachable "
        f"(canonical is {CANONICAL}):\n  "
        + "\n  ".join(
            f"{d.relative_to(REPO)}  ({len(list(d.iterdir()))} entries)"
            for d in legacy
        )
    )


def test_scaffold_only_emits_the_canonical_layout():
    """If the generator drifts, every new topic reintroduces the bug."""
    if not TEMPLATE.is_dir():
        return  # scaffold is optional; nothing to guard
    stray = sorted(TEMPLATE.glob("*.zsh")) + sorted((TEMPLATE / "zsh").glob("*.zsh"))
    assert not stray, (
        "template_dir scaffolds zsh fragments outside files/zsh/, so every "
        "topic generated from it starts with dead copies:\n  "
        + "\n  ".join(str(p.relative_to(REPO)) for p in stray)
    )


def test_canonical_fragments_still_exist():
    """
    Guards the failure mode where the two tests above pass because someone
    deleted the live fragments instead of the dead ones.
    """
    live = sorted(APPS.glob("*/files/zsh/*.zsh"))
    assert len(live) > 20, (
        f"only {len(live)} canonical fragments found under {CANONICAL} — "
        "expected the topics' live zsh config. Deleting live fragments would "
        "also satisfy the dead-fragment tests, so this is the counterweight."
    )
