"""Filters for roles/restart-stale: is a running process older than its binary?

Pure functions, no Ansible imports, so tests/restart_stale can call them
directly and a hypothesis run costs milliseconds instead of a playbook each.

Why ctime, and only ctime
-------------------------
A process is stale when it started before its binary's **ctime** (inode change
time). mtime and birthtime look like the obvious choices and are both wrong
for Homebrew, measured on 2026-09-22 against the ollama 0.34.3 binary:

    mtime   2026-09-18 17:15:35   copied from the bottle archive
    birth   2026-09-18 17:15:35   also the bottle's; Homebrew preserves it
    ctime   2026-09-22 17:52:10   the actual install

A server started 2026-09-20 on the old version is older than the install but
newer than both of the first two, so an mtime check calls it fresh. ctime is
set by the kernel when the file is written into place and cannot be copied
from an archive. It also moves on chmod, chown and xattr changes; that can
cost an unneeded restart, which is the safe direction.

Start times come from `ps -o lstart=` run under TZ=UTC and LC_ALL=C, so the
text is locale-independent and parses as UTC without a timezone database.
lstart is whole seconds, truncated. Comparing the truncated start against a
sub-second ctime can only move a verdict toward stale, never away from it.
"""

from __future__ import annotations

import calendar
import time

LSTART_FORMAT = "%a %b %d %H:%M:%S %Y"
# pid, then lstart's five fields (weekday month day time year), then the
# command, which may itself contain spaces.
_PS_FIELDS = 7


def _utc(epoch: float) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(epoch))


def parse_lstart(text: str) -> int:
    """Epoch seconds for an lstart value printed under TZ=UTC LC_ALL=C."""
    return calendar.timegm(time.strptime(" ".join(text.split()), LSTART_FORMAT))


def ps_rows(text: str) -> list[dict]:
    """Rows of `ps -o pid=,lstart=,comm=` output as {pid, start, comm}.

    An unreadable row raises rather than being skipped: a dropped row reads as
    "not running", which is a verdict, and an unreadable one is an unknown.
    """
    rows = []
    for line in text.splitlines():
        if not line.strip():
            continue
        fields = line.split(None, _PS_FIELDS - 1)
        if len(fields) < _PS_FIELDS or not fields[0].isdigit():
            raise ValueError(f"unexpected ps row: {line!r}")
        pid, *start, comm = fields
        rows.append(
            {
                "pid": int(pid),
                "start": parse_lstart(" ".join(start)),
                "comm": comm.rstrip(),
            }
        )
    return rows


def launchd_pid(text: str, label: str) -> int:
    """PID of `label` in `launchctl list` output; 0 when not running or absent.

    The table is tab-separated `PID  Status  Label`, with `-` as the PID of a
    job that is loaded but not running.
    """
    for line in text.splitlines():
        fields = line.split("\t", 2)
        if len(fields) == 3 and fields[2] == label:
            return int(fields[0]) if fields[0].isdigit() else 0
    return 0


def verdict(rows: list[dict], ctime: float | None, comm: str | None = None) -> dict:
    """Whether a restart is owed, and a sentence saying why.

    rows  ps rows for the candidate processes
    ctime the binary's ctime, symlinks resolved; None when it does not exist
    comm  if given, only rows whose executable path is exactly this count.
          An app's helpers share its bundle, and a prefix match would let a
          helper's age decide.
    """
    candidates = [r for r in rows if comm is None or r["comm"] == comm]
    if not candidates:
        return {
            "running": False,
            "stale": False,
            "pid": 0,
            "started": None,
            "reason": "not running, so it will start on the current binary",
        }

    oldest = min(candidates, key=lambda r: r["start"])
    base = {"running": True, "pid": oldest["pid"], "started": _utc(oldest["start"])}

    if ctime is None:
        return {
            **base,
            "stale": False,
            "reason": "binary not found, so there is nothing to restart onto",
        }

    if oldest["start"] < ctime:
        return {
            **base,
            "stale": True,
            "reason": f"pid {oldest['pid']} started {_utc(oldest['start'])}, "
            f"before the binary changed at {_utc(ctime)}",
        }
    return {
        **base,
        "stale": False,
        "reason": f"pid {oldest['pid']} started {_utc(oldest['start'])}, "
        f"after the binary changed at {_utc(ctime)}",
    }


class FilterModule:
    def filters(self):
        return {
            "restart_stale_ps_rows": ps_rows,
            "restart_stale_launchd_pid": launchd_pid,
            "restart_stale_verdict": verdict,
        }
