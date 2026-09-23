**Added**

- A `deep` opencode agent that opens on Claude Opus 5 (via OpenRouter) at max
  reasoning effort, with `xhigh`/`medium` variants to cycle down to. The
  default model is unchanged.
- opencode model, provider and agent settings now live in
  `.chezmoidata/opencode.yaml`, layered `common` → `os.<darwin|linux>` →
  `hosts.<hostname>`. Share a setting across machines by moving it to
  `common`; give one machine its own by adding a `hosts` entry. Permissions
  stay literal in the template because their order matters. Project configs
  stay in each project's own git.
