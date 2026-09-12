"""Command line entry point.

Exit codes deliberately match `bin/policy`, because this answers the same shape
of question and a caller should not have to learn two vocabularies:

    0 PERMITTED   1 DENIED   2 UNKNOWN   3 ERROR
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys

import yaml

from .decide import Decision, Verdict, decide
from .discover import licence_from_dir, licence_from_repo

PERMITTED, DENIED, UNKNOWN, ERROR = 0, 1, 2, 3


class ConfigError(Exception):
    """A rules file that could not be read. Distinct from a denial on purpose:
    "I could not tell you" and "I told you no" mean different things to a
    caller, and collapsing them lets a mistyped path read as a clean refusal."""



def require(*commands: str) -> None:
    """Report every missing dependency at once, then exit 127.

    Same contract as the shell guards in docs/TOPICS.md: one run names every gap
    rather than one per invocation, and 127 is the conventional
    command-not-found status.
    """
    missing = [c for c in commands if not shutil.which(c)]
    if missing:
        print(f"skill-trust: missing dependencies: {' '.join(missing)}", file=sys.stderr)
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


def _judge(source: str, skill: str | None, config: dict,
           skill_dir: pathlib.Path | None, offline: bool) -> Decision:
    """Decide once without a licence, and only look one up if that was the
    level that would have decided it."""
    provisional = decide(source, skill, config, spdx=None)
    if provisional.rule != "default":
        return provisional
    spdx = licence_from_dir(skill_dir) if skill_dir else None
    if spdx is None and not offline:
        spdx = licence_from_repo(source)
    return decide(source, skill, config, spdx=spdx)


def cmd_check(args) -> int:
    config = load_config(args.config)
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
    config = load_config(args.config)
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
        raw = sys.stdin.read() if args.declared_json == "-" else \
            pathlib.Path(args.declared_json).read_text(encoding="utf-8")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"--declared-json is not JSON: {exc}") from exc
        for entry in payload.get("skills") or []:
            if entry.get("name") and entry.get("source"):
                declared[entry["name"]] = entry["source"]

    vendored = set(config.get("vendored") or [])
    problems: list[tuple[str, Decision]] = []
    # Counted before the vendored skip on purpose: a directory whose skills are
    # all exempt is fully accounted for, not unexamined. Conflating the two would
    # report UNKNOWN for a correctly configured machine.
    seen = 0

    for path in sorted(p for p in root.iterdir() if p.is_dir()):
        # Directories only. A loose file beside the skills — a config, a README,
        # a .DS_Store — is not an undeclared skill, and reporting it as one
        # trains people to ignore the audit.
        name = path.name
        seen += 1
        if name in vendored:
            continue
        source = declared.get(name)
        if source is None:
            spdx = licence_from_dir(path)
            decision = decide(name, None, config, spdx=spdx) if spdx else Decision(
                Verdict.DENIED, "undeclared",
                f'"{name}" is installed but nothing declares it, and it carries '
                "no licence of its own. Every agent on this machine loads it.",
            )
        else:
            decision = _judge(source, name, config, path, args.offline)
        if not decision.permitted:
            problems.append((name, decision))

    for name, decision in problems:
        print(f"DENIED [{decision.rule}] {name}: {decision.reason}")
    if not seen:
        print(f"skill-trust: {root} holds no skill directories", file=sys.stderr)
        return UNKNOWN
    if not problems:
        print(f"PERMITTED all {seen} skill(s) in {root} are accounted for")
        return PERMITTED
    return DENIED


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skill-trust",
        description="Decide whether an agent skill may be installed, by source "
                    "ban, approval, or licence. Exit: 0 permitted, 1 denied, "
                    "2 unknown, 3 error (matching bin/policy).",
    )
    parser.add_argument("--config", type=pathlib.Path, help="trust rules, YAML")
    parser.add_argument("--offline", action="store_true",
                        help="never consult the network; an unknown licence then denies")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="judge one source, optionally one skill")
    check.add_argument("source", help="owner/repo, or an org")
    check.add_argument("--skill", help="skill name, for exclude rules")
    check.add_argument("--skill-dir", help="installed directory, for its own licence")
    check.set_defaults(func=cmd_check)

    audit = sub.add_parser("audit", help="judge every installed skill directory")
    audit.add_argument("--skills-dir", required=True)
    audit.add_argument("--declared-json", metavar="FILE",
                       help="a manager's inventory as {\"skills\":[{name,source}]}; "
                            "'-' reads stdin (e.g. dotagents list --json | ...)")
    audit.set_defaults(func=cmd_audit)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.offline:
        # gh is only needed for the repository fallback, so it is required only
        # when that fallback is reachable.
        require("gh")
    try:
        return args.func(args)
    except ConfigError as exc:
        print(f"skill-trust: {exc}", file=sys.stderr)
        return ERROR
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - the CLI boundary reports, never raises
        print(f"skill-trust: {exc}", file=sys.stderr)
        return ERROR


if __name__ == "__main__":
    raise SystemExit(main())
