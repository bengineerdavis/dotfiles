"""
Invariants on the layers this repo actually ships.

The resolver above is generic; these assert the real files still hold the design
property they were written for. The important one is restrictions-only: if a
`may_*: true` ever lands in a versioned layer, permission becomes expressible in
a file, and a typo or a careless merge can grant it. That is exactly what the
schema was shaped to prevent, so it is worth a test rather than a comment.
"""

from __future__ import annotations

import os
import pathlib

import pytest

yaml = pytest.importorskip("yaml")

REPO = pathlib.Path(__file__).resolve().parents[2]
VERSIONED = {
    "ethics": REPO / "dotfiles" / "policy" / "ethics.yaml",
    "personal": REPO / "dotfiles" / "policy" / "personal.yaml",
}
# Machine-local and never committed, so it is absent on a fresh clone and in CI.
COMPANY = (
    pathlib.Path(os.environ.get("XDG_STATE_HOME", pathlib.Path.home() / ".local/state"))
    / "ai-policy"
    / "company.yaml"
)

GRANT_PREFIXES = ("may_", "can_", "allow_")


def _grants(node, path=""):
    """Every boolean field named like a permission and set true."""
    found = []
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}".lstrip(".")
            if isinstance(value, bool) and value and key.startswith(GRANT_PREFIXES):
                found.append(here)
            found += _grants(value, here)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            found += _grants(value, f"{path}[{i}]")
    return found


@pytest.mark.parametrize("name", sorted(VERSIONED))
def test_versioned_layer_parses(name):
    assert isinstance(yaml.safe_load(VERSIONED[name].read_text()), dict)


@pytest.mark.parametrize("name", sorted(VERSIONED))
def test_versioned_layer_grants_nothing(name):
    doc = yaml.safe_load(VERSIONED[name].read_text())
    assert _grants(doc) == [], (
        f"{name} contains permission-granting field(s). The layers are "
        "restrictions-only: a field may forbid or bound, never authorise. "
        "See dotfiles/docs/GOALS.md."
    )


def test_company_layer_grants_nothing_when_present():
    if not COMPANY.exists():
        pytest.skip("machine-local company layer not present on this machine")
    doc = yaml.safe_load(COMPANY.read_text())
    assert _grants(doc) == []


def test_precedence_is_a_total_order():
    """ethics < company < personal, with no ties — otherwise 'first to speak
    wins' has no defined answer when two layers both hold a key."""
    seen = {}
    for name, path in VERSIONED.items():
        meta = (yaml.safe_load(path.read_text()) or {}).get("meta", {})
        seen[name] = meta.get("precedence")
    assert seen["ethics"] == 1
    assert seen["personal"] == 3
    assert seen["ethics"] < seen["personal"]


def test_ethics_declares_itself_unrelaxable():
    meta = (yaml.safe_load(VERSIONED["ethics"].read_text()) or {}).get("meta", {})
    assert meta.get("relaxable_by_lower_layers") is False
