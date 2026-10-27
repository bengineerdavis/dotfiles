"""Precedence, and the fail-closed guarantee.

Every test here is a way this could break OPEN — a ban that loses to a licence,
an absent licence read as permission, a source-available licence mistaken for
open source. All of them must deny.

The reason the order matters is the first level. A ban is a judgement about a
publisher; if a permissive licence could overturn it, the ban would mean nothing
the moment the publisher added a LICENSE file.

Run:
    uv run --project tools/skill-trust pytest tools/skill-trust
"""

from __future__ import annotations

import pytest

# pyrefly: ignore [missing-import]
from skill_trust.decide import Tier, decide, licence_tier, source_matches

APPROVED = {"approved_sources": ["owner/lib"]}


# --- a None source (undeclared directories) ------------------------------------


def test_a_none_source_matches_no_pattern():
    """Undeclared directories are judged on their own licence alone. This
    guard used to be missing: undeclared-with-licence crashed the whole audit
    on None.strip() whenever any source pattern was configured — and the
    naive fix (pass the directory name as the source) lets a directory named
    like a bare-org pattern inherit that pattern's approval.
    """
    assert source_matches("owner", None) is False
    assert source_matches("owner/lib", None) is False
    assert source_matches("owner", "") is False


def test_a_directory_named_like_an_org_pattern_gains_no_approval():
    """The exploit the naive fix opened: approved_sources carries a bare org,
    and a dropped directory happens to share its name. It must still be
    judged on its licence — here, none, so denied.
    """
    config = {"approved_sources": ["evilorg"]}
    d = decide(None, "evilorg", config, spdx=None)
    assert not d.permitted
    d_mit = decide(None, "evilorg", config, spdx="MIT")
    assert d_mit.permitted
    assert d_mit.rule == "licence"  # via its own licence, never approved_sources


def test_a_none_source_still_fires_deny_skills():
    """The name is passed for exactly this: a recorded denial by directory
    name must bite even with no source to match.
    """
    d = decide(None, ".trash", {"deny_skills": [".trash"]})
    assert not d.permitted
    assert d.rule == "deny_skills"


# --- precedence ---------------------------------------------------------------


def test_a_ban_outranks_a_permissive_licence():
    config = {"deny_sources": ["bad/repo"], "approved_sources": []}
    d = decide("bad/repo", None, config, spdx="MIT")
    assert not d.permitted and d.rule == "deny_sources"


def test_a_ban_outranks_an_explicit_approval():
    """Both lists naming the same repo is a contradiction someone will
    eventually write; denying is the only safe way to resolve it.
    """
    config = {"deny_sources": ["owner/lib"], "approved_sources": ["owner/lib"]}
    assert not decide("owner/lib", None, config, spdx="MIT").permitted


def test_an_exclude_outranks_its_own_approved_source():
    config = {"approved_sources": ["owner/lib"], "exclude": {"owner/lib": ["noisy"]}}
    assert not decide("owner/lib", "noisy", config).permitted
    assert decide("owner/lib", "wanted", config).permitted


def test_an_approved_source_needs_no_licence():
    assert decide("owner/lib", None, APPROVED, spdx=None).permitted


def test_a_permissive_licence_admits_an_unnamed_source():
    d = decide("stranger/repo", None, APPROVED, spdx="MIT")
    assert d.permitted and d.rule == "licence"


# --- fail closed --------------------------------------------------------------


def test_absent_licence_denies():
    """The rule the whole design rests on. Unlicensed means all rights
    reserved — the most restrictive position, not the least.
    """
    d = decide("stranger/repo", None, APPROVED, spdx=None)
    assert not d.permitted and d.rule == "default"


@pytest.mark.parametrize("spdx", ["NOASSERTION", "NONE", "", "  "])
def test_github_s_ways_of_saying_nothing_all_deny(spdx):
    assert not decide("stranger/repo", None, APPROVED, spdx=spdx).permitted


@pytest.mark.parametrize("spdx", ["BUSL-1.1", "SSPL-1.0", "Elastic-2.0", "FSL-1.1"])
def test_source_available_is_not_open_source(spdx):
    d = decide("stranger/repo", None, APPROVED, spdx=spdx)
    assert not d.permitted, f"{spdx} is source-available, not open"


def test_copyleft_denies_unless_opted_in():
    assert not decide("stranger/repo", None, APPROVED, spdx="GPL-3.0").permitted
    opted = dict(APPROVED, licences={"allow_copyleft": True})
    assert decide("stranger/repo", None, opted, spdx="GPL-3.0").permitted


def test_an_unrecognised_identifier_denies_rather_than_guessing():
    assert not decide("stranger/repo", None, APPROVED, spdx="Weird-1.0").permitted


def test_empty_config_denies_everything_unlicensed():
    """A caller that forgets to pass rules must get a loud wrong answer."""
    assert not decide("anyone/anything", None, {}, spdx=None).permitted


# --- matching -----------------------------------------------------------------


def test_a_bare_owner_matches_the_whole_org():
    assert source_matches("owner", "owner/anything")
    assert not source_matches("owner", "otherowner/thing")


def test_owner_repo_matches_only_that_repo():
    assert source_matches("owner/lib", "owner/lib")
    assert not source_matches("owner/lib", "owner/other")


def test_matching_ignores_case():
    assert source_matches("Owner/Lib", "owner/lib")


def test_boost_is_not_the_business_source_licence():
    """BSL-1.0 is Boost and permissive; BSL-1.1 is Business Source and is not.
    One character apart, opposite answers.
    """
    assert licence_tier("BSL-1.0") is Tier.PERMISSIVE
    assert licence_tier("BSL-1.1") is Tier.SOURCE_AVAILABLE
