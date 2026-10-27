"""The machine-local decision store.

`~/.config/skill-trust/trust.yaml` holds decisions a human made when the
resolver asked: sources they approved or denied, skills they denied or
vendored, hidden directories they want audited. It is never versioned —
per-machine decisions stay on the machine, the same split `bin/policy` makes
with its machine-local layer in `~/.local/state/ai-policy`.

The store is layered UNDER the repo-composed rules (`decide.layer_configs`):
deny wins across layers, so a store approval can never overturn a repo ban,
while a store denial can tighten a repo approval.

An ABSENT store is normal — nobody has decided anything yet — and reads as
empty. A PRESENT but malformed store is a hand-edited file in the expected
state of being edited, so it errors loudly with the file, kind and entry
named rather than reading as "no decisions".
"""

from __future__ import annotations

import datetime
import os
import pathlib

import yaml

# os is imported (not `from os import replace`) so tests can monkeypatch
# os.replace and watch the failure path of an atomic save.


class StoreError(Exception):
    """A store file that could not be read. Distinct from an absent store on
    purpose: a mistyped key must not read as "no decisions".
    """


# Kinds a store entry can belong to, and the field that carries the value the
# rule matches on. `exclude` is the odd one: its entries name a source AND a
# skill, so it is normalised into the {source: [names]} shape decide() reads.
KIND_KEYS = {
    "approved_sources": "source",
    "deny_sources": "source",
    "deny_skills": "name",
    "vendored": "name",
    "include_hidden": "name",
    "exclude": None,
}

_ENTRY_META = {"why", "decided"}


def default_config_dir() -> pathlib.Path:
    """`$XDG_CONFIG_HOME/skill-trust`, falling back to `~/.config`."""
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = pathlib.Path(xdg) if xdg else pathlib.Path.home() / ".config"
    return base / "skill-trust"


def default_store_path() -> pathlib.Path:
    return default_config_dir() / "trust.yaml"


def default_rules_path() -> pathlib.Path:
    """Where the Ansible guard writes the repo-composed rules each run, so a
    standalone `skill-trust resolve` judges with exactly what the guard
    enforces. Generated, not user-edited — the guard overwrites it.
    """
    return default_config_dir() / "rules.yaml"


def today() -> str:
    return datetime.date.today().isoformat()


def _normalise_entry(kind: str, raw: object, path: pathlib.Path, index: int) -> dict:
    """One entry to {value-field, why?, decided?}, or a StoreError naming it."""
    where = f"{path}: {kind}[{index}]"
    key = KIND_KEYS[kind]
    if isinstance(raw, str):
        if kind == "exclude":
            raise StoreError(f"{where}: exclude entries need a source and a name")
        return {key: raw}
    if not isinstance(raw, dict):
        raise StoreError(f"{where}: must be a mapping or a bare string")
    unknown = set(raw) - _ENTRY_META - ({key} if key else {"source", "name"})
    if unknown:
        raise StoreError(f"{where}: unknown field(s) {sorted(unknown)}")
    # YAML reads an unquoted date as datetime.date; keep everything strings so
    # read/write round-trips are stable.
    meta = {
        m: (raw[m].isoformat() if isinstance(raw[m], datetime.date) else raw[m])
        for m in _ENTRY_META
        if m in raw
    }
    if kind == "exclude":
        if not raw.get("source") or not raw.get("name"):
            raise StoreError(f"{where}: exclude entries need a source and a name")
        return {"source": raw["source"], "name": raw["name"], **meta}
    if not raw.get(key):
        raise StoreError(f'{where}: missing "{key}"')
    return {key: raw[key], **meta}


def read_store(path: pathlib.Path) -> dict[str, list[dict]]:
    """The store as {kind: [entry, ...]}. Absent means empty, never an error."""
    if not path.is_file():
        return {}
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise StoreError(f"unreadable store {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise StoreError(f"store must be a mapping: {path}")
    unknown = set(loaded) - set(KIND_KEYS)
    if unknown:
        raise StoreError(
            f"{path}: unknown kind(s) {sorted(unknown)}; "
            f"valid kinds are {sorted(KIND_KEYS)}"
        )
    store: dict[str, list[dict]] = {}
    for kind, entries in loaded.items():
        if not isinstance(entries, list):
            raise StoreError(f"{path}: {kind} must be a list")
        store[kind] = [
            _normalise_entry(kind, raw, path, i) for i, raw in enumerate(entries)
        ]
    return store


def normalised(store: dict[str, list[dict]]) -> dict:
    """The decide()-shaped config fragment: bare value lists, exclude as
    {source: [names]}. This is what `layer_configs` merges under the repo
    rules — the why/decided metadata is for humans and stays in the file.
    """
    out: dict = {}
    for kind, key in KIND_KEYS.items():
        entries = store.get(kind) or []
        if kind == "exclude":
            merged: dict[str, list[str]] = {}
            for entry in entries:
                merged.setdefault(entry["source"], []).append(entry["name"])
            if merged:
                out["exclude"] = merged
        elif entries:
            out[kind] = [entry[key] for entry in entries]
    return out


def add_entry(
    store: dict[str, list[dict]],
    kind: str,
    *,
    why: str,
    decided: str | None = None,
    source: str | None = None,
    name: str | None = None,
) -> dict[str, list[dict]]:
    """Append one decision. Pure: returns the updated store, writes nothing.

    A repeated value replaces the old entry rather than duplicating — the
    store is a set of decisions, and two entries for one value is a
    disagreement nothing resolves.
    """
    if kind not in KIND_KEYS:
        raise StoreError(f"unknown kind {kind!r}; valid kinds are {sorted(KIND_KEYS)}")
    if not why.strip():
        raise StoreError("a decision needs a why — a reason a human can check")
    entry: dict = {"why": why.strip(), "decided": decided or today()}
    if kind == "exclude":
        if not source or not name:
            raise StoreError("exclude entries need a source and a name")
        entry = {"source": source, "name": name, **entry}
        match = lambda e: e["source"] == source and e["name"] == name  # noqa: E731
    else:
        key = KIND_KEYS[kind]
        value = source if key == "source" else name
        if not value:
            raise StoreError(f'{kind} entries need a "{key}"')
        entry = {key: value, **entry}
        match = lambda e: e[key] == value  # noqa: E731
    kept = [e for e in store.get(kind, []) if not match(e)]
    return {**store, kind: [*kept, entry]}


def remove_entry(
    store: dict[str, list[dict]], kind: str, value: str
) -> tuple[dict[str, list[dict]], bool]:
    """Drop every entry under `kind` matching `value`. Returns the store and
    whether anything was removed — a remove that matched nothing must say so,
    or a typo reads as a decision retracted.
    """
    if kind not in KIND_KEYS:
        raise StoreError(f"unknown kind {kind!r}; valid kinds are {sorted(KIND_KEYS)}")
    entries = store.get(kind, [])
    if kind == "exclude":
        kept = [e for e in entries if e["source"] != value and e["name"] != value]
    else:
        key = KIND_KEYS[kind]
        kept = [e for e in entries if e[key] != value]
    removed = len(kept) != len(entries)
    return {**store, kind: kept}, removed


def save_store(path: pathlib.Path, store: dict[str, list[dict]]) -> None:
    """Write the store, 0700 dir / 0600 file, ATOMICALLY: temp sibling plus
    os.replace, so an interrupt mid-write can never replace a valid store
    with a truncated one — every later run would read that as a corrupt
    store and error (roborev job 16, finding 3). Kinds in a fixed order so
    the file diffs calmly between decisions.
    """
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    ordered = {kind: store[kind] for kind in KIND_KEYS if store.get(kind)}
    body = yaml.safe_dump(ordered, sort_keys=False, allow_unicode=True)
    header = (
        "# Machine-local skill trust decisions — never versioned.\n"
        "# Written by `skill-trust resolve` / `skill-trust trust`; hand edits are\n"
        "# read strictly (an unknown field or kind is an error, not a skip).\n"
    )
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        tmp.write_text(header + body, encoding="utf-8")
        tmp.chmod(0o600)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)
