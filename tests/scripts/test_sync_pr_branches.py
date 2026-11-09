import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts" / "sync-pr-branches.py"
REPO = "owner/project"


def run_pulse(
    tmp_path: Path,
    *,
    pages: list[list[dict]] | None = None,
    settings: dict | None = None,
    failures: dict | None = None,
) -> subprocess.CompletedProcess[str]:
    fixture = tmp_path / "fixture.json"
    fixture.write_text(
        json.dumps(
            {
                "pages": pages or [],
                "settings": settings
                or {"allow_update_branch": True, "default_branch": "main"},
                "failures": failures or {},
                "details": {
                    **{
                        f"repos/{REPO}/pulls/{item['number']}": item
                        for page in pages or []
                        for item in page
                    },
                    **{
                        f"repos/{REPO}/compare/main...{item['head']['sha']}": {
                            "behind_by": item.get("behind_by", 1)
                        }
                        for page in pages or []
                        for item in page
                        if not item["head"]["repo"]["full_name"] != REPO
                        if item["base"]["ref"] == "main"
                    },
                },
            }
        )
    )
    env = os.environ.copy()
    env.pop("MISE_CONFIG_FILE", None)
    (tmp_path / "gh").write_text(
        (Path(__file__).parents[1] / "fixtures" / "gh")
        .read_text()
        .replace("#!/usr/bin/env python3", f"#!{sys.executable}", 1)
    )
    (tmp_path / "gh").chmod(0o755)
    env.update(
        GH_TOKEN="fixture",
        GH_REPOSITORY=REPO,
        BRANCH_SYNC_FIXTURE=str(fixture),
        PATH=f"{tmp_path}:{env['PATH']}",
    )
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def pr(number: int, *, behind: int = 1, fork: bool = False, base: str = "main") -> dict:
    return {
        "number": number,
        "behind_by": behind,
        "head": {
            "ref": f"feature-{number}",
            "sha": f"head-{number}",
            "repo": {"full_name": "someone/fork" if fork else REPO},
        },
        "base": {"ref": base},
    }


def test_only_behind_same_repository_prs_get_expected_head_updates(
    tmp_path: Path,
) -> None:
    result = run_pulse(
        tmp_path,
        pages=[[pr(1), pr(2, behind=0), pr(3, fork=True)]],
    )

    assert result.returncode == 0, result.stderr
    calls = json.loads((tmp_path / "calls.json").read_text())
    assert calls == [
        {
            "endpoint": f"repos/{REPO}/pulls/1/update-branch",
            "expected_head_sha": "head-1",
        }
    ]


def test_all_pages_are_processed(tmp_path: Path) -> None:
    result = run_pulse(
        tmp_path,
        pages=[
            [pr(number, behind=0) for number in range(1, 101)],
            [pr(101)],
        ],
    )

    assert result.returncode == 0
    calls = json.loads((tmp_path / "calls.json").read_text())
    assert [call["endpoint"] for call in calls] == [
        f"repos/{REPO}/pulls/101/update-branch",
    ]


def test_stacked_pr_is_reported_without_an_update(tmp_path: Path) -> None:
    result = run_pulse(tmp_path, pages=[[pr(1, base="parent-feature")]])

    assert result.returncode == 0
    assert "parent-feature" in result.stdout
    assert not (tmp_path / "calls.json").exists()


def test_disabled_native_update_capability_fails_before_listing(tmp_path: Path) -> None:
    result = run_pulse(
        tmp_path,
        pages=[[pr(1)]],
        settings={"allow_update_branch": False, "default_branch": "main"},
    )

    assert result.returncode != 0
    assert "allow_update_branch" in result.stderr
    assert not (tmp_path / "calls.json").exists()


def test_one_conflict_does_not_hide_other_updates_and_fails_the_run(
    tmp_path: Path,
) -> None:
    result = run_pulse(
        tmp_path,
        pages=[[pr(1), pr(2)]],
        failures={"1": {"status": 422, "message": "merge conflict"}},
    )

    assert result.returncode != 0
    assert "#1" in result.stderr
    calls = json.loads((tmp_path / "calls.json").read_text())
    assert [call["endpoint"] for call in calls] == [
        f"repos/{REPO}/pulls/1/update-branch",
        f"repos/{REPO}/pulls/2/update-branch",
    ]
