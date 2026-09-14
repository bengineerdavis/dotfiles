**Added**

- `dotfiles/docs/MULTI-MACHINE.md` — the multi-machine contribution research
  record: the requirement is environment-general committed artifacts (no
  machine identification, no obfuscation signaling) under a forced-disclosure
  threat model, with ZDR handover context kept local by default and
  promotable only after pseudo-anonymization through the pii-redactor tool.
  Contains the audited list of machine-adjacent content already committed,
  a survey of chezmoi/git/Ansible practice, the design (privacy by
  generalization; local state in `~/.local/state/chezmoi/` — a machines map
  and a discardable handover store), and rejected options with reasons
  (including a withdrawn role-codename draft). Four open questions go to a
  panel-of-judges council, queued in ai-prompt-library with a
  questioning-first workflow; implementation waits for that verdict.

**Changed**

- `TASKS.md` queues the machine-string sweep as its own item, gated on the
  council verdict.
