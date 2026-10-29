"""Report which apt sources failed an `apt-get update`, and for how many runs.

Called by apps/apt/tasks/upgrade.yaml with the combined output of
`apt-get update` on stdin. Report-only: it never edits a source. Retiring a dead
repository is a human decision recorded in `apt_retired_sources`.

Why the run count matters: proget.makedeb.org returned HTTP 530 for months
before anyone noticed it was not an outage but an archived project
(makedeb, archived 2025-11-21). One failure is noise; the same host failing
run after run is a retirement candidate, and saying so is the point.

State is a small JSON file mapping host -> consecutive failing runs. A host that
succeeds is dropped, so the count is consecutive, not cumulative.

Prints one JSON object: {"failures": [...], "recovered": [...]}.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NO_PUBKEY = re.compile(r"GPG error: (?P<url>\S+) .*NO_PUBKEY (?P<key>[0-9A-F]+)")
FETCH_FAILED = re.compile(r"^E: Failed to fetch (?P<url>\S+)\s+(?P<why>.*)$")
NOT_SIGNED = re.compile(
    r"^E: The repository '(?P<url>\S+) .*' (?:is no longer signed|is not signed)"
)


def host_of(url: str) -> str:
    return re.sub(r"^[a-z]+://", "", url).split("/", 1)[0]


def parse(output: str) -> dict[str, dict]:
    """host -> {"kinds": [...], "lines": [...]} for every failing source."""
    found: dict[str, dict] = {}

    def add(url: str, kind: str, line: str) -> None:
        entry = found.setdefault(host_of(url), {"kinds": [], "lines": []})
        if kind not in entry["kinds"]:
            entry["kinds"].append(kind)
        if line not in entry["lines"]:
            entry["lines"].append(line)

    for raw in output.splitlines():
        line = raw.strip()
        if not line.startswith(("W:", "E:")):
            continue
        if m := NO_PUBKEY.search(line):
            add(m["url"], f"NO_PUBKEY {m['key']}", line)
        elif m := FETCH_FAILED.match(line):
            add(m["url"], "fetch-failed", line)
        elif m := NOT_SIGNED.match(line):
            add(m["url"], "unsigned", line)
    return found


def update_state(
    state: dict[str, int], failing: dict[str, dict]
) -> tuple[dict[str, int], list[str]]:
    recovered = sorted(h for h in state if h not in failing)
    new_state = {h: state.get(h, 0) + 1 for h in failing}
    return new_state, recovered


def load_state(path: Path) -> dict[str, int]:
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return {}
    return {str(k): int(v) for k, v in data.items()} if isinstance(data, dict) else {}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--state", required=True, help="JSON state file (created if missing)"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=3,
        help="consecutive failing runs before a host is flagged for retirement",
    )
    parser.add_argument(
        "--check", action="store_true", help="do not write the state file"
    )
    args = parser.parse_args(argv)

    failing = parse(sys.stdin.read())
    state_path = Path(args.state)
    new_state, recovered = update_state(load_state(state_path), failing)

    if not args.check:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(new_state, indent=2, sort_keys=True) + "\n")

    failures = [
        {
            "host": host,
            "kinds": info["kinds"],
            "consecutive_runs": new_state[host],
            "retirement_candidate": new_state[host] >= args.threshold,
            "lines": info["lines"],
        }
        for host, info in sorted(failing.items())
    ]
    print(json.dumps({"failures": failures, "recovered": recovered}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
