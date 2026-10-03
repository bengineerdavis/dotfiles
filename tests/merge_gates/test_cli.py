"""End-to-end runs of the checker CLI against a scratch git repo.

chezmoi is faked on PATH so the deployed-tree bucket is driven by data
the test controls, the same way tests/clipped mocks uname. The real-repo
verification (a real `chezmoi managed` diff against recent commits) is
run by hand at development time, per the task's done-condition, and is
not a committed test: it depends on this machine's chezmoi state.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _git(repo: pathlib.Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def run_script(
    repo: pathlib.Path,
    env: dict[str, str],
    *args: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "python3",
            str(REPO_ROOT / "scripts" / "check_merge_gates.py"),
            "--repo",
            str(repo),
            *args,
        ],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(repo),
    )


def commit_three(repo: pathlib.Path) -> None:
    """One docs, one policy, one code file, plus a deployed file."""
    (repo / "docs").mkdir()
    (repo / "docs" / "probe.md").write_text("note\n")
    (repo / "dotfiles" / "policy").mkdir(parents=True)
    (repo / "dotfiles" / "policy" / "probe.yaml").write_text("x: 1\n")
    (repo / "tools").mkdir()
    (repo / "tools" / "probe.py").write_text("print('hi')\n")
    (repo / "bin").mkdir()
    (repo / "bin" / "executable_probe").write_text("#!/bin/sh\n")
    _git(
        repo,
        "add",
        "docs/probe.md",
        "dotfiles/policy/probe.yaml",
        "tools/probe.py",
        "bin/executable_probe",
    )
    _git(repo, "commit", "-q", "-m", "three files")


def row(stdout: str, label: str, path: str) -> bool:
    """A bucket row, compared without depending on column width."""
    return any(
        line.strip().rsplit(None, 1) == [label, path] for line in stdout.splitlines()
    )


class TestThreeFileDiff:
    """The done-condition diff.

    One docs, one policy, one code file — plus a deployed file, so every
    bucket is exercised at once.
    """

    def test_sorted_into_right_buckets(self, git_repo, fake_chezmoi, env_with):
        commit_three(git_repo)
        env = env_with(fake_chezmoi(["bin/executable_probe", "dot_zshrc.tmpl"]))
        r = run_script(git_repo, env, "--base", "main")
        assert r.returncode == 0, r.stderr
        assert row(r.stdout, "docs", "docs/probe.md")
        assert row(r.stdout, "policy", "dotfiles/policy/probe.yaml")
        assert row(r.stdout, "other", "tools/probe.py")
        assert row(r.stdout, "deployed", "bin/executable_probe")
        assert "PR + human review" in r.stdout

    def test_json_artifact(self, git_repo, fake_chezmoi, env_with, tmp_path):
        commit_three(git_repo)
        out = tmp_path / "gates.json"
        env = env_with(fake_chezmoi(["bin/executable_probe"]))
        r = run_script(git_repo, env, "--base", "main", "--json", str(out))
        assert r.returncode == 0, r.stderr
        data = json.loads(out.read_text())
        assert data["mode"] == "advisory"
        assert data["verdict"] == "pr"
        buckets = {f["path"]: f["buckets"] for f in data["files"]}
        assert buckets["docs/probe.md"] == ["docs"]
        assert buckets["dotfiles/policy/probe.yaml"] == ["policy"]
        assert buckets["tools/probe.py"] == []
        assert buckets["bin/executable_probe"] == ["deployed"]
        assert data["egress_reminder"]


class TestVerdicts:
    def test_docs_only_diff(self, git_repo, fake_chezmoi, env_with):
        (git_repo / "note.md").write_text("hi\n")
        _git(git_repo, "add", "note.md")
        _git(git_repo, "commit", "-q", "-m", "docs")
        env = env_with(fake_chezmoi(["bin/executable_probe"]))
        r = run_script(git_repo, env, "--base", "main")
        assert r.returncode == 0
        assert "docs-only diff" in r.stdout
        assert "pytest tests/docs" in r.stdout

    def test_no_diff_is_empty(self, git_repo, fake_chezmoi, env_with):
        env = env_with(fake_chezmoi([]))
        r = run_script(git_repo, env, "--base", "main")
        assert r.returncode == 0
        assert "nothing to check" in r.stdout

    def test_staged_mode(self, git_repo, fake_chezmoi, env_with):
        (git_repo / "staged.py").write_text("x = 1\n")
        _git(git_repo, "add", "staged.py")
        env = env_with(fake_chezmoi([]))
        r = run_script(git_repo, env, "--staged")
        assert r.returncode == 0
        assert "staged.py" in r.stdout
        assert "full gate" in r.stdout

    def test_deployed_via_managed_list(self, git_repo, fake_chezmoi, env_with):
        (git_repo / "bin").mkdir()
        (git_repo / "bin" / "executable_probe").write_text("#!/bin/sh\n")
        _git(git_repo, "add", "bin/executable_probe")
        _git(git_repo, "commit", "-q", "-m", "probe")
        env = env_with(fake_chezmoi(["bin/executable_probe"]))
        r = run_script(git_repo, env, "--base", "main")
        assert "deployed" in r.stdout
        assert "PR + human review" in r.stdout


class TestDegraded:
    def test_chezmoi_failure_fails_closed(self, git_repo, fake_chezmoi, env_with):
        (git_repo / "note.md").write_text("hi\n")
        _git(git_repo, "add", "note.md")
        _git(git_repo, "commit", "-q", "-m", "docs")
        env = env_with(fake_chezmoi([], fail=True))
        r = run_script(git_repo, env, "--base", "main")
        assert r.returncode == 0
        # the one gate line only the full gate carries
        assert "skillet validate . exits 0 with no errors" in r.stdout
        assert "chezmoi unavailable" in r.stderr


class TestInvocation:
    def test_unknown_flag_exits_2(self, git_repo, env_with):
        env = env_with(None)
        r = run_script(git_repo, env, "--wat")
        assert r.returncode == 2

    def test_output_states_advisory(self, git_repo, env_with):
        env = env_with(None)
        r = run_script(git_repo, env, "--base", "main")
        assert "runs no gate and blocks no merge" in r.stdout
