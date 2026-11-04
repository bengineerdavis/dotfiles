# Linux provider-routing investigation

Measured 2026-11-01. This is a troubleshooting record for the OpenCode
extension, not a claim of continuous Linux-host coverage.

## Scope and isolation

- Disposable rootless Lima Debian 12 aarch64 guest, official OpenCode 2.2.2
  Linux ARM64 release, isolated guest HOME and `--standalone` request probes.
- Synthetic key assigned to both `OPENAI_API_KEY` and `OPENROUTER_API_KEY`.
- A local mock gateway listened on `127.0.0.1:3207/v1`, returned SSE chat
  completions, and recorded paths, model IDs, and synthetic credentials.
- No real provider traffic, live gateway, live database, deployed home, or
  active host service was used. The guest was deleted after the probes.

## Baseline

With the native OpenRouter provider and only its `baseURL` overridden to the
local gateway, this selected an OpenRouter model:

```bash
opencode run --standalone --model openrouter/z-ai/glm-5.3-flash \
  "Reply with ACK only"
```

Output: `ACK synthetic routing`. The mock recorded exactly one request to
`/v1/chat/completions` for `z-ai/glm-5.3-flash`, carrying the synthetic key.
The explicit `@ai-sdk/openai-compatible` override produced the same route.

An `openrouter/...` selection therefore does not inherently call OpenAI on
Linux. The `openrouter` provider's effective URL is the first thing to check
when that model selection produces an OpenAI endpoint error.

## Variants

| Variant | Result |
|---|---|
| Unreachable OpenRouter gateway | Failed without a request to another provider; no OpenAI fallback observed. |
| `OPENAI_BASE_URL` set to an unreachable URL | Selected OpenRouter request still used its configured local gateway. |
| `small_model=openai/...` | Minimal CLI run made only the selected OpenRouter request; no secondary title/small-model request observed. |
| `disabled_providers=["openai"]` | Selected OpenRouter request still succeeded through the gateway. |
| Wrong OpenRouter URL in `.jsonc`, correct URL in `.json` | No local gateway request; `.jsonc` won. |

The private stale-service probe was inconclusive: after its synthetic service
password was set, it timed out without an error or provider request. It is not
evidence for or against stale service configuration. Separately, on the host
on 2026-11-02, an older service retained the removed Lore plugin and logged
fresh loader errors despite empty plugin lists in both global config files;
see the [README troubleshooting section](README.md#plugin-errors-after-the-config-says-plugin-).

## What to inspect on a machine

Inspect `openrouter`, not just `openai`, when the selected model is
`openrouter/...`. In the winning `opencode.jsonc`, its `options.baseURL` must
be `http://127.0.0.1:3207/v1` for this integration. Check the other gateway
provider blocks too, then review scoped chezmoi drift and inspect a fresh log
around the failure if the route is already correct.

Do not assume `OPENAI_BASE_URL` is globally unset: the topic's `env.zsh` does
not export it for OpenCode, but a separately launched `lore run opencode`
process may set it. Inspect the actual process environment. The gateway's
`LORE_UPSTREAM_OPENAI` is a different setting and is not a substitute for the
client provider's `baseURL`.
