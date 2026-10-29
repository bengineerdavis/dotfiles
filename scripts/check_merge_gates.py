#!/usr/bin/env python3
"""Classify a diff into merge-gate buckets and report which gates apply.

ADVISORY ONLY. This script runs no gate and blocks no merge; it reports
which gates a diff must pass, per AGENTS.md § Merge gates, so an agent or
human deciding "may I self-merge" computes the answer instead of recalling
it. The advisory decision was made explicitly by the author on 2026-10-03,
per the task handoff's recommendation: a new deterministic mechanism earns
enforcement through use, not by starting maximal. Tightening it to enforce
is a later, deliberate change — and if it ever gains an --enforce flag, the
pytest gate should consume the pytest-json-report artifact queued in
TASKS.md § Now ("Machine-shaped gate outputs") rather than re-parsing text.

DELIBERATELY NOT A GIT HOOK. A gate wired into pre-commit or pre-push gets
bypassed by habit within a week, and --no-verify silently kills whatever
else shares that stage. Self-merging is a deliberate act; this script is
something the actor chooses to run as part of that reasoning.

Buckets, in the order the gate list cares about:

- deployed-tree — chezmoi-managed source paths, listed mechanically by
  `chezmoi managed --path-style=source-relative`. Zero judgment. A change
  here always means PR + human review.
- policy — permission-bearing surfaces: the policy resolver, the policy
  layer files, and every config that grants or denies an agent authority.
  A change here always means PR + human review. A file can be deployed AND
  policy (bin/executable_policy is both); buckets accumulate, and the
  verdict takes the most restrictive gate across all of a path's buckets.
- docs — markdown and non-executable metadata, matched by an editable
  pattern list. A docs-only diff needs only the doc gates.
- everything else — the full gate, unchanged.

Egress is reported as a standing reminder, never as a finding: whether a
change enables a new network call is a property of code, not of paths, and
a mechanical answer here would be false automation. The honest output is
"this checker cannot see egress; self-check".

Pattern lists use fnmatch semantics, where `*` also crosses `/`: `docs/*`
matches every depth under docs/, and `*.md` matches a README at any depth.
"""

from __future__ import annotations

import fnmatch
import json
import subprocess
import sys
from pathlib import Path

# Permission-bearing surfaces, enumerated by inspection 2026-10-03 and kept
# here rather than discovered, because "what counts as policy" is a decision
# only a human can ratify. Confirm completeness before widening.
POLICY_EXACT = frozenset(
    {
        "bin/executable_policy",  # the resolver itself; also deployed
        ".claude/settings.json",  # repo-native Claude permission tiers
        "opencode.jsonc",  # repo-scoped opencode tiers; deploy-ignored
        "dot_config/opencode/opencode.jsonc.tmpl",  # global tiers; deployed
    }
)
POLICY_GLOBS = ("dotfiles/policy/*",)

DOCS_GLOBS = ("*.md", "docs/*", "changelog.d/*")

DEPLOYED_CMD = ["chezmoi", "managed", "--path-style=source-relative"]

FULL_GATES = (
    "full test suite green: uv run --frozen --with pytest-xdist "
    "pytest tests tools -q -n auto --dist worksteal",
    "skillet validate . exits 0 with no errors",
    "new or changed test seen to fail, mutation recorded in commit message",
    "nothing under Cross-session hazards touched without a claim",
)
DOCS_GATES = (
    "skillet validate . exits 0",
    "doc-link/doc-integrity tests green: uv run --frozen pytest tests/docs -q",
)
PR_GATES = ("push the branch and open a PR — human review, no self-merge",)

EGRESS_REMINDER = (
    "egress: not mechanically detectable — check the diff yourself for new "
    "network call sites (curl, llm, ollama, fetch)"
)

VERDICTS = {
    "empty": "no changed files — nothing to check",
    "docs": "docs-only diff — light gate",
    "full": "non-docs diff — full gate",
    "pr": "diff touches a deployed-tree or policy path — PR + human review",
    "degraded": "chezmoi unavailable — deployed-tree check skipped; "
    "treating the diff as non-docs (fail closed)",
}


def buckets_for(path: str, managed: frozenset[str]) -> tuple[str, ...]:
    """Buckets a changed path falls into; a path may carry several."""
    out = []
    # .chezmoiroot=home changes repository paths, not the managed source paths
    # returned by chezmoi. Repo-native paths outside home/ stay unchanged.
    source_path = path.removeprefix("home/")
    if source_path in managed:
        out.append("deployed")
    if source_path in POLICY_EXACT or any(
        fnmatch.fnmatch(source_path, g) for g in POLICY_GLOBS
    ):
        out.append("policy")
    if any(fnmatch.fnmatch(path, g) for g in DOCS_GLOBS):
        out.append("docs")
    return tuple(out)


def verdict_for(
    paths: list[str], classified: dict[str, tuple[str, ...]], managed_ok: bool
) -> tuple[str, tuple[str, ...]]:
    """(verdict key, gates). Pure, so both directions are testable."""
    if not paths:
        return "empty", ()
    hits = [b for bs in classified.values() for b in bs]
    if "deployed" in hits or "policy" in hits:
        return "pr", PR_GATES
    if not managed_ok:
        # Without chezmoi we cannot prove a path is absent from the deployed
        # tree, so a docs-only verdict would be an unverified claim.
        return "degraded", FULL_GATES
    if all(bs == ("docs",) for bs in classified.values()):
        return "docs", DOCS_GATES
    return "full", FULL_GATES


def managed_paths(repo: Path) -> frozenset[str] | None:
    """The chezmoi-managed source paths, or None when chezmoi cannot answer."""
    try:
        out = subprocess.run(
            DEPLOYED_CMD, capture_output=True, text=True, cwd=repo, timeout=60
        )
    except OSError, subprocess.TimeoutExpired:
        return None
    if out.returncode != 0:
        return None
    return frozenset(out.stdout.split())


def changed_paths(repo: Path, staged: bool, base: str | None) -> list[str] | None:
    """Changed paths for the requested diff, or None when git cannot answer."""
    if staged:
        cmd = ["git", "-C", str(repo), "diff", "--cached", "--name-only"]
    elif base:
        cmd = ["git", "-C", str(repo), "diff", "--name-only", f"{base}...HEAD"]
    else:
        return None
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        return None
    return [p for p in out.stdout.splitlines() if p]


def report(
    base: str | None,
    staged: bool,
    paths: list[str],
    classified: dict[str, tuple[str, ...]],
    verdict: str,
    gates: tuple[str, ...],
    managed_ok: bool,
) -> dict:
    """One JSON artifact, the shape queued as 'Machine-shaped gate outputs'."""
    return {
        "mode": "advisory",
        "diff": "staged" if staged else f"merge-base({base})...HEAD",
        "files": [{"path": p, "buckets": list(classified[p])} for p in paths],
        "verdict": verdict,
        "verdict_text": VERDICTS[verdict],
        "gates": list(gates),
        "degraded": not managed_ok,
        "egress_reminder": EGRESS_REMINDER,
    }


def print_human(r: dict) -> None:
    print(f"diff: {r['diff']}")
    for f in r["files"]:
        label = ", ".join(f["buckets"]) if f["buckets"] else "other"
        print(f"  {label:<28} {f['path']}")
    print(f"verdict: {r['verdict_text']}")
    for g in r["gates"]:
        print(f"  gate: {g}")
    print(f"note: {r['egress_reminder']}")
    print("advisory: this report runs no gate and blocks no merge")


def main(argv: list[str]) -> int:
    staged = "--staged" in argv
    base = None
    json_path = None
    repo = Path.cwd()
    args = [a for a in argv[1:] if a not in ("--staged",)]
    i = 0
    while i < len(args):
        if args[i] == "--base":
            i += 1
            if i >= len(args):
                print("--base needs a ref", file=sys.stderr)
                return 2
            base = args[i]
        elif args[i] == "--json":
            i += 1
            if i >= len(args):
                print("--json needs a path", file=sys.stderr)
                return 2
            json_path = args[i]
        elif args[i] == "--repo":
            i += 1
            if i >= len(args):
                print("--repo needs a directory", file=sys.stderr)
                return 2
            repo = Path(args[i])
        elif args[i].startswith("-"):
            print(f"unknown flag {args[i]}", file=sys.stderr)
            return 2
        else:
            print(f"unexpected argument {args[i]}", file=sys.stderr)
            return 2
        i += 1

    if not staged and base is None:
        base = "origin/main"

    paths = changed_paths(repo, staged, base)
    if paths is None:
        print("could not compute the requested diff", file=sys.stderr)
        return 2

    managed = managed_paths(repo)
    managed_ok = managed is not None
    if not managed_ok:
        print(
            "warning: chezmoi unavailable — deployed-tree bucket skipped, "
            "verdict degraded (fail closed)",
            file=sys.stderr,
        )
    classified = {p: buckets_for(p, managed or frozenset()) for p in paths}
    verdict, gates = verdict_for(paths, classified, managed_ok)
    r = report(base, staged, paths, classified, verdict, gates, managed_ok)

    if json_path:
        text = json.dumps(r, indent=2)
        if json_path == "-":
            print(text)
        else:
            Path(json_path).write_text(text + "\n", encoding="utf-8")
    print_human(r)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
