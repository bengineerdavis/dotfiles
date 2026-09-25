"""Harness for running roles/restart-stale against stub supervisors.

The role's job is to restart things, so it cannot be exercised against the real
launchd, systemd or a real app: that would restart ollama or quit 1Password,
which other sessions depend on. Instead the commands it shells out to —
`launchctl`, `systemctl`, `ps`, `osascript`, `open` — are replaced by stubs on
PATH that read a scripted process table and log every call. The Ansible side is
real: the role is imported into a throwaway play exactly as a topic imports it,
and the binary's ctime is read from a real file under `tmp_path`.

Nothing outside `tmp_path` is read or written.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import textwrap

import pytest

from restart_stale_harness import DOTFILES, HARNESS

STUB = textwrap.dedent('''\
    #!{python}
    """Stub for {name}: answers from $RS_FAKE/state.json, logs to calls.jsonl."""
    import json, os, sys, time
    fake = os.environ["RS_FAKE"]
    state = json.load(open(os.path.join(fake, "state.json")))
    args = sys.argv[1:]
    # Fact gathering probes `ps -p 1 -o comm` for service_mgr. That is not the
    # role talking, so hand it to the real ps and keep it out of the log.
    if {name!r} == "ps" and "-o" in args and \\
            args[args.index("-o") + 1] not in ("pid=", "pid=,lstart=,comm="):
        os.execv("/bin/ps", ["ps"] + args)
    with open(os.path.join(fake, "calls.jsonl"), "a") as log:
        log.write(json.dumps([{name!r}] + args) + "\\n")
    quit_sent = os.path.exists(os.path.join(fake, "quit_sent"))

    def procs():
        gone = set(state.get("exits_on_quit", [])) if quit_sent else set()
        return [p for p in state.get("procs", []) if p["pid"] not in gone]

    if {name!r} == "launchctl":
        if args[:1] == ["list"]:
            print("PID\\tStatus\\tLabel")
            for label, pid in state.get("launchd", {{}}).items():
                print(f"{{pid}}\\t0\\t{{label}}")
        sys.exit(0)

    if {name!r} == "systemctl":
        units = state.get("systemd", {{}})
        if "--value" in args:                      # the role's MainPID probe
            print(units.get(args[-1], 0))
        elif "show" in args:                       # systemd_service's status read
            unit = args[-1]
            pid = units.get(unit, 0)
            print(f"Id={{unit}}\\nNames={{unit}}\\nLoadState=loaded\\n"
                  f"ActiveState={{'active' if pid else 'inactive'}}\\n"
                  f"SubState={{'running' if pid else 'dead'}}\\nMainPID={{pid}}\\n"
                  "UnitFileState=enabled")
        sys.exit(0)

    if {name!r} == "ps":
        fmt = args[args.index("-o") + 1]
        if fmt == "pid=" and "exit_probe_error" in state:
            error = state["exit_probe_error"]
            print(error["stderr"], file=sys.stderr)
            sys.exit(error["rc"])
        if fmt != "pid=" and "process_probe_error" in state:
            error = state["process_probe_error"]
            print(error["stderr"], file=sys.stderr)
            sys.exit(error["rc"])
        rows = procs()
        if "-p" in args:
            rows = [p for p in rows if str(p["pid"]) == args[args.index("-p") + 1]]
        for p in rows:
            if fmt == "pid=":
                print(p["pid"])
            else:
                lstart = time.strftime("%a %b %e %H:%M:%S %Y", time.gmtime(p["start"]))
                print(f"{{p['pid']:>5}} {{lstart}}     {{p['comm']}}")
        sys.exit(0 if rows else 1)

    if {name!r} == "osascript":
        rc = state.get("quit_rc", 0)
        if rc:
            print(state.get("quit_stderr", "execution error"), file=sys.stderr)
            sys.exit(rc)
        open(os.path.join(fake, "quit_sent"), "w").close()
        sys.exit(0)

    sys.exit(0)   # open
''')

STUBBED = ["launchctl", "systemctl", "ps", "osascript", "open"]


@pytest.fixture(scope="session")
def ansible_playbook() -> str:
    exe = shutil.which("ansible-playbook")
    if not exe:
        pytest.skip("ansible-playbook not on PATH — run: mise install")
    return exe


class Machine:
    """A scripted process table plus a real binary whose ctime is the truth."""

    def __init__(self, root: pathlib.Path) -> None:
        self.root = root
        self.fake = root / "fake"
        self.bin = root / "stubs"
        self.fake.mkdir()
        self.bin.mkdir()
        for name in STUBBED:
            stub = self.bin / name
            stub.write_text(STUB.format(python=sys.executable, name=name))
            stub.chmod(0o755)
        self.state: dict = {"procs": []}

    def binary(self, relpath: str = "Cellar/thing/2/thing",
               bottle_age: float = 0) -> pathlib.Path:
        """A real file to stand in for the binary.

        `bottle_age` backdates its mtime the way a Homebrew bottle does. Setting
        mtime is itself an inode change, so ctime stays "now": the file ends up
        with an old mtime and a current ctime, exactly as installed binaries do.
        """
        path = self.root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/bin/sh\n")
        if bottle_age:
            old = os.stat(path).st_mtime - bottle_age
            os.utime(path, (old, old))
        return path

    @staticmethod
    def ctime(path: pathlib.Path) -> float:
        return os.stat(path).st_ctime

    def process(self, pid: int, start: float, comm: str) -> None:
        self.state["procs"].append({"pid": pid, "start": int(start), "comm": comm})

    def calls(self, name: str | None = None) -> list[list[str]]:
        log = self.fake / "calls.jsonl"
        if not log.exists():
            return []
        calls = [json.loads(line) for line in log.read_text().splitlines()]
        return [c for c in calls if name is None or c[0] == name]

    def env(self) -> dict:
        (self.fake / "state.json").write_text(json.dumps(self.state))
        return {
            **os.environ,
            "PATH": f"{self.bin}{os.pathsep}{os.environ['PATH']}",
            "RS_FAKE": str(self.fake),
        }


@pytest.fixture
def machine(tmp_path) -> Machine:
    return Machine(tmp_path)


@pytest.fixture
def run_role(ansible_playbook, tmp_path, machine):
    """Run the role with these parameters against `machine`."""

    def _run(*flags: str, **params) -> subprocess.CompletedProcess:
        play = tmp_path / "harness.yaml"
        play.write_text(HARNESS, encoding="utf-8")
        params.setdefault("restart_stale_caller", "tests/restart_stale")
        return subprocess.run(
            [ansible_playbook, "-i", "localhost,", str(play),
             "-e", json.dumps(params), *flags],
            cwd=DOTFILES,
            env=machine.env(),
            capture_output=True,
            text=True,
            timeout=180,
        )

    return _run
