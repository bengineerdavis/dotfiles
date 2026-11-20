"""Real-data consistency: the policy lists vs a live `chezmoi managed`.

The other suites here drive the checker through a fake `chezmoi`; this
one runs the real `chezmoi managed --path-style=source-relative` and
asserts POLICY_EXACT and POLICY_GLOBS still describe what chezmoi
actually manages. It is the committed form of the hand-run verification
test_cli.py's docstring records — the same property, now a test that
skips cleanly wherever this machine has no chezmoi to answer.

chezmoi answers from its configured source directory, not the working
directory, so from a worktree the managed set describes the main
checkout — the deployed reality these lists must match. The module is
read-only: one chezmoi query, no writes.
"""

from __future__ import annotations

import fnmatch
import pathlib
import shutil
import subprocess

import pytest

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

REPO = pathlib.Path(__file__).resolve().parents[2]
MANAGED_CMD = ["chezmoi", "managed", "--path-style=source-relative"]

# POLICY_EXACT entries that are repo-native files, deliberately kept out
# of the deployed tree (.chezmoiignore carries both). Every other entry
# names a chezmoi source file and must stay in the live managed output.
REPO_NATIVE = frozenset({".claude/settings.json", "opencode.jsonc"})


def live_managed() -> frozenset[str] | None:
    """The real managed set, or None where chezmoi cannot answer.

    An unconfigured chezmoi reports a source directory that does not
    exist and answers `managed` with an empty set. That is not a real
    answer, so skip. If the source directory exists but the managed set
    is empty, return the empty set: the nonempty assertion must fail
    rather than passing a broken deployment as an unavailable check.
    """
    if shutil.which("chezmoi") is None:
        return None
    try:
        source = subprocess.run(
            ["chezmoi", "source-path"],
            capture_output=True,
            text=True,
            cwd=REPO,
            timeout=60,
        )
        out = subprocess.run(
            MANAGED_CMD, capture_output=True, text=True, cwd=REPO, timeout=60
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if source.returncode != 0 or out.returncode != 0:
        return None
    if not pathlib.Path(source.stdout.strip()).is_dir():
        return None
    return frozenset(out.stdout.split())


@pytest.fixture(scope="module")
def managed() -> frozenset[str]:
    got = live_managed()
    if got is None:
        pytest.skip("chezmoi unavailable — no live managed set to check against")
    return got


def test_deployed_membership_set_is_nonempty(managed):
    """An empty answer would leave the deployed bucket never firing."""
    assert managed


def test_live_managed_skips_only_when_no_source_directory_exists(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
):
    """An existing source must not turn an empty answer into a skip."""
    monkeypatch.setattr("shutil.which", lambda _name: "/bin/chezmoi")

    def answer(command, **_kwargs):
        stdout = f"{tmp_path}\n" if command[1] == "source-path" else ""
        return subprocess.CompletedProcess([], 0, stdout=stdout, stderr="")

    monkeypatch.setattr(subprocess, "run", answer)
    assert live_managed() == frozenset()

    def missing_source(command, **_kwargs):
        stdout = f"{tmp_path / 'missing'}\n" if command[1] == "source-path" else ""
        return subprocess.CompletedProcess([], 0, stdout=stdout, stderr="")

    monkeypatch.setattr(subprocess, "run", missing_source)
    assert live_managed() is None


def test_live_managed_preserves_a_real_membership_answer(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
):
    """The source probe must not discard a nonempty managed set."""
    monkeypatch.setattr("shutil.which", lambda _name: "/bin/chezmoi")

    def answer(command, **_kwargs):
        stdout = (
            f"{tmp_path}\n"
            if command[1] == "source-path"
            else "dot_zshrc.tmpl\nbin/executable_triage\n"
        )
        return subprocess.CompletedProcess([], 0, stdout=stdout, stderr="")

    monkeypatch.setattr(subprocess, "run", answer)
    assert live_managed() == frozenset({"dot_zshrc.tmpl", "bin/executable_triage"})


def test_home_git_paths_normalize_to_managed_paths(m):
    """Repo paths change, not chezmoi-managed paths."""
    buckets_for = m.buckets_for

    managed = frozenset({"bin/executable_triage", "dot_zshrc.tmpl"})
    assert buckets_for("home/bin/executable_triage", managed) == ("deployed",)
    assert buckets_for("home/dot_zshrc.tmpl", managed) == ("deployed",)


class TestPolicyExact:
    def test_every_entry_is_managed_or_repo_native(self, m, managed):
        unaccounted = sorted(
            e for e in m.POLICY_EXACT if e not in managed and e not in REPO_NATIVE
        )
        assert not unaccounted, (
            f"POLICY_EXACT names paths chezmoi does not manage: {unaccounted}"
        )

    def test_repo_native_entries_stay_out_of_the_deployed_tree(self, managed):
        leaked = sorted(REPO_NATIVE & managed)
        assert not leaked, (
            f"repo-native policy entries are now chezmoi-managed: {leaked}"
        )


class TestPolicyGlobs:
    def test_globs_cover_every_managed_policy_layer_file(self, m, managed):
        layer = {
            str(p.relative_to(PAYLOAD_ROOT))
            for p in (PAYLOAD_ROOT / "dotfiles" / "policy").iterdir()
            if p.is_file()
        }
        covered = layer & managed
        assert covered, "no dotfiles/policy file is both in the repo and managed"
        unmatched = sorted(
            p for p in covered if not any(fnmatch.fnmatch(p, g) for g in m.POLICY_GLOBS)
        )
        assert not unmatched, f"POLICY_GLOBS miss managed policy files: {unmatched}"
