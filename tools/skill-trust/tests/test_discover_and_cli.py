"""Licence discovery, and the CLI contract.

Discovery is ordered most-specific-first for a reason worth a test: a
permissively licensed skill can live inside a repository licensed differently,
and the skill's own LICENSE is the truth about that skill. Reading the repository
first gets it wrong in both directions at once.

The CLI tests pin the exit vocabulary, which is shared with `bin/policy` so a
caller does not have to learn two. A wrong code here is worse than a wrong
message: scripts branch on it.

Run:
    uv run --project tools/skill-trust pytest tools/skill-trust
"""

from __future__ import annotations

import json
import textwrap

import pytest

from skill_trust.cli import DENIED, ERROR, PERMITTED, UNKNOWN, main
from skill_trust.decide import Tier, licence_tier
from skill_trust.discover import licence_from_dir

MIT_TEXT = "MIT License\n\nCopyright (c) 2026\n\nPermission is hereby granted..."


@pytest.fixture
def skill(tmp_path):
    def _make(name: str, *, licence_text: str | None = None,
              frontmatter: str | None = None) -> "pathlib.Path":
        d = tmp_path / name
        d.mkdir(parents=True)
        if licence_text is not None:
            (d / "LICENSE").write_text(licence_text)
        body = f"---\nname: {name}\ndescription: x\n"
        if frontmatter:
            body += f"{frontmatter}\n"
        (d / "SKILL.md").write_text(body + "---\n\n# x\n")
        return d
    return _make


# --- discovery ----------------------------------------------------------------


def test_reads_an_spdx_identifier_from_the_skill_s_own_frontmatter(skill):
    assert licence_from_dir(skill("a", frontmatter="license: Apache-2.0")) == "Apache-2.0"


def test_a_prose_licence_field_is_read_rather_than_missed(skill):
    """Anthropic's synced skills write a sentence here, not an identifier:
    `license: Proprietary. LICENSE.txt has complete terms`. The pattern used to
    anchor on end-of-line after one token, so this matched nothing and the skill
    was reported as carrying no licence at all — which reads as an oversight by
    whoever published it, when in fact they said the opposite clearly."""
    d = skill("p", frontmatter="license: Proprietary. LICENSE.txt has complete terms")
    assert licence_from_dir(d) == "Proprietary"


def test_a_declared_proprietary_licence_is_not_reported_as_unknown(skill):
    """Both deny. They are not the same fact, and the difference decides what a
    human does next: chase the publisher for a missing licence, or accept that
    the material is not theirs to take."""
    assert licence_tier("Proprietary") is Tier.PROPRIETARY
    assert licence_tier(None) is Tier.UNKNOWN


def test_the_proprietary_denial_says_it_was_declared(tmp_path, skill, capsys):
    skill("p", frontmatter="license: Proprietary. LICENSE.txt has complete terms")
    cfg = _config(tmp_path, "approved_sources: []\n")
    assert main(["--offline", "--config", cfg, "audit",
                 "--skills-dir", str(tmp_path)]) == DENIED
    assert "declares itself Proprietary" in capsys.readouterr().out


def test_recognises_a_licence_from_its_text_when_no_identifier_is_given(skill):
    assert licence_from_dir(skill("b", licence_text=MIT_TEXT)) == "MIT"


def test_frontmatter_beats_the_licence_file(skill):
    """The specific declaration wins over the boilerplate beside it."""
    d = skill("c", licence_text=MIT_TEXT, frontmatter="license: GPL-3.0")
    assert licence_from_dir(d) == "GPL-3.0"


def test_returns_none_rather_than_guessing(skill):
    assert licence_from_dir(skill("d")) is None


def test_distinguishes_business_source_from_a_permissive_licence(skill):
    d = skill("e", licence_text="Business Source License 1.1\n\nParameters...")
    assert licence_from_dir(d) == "BUSL-1.1"


# --- the CLI contract ---------------------------------------------------------


def _config(tmp_path, body: str):
    # Deliberately not inside tmp_path itself: several tests audit tmp_path, and
    # a rules file sitting among the skills it governs would be scanned as one.
    d = tmp_path.parent / f"cfg-{tmp_path.name}"
    d.mkdir(exist_ok=True)
    p = d / "trust.yaml"
    p.write_text(textwrap.dedent(body))
    return str(p)


def test_check_exits_permitted_for_an_approved_source(tmp_path, capsys):
    cfg = _config(tmp_path, "approved_sources: [owner/lib]\n")
    assert main(["--offline", "--config", cfg, "check", "owner/lib"]) == PERMITTED
    assert "PERMITTED" in capsys.readouterr().out


def test_check_exits_denied_and_says_which_rule(tmp_path, capsys):
    cfg = _config(tmp_path, "deny_sources: [bad/repo]\n")
    assert main(["--offline", "--config", cfg, "check", "bad/repo"]) == DENIED
    assert "[deny_sources]" in capsys.readouterr().out


def test_a_missing_config_is_an_error_not_a_denial(tmp_path):
    """ERROR and DENIED mean different things to a caller: one is 'I could not
    tell you', the other is 'I told you no'. Collapsing them would let a typo in
    a path read as a clean refusal."""
    assert main(["--offline", "--config", str(tmp_path / "nope.yaml"),
                 "check", "owner/lib"]) == ERROR


def test_an_unparseable_config_is_an_error(tmp_path):
    cfg = _config(tmp_path, "approved_sources: [unclosed\n")
    assert main(["--offline", "--config", cfg, "check", "owner/lib"]) == ERROR


def test_audit_reports_an_undeclared_directory(tmp_path, skill, capsys):
    skill("mystery")
    cfg = _config(tmp_path, "approved_sources: [owner/lib]\n")
    code = main(["--offline", "--config", cfg, "audit", "--skills-dir", str(tmp_path)])
    assert code == DENIED
    assert "mystery" in capsys.readouterr().out


def test_audit_admits_an_undeclared_directory_that_licenses_itself(tmp_path, skill, capsys):
    """A vendored copy that carries its own permissive licence is accounted for,
    which is the difference between deliberate vendoring and forgetting."""
    skill("vendored", licence_text=MIT_TEXT)
    cfg = _config(tmp_path, "approved_sources: []\n")
    assert main(["--offline", "--config", cfg, "audit",
                 "--skills-dir", str(tmp_path)]) == PERMITTED


def test_audit_honours_the_vendored_exception_list(tmp_path, skill):
    skill("hand-placed")
    cfg = _config(tmp_path, "vendored: [hand-placed]\n")
    assert main(["--offline", "--config", cfg, "audit",
                 "--skills-dir", str(tmp_path)]) == PERMITTED


def test_audit_on_an_empty_directory_is_unknown_not_success(tmp_path):
    """Nothing checked is not the same as nothing wrong. Reporting success for an
    empty or mistyped directory is how an audit silently stops auditing."""
    (tmp_path / "empty").mkdir()
    assert main(["--offline", "--config", _config(tmp_path, "{}\n"),
                 "audit", "--skills-dir", str(tmp_path / "empty")]) == UNKNOWN


def test_audit_on_a_missing_directory_is_an_error(tmp_path):
    assert main(["--offline", "--config", _config(tmp_path, "{}\n"),
                 "audit", "--skills-dir", str(tmp_path / "nope")]) == ERROR


# --- foreign buckets ---------------------------------------------------------


def _bucket(tmp_path, bucket_id: str, *, marker: bool = True):
    """A bucket-shaped directory under `tmp_path/synced/`."""
    synced = tmp_path / "synced"
    synced.mkdir(parents=True, exist_ok=True)
    bucket = synced / bucket_id
    bucket.mkdir(parents=True, exist_ok=True)
    if marker:
        (synced / f".bucket-{bucket_id}").write_text("")
    (bucket / "manifest.json").write_text(
        json.dumps({"skills": [{"name": "one"}, {"name": "two"}]}))
    return bucket


def test_a_foreign_bucket_is_external_not_denied(tmp_path, capsys):
    _bucket(tmp_path, "org_user")
    code = main(["--offline", "--config", _config(tmp_path, "{}\n"),
                 "audit", "--skills-dir", str(tmp_path)])
    assert code == PERMITTED
    out = capsys.readouterr().out
    assert "EXTERNAL [foreign_bucket]" in out
    assert "org_user (claude-sync)" in out
    assert "DENIED" not in out


def test_a_dir_named_like_a_bucket_without_evidence_fails_closed(tmp_path, capsys):
    """The exemption is evidence, never the name — a directory merely named like
    a bucket still fails closed rather than passing."""
    _bucket(tmp_path, "org_user", marker=False)
    code = main(["--offline", "--config", _config(tmp_path, "{}\n"),
                 "audit", "--skills-dir", str(tmp_path)])
    assert code == DENIED
    assert "fails closed" in capsys.readouterr().out


def test_a_deny_rule_keyed_on_the_id_is_refused_not_attempted(tmp_path, capsys):
    """deny is not implementable against a foreign bucket — deleting loops
    forever — so a deny naming the bucket id is refused, loudly, and the run
    still proceeds rather than attempting an unenforceable deletion."""
    _bucket(tmp_path, "org_user")
    cfg = _config(tmp_path, "deny_sources: [org_user]\n")
    code = main(["--offline", "--config", cfg,
                 "audit", "--skills-dir", str(tmp_path)])
    assert code == PERMITTED
    out = capsys.readouterr().out
    assert "EXTERNAL [foreign_bucket]" in out
    assert "refused" in out
    assert "inert" in out
    assert "byte-identical" in out
    assert "DENIED" not in out


def test_a_deny_rule_keyed_on_the_alias_changes_nothing(tmp_path, capsys):
    """The alias is a display label; rules key on the id. A deny naming the
    alias must not trip the refusal path — the bucket is still merely external."""
    _bucket(tmp_path, "org_user")
    cfg = _config(tmp_path, "deny_sources: [claude-sync]\n")
    code = main(["--offline", "--config", cfg,
                 "audit", "--skills-dir", str(tmp_path)])
    assert code == PERMITTED
    out = capsys.readouterr().out
    assert "EXTERNAL [foreign_bucket]" in out
    assert "refused" not in out


def test_foreign_buckets_off_restores_the_denial(tmp_path, capsys):
    _bucket(tmp_path, "org_user")
    cfg = _config(tmp_path, "foreign_buckets: false\n")
    code = main(["--offline", "--config", cfg,
                 "audit", "--skills-dir", str(tmp_path)])
    assert code == DENIED
