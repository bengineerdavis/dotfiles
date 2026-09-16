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


# ── Layer 1 — crash reports, HAR files, and local paths ──────────────────────
#
# Same rule as above, stated again for the new classes: a test claiming to
# prove redaction must assert the input's identifier is absent from the output.
# What survives is what debugging needs — the field name, the auth scheme, the
# code-identifying leaf of a path — never the device, the session, the owner.

@pytest.mark.parametrize(
    ("text", "label", "absent"),
    [
        ('{"deviceIdentifierForVendor":"9B4E0B7C-A1B2-3C4D-5E6F-7A8B9C0D1E2F"}',  "ips_device_uuid", ["9B4E0B7C"]),
        ('{"incidentID":"A1B2C3D4-1111-2222-3333-444455556666"}',                 "ips_device_uuid", ["A1B2C3D4"]),
        ('{"incident_id":"A1B2C3D4-1111-2222-3333-444455556666"}',                "ips_device_uuid", ["A1B2C3D4"]),
        ('{"crashReporterKey":"B7C9D1E3-2222-3333-4444-555566667777"}',           "ips_device_uuid", ["B7C9D1E3"]),
        ('{"bootSessionUUID":"C8D0E2F4-3333-4444-5555-666677778888"}',            "ips_device_uuid", ["C8D0E2F4"]),
        ('"/private/var/containers/Bundle/Application/D9E1F3A5-4444-5555-6666-777788889999/App.app/App"', "ips_container_path", ["D9E1F3A5"]),
        ('"/var/mobile/Containers/Data/Application/EAF2A4B6-5555-6666-7777-888899990000/Documents/db.sqlite"', "ips_container_path", ["EAF2A4B6"]),
        ('{"userID":501}',                                                        "ips_user_id", ["501"]),
        ('{"experimentId":"Kx9mQ2vL7pR4tY8w"}',                                   "ips_trial_id", ["Kx9mQ2vL7pR4tY8w"]),
        ('{"rolloutId":"8fJ2kQ9vL5pR7tY3w"}',                                     "ips_trial_id", ["8fJ2kQ9vL5pR7tY3w"]),
        ("Cookie: session_id=abc123def; Path=/; HttpOnly",                        "har_cookie_line", ["abc123def"]),
        ("Set-Cookie: sid=xyz789; Domain=example.com; Max-Age=3600",              "har_cookie_line", ["xyz789"]),
        ('{"cookies":[{"name":"session_id","value":"xyz789","path":"/"}]}',       "har_cookie_json", ["xyz789"]),
        ("Authorization: Bearer eyJhbGciOi.eyJzdWIi.SflKxwRJ",                    "har_auth_line", ["eyJhbGciOi"]),
        ("x-api-key: sk-live-abc123def456",                                       "har_auth_line", ["sk-live"]),
        ('{"name":"X-API-Key","value":"sk-live-abc123def456"}',                   "har_auth_json", ["sk-live"]),
        ('{"name":"Authorization","value":"Bearer eyJhbGciOi.eyJzdWIi.SflKxwRJ"}', "har_auth_json", ["eyJhbGciOi"]),
        ("https://fed3c1d5d2c34e2a9d71b0e1a2b3c4d5@o450.ingest.us.sentry.io/4507001", "sentry_dsn", ["fed3c1d5"]),
    ],
)
def test_scrub_redacts_crash_and_har_classes(pii_module, text, label, absent):
    scrubbed, hits = pii_module.scrub(text)
    assert hits[label] == 1, f"{label} not detected in {text!r}"
    # The identifier itself must be gone, not merely counted away. What stays
    # is the field name, the auth scheme, the cookie attributes — the parts
    # debugging reads.
    for value in absent:
        assert value not in scrubbed, f"{value!r} survived scrubbing"


@pytest.mark.parametrize(
    "text",
    [
        # The key of a field is diagnostic; the rule must not eat the whole line.
        '{"userID":0501}',                       # leading zero: a version, not a uid
        '{"userID":0}',
        '{"userID":"501"}',                      # quoted: a string field, not the uid
        '{"incidentID":"not-a-uuid"}',
        '{"experimentId":12345678}',             # unquoted, not the id form
        # Cookie attributes are not credentials.
        "Path=/; Domain=example.com; HttpOnly",
        # URLs and relative names are network shape or bare code, not local paths.
        "see https://example.com/docs/setup for details",
        "Frameworks/Alamofire.framework/Alamofire",
        # The IP is redacted by the address rule; the /8 mask must survive it,
        # unclaimed by the path collapser.
        "the /8 suffix in 10.0.0.0/8 is a mask",
    ],
)
def test_scrub_leaves_crash_and_har_lookalikes_alone(pii_module, text):
    scrubbed, hits = pii_module.scrub(text)
    if hits:
        # The one allowed hit: the IP address itself, not the mask.
        assert text.startswith("the /8") and scrubbed.endswith("/8 is a mask")
        assert "10.0.0.0" not in scrubbed
    else:
        assert scrubbed == text, f"over-redacted: {text!r} -> {scrubbed!r}"


# Local paths: policy A — collapse the shape, keep the code identity.

@pytest.mark.parametrize(
    ("given", "expected"),
    [
        # The leaf survives; the topology does not.
        ("/Users/jane/Projects/app-ios/Build/Products/Debug/App.app/App",
         "[HOME]/App.app/App"),
        ("/Users/jane/Projects/app-ios/AppDelegate.swift",
         "[HOME]/AppDelegate.swift"),
        ("/System/Library/PrivateFrameworks/UIKitCore.framework/UIKitCore",
         "[SYSTEM]/UIKitCore.framework/UIKitCore"),
        ("/usr/lib/system/libsystem_c.dylib", "[SYSTEM]/libsystem_c.dylib"),
        ("/opt/homebrew/Cellar/wget/1.21/bin/wget", "[SYSTEM]/wget"),
        # A container path is claimed by its own detector first: the whole
        # per-install prefix goes, not just the UUID.
        ("/var/mobile/Containers/Data/Application/D9E1F3A5-4444-5555-6666-777788889999/notes.txt",
         "[APP-INSTALL]/notes.txt"),
        ("/srv/builds/acme-internal/App", "[LOCAL-PATH]/App"),
        # Trailing punctuation in prose is not part of the path.
        ("crash in /Users/jane/app/bin/run.", "crash in [HOME]/run"),
    ],
)
def test_paths_collapse_but_keep_the_code_identity(pii_module, given, expected):
    scrubbed, hits = pii_module.scrub(given)
    assert scrubbed == expected, f"{given!r} -> {scrubbed!r}"
    # Claimed by exactly one detector — the container paths by their own rule,
    # everything else by the generic collapse.
    assert sum(hits.values()) == 1, hits


def test_the_scrubbed_path_names_the_same_code(pii_module):
    """The property the policy exists for: what called is still knowable."""
    text = 'frames: /Users/jane/Projects/app-ios/App.app/App then /usr/lib/system/libsystem_kernel.dylib'
    scrubbed, _ = pii_module.scrub(text)
    assert "App.app/App" in scrubbed
    assert "libsystem_kernel.dylib" in scrubbed
    assert "jane" not in scrubbed
    assert "/Users/" not in scrubbed


def test_cookie_redaction_keeps_names_and_attributes(pii_module):
    scrubbed, hits = pii_module.scrub("Cookie: session_id=abc123def; theme=dark; Path=/assets; HttpOnly")
    assert hits["har_cookie_line"] == 1
    assert "session_id=[REDACTED]" in scrubbed
    assert "theme=[REDACTED]" in scrubbed
    assert "Path=/assets" in scrubbed
    assert "HttpOnly" in scrubbed


def test_authorization_redaction_keeps_the_scheme(pii_module):
    scrubbed, _ = pii_module.scrub("Authorization: Bearer eyJhbGciOi.eyJzdWIi.SflKxwRJ")
    assert scrubbed == "Authorization: Bearer [REDACTED]"
    scrubbed, _ = pii_module.scrub("x-api-key: sk-live-abc123def456")
    assert scrubbed == "x-api-key: [REDACTED]"


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
