"""The launchd service-manager seam for the Lore gateway."""

from loreai_service_helpers import run_service_command


def test_launchd_command_replaces_adopted_gateway_with_local_mode(tmp_path):
    result = run_service_command(tmp_path, "launchd")
    calls = (tmp_path / "call-log").read_text().splitlines()
    assert calls[:3] == ["start --local", "stop", "start --local"]
    assert result.returncode == 1


def test_launchd_command_supervises_until_gateway_disappears(tmp_path):
    result = run_service_command(tmp_path, "launchd")
    assert result.returncode == 1, result.stderr
    assert (tmp_path / "doctor-count").read_text().strip() == "3"
