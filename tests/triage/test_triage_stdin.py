"""stdin handling: empty input refuses, real input reaches the prompt.

The prompt is observed through the stub `llm`, which records its argv — so
'content is read' is proven on the text that would have gone to the model,
without calling one.
"""

from __future__ import annotations


def test_empty_stdin_exits_nonzero(cli):
    proc = cli(input_text="")
    assert proc.returncode != 0
    assert "stdin was empty" in proc.stderr
    assert proc.stdout == "", "a memo was printed despite empty input"


def test_whitespace_stdin_exits_nonzero(cli):
    proc = cli(input_text="  \n\t ")
    assert proc.returncode != 0
    assert "stdin was empty" in proc.stderr
    assert proc.stdout == "", "a memo was printed despite empty input"


def test_stdin_content_reaches_the_prompt(cli, shims, stub_memo):
    proc = cli(input_text="the battery swells on my device")
    assert proc.returncode == 0, proc.stderr
    args = shims.read_llm_args()
    prompt = args[-1]
    assert prompt.strip(), "llm received an empty prompt"
    assert "the battery swells on my device" in prompt
    assert stub_memo in proc.stdout
