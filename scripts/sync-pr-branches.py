#!/usr/bin/env python3
"""Clean-merge behind same-repository GitHub PRs, or report in dry-run mode."""

import argparse
import json
import os
import subprocess
import sys


def call(args: list[str]) -> dict | list:
    result = subprocess.run(
        ["gh", "api", *args], text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    repository = os.environ.get("GH_REPOSITORY")
    if not repository:
        print("GH_REPOSITORY must be owner/repo", file=sys.stderr)
        return 2

    try:
        settings = call([f"repos/{repository}"])
        if not isinstance(settings, dict) or not settings.get("allow_update_branch"):
            raise RuntimeError(
                "allow_update_branch is disabled. On GitHub, enable "
                "'Always suggest updating pull request branches'."
            )
        default_branch = settings.get("default_branch")
        if not isinstance(default_branch, str) or not default_branch:
            raise RuntimeError("the repository did not report its default branch")

        failures = []
        page = 1
        while True:
            prs = call(
                [
                    "-X",
                    "GET",
                    f"repos/{repository}/pulls",
                    "-f",
                    "state=open",
                    "-f",
                    "per_page=100",
                    "-f",
                    f"page={page}",
                ]
            )
            if not isinstance(prs, list):
                raise RuntimeError("GitHub returned an invalid pull-request list")
            for item in prs:
                if not isinstance(item, dict) or not isinstance(
                    item.get("number"), int
                ):
                    raise RuntimeError("GitHub returned an invalid pull-request entry")
                number = item["number"]
                try:
                    detail = call([f"repos/{repository}/pulls/{number}"])
                    if not isinstance(detail, dict):
                        raise RuntimeError("invalid pull-request detail")
                    head = detail["head"]
                    if head["repo"]["full_name"] != repository:
                        print(f"#{number}: fork; no update attempted")
                        continue
                    base = detail["base"]["ref"]
                    if base != default_branch:
                        print(f"#{number}: stacked on {base}; manual update required")
                        continue
                    comparison = call(
                        [f"repos/{repository}/compare/{default_branch}...{head['sha']}"]
                    )
                    if not isinstance(comparison, dict) or not isinstance(
                        comparison.get("behind_by"), int
                    ):
                        raise RuntimeError("invalid branch comparison")
                    if comparison["behind_by"] == 0:
                        print(f"#{number}: up to date")
                        continue
                    if args.dry_run:
                        print(
                            f"#{number}: {comparison['behind_by']} commits behind; "
                            "clean merge would be requested"
                        )
                        continue
                    call(
                        [
                            "-X",
                            "PUT",
                            f"repos/{repository}/pulls/{number}/update-branch",
                            "-f",
                            f"expected_head_sha={head['sha']}",
                        ]
                    )
                    print(f"#{number}: clean merge update requested")
                except (KeyError, TypeError, RuntimeError) as error:
                    failures.append(f"#{number}: {error}")
            if len(prs) < 100:
                break
            page += 1
    except (KeyError, TypeError, RuntimeError) as error:
        print(f"branch sync failed: {error}", file=sys.stderr)
        return 1

    for failure in failures:
        print(f"branch sync needs attention: {failure}", file=sys.stderr)
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
