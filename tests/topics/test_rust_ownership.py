"""The Rust channel has exactly one owner, and it is `apps/mise`.

Author ruling 2026-11-04: rustup owns the Rust toolchain; mise syncs to it.
The measurement behind it is that mise's `rust` entry is not a version pin — its
`core:rust` backend downloads `rustup-init` and runs it, then symlinks
`installs/rust/<version>` at `~/.cargo/bin` instead of copying a toolchain.
So mise already installs rustup, and the only gap was that no topic *declared*
it.

These tests hold that conclusion in place. They fail if someone:

- adds a second topic that installs rustup (the duplicate-channel hazard the
  roborev incident in AGENTS.md records), or
- drops rust/rustup/cargo from mise's `topic_provides`, which would silently
  break every `topic_requires: [cargo]` a consumer declares.

The keepalive case is the one that matters most: a provides list is easy to
"tidy up" back to its old value, and nothing else in the suite would notice.
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
APPS = REPO / "home" / "dotfiles" / "apps"


def topic_meta(topic: str) -> dict:
    return yaml.safe_load((APPS / topic / "topic.yml").read_text())


def test_mise_advertises_the_rust_channel():
    provides = topic_meta("mise")["topic_provides"]
    assert {"rust", "rustup", "cargo"} <= set(provides), (
        f"apps/mise must advertise rust/rustup/cargo, got {provides}. "
        "mise's core:rust backend installs rustup, so a consumer's "
        "topic_requires: [cargo] resolves here or nowhere."
    )


def test_no_second_topic_installs_rustup():
    """One channel, one installer. A rust topic that installs rustup duplicates it.

    Matched against the installer as it is actually written, not one spelling:
    the canonical one-liner is `curl https://sh.rustup.rs | sh`, and
    `rustup-init` is the binary it downloads. A check for `rustup-init` alone
    passed a topic using the curl form (measured 2026-11-04 — the mutation
    survived), so both are matched here.
    """
    installer_markers = ("rustup-init", "sh.rustup.rs", "rustup.rs")
    offenders = []
    for topic_dir in sorted(p for p in APPS.iterdir() if p.is_dir()):
        if topic_dir.name == "mise":
            continue
        tasks_dir = topic_dir / "tasks"
        if not topic_dir.is_dir():
            continue
        for task_file in sorted(topic_dir.rglob("*.yaml")):
            text = task_file.read_text()
            hits = [marker for marker in installer_markers if marker in text]
            if hits:
                offenders.append(f"{task_file.relative_to(REPO)} ({', '.join(hits)})")
    assert not offenders, (
        "apps/mise already installs rustup through its core:rust backend. "
        f"These tasks install it again: {offenders}. See "
        "docs/TOPIC-RECIPES.md — rust is a mise entry, not a toolchain topic."
    )


def test_no_other_topic_claims_the_rust_channel():
    """Two topics advertising cargo would make topic_requires ambiguous.

    `provides_map` is `{provided_name: topic_name}`, so a second claim silently
    overwrites the first and the resolver stops pointing at the topic that
    actually installs it.
    """
    claimed = {}
    for topic_dir in sorted(p for p in APPS.iterdir() if p.is_dir()):
        meta_file = topic_dir / "topic.yml"
        if not meta_file.is_file():
            continue
        provides = yaml.safe_load(meta_file.read_text()).get("topic_provides") or []
        for token in ("rust", "rustup", "cargo"):
            if token in provides:
                claimed.setdefault(token, []).append(topic_dir.name)
    duplicated = {token: owners for token, owners in claimed.items() if len(owners) > 1}
    assert not duplicated, (
        f"rust channel claimed by more than one topic: {duplicated}. "
        "apps/mise owns it; a second claimant is the duplicate-channel hazard."
    )


def test_mise_rust_entry_stays_declared():
    """The entry the ownership rests on. Removing it breaks every cargo: backend."""
    config = (APPS / "mise" / "files" / "config.toml").read_text()
    declared = [
        line.split("=")[0].strip().strip('"')
        for line in config.splitlines()
        if "=" in line and not line.lstrip().startswith("#")
    ]
    assert "rust" in declared, (
        "apps/mise/files/config.toml no longer declares `rust`. That entry is "
        "what installs rustup — the cargo: backends (lychee, broot, eza, "
        "fd-find, ripgrep) cannot build without it."
    )
