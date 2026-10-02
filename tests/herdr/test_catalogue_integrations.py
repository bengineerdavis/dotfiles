"""Catalogue + integration-loop tests for the herdr topic — swarm dimension 2 of 4.

Deduced from written artifacts only; no implementation existed when this file
was written. These tests are the executable form of the contract, and the
implementation must match them:

- ``dotfiles/apps/herdr/README.md`` — the design record: wired set (opencode,
  claude, cursor; codex a listed candidate, not wired), skip-and-report
  integration loop, raise-when-herdr-missing, gated intersection removal,
  opencode native-restore floor (herdr integration v5+)
- ``dotfiles/docs/TOPIC-RECIPES.md`` — shared-catalogue recipe (schema shape,
  explicit ignored list, thin install-and-report loop, gated teardown that
  uninstalls only the claimed∩installed intersection) and the skip-vs-raise
  recipe (absent agent skips and stays green; missing required dependency
  raises naming the fix)
- ``dotfiles/config/editors.yaml`` — the catalogue pattern the schema asserts
  mirror: ``version``, a domain-named entry list plus an ignored list, dated
  verdicts as recorded evidence
- ``https://herdr.dev/docs/integrations/`` (docs 0.9.1, checked 2026-09-19) —
  frozen below: integration ids as herdr's CLI spells them, lifecycle vs
  session-identity types, per-integration native-restore minimum versions,
  config-dir-must-exist rule and its default directories
- ``spec.md`` § Verification — guards proven to relent in both directions,
  properties that state the rule independently, failing-first with named
  messages, never skip-quietly

Run::

    uv run --with pytest --with pyyaml --with hypothesis pytest \
        tests/herdr/test_catalogue_integrations.py -q

While ``dotfiles/config/agents.yaml`` does not exist, EVERY test in this file
fails with a message naming that path. Never skips, never collection errors.

Deduced schema spellings (flagged as ambiguities in the swarm report — the
catalogue keys mirror editors.yaml's ``editor_extensions`` /
``editor_extensions_ignored``; entry fields are ``id``, ``why``, ``probe``,
``config_dir``, ``kind``, ``min_version`` as a dated verdict
``{version, checked}``; the optional scope field is ``topics``, listing
subscriber topic names, absent = shared by default — the editors.yaml
``editors:`` pattern).
"""

from __future__ import annotations

import datetime
import re
import string
from pathlib import Path

import pytest
import yaml

# importorskip, NOT a try/except: @given is evaluated at import time, so a
# skipif marker would never fire and the module would raise NameError during
# collection instead of skipping. Under the documented run command hypothesis
# is always installed, so the artifact gate below is what fires.
pytest.importorskip("hypothesis", reason="hypothesis not installed")

from hypothesis import given, settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

# ── Frozen upstream facts ────────────────────────────────────────────────────
# https://herdr.dev/docs/integrations/ — docs version 0.9.1, checked
# 2026-09-19 (same date recorded in apps/herdr/README.md § Upstream references).
# Integration ids are spelled exactly as herdr's own install commands spell
# them (`herdr integration install <id>`).

HC_UPSTREAM_IDS = frozenset(
    {
        "pi",
        "omp",
        "claude",
        "codex",
        "copilot",
        "devin",
        "droid",
        "kimi",
        "opencode",
        "kilo",
        "hermes",
        "qodercli",
        "qwen",
        "letta",
        "cursor",
        "mastracode",
        "antigravity-cli",
        "grok",
    }
)

# Native session restore requires current herdr integrations (upstream table):
# OpenCode version 5, Claude Code version 6, Cursor Agent CLI version 1.
HC_WIRED_IDS = ("opencode", "claude", "cursor")
HC_WIRED_FACTS = {
    "opencode": {
        "probe": "opencode",
        "config_dir": "~/.config/opencode",
        "kind": "lifecycle",
        "floor": 5,
    },
    "claude": {
        "probe": "claude",
        "config_dir": "~/.claude",
        "kind": "session",
        "floor": 6,
    },
    "cursor": {
        # README names the cursor-agent probe explicitly; `cursor` never
        # resolves, and the entry would then skip forever while looking right.
        "probe": "cursor-agent",
        "config_dir": "~/.cursor",
        "kind": "session",
        "floor": 1,
    },
}

# Fake-state stand-ins for machine-held integrations the catalogue does not
# claim (upstream facts: codex uses ~/.codex, grok uses ~/.grok, pi uses
# ~/.pi/agent). Used to prove teardown and the loop leave them alone.
HC_UNCLAIMED_FACTS = {
    "codex": {"probe": "codex", "config_dir": "~/.codex"},
    "grok": {"probe": "grok", "config_dir": "~/.grok"},
}

HC_REPO = Path(__file__).resolve().parents[2]
HC_CATALOGUE = HC_REPO / "dotfiles" / "config" / "agents.yaml"

# The subscriber that consumes the catalogue today (interim role-relative
# direct read; TOPIC-RECIPES.md shared-catalogue recipe).
HC_SUBSCRIBER = "herdr"


# ── Artifact gate and catalogue loaders ─────────────────────────────────────


def hc_require_catalogue():
    """Fail NAMED while dotfiles/config/agents.yaml is absent. Never skip."""
    if not HC_CATALOGUE.is_file():
        pytest.fail(
            "missing artifact: dotfiles/config/agents.yaml — the herdr "
            "integration catalogue does not exist yet (expected at "
            f"{HC_CATALOGUE}). This suite is failing-first: the catalogue + "
            "integration-loop contract cannot be checked without the file. "
            "Sources: dotfiles/apps/herdr/README.md; dotfiles/docs/"
            "TOPIC-RECIPES.md (shared-catalogue recipe)."
        )
    try:
        with HC_CATALOGUE.open(encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        pytest.fail(f"dotfiles/config/agents.yaml does not parse as YAML: {exc}")
    if not isinstance(doc, dict):
        pytest.fail(
            "dotfiles/config/agents.yaml must parse to a mapping "
            "(editors.yaml pattern), got: " + type(doc).__name__
        )
    return doc


def hc_entries(doc):
    entries = doc.get("agent_integrations")
    if not isinstance(entries, list) or not entries:
        pytest.fail(
            "dotfiles/config/agents.yaml is missing a non-empty "
            "`agent_integrations` list (editors.yaml names its domain key "
            "`editor_extensions`; the herdr catalogue mirrors that shape)."
        )
    return entries


def hc_ignored(doc):
    ignored = doc.get("agent_integrations_ignored")
    if not isinstance(ignored, list):
        pytest.fail(
            "dotfiles/config/agents.yaml is missing the explicit "
            "`agent_integrations_ignored` list (the pattern keeps one so an "
            "id-diff drift report does not read non-wired ids as drift forever)."
        )
    return ignored


def hc_entry_by_id(doc, entry_id):
    for entry in hc_entries(doc):
        if isinstance(entry, dict) and entry.get("id") == entry_id:
            return entry
    pytest.fail(
        f"dotfiles/config/agents.yaml has no wired entry with id "
        f"`{entry_id}` (README wires {list(HC_WIRED_IDS)})."
    )


def hc_is_iso_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


# ── Executable contract: the integration loop (fake state, no ansible) ──────


class hc_HerdrMissing(RuntimeError):
    """The loop ran without herdr installed — the contract says RAISE.

    Naming the fix is part of the contract.
    """


def hc_run_integration_loop(entries, probes, dirs, *, herdr_present=True):
    """Executable statement of the skip-vs-raise contract, simulated in Python.

    Contract (apps/herdr/README.md; TOPIC-RECIPES.md skip-vs-raise recipe):
    without herdr the run raises, naming the fix (the mise entry the topic
    owns); per entry, install happens only when the probe binary resolves AND
    the config dir exists (herdr itself refuses to install into a missing
    config dir, so the topic must decline first); otherwise the entry is
    SKIPPED with a report line naming its id, and the run still exits 0 — an
    absent agent never fails the run.
    """
    if not herdr_present:
        raise hc_HerdrMissing(
            "herdr is not installed — fix: install it through mise "
            "(`mise use -g herdr`; the herdr topic owns the entry; never "
            "`herdr update` on a mise install)"
        )
    report, installed = [], []
    for entry in entries:
        probe_ok = entry["probe"] in probes
        dir_ok = entry["config_dir"] in dirs
        if probe_ok and dir_ok:
            installed.append(entry["id"])
            report.append(f"installed {entry['id']}")
        else:
            missing = []
            if not probe_ok:
                missing.append(f"probe `{entry['probe']}` not on PATH")
            if not dir_ok:
                missing.append(f"config dir {entry['config_dir']} does not exist")
            report.append(f"skipped {entry['id']} — " + "; ".join(missing))
    return {"exit_code": 0, "installed": installed, "report": report}


def hc_run_remove(claimed_ids, installed_ids, *, gate=False):
    """Executable statement of the gated-intersection teardown contract.

    Contract (apps/herdr/README.md; TOPIC-RECIPES.md shared-catalogue recipe):
    the gate var `herdr_remove_integrations` defaults false and a plain remove
    uninstalls nothing; when the gate is on, removal uninstalls only the
    intersection of the catalogue-claimed ids and the ids actually installed —
    a machine-held integration the catalogue never claimed is left alone, and
    a claimed id that is not installed produces no uninstall call and no
    failure.
    """
    if not gate:
        return {"exit_code": 0, "uninstalled": []}
    return {
        "exit_code": 0,
        "uninstalled": sorted(set(claimed_ids) & set(installed_ids)),
    }


# ── Synthetic-catalogue generator (valid shapes only) ────────────────────────
# Malformed hand-edited YAML belongs to the edge/stress dimension; these
# properties generate well-formed catalogues to pin the slice RULE itself.

HC_OTHER_SUBSCRIBERS = ("topic-x", "topic-y")


@st.composite
def hc_synthetic_catalogue(draw):
    """Generate a catalogue with at least one entry of every scope class.

    Classes: shared (no ``topics`` key), herdr-scoped, scoped-elsewhere, and
    mixed (herdr plus another subscriber). Guarantees one never-ignored entry
    per in-scope class so the properties always exercise the rule (spec.md:
    assert on the data a property received — no vacuous passes).
    """
    n_shared = draw(st.integers(min_value=1, max_value=3))
    n_herdr = draw(st.integers(min_value=1, max_value=3))
    n_other = draw(st.integers(min_value=1, max_value=3))
    n_mixed = draw(st.integers(min_value=1, max_value=2))
    total = n_shared + n_herdr + n_other + n_mixed
    ids = draw(
        st.lists(
            st.text(alphabet=string.ascii_lowercase, min_size=3, max_size=8),
            min_size=total,
            max_size=total,
            unique=True,
        )
    )
    shared = ids[:n_shared]
    herdr_only = ids[n_shared : n_shared + n_herdr]
    other_only = ids[n_shared + n_herdr : n_shared + n_herdr + n_other]
    mixed = ids[n_shared + n_herdr + n_other :]
    entries = [{"id": entry_id} for entry_id in shared]
    entries += [{"id": entry_id, "topics": [HC_SUBSCRIBER]} for entry_id in herdr_only]
    entries += [
        {
            "id": entry_id,
            "topics": [draw(st.sampled_from(HC_OTHER_SUBSCRIBERS))],
        }
        for entry_id in other_only
    ]
    entries += [
        {
            "id": entry_id,
            "topics": [HC_SUBSCRIBER, draw(st.sampled_from(HC_OTHER_SUBSCRIBERS))],
        }
        for entry_id in mixed
    ]
    protected = {shared[0], herdr_only[0], mixed[0]}
    pool = [entry_id for entry_id in ids if entry_id not in protected]
    ignored = draw(st.sets(st.sampled_from(pool), min_size=1, max_size=len(pool)))
    return {
        "entries": entries,
        "ignored": set(ignored),
        "all_ids": set(ids),
        "keep_shared": shared[0],
        "keep_herdr": herdr_only[0],
        "keep_mixed": mixed[0],
    }


# ── Catalogue schema conformance ─────────────────────────────────────────────


def test_catalogue_exists_parses_with_pattern_shape():
    """The catalogue exists, parses, and carries the editors.yaml pattern shape.

    Dimension: catalogue schema. Sources: dotfiles/config/editors.yaml (the
    pattern: version + domain key + ignored key), TOPIC-RECIPES.md
    shared-catalogue recipe, apps/herdr/README.md.
    """
    # mutation: a top-level key renamed or dropped (agent_integrations ->
    # integrations) silently orphans every consumer of the catalogue.
    doc = hc_require_catalogue()
    assert doc.get("version") == 1, (
        "agents.yaml must pin a schema `version` like editors.yaml does "
        "(found: " + repr(doc.get("version")) + ")"
    )
    entries = doc.get("agent_integrations")
    assert isinstance(entries, list) and entries, (
        "agents.yaml must carry a non-empty `agent_integrations` list "
        "(editors.yaml names its domain key `editor_extensions`)"
    )
    ignored = doc.get("agent_integrations_ignored")
    assert isinstance(ignored, list), (
        "agents.yaml must carry an explicit `agent_integrations_ignored` "
        "list — the pattern keeps one so an id-diff drift report does not "
        "read non-wired ids as drift forever"
    )
    for entry in entries:
        assert isinstance(entry, dict) and entry.get("id"), (
            "every agent_integrations entry must be a mapping with an `id`"
        )


def test_wired_entries_carry_every_required_field():
    """Every wired entry has exactly the fields the pattern requires, well-formed.

    Dimension: catalogue schema. Sources: the field list in the swarm
    assignment (id, why, probe binary, config dir, integration kind, min
    herdr integration version for native restore), editors.yaml entry shape,
    upstream docs for the config-dir-must-exist rule.
    """
    # mutation: dropping a required field (e.g. `why`) or misspelling `kind`
    # passes a casual read; the loop would then install blind or skip blind.
    doc = hc_require_catalogue()
    for entry_id in HC_WIRED_IDS:
        entry = hc_entry_by_id(doc, entry_id)
        assert isinstance(entry.get("why"), str) and entry["why"].strip(), (
            f"entry `{entry_id}` needs a non-empty `why` (required by the "
            "pattern: a verdict is evidence, not a switch)"
        )
        assert not entry["why"].startswith("Review"), (
            f"entry `{entry_id}` is wired per the README, so its `why` is "
            "confirmed — a `Review:` prefix would mark it drafted-only"
        )
        probe = entry.get("probe")
        assert isinstance(probe, str) and probe.strip() and "/" not in probe, (
            f"entry `{entry_id}` needs a `probe` binary NAME resolved on PATH "
            f"(no path separators); got {probe!r}"
        )
        config_dir = entry.get("config_dir")
        assert isinstance(config_dir, str) and config_dir.startswith("~/"), (
            f"entry `{entry_id}` needs a home-relative `config_dir` (starts "
            "with `~/`, resolved on the target at deploy time per the "
            "resolved-never-written rule); got " + repr(config_dir)
        )
        assert entry.get("kind") in ("lifecycle", "session"), (
            f"entry `{entry_id}` needs `kind` lifecycle|session (upstream "
            "docs: lifecycle authority vs session identity); got "
            + repr(entry.get("kind"))
        )
        floor = entry.get("min_version")
        assert isinstance(floor, dict), (
            f"entry `{entry_id}` needs `min_version` as a dated verdict "
            "{version, checked} (editors.yaml verdict style); got " + repr(floor)
        )
        assert isinstance(floor.get("version"), int) and floor["version"] >= 1, (
            f"entry `{entry_id}` min_version.version must be a positive int"
        )
        assert hc_is_iso_date(floor.get("checked")), (
            f"entry `{entry_id}` min_version.checked must be an ISO date "
            "(the dated-evidence rule: a figure carries what produced it)"
        )


def test_wired_set_is_exactly_the_readme_three():
    """Wired ids are exactly {opencode, claude, cursor}; codex is not wired.

    Dimension: catalogue content vs README. Source: apps/herdr/README.md —
    wired: opencode (lifecycle), claude (session-identity hook), cursor
    (session identity); candidates listed but NOT wired: codex.
    """
    # mutation: codex wired (it has no topic and would install behind the
    # catalogue), or cursor dropped (the entry must stay to keep
    # skip-and-report exercised on a real agent).
    doc = hc_require_catalogue()
    entries = hc_entries(doc)
    wired = [e.get("id") for e in entries]
    assert len(wired) == len(set(wired)), (
        "wired ids must be unique; got duplicates: "
        + repr(sorted({i for i in wired if wired.count(i) > 1}))
    )
    assert set(wired) == set(HC_WIRED_IDS), (
        f"wired set must be exactly {sorted(HC_WIRED_IDS)} per the README; "
        f"got {sorted(wired)}"
    )
    ignored_ids = {e.get("id") for e in hc_ignored(doc)}
    overlap = set(wired) & ignored_ids
    assert not overlap, f"an id must not be both wired and ignored: {sorted(overlap)}"


def test_wired_entry_facts_match_upstream_docs():
    """Probe, config dir and kind per entry match the upstream integration docs.

    Dimension: catalogue content. Sources: herdr docs 0.9.1 (checked
    2026-09-19) — OpenCode is lifecycle authority, Claude Code and Cursor
    Agent CLI are session identity; config dirs ~/.config/opencode,
    ~/.claude, ~/.cursor must already exist; the README names the
    cursor-agent probe.
    """
    # mutation: cursor's probe written as `cursor` instead of `cursor-agent`
    # (the README names cursor-agent explicitly) — the probe would never
    # resolve and the entry would skip forever while looking correct.
    # mutation: opencode's kind flipped to session — native lifecycle
    # authority would be dropped silently.
    doc = hc_require_catalogue()
    for entry_id, facts in HC_WIRED_FACTS.items():
        entry = hc_entry_by_id(doc, entry_id)
        assert entry["probe"] == facts["probe"], (
            f"{entry_id}: probe must be {facts['probe']!r} (upstream/README); "
            f"got {entry['probe']!r}"
        )
        assert entry["config_dir"] == facts["config_dir"], (
            f"{entry_id}: config_dir must be {facts['config_dir']!r} — herdr "
            "refuses to install when that dir does not exist; got "
            f"{entry['config_dir']!r}"
        )
        assert entry["kind"] == facts["kind"], (
            f"{entry_id}: kind must be {facts['kind']!r} per the upstream "
            f"integration-type table; got {entry['kind']!r}"
        )


def test_ignored_list_covers_codex_and_upstream_ids():
    """Codex is ignored (candidate, not wired) and every upstream id is accounted for.

    Dimension: catalogue content. Sources: apps/herdr/README.md — candidates
    listed but not wired: codex (mise-owned npm binary, no topic), and the
    rest of herdr's integration list marked why-not; editors.yaml ignored
    list shape (id + why + checked).
    """
    # mutation: codex deleted from the ignored list — every future id-diff
    # drift report then flags codex forever, the exact drift-noise the
    # ignored list exists to prevent.
    # mutation: an upstream integration (say grok) dropped from both wired
    # and ignored — the catalogue no longer accounts for herdr's own list.
    doc = hc_require_catalogue()
    entries = hc_entries(doc)
    wired = {e.get("id") for e in entries}
    ignored = hc_ignored(doc)
    ignored_ids = [e.get("id") for e in ignored]
    assert len(ignored_ids) == len(set(ignored_ids)), "ignored ids must be unique"
    assert "codex" in ignored_ids, (
        "codex must be in agent_integrations_ignored (README: candidate, "
        "not wired — mise-owned npm binary, no topic)"
    )
    assert "codex" not in wired, "codex must not be wired"
    for entry in ignored:
        assert isinstance(entry, dict) and entry.get("id"), (
            "every agent_integrations_ignored entry must be a mapping with an `id`"
        )
        assert isinstance(entry.get("why"), str) and entry["why"].strip(), (
            f"ignored entry {entry.get('id')!r} needs a why-not (`why`)"
        )
        assert hc_is_iso_date(entry.get("checked")), (
            f"ignored entry {entry.get('id')!r} needs a dated `checked` "
            "(the pattern's dated verdicts are the recorded evidence)"
        )
    unaccounted = HC_UPSTREAM_IDS - wired - set(ignored_ids)
    assert not unaccounted, (
        "every herdr upstream integration id must be either wired or "
        f"ignored (docs 0.9.1, checked 2026-09-19); unaccounted: "
        f"{sorted(unaccounted)}"
    )


def test_native_restore_floors_recorded_dated():
    """The per-entry native-restore floors are recorded, dated verdict style.

    Dimension: catalogue content. Source: herdr docs 0.9.1 (checked
    2026-09-19): "Native session restore requires current Herdr
    integrations: ... Claude Code version 6 ... OpenCode version 5 ...
    Cursor Agent CLI version 1". The README calls the opencode floor out
    explicitly (needs herdr integration v5+ for native restore).
    """
    # mutation: the opencode floor edited to 4 (or its checked date dropped) —
    # native restore for opencode would silently break on a v4 integration
    # while the catalogue still reads as healthy.
    doc = hc_require_catalogue()
    for entry_id in HC_WIRED_IDS:
        entry = hc_entry_by_id(doc, entry_id)
        floor = entry["min_version"]
        assert floor["version"] == HC_WIRED_FACTS[entry_id]["floor"], (
            f"{entry_id}: native-restore floor must be "
            f"{HC_WIRED_FACTS[entry_id]['floor']} (herdr integration version, "
            f"docs 0.9.1 checked 2026-09-19); got {floor['version']}"
        )
        assert hc_is_iso_date(floor["checked"]), (
            f"{entry_id}: the floor must carry its checked date (dated "
            "verdict style — evidence, not assertion)"
        )
    opencode_floor = hc_entry_by_id(doc, "opencode")["min_version"]
    assert opencode_floor["version"] == 5, (
        "the README names it: opencode needs herdr integration v5+ for "
        f"native restore; recorded {opencode_floor['version']}"
    )


# ── Slice resolution (pure rule, stated independently) ──────────────────────


def test_real_catalogue_slice_matches_first_principles():
    """The slice herdr consumes, computed from first principles on the real file.

    Dimension: slice resolution. Sources: the swarm assignment's rule and the
    editors.yaml scope semantics (absent scope = shared by default; scoped
    entries name their subscribers; the ignored list never reaches a
    subscriber).

    The rule, stated here as the spec — no implementation exists yet, and the
    resolver must match it:
        slice = {entry ids with no `topics` key or `herdr` in `topics`}
                minus the ignored ids.
    """
    # mutation: the slice leaking ignored ids to the subscriber, or dropping
    # shared-by-default entries (scope must default to shared, not shared-
    # only-when-listed).
    doc = hc_require_catalogue()
    entries = hc_entries(doc)
    ignored = {e.get("id") for e in hc_ignored(doc)}
    all_ids = {e.get("id") for e in entries}
    additive = {
        e["id"]
        for e in entries
        if (e.get("topics") is None or HC_SUBSCRIBER in e["topics"])
        and e["id"] not in ignored
    }
    # The same rule stated subtractively — two independent constructions of
    # the expected set must agree on the real file.
    scoped_away = {
        e["id"]
        for e in entries
        if e.get("topics") is not None and HC_SUBSCRIBER not in e["topics"]
    }
    subtractive = all_ids - ignored - scoped_away
    assert additive == subtractive, (
        "the two independent statements of the slice rule disagree on the "
        f"real catalogue: additive {sorted(additive)} vs subtractive "
        f"{sorted(subtractive)}"
    )
    assert set(HC_WIRED_IDS) <= additive, (
        f"the README wires {sorted(HC_WIRED_IDS)} to herdr; missing from "
        f"the slice: {sorted(set(HC_WIRED_IDS) - additive)}"
    )
    assert additive.isdisjoint(ignored), (
        f"ignored ids must never reach a subscriber's slice; leaked: "
        f"{sorted(additive & ignored)}"
    )
    assert additive <= all_ids, (
        f"the slice must be a subset of the catalogue ids; invented: "
        f"{sorted(additive - all_ids)}"
    )
    assert additive, "the resolved slice must not be empty"
    assert "codex" not in additive, (
        "codex is a candidate, not wired — never in the slice"
    )


@settings(max_examples=100, deadline=None)
@given(hc_synthetic_catalogue())
def test_slice_resolution_idempotent_property(catalogue_data):
    """Property: slice(slice(x)) == slice(x) over generated catalogues.

    Dimension: slice resolution. Source: the swarm assignment (idempotence
    property) and spec.md § Verification — invariants are tested as
    properties, stated independently. The rule is computed from first
    principles per generated entry below, not by a resolver the
    implementation may later copy.
    """
    # mutation: a resolver that mutates scoping or ignored state as it
    # filters — re-resolving an already-resolved slice would then shrink or
    # grow it, and a second converge would report changes forever.
    hc_require_catalogue()
    entries = catalogue_data["entries"]
    ignored = catalogue_data["ignored"]
    # Data-received guard: the generator guarantees one entry per scope class
    # and a non-empty ignored set — prove it held, or the property is vacuous.
    assert entries and ignored, "generator produced an empty catalogue"
    assert catalogue_data["keep_shared"] in {e["id"] for e in entries}
    # The rule, applied once (additive, per entry, from first principles):
    selected = {
        e["id"]
        for e in entries
        if (e.get("topics") is None or HC_SUBSCRIBER in e["topics"])
        and e["id"] not in ignored
    }
    # Applied a second time: the slice handed back through resolution must
    # resolve to itself — scope facts and ignored membership do not change
    # between applications.
    reselected = {
        entry_id
        for entry_id in selected
        if entry_id not in ignored
        and any(
            (e.get("topics") is None or HC_SUBSCRIBER in e["topics"])
            for e in entries
            if e["id"] == entry_id
        )
    }
    assert reselected == selected, (
        f"slice resolution is not idempotent: first pass {sorted(selected)}, "
        f"second pass {sorted(reselected)}"
    )


@settings(max_examples=100, deadline=None)
@given(hc_synthetic_catalogue())
def test_slice_subset_and_ignored_disjoint_property(catalogue_data):
    """Property: the slice is a subset of the input ids and never contains ignored ids.

    Dimension: slice resolution. Sources: the swarm assignment (subset
    property; minus the ignored list) and the shared-catalogue recipe (the
    ignored list exists so non-wired ids are expected, never delivered).
    """
    # mutation: the slice built from the union of wired and ignored lists, or
    # an ignored id reaching a subscriber (the codex leak).
    hc_require_catalogue()
    entries = catalogue_data["entries"]
    ignored = catalogue_data["ignored"]
    all_ids = catalogue_data["all_ids"]
    assert entries and ignored, "generator produced an empty catalogue"
    selected = {
        e["id"]
        for e in entries
        if (e.get("topics") is None or HC_SUBSCRIBER in e["topics"])
        and e["id"] not in ignored
    }
    assert selected <= all_ids, (
        f"slice invented ids outside the catalogue: {sorted(selected - all_ids)}"
    )
    assert selected.isdisjoint(ignored), (
        f"ignored ids leaked into the slice: {sorted(selected & ignored)}"
    )
    # Data-received guards: the generator protects one never-ignored entry
    # per in-scope class; each must actually arrive in the slice.
    assert catalogue_data["keep_shared"] in selected, (
        "a shared-by-default entry must be in the slice — scope defaults to "
        "shared, not shared-only-when-listed"
    )
    assert catalogue_data["keep_herdr"] in selected, (
        "an entry explicitly scoped to herdr must be in the slice"
    )
    assert catalogue_data["keep_mixed"] in selected, (
        "an entry scoped to herdr among other subscribers must be in the "
        "slice (the union rule's explicit-scope half)"
    )


@settings(max_examples=100, deadline=None)
@given(hc_synthetic_catalogue())
def test_slice_membership_agrees_across_two_procedures(catalogue_data):
    """Property: per-entry membership by scope, computed two independent ways.

    Dimension: slice resolution. Source: the swarm assignment — the rule is
    the spec; state it independently of any implementation. Here the additive
    form (select shared-or-herdr-scoped, minus ignored) and the subtractive
    form (all ids, minus ignored, minus scoped-elsewhere) must classify every
    generated entry identically.
    """
    # mutation: scoping inverted — an `is None` flipped so entries scoped
    # AWAY from herdr leak in while shared-by-default entries drop out.
    hc_require_catalogue()
    entries = catalogue_data["entries"]
    ignored = catalogue_data["ignored"]
    all_ids = catalogue_data["all_ids"]
    assert entries and ignored, "generator produced an empty catalogue"
    additive = {
        e["id"]
        for e in entries
        if (e.get("topics") is None or HC_SUBSCRIBER in e["topics"])
        and e["id"] not in ignored
    }
    scoped_away = {
        e["id"]
        for e in entries
        if e.get("topics") is not None and HC_SUBSCRIBER not in e["topics"]
    }
    subtractive = all_ids - ignored - scoped_away
    assert additive == subtractive, (
        "the two statements of the membership rule disagree: "
        f"additive {sorted(additive)} vs subtractive {sorted(subtractive)}"
    )
    for entry in entries:
        topics = entry.get("topics")
        in_scope = topics is None or HC_SUBSCRIBER in topics
        should_be_in = in_scope and entry["id"] not in ignored
        is_in = entry["id"] in additive
        assert is_in == should_be_in, (
            f"entry {entry!r} misclassified: expected "
            f"{'in' if should_be_in else 'out'} of the herdr slice"
        )


# ── The integration loop (simulated against fake state) ─────────────────────


def test_loop_installs_entries_when_probe_and_dir_present():
    """The gate PROCEEDS: present probe + config dir installs, run stays green.

    Dimension: skip-vs-raise, install direction. Sources: apps/herdr/README.md
    (installs per entry whose probe binary and config dir both exist) and the
    skip-vs-raise recipe; spec.md § Verification — a guard is proven to
    proceed when it may, not only to decline.
    """
    # mutation: the guard inverted or removed — the loop installing entries
    # whose agent is absent, or never installing present ones (a guard that
    # always declines is indistinguishable from one that never runs).
    doc = hc_require_catalogue()
    entries = [hc_entry_by_id(doc, entry_id) for entry_id in HC_WIRED_IDS]
    probes = {e["probe"] for e in entries}
    dirs = {e["config_dir"] for e in entries}
    result = hc_run_integration_loop(entries, probes, dirs)
    assert set(result["installed"]) == set(HC_WIRED_IDS), (
        f"every present wired entry must install; got {result['installed']}"
    )
    assert result["exit_code"] == 0, "a converged install run exits 0"
    assert all(line.startswith("installed") for line in result["report"]), (
        f"report must record installs, got {result['report']}"
    )
    assert not any("skipped" in line for line in result["report"]), (
        "nothing should be skipped when every probe and config dir exists"
    )


def test_loop_skips_absent_agents_reports_and_stays_green():
    """The gate DECLINES: absent agents skip, the run reports each id, exits 0.

    Dimension: skip-vs-raise, skip direction. Sources: apps/herdr/README.md —
    skips-and-reports when the agent is absent (the dated instance: cursor's
    cursor-agent probe not installed on this Mac as of 2026-09-19); the
    skip-vs-raise recipe — the integration phase never fails the run for an
    absent agent. Fake state only; the tests never probe the real machine.
    """
    # mutation: a skip that fails the run (exit != 0) — one absent agent
    # would then break every converge on every machine lacking it.
    # mutation: a silent skip — no report line naming the id, so the run
    # "succeeds" having done nothing and said nothing.
    doc = hc_require_catalogue()
    entries = [hc_entry_by_id(doc, entry_id) for entry_id in HC_WIRED_IDS]
    result = hc_run_integration_loop(entries, probes=set(), dirs=set())
    assert result["installed"] == [], "nothing may install when all state is absent"
    assert result["exit_code"] == 0, "a skip must never fail the run"
    report_text = "\n".join(result["report"])
    assert report_text.strip(), "the skip path must REPORT, not continue silently"
    for entry_id in HC_WIRED_IDS:
        lines = [line for line in result["report"] if entry_id in line]
        assert len(lines) == 1 and lines[0].startswith("skipped"), (
            f"{entry_id} must be reported skipped exactly once; got {lines}"
        )
    assert "cursor-agent" in report_text, (
        "the skip line names the missing probe (cursor-agent), per the README's why"
    )


def test_loop_gate_requires_probe_and_config_dir():
    """The gate is AND: both present installs; each single-missing combo skips.

    Dimension: skip-vs-raise gate semantics. Sources: apps/herdr/README.md —
    "installs per entry whose probe binary and config dir both exist";
    upstream docs — herdr refuses to install an integration when the config
    dir does not exist, so the topic must decline first.
    """
    # mutation: the guard degraded to OR — installing when only one of the
    # two exists would hand herdr a missing config dir, which herdr itself
    # refuses (the run would then report an install herdr never accepted).
    hc_require_catalogue()
    entries = [
        {"id": "agent-a", "probe": "agent-a", "config_dir": "~/.agent-a"},
        {"id": "agent-b", "probe": "agent-b", "config_dir": "~/.agent-b"},
        {"id": "agent-c", "probe": "agent-c", "config_dir": "~/.agent-c"},
        {"id": "agent-d", "probe": "agent-d", "config_dir": "~/.agent-d"},
    ]
    probes = {"agent-a", "agent-b"}
    dirs = {"~/.agent-a", "~/.agent-c"}
    result = hc_run_integration_loop(entries, probes, dirs)
    assert result["installed"] == ["agent-a"], (
        "only the entry with BOTH probe and config dir present installs; "
        f"got {result['installed']}"
    )
    assert result["exit_code"] == 0, "skips keep the run green"
    for entry_id in ("agent-b", "agent-c", "agent-d"):
        lines = [line for line in result["report"] if entry_id in line]
        assert len(lines) == 1 and lines[0].startswith("skipped"), (
            f"{entry_id} must be reported skipped exactly once; got {lines}"
        )


def test_loop_raises_naming_the_fix_when_herdr_missing():
    """Herdr absent RAISES with the named fix — it is not a fourth skip.

    Dimension: skip-vs-raise, raise direction. Sources: TOPIC-RECIPES.md
    skip-vs-raise recipe (a required provider absent raises — a run that
    leaves the integration phase half-wired is worse than a failed run with a
    named fix); apps/herdr/README.md (the binary installs through mise; the
    topic owns the entry).
    """
    # mutation: herdr-absent downgraded to a skip — the whole loop would
    # silently no-op on a box where herdr never installed, and nothing would
    # name the fix.
    doc = hc_require_catalogue()
    entries = [hc_entry_by_id(doc, entry_id) for entry_id in HC_WIRED_IDS]
    with pytest.raises(hc_HerdrMissing) as excinfo:
        hc_run_integration_loop(entries, probes=set(), dirs=set(), herdr_present=False)
    message = str(excinfo.value)
    assert message.strip(), "the raise must carry a message"
    assert "herdr" in message, "the raise names what is missing"
    assert "mise" in message and "mise use -g herdr" in message, (
        "the raise names the fix: the mise entry the herdr topic owns "
        f"(`mise use -g herdr`); got {message!r}"
    )


def test_loop_acts_on_slice_never_on_ignored_ids():
    """The loop consumes the resolved slice — an ignored id is never installed.

    Dimension: slice → loop handoff. Sources: TOPIC-RECIPES.md shared-
    catalogue recipe (the subscriber consumes its slice; the ignored list
    marks ids that must not be delivered) and apps/herdr/README.md (codex is
    a candidate, not wired). Fake state gives codex and grok BOTH probe and
    config dir — present on the machine, unclaimed by the catalogue.
    """
    # mutation: the loop iterating the raw catalogue list instead of the
    # resolved slice — codex (or any ignored id) with its agent state present
    # would get installed behind the catalogue's back.
    doc = hc_require_catalogue()
    entries = hc_entries(doc)
    ignored = {e.get("id") for e in hc_ignored(doc)}
    slice_entries = [
        e
        for e in entries
        if (e.get("topics") is None or HC_SUBSCRIBER in e.get("topics", []))
        and e["id"] not in ignored
    ]
    assert not ({e["id"] for e in slice_entries} & ignored), (
        "the handoff to the loop is the slice — no ignored id in it"
    )
    probes = {e["probe"] for e in slice_entries}
    dirs = {e["config_dir"] for e in slice_entries}
    for facts in HC_UNCLAIMED_FACTS.values():
        probes.add(facts["probe"])
        dirs.add(facts["config_dir"])
    result = hc_run_integration_loop(slice_entries, probes, dirs)
    assert set(result["installed"]) == set(HC_WIRED_IDS), (
        f"the loop installs exactly the wired slice, never the ignored ids "
        f"whose state is present; got {result['installed']}"
    )
    for unclaimed in HC_UNCLAIMED_FACTS:
        assert unclaimed not in result["installed"], (
            f"{unclaimed} is not wired — the catalogue must never hand it to the loop"
        )


# ── Gated teardown ───────────────────────────────────────────────────────────


def test_remove_defaults_to_no_uninstall():
    """`herdr_remove_integrations` defaults false: a plain remove uninstalls nothing.

    Dimension: gated teardown, gate-off direction. Sources: apps/herdr/README.md
    (remove uninstalls only the installed intersection, gated by
    herdr_remove_integrations, default off — same gate pattern as
    vscode_remove_extensions) and the shared-catalogue recipe (teardown is
    gated, default-off opt-out).
    """
    # mutation subject: THIS test pins the contract module's gate semantics
    # (gate False -> []). The defaults VAR is pinned by the lifecycle and
    # edge tests (test_remove_integrations_gate_defaults_off reads
    # defaults/main.yaml) — mutation M1's log records exactly this split.
    doc = hc_require_catalogue()
    claimed = list(HC_WIRED_IDS)
    installed = list(HC_WIRED_IDS)
    result = hc_run_remove(claimed, installed)
    assert result["uninstalled"] == [], (
        "with the gate at its default (off), remove must uninstall nothing"
    )
    assert result["exit_code"] == 0, "a gate-off remove is a clean no-op"


def test_remove_intersection_leaves_unclaimed_and_absent_alone():
    """Gate on: only claimed∩installed uninstalls.

    Unclaimed held ids and absent claims are safe.

    Dimension: gated teardown, intersection semantics. Sources:
    TOPIC-RECIPES.md shared-catalogue recipe — teardown uninstalls only the
    intersection of what the catalogue claims and what is actually installed,
    never everything installed, because the machine may hold things the topic
    does not own; apps/herdr/README.md (codex/grok-style unclaimed ids).
    """
    # mutation: remove uninstalling everything installed — machine-held
    # integrations the catalogue never claimed (codex installed by hand) get
    # stripped.
    # mutation: remove uninstalling everything claimed — claimed-but-absent
    # ids produce phantom uninstall calls or a failure.
    hc_require_catalogue()
    claimed = list(HC_WIRED_IDS)
    held = ["opencode", "codex", "grok"]
    result = hc_run_remove(claimed, held, gate=True)
    assert result["uninstalled"] == ["opencode"], (
        f"only the claimed∩installed id uninstalls; got {result['uninstalled']}"
    )
    for unclaimed in ("codex", "grok"):
        # pyrefly: ignore [not-iterable]
        assert unclaimed not in result["uninstalled"], (
            f"{unclaimed} is on the machine but unclaimed — left alone"
        )
    only_absent = hc_run_remove(claimed, ["claude"], gate=True)
    assert only_absent["uninstalled"] == ["claude"], (
        "the one held claimed id uninstalls"
    )
    # pyrefly: ignore [not-iterable]
    assert "cursor" not in only_absent["uninstalled"], (
        "a claimed-but-not-installed id gets no uninstall call"
    )
    assert only_absent["exit_code"] == 0, (
        "a claimed id that is not installed never fails the remove"
    )


# The remove property needs the held/installed set generated directly, not
# the catalogue generator: gate-on remove is a pure intersection over ids.
HC_REMOVE_UNIVERSE = ("opencode", "claude", "cursor", "codex", "grok", "pi", "kimi")


@settings(max_examples=75, deadline=None)
@given(installed=st.sets(st.sampled_from(HC_REMOVE_UNIVERSE)))
def test_remove_uninstalls_exactly_the_intersection_property(installed):
    """Property: gate-on remove == claimed ∩ installed, over generated states.

    Dimension: gated teardown. Sources: the swarm assignment (property on the
    intersection) and TOPIC-RECIPES.md shared-catalogue recipe — teardown
    uninstalls only the intersection of what the catalogue claims and what is
    actually installed, never everything installed. The expected set is the
    first-principles set expression in the test; the simulation helper is the
    contract statement this property checks the rule against.
    """
    # mutation: the intersection computed as claimed ∪ installed, or the
    # gate checked per-entry instead of per-run — the remove set grows
    # beyond what the catalogue owns.
    hc_require_catalogue()
    claimed = set(HC_WIRED_IDS)
    assert claimed <= set(HC_REMOVE_UNIVERSE), (
        "the universe must contain every claimed id (data-received guard)"
    )
    expected = sorted(claimed & installed)
    result = hc_run_remove(sorted(claimed), sorted(installed), gate=True)
    assert result["uninstalled"] == expected, (
        f"gate-on remove must be exactly claimed ∩ installed: expected "
        f"{expected}, got {result['uninstalled']}"
    )
    # pyrefly: ignore [not-iterable]
    assert all(entry_id in claimed for entry_id in result["uninstalled"]), (
        f"unclaimed ids must never be uninstalled: {result['uninstalled']}"
    )
    assert result["exit_code"] == 0, "a gated remove never fails on intersections"
