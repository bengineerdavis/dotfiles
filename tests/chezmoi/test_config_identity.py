"""The identity data section must survive config-template rendering.

`.chezmoi.toml.tmpl` supplies `.email` and `.name` to `dot_gitconfig.tmpl`
through `promptStringOnce`, which most examples write with `{{- ... -}}` trim
markers. Those markers swallow the newline before `[data]`, so the section
header lands glued to the preceding comment line — `# …[data]` — and the whole
`[data]` section is commented out. The failure is silent in the worst way: the
template still renders, `.email` and `.name` come out empty, and git stamps
every commit with no identity.

This renders the template and asserts `[data]` is a real TOML header rather
than the tail of a comment.
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.skipif(
    shutil.which("chezmoi") is None, reason="chezmoi not installed"
)


def test_config_template_keeps_its_data_section():
    tmpl = REPO / ".chezmoi.toml.tmpl"
    out = subprocess.run(
        ["chezmoi", "execute-template", "--init", "--file",
         "--promptString", "email=x@y.z", "--promptString", "name=Test",
         str(tmpl)],
        capture_output=True, text=True, timeout=60,
    )
    assert out.returncode == 0, out.stderr

    rendered = out.stdout
    assert "\n[data]\n" in rendered, (
        "the [data] section header is missing or glued to another line — a "
        "trim marker has swallowed the newline before it, which comments the "
        "section out and blanks .email/.name"
    )
    assert "\n    email = " in rendered
    assert "\n    name = " in rendered