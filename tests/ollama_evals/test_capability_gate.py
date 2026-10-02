"""Contract tests for the capability gate.

A text-only model handed a vision case used to return HTTP 400, which the table
showed as an ERROR — indistinguishable from a broken harness. The gate fixed
that by reporting such cases as n/a. But it introduced the failure mode this
suite exists to catch:

    A gate that skips CORRECTLY and a gate that skips EVERYTHING both produce a
    clean-looking run.

If `model_caps()` ever returned an empty set where it means "could not
determine", every case carrying a requirement would be marked n/a and the suite
would report success having executed nothing. Refusing to run is not evidence of
anything; only RELENTING is.

So each test asserts both directions. Same pattern as
tests/policy/test_policy_callers.py, and for the same reason.

Run:
    pytest tests/ollama_evals -v
"""

from __future__ import annotations

import json
import urllib.error


# --- the predicate: skips when it must, RELENTS when it can ------------------


def test_skips_when_the_model_lacks_a_required_capability(ev):
    assert ev.unmet_capabilities({"completion", "tools"}, {"vision"}) == ["vision"]


def test_relents_when_the_model_has_it(ev):
    """The direction that distinguishes a working gate from one that skips all."""
    assert ev.unmet_capabilities({"completion", "vision"}, {"vision"}) is None


def test_relents_when_the_case_requires_nothing(ev):
    assert ev.unmet_capabilities(set(), set()) is None
    assert ev.unmet_capabilities({"completion"}, set()) is None


def test_undeterminable_capabilities_never_skip(ev):
    """None means 'could not tell' — remote models, or an unreachable server.

    Skipping here would silently drop every case for a model we simply failed to
    interrogate. Better to run it and let it fail honestly.
    """
    assert ev.unmet_capabilities(None, {"vision"}) is None


def test_reports_every_missing_capability_not_just_the_first(ev):
    assert ev.unmet_capabilities({"completion"}, {"vision", "audio"}) == [
        "audio",
        "vision",
    ]


def test_partial_match_still_skips(ev):
    assert ev.unmet_capabilities({"vision"}, {"vision", "audio"}) == ["audio"]


# --- model_caps: the error path must be None, never an empty set -------------


def test_unreachable_server_yields_none_not_empty_set(ev, monkeypatch):
    """The specific bug that would silently skip the entire suite.

    An empty set is a positive claim — "this model has no capabilities" — and
    would skip every case with a requirement. Absence of knowledge must be None.
    """

    def boom(*_a, **_k):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(ev.urllib.request, "urlopen", boom)
    caps = ev.model_caps("some-local-model")
    assert caps is None, (
        "an unreachable server must not look like a model with no capabilities"
    )
    assert ev.unmet_capabilities(caps, {"vision"}) is None, (
        "and must therefore not skip"
    )


def test_remote_models_are_never_interrogated_or_skipped(ev):
    assert ev.model_caps("openrouter/z-ai/glm-5.2") is None
    assert ev.unmet_capabilities(ev.model_caps("openrouter/x/y"), {"vision"}) is None


def test_a_real_capability_list_is_parsed_and_relents(ev, monkeypatch):
    """End of the happy path: a vision model must actually RUN a vision case."""

    class FakeResp:
        def read(self):
            return json.dumps(
                {"capabilities": ["completion", "vision", "tools"]}
            ).encode()

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

    monkeypatch.setattr(ev.urllib.request, "urlopen", lambda *_a, **_k: FakeResp())
    caps = ev.model_caps("a-vision-model")
    assert caps == {"completion", "vision", "tools"}
    assert ev.unmet_capabilities(caps, {"vision"}) is None


# --- case_requires: what a case declares it needs ----------------------------


def test_an_image_implies_vision(ev):
    assert ev.case_requires({"image": {"size": [10, 10]}}) == {"vision"}


def test_explicit_requires_is_honoured(ev):
    assert ev.case_requires({"requires": ["audio"]}) == {"audio"}


def test_a_plain_case_requires_nothing(ev):
    assert ev.case_requires({"prompt": "x"}) == set()


def test_the_real_vision_cases_declare_vision(ev):
    """Guards against a case losing its image and silently becoming text-only."""
    import pathlib
    import yaml

    cases = pathlib.Path(ev.__file__).resolve().parents[1] / "evals" / "cases"
    for name in (
        "vision-topology",
        "vision-faithfulness",
        "vision-instruction-adherence",
    ):
        c = yaml.safe_load((cases / f"{name}.yaml").read_text())
        assert ev.case_requires(c) == {"vision"}, f"{name} no longer requires vision"
