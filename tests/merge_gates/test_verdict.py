"""Verdict selection: the most restrictive gate across a diff's buckets.

The dangerous direction is downgrading — a diff that touches policy or
the deployed tree must never come back docs-only or full-gate. The
degraded verdict exists because an absent chezmoi means "not deployed"
is unprovable; the checker fails closed to the full gate rather than
claim.
"""

from __future__ import annotations

DOCS = ("docs",)
DEPLOYED = ("deployed",)
POLICY = ("policy",)
BOTH = ("deployed", "policy")


class TestEmpty:
    def test_no_paths_is_empty(self, m):
        assert m.verdict_for([], {}, True) == ("empty", ())


class TestPr:
    def test_deployed_file_forces_pr(self, m):
        v, gates = m.verdict_for(["bin/x"], {"bin/x": DEPLOYED}, True)
        assert v == "pr" and gates == m.PR_GATES

    def test_policy_file_forces_pr(self, m):
        v, _ = m.verdict_for(
            ["dotfiles/policy/a.yaml"],
            {"dotfiles/policy/a.yaml": POLICY},
            True,
        )
        assert v == "pr"

    def test_policy_among_docs_still_pr(self, m):
        cls = {"README.md": DOCS, "opencode.jsonc": POLICY}
        v, _ = m.verdict_for(["README.md", "opencode.jsonc"], cls, True)
        assert v == "pr"

    def test_deployed_among_docs_still_pr(self, m):
        cls = {"README.md": DOCS, "bin/x": DEPLOYED}
        v, _ = m.verdict_for(["README.md", "bin/x"], cls, True)
        assert v == "pr"


class TestDocs:
    def test_all_docs_gets_doc_gates(self, m):
        cls = {"README.md": DOCS, "docs/a": DOCS}
        v, gates = m.verdict_for(["README.md", "docs/a"], cls, True)
        assert v == "docs" and gates == m.DOCS_GATES

    def test_docs_plus_other_is_full(self, m):
        cls = {"README.md": DOCS, "tools/x.py": ()}
        v, gates = m.verdict_for(["README.md", "tools/x.py"], cls, True)
        assert v == "full" and gates == m.FULL_GATES

    def test_only_other_is_full(self, m):
        v, _ = m.verdict_for(["tools/x.py"], {"tools/x.py": ()}, True)
        assert v == "full"


class TestDegraded:
    def test_docs_only_degrades_without_chezmoi(self, m):
        cls = {"README.md": DOCS}
        v, gates = m.verdict_for(["README.md"], cls, managed_ok=False)
        assert v == "degraded" and gates == m.FULL_GATES

    def test_policy_still_pr_without_chezmoi(self, m):
        cls = {"opencode.jsonc": POLICY}
        v, _ = m.verdict_for(["opencode.jsonc"], cls, managed_ok=False)
        assert v == "pr"

    def test_empty_stays_empty_without_chezmoi(self, m):
        v, _ = m.verdict_for([], {}, managed_ok=False)
        assert v == "empty"
