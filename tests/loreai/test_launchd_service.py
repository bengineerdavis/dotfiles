"""The launchd service-manager seam for the Lore gateway."""

from loreai_service_helpers import run_service_command


def test_launchd_command_supplies_credentials_and_supervises_adoption(tmp_path):
    result = run_service_command(tmp_path, "launchd")
    assert result.returncode == 1, result.stderr
