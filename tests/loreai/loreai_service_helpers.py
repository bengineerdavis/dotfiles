"""Shared rendering helpers for Lore service seam tests."""

from __future__ import annotations

import os
from pathlib import Path
import plistlib
import re
import shlex
import subprocess

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT
import jinja2

TOPIC = PAYLOAD_ROOT / "dotfiles" / "apps" / "loreai"
JINJA = jinja2.Environment(undefined=jinja2.StrictUndefined)
JINJA.tests["match"] = lambda value, pattern: re.match(str(pattern), str(value))


def render(template_name: str, **variables) -> str:
    template = JINJA.from_string((TOPIC / "templates" / template_name).read_text())
    return template.render(**variables)


def render_env_file() -> str:
    return render(
        "loreai-env.zsh.j2",
        ansible_date_time={"date": "2026-10-27"},
        loreai_telemetry_final=1,
        loreai_inference_final="openrouter",
        loreai_local_upstream="http://localhost:11434",
        loreai_worker_model_final="openrouter/z-ai/glm-5.3-flash",
        loreai_openai_upstream="https://openrouter.ai/api",
        loreai_worker_model_candidates=[],
        loreai_worker_model_local_candidates=[],
    )


def service_command(tmp_path, manager: str) -> tuple[list[str], str]:
    """Return the command a rendered service manager would run."""
    env_file = tmp_path / "env.zsh"
    env_file.write_text('export OPENROUTER_API_KEY="$(llm keys get openrouter)"\n')
    variables = {
        "ansible_env": {"HOME": str(tmp_path)},
        "loreai_env_file": str(env_file),
        "loreai_install_dir": str(tmp_path),
        "loreai_service_path": f"{tmp_path / 'bin'}:{os.defpath}",
        "loreai_gateway_label": "ai.withlore.gateway",
        "loreai_logs_dir": str(tmp_path),
    }
    if manager == "launchd":
        document = render("lore-gateway.plist.j2", **variables)
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE'
            + document.split("<!DOCTYPE", 1)[1]
        )
        plist = plistlib.loads(body.encode())
        return plist["ProgramArguments"], plist["EnvironmentVariables"]["PATH"]

    document = render("lore-gateway.service.j2", **variables)
    exec_start = next(
        line for line in document.splitlines() if line.startswith("ExecStart=")
    )
    # systemd turns $$ into a literal dollar before invocation.
    command = shlex.split(exec_start.removeprefix("ExecStart=").replace("$$", "$"))
    path = next(
        line.removeprefix('Environment="PATH=').removesuffix('"')
        for line in document.splitlines()
        if line.startswith('Environment="PATH=')
    )
    return command, path


def run_service_command(tmp_path, manager):
    """Execute a rendered launch command with stub binaries."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    llm = bin_dir / "llm"
    llm.write_text("#!/bin/sh\nprintf 'dummy-openrouter-key\\n'\n")
    llm.chmod(0o755)
    lore = tmp_path / "lore"
    lore.write_text(
        "#!/bin/sh\n"
        'printf \'%s\\n\' "$*" >> "$LORE_TEST_CALL_LOG"\n'
        'case "$1" in\n'
        "  start)\n"
        '    [ "$2" = --local ] '
        '&& [ "$OPENROUTER_API_KEY" = dummy-openrouter-key ] '
        '&& [ "$LORE_WORKER_API_KEY" = dummy-openrouter-key ] || exit 90\n'
        "    exit 0 ;;\n"
        "  stop)\n"
        "    exit 0 ;;\n"
        "  doctor)\n"
        "    count=0\n"
        '    [ ! -f "$LORE_TEST_DOCTOR_COUNT" ] || '
        'count=$(cat "$LORE_TEST_DOCTOR_COUNT")\n'
        "    count=$((count + 1))\n"
        '    printf \'%s\\n\' "$count" > "$LORE_TEST_DOCTOR_COUNT"\n'
        '    if [ "$count" -le 2 ]; then\n'
        "      printf '[lore] [PASS] gateway reachable: responding on port 3207\\n'\n"
        "      exit 0\n"
        "    fi\n"
        "    exit 1 ;;\n"
        "esac\n"
    )
    lore.chmod(0o755)
    sleep = bin_dir / "sleep"
    sleep.write_text("#!/bin/sh\nexit 0\n")
    sleep.chmod(0o755)
    command, path = service_command(tmp_path, manager)
    port_file = tmp_path / ".local" / "share" / "lore" / "gateway.port"
    port_file.parent.mkdir(parents=True)
    port_file.write_text("3207\n")

    return subprocess.run(
        command,
        env={
            "HOME": str(tmp_path),
            "PATH": path,
            "LORE_TEST_DOCTOR_COUNT": str(tmp_path / "doctor-count"),
            "LORE_TEST_CALL_LOG": str(tmp_path / "call-log"),
        },
        capture_output=True,
        text=True,
        check=False,
    )
