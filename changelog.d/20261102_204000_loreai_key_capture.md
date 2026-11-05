### Fixed

- loreai: keep the fitz deprecation notice out of the OpenRouter key the
  gateway captures. `llm keys get` writes PyMuPDF's notice to STDOUT, so
  `2>/dev/null` filtered nothing and the captured value was two lines —
  notice, then key (98 bytes instead of 73). The service held that value
  and every background worker failed `Headers.append: ... is an invalid
  header value`, losing distillation and curation for the whole session
  (measured 2026-11-02: 43 minutes, zero distillations). The env template
  now sets `PYMUPDF_MESSAGE=fd:2` for that one call and keeps only the last
  line, which holds even in a systemd service shell that never sources the
  mise fragment exporting the same variable.
