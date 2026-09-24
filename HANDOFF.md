# HANDOFF — `skill-trust-foreign-buckets`

Branch cut from `main` at `07cd1b2`. Written 2026-09-23. Cold-readable: you need
no context from the session that produced it.

Worktree: `~/code/wt-skill-trust-foreign-buckets`
Task: `TASKS.md` § Now, "Teach `skill-trust` about foreign skill buckets".

This file is branch-local and chezmoi-ignored. Delete it in the commit that
merges the branch — it describes work in flight, not the repo.

---

## Why this branch exists

Claude Code's cloud sync writes `synced/<org>_<user>/` into `~/.agents/skills`,
because `~/.claude/skills` is a dotagents-made symlink to it. `skill-trust`
reads that directory as an undeclared, unlicensed skill and denies, which fails
the whole provisioning run. The bucket holds 10 skills: 4 Anthropic proprietary,
4 with no licence, 2 MIT.

The fix is not to silence the guard. It is to teach it that a directory another
program owns is not a skill it has jurisdiction over.

---

## Measured facts — tested on 2026-09-23, not inferred

Re-testing these costs an hour. They are recorded so you do not have to.

| Question | Answer | How it was established |
|---|---|---|
| What triggers the sync? | Claude Code session start. No daemon, no launchd job | `ps`, `~/Library/LaunchAgents` both empty; manifest rewrote only on `claude -p` |
| Does sync prune directories it does not own? | **No** | A probe dir survived two syncs and never entered `manifest.json` |
| Does deleting a skill remove it? | **No — recreated byte-identical** | Deleted `adhd`, re-synced, `cmp` reported identical |
| Does `manifest.json` carry content hashes? | **No.** Only `skillId, name, description, source, updatedAt` | Parsed directly |
| Is the bucket genuinely live? | **Yes** | `docx` moved 2026-09-14 → 2026-09-23 mid-test |
| Anything that suppresses the sync? | **Yes — `ANTHROPIC_API_KEY`** | With it set, Claude Code disables claude.ai connectors and syncs nothing |

**The consequence that shapes the design:** `deny` is not implementable against a
foreign bucket. Deleting loops forever. The tool must refuse the verdict and say
why, rather than attempt it.

The bucket was restored exactly as found. Proprietary files were never copied,
moved, or deleted — only `pdf/LICENSE.txt` was read. The one directory copied
(`adhd`, MIT, the author's own) was deleted after the sync restored the original.

---

## What is committed here

```
309addb  tasks: close the portable git-config item
cf30fb7  gitconfig: record merge resolutions and show the common ancestor
d9b15a1  gitconfig: bring it under chezmoi, resolving the home paths
aaec63b  tasks: queue portable rerere and zdiff3, record why it stalled
4260bec  agents: land everything by merge, never by a direct write to main
         ← 07cd1b2 main
```

**`4260bec` is the one to read first.** It reverses `AGENTS.md` § Never branched
into § Everything is branched: no session commits to `main` directly, including
for `TASKS.md` and governance docs. `TASKS.md` § Conventions said "straight to
main" too and was corrected in the same commit, or it would have kept teaching
the old rule to anyone who read the queue first.

**`d9b15a1`** adopted the previously unmanaged `~/.gitconfig` as
`dot_gitconfig.tmpl`. It held three hardcoded `/Users/ben.davis` paths
(`init.templateDir`, `core.excludesfile`, `commit.template`) that would fail
silently on Linux — git proceeds without them and says nothing. They now resolve
through `.chezmoi.homeDir`. Verified by rendering: byte-identical output on this
machine, and `git config --file` parses the result clean.

**`cf30fb7`** adds `rerere.enabled` and `merge.conflictstyle=zdiff3`. Both were
also set directly on this machine's `.git/config`, which is why they already
work in this worktree; the commit is the half that reaches a second machine.

Note `eb0b4b2` is on `main`, not here: it fixed `discover.py` so a prose
`license:` field is read rather than missed, and added a `PROPRIETARY` tier.
That was the first half of this task.

---

## What is NOT done

All of it is in `tools/skill-trust/`, none started:

1. **`buckets.py`** — detect a foreign bucket on three pieces of evidence: path
   matches `<store>/synced/<id>/`, a sibling marker `synced/.bucket-<id>` exists,
   and `<id>/manifest.json` parses with a `skills[]` array. Match on evidence,
   never on a name, or a rogue directory buys an exemption by picking the right
   name.
2. **Bucket aliases** — deduced default (`claude-sync`, disambiguated to
   `claude-sync@<first8>` when more than one). **The alias is a label; the bucket
   id is the match key.** If rules keyed on the alias, renaming one would be a
   privilege change.
3. **`external` verdict** — recorded with a date and a reason, not an absence.
   It asserts "not mine to rule on", not "allowed".
4. **`deny` refused for foreign buckets**, carrying the churn-loop reason above.
5. **Config keys** — `guard_foreign_buckets` in `roles/guards/defaults/main.yaml`,
   `opencode_skill_foreign` in `apps/opencode/defaults/main.yaml`.
6. **Move the guard to the last task** in `apps/opencode/tasks/install.yaml`
   (currently at lines 199-213) so unrelated topics converge before the gate can
   fail. This is the direct fix for "one skill blocks my whole install".

Every new test must be seen to fail first, with the mutation named in the commit
message. Mutations worth using: make the evidence check unconditional (a real
undeclared skill should start passing); drop the marker requirement; key rules on
the alias instead of the id.

---

## Open, needs the author

- **`user.email` in `dot_gitconfig.tmpl`** is a personal address that will now
  follow the file onto a work machine. A work address must never be committed —
  `spec.md` § Data.
- **`[mergetool ""]` and `[difftool ""]`** look vestigial: their `cmd` lines begin
  at `"$LOCAL"` where a program name should be. Preserved verbatim rather than
  deleted, because "looks dead" is not "is dead".
- **Machine id** for the Part 2 rules filename. Hostname (`L37V3P6GQ3`) does not
  survive a rebuild, and the backup requirement means the key must.
- **A fourth `blocked` verdict?** The honest way to say "unsolved" without faking
  a refusal.

---

## Environment gotchas that cost time

- **`chezmoi -S "$PWD" add`** — the `-S` is required in a worktree. chezmoi's
  source dir is fixed, so a bare `chezmoi add` writes into `main`'s tree.
- **`chezmoi diff` hangs.** It is configured to use meld, which wants a GUI.
  Use `chezmoi -S "$PWD" cat <target>` and inspect the render instead.
- **Agent sandbox reaches `~/.local/share/chezmoi/**` and `~/code/**` only.** A
  worktree at `~/.local/share/chezmoi-<branch>` is *outside* it — `chezmoi/**`
  does not match `chezmoi-*`. That is why this worktree is under `~/code/`.
  `~/.gitconfig` and `~/.agents/` are also unreachable; the author pasted the
  gitconfig in.
- **The commit-proportionality hook is strict** and rejected four messages here.
  It wants a split, not trimmed prose. When the change genuinely is one decision,
  use a `Proportionality:` trailer — `4260bec` does.
- **Another session shares `main`'s working tree.** It swept an uncommitted
  `TASKS.md` edit into its own commit (`80d8f27`) and recorded a `PROVENANCE`
  note about it. Stay in this worktree.

---

## Resuming

```bash
cd ~/code/wt-skill-trust-foreign-buckets
git log --oneline main..HEAD          # the five commits above
uv run --with pytest --with pyyaml pytest tools/skill-trust -q   # 38 green
```

Read `TASKS.md` § Now for the task, then start at item 1 above.

`chezmoi apply` has not been run and must not be. `chezmoi status` shows
` M .gitconfig` pending, which is the author's to apply.

`dot_gitconfig.tmpl` is a deployed-tree path, so this branch is PR-and-review
per `AGENTS.md` § Merge gates regardless of how green the suite is.
