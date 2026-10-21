"""Command line entry point.

Exit codes deliberately match `bin/policy`, because this answers the same shape
of question and a caller should not have to learn two vocabularies:

    0 PERMITTED   1 DENIED   2 UNKNOWN   3 ERROR
"""

from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import shutil
import sys

import yaml

# pyrefly: ignore [missing-import]
from .buckets import ForeignBucket, find_buckets

# pyrefly: ignore [missing-import]
from .decide import Decision, Verdict, decide, layer_configs

# pyrefly: ignore [missing-import]
from .discover import licence_from_dir, licence_from_repo

# pyrefly: ignore [missing-import]
from . import store as store_mod

PERMITTED, DENIED, UNKNOWN, ERROR = 0, 1, 2, 3


class ConfigError(Exception):
    """A rules file that could not be read. Distinct from a denial on purpose:
    "I could not tell you" and "I told you no" mean different things to a
    caller, and collapsing them lets a mistyped path read as a clean refusal.
    """


def require(*commands: str) -> None:
    """Report every missing dependency at once, then exit 127.

    Same contract as the shell guards in docs/TOPICS.md: one run names every gap
    rather than one per invocation, and 127 is the conventional
    command-not-found status.
    """
    missing = [c for c in commands if not shutil.which(c)]
    if missing:
        print(
            f"skill-trust: missing dependencies: {' '.join(missing)}", file=sys.stderr
        )
        raise SystemExit(127)


def load_config(path: pathlib.Path | None) -> dict:
    if path is None:
        return {}
    if not path.is_file():
        raise ConfigError(f"no such config: {path}")
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"unreadable config {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ConfigError(f"config must be a mapping: {path}")
    return loaded


def _judge(
    source: str,
    skill: str | None,
    config: dict,
    skill_dir: pathlib.Path | None,
    offline: bool,
) -> Decision:
    """Decide once without a licence, and only look one up if that was the
    level that would have decided it.
    """
    provisional = decide(source, skill, config, spdx=None)
    if provisional.rule != "default":
        return provisional
    spdx = licence_from_dir(skill_dir) if skill_dir else None
    if spdx is None and not offline:
        spdx = licence_from_repo(source)
    return decide(source, skill, config, spdx=spdx)


def _deny_rule_naming_bucket(config: dict, bucket_id: str) -> str | None:
    """A `deny_sources` pattern that names this bucket id exactly, or None.

    The id is the bucket's match key, so this compares on the id — never the
    alias — which is what keeps the alias a display-only label: renaming it
    cannot change what a rule approves or refuses.
    """
    for pattern in config.get("deny_sources") or []:
        if pattern.strip().lower() == bucket_id.lower():
            return pattern
    return None


def _external_line(bucket: ForeignBucket, config: dict, today: str) -> str:
    """The recorded `external` verdict: a date and a reason, not an absence.

    It asserts "not mine to rule on" — which is not "allowed" — and, when a
    deny rule names the bucket anyway, refuses to enforce it: deleting a synced
    skill only makes the sync recreate it byte-identical on the next session,
    so deny loops forever and is refused rather than attempted.
    """
    denial = _deny_rule_naming_bucket(config, bucket.id)
    if denial is not None:
        return (
            f"EXTERNAL [foreign_bucket] {bucket.id} ({bucket.alias}): a deny "
            f'rule names "{denial}", but deny is refused here. This bucket is '
            "owned by another program's sync, and deleting its skills only "
            "makes the sync recreate them byte-identical on the next session, "
            f"so the rule is inert and nothing is deleted. Observed {today}."
        )
    return (
        f"EXTERNAL [foreign_bucket] {bucket.id} ({bucket.alias}): not ours to "
        "rule on — a directory another program owns in the skills store, and "
        "denying it would loop forever, because a deleted synced skill is "
        f"recreated byte-identical next session. Observed {today}."
    )


def _load_layered(args) -> dict:
    """The repo rules with the machine-local store layered underneath.

    The store tightens or admits names; it cannot overturn a repo ban or touch
    licence policy — see decide.layer_configs.
    """
    base = load_config(args.config)
    overlay = store_mod.normalised(store_mod.read_store(args.store))
    return layer_configs(base, overlay)


def cmd_check(args) -> int:
    config = _load_layered(args)
    skill_dir = pathlib.Path(args.skill_dir) if args.skill_dir else None
    decision = _judge(args.source, args.skill, config, skill_dir, args.offline)
    marker = "PERMITTED" if decision.permitted else "DENIED"
    print(f"{marker} [{decision.rule}] {decision.reason}")
    return PERMITTED if decision.permitted else DENIED


def cmd_audit(args) -> int:
    """Judge every installed skill directory, not just the declared ones.

    The undeclared directory is the whole point: a tool that manages skills can
    say whether what it declared is present, but never whether something is
    present that it never declared.
    """
    config = _load_layered(args)
    root = pathlib.Path(args.skills_dir)
    if not root.is_dir():
        print(f"skill-trust: no such skills directory: {root}", file=sys.stderr)
        return ERROR

    declared: dict[str, str] = {}
    for entry in config.get("installed") or []:
        declared[entry["name"]] = entry["source"]
    # A manager's own inventory, piped in. Deliberately a JSON shape rather than
    # a call to any particular tool: `dotagents list --json` produces it today,
    # and anything that can emit {"skills":[{"name","source"}]} works tomorrow.
    if args.declared_json:
        raw = (
            sys.stdin.read()
            if args.declared_json == "-"
            else pathlib.Path(args.declared_json).read_text(encoding="utf-8")
        )
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"--declared-json is not JSON: {exc}") from exc
        for entry in payload.get("skills") or []:
            if entry.get("name") and entry.get("source"):
                declared[entry["name"]] = entry["source"]

    vendored = set(config.get("vendored") or [])
    include_hidden = set(config.get("include_hidden") or [])
    foreign = bool(config.get("foreign_buckets", True))
    buckets = find_buckets(root) if foreign else []
    bucket_ids = {b.id for b in buckets}
    today = datetime.date.today().isoformat()
    problems: list[tuple[str, Decision]] = []
    skipped_hidden: list[str] = []
    # Counted before the vendored skip on purpose: a directory whose skills are
    # all exempt is fully accounted for, not unexamined. Conflating the two would
    # report UNKNOWN for a correctly configured machine.
    seen = 0

    for path in sorted(p for p in root.iterdir() if p.is_dir()):
        # Directories only. A loose file beside the skills — a config, a README,
        # a .DS_Store — is not an undeclared skill, and reporting it as one
        # trains people to ignore the audit.
        name = path.name
        if name.startswith(".") and name not in include_hidden:
            # Hidden directories are not skill load paths for the loaders that
            # could be checked (verified 2026-10-21): dotagents excludes them
            # mechanically (its SKILL_NAME_RE requires an alphanumeric first
            # character, and its sync names hidden dirs — including .trash/ —
            # as non-skills); opencode's skill-scan filters dot entries;
            # codex's host loader prunes hidden directories. claude-code,
            # cursor and copilot are closed or minified and are UNVERIFIED —
            # which is why a skip is still REPORTED below: a skip nobody can
            # see is a place to hide something, and include_hidden puts a
            # named directory back under judgement.
            skipped_hidden.append(name)
            continue
        if name == "synced" and foreign:
            # The `synced` container is not a skill. Its evidenced children are
            # foreign buckets and get the recorded `external` verdict; its other
            # children are undeclared and fail closed — a directory merely named
            # like a bucket is not one.
            for bucket in buckets:
                seen += 1
                print(_external_line(bucket, config, today))
            for child in sorted(p for p in path.iterdir() if p.is_dir()):
                child_name = child.name
                if child_name in bucket_ids:
                    continue
                seen += 1
                problems.append(
                    (
                        child_name,
                        Decision(
                            Verdict.DENIED,
                            "undeclared",
                            f'"{child_name}" sits under synced/ but carries no bucket '
                            "evidence — no sibling .bucket-<id> marker, or a "
                            "manifest.json that does not parse to a skills[] array. "
                            "Named like a bucket is not being one; it fails closed.",
                        ),
                    )
                )
            continue
        seen += 1
        if name in vendored:
            continue
        source = declared.get(name)
        if source is None:
            if name in (config.get("deny_skills") or []):
                decision = Decision(
                    Verdict.DENIED,
                    "deny_skills",
                    f'"{name}" is installed, nothing declares it, and it is '
                    "denied by name in the trust rules. Remove it from disk, or "
                    "retract the denial with `skill-trust trust remove`.",
                )
            else:
                spdx = licence_from_dir(path)
                decision = (
                    decide(name, name, config, spdx=spdx)
                    if spdx
                    else Decision(
                        Verdict.DENIED,
                        "undeclared",
                        f'"{name}" is installed but nothing declares it, and '
                        "it carries no licence of its own. Every agent on this "
                        "machine loads it.",
                    )
                )
        else:
            decision = _judge(source, name, config, path, args.offline)
        if not decision.permitted:
            problems.append((name, decision))

    for name in skipped_hidden:
        print(
            f"SKIPPED [hidden] {name}: hidden directory, not audited; "
            "name it in include_hidden to audit it"
        )
    for name, decision in problems:
        print(f"DENIED [{decision.rule}] {name}: {decision.reason}")
    if not seen:
        print(f"skill-trust: {root} holds no skill directories", file=sys.stderr)
        return UNKNOWN
    if not problems:
        suffix = ""
        if skipped_hidden:
            suffix = (
                f" ({len(skipped_hidden)} hidden skipped: {', '.join(skipped_hidden)})"
            )
        print(f"PERMITTED all {seen} skill(s) in {root} are accounted for{suffix}")
        return PERMITTED
    return DENIED


# Flag dest → store kind, for `trust add` / `trust remove`.
_TRUST_KINDS = {
    "source": "approved_sources",
    "deny_source": "deny_sources",
    "deny_skill": "deny_skills",
    "vendor": "vendored",
    "include_hidden": "include_hidden",
    "exclude": "exclude",
}


def _trust_kind_value(args) -> tuple[str, str]:
    for flag, kind in _TRUST_KINDS.items():
        value = getattr(args, flag)
        if value is not None:
            return kind, value
    raise ConfigError(
        "trust needs one of "
        + ", ".join(f"--{f.replace('_', '-')}" for f in _TRUST_KINDS)
    )


def cmd_trust_list(args) -> int:
    found = store_mod.read_store(args.store)
    if not found:
        print(f"no decisions recorded ({args.store})")
        return PERMITTED
    for kind, entries in found.items():
        print(f"{kind}:")
        for entry in entries:
            if kind == "exclude":
                label = f"{entry['source']} : {entry['name']}"
            else:
                label = entry[store_mod.KIND_KEYS[kind]]
            meta = " — ".join(x for x in (entry.get("why"), entry.get("decided")) if x)
            print(f"  {label}" + (f"  ({meta})" if meta else ""))
    return PERMITTED


def cmd_trust_add(args) -> int:
    kind, value = _trust_kind_value(args)
    if kind == "exclude" and not args.from_source:
        raise ConfigError("--exclude names a skill; --from names its source")
    if kind != "exclude" and args.from_source:
        raise ConfigError("--from only makes sense with --exclude")
    found = store_mod.read_store(args.store)
    if kind == "exclude":
        updated = store_mod.add_entry(
            found,
            kind,
            source=args.from_source,
            name=value,
            why=args.why,
            decided=args.decided,
        )
    else:
        key = store_mod.KIND_KEYS[kind]
        if key is None:  # exclude carries a source and a name, handled above
            raise ConfigError(f"{kind} needs a source and a name, not a bare value")
        updated = store_mod.add_entry(
            found, kind, why=args.why, decided=args.decided, **{key: value}
        )
    store_mod.save_store(args.store, updated)
    print(f"recorded in {args.store}: {kind} += {value}")
    return PERMITTED


def cmd_trust_remove(args) -> int:
    kind, value = _trust_kind_value(args)
    found = store_mod.read_store(args.store)
    updated, removed = store_mod.remove_entry(found, kind, value)
    if not removed:
        print(
            f"skill-trust: no {kind} entry matching {value!r} in {args.store}",
            file=sys.stderr,
        )
        return ERROR
    store_mod.save_store(args.store, updated)
    print(f"retracted from {args.store}: {kind} -= {value}")
    return PERMITTED


def _trust_value_flags(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--source", help="approve this source (owner/repo or org)")
    group.add_argument("--deny-source", help="ban this source outright")
    group.add_argument("--deny-skill", help="deny this skill directory by name")
    group.add_argument("--vendor", help="allow this directory to exist undeclared")
    group.add_argument("--include-hidden", help="audit this hidden directory after all")
    group.add_argument(
        "--exclude", metavar="SKILL", help="veto this skill from its source"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skill-trust",
        description="Decide whether an agent skill may be installed, by source "
        "ban, approval, or licence. Exit: 0 permitted, 1 denied, "
        "2 unknown, 3 error (matching bin/policy).",
    )
    parser.add_argument("--config", type=pathlib.Path, help="trust rules, YAML")
    parser.add_argument(
        "--store",
        type=pathlib.Path,
        default=store_mod.default_store_path(),
        help="machine-local decisions, YAML (default "
        "~/.config/skill-trust/trust.yaml). Absent reads as empty — point at a "
        "nonexistent path to judge the repo rules alone.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="never consult the network; an unknown licence then denies",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="judge one source, optionally one skill")
    check.add_argument("source", help="owner/repo, or an org")
    check.add_argument("--skill", help="skill name, for exclude rules")
    check.add_argument("--skill-dir", help="installed directory, for its own licence")
    check.set_defaults(func=cmd_check)

    audit = sub.add_parser("audit", help="judge every installed skill directory")
    audit.add_argument("--skills-dir", required=True)
    audit.add_argument(
        "--declared-json",
        metavar="FILE",
        help='a manager\'s inventory as {"skills":[{name,source}]}; '
        "'-' reads stdin (e.g. dotagents list --json | ...)",
    )
    audit.set_defaults(func=cmd_audit)

    trust = sub.add_parser(
        "trust", help="inspect and edit the machine-local decision store"
    )
    tsub = trust.add_subparsers(dest="trust_command", required=True)
    tlist = tsub.add_parser("list", help="show every recorded decision")
    tlist.set_defaults(func=cmd_trust_list)
    tadd = tsub.add_parser("add", help="record a decision")
    _trust_value_flags(tadd)
    tadd.add_argument(
        "--from",
        dest="from_source",
        metavar="SOURCE",
        help="the source --exclude vetoes the skill from",
    )
    tadd.add_argument(
        "--why", required=True, help="the reason a human can check later; required"
    )
    tadd.add_argument("--decided", help="decision date, ISO (default: today)")
    tadd.set_defaults(func=cmd_trust_add)
    trem = tsub.add_parser("remove", help="retract a decision")
    _trust_value_flags(trem)
    trem.set_defaults(func=cmd_trust_remove)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.offline:
        # gh is only needed for the repository fallback, so it is required only
        # when that fallback is reachable.
        require("gh")
    try:
        return args.func(args)
    except (ConfigError, store_mod.StoreError) as exc:
        print(f"skill-trust: {exc}", file=sys.stderr)
        return ERROR
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - the CLI boundary reports, never raises
        print(f"skill-trust: {exc}", file=sys.stderr)
        return ERROR


if __name__ == "__main__":
    raise SystemExit(main())
