"""Source-resolution tests for binned's self-improve edit target.

The self-improvement loop must edit the source chezmoi manages, not a guess.
When the payload moved under home/ (`.chezmoiroot`), the old hardcoded
~/.local/share/chezmoi/bin/executable_binned pointed at a file that was no
longer the source, and the test-context lookup's parent arithmetic
(src.parent.parent) landed in the payload root and silently found no tests.
Resolution now asks `chezmoi source-path` first, walks the git root as a
fallback, and anchors the test-context walk on that git root.

Fake trees follow tests/binned's tmp-dir pattern: a real directory tree with
a bare `.git` marker (find_git_root only checks existence), a deployed copy
outside the repo, and a PATH shim standing in for the chezmoi binary.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

BINNED_SOURCE = "#!/usr/bin/env python3\nprint('fake binned source')\n"
FAKE_TESTS = "# fake test_binned_property.py\n"


def _make_repo(root: Path, layout: str) -> Path:
    """Build a fake dotfiles repo with bin/ at the given layout position.

    layout "current" is today's tree (bin/ at the repo root); layout "home"
    is the post-`.chezmoiroot` tree (the payload, bin/ included, under
    home/ — the old bin/ location no longer holds the file).
    """
    bin_dir = root / "bin" if layout == "current" else root / "home" / "bin"
    bin_dir.mkdir(parents=True)
    (root / ".git").mkdir()
    (root / "tests").mkdir()
    (bin_dir / "executable_binned").write_text(BINNED_SOURCE)
    (root / "tests" / "test_binned_property.py").write_text(FAKE_TESTS)
    return root


def _make_deployed(tmp_path: Path) -> Path:
    """A deployed copy outside any repo, like ~/bin/binned."""
    deployed = tmp_path / "fakehome" / "bin" / "binned"
    deployed.parent.mkdir(parents=True)
    deployed.write_text("# deployed copy\n")
    return deployed


@pytest.fixture
def chezmoi_shim(tmp_path, monkeypatch):
    """A PATH shim standing in for `chezmoi source-path`.

    Call with the path the (fake) chezmoi should name as the source, or None
    to simulate "target not managed in source state" (exit 1). The shim
    exercises the real subprocess call: argv, stdout parsing, exit code.
    """
    shim_dir = tmp_path / "shim-bin"
    shim_dir.mkdir()

    def _install(source_path_output: str | None) -> None:
        shim = shim_dir / "chezmoi"
        if source_path_output is None:
            shim.write_text("#!/bin/sh\nexit 1\n")
        else:
            # The path is interpolated into the script body verbatim; test
            # paths contain no shell metacharacters.
            shim.write_text(f"#!/bin/sh\nprintf '%s\\n' '{source_path_output}'\n")
        shim.chmod(0o755)
        monkeypatch.setenv("PATH", f"{shim_dir}{os.pathsep}{os.environ['PATH']}")

    return _install


@pytest.fixture
def no_chezmoi(tmp_path, monkeypatch):
    """A PATH with nothing on it, so `chezmoi` is not found at all."""
    empty = tmp_path / "empty-path"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))


# ── resolve_source_path ───────────────────────────────────────────────────────


def test_tracks_chezmoi_answer_current_layout(binned_module, tmp_path, chezmoi_shim):
    """Today's layout: chezmoi manages <repo>/bin/executable_binned."""
    repo = _make_repo(tmp_path / "repo", "current")
    deployed = _make_deployed(tmp_path)
    chezmoi_shim(str(repo / "bin" / "executable_binned"))
    resolved = binned_module.resolve_source_path(deployed)
    assert resolved == repo / "bin" / "executable_binned"


def test_tracks_chezmoi_answer_after_home_move(binned_module, tmp_path, chezmoi_shim):
    """After the payload move the source lives under home/.

    The old code hardcoded ~/.local/share/chezmoi/bin/executable_binned —
    under the new layout that file no longer exists, so only a dynamic
    answer targets the real source. The fixture reproduces the moved tree:
    the source is at home/bin/, and the old bin/ location holds nothing.
    """
    repo = _make_repo(tmp_path / "repo", "home")
    assert not (repo / "bin" / "executable_binned").exists()
    deployed = _make_deployed(tmp_path)
    chezmoi_shim(str(repo / "home" / "bin" / "executable_binned"))
    resolved = binned_module.resolve_source_path(deployed)
    assert resolved == repo / "home" / "bin" / "executable_binned"
    assert resolved != deployed


def test_unmanaged_target_falls_back_to_git_walk(
    binned_module, tmp_path, monkeypatch, chezmoi_shim
):
    """The git-root walk takes over when chezmoi says not-managed."""
    repo = _make_repo(tmp_path / "repo", "current")
    deployed = _make_deployed(tmp_path)
    chezmoi_shim(None)
    monkeypatch.chdir(repo)
    resolved = binned_module.resolve_source_path(deployed)
    assert resolved == repo / "bin" / "executable_binned"


def test_git_walk_finds_source_without_chezmoi(
    binned_module, tmp_path, monkeypatch, no_chezmoi
):
    """No chezmoi binary at all (FileNotFoundError): the walk still
    finds in-repo source when run from a checkout.
    """
    repo = _make_repo(tmp_path / "repo", "current")
    _make_deployed(tmp_path)
    monkeypatch.chdir(repo)
    resolved = binned_module.resolve_source_path(
        tmp_path / "fakehome" / "bin" / "binned"
    )
    assert resolved == repo / "bin" / "executable_binned"


def test_chezmoi_answer_must_exist(
    binned_module, tmp_path, monkeypatch, chezmoi_shim, no_chezmoi
):
    """A chezmoi answer naming a missing file must not be trusted; with
    no repo to walk, resolution lands on the deployed copy (last
    resort).
    """
    deployed = _make_deployed(tmp_path)
    chezmoi_shim(str(tmp_path / "nowhere" / "executable_binned"))
    monkeypatch.chdir(tmp_path)
    assert binned_module.resolve_source_path(deployed) == deployed


def test_deployed_copy_is_the_last_resort(
    binned_module, tmp_path, monkeypatch, no_chezmoi
):
    """No chezmoi, no git root above cwd or the deployed dir: edit the
    deployed copy.
    """
    deployed = _make_deployed(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert binned_module.resolve_source_path(deployed) == deployed


# ── _collect_binned_tests: git-root anchor vs parent arithmetic ───────────────


def test_test_context_anchored_on_git_root_current_layout(binned_module, tmp_path):
    repo = _make_repo(tmp_path / "repo", "current")
    bin_dir = tmp_path / "fakehome" / "bin"
    bin_dir.mkdir(parents=True)
    found = binned_module._collect_binned_tests(
        repo / "bin" / "executable_binned", bin_dir
    )
    assert found == {"tests/test_binned_property.py": FAKE_TESTS}


def test_test_context_anchored_on_git_root_after_home_move(binned_module, tmp_path):
    """The old parent-arithmetic anchor (src.parent.parent) is home/
    after the move and finds no tests there; the git root still does.
    """
    repo = _make_repo(tmp_path / "repo", "home")
    src = repo / "home" / "bin" / "executable_binned"
    assert src.parent.parent == repo / "home"  # exactly the stale anchor
    assert not (repo / "home" / "tests").exists()
    bin_dir = tmp_path / "fakehome" / "bin"
    bin_dir.mkdir(parents=True)
    found = binned_module._collect_binned_tests(src, bin_dir)
    assert found == {"tests/test_binned_property.py": FAKE_TESTS}


def test_test_context_returns_empty_without_a_repo(binned_module, tmp_path):
    """No git root above the source or bin_dir: no test files, cleanly."""
    src_dir = tmp_path / "standalone" / "bin"
    src_dir.mkdir(parents=True)
    src = src_dir / "executable_binned"
    src.write_text(BINNED_SOURCE)
    bin_dir = tmp_path / "fakehome" / "bin"
    bin_dir.mkdir(parents=True)
    assert binned_module._collect_binned_tests(src, bin_dir) == {}
