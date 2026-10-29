"""Select documentation links without weakening the egress boundary."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "check-docs-links.py"
spec = importlib.util.spec_from_file_location("check_docs_links", SCRIPT)
assert spec and spec.loader
links = importlib.util.module_from_spec(spec)
spec.loader.exec_module(links)


def hook(hook_id: str) -> dict:
    config = yaml.safe_load((REPO / ".pre-commit-config.yaml").read_text())
    return next(
        hook
        for repo in config["repos"]
        for hook in repo.get("hooks", [])
        if hook.get("id") == hook_id
    )


@pytest.mark.parametrize(
    "path",
    [
        ".lore.md",
        "backlog/tasks/DOT-1.md",
        "changelog.d/fragment.md",
        "CHANGELOG.md",
        "home/bin/executable_READMD.archive.md",
        "home/dotfiles/apps/ollama/docs/RESEARCH.md",
        "scripts/README.txt",
        "../outside.md",
    ],
)
def test_excluded_documents_are_never_selected(path: str):
    assert not links.is_selected(path)


def test_full_scan_uses_tracked_markdown_and_never_dot(tmp_path: Path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("[local](target.md)")
    (tmp_path / ".lore.md").write_text("[private](https://example.com)")
    (tmp_path / "untracked.md").write_text("[broken](missing.md)")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "docs/guide.md", ".lore.md"], check=True
    )
    assert links.tracked_markdown(tmp_path) == ["docs/guide.md"]


def test_offline_command_cannot_make_network_requests():
    command = links.lychee_command(["docs/guide.md"], external=False)
    assert "--offline" in command
    assert "--offline=false" not in command
    assert command[-2:] == ["--files-from", "-"]


def test_external_mode_is_explicit_and_not_an_unattended_hook():
    assert "--external" in links.USAGE
    assert hook("docs-links-local")["entry"].endswith("--changed")
    assert hook("docs-links-full")["stages"] == ["pre-push"]
    assert "--external" not in hook("docs-links-local")["entry"]
    assert "--external" not in hook("docs-links-full")["entry"]


def test_external_mode_requires_explicit_approval(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("LYCHEE_EXTERNAL_APPROVED", raising=False)
    with pytest.raises(SystemExit) as error:
        links.parse_args(["--external", "--changed"])
    assert error.value.code == 2


def test_unapproved_external_run_does_not_invoke_lychee(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.delenv("LYCHEE_EXTERNAL_APPROVED", raising=False)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("Lychee ran without approval")

    monkeypatch.setattr(links.subprocess, "run", fail_if_called)
    assert links.main(["--external"]) == 2


def test_real_lychee_detects_broken_local_link(tmp_path: Path):
    document = tmp_path / "broken.md"
    document.write_text("[missing](missing.md)\n")
    result = subprocess.run(
        [*links.lychee_command([str(document)], external=False)[:-2], str(document)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode != 0
    assert "missing.md" in result.stdout + result.stderr


def test_changed_scope_does_not_expand_to_the_whole_repository():
    args = links.parse_args(["--changed", "docs/guide.md"])
    assert args.changed
    assert args.files == ["docs/guide.md"]


def test_changed_scope_only_checks_selected_tracked_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("[local](target.md)")
    (tmp_path / "other.md").write_text("[broken](missing.md)")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    calls: list[tuple[list[str], dict]] = []

    def record(command, **kwargs):
        calls.append((command, kwargs))
        stdout = b"docs/guide.md\0" if command[:2] == ["git", "-C"] else None
        return subprocess.CompletedProcess(command, 0, stdout=stdout)

    monkeypatch.setattr(links, "CONFIG", tmp_path / "lychee.toml")
    (tmp_path / "lychee.toml").write_text("offline = true\n")
    monkeypatch.setattr(links.subprocess, "run", record)
    assert links.main(["--changed", "docs/guide.md"], repo=tmp_path) == 0
    lychee_calls = [(call, kwargs) for call, kwargs in calls if "lychee" in call]
    assert len(lychee_calls) == 1
    command, kwargs = lychee_calls[0]
    assert "--offline" in command
    assert kwargs["input"] == "docs/guide.md\n"
    assert "other.md" not in kwargs["input"]
