"""Fixture for real profile wrappers, without provider traffic."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def claude_environment(tmp_path):
    """Capture a fake Claude binary's inherited environment.

    The seam is the wrapper a shell or eval harness executes. The fake
    CLI is a plain shell script: it reports profile paths and whether
    conflicting credentials reached it, never any secret value.
    """
    binary = tmp_path / "claude"
    binary.write_text(
        "#!/bin/sh\n"
        'capture="${CLAUDE_TEST_CAPTURE}-$(basename "${CLAUDE_CONFIG_DIR:-unset}")"\n'
        'printf \'%s\\n\' "$@" > "$capture"\n'
        "for key in CLAUDE_CONFIG_DIR ANTHROPIC_BASE_URL; do\n"
        '  eval "value=\\${$key-unset}"\n'
        '  printf "%s=%s\\n" "$key" "$value"\n'
        "done\n"
        "for key in ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN"
        " CLAUDE_CODE_OAUTH_TOKEN; do\n"
        '  eval "present=\\${$key+set}"\n'
        '  printf "%s_present=%s\\n" "$key" "${present:-unset}"\n'
        "done\n"
    )
    binary.chmod(0o755)
    (tmp_path / ".localrc").write_text(
        "export ANTHROPIC_API_KEY=stale-anthropic-key\n"
        "export ANTHROPIC_AUTH_TOKEN=stale-auth-token\n"
        "export CLAUDE_CODE_OAUTH_TOKEN=stale-oauth-token\n"
    )
    return {
        "PATH": f"{tmp_path}:/usr/bin:/bin",
        "HOME": str(tmp_path),
        "CLAUDE_TEST_CAPTURE": str(tmp_path / "invocation"),
        "ANTHROPIC_API_KEY": "stale-anthropic-key",
        "ANTHROPIC_AUTH_TOKEN": "stale-auth-token",
        "ANTHROPIC_BASE_URL": "http://127.0.0.1:3207",
        "CLAUDE_CODE_OAUTH_TOKEN": "stale-oauth-token",
    }
