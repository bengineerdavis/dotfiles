"""
The three redaction layers: deterministic pass, model pass, verification.

These are the cases the suite was missing when pii-redactor was a single model
call. The gap was not subtle — with `llm` stubbed as `cat`, which is what an
ignored instruction looks like, the tool produced a byte-identical "redacted"
file and exited 0. Every assertion in the old suite was satisfied by that run,
because none of them looked at the content.

So the rule these tests follow, and which the pii-redaction skill states
outright: a test claiming to prove redaction must assert that the input's PII is
absent from the output. Exit status and file non-emptiness are not evidence.
"""
from __future__ import annotations

import pytest


# ── Layer 1: deterministic detection ─────────────────────────────────────────

@pytest.mark.parametrize(
    ("text", "label"),
    [
        ("mail jane.smith@example.com now",                    "email"),
        ("call 555-867-5309 today",                            "phone"),
        ("card 4111 1111 1111 1111 declined",                  "card"),
        ("card 4111111111111111 declined",                     "card"),
        ("host 192.168.1.1 timed out",                         "ipv4"),
        ("host 2001:db8::8a2e:370:7334 timed out",             "ipv6"),
        ("nic aa:bb:cc:dd:ee:ff down",                         "mac"),
        ("ssn 123-45-6789 on file",                            "national_id"),
        ("key AKIAIOSFODNN7EXAMPLE leaked",                    "cloud_key"),
        ("tok eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.dBjftJeZ4", "jwt"),
        ("see https://user:pa55@host/path",                    "url_credentials"),
        ("get https://api.example/x?token=abc123def456",       "url_token"),
    ],
)
def test_scrub_redacts_each_decidable_class(pii_module, text, label):
    scrubbed, hits = pii_module.scrub(text)
    assert hits[label] == 1, f"{label} not detected in {text!r}"
    # The value itself must be gone, not merely counted.
    for token in text.split():
        if any(ch.isdigit() for ch in token) or "@" in token:
            assert token not in scrubbed


@pytest.mark.parametrize(
    "text",
    [
        # Fails the Luhn check, so it is a 16-digit number, not a card.
        "order 1234 5678 9012 3456 shipped",
        # Final octet exceeds a byte: a version string, not an address.
        "version 1.2.3.400 released",
        # Three colon-separated groups is a timestamp, not a compressed IPv6.
        "deploy finished at 12:34:56",
        "plain prose with no identifiers at all",
    ],
)
def test_scrub_leaves_lookalikes_alone(pii_module, text):
    """False positives make a redactor unusable; the validators earn their keep."""
    scrubbed, hits = pii_module.scrub(text)
    assert scrubbed == text
    assert not hits


def test_find_hits_agrees_with_scrub(pii_module):
    """Verification must apply the same validators as the scrub, or a
    Luhn-rejected number would pass layer 1 and be reported as a leak by layer 3."""
    text = "card 1234 5678 9012 3456 and mail a@b.co and ip 1.2.3.400"
    scrubbed, hits = pii_module.scrub(text)
    assert pii_module.find_hits(text) == hits
    assert not pii_module.find_hits(scrubbed)


# ── Layer 2: what the model is allowed to see ────────────────────────────────

SENSITIVE = "Contact Jane Smith at jane.smith@example.com or 555-867-5309.\n"


def test_model_never_receives_decidable_pii(mock_llm, run_script, tmp_path):
    sent = tmp_path / "sent.txt"
    mock_llm(f'tee {sent!s}')
    src = tmp_path / "in.md"
    src.write_text(SENSITIVE)

    run_script("-i", str(src))

    received = sent.read_text()
    assert "jane.smith@example.com" not in received
    assert "555-867-5309" not in received
    assert "[EMAIL]" in received and "[PHONE]" in received
    # The name is deliberately still there — that is what the model is for.
    assert "Jane Smith" in received


# ── Layer 3: verification ────────────────────────────────────────────────────

def test_passthrough_model_fails_and_writes_nothing(mock_llm, run_script, tmp_path):
    """The original defect: `cat` for a model produced a clean exit and a file."""
    mock_llm("cat")
    src, dst = tmp_path / "in.md", tmp_path / "out.md"
    src.write_text(SENSITIVE)

    r = run_script("-i", str(src), "-o", str(dst))

    assert r.returncode != 0
    assert not dst.exists()
    assert not list(tmp_path.glob("out.md.*"))


def test_refusal_is_not_written_as_output(mock_llm, run_script, tmp_path):
    mock_llm('cat >/dev/null; echo "I am sorry, I cannot help with that."')
    src, dst = tmp_path / "in.md", tmp_path / "out.md"
    src.write_text(SENSITIVE * 8)

    r = run_script("-i", str(src), "-o", str(dst))

    assert r.returncode != 0
    assert not dst.exists()


def test_empty_model_response_fails(mock_llm, run_script, tmp_path):
    mock_llm("cat >/dev/null")
    src, dst = tmp_path / "in.md", tmp_path / "out.md"
    src.write_text(SENSITIVE)

    r = run_script("-i", str(src), "-o", str(dst))

    assert r.returncode != 0
    assert not dst.exists()


def test_model_reintroducing_pii_fails(mock_llm, run_script, tmp_path):
    """Layer 1 cannot help if the model puts an address back; layer 3 must."""
    mock_llm('cat >/dev/null; echo "Reach them at leaked@example.com instead."')
    src, dst = tmp_path / "in.md", tmp_path / "out.md"
    src.write_text(SENSITIVE)

    r = run_script("-i", str(src), "-o", str(dst))

    assert r.returncode != 0
    assert not dst.exists()


def test_failure_names_the_class_not_the_value(mock_llm, run_script, tmp_path):
    """Reporting a leak must not itself leak; error output goes to logs."""
    mock_llm('cat >/dev/null; echo "Reach them at leaked@example.com instead."')
    src = tmp_path / "in.md"
    src.write_text(SENSITIVE)

    r = run_script("-i", str(src))

    combined = r.stdout + r.stderr
    assert "leaked@example.com" not in combined
    assert "email" in combined


def test_no_op_model_is_allowed_when_nothing_was_detectable(mock_llm, run_script, tmp_path):
    """An already-clean document returned unchanged is the correct answer, and
    must not be rejected — otherwise every PII-free file fails."""
    mock_llm("cat")
    src, dst = tmp_path / "in.md", tmp_path / "out.md"
    src.write_text("The build failed on line 42 of the parser.\n")

    r = run_script("-i", str(src), "-o", str(dst))

    assert r.returncode == 0, r.stderr
    assert dst.read_text() == "The build failed on line 42 of the parser.\n"


def test_verified_output_keeps_placeholders_from_both_layers(mock_llm, run_script, tmp_path):
    mock_llm("sed -e 's/Jane Smith/[NAME]/g'")
    src, dst = tmp_path / "in.md", tmp_path / "out.md"
    src.write_text(SENSITIVE)

    r = run_script("-i", str(src), "-o", str(dst))

    assert r.returncode == 0, r.stderr
    result = dst.read_text()
    assert "jane.smith@example.com" not in result
    assert "555-867-5309" not in result
    assert "Jane Smith" not in result
    assert "[EMAIL]" in result and "[PHONE]" in result and "[NAME]" in result


def test_nothing_reaches_stdout_when_verification_fails(mock_llm, run_script, tmp_path):
    """With no -o the output is stdout, so a failure must print no content."""
    mock_llm("cat")
    src = tmp_path / "in.md"
    src.write_text(SENSITIVE)

    r = run_script("-i", str(src))

    assert r.returncode != 0
    assert "jane.smith@example.com" not in r.stdout
    assert "Jane Smith" not in r.stdout
