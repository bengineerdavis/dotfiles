**Added**

- `dotfiles/docs/MODEL-ACCESS.md` — the model-gateway and tool-boundary
  decision, from the author's anti-lock-in brief: the `llm` CLI with provider
  plugins stays as the model layer (it is the only layer the egress policy
  resolver wraps; no surveyed gateway implements that), MCP is the adopted
  tool-execution boundary for when tool exposure is needed (spec 2026-07-28,
  nothing stood up yet), and managed gateways like Vercel AI Gateway are
  rejected for personal use because they move the egress decision off-device.
  LiteLLM is deferred with a named revisit trigger: a second developer
  depending on these workflows. The brief's third vector was already decided
  in `dotfiles/docs/AGENT-ARTIFACTS.md` the same day.

**Changed**

- `docs/REFERENCES.md`: MCP watch-list entry updated to spec 2026-07-28 with
  the record link; LiteLLM added to the watch list (deferred, trigger named);
  Vercel AI Gateway and native vendor SDKs recorded as deliberately not
  followed, with reasons.
