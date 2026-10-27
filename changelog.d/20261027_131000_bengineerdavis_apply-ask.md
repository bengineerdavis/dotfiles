**Changed**

- `chezmoi apply` moves from `deny` to `ask` for agents. The convention changed
  with the configuration: an agent may apply only from `main`, after showing
  `chezmoi status` and `chezmoi diff`, and the prompt is the author's approval.
  The `autonomous` agent asks too; applying touches the one deployed tree.
- `AGENTS.md` § Applying is main-only and `docs/PERMISSIONS.md` record the new
  rule, including what to do when a target changed since chezmoi last wrote it.
