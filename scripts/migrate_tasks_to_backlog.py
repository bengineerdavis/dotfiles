#!/usr/bin/env python3
"""One-shot migration: TASKS.md § Now + § Planned items -> backlog/ tasks.

Part of the backlog-md-py cutover (docs/BACKLOG-MIGRATION.md). Parses
top-level `- ` items between the section headings, extracts a title (bold
prefix, else first sentence), and creates one backlog task per item with
the body moved verbatim (minus the leading "- "). Mapping:

  § Now     -> status "To Do", labels [now], priority high
  § Planned -> status "To Do", labels [planned, group:<subhead> if any]
  [blocked: ...] in body -> adds label "blocked"

In Progress is deliberately never set: it is a claimed workflow state, not
a storage status (docs/BACKLOG-MIGRATION.md § Verified). Owners re-claim
via orchestration on resume.

Usage:
  scripts/migrate_tasks_to_backlog.py [--dry-run] [--cwd DIR]

Run against a COPY of the repo first (the cutover-validation protocol);
--cwd points the backlog-py invocation, so the script can run from the
real checkout against the copy. Refuses to run into a non-empty
backlog/tasks/ unless --force.
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

BOLD_TITLE = re.compile(r"^-\s+\*\*(.+?)\*\*\s*:?[.!]?\s*", re.DOTALL)
ITEM_START = re.compile(r"^- ")
HEADING = re.compile(r"^## ")
SUBHEADING = re.compile(r"^### (.+)")


def parse_items(text: str):
    """Yield (section, subhead, body) for each top-level item in Now/Planned.

    Only lines that START an item begin a buffer: section and subhead
    preamble prose (text between a heading and the first `- `) must never
    become a task — it inflated the count by exactly the number of
    preambles when first written (1 Now + 1 Planned + 4 subheads).
    """
    section = None
    subhead = None
    buf = []
    in_item = False

    def flush():
        nonlocal in_item
        if in_item and buf and section is not None:
            body = "\n".join(buf).strip()
            body = body[2:] if body.startswith("- ") else body
            if body:
                yield section, subhead, body
        buf.clear()
        in_item = False

    for line in text.splitlines():
        if HEADING.match(line):
            name = line[3:].split(" — ")[0].strip()
            yield from flush()
            section = name if name in ("Now", "Planned") else None
            subhead = None
            continue
        if section is None:
            continue
        sub_match = SUBHEADING.match(line)
        if sub_match:
            yield from flush()
            subhead = sub_match.group(1).strip()
            continue
        if ITEM_START.match(line):
            yield from flush()
            in_item = True
        if in_item:
            buf.append(line)
    yield from flush()


def title_of(body: str) -> str:
    m = BOLD_TITLE.match("- " + body)
    if m:
        title = m.group(1)
    else:
        title = (body.splitlines() or ["Untitled item"])[0] or "Untitled item"
        for sep in (". ", " — ", ": "):
            if sep in title:
                title = title.split(sep, 1)[0]
    # Bold markers must never survive into a title: multi-line bold titles
    # fall to the fallback when DOTALL is off, and unbolded items can carry
    # inline emphasis. Collapse whitespace from multi-line titles too.
    title = title.replace("**", "")
    title = re.sub(r"\s+", " ", title)
    return title.strip().rstrip(".")[:100]


def labels_of(section: str, subhead: str | None, body: str) -> list[str]:
    labels = [section.lower()]
    if subhead:
        slug = re.sub(r"[^a-z0-9]+", "-", subhead.lower()).strip("-")
        labels.append(f"group:{slug}")
    if "[blocked" in body.lower():
        labels.append("blocked")
    return labels


def backlog_cmd() -> list[str]:
    """A shim on PATH is not proof of a working install: mise creates the
    shim when an entry is declared, and it errors 'No version is set for
    shim' until the version is actually installed (a stale shim sat on this
    machine with no entry behind it). Probe viability, not presence.
    """
    exe = shutil.which("backlog-py")
    if exe:
        probe = subprocess.run([exe, "--version"], capture_output=True)
        if probe.returncode == 0:
            return [exe]
    return ["uvx", "--from", "backlog-md-py", "backlog-py"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--cwd", default=".")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--tasks-md", default="TASKS.md")
    args = ap.parse_args()

    tasks_dir = Path(args.cwd) / "backlog" / "tasks"
    if tasks_dir.exists() and any(tasks_dir.iterdir()) and not args.force:
        sys.exit(
            f"{tasks_dir} is not empty; one-shot import refuses (--force to override)"
        )

    text = Path(args.tasks_md).read_text()
    items = list(parse_items(text))
    by_section = {}
    for section, _, _ in items:
        by_section[section] = by_section.get(section, 0) + 1
    print(f"parsed {len(items)} items: {by_section}")

    if args.dry_run:
        return 0

    cmd = backlog_cmd()
    created = 0
    for section, subhead, body in items:
        argv = cmd + [
            "--cwd",
            args.cwd,
            "task",
            "create",
            title_of(body),
            "-d",
            body,
            "-s",
            "To Do",
            "-l",
            ",".join(labels_of(section, subhead, body)),
        ]
        if section == "Now":
            argv += ["--priority", "high"]
        result = subprocess.run(argv, capture_output=True, text=True)
        if result.returncode != 0:
            print(
                f"FAILED: {title_of(body)!r}: {result.stderr.strip()}", file=sys.stderr
            )
            return 1
        created += 1
    print(f"created {created} tasks in {args.cwd}/backlog/tasks/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
