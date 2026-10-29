# Environment for mise-managed tools.
# Sourced by ~/.zshrc via the canonical glob $ZSH/apps/*/files/zsh/*.zsh.

# ── Keep PyMuPDF's deprecation notice off STDOUT ─────────────────────────────
# The llm-pdf-to-images plugin imports `fitz`, and PyMuPDF answers with:
#
#   warning: The `fitz` API is deprecated and will be removed in future.
#
# PyMuPDF's default message stream is STDOUT, not stderr — so that line is
# prepended to the output of EVERY `llm` invocation, whether or not a PDF is
# involved. It lands in piped output, in captured variables, and at the head of
# JSON responses, where it breaks any parser downstream. `model-bench` already
# carries a workaround for exactly this.
#
# fd:2 redirects PyMuPDF's messages to stderr rather than silencing them: the
# deprecation is real and worth seeing when it eventually breaks, it just must
# not contaminate the data stream. Remove this once llm-pdf-to-images moves to
# `import pymupdf`.
export PYMUPDF_MESSAGE=fd:2
