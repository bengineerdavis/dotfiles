"""Layering the machine-local store under the repo rules, as properties.

The invariants, stated without reference to how the merge is written:

- a source denied in EITHER layer is denied after layering
- a source approved in either layer and denied in neither is permitted
- a store denial tightens a repo approval (never the reverse)
- the store cannot loosen licence policy

Small source pools on purpose: collisions between layers are the cases that
matter, and large pools would let a run pass without ever producing one.
"""

from __future__ import annotations

import hypothesis.strategies as st
from hypothesis import given, settings

# pyrefly: ignore [missing-import]
from skill_trust.decide import Verdict, decide, layer_configs, source_matches

SOURCES = ["aaa/lib", "bbb/lib", "ccc/tool", "ddd"]
SKILLS = ["skill-a", "skill-b", ".trash"]

_fragment = st.fixed_dictionaries(
    {
        "deny_sources": st.lists(st.sampled_from(SOURCES), max_size=3),
        "approved_sources": st.lists(st.sampled_from(SOURCES), max_size=3),
        "deny_skills": st.lists(st.sampled_from(SKILLS), max_size=2),
    }
)


def _denied_somewhere(source: str, *fragments: dict) -> bool:
    return any(source_matches(p, source) for f in fragments for p in f["deny_sources"])


@settings(max_examples=200)
@given(base=_fragment, overlay=_fragment, source=st.sampled_from(SOURCES))
def test_a_denial_in_either_layer_denies(base, overlay, source):
    if source not in overlay["deny_sources"] and source not in base["deny_sources"]:
        return  # not this property's case; see the approval one below
    merged = layer_configs(base, overlay)
    assert decide(source, None, merged).verdict is Verdict.DENIED


@settings(max_examples=200)
@given(base=_fragment, overlay=_fragment, source=st.sampled_from(SOURCES))
def test_an_approval_in_either_layer_admits(base, overlay, source):
    if (
        source not in overlay["approved_sources"]
        and source not in base["approved_sources"]
    ):
        return
    if _denied_somewhere(source, base, overlay):
        return  # deny outranks approval; the property above owns that case
    merged = layer_configs(base, overlay)
    decision = decide(source, None, merged)
    assert decision.verdict is Verdict.PERMITTED
    assert decision.rule == "approved_sources"


def test_a_store_denial_tightens_a_repo_approval():
    """The direction the whole design rests on: the human's no outranks the
    repo's yes, because deny is checked first and the layers union.
    """
    merged = layer_configs(
        {"approved_sources": ["aaa/lib"]}, {"deny_sources": ["aaa/lib"]}
    )
    assert decide("aaa/lib", None, merged).verdict is Verdict.DENIED


def test_a_store_approval_relents_a_repo_silence():
    """And the mechanism relents: a source the repo never named is admitted on
    the human's say-so. A store that could only deny would be a one-way ratchet.
    """
    merged = layer_configs({"approved_sources": []}, {"approved_sources": ["aaa/lib"]})
    decision = decide("aaa/lib", None, merged)
    assert decision.verdict is Verdict.PERMITTED


def test_the_store_cannot_loosen_licence_policy():
    """`allow_copyleft` in the store must do nothing: the store decides names,
    not policy. licence keys come from the base alone.
    """
    merged = layer_configs(
        {"licences": {"allow_copyleft": False}},
        {"licences": {"allow_copyleft": True}},
    )
    assert merged.get("licences", {}).get("allow_copyleft") is not True
    decision = decide("unrelated/repo", None, merged, spdx="GPL-3.0")
    assert decision.verdict is Verdict.DENIED


def test_deny_skills_denies_a_named_skill_whatever_its_source():
    config = {"approved_sources": ["aaa/lib"], "deny_skills": ["skill-a"]}
    decision = decide("aaa/lib", "skill-a", config)
    assert decision.verdict is Verdict.DENIED
    assert decision.rule == "deny_skills"
    # ...while a sibling from the same approved source still passes.
    assert decide("aaa/lib", "skill-b", config).verdict is Verdict.PERMITTED


def test_deny_skills_layers_from_the_store():
    merged = layer_configs(
        {"approved_sources": ["aaa/lib"]}, {"deny_skills": ["skill-a"]}
    )
    assert decide("aaa/lib", "skill-a", merged).verdict is Verdict.DENIED
