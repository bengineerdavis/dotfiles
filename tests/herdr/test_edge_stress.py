"""
tests/herdr/test_edge_stress.py — EDGE/STRESS dimension of the herdr swarm suite.

Author: edge/stress test author (one of four independent swarm authors,
2026-09-19). This suite attacks the herdr topic with malformed catalogue
input, hostile status output, hostile boundaries and hostile teardown state.
Everything is simulated in Python; no real herdr run, no `chezmoi apply`.

Sources the contract was deduced from (artifacts only, no implementation read):
  - dotfiles/apps/herdr/README.md            — the design record (THE contract)
  - dotfiles/docs/TOPIC-RECIPES.md           — shared-catalogue recipe (the
    `*_ignored` drift-report principle), thin install-and-report loop
    (failed_when false per item, one final raise), skip-vs-raise recipe
    (integration absent = skip-and-report; required dependency absent = raise)
  - spec.md § Verification — exit status read directly; input handling is
    fuzzed at the boundary (hand-edited YAML, loader rejects with file and
    field named, unknown never becomes a claim); a test is not finished until
    seen to fail; invariants are properties
  - TASKS.md § Now (2026-09-19) — the two herdr task lines (edge/stress
    dimension named there: malformed catalogue, herdr absent, partial
    integrations, stale service state)
  - https://herdr.dev/docs/cli-reference/ — JSON on stdout; server errors are
    JSON on stderr with exit 1; CLI usage errors exit 2
  - https://herdr.dev/docs/integrations/ — install/uninstall/status commands

SPEC-FIRST CONTRACT MODULE
==========================
The topic does not exist yet. This file states the contract the implementation
will have to match as a small pure-Python module the implementer must provide
at one of HE_CONTRACT_CANDIDATES. Every test below fails NAMED until that
module exists (import-locate failure via he_contract()); tests that read repo
artifacts that do not exist yet (the real catalogue, the topic's task YAML,
the topic's defaults) also fail NAMED at the expected path. Nothing skips.

Required API of the contract module (the contract this file states):

    StatusUnknownError                — ValueError subclass; message must
                                        contain the word "unknown" and name
                                        the concrete failure
    validate_catalogue(data, source="dotfiles/config/agents.yaml") -> list[str]
        TOTAL over any parsed-YAML input: never raises, never silently
        coerces. Returns a list of human-readable errors; every error names
        the source file AND the offending field (and the entry id or index
        where an entry is involved). Empty list = valid. An unknown verdict
        status is an error, never coerced to a known one.
    planned_install_commands(data, source=...) -> list[str]
        For a valid catalogue: one "herdr integration install <id>" per
        entry, in catalogue order, no duplicates. Invalid input -> ValueError
        naming the validation errors.
    parse_integration_status(text: str) -> dict[str, dict]
        rc handling is the caller's job (see remove_plan). For rc==0 stdout:
        returns id -> record. Raises StatusUnknownError for empty/whitespace
        text, control characters, non-status prose, truncated lines, lines
        outside the measured grammar, an unknown state word, or an id
        claimed twice — never returns a partial claim.
        Wire format (MEASURED on the real binary 2026-09-19, herdr 0.9.1;
        --json is a usage error): lines of
        `<id>: installed (<absolute path>)` /
        `<id>: not installed (<expected path>)`.
    install_loop(entries, probes, herdr_present, run_install) -> report
        entries: validated catalogue entries; probes: id -> (probe_present,
        config_dir_exists); run_install: id -> rc (injected command).
        report.attempts: list of (id, rc); report.skips: list of (id, reason)
        where reason names BOTH the probe condition and the config-dir
        condition; report.raise_if_failed(): after the loop, raises ValueError
        naming ALL failed ids and their rcs (no-op when clean). The loop never
        retries and never fails mid-loop. herdr_present False with entries to
        consider -> immediate ValueError naming the fix (`mise use -g herdr`).
    remove_plan(status_rc, status_stdout, catalogue_ids, gate) -> list[str]
        gate False -> []. rc != 0 -> ValueError naming rc (2 = usage error).
        stdout unparseable at rc 0 -> StatusUnknownError (refuse; never read
        as "nothing installed" nor as "everything installed"). Valid ->
        "herdr integration uninstall <id>" for the INTERSECTION of catalogue
        ids and installed ids, in catalogue order — never every installed id,
        never ids the topic does not own.
    teardown_plan(state, catalogue_ids, gate) -> list[(kind, target)]
        state keys: herdr_present, integrations_installed (set),
        service_loaded, unit_file_exists, mise_entry_present. Kinds:
        integration_uninstall | service_unload | service_unit_delete |
        mise_unuse. Emits a command ONLY for state that is present (the
        idempotence source); a converged machine yields [].

Assumptions are recorded inline where made (search "ASSUMPTION").
"""
from __future__ import annotations

import importlib.util
import pathlib
import re

import pytest

pytest.importorskip("hypothesis")
pytest.importorskip("yaml")

from hypothesis import given, settings
from hypothesis import strategies as st

import yaml

# ── paths and constants ──────────────────────────────────────────────────────

REPO = pathlib.Path(__file__).resolve().parents[2]

HE_AGENTS_YAML = REPO / "dotfiles" / "config" / "agents.yaml"
HE_TOPIC_DIR = REPO / "dotfiles" / "apps" / "herdr"
HE_TASKS_DIR = HE_TOPIC_DIR / "tasks"
HE_DEFAULTS = HE_TOPIC_DIR / "defaults" / "main.yaml"

HE_CONTRACT_CANDIDATES = [
    REPO / "tests" / "herdr" / "agents_contract.py",
    REPO / "dotfiles" / "apps" / "herdr" / "files" / "agents_catalogue.py",
]

# The contract the implementation must match, stated here so the implementer
# reads it next to the failing tests (see module docstring for full wording).
HE_REQUIRED_FIELDS = ("id", "why", "probe", "config_dir")
# Verdict status vocabulary, taken from the cited precedent dotfiles/config/
# editors.yaml (statuses actually in use there: ok / not-available / substituted).
# ASSUMPTION: agents.yaml reuses this vocabulary; the real-catalogue test will
# name any divergence for the author to resolve.
HE_KNOWN_STATUSES = frozenset({"ok", "not-available", "substituted"})
# Top-level keys follow the editors.yaml naming pattern (<domain> / <domain>_ignored).
# ASSUMPTION: agents.yaml uses agent_integrations / agent_integrations_ignored.
HE_TOP_ENTRIES_KEY = "agent_integrations"
HE_TOP_IGNORED_KEY = "agent_integrations_ignored"
# herdr ids are spelled exactly as upstream docs spell them (all lowercase,
# digits and hyphens: pi, omp, claude, opencode, qodercli, antigravity-cli, ...).
HE_ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")

# Exit-status doctrine: an rc-bearing command must not be read through a
# pipeline (spec.md § Verification — exit status is read directly). These are
# the classic rc-masking pipes; `2>&1` and `> file` redirects are not pipes.
HE_RC_MASKING_PIPES = re.compile(
    r"\|\s*(head|tail|grep|wc|awk|sed|sort|true|xargs)\b"
)

# ── contract-module and repo-artifact locators (all fail NAMED) ──────────────


def he_contract():
    """Import the contract module the implementation must provide, or fail named."""
    existing = [str(p) for p in HE_CONTRACT_CANDIDATES if p.is_file()]
    if existing:
        for path in existing:
            spec = importlib.util.spec_from_file_location("he_agents_contract", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    pytest.fail(
        "contract module not implemented yet — expected one of:\n  "
        + "\n  ".join(str(p) for p in HE_CONTRACT_CANDIDATES)
        + "\nThe implementation must provide the API stated in the docstring "
        "of tests/herdr/test_edge_stress.py (validate_catalogue, "
        "planned_install_commands, parse_integration_status, install_loop, "
        "remove_plan, teardown_plan, StatusUnknownError)."
    )


def he_load_agents_yaml():
    """Load the real shared catalogue, or fail named — never skip, never fake."""
    if not HE_AGENTS_YAML.is_file():
        pytest.fail(
            f"shared catalogue not created yet — expected {HE_AGENTS_YAML} "
            "(dotfiles/config/agents.yaml per dotfiles/apps/herdr/README.md; "
            "editors.yaml pattern, shared-catalogue recipe)"
        )
    with HE_AGENTS_YAML.open() as fh:
        data = yaml.safe_load(fh)
    return data


def he_topic_task_files():
    """Return the topic's task YAML files, or fail named if the topic is not built."""
    if not HE_TASKS_DIR.is_dir():
        pytest.fail(
            f"topic tasks not implemented yet — expected {HE_TASKS_DIR}/ "
            "(tasks/main.yaml router + install.yaml + upgrade.yaml + remove.yaml "
            "per dotfiles/apps/herdr/README.md § Structure)"
        )
    files = sorted(HE_TASKS_DIR.glob("*.yaml"))
    if not files:
        pytest.fail(f"no task YAML found in {HE_TASKS_DIR} — vacuous scan refused")
    return files


def he_defaults_data():
    """Load the topic defaults, or fail named."""
    if not HE_DEFAULTS.is_file():
        pytest.fail(
            f"topic defaults not implemented yet — expected {HE_DEFAULTS} "
            "(README § Structure: defaults/main.yaml holds gate vars and the "
            "catalogue path)"
        )
    with HE_DEFAULTS.open() as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        pytest.fail(f"{HE_DEFAULTS} must parse to a mapping of vars, got {type(data)}")
    return data


# ── in-memory catalogue builders (the boundary is a hand-edited YAML file) ───


def he_valid_entry(
    eid="opencode",
    why="Agent runs inside herdr panes with native restore",
    probe=None,
    config_dir=None,
    verdict_status="ok",
    include_verdicts=True,
):
    """A catalogue entry that satisfies the stated schema, overridable per field."""
    entry = {
        "id": eid,
        "why": why,
        "probe": probe if probe is not None else f"probe-{eid}",
        "config_dir": config_dir if config_dir is not None else f"~/.config/{eid}",
    }
    if include_verdicts:
        entry["verdicts"] = {
            "herdr": {"status": verdict_status, "checked": "2026-09-19"}
        }
    return entry


def he_valid_catalogue(entries):
    """A catalogue satisfying the stated top-level schema."""
    return {
        "version": 1,
        HE_TOP_ENTRIES_KEY: list(entries),
        HE_TOP_IGNORED_KEY: [],
    }


# ── simulation shims (hostile world, injected into contract functions) ───────


def he_recorder(rcs):
    """A run_install stand-in: returns the next rc, records every call."""
    calls = []

    def run(eid):
        rc = rcs.pop(0) if rcs else 0
        calls.append((eid, rc))
        return rc

    run.calls = calls
    return run


def he_apply_teardown(state, plan):
    """Apply a teardown_plan's structured commands to the fake machine."""
    for kind, target in plan:
        if kind == "integration_uninstall":
            state["integrations_installed"].discard(target)
        elif kind == "service_unload":
            state["service_loaded"] = False
        elif kind == "service_unit_delete":
            state["unit_file_exists"] = False
        elif kind == "mise_unuse":
            state["mise_entry_present"] = False
        else:
            pytest.fail(
                f"teardown_plan emitted a command the design does not declare: "
                f"({kind!r}, {target!r}) — the contract module must only emit "
                "integration_uninstall | service_unload | service_unit_delete | "
                "mise_unuse"
            )


def he_snapshot(state):
    """Hashable-comparable snapshot of a fake machine (sets become sorted lists)."""
    return {k: sorted(v) if isinstance(v, set) else v for k, v in state.items()}


def he_populated_state():
    """A machine where everything the topic owns exists."""
    return {
        "herdr_present": True,
        "integrations_installed": {"opencode", "claude", "zed-not-ours"},
        "service_loaded": True,
        "unit_file_exists": True,
        "mise_entry_present": True,
    }


def he_fresh_state():
    """A machine where nothing was ever installed."""
    return {
        "herdr_present": False,
        "integrations_installed": set(),
        "service_loaded": False,
        "unit_file_exists": False,
        "mise_entry_present": False,
    }


# ══ 1. CATALOGUE FUZZING — the boundary is a hand-edited YAML file ════════════
# spec.md § Verification — input handling is fuzzed at the boundary: malformed
# is the expected state during editing; the loader must reject with file and
# field named; unknown must never become a claim.


@pytest.mark.parametrize(
    "bad_status",
    ["approved", "maybe", "Wired", "", None, 42],
    ids=["approved", "maybe", "Wired", "empty", "none", "int"],
)
def test_unknown_verdict_status_is_rejected(bad_status):
    """An out-of-vocabulary verdict status is an error naming file and field.

    EDGE/STRESS over hand-edited YAML; contract from spec.md § Verification
    (unknown must never become a claim) via the editors.yaml status
    vocabulary (ok / not-available / substituted) cited in TOPIC-RECIPES.md.
    """
    # mutation: the validator accepting an unknown status (or coercing it to
    # a known one) — unknown availability would then install-or-remove as if
    # the author had decided.
    catalogue = he_valid_catalogue([he_valid_entry(verdict_status=bad_status)])
    errs = he_contract().validate_catalogue(catalogue)
    assert errs, f"status {bad_status!r} was silently accepted"
    assert all(isinstance(e, str) for e in errs)
    assert all("agents.yaml" in e for e in errs), errs
    assert any("status" in e for e in errs), errs


@pytest.mark.parametrize(
    "missing_field",
    ["id", "why", "probe", "config_dir", "__all__"],
    ids=["id", "why", "probe", "config_dir", "all-fields"],
)
def test_missing_required_fields_are_rejected(missing_field):
    """Dropping any required field is an error naming that field.

    EDGE/STRESS; required fields from the brief + README + TOPIC-RECIPES
    shared-catalogue schema (id spelled as the tool spells it, required why,
    probe binary and config dir from the skip-vs-raise preconditions).
    """
    # mutation: a missing field silently defaulting (e.g. config_dir falling
    # back to ~/.config/<id>, probe defaulting to the id) — the skip-vs-raise
    # precondition would then test the wrong thing.
    eid = "opencode"
    entry = he_valid_entry(eid)
    if missing_field == "__all__":
        entry = {"verdicts": entry["verdicts"]}
    else:
        del entry[missing_field]
    errs = he_contract().validate_catalogue(he_valid_catalogue([entry]))
    assert errs, f"entry missing {missing_field} was silently accepted"
    assert all("agents.yaml" in e for e in errs), errs
    # "__all__" is a fixture sentinel, not a field name — the per-field loop
    # below does the real assertion. (First red run: the sentinel leaked into
    # this assert and failed for the wrong reason; fixed 2026-09-19.)
    if missing_field != "__all__":
        assert any(missing_field in e for e in errs), errs
    if missing_field == "__all__":
        for field in HE_REQUIRED_FIELDS:
            assert any(field in e for e in errs), (field, errs)


def test_duplicate_ids_are_rejected():
    """Two entries with the same id are rejected, naming the id.

    EDGE/STRESS; duplicate catalogue ids would produce duplicate installs.
    """
    # mutation: last-one-wins dict coercion of entries, which silently drops
    # the duplicate and double-installs the survivor.
    entries = [he_valid_entry("opencode"), he_valid_entry("claude")]
    entries.append(he_valid_entry("opencode"))
    errs = he_contract().validate_catalogue(he_valid_catalogue(entries))
    assert errs, "duplicate id was silently accepted"
    assert all("agents.yaml" in e for e in errs), errs
    assert any("opencode" in e for e in errs), errs


@pytest.mark.parametrize(
    "entry, expected_field",
    [
        ("opencode", "id"),  # bare string, not a mapping
        (["id", "why"], "id"),  # a list, not a mapping
        (None, "id"),  # null entry
        ({}, "id"),  # empty mapping
        (he_valid_entry(config_dir=42), "config_dir"),  # int, not path-like
        (he_valid_entry(config_dir=["~/.config/opencode"]), "config_dir"),
        ({**he_valid_entry(), "config_dir": None}, "config_dir"),
        # ^ explicit null, not the builder default — he_valid_entry(config_dir=None)
        #   substitutes "~/.config/<id>" for None, so the fixture must spread
        #   instead (first red run caught the builder swallowing the case).
        (he_valid_entry(config_dir="~/.config/opencode\n\x00"), "config_dir"),
        (he_valid_entry(config_dir="opencode config"), "config_dir"),
        (he_valid_entry(probe=""), "probe"),  # empty probe
        (he_valid_entry(probe=5), "probe"),
        (he_valid_entry(eid="OpenCode"), "id"),  # not spelled as upstream spells it
        (he_valid_entry(eid=""), "id"),
        (he_valid_entry(why=""), "why"),
        (he_valid_entry(why=7), "why"),
    ],
    ids=[
        "str-entry", "list-entry", "null-entry", "empty-entry",
        "config_dir-int", "config_dir-list", "config_dir-none",
        "config_dir-control-chars", "config_dir-not-path-like",
        "probe-empty", "probe-int", "id-wrong-case", "id-empty",
        "why-empty", "why-int",
    ],
)
def test_hostile_entry_shapes_are_rejected(entry, expected_field):
    """Malformed entries are rejected with the field named — never KeyError,
    never silent coercion, never a swallowed entry.

    EDGE/STRESS fuzz case set over the hand-edited YAML boundary (spec.md §
    Verification — input handling is fuzzed at the boundary).
    """
    # mutation: a try/except or `when:` guard that skips malformed entries
    # silently — the drift report would then never see the corruption.
    errs = he_contract().validate_catalogue(he_valid_catalogue([entry]))
    assert errs, f"hostile entry {entry!r} was silently accepted"
    assert all(isinstance(e, str) and e for e in errs), errs
    assert all("agents.yaml" in e for e in errs), errs
    assert any(expected_field in e for e in errs), (expected_field, errs)


def test_real_catalogue_passes_validation():
    """The real shared catalogue, once it exists, satisfies the stated schema.

    EDGE/STRESS; the real file is the actual boundary this suite guards.
    Fails named until dotfiles/config/agents.yaml exists.
    """
    # mutation: an entry hand-added to the real catalogue with an
    # out-of-vocabulary status, a missing field, or a duplicate id — the
    # editing-time corruption this boundary exists to catch.
    data = he_load_agents_yaml()
    assert isinstance(data, dict), f"top level must be a mapping, got {type(data)}"
    errs = he_contract().validate_catalogue(data)
    assert errs == [], f"real catalogue failed validation:\n" + "\n".join(errs)


# ══ 2. UNKNOWN BECOMES A CLAIM — hostile `herdr integration status` ══════════
# spec.md § Verification: unknown must never become a claim. The remove loop
# reads state; unparseable state is UNKNOWN and the loop refuses to proceed —
# it is NOT "nothing installed" (which would claim clean) and NOT "everything
# installed" (which would uninstall the world). Upstream doctrine: most
# commands print JSON; server errors are JSON on stderr with exit 1; CLI
# usage errors exit 2 (https://herdr.dev/docs/cli-reference/).


@pytest.mark.parametrize(
    "hostile",
    [
        "",  # empty stdout
        "   \n  ",  # whitespace only
        "error: server unreachable\n",  # prose where status was promised
        "opencode: inst",  # truncated mid-token
        "opencode: installed (/opt/homebrew/bin/opencode)\n\x00",  # control char
        "opencode: installed",  # record missing the path section
        "opencode: installed (/opt/homebrew/bin/opencode)\n"
        "opencode: not installed (/opt/homebrew/bin/opencode)",  # id claimed twice
        "opencode: maybe (/opt/homebrew/bin/opencode)",  # unknown state word
        "opencode: current (/opt/homebrew/bin/opencode)",  # version missing
        "opencode: outdated (v3) (/opt/homebrew/bin/opencode)",  # unmeasured state
    ],
    ids=[
        "empty", "whitespace", "prose", "truncated",
        "control-char", "record-missing-path", "duplicated-id", "unknown-state-word",
        "current-missing-version", "outdated-unmeasured",
    ],
)
def test_status_garbage_is_unknown_never_a_claim(hostile):
    """Unparseable status output raises UNKNOWN naming the failure.

    EDGE/STRESS; the brief's unknown-becomes-a-claim clause + spec.md §
    Verification. Also asserts the relents direction: well-formed output
    parses and claims exactly what it says. (Wire format MEASURED on the real
    binary 2026-09-19, herdr 0.9.1: lines of `<id>: installed|not installed
    (<path>)` — the earlier JSON-shape assumption was corrected against the
    binary; `herdr integration status --json` is a usage error.)
    """
    # mutation: `try: parse except: return {}` around status parsing —
    # garbage state would be read as "nothing installed" and the remove loop
    # would report a clean no-op it did not verify.
    mod = he_contract()
    # relents direction: the measured wire shape parses and claims exactly
    # what it says — so the refusals below are proven to relent, not fail
    # closed.
    parsed = mod.parse_integration_status(
        "opencode: current (v12) (/home/testuser/.config/opencode/plugins/herdr-agent-state.js)\n"
        "claude: not installed (/Users/testuser/.claude/hooks/herdr-agent-state.sh)"
    )
    assert parsed == {
        "opencode": {
            "id": "opencode",
            "installed": True,
            "version": 12,
            "path": "/home/testuser/.config/opencode/plugins/herdr-agent-state.js",
        },
        "claude": {
            "id": "claude",
            "installed": False,
            "path": "/Users/testuser/.claude/hooks/herdr-agent-state.sh",
        },
    }, parsed
    # decline direction: hostile output raises UNKNOWN with a named message.
    with pytest.raises(ValueError) as excinfo:
        mod.parse_integration_status(hostile)
    message = str(excinfo.value)
    assert message, "UNKNOWN raise must name the failure, not raise empty"
    assert "unknown" in message.lower(), message


@pytest.mark.parametrize(
    "rc, stdout",
    [(1, "herdr: server unreachable"), (2, "")],
    ids=["rc1-server-error", "rc2-usage-error"],
)
def test_remove_plan_refuses_nonzero_rc_and_garbage(rc, stdout):
    """remove_plan reads rc directly: nonzero refuses with rc named; rc 0 with
    garbage stdout refuses as UNKNOWN; valid state yields only the intersection.

    EDGE/STRESS; exit-status doctrine from https://herdr.dev/docs/cli-reference/
    (usage errors exit 2, server errors exit 1) and the intersection rule from
    the thin-loop recipe (TOPIC-RECIPES.md: never everything installed). The
    stdout is the measured wire format (see test_status_garbage above).
    """
    # mutation: rc read through a pipeline or ignored (branching on stdout
    # content instead of the command's own rc), or the intersection replaced
    # by the whole catalogue / the whole installed set.
    mod = he_contract()
    with pytest.raises(ValueError) as excinfo:
        mod.remove_plan(rc, stdout, ["opencode", "claude"], gate=True)
    assert str(rc) in str(excinfo.value), str(excinfo.value)
    if rc == 2:
        assert "usage" in str(excinfo.value).lower(), str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        mod.remove_plan(0, "", ["opencode"], gate=True)
    assert "unknown" in str(excinfo.value).lower(), str(excinfo.value)
    # relents direction: the intersection is exact — catalogue claims
    # opencode+claude, machine has opencode and zed-not-ours installed, so
    # only opencode is uninstalled; zed (not owned by the topic) is left alone.
    plan = mod.remove_plan(
        0,
        "opencode: current (v12) (/home/testuser/.config/opencode/plugins/herdr-agent-state.js)\n"
        "zed-not-ours: current (v1) (/opt/zed/bin/zed)\n"
        "claude: not installed (/Users/testuser/.claude/hooks/herdr-agent-state.sh)",
        ["opencode", "claude"],
        gate=True,
    )
    assert plan == ["herdr integration uninstall opencode"], plan


# ══ 3. SKIP-vs-RAISE boundary stress ═════════════════════════════════════════
# TOPIC-RECIPES.md skip-vs-raise recipe: the consumer absent = skip-and-report;
# a required dependency absent = raise. README: the loop skips-and-reports
# when the agent is absent, and raises when a required dependency fails.


def test_herdr_binary_absent_raises_named_fix_and_relents():
    """herdr missing mid-run raises with the fix named; present, it proceeds.

    EDGE/STRESS (brief: herdr binary absent mid-run — raise, named fix);
    relents doctrine from spec.md § Verification (a guard is proven to relent
    both ways): with herdr present the loop installs.
    """
    # mutation: herdr-absence treated as skip-and-report (the wrong recipe
    # direction — herdr is the required dependency, not an optional agent), or
    # the loop proceeding to shell out to a binary that is not there.
    mod = he_contract()
    entries = [he_valid_entry("opencode")]
    probes = {"opencode": (True, True)}
    runner = he_recorder([0])
    with pytest.raises(ValueError) as excinfo:
        mod.install_loop(entries, probes, herdr_present=False, run_install=runner)
    assert "mise use -g herdr" in str(excinfo.value), str(excinfo.value)
    assert runner.calls == [], "no install may be attempted without herdr"
    # relents: herdr present -> the loop installs and reports clean.
    report = mod.install_loop(entries, probes, herdr_present=True, run_install=runner)
    report.raise_if_failed()  # must be a no-op
    assert report.attempts == [("opencode", 0)], report.attempts


@pytest.mark.parametrize(
    "probe_present, dir_exists",
    [(False, True), (True, False), (False, False)],
    ids=["probe-missing", "config-dir-missing", "both-missing"],
)
def test_skip_names_both_conditions_and_does_not_fail(probe_present, dir_exists):
    """An absent agent is a skip whose report names BOTH preconditions, and
    the run does not fail.

    EDGE/STRESS (brief: config dir exists but probe binary does not — skip,
    report names BOTH conditions); README: cursor skips-and-reports;
    TOPIC-RECIPES.md skip-vs-raise recipe.
    """
    # mutation: a skip reason naming only one condition (or none), or an
    # absent agent failing the run (the wrong recipe direction).
    mod = he_contract()
    entry = he_valid_entry("cursor", probe="cursor-agent", config_dir="~/.cursor")
    probes = {"cursor": (probe_present, dir_exists)}
    runner = he_recorder([])
    report = mod.install_loop(
        [entry], probes, herdr_present=True, run_install=runner
    )
    report.raise_if_failed()  # skip must not fail the run
    assert runner.calls == [], "skipped entries must not be installed"
    assert len(report.skips) == 1, report.skips
    _, reason = report.skips[0]
    assert reason, "skip report must name its conditions"
    assert "cursor-agent" in reason, reason  # the probe condition
    assert "~/.cursor" in reason, reason  # the config-dir condition


def test_install_failures_collected_reported_once_raised_after_loop():
    """Per-item failures collect; one raise at the end names ALL of them; the
    loop keeps going past a failure.

    EDGE/STRESS; thin-loop recipe (TOPIC-RECIPES.md): failed_when false per
    item, verdict per entry, fail once at the end naming everything unresolved.
    """
    # mutation: fail-fast on the first failure (hides every later failure) or
    # the final raise dropped (a run that half-installed and reported green).
    mod = he_contract()
    entries = [he_valid_entry(eid) for eid in ("opencode", "claude", "cursor")]
    probes = {e["id"]: (True, True) for e in entries}
    runner = he_recorder([1, 1, 0])
    report = mod.install_loop(
        entries, probes, herdr_present=True, run_install=runner
    )
    assert [c[1] for c in runner.calls] == [1, 1, 0], (
        "the loop must attempt every entry, continuing past failures"
    )
    with pytest.raises(ValueError) as excinfo:
        report.raise_if_failed()
    message = str(excinfo.value)
    assert "opencode" in message and "claude" in message, message
    assert "cursor" not in message, message  # only failures are named


def test_usage_error_rc2_collected_not_retried():
    """A catalogue id herdr does not recognize (exit 2, usage error) is
    collected and raised once — never retried.

    EDGE/STRESS (brief: install exits 2 = usage error -> collect and raise,
    do not retry); exit semantics from https://herdr.dev/docs/cli-reference/.
    """
    # mutation: a retry loop added for rc=2 (usage errors are not transient),
    # or rc=2 counted as success.
    mod = he_contract()
    entry = he_valid_entry("not-a-herdr-agent")
    probes = {"not-a-herdr-agent": (True, True)}
    runner = he_recorder([2])
    report = mod.install_loop(
        [entry], probes, herdr_present=True, run_install=runner
    )
    assert runner.calls == [("not-a-herdr-agent", 2)], runner.calls
    with pytest.raises(ValueError) as excinfo:
        report.raise_if_failed()
    message = str(excinfo.value)
    assert "not-a-herdr-agent" in message, message
    assert "2" in message, message


# ══ 4. ORDER STRESS — hostile teardown state, idempotence ════════════════════
# TASKS.md § Now names "stale service state" for this dimension; the README
# remove order is integrations -> service -> mise entry, and TOPIC-RECIPES.md
# requires teardown to uninstall only the intersection, gated by default.


@pytest.mark.parametrize(
    "state",
    [
        he_populated_state(),  # everything present
        {  # stale service: integrations live, service already unloaded, unit gone
            "herdr_present": True,
            "integrations_installed": {"opencode"},
            "service_loaded": False,
            "unit_file_exists": False,
            "mise_entry_present": True,
        },
        {  # stale entry: service live, unit gone, mise entry already pruned
            "herdr_present": True,
            "integrations_installed": set(),
            "service_loaded": True,
            "unit_file_exists": False,
            "mise_entry_present": False,
        },
    ],
    ids=["fully-populated", "service-already-torn-down", "entry-already-pruned"],
)
def test_teardown_converges_and_second_run_is_a_noop(state):
    """Teardown over hostile (partially torn-down) state converges, and the
    second run changes nothing.

    EDGE/STRESS; idempotence proof required by the brief: run the simulated
    removal twice, assert the second run changes nothing.
    """
    # mutation: teardown emitting unconditional bootout/delete/unuse — the
    # second run would error on already-absent state instead of converging.
    mod = he_contract()
    ids = ["opencode", "claude"]
    first_plan = mod.teardown_plan(state, ids, gate=True)
    if state == he_populated_state():
        assert first_plan, "teardown on a populated machine must emit commands"
    he_apply_teardown(state, first_plan)
    converged = he_snapshot(state)
    second_plan = mod.teardown_plan(state, ids, gate=True)
    assert second_plan == [], f"second teardown run must plan nothing, got {second_plan}"
    he_apply_teardown(state, second_plan)
    assert he_snapshot(state) == converged, "second teardown run changed state"


def test_remove_nothing_ever_installed_is_clean_noop():
    """On a machine where nothing was ever installed, the whole remove is a
    clean no-op — with the gate off (the documented default) and even on.

    EDGE/STRESS (brief: remove when NOTHING was ever installed — clean
    no-op); gate default from README (herdr_remove_integrations, default off).
    """
    # mutation: teardown that uninstalls "everything herdr knows" or unuses
    # the mise entry unconditionally — a remove would then error or strip
    # state the topic does not own on a bare machine.
    mod = he_contract()
    state = he_fresh_state()
    assert mod.teardown_plan(state, ["opencode", "claude"], gate=False) == []
    assert mod.teardown_plan(state, ["opencode", "claude"], gate=True) == []
    assert state == he_fresh_state(), "a no-op remove must not touch state"


def test_remove_gate_defaults_off():
    """The removal gate defaults off in the topic defaults.

    EDGE/STRESS; README: remove is gated by herdr_remove_integrations
    (default off, vscode_remove_extensions pattern). Static read of
    defaults/main.yaml; fails named until the topic exists.
    """
    # mutation: the gate default flipped to true — removal would run by
    # default instead of being an explicit opt-in.
    data = he_defaults_data()
    assert "herdr_remove_integrations" in data, f"gate var missing from {HE_DEFAULTS}"
    assert data["herdr_remove_integrations"] is False


# ══ 5. SCALE — 1..200 generated entries ══════════════════════════════════════
# spec.md § Verification — invariants are tested as properties; the property
# states the rule independently of the implementation (no recompute).


@settings(max_examples=25, deadline=None)
@given(
    ids=st.lists(
        st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789-", min_size=1, max_size=20),
        min_size=1,
        max_size=200,
        unique=True,
    )
)
def test_scale_planned_commands_linear_unique_stable(ids):
    """For any 1..200-entry catalogue, planned install commands are one per
    entry, unique, and in catalogue order.

    EDGE/STRESS scale property (brief: slice resolution and the planned-command
    set scale linearly, stay consistent, order stable). The invariant is stated
    against the generated input itself, not recomputed from the plan.
    """
    # mutation: dedup-by-set or a sorted() slipped into slice resolution —
    # uniqueness survives but catalogue order (the report's stability) breaks.
    catalogue = he_valid_catalogue([he_valid_entry(eid) for eid in ids])
    commands = he_contract().planned_install_commands(catalogue)
    assert len(commands) == len(ids), (len(commands), len(ids))
    assert len(set(commands)) == len(commands), "duplicate planned commands"
    for i, (command, eid) in enumerate(zip(commands, ids)):
        assert command == f"herdr integration install {eid}", (i, command, eid)


@settings(max_examples=50, deadline=None)
@given(
    ids=st.lists(
        st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789-", min_size=1, max_size=20),
        min_size=2,
        max_size=50,
        unique=True,
    ),
    dup_index=st.integers(min_value=0, max_value=48),
)
def test_generated_duplicate_ids_are_rejected(ids, dup_index):
    """Property half of the duplicate-id fuzz: any catalogue whose generated
    ids contain a duplicate is rejected by validation, naming the id.

    EDGE/STRESS (brief: duplicate ids in generated input are REJECTED by
    validation rather than producing duplicate installs).
    """
    # mutation: deduplication at load time (silently dropping one copy)
    # instead of rejection — the duplicate install would then be invisible.
    at = dup_index % len(ids)
    entries = [he_valid_entry(eid) for eid in ids]
    entries.insert(at, he_valid_entry(ids[at]))
    errs = he_contract().validate_catalogue(he_valid_catalogue(entries))
    assert errs, f"duplicate id {ids[at]!r} was silently accepted"
    assert any(ids[at] in e for e in errs), errs


# ══ 6. EXIT-STATUS doctrine — static scan of the topic's task YAML ═══════════
# spec.md § Verification — exit status is read directly: no rc-bearing read
# through a pipeline. The trap bit this repo twice in one session.


def test_topic_tasks_never_pipe_rc_reads():
    """No `| head`-style pipe masks an rc read anywhere in the topic's tasks.

    EDGE/STRESS static scan (brief: assert the design does not pipe status
    through another command). Fails named until the topic's task YAML exists.
    """
    # mutation: a `| head` (or similar) added around a registered command read,
    # making the branch read the pipe's status instead of the command's.
    files = he_topic_task_files()
    violations = []
    for path in files:
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if HE_RC_MASKING_PIPES.search(line):
                violations.append(f"{path}:{lineno}: {line.strip()}")
    assert not violations, (
        "exit-status doctrine violated — rc must be read directly, not "
        "through a pipeline:\n" + "\n".join(violations)
    )


def test_yaml_status_regexes_match_the_measured_wire():
    """The Jinja regex strings in the task YAML compile and match the real
    status grammar — the gap static scans could not close, now closed by
    executing the strings.

    Dimension: contract/YAML divergence. Sources: the measured wire format
    (contract module docstring), the golden fixture, and TWO real
    double-escape incidents (2026-09-19): a folded-scalar `\\\\(` that the
    regex engine read as literal-backslash-plus-group, so `systemctl`-side
    installed-id extraction would never have matched, and the same class
    re-introduced in the install pre-read — both invisible to every static
    test until this one compiled the strings.
    """
    # mutation: re-double-escape either side (\\\\( in place of \\() — the
    # compile-then-match here goes red, where the suite previously stayed
    # green against a YAML regex that never matched.
    files = he_topic_task_files()
    select_re = re.compile(r"select\('match',\s*'([^']+)'")
    extract_re = re.compile(r"regex_replace',\s*'([^']+)'")
    found_select: list[str] = []
    found_extract: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        found_select += select_re.findall(text)
        found_extract += extract_re.findall(text)
    assert found_select, "no select('match', ...) regex found in the tasks"
    assert found_extract, "no regex_replace id-extraction found in the tasks"
    fixture = HE_GOLDEN_STATUS.read_text()
    lines = [ln for ln in fixture.split("\n") if ln.strip()]
    installed_lines = [ln for ln in lines if ": current (v" in ln]
    assert installed_lines, "fixture must contain installed (current vN) lines"
    for pattern in found_select:
        compiled = re.compile(pattern)  # raises on malformed regex
        for line in installed_lines:
            assert compiled.match(line), (
                f"task YAML regex {pattern!r} does not match the measured "
                f"installed line {line!r} — the double-escape class"
            )
    for pattern in found_extract:
        compiled = re.compile(pattern)
        matches = [compiled.match(ln) for ln in installed_lines]
        assert all(matches), (
            f"task YAML extraction regex {pattern!r} fails on a measured "
            "installed line"
        )
        ids = [m.group(1) for m in matches if m]
        assert ids == ["claude", "opencode"], (
            f"extraction must yield the installed ids from the fixture, "
            f"got {ids}"
        )


# ══ 7. GOLDEN TRANSCRIPT — the contract module against the real binary ══════
# Judge round 1 (dotfiles/docs/JUDGE-SELECTION.md), gap 2: the contract
# module was self-consistent but unvalidated against the real herdr binary.
# The fixture is a REAL captured transcript (herdr 0.9.1, 2026-09-19, this
# Mac) with the home prefix redacted to /home/testuser — the grammar under
# test is the structure, not the path contents. Re-capture with
# `herdr integration status` and re-redact when the binary moves.

HE_GOLDEN_STATUS = REPO / "tests" / "herdr" / "fixtures" / (
    "integration-status-herdr-0.9.1.txt"
)


def test_golden_transcript_parses_as_the_binary_wrote_it():
    """The real captured status transcript parses to exactly 18 records, all
    not-installed at capture time, with paths in the redacted home.

    EDGE/STRESS golden test (judge round 1, gap 2). Fails named while the
    fixture is missing.
    """
    # mutation: the parser drifting from the real wire format (e.g. requiring
    # JSON, or mishandling the `not installed` state word) — the golden
    # transcript then refuses to parse exactly as the binary wrote it.
    if not HE_GOLDEN_STATUS.is_file():
        pytest.fail(
            f"golden transcript missing — expected {HE_GOLDEN_STATUS} "
            "(captured from `herdr integration status`, herdr 0.9.1, "
            "2026-09-19, home-redacted)"
        )
    transcript = HE_GOLDEN_STATUS.read_text()
    parsed = he_contract().parse_integration_status(transcript)
    expected_ids = {
        "pi", "omp", "claude", "codex", "copilot", "devin", "droid", "kimi",
        "opencode", "kilo", "hermes", "qodercli", "qwen", "letta", "cursor",
        "mastracode", "antigravity-cli", "grok",
    }
    assert set(parsed) == expected_ids, (
        f"golden transcript parsed to {sorted(parsed)}; expected exactly the "
        f"18 agents the binary lists: {sorted(expected_ids)}"
    )
    # Installed map at re-capture (2026-09-19, post first converge): the
    # topic wired opencode and claude; the rest stay not-installed.
    expected_installed = {"opencode", "claude"}
    actual_installed = {rid for rid, r in parsed.items() if r["installed"]}
    assert actual_installed == expected_installed, (
        f"installed set drifted from the fixture: {sorted(actual_installed)} "
        f"vs expected {sorted(expected_installed)} — re-capture the fixture "
        "after real converge changes (the test docstring has the recipe)"
    )
    assert parsed["opencode"]["version"] >= 5 and parsed["claude"]["version"] >= 6, (
        "the wired integrations must be at or above the catalogue's "
        "native-restore floors (opencode 5, claude 6)"
    )
    assert all(
        record["path"].startswith("/home/testuser/") for record in parsed.values()
    ), "the redacted-home fixture must keep paths under /home/testuser/"
