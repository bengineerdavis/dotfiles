"""Executable contract for the herdr catalogue + integration loop (spec-as-code).

The herdr topic's runtime behaviour lives in Ansible YAML, which pytest cannot
execute. This module is the pure-Python statement of that behaviour's CONTRACT,
authored against tests/herdr/test_edge_stress.py (which imports it) and the
written artifacts:

- dotfiles/apps/herdr/README.md — the design record
- docs/TOPIC-RECIPES.md — shared-catalogue + skip-vs-raise recipes
- spec.md § Verification — unknown never becomes a claim; relents both ways
- https://herdr.dev/docs/cli-reference/ — exit statuses (server errors exit 1,
  usage errors exit 2; most commands print JSON)

It is NOT a copy of the task YAML. tests/herdr/test_lifecycle_contract.py and
test_user_acceptance.py pin the YAML to the same rules statically, so a
divergence between the YAML and this module fails somewhere. Wire-shape
ASSUMPTIONS are marked inline (search "ASSUMPTION").

No side effects, no I/O, no subprocess — everything is simulated by callers.
"""

from __future__ import annotations

import re
import string  # noqa: F401  (kept for future generators; harmless)

# ── the contract's own vocabulary ────────────────────────────────────────────

# Verdict statuses, from the cited precedent dotfiles/config/editors.yaml.
KNOWN_STATUSES = frozenset({"ok", "not-available", "substituted"})

# herdr integration ids are non-empty lowercase alphanumerics and hyphens.
# Upstream ids happen to be letter-lead (pi, omp, claude, opencode,
# antigravity-cli), but the scale property in test_edge_stress.py generates
# ids from the full lowercase-alnum-hyphen alphabet and its invariant — one
# planned command per entry — must hold for every generated id, so the format
# check stays at the alphabet level: it still rejects uppercase, empties,
# whitespace and separators.
ID_RE = re.compile(r"^[a-z0-9-]+$")

# Control characters (never legitimate in hand-edited YAML values).
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

REQUIRED_FIELDS = ("id", "why", "probe", "config_dir")


class StatusUnknownError(ValueError):
    """Unparseable machine state — unknown must never become a claim."""

    def __init__(self, message: str):
        super().__init__(f"unknown integration state: {message}")


class CatalogueInvalidError(ValueError):
    """The catalogue failed validation; the message names every error."""


# ── catalogue validation (TOTAL: never raises, never coerces) ────────────────


def validate_catalogue(data, source: str = "dotfiles/config/agents.yaml") -> list[str]:
    """Validate a parsed agents.yaml document. Returns human-readable errors,
    each naming the source file and the offending field (and entry id/index
    where an entry is involved). Empty list = valid. Never raises.
    """
    errors: list[str] = []

    def err(message: str) -> None:
        errors.append(f"{source}: {message}")

    if not isinstance(data, dict):
        err(f"top level must be a mapping, got {type(data).__name__}")
        return errors

    version = data.get("version")
    if version is not None and not isinstance(version, int):
        err(f"version must be an int, got {type(version).__name__}")

    entries = data.get("agent_integrations")
    if not isinstance(entries, list):
        err("`agent_integrations` must be a list, got " + type(entries).__name__)
        entries = []

    seen_ids: dict[str, int] = {}
    for index, entry in enumerate(entries):
        _validate_entry(
            entry,
            index,
            "agent_integrations",
            err,
            seen_ids,
            require_probe_and_dir=True,
        )

    ignored = data.get("agent_integrations_ignored")
    if not isinstance(ignored, list):
        err(
            "`agent_integrations_ignored` must be a list, got " + type(ignored).__name__
        )
        ignored = []
    for index, entry in enumerate(ignored):
        _validate_entry(
            entry,
            index,
            "agent_integrations_ignored",
            err,
            seen_ids,
            require_probe_and_dir=False,
        )

    return errors


def _validate_entry(
    entry, index, list_name, err, seen_ids, *, require_probe_and_dir: bool
) -> None:
    """Validate one catalogue entry; errors name the field, id and index."""
    where = f"{list_name}[{index}]"
    if not isinstance(entry, dict):
        err(
            f"{where} must be a mapping with an `id` field, got " + type(entry).__name__
        )
        return

    entry_id = entry.get("id")
    if entry_id is None:
        err(f"{where} is missing required field `id`")
    elif not isinstance(entry_id, str) or not ID_RE.fullmatch(entry_id):
        err(
            f"{where} field `id` must match {ID_RE.pattern} "
            f"(spelled as herdr spells it), got {entry_id!r}"
        )
        entry_id = None
    else:
        if entry_id in seen_ids:
            err(
                f"{where} field `id` duplicates id `{entry_id}` first seen at "
                f"{list_name}[{seen_ids[entry_id]}] — duplicate ids would "
                "double-install"
            )
        else:
            seen_ids[entry_id] = index

    why = entry.get("why")
    if why is None:
        err(f"{where} ({entry_id!r}) is missing required field `why`")
    elif not isinstance(why, str) or not why.strip():
        err(
            f"{where} ({entry_id!r}) field `why` must be a non-empty string, "
            f"got {why!r}"
        )

    checked = entry.get("checked")
    if checked is not None and not _is_iso_date(checked):
        err(
            f"{where} ({entry_id!r}) field `checked` must be an ISO date, "
            f"got {checked!r}"
        )

    if require_probe_and_dir:
        probe = entry.get("probe")
        if probe is None:
            err(f"{where} ({entry_id!r}) is missing required field `probe`")
        elif (
            not isinstance(probe, str)
            or not probe.strip()
            or "/" in probe
            or _CONTROL_RE.search(probe)
        ):
            err(
                f"{where} ({entry_id!r}) field `probe` must be a non-empty "
                f"binary NAME resolvable on PATH (no separators), got {probe!r}"
            )

        config_dir = entry.get("config_dir")
        if config_dir is None:
            err(f"{where} ({entry_id!r}) is missing required field `config_dir`")
        elif (
            not isinstance(config_dir, str)
            or not config_dir.startswith("~/")
            or _CONTROL_RE.search(config_dir)
        ):
            err(
                f"{where} ({entry_id!r}) field `config_dir` must be a "
                f"home-relative path starting with `~/`, got {config_dir!r}"
            )

        kind = entry.get("kind")
        if kind is not None and kind not in ("lifecycle", "session"):
            err(
                f"{where} ({entry_id!r}) field `kind` must be lifecycle or "
                f"session, got {kind!r}"
            )

        topics = entry.get("topics")
        if topics is not None and (
            not isinstance(topics, list) or not all(isinstance(t, str) for t in topics)
        ):
            err(
                f"{where} ({entry_id!r}) field `topics` must be a list of "
                f"subscriber names, got {topics!r}"
            )

        min_version = entry.get("min_version")
        if min_version is not None:
            if not isinstance(min_version, dict):
                err(
                    f"{where} ({entry_id!r}) field `min_version` must be a "
                    f"dated verdict mapping, got {min_version!r}"
                )
            else:
                ver = min_version.get("version")
                if not isinstance(ver, int) or isinstance(ver, bool) or ver < 1:
                    err(
                        f"{where} ({entry_id!r}) field `min_version.version` "
                        f"must be a positive int, got {ver!r}"
                    )
                checked_at = min_version.get("checked")
                if not _is_iso_date(checked_at):
                    err(
                        f"{where} ({entry_id!r}) field `min_version.checked` "
                        f"must be an ISO date, got {checked_at!r}"
                    )

    verdicts = entry.get("verdicts")
    if verdicts is not None:
        if not isinstance(verdicts, dict):
            err(
                f"{where} ({entry_id!r}) field `verdicts` must be a mapping "
                f"of consumer -> verdict, got {verdicts!r}"
            )
        else:
            for consumer, verdict in verdicts.items():
                if not isinstance(verdict, dict):
                    err(
                        f"{where} ({entry_id!r}) verdict for `{consumer}` "
                        f"must be a mapping, got {verdict!r}"
                    )
                    continue
                status = verdict.get("status")
                if status not in KNOWN_STATUSES:
                    err(
                        f"{where} ({entry_id!r}) verdict for `{consumer}` "
                        f"field `status` must be one of "
                        f"{sorted(KNOWN_STATUSES)}, got {status!r}"
                    )
                if not _is_iso_date(verdict.get("checked")):
                    err(
                        f"{where} ({entry_id!r}) verdict for `{consumer}` "
                        f"field `checked` must be an ISO date, got "
                        f"{verdict.get('checked')!r}"
                    )


def _is_iso_date(value) -> bool:
    return (
        isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is not None
    )


# ── planned install commands ────────────────────────────────────────────────


def planned_install_commands(
    data, source: str = "dotfiles/config/agents.yaml"
) -> list[str]:
    """One `herdr integration install <id>` per entry, catalogue order, no
    duplicates. Invalid input raises ValueError naming the validation errors.
    """
    errors = validate_catalogue(data, source)
    if errors:
        raise CatalogueInvalidError(
            f"{source} failed validation:\n" + "\n".join(errors)
        )
    return [
        f"herdr integration install {entry['id']}"
        for entry in data.get("agent_integrations", [])
        if isinstance(entry, dict) and entry.get("id")
    ]


# ── status parsing (unknown never becomes a claim) ───────────────────────────

# Wire format, MEASURED on the real binary 2026-09-19 (herdr 0.9.1; the
# upstream CLI-reference sentence "most commands print JSON" does not hold for
# this subcommand, and `herdr integration status --json` is a usage error).
# One line per agent; the state grammar grew with the first fixture refresh:
#
#     <id>: not installed (<expected path>)
#     <id>: current (v<int>) (<absolute path>)      [installed at/above floor]
#     <id> (experimental): not installed (<path>)   [measured: letta]
#
# (`outdated (vN)` is the presumed stale state behind --outdated-only; it has
# NOT been measured, so it is NOT in the grammar — unknown states refuse,
# which is fail-closed.) The status subcommand works without a running
# server (measured same day), which is what makes the remove-time state read
# possible. The annotation is accepted ONLY as exactly `(experimental)`.

_STATUS_LINE_RE = re.compile(
    r"^([a-z0-9-]+)(?: \(experimental\))?: "
    r"(not installed|current \(v(\d+)\)) "
    r"\((.+)\)$"
)


def parse_integration_status(text: str) -> dict[str, dict]:
    """Parse rc==0 stdout of `herdr integration status` into id -> record.

    Raises StatusUnknownError for empty/whitespace text, control characters,
    prose, truncated lines, lines outside the measured grammar, a state word
    other than `not installed`/`current (vN)`, an annotation other than
    (experimental), or an id claimed twice — never returns a partial claim.
    Records carry `installed` (True for `current (vN)`), `version` (int, when
    the state carries one), and `path`.
    """
    if not isinstance(text, str) or not text.strip():
        raise StatusUnknownError("empty status output")
    if _CONTROL_RE.search(text.replace("\n", "").replace("\r", "").replace("\t", "")):
        raise StatusUnknownError("control characters in status output")

    out: dict[str, dict] = {}
    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        match = _STATUS_LINE_RE.match(line)
        if not match:
            raise StatusUnknownError(
                f"unparseable status line (expected `<id>[( (experimental))]>: "
                f"not installed|current (vN) (<path>)`): {line!r}"
            )
        record_id = match.group(1)
        installed = match.group(2) != "not installed"
        version = int(match.group(3)) if match.group(3) else None
        path = match.group(4)
        record = {
            "id": record_id,
            "installed": installed,
            "path": path,
        }
        if version is not None:
            record["version"] = version
        if "(experimental)" in line:
            record["experimental"] = True
        if record_id in out:
            raise StatusUnknownError(f"status output claims id {record_id!r} twice")
        out[record_id] = record
    return out


# ── the install loop (skip-and-report; raise for the required dependency) ────


class InstallReport:
    """What the thin install-and-report loop accumulated."""

    def __init__(self):
        self.attempts: list[tuple[str, int]] = []
        self.skips: list[tuple[str, str]] = []

    def raise_if_failed(self) -> None:
        """Raise once, naming EVERY failed id and its rc; no-op when clean."""
        if not self.attempts:
            return
        failed = [(eid, rc) for eid, rc in self.attempts if rc != 0]
        if failed:
            detail = ", ".join(f"{eid} (rc {rc})" for eid, rc in failed)
            raise ValueError(
                "herdr integration install failed for: "
                f"{detail} — fix the named entries and re-run"
            )


def install_loop(entries, probes, *, herdr_present: bool, run_install) -> InstallReport:
    """The skip-vs-raise install loop.

    entries: validated catalogue entries (dicts with id/probe/config_dir).
    probes: id -> (probe_present, config_dir_exists).
    run_install: id -> rc, injected (the simulated command).

    Contract: without herdr the loop raises immediately, naming the fix
    (`mise use -g herdr`) and attempting nothing. Per entry, install runs only
    when the probe binary is present AND the config dir exists; otherwise the
    entry is skipped with a reason naming BOTH conditions (probe name and
    config dir). Failures are collected — the loop continues — and
    raise_if_failed() raises once at the end naming every failure. No retries.
    """
    report = InstallReport()
    if not herdr_present:
        raise ValueError(
            "herdr is not installed — fix: install it through mise "
            "(`mise use -g herdr`; the herdr topic owns the entry; never "
            "`herdr update` on a mise install)"
        )
    for entry in entries:
        entry_id = entry["id"]
        probe_name = entry["probe"]
        config_dir = entry["config_dir"]
        probe_present, config_dir_exists = probes.get(entry_id, (False, False))
        probe_state = "on PATH" if probe_present else "not on PATH"
        dir_state = "exists" if config_dir_exists else "does not exist"
        if probe_present and config_dir_exists:
            rc = run_install(entry_id)
            report.attempts.append((entry_id, rc))
        else:
            report.skips.append(
                (
                    entry_id,
                    f"skipped {entry_id} — probe `{probe_name}` {probe_state}; "
                    f"config dir {config_dir} {dir_state}",
                )
            )
    return report


# ── the gated intersection remove ───────────────────────────────────────────


def remove_plan(
    status_rc: int, status_stdout: str, catalogue_ids, *, gate: bool
) -> list[str]:
    """Plan the integration teardown from actual machine state.

    gate False -> [] (the documented default; status is not even consulted).
    rc != 0 -> ValueError naming the rc (2 is a usage error). rc 0 with
    unparseable stdout -> StatusUnknownError (refuse; never read as "nothing
    installed" nor as "everything installed"). Valid state -> one
    `herdr integration uninstall <id>` per INTERSECTION id, in catalogue
    order — never every installed id, never ids the topic does not own.
    """
    if not gate:
        return []
    if status_rc != 0:
        kind = "usage error" if status_rc == 2 else "error"
        raise ValueError(
            f"`herdr integration status` failed with rc {status_rc} ({kind}) "
            "— refusing to plan a remove from unknown state"
        )
    status = parse_integration_status(status_stdout)
    installed_ids = {rid for rid, record in status.items() if record["installed"]}
    claimed = list(catalogue_ids)
    return [
        f"herdr integration uninstall {entry_id}"
        for entry_id in claimed
        if entry_id in installed_ids
    ]


# ── the full teardown plan (idempotent, ordered, state-derived) ──────────────

LAUNCHD_LABEL = "com.herdr.server"
SYSTEMD_UNIT = "herdr-server.service"


def teardown_plan(state, catalogue_ids, *, gate: bool) -> list[tuple[str, str]]:
    """Ordered, state-derived teardown plan: integrations -> service -> entry.

    state keys: herdr_present, integrations_installed (set), service_loaded,
    unit_file_exists, mise_entry_present. Emits a command ONLY for state that
    is present (the idempotence source); a converged machine yields []. The
    gate covers ONLY integrations; the service unit and the mise entry are
    topic-owned regardless.
    """
    plan: list[tuple[str, str]] = []
    if gate and state.get("herdr_present"):
        for entry_id in catalogue_ids:
            if entry_id in state.get("integrations_installed", set()):
                plan.append(("integration_uninstall", entry_id))
    if state.get("service_loaded"):
        plan.append(("service_unload", LAUNCHD_LABEL))
    if state.get("unit_file_exists"):
        plan.append(("service_unit_delete", SYSTEMD_UNIT))
    if state.get("mise_entry_present"):
        plan.append(("mise_unuse", "herdr"))
    return plan
