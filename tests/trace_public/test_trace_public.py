"""
Contract tests for the stack-trace reducer.

The property under test is one-directional: nothing site-specific may survive.
So most cases assert on what is *absent* from the output, and the leak fixtures
carry deliberately distinctive tokens — a real trace's identifiers are rarely as
obvious as `acme-corp`, and a test that only checked shape would pass while
leaking.

The other half is usefulness. A whitelist that drops everything is trivially
safe and worthless, so each language has a case asserting a public frame
survives. Both halves have to hold at once.

Run:
    pytest tests/trace_public -v
"""

from __future__ import annotations

import pathlib
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "bin" / "executable_trace-public"

# Tokens that must never appear in output, whatever the input format.
LEAK_TOKENS = (
    "ben.davis", "acme-corp", "acmecorp", "/Users/", "jane@",
    "180776", "InvoiceJob", "internal/billing", ".venv",
)

PY_TRACE = '''Traceback (most recent call last):
  File "/Users/ben.davis/code/work/acme-corp/billing/tasks.py", line 88, in run_invoice
    customer = Customer.objects.get(email="jane@acme-corp.example")
  File "/Users/ben.davis/code/work/acme-corp/.venv/lib/python3.12/site-packages/django/db/models/query.py", line 496, in get
    raise self.model.DoesNotExist(
django.core.exceptions.ObjectDoesNotExist: Customer matching query does not exist. id=180776
'''

JS_TRACE = '''TypeError: Cannot read properties of undefined (reading 'id')
    at resolveCustomer (/Users/ben.davis/code/work/acme-corp/src/billing.ts:42:19)
    at /Users/ben.davis/code/work/acme-corp/node_modules/express/lib/router/route.js:149:13
'''

JAVA_TRACE = '''java.lang.NullPointerException: Cannot invoke "Customer.getId()" because customer is null
\tat com.acmecorp.billing.InvoiceJob.run(InvoiceJob.java:88)
\tat org.springframework.scheduling.support.DelegatingErrorHandlingRunnable.run(DelegatingErrorHandlingRunnable.java:54)
'''

GO_TRACE = '''panic: runtime error: invalid memory address or nil pointer dereference
goroutine 42 [running]:
\t/Users/ben.davis/code/work/acme-corp/internal/billing/invoice.go:71 +0x1a
\t/opt/homebrew/Cellar/go/1.24/libexec/src/net/http/server.go:2136 +0x2f
'''

ALL_TRACES = {
    "python": PY_TRACE, "js": JS_TRACE, "java": JAVA_TRACE, "go": GO_TRACE,
}


def run(text: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(SCRIPT), *args],
        input=text, capture_output=True, text=True,
    )


# --- the safety half: nothing site-specific survives -------------------------


@pytest.mark.parametrize("name", sorted(ALL_TRACES))
def test_no_site_specific_token_survives(name):
    out = run(ALL_TRACES[name]).stdout
    leaked = [t for t in LEAK_TOKENS if t.lower() in out.lower()]
    assert not leaked, f"{name} trace leaked {leaked}"


@pytest.mark.parametrize("name", sorted(ALL_TRACES))
def test_exception_message_is_removed(name):
    """Messages carry interpolated values — ids, emails, record contents."""
    out = run(ALL_TRACES[name]).stdout
    assert "<message removed>" in out or "goroutine" in out


def test_first_party_frame_is_dropped():
    out = run(PY_TRACE).stdout
    assert "tasks.py" not in out
    assert "run_invoice" not in out


def test_echoed_source_lines_are_dropped():
    """The line of code under a frame is the likeliest place for real data."""
    out = run(PY_TRACE).stdout
    assert "Customer.objects" not in out
    assert "raise self.model" not in out


def test_unclassifiable_input_yields_nothing_rather_than_passing_through():
    result = run("some free-form log line with customer jane@acme-corp.example in it\n")
    assert result.returncode == 2
    assert "jane@" not in result.stdout
    assert "--explain" in result.stderr


# --- the usefulness half: public frames survive ------------------------------


def test_python_public_frame_survives_with_prefix_stripped():
    out = run(PY_TRACE).stdout
    assert "django/db/models/query.py" in out
    assert "in get" in out


def test_js_public_frame_survives():
    out = run(JS_TRACE).stdout
    assert "express/lib/router/route.js" in out


def test_java_public_package_survives_without_a_path():
    """JVM frames have no directory, so they classify by package prefix."""
    out = run(JAVA_TRACE).stdout
    assert "org.springframework" in out


def test_go_stdlib_frame_survives():
    """Go's stdlib lives in the toolchain, not a package directory."""
    out = run(GO_TRACE).stdout
    assert "net/http/server.go" in out


def test_trace_header_is_kept_for_orientation():
    assert "Traceback (most recent call last):" in run(PY_TRACE).stdout


# --- reporting ---------------------------------------------------------------


def test_explain_shows_a_decision_per_line_and_writes_no_trace():
    result = run(PY_TRACE, "--explain")
    assert result.returncode == 0
    assert "DROP" in result.stdout and "keep" in result.stdout
    assert "first-party or unknown frame path" in result.stdout


def test_summary_separates_kept_from_dropped():
    err = run(PY_TRACE).stderr
    assert "kept" in err and "dropped" in err
    assert "keep " in err and "drop " in err


def test_output_is_never_described_as_safe_to_share():
    """Provenance survives reduction; the tool must not imply otherwise."""
    err = run(PY_TRACE).stderr.lower()
    assert "derived" in err
    for phrase in ("safe to share", "safe to send", "cleared", "sanitised"):
        assert phrase not in err


def test_quiet_suppresses_the_summary_but_not_the_output():
    result = run(PY_TRACE, "--quiet")
    assert "django/db/models/query.py" in result.stdout
    assert result.stderr.strip() == ""


def test_no_lineno_drops_line_numbers():
    out = run(PY_TRACE, "--no-lineno").stdout
    assert "django/db/models/query.py" in out
    assert "line 496" not in out
