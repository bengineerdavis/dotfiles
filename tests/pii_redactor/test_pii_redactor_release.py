"""
The release gate: nothing verified is also released without a human.

Kept in its own file rather than folded into the existing suites, because those
are actively edited by more than one session and this needs no changes to them.

Adding the gate broke 17 of the existing tests, every one of them a success-path
case — which is the right number, because the gate stands between a verified
result and its release, and those are exactly the tests that release something.
The conftest runner now waives the gate by default so those keep testing what
they were written to test, and the cases here opt back in with `gated=True`.

Worth recording: the gate appeared to break nothing on the first run. That was
a stale deployed copy — these tests execute ~/bin/pii-redactor, not the chezmoi
source, so an unapplied edit tests the old binary and passes for the wrong
reason. `chezmoi status` before trusting a green run on this suite.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

from conftest import SCRIPT

# A model that returns already-clean text, so layers 2 and 3 both pass and
# execution actually reaches the release decision.
CLEAN_MODEL = 'cat >/dev/null; echo "Dear [REDACTED], your ticket is closed."'

DIRTY_INPUT = "Dear Jane Doe, your ticket is closed. jane@acme.example\n"


# ── the gate, end to end ──────────────────────────────────────────────────────


def test_file_write_is_withheld_without_approval(run_script, mock_llm, tmp_path):
    """A file exists to be used later, by which time nobody recalls reading it."""
    mock_llm(CLEAN_MODEL)
    src = tmp_path / "in.md"
    src.write_text(DIRTY_INPUT)
    out = tmp_path / "out.md"

    r = run_script("-i", str(src), "-o", str(out), gated=True)

    assert r.returncode != 0
    assert not out.exists(), "verified output was released without review"
    assert "Refusing to release un-reviewed output" in r.stderr


def test_piped_stdout_is_withheld_without_approval(run_script, mock_llm, tmp_path):
    mock_llm(CLEAN_MODEL)
    src = tmp_path / "in.md"
    src.write_text(DIRTY_INPUT)

    r = run_script("-i", str(src), gated=True)

    assert r.returncode != 0
    assert r.stdout.strip() == "", "content escaped to stdout without review"


def test_assume_reviewed_releases_and_announces_the_bypass(run_script, mock_llm, tmp_path):
    mock_llm(CLEAN_MODEL)
    src = tmp_path / "in.md"
    src.write_text(DIRTY_INPUT)
    out = tmp_path / "out.md"

    r = run_script("-i", str(src), "-o", str(out), "--assume-reviewed")

    assert r.returncode == 0
    assert out.exists()
    assert "[REDACTED]" in out.read_text()
    assert "review gate skipped" in r.stderr, "a bypass must not be silent"


def test_bypass_still_requires_verification_to_pass(run_script, mock_llm, tmp_path):
    """--assume-reviewed skips review, not layer 3.

    The gate is additional to verification, never a way around it: a model that
    echoes its input back must still be caught even when review is waived.
    """
    mock_llm("cat")  # pass-through: the redaction never happened
    src = tmp_path / "in.md"
    src.write_text(DIRTY_INPUT)
    out = tmp_path / "out.md"

    r = run_script("-i", str(src), "-o", str(out), "--assume-reviewed")

    assert r.returncode != 0
    assert not out.exists()
    assert "verification failed" in r.stderr or "Refusing to write" in r.stderr


def test_dry_run_is_unaffected_by_the_gate(run_script, tmp_path):
    """--dry-run produces nothing to review, so it must not prompt."""
    src = tmp_path / "in.md"
    src.write_text(DIRTY_INPUT)
    r = run_script("--dry-run", "-i", str(src))
    assert r.returncode == 0
    assert "Would process" in r.stderr


def test_assume_reviewed_is_documented(run_script):
    assert "--assume-reviewed" in run_script("--help").stdout


# ── the decision itself ───────────────────────────────────────────────────────


def _module():
    spec = importlib.util.spec_from_loader("pr", loader=None)
    mod = importlib.util.module_from_spec(spec)
    src = pathlib.Path(SCRIPT).read_text().split("if __name__ ==")[0]
    exec(compile(src, str(SCRIPT), "exec"), mod.__dict__)
    return mod


class _FakeTTY:
    def __init__(self, answer: str):
        self._answer = answer
        self.shown: list[str] = []

    def write(self, s: str) -> int:
        self.shown.append(s)
        return len(s)

    def flush(self) -> None:
        pass

    def readline(self, *a) -> str:
        return self._answer

    def close(self) -> None:
        pass

    @property
    def text(self) -> str:
        return "".join(self.shown)


@pytest.mark.parametrize(
    "answer,approved",
    [("y\n", True), ("Y\n", True), ("yes\n", True),
     ("n\n", False), ("\n", False), ("later\n", False), ("", False)],
)
def test_gate_fails_closed_on_anything_but_yes(answer, approved):
    pr = _module()
    assert pr.confirm_egress("BODY", "out.md", tty=_FakeTTY(answer)) is approved


def test_gate_shows_the_content_and_does_not_claim_safety():
    """Verification proves no *detectable* PII, which is a weaker claim."""
    pr = _module()
    tty = _FakeTTY("n\n")
    pr.confirm_egress("REDACTED-BODY-HERE", "out.md", tty=tty)
    assert "REDACTED-BODY-HERE" in tty.text, "cannot approve what you were not shown"
    assert "not the same as safe to" in tty.text
    assert "Approve for release?" in tty.text


def test_gate_names_the_destination():
    """Approving output to stdout is a different decision from a file on disk."""
    pr = _module()
    tty = _FakeTTY("n\n")
    pr.confirm_egress("BODY", "/tmp/somewhere.md", tty=tty)
    assert "/tmp/somewhere.md" in tty.text
