"""Meld must open with pane labels, from sections git actually reads.

Git looks up `mergetool.<name>.cmd` and `difftool.<name>.cmd` for the name in
`merge.tool` / `diff.tool`. A section written as `[mergetool ""]` sets
`mergetool..cmd` — an empty name — which git never consults, so its labels
silently never reach meld. That is the shape the hand-written config had
before 4342f6e deleted it.

This renders dot_gitconfig.tmpl and asks git itself what it resolves.
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.skipif(
    shutil.which("chezmoi") is None or shutil.which("git") is None,
    reason="chezmoi and git are required",
)


@pytest.fixture(scope="module")
def gitconfig(tmp_path_factory) -> pathlib.Path:
    out = subprocess.run(
        ["chezmoi", "execute-template", "--file", str(REPO / "dot_gitconfig.tmpl")],
        capture_output=True, text=True, timeout=60,
    )
    assert out.returncode == 0, out.stderr
    assert "[merge]" in out.stdout, "rendered nothing recognisable"
    path = tmp_path_factory.mktemp("gitconfig") / "gitconfig"
    path.write_text(out.stdout, encoding="utf-8")
    return path


def _get(cfg: pathlib.Path, key: str) -> str:
    out = subprocess.run(
        ["git", "config", "--file", str(cfg), "--get", key],
        capture_output=True, text=True,
    )
    assert out.returncode == 0, f"{key} is not set"
    return out.stdout.strip()


def test_mergetool_labels_all_three_panes(gitconfig):
    assert _get(gitconfig, "merge.tool") == "meld"
    assert _get(gitconfig, "mergetool.meld.cmd") == (
        'meld "$LOCAL" --label=LOCAL "$MERGED" --label=MERGED '
        '"$REMOTE" --label=REMOTE --output "$MERGED"'
    )


def test_difftool_labels_both_panes(gitconfig):
    assert _get(gitconfig, "diff.tool") == "meld"
    assert _get(gitconfig, "difftool.meld.cmd") == (
        'meld "$LOCAL" --label=LOCAL "$REMOTE" --label=REMOTE'
    )


def test_no_empty_named_tool_sections(gitconfig):
    out = subprocess.run(
        ["git", "config", "--file", str(gitconfig), "--get-regexp",
         r"^(merge|diff)tool\.\."],
        capture_output=True, text=True,
    )
    assert out.stdout == "", f"empty-named sections git never reads:\n{out.stdout}"
