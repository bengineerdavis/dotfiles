"""Global Git files are managed, portable, and contain no default message.

A comment-only commit template guides an editor without supplying a reusable
commit message. The behavior check uses Git's own comment stripping and an
editor that only records the supplied template; it creates an isolated empty
repository and commits only there when deliberately testing a broken template.
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess

import pytest

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

pytestmark = pytest.mark.skipif(
    shutil.which("chezmoi") is None or shutil.which("git") is None,
    reason="chezmoi and git are required",
)


@pytest.fixture(scope="module")
def managed() -> set[str]:
    out = subprocess.run(
        [
            "chezmoi",
            "-S",
            str(PAYLOAD_ROOT),
            "managed",
            "--path-style=source-relative",
            "--include=files",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert out.returncode == 0, out.stderr
    paths = set(out.stdout.split())
    assert "dot_gitconfig.tmpl" in paths, "empty or incomplete chezmoi inventory"
    return paths


@pytest.fixture(scope="module")
def rendered_gitconfig(tmp_path_factory) -> pathlib.Path:
    out = subprocess.run(
        [
            "chezmoi",
            "-S",
            str(PAYLOAD_ROOT),
            "execute-template",
            "--file",
            str(PAYLOAD_ROOT / "dot_gitconfig.tmpl"),
            "--override-data",
            '{"email":"person@example.invalid","name":"Example Person"}',
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert out.returncode == 0, out.stderr
    path = tmp_path_factory.mktemp("git-global") / "gitconfig"
    path.write_text(out.stdout, encoding="utf-8")
    return path


def _get(config: pathlib.Path, key: str) -> str:
    out = subprocess.run(
        ["git", "config", "--file", str(config), "--get", key],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert out.returncode == 0, f"{key} is missing: {out.stderr}"
    return out.stdout.strip()


def test_global_git_files_are_managed(managed):
    assert {
        "dot_gitconfig.tmpl",
        "dot_gitignore_global",
        "dot_commit-message-template",
    } <= managed


def test_global_paths_and_identity_are_portable(rendered_gitconfig):
    assert _get(rendered_gitconfig, "core.excludesfile") == str(
        pathlib.Path.home() / ".gitignore_global"
    )
    assert _get(rendered_gitconfig, "commit.template") == str(
        pathlib.Path.home() / ".commit-message-template"
    )
    assert "{{" not in _get(rendered_gitconfig, "user.name")
    assert "{{" not in _get(rendered_gitconfig, "user.email")
    assert _get(rendered_gitconfig, "user.name") == "Example Person"
    assert _get(rendered_gitconfig, "user.email") == "person@example.invalid"


def test_global_excludes_capture_local_tool_files():
    assert (PAYLOAD_ROOT / "dot_gitignore_global").read_text() == (
        "# Global ignores for machine-local tool configuration.\n"
        "mise.local.toml\n"
        ".mise.local.toml\n\n"
        "**/.claude/settings.local.json\n"
    )


def test_commit_template_has_guidance_but_no_message():
    template = (PAYLOAD_ROOT / "dot_commit-message-template").read_text()
    assert "imperative" in template
    assert "reviewable decision" in template
    assert "problem" in template
    assert "trailers" in template
    assert all(not line or line.startswith("#") for line in template.splitlines())
    stripped = subprocess.run(
        ["git", "stripspace", "--strip-comments"],
        input=template,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert stripped.returncode == 0, stripped.stderr
    assert stripped.stdout == "", "the template would supply a commit message"


def test_git_editor_receives_only_commented_guidance(tmp_path):
    template = PAYLOAD_ROOT / "dot_commit-message-template"
    repo = tmp_path / "repo"
    repo.mkdir()
    captured = tmp_path / "captured-message"
    editor = tmp_path / "record-editor"
    editor.write_text(f'#!/bin/sh\ncp "$1" "{captured}"\n', encoding="utf-8")
    editor.chmod(0o755)
    env = {
        **os.environ,
        "HOME": str(tmp_path),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_EDITOR": str(editor),
    }

    def git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                "git",
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.invalid",
                "-c",
                f"commit.template={template}",
                *args,
            ],
            cwd=repo,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )

    initialized = git("init", "--quiet")
    assert initialized.returncode == 0, initialized.stderr
    committed = git("commit", "--allow-empty")
    assert committed.returncode != 0, "a comment-only template committed a message"
    assert "empty commit message" in committed.stdout + committed.stderr
    captured_text = captured.read_text()
    assert template.read_text() in captured_text
    assert all(
        not line or line.startswith("#") for line in captured_text.splitlines()
    ), "Git supplied uncommented commit-message text"
