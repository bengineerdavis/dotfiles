"""Bucket classification: which buckets a changed path falls into.

A path may carry several buckets — bin/executable_policy is both
deployed and policy — and the verdict takes the most restrictive gate
across all of them. These tests pin that accumulation, because losing
the second bucket would silently downgrade a policy change to a code
change.
"""

from __future__ import annotations

MANAGED = frozenset(
    {
        "bin/executable_policy",
        "bin/executable_foo",
        "dot_config/opencode/opencode.jsonc.tmpl",
        "dot_zshrc.tmpl",
    }
)


class TestDeployed:
    def test_managed_path_is_deployed(self, m):
        assert m.buckets_for("bin/executable_foo", MANAGED) == ("deployed",)

    def test_unmanaged_path_is_not(self, m):
        assert m.buckets_for("bin/executable_bar", MANAGED) == ()

    def test_deployed_template_counts(self, m):
        assert "deployed" in m.buckets_for("dot_zshrc.tmpl", MANAGED)


class TestPolicy:
    def test_resolver_is_policy_and_deployed(self, m):
        bs = m.buckets_for("bin/executable_policy", MANAGED)
        assert "policy" in bs and "deployed" in bs

    def test_policy_layer_yaml(self, m):
        assert m.buckets_for("dotfiles/policy/ethics.yaml", MANAGED) == ("policy",)

    def test_policy_layer_nested(self, m):
        assert m.buckets_for("dotfiles/policy/sub/x.yaml", MANAGED) == ("policy",)

    def test_claude_settings(self, m):
        assert m.buckets_for(".claude/settings.json", MANAGED) == ("policy",)

    def test_repo_opencode_config(self, m):
        assert m.buckets_for("opencode.jsonc", MANAGED) == ("policy",)

    def test_global_opencode_config_is_policy_and_deployed(self, m):
        bs = m.buckets_for("dot_config/opencode/opencode.jsonc.tmpl", MANAGED)
        assert "policy" in bs and "deployed" in bs

    def test_opencode_like_name_is_not_policy(self, m):
        assert m.buckets_for("tools/opencode.jsonc.bak", MANAGED) == ()


class TestDocs:
    def test_root_markdown(self, m):
        assert m.buckets_for("README.md", MANAGED) == ("docs",)

    def test_nested_markdown(self, m):
        assert m.buckets_for("docs/TOPICS.md", MANAGED) == ("docs",)

    def test_docs_tree(self, m):
        assert m.buckets_for("docs/deep/note.txt", MANAGED) == ("docs",)

    def test_changelog_fragment(self, m):
        assert m.buckets_for("changelog.d/20260101_x.md", MANAGED) == ("docs",)

    def test_markdown_in_bin_is_docs_not_other(self, m):
        assert m.buckets_for("bin/notes.md", MANAGED) == ("docs",)


class TestOther:
    def test_python_script(self, m):
        assert m.buckets_for("tools/skill-trust/x.py", MANAGED) == ()

    def test_yaml_outside_policy(self, m):
        assert m.buckets_for("dotfiles/apps/ollama/defaults/main.yaml", MANAGED) == ()

    def test_test_file(self, m):
        assert m.buckets_for("tests/policy/test_x.py", MANAGED) == ()
