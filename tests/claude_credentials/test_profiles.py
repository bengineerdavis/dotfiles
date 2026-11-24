"""Claude's OAuth profile must not inherit gateway API credentials."""

from claude_credentials_harness import invoke


def test_direct_subprocess_inherits_oauth_profile(claude_environment):
    result = invoke(claude_environment, "eval", "command claude auth status")

    assert result.returncode == 0, result.stderr
    assert (
        "CLAUDE_CONFIG_DIR=" + claude_environment["HOME"] + "/.claude-direct"
        in result.stdout
    )


def test_lore_after_direct_in_same_shell_restores_gateway_credential(
    claude_environment,
):
    result = invoke(
        claude_environment,
        "eval",
        "claude auth status; claude-lore auth status",
    )

    assert result.returncode == 0, result.stderr
    assert "ANTHROPIC_API_KEY_present=set" in result.stdout


def test_direct_claude_uses_oauth_profile_without_gateway_credentials(
    claude_environment,
):
    result = invoke(claude_environment, "claude", "auth", "status")

    assert result.returncode == 0, result.stderr
    assert (
        "CLAUDE_CONFIG_DIR=" + claude_environment["HOME"] + "/.claude-direct"
        in result.stdout
    )
    assert "ANTHROPIC_BASE_URL=unset" in result.stdout
    assert "ANTHROPIC_API_KEY_present=unset" in result.stdout
    assert "ANTHROPIC_AUTH_TOKEN_present=unset" in result.stdout
    assert "CLAUDE_CODE_OAUTH_TOKEN_present=unset" in result.stdout


def test_lore_wrapper_preserves_gateway_route_and_credential(claude_environment):
    result = invoke(claude_environment, "claude-lore", "auth", "status")

    assert result.returncode == 0, result.stderr
    assert (
        "CLAUDE_CONFIG_DIR=" + claude_environment["HOME"] + "/.claude" in result.stdout
    )
    assert "ANTHROPIC_BASE_URL=http://127.0.0.1:3207" in result.stdout
    assert "ANTHROPIC_API_KEY_present=set" in result.stdout


def test_direct_wrapper_does_not_change_lore_environment(claude_environment):
    invoke(claude_environment, "claude", "auth", "status")
    result = invoke(claude_environment, "claude-lore", "auth", "status")

    assert "ANTHROPIC_BASE_URL=http://127.0.0.1:3207" in result.stdout
    assert "ANTHROPIC_API_KEY_present=set" in result.stdout
