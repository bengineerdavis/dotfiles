# Model access: the gateway and the tool boundary

Decided 2026-09-12, from the author's anti-lock-in handoff brief. Companion to
`dotfiles/docs/AGENT-ARTIFACTS.md`, which settled the context-and-skills layer
(the brief's third vector) the same day — that record is not repeated here.

**The decision, first.**

**Nothing here adopts a gateway.** Today's model layer is exactly what it was
before this research: the `llm` CLI with provider plugins. The decision is
which candidates to reject, which to defer, and what would make that change —
not a switch.

1. **Keep the incumbent thin gateway.** The `llm` CLI with provider plugins
   (`llm-openrouter`, `llm-ollama`) is the model-access layer. It already
   satisfies the repo's binding constraint — `spec.md` § Shared code does not
   assume a provider — through one interface over local and hosted models, and
   it is the only layer our egress policy (`bin/policy` consult-at-egress)
   actually wraps. No surveyed gateway implements that policy integration.
2. **MCP is the tool-execution boundary, adopted as a target, not stood up
   today.** When a tool needs to cross from an agent runtime into local
   systems, it goes through an MCP server declared via dotagents — never an
   IDE-specific engine. No MCP server is authored in this session; that work
   belongs to the factored-out AI tooling home (`PRD.md` § Architecture).
3. **Managed gateways are rejected for personal use.** Vercel AI Gateway
   routes every request through a third-party control plane. Our policy layers
   exist to answer "may this content leave?" at the point of egress — a hosted
   gateway answers that question for us, badly.

**The employer boundary.** None of this binds a machine the author does not
own. Any gateway, hosted or self-hosted, on a work-governed machine is gated
by the governing policy for that machine — which `PRD.md` § Work environments
records as unresolved. A personal-machine decision here licenses nothing on a
work machine, and a work-machine restriction does not reopen this one.

## The requirement

Model calls must survive vendor churn — model releases, API schema changes,
payload adjustments by aggregators — without rewriting workflows, fragmenting
project context, or locking workflows to one vendor's SDK or one IDE's
indexing. A candidate that moves the policy decision off-device, or that
replaces the provider-neutral constraint with a new single-vendor dependency,
is disqualified.

## Vector 1 — the model gateway, measured

| | Incumbent: `llm` + plugins | LiteLLM (self-hosted) | Vercel AI Gateway (managed) |
|---|---|---|---|
| Provider coverage | OpenRouter + Ollama via plugins; more exist | 100+ providers, OpenAI format out | Most major providers, BYOK |
| Policy integration | **Native** — `bin/policy` gates every egress; `llm-ctx` forces no-log | None built in; guardrails are a different model, not our resolver | Their access policies, not ours; data transits Vercel |
| Local models | First-class (`llm-ollama`, incl. tool calls) | Supported (OpenAI-compatible endpoints) | Cloud-only |
| Operational cost | Zero — a CLI already installed | A service to run, patch, and configure (Python + Rust core) | Zero ops; account + key management |
| Latency | Direct | Claimed 8ms P95 overhead at 1k RPS | Network hop to Vercel, unmeasured here |
| Lock-in direction | `llm` CLI (small, auditable, plugins are thin) | LiteLLM's config schema and virtual-key model | Vercel's control plane and billing |
| Scale path | Fine for one machine and its agents | **The candidate at team scale** — virtual keys, spend, load balancing, 58.6k stars | Team scale without ops, at the cost of the policy boundary |
| Evidence quality | Verified live on this machine (v0.35, 11 plugins) | Verified against README + docs 2026-09-12 | Verified against docs 2026-09-12 |

The handoff's specific worries, answered with evidence:

- **"Claude's proprietary caching/messages schema"** — real, but no incident
  here: this machine reaches Claude through OpenRouter, never through native
  SDKs. Nothing to normalize.
- **"OpenRouter payload anomalies"** — no measured anomaly on this machine.
  The risk is plausible and the mitigation is structural: every `llm` call is
  logged by our own scripts with the model id recorded, so an anomaly shows up
  as a diff, not a mystery.
- **"SDK maturity of the choices"** — the handoff assumed a TS/Go backend.
  This repo is Python/Bash tooling with node present only for agent CLIs. On
  that stack, a Python SDK (LiteLLM) is the only gateway candidate that even
  fits, and the incumbent already is Python.

**Why the incumbent wins today:** the decisive row is policy integration. Our
architecture answers "may this content go to a remote model?" at the point of
egress, per machine, per policy layer. LiteLLM's guardrails and Vercel's
access policies are someone else's answer to a different question. Adopting
either would route around the policy resolver — the one thing this repo's
model-access layer must not do.

**When this decision is revisited:** when model access becomes multi-developer
(Sentry-scale), LiteLLM self-hosted is the named candidate — it is the only
surveyed option that keeps egress on-device while centralizing keys and spend.
The trigger is a second person depending on this machine's workflows, not a
new model release. Two checks gate that revisit, both the author's:

- **Employer permission.** Whether a self-hosted gateway may serve work
  flows at all is a question for the governing policy on the machines
  involved — the same unresolved dependency `PRD.md` records. Self-hosted
  keeps the data path on-device, which is the right *shape* of answer, but
  shape is not permission.
- **License split.** LiteLLM's core is MIT, but SSO, admin features and parts
  of the guardrail set sit in the enterprise tier. The feature set available
  under the OSS license is part of what "revisit" evaluates — the deferred
  candidate is the MIT core, not the product page.

## Vector 2 — the tool-execution boundary

MCP (current specification 2026-07-28) is the adopted boundary for exposing
local tools to agent runtimes, when that need arrives:

- **Transports:** stdio for local servers (the JSON-RPC loop the handoff
  describes — child process, no network), Streamable HTTP for remote.
- **Security model:** local stdio servers run with the user's full authority —
  the client gates installation and trust (SEP-1024, client security
  requirements for local installs, is in progress and worth tracking). Remote
  servers use OAuth 2.1; the spec ships Security Best Practices and
  Authorization Security Considerations pages, and an official Registry with a
  moderation policy.
- **What adoption looks like here:** servers declared through dotagents'
  `mcp` command (managed keys, ownership sidecars — client-owned config is
  never rewritten),   consumed by opencode/claude. The `opencode.json`-vs-`opencode.jsonc`
  precedence finding (measured 2026-09-12, recorded in
  `dotfiles/apps/opencode/README.md`) applies: jsonc is authoritative.
- **What we deliberately do not do:** no MCP server authoring in this repo.
  Tool logic is AI tooling; the PRD's architecture rule sends it to the
  factored-out home with everything else. Provisioning may install and trigger
  an MCP server; it must never contain one.

A "Skills Over MCP" working group exists in MCP governance — the two standards
are converging, which is further reason skills went through the Agent Skills
spec rather than through MCP.

## Vector 3 — already decided

The handoff's third vector (repository context and prompt portability) is
`AGENT-ARTIFACTS.md`, decided the same day: Agent Skills format, AGENTS.md
under Linux Foundation stewardship, dotagents distribution, symlink-not-copy
(verified against dotagents' own documentation — the handoff's "test local
file symlinking stability" is answered by design, and by this machine's
working setup).

## Rejected and deferred, with reasons

| Candidate | Verdict | Reason |
|---|---|---|
| LiteLLM AI Gateway | Deferred, named revisit trigger | Correct tool at team scale; wrong tool for one machine whose policy boundary is the differentiator. Revisit when a second developer depends on these workflows. |
| Vercel AI Gateway | Rejected for personal use | Third-party control plane replaces the on-device policy decision; local models unsupported; cloud-only. |
| Direct SDK wrappers (Anthropic/OpenAI native) | Rejected | This is the lock-in the brief exists to prevent; also nothing here calls native SDKs today. |
| Vercel AI SDK ("Core Proxy" in the brief) | Rejected | TypeScript SDK, not a proxy product; this repo has no TS surface. The brief's name and link were both wrong (the SDK lives at ai-sdk.dev; the gateway product is AI Gateway). |
| Standing up MCP now | Deferred | No current tool-exposure need; dotagents already owns the declaration path for when one appears. |

## Open items

- The upstream `llm-pdf-to-images` issue (its `import fitz` shim prints a
  deprecation notice to stdout — observed live on this machine 2026-09-12)
  remains queued in `TASKS.md`.
- No PoC was built, per scope. The handoff's proof-of-concept (generic payload
  → MCP tool boundary) belongs to the factored-out AI tooling home when its
  build starts.
