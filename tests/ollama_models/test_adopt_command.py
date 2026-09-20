"""`adopt` as a command: who is allowed to make it write, and what it does
when nobody is there to ask.

Split from the rewrite tests on purpose. Those ask "is the edit correct"; these
ask "was the edit permitted". A correct edit made without consent is still the
failure this whole feature was gated to avoid.

Every test writes to a COPY of the real manifest in tmp_path. The real one is
never a test subject — the `manifest_copy` fixture exists so that cannot be
forgotten.

Upstream is stubbed throughout. Whether ollama.com is reachable is not what
these assert, and a suite that needs the network is a suite that gets skipped.
"""

from __future__ import annotations

import argparse
import urllib.error

import pytest

yaml = pytest.importorskip("yaml")

ADOPTED = "qwen3.7"
REFUSED = 3      # ollama-models' documented code for a deliberate no (2 is argparse's)


@pytest.fixture
def run(om, monkeypatch, capsys):
    """Invoke cmd_adopt the way main() does, against a manifest copy.

    Returns (exit_code, stdout, stderr). `upstream` defaults to "every
    candidate exists"; pass a set to constrain it, or an exception to raise.
    """
    def _run(manifest, family="qwen3.6", to=ADOPTED, dry_run=False,
             upstream=None, tty=False, answer=None):
        def fake_upstream(fam):
            if isinstance(upstream, Exception):
                raise upstream
            if upstream is None:
                doc = yaml.safe_load(manifest.read_text())["ollama_models"]
                return {n for _, n in om.retag_plan(doc.get(family), family, fam)}
            return set(upstream)

        monkeypatch.setattr(om, "upstream_tags", fake_upstream)
        monkeypatch.setattr(om, "interactive", lambda: tty)
        if answer is not None:
            monkeypatch.setattr("builtins.input", lambda _p="": answer)
        reserve, families, keep, ctx, roles, gate = om.load_manifest(manifest)
        args = argparse.Namespace(manifest=manifest, family=family, to=to,
                                  dry_run=dry_run)
        code = om.cmd_adopt(args, reserve, families, keep, ctx, roles, gate)
        out = capsys.readouterr()
        return code, out.out, out.err
    return _run


def set_keys(path, **kv):
    text = path.read_text()
    for key, value in kv.items():
        assert f"\n{key}:" in text, key
        text = "\n".join(
            f"{key}: {value}" if ln.startswith(f"{key}:") else ln
            for ln in text.splitlines()
        ) + "\n"
    path.write_text(text)


def allow(path, policy="auto"):
    set_keys(path, ollama_model_update_scope="manifest",
             ollama_model_update_policy=policy)


# ── scope: may this tool edit the manifest at all ──────────────────────────


def test_the_shipped_default_refuses_to_write(manifest_copy, run):
    """The manifest as committed says `weights`. A fresh checkout must not be
    one command away from a rewritten manifest."""
    before = manifest_copy.read_text()
    code, _, err = run(manifest_copy)
    assert code == REFUSED
    assert "ollama_model_update_scope" in err
    assert "manifest" in err, "the refusal must name the fix"
    assert manifest_copy.read_text() == before


@pytest.mark.parametrize("scope,writes", [("weights", False), ("manifest", True),
                                          ("both", True)])
def test_each_scope_value(manifest_copy, run, scope, writes):
    set_keys(manifest_copy, ollama_model_update_scope=scope,
             ollama_model_update_policy="auto")
    before = manifest_copy.read_text()
    code, _, _ = run(manifest_copy)
    assert (manifest_copy.read_text() != before) is writes
    assert (code == 0) is writes


def test_an_unknown_scope_is_rejected_at_load(om, manifest_copy):
    set_keys(manifest_copy, ollama_model_update_scope="everything")
    with pytest.raises(SystemExit) as e:
        om.load_manifest(manifest_copy)
    assert "ollama_model_update_scope" in str(e.value)


def test_an_unknown_policy_is_rejected_at_load(om, manifest_copy):
    set_keys(manifest_copy, ollama_model_update_policy="yolo")
    with pytest.raises(SystemExit) as e:
        om.load_manifest(manifest_copy)
    assert "ollama_model_update_policy" in str(e.value)


def test_the_defaults_when_neither_key_is_present(om, tmp_path):
    """Absent means the old behaviour, not the new one."""
    p = tmp_path / "m.yaml"
    p.write_text("ollama_models: {}\n")
    *_, gate = om.load_manifest(p)
    assert gate == ("prompt", "weights")


# ── policy: how much say ───────────────────────────────────────────────────


def test_skip_refuses_and_says_so(manifest_copy, run):
    allow(manifest_copy, policy="skip")
    before = manifest_copy.read_text()
    code, _, err = run(manifest_copy)
    assert code == REFUSED
    assert "skip" in err
    assert manifest_copy.read_text() == before


def test_report_shows_the_diff_and_refuses(manifest_copy, run):
    allow(manifest_copy, policy="report")
    before = manifest_copy.read_text()
    code, out, err = run(manifest_copy)
    assert code == REFUSED, "a wanted write did not happen; that is a refusal"
    assert "--- a/main.yaml" in out and "+++ b/main.yaml" in out
    assert "nothing written" in err
    assert manifest_copy.read_text() == before


def test_prompt_without_a_tty_degrades_to_report(manifest_copy, run):
    """Non-interactive, so refuse rather than assume. The same degradation
    playbook.yaml applies, so the two cannot disagree."""
    allow(manifest_copy, policy="prompt")
    before = manifest_copy.read_text()
    code, _, err = run(manifest_copy, tty=False)
    assert code == REFUSED
    assert "no TTY" in err
    assert manifest_copy.read_text() == before


@pytest.mark.parametrize("answer,writes", [("y", True), ("yes", True), ("Y", True),
                                           ("n", False), ("", False), ("sure", False)])
def test_prompt_with_a_tty_writes_only_on_an_explicit_yes(manifest_copy, run,
                                                          answer, writes):
    allow(manifest_copy, policy="prompt")
    before = manifest_copy.read_text()
    code, _, _ = run(manifest_copy, tty=True, answer=answer)
    assert (manifest_copy.read_text() != before) is writes
    assert code == (0 if writes else REFUSED)


def test_auto_writes_without_asking(manifest_copy, run, monkeypatch):
    allow(manifest_copy, policy="auto")
    monkeypatch.setattr("builtins.input",
                        lambda *_a: pytest.fail("auto must not prompt"))
    code, out, _ = run(manifest_copy)
    assert code == 0
    assert "wrote" in out
    assert ADOPTED in yaml.safe_load(manifest_copy.read_text())["ollama_models"]


# ── dry run ────────────────────────────────────────────────────────────────


def test_dry_run_prints_the_diff_and_writes_nothing(manifest_copy, run):
    allow(manifest_copy, policy="auto")
    before = manifest_copy.read_text()
    code, out, err = run(manifest_copy, dry_run=True)
    assert code == 0, "--dry-run got exactly what it asked for; that is success"
    assert "-  qwen3.6:" in out and "+  qwen3.7:" in out
    assert "--dry-run" in err
    assert manifest_copy.read_text() == before


def test_dry_run_overrides_even_auto(manifest_copy, run):
    """One implementation behind two names: the flag forces the policy rather
    than branching beside it."""
    allow(manifest_copy, policy="auto")
    before = manifest_copy.read_text()
    run(manifest_copy, dry_run=True)
    assert manifest_copy.read_text() == before


def test_dry_run_still_needs_the_scope(manifest_copy, run):
    """Showing a diff is harmless; being told the tool may not edit this file
    is more useful than a preview of an edit that can never happen."""
    code, _, err = run(manifest_copy, dry_run=True)
    assert code == REFUSED
    assert "scope" in err


# ── refusing rather than guessing ──────────────────────────────────────────


def test_a_tag_missing_upstream_refuses_the_whole_family(om, manifest_copy, run):
    """Fail closed. A half-migrated family is worse than an untouched one."""
    allow(manifest_copy)
    doc = yaml.safe_load(manifest_copy.read_text())["ollama_models"]
    plan = om.retag_plan(doc["qwen3.6"], "qwen3.6", ADOPTED)
    partial = sorted(n for _, n in plan)[:-1]
    before = manifest_copy.read_text()
    code, _, err = run(manifest_copy, upstream=partial)
    assert code == REFUSED
    assert "no `qwen3.7` build upstream" in err
    assert manifest_copy.read_text() == before


def test_an_unreachable_registry_refuses(manifest_copy, run):
    allow(manifest_copy)
    before = manifest_copy.read_text()
    code, _, err = run(manifest_copy,
                       upstream=urllib.error.URLError("connection refused"))
    assert code == REFUSED
    assert "unverified guess" in err
    assert manifest_copy.read_text() == before


def test_an_unknown_family_is_an_error_not_a_refusal(manifest_copy, run):
    allow(manifest_copy)
    with pytest.raises(SystemExit) as e:
        run(manifest_copy, family="not-a-family")
    assert "no family" in str(e.value)


def test_adopting_onto_an_existing_family_is_refused(manifest_copy, run):
    """A family must appear exactly once; duplicate YAML keys silently discard
    the earlier block, which would delete members without saying so."""
    allow(manifest_copy)
    with pytest.raises(SystemExit) as e:
        run(manifest_copy, family="qwen3.6", to="qwen3.5")
    assert "exactly once" in str(e.value)


def test_adopting_a_family_onto_itself_is_refused(manifest_copy, run):
    allow(manifest_copy)
    with pytest.raises(SystemExit) as e:
        run(manifest_copy, family="qwen3.6", to="qwen3.6")
    assert "already is" in str(e.value)


# ── what a successful write leaves behind ──────────────────────────────────


def test_a_failed_verification_stops_the_write(om, manifest_copy, run, monkeypatch):
    """verify_rewrite proves the edit is clean; this proves cmd_adopt listens.

    Found by mutation: bypassing the `if problems:` branch left all 71 tests
    passing, because a clean rewrite never populates it. A checker nobody acts
    on is decoration, so the acting is asserted separately from the checking.
    """
    monkeypatch.setattr(om, "verify_rewrite",
                        lambda *a, **k: ["line 9: invented problem"])
    allow(manifest_copy, policy="auto")
    before = manifest_copy.read_text()
    code, _, err = run(manifest_copy)
    assert code == 1, "a broken rewrite is an error, not a policy refusal"
    assert "ABORTED" in err and "invented problem" in err
    assert manifest_copy.read_text() == before


def test_a_clean_verification_lets_the_write_through(om, manifest_copy, run):
    """The relenting direction. Without it the test above is satisfied by a
    gate that refuses everything."""
    allow(manifest_copy, policy="auto")
    assert run(manifest_copy)[0] == 0
    assert ADOPTED in yaml.safe_load(manifest_copy.read_text())["ollama_models"]


def test_the_written_file_passes_its_own_verifier(om, manifest_copy, run):
    before = manifest_copy.read_text()
    allow(manifest_copy, policy="auto")
    staged = manifest_copy.read_text()
    run(manifest_copy)
    doc = yaml.safe_load(staged)["ollama_models"]
    pairs = om.retag_plan(doc["qwen3.6"], "qwen3.6", ADOPTED)
    assert om.verify_rewrite(staged, manifest_copy.read_text(),
                             "qwen3.6", ADOPTED, pairs) == []
    assert before != staged  # the scope edit really did land


def test_the_diff_you_approve_is_the_diff_you_get(manifest_copy, run, tmp_path):
    """The preview is the consent artifact. If the write could differ from it,
    `prompt` would be asking about something other than what happens."""
    import difflib

    allow(manifest_copy, policy="auto")
    twin_dir = tmp_path / "twin"
    twin_dir.mkdir()
    twin = twin_dir / manifest_copy.name      # same name, so the diff headers match
    twin.write_text(manifest_copy.read_text())

    _, previewed, _ = run(twin, dry_run=True)
    assert twin.read_text() == manifest_copy.read_text(), "dry run wrote"

    before = manifest_copy.read_text()
    run(manifest_copy)
    actual = "".join(difflib.unified_diff(
        before.splitlines(keepends=True),
        manifest_copy.read_text().splitlines(keepends=True),
        "a/main.yaml", "b/main.yaml"))
    assert actual and actual in previewed


def test_a_write_reports_the_role_drift_it_created(manifest_copy, run):
    """`chat/best` and `think/best` point at qwen3.8; `code/best` points at a
    qwen3.6 coding build. Retagging qwen3.6 strands that pick, and the human
    has to know — repointing a role is a judgement this tool does not make."""
    allow(manifest_copy, policy="auto")
    code, out, _ = run(manifest_copy)
    assert code == 0
    assert "role pick(s) declared by no family" in out
    assert "code/best: qwen3.6:27b-coding-nvfp4" in out


def test_a_write_says_no_weights_were_pulled(manifest_copy, run):
    allow(manifest_copy, policy="auto")
    _, out, _ = run(manifest_copy)
    assert "NO WEIGHTS ARE PULLED" in out


def test_adopt_never_shells_out_to_ollama(manifest_copy, run, om, monkeypatch):
    """The whole point of the manifest scope. Nothing here may pull."""
    monkeypatch.setattr(om.subprocess, "run",
                        lambda *a, **k: pytest.fail(f"adopt ran {a}"))
    allow(manifest_copy, policy="auto")
    assert run(manifest_copy)[0] == 0


def test_the_result_is_reloadable_and_unchanged_elsewhere(manifest_copy, om, run):
    before = yaml.safe_load(manifest_copy.read_text())
    allow(manifest_copy, policy="auto")
    run(manifest_copy)
    after = yaml.safe_load(manifest_copy.read_text())
    for key in before:
        if key not in ("ollama_models", "ollama_model_update_scope",
                       "ollama_model_update_policy"):
            assert after[key] == before[key], key
    # And the tool can still read what it wrote.
    _r, families, _k, _c, _ro, gate = om.load_manifest(manifest_copy)
    assert ADOPTED in families and "qwen3.6" not in families
    assert gate == ("auto", "manifest")
