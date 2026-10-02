"""The stale-or-fresh decision, as pure functions.

The rule: a running process is stale when it started before its binary's
ctime. Not mtime, not birthtime — both come from the Homebrew bottle and
predate the install. Measured on 2026-09-22 against the ollama 0.34.3 binary:

    mtime   2026-09-18 17:15:35   bottle build time
    birth   2026-09-18 17:15:35   also bottle time; Homebrew preserves it
    ctime   2026-09-22 17:52:10   the install

A server started 2026-09-20 on 0.33.3 looks fresh against the first two. That
is the incident these tests exist for, so it is the first example below.

Every property states the rule from the outside. None of them recomputes
`start < ctime` and compares — that would prove the code equals itself.

Run:
    uv run --with pytest --with hypothesis pytest tests/restart_stale -q
"""

from __future__ import annotations

import calendar
import math
import string
import time

import pytest

pytest.importorskip("hypothesis", reason="hypothesis not installed")

from hypothesis import given
from hypothesis import strategies as st
from restart_stale_harness import load_filters

rs = load_filters()

PDT = -7 * 3600


def pdt(text: str) -> float:
    """Epoch seconds for a wall-clock time in PDT, as written in the incident."""
    return calendar.timegm(time.strptime(text, "%Y-%m-%d %H:%M:%S")) - PDT


def lstart(epoch: float) -> str:
    """What `TZ=UTC LC_ALL=C ps -o lstart=` prints for a process started then.

    macOS pads a single-digit day with a space (`Sep  5`); procps-ng 4.0.4 on
    Debian prints the same layout. Both measured, not assumed.
    """
    return time.strftime("%a %b %e %H:%M:%S %Y", time.gmtime(epoch))


def row(pid: int, start: float, comm: str = "/opt/homebrew/bin/ollama") -> dict:
    return {"pid": pid, "start": math.floor(start), "comm": comm}


# ── the incident ─────────────────────────────────────────────────────────────


def test_the_2026_09_22_server_is_stale_by_ctime():
    started = pdt("2026-09-20 09:00:00")  # running 0.33.3
    ctime = pdt("2026-09-22 17:52:10")  # brew installed 0.34.3
    mtime = pdt("2026-09-18 17:15:35")  # what a naive check would read

    verdict = rs.verdict([row(37089, started)], ctime)

    assert verdict["stale"] is True
    assert verdict["pid"] == 37089
    # The same process judged against mtime would pass as fresh. Keeping the
    # contrast in the test is the point: it is the check that must not return.
    assert started > mtime


def test_the_server_restarted_at_19_03_is_fresh():
    """The machine's state when this was written: restarted onto 0.34.3."""
    verdict = rs.verdict(
        [row(37089, pdt("2026-09-22 19:03:34"))], pdt("2026-09-22 17:52:10")
    )
    assert verdict["stale"] is False
    assert verdict["running"] is True


# ── the rule, for all inputs ─────────────────────────────────────────────────

epochs = st.floats(min_value=0, max_value=4_000_000_000, allow_nan=False)
gaps = st.floats(min_value=1, max_value=10 * 365 * 86400, allow_nan=False)


@given(ctime=st.one_of(epochs, st.none()))
def test_never_stale_when_nothing_is_running(ctime):
    """Not running means it will start on the new binary. Nothing to do."""
    verdict = rs.verdict([], ctime)
    assert verdict["stale"] is False
    assert verdict["running"] is False


@given(start=epochs, gap=gaps)
def test_started_before_the_binary_changed_is_stale(start, gap):
    assert rs.verdict([row(1, start)], start + gap)["stale"] is True


@given(ctime=epochs, gap=gaps)
def test_started_a_second_or_more_after_the_binary_changed_is_fresh(ctime, gap):
    assert rs.verdict([row(1, ctime + gap)], ctime)["stale"] is False


@given(true_start=epochs, gap=st.floats(min_value=1e-3, max_value=86400))
def test_whole_second_start_times_never_hide_a_stale_process(true_start, gap):
    """`ps` reports start to the second, truncated. The binary's ctime has
    sub-second precision. A process that truly started before the binary
    changed must still read as stale after truncation — including when both
    fall inside the same second. Truncation may cost an extra restart; it may
    never cost a missed one."""
    reported = math.floor(true_start)
    assert rs.verdict([row(1, reported)], true_start + gap)["stale"] is True


@given(start=epochs, ctime=epochs, later=gaps)
def test_a_later_binary_change_never_makes_a_process_fresher(start, ctime, later):
    """Metamorphic: move the change later and a stale verdict must stand."""
    if rs.verdict([row(1, start)], ctime)["stale"]:
        assert rs.verdict([row(1, start)], ctime + later)["stale"] is True


@given(starts=st.lists(epochs, min_size=1, max_size=5), ctime=epochs)
def test_one_stale_instance_makes_the_whole_thing_stale(starts, ctime):
    """For an app matched by path there can be several processes. If any of
    them is older than the binary, a restart is owed."""
    rows = [row(i + 1, s) for i, s in enumerate(starts)]
    any_old = any(math.floor(s) < ctime for s in starts)
    assert rs.verdict(rows, ctime)["stale"] is any_old


@given(start=epochs)
def test_a_missing_binary_is_reported_not_restarted(start):
    """Restarting onto a binary that is not there would fail — or worse,
    succeed onto nothing. Report and leave it."""
    verdict = rs.verdict([row(1, start)], None)
    assert verdict["stale"] is False
    assert verdict["running"] is True
    assert "not found" in verdict["reason"]


# ── matching an app by its executable path ───────────────────────────────────

OP = "/Applications/1Password.app/Contents/MacOS/1Password"
# These are the real process paths 1Password runs on this Mac (names of
# software, not user data). Each one starts with the main binary's path or
# shares its directory, so each is a near-miss a prefix match would accept.
OP_NEIGHBOURS = [
    "/Applications/1Password.app/Contents/MacOS/1Password-Crash-Handler",
    (
        "/Applications/1Password.app/Contents/Frameworks/1Password Helper.app"
        "/Contents/MacOS/1Password Helper"
    ),
    (
        "/Applications/1Password.app/Contents/Library/LoginItems/1Password Browser"
        " Helper.app/Contents/MacOS/1Password-BrowserSupport"
    ),
]


def test_only_the_main_binary_counts_for_an_app():
    old = pdt("2026-09-01 00:00:00")
    rows = [row(10 + i, old, comm) for i, comm in enumerate(OP_NEIGHBOURS)]
    rows.append(row(1597, pdt("2026-09-12 11:48:55"), OP))

    verdict = rs.verdict(rows, pdt("2026-09-08 17:58:28"), comm=OP)

    assert verdict["pid"] == 1597
    assert verdict["stale"] is False, "a helper's age decided the verdict"


@given(
    suffix=st.text(alphabet=string.ascii_letters + " -_.()/", min_size=1, max_size=12)
)
def test_a_path_that_merely_starts_with_the_binary_never_matches(suffix):
    rows = [row(1, 0, OP + suffix)]
    assert rs.verdict(rows, 1.0, comm=OP)["running"] is False


# ── parsing ps ───────────────────────────────────────────────────────────────


def test_parses_ps_rows_as_macos_prints_them():
    text = (
        "37089 Wed Sep 23 02:03:34 2026     /opt/homebrew/bin/ollama\n"
        "  920 Sat Sep  5 00:38:36 2026     /Applications/1Password.app/Contents"
        "/Frameworks/1Password Helper (Renderer).app/Contents/MacOS/1Password"
        " Helper (Renderer)   \n"
    )
    rows = rs.ps_rows(text)

    assert rows[0] == {
        "pid": 37089,
        "start": calendar.timegm((2026, 9, 23, 2, 3, 34, 0, 0, 0)),
        "comm": "/opt/homebrew/bin/ollama",
    }
    assert rows[1]["pid"] == 920
    assert rows[1]["start"] == calendar.timegm((2026, 9, 5, 0, 38, 36, 0, 0, 0))
    assert rows[1]["comm"].endswith("1Password Helper (Renderer)")


def test_no_output_is_no_processes():
    assert rs.ps_rows("") == []
    assert rs.ps_rows("\n  \n") == []


@pytest.mark.parametrize(
    "line",
    [
        "37089",  # truncated
        "37089 Wed Sep 23 02:03:34 2026",  # no command
        "abc Wed Sep 23 02:03:34 2026 /bin/x",  # pid not a number
        "37089 Mitt Sep 23 02:03:34 2026 /bin/x",  # a locale ps was not run in
    ],
)
def test_an_unreadable_row_is_an_error_not_a_skip(line):
    """Dropping a row would read as "not running", which is a verdict. An
    unreadable row is an unknown, and unknowns must not become verdicts."""
    with pytest.raises(ValueError):
        rs.ps_rows(line)


comms = (
    st.text(
        alphabet=string.ascii_letters + string.digits + " ()-_./",
        min_size=1,
        max_size=40,
    )
    .map(str.strip)
    .filter(bool)
)


@given(
    entries=st.lists(
        st.tuples(st.integers(1, 99999), st.integers(0, 4_000_000_000), comms),
        max_size=6,
    ),
    pad=st.integers(0, 6),
)
def test_ps_rows_round_trips_what_ps_prints(entries, pad):
    text = "".join(
        f"{pid:>{pad}} {lstart(start)}{' ' * pad} {comm}\n"
        for pid, start, comm in entries
    )
    assert rs.ps_rows(text) == [
        {"pid": pid, "start": start, "comm": comm} for pid, start, comm in entries
    ]


# ── parsing launchctl list ───────────────────────────────────────────────────

LAUNCHCTL_LIST = (
    "PID\tStatus\tLabel\n"
    "-\t0\tcom.ollama-models.check\n"
    "37089\t-9\tcom.ollama.server\n"
    "-\t0\tcom.ollama-usage.snapshot\n"
)


def test_launchd_pid_of_a_running_agent():
    assert rs.launchd_pid(LAUNCHCTL_LIST, "com.ollama.server") == 37089


def test_launchd_loaded_but_not_running_is_zero():
    assert rs.launchd_pid(LAUNCHCTL_LIST, "com.ollama-models.check") == 0


def test_launchd_not_loaded_is_zero():
    assert rs.launchd_pid(LAUNCHCTL_LIST, "com.example.absent") == 0


labels = st.text(alphabet=string.ascii_lowercase + ".-", min_size=1, max_size=10)


@given(label=labels, other=labels)
def test_launchd_label_matches_exactly_or_not_at_all(label, other):
    """Near-miss: `com.ollama.server` must not find `com.ollama.server.helper`,
    nor the reverse."""
    table = f"PID\tStatus\tLabel\n4242\t0\t{other}\n"
    expected = 4242 if label == other else 0
    assert rs.launchd_pid(table, label) == expected
