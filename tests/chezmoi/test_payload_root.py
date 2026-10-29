"""The payload root cannot silently become an empty chezmoi source state."""

from pathlib import Path
import shutil

import pytest

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT, payload_census

REPO = Path(__file__).parents[2]

pytestmark = pytest.mark.skipif(
    shutil.which("chezmoi") is None, reason="chezmoi not installed"
)


def test_payload_root_is_home_and_manages_files():
    """A wrong root must fail before apply could plan mass deletion."""
    assert (REPO / ".chezmoiroot").read_text().strip() == "home"
    assert PAYLOAD_ROOT == REPO / "home"
    managed = payload_census(REPO)
    assert "dot_zshrc.tmpl" in managed
    assert "bin/executable_triage" in managed


def test_empty_payload_root_fails_the_census(tmp_path):
    """An empty source directory is not accepted as a valid payload."""
    (tmp_path / ".chezmoiroot").write_text("home\n")
    (tmp_path / "home").mkdir()
    with pytest.raises(RuntimeError, match="empty chezmoi source state"):
        payload_census(tmp_path)
