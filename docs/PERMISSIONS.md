# PERMISSIONS.md

How agent permissions are set in this repository, and — more importantly — what
they do not protect against.

Two agent surfaces are configured here, and the rules for both are versioned:
**opencode** — the global template `home/dot_config/opencode/opencode.jsonc.tmpl`
and the project file `opencode.jsonc` — and **Claude Code**
(`.claude/settings.json`). Claude Code's file is JSON and cannot carry
comments; opencode's are JSONC and carry the reasoning inline. This file is
the reasoning for both. Change rules and this file together.

## What this layer is for

**It catches accidents. It does not contain a misaligned agent.**

That is the whole threat model, and it is stated first because everything else
follows from it. A well-behaved agent doing something irreversible without
meaning to is the realistic risk here, and it is the risk these rules address.

Anything stronger is not achievable at this layer. Claude Code matches patterns
against command strings, and this repository requires commands that execute
arbitrary code by design: `uv run --with <anything> pytest` is the documented
test command, `pytest` and `bats` run code as their purpose, `./run-role.sh`
hands work to Ansible, and git hooks fire on every commit. Denying `python3 -c`
while those remain would close one door in a building with five open ones — and
it would feel like a boundary, which is worse than an honest speed bump. A guard
you trust further than it deserves is the more dangerous of the two.

Real containment needs a sandbox — a restricted filesystem view, a container, or
egress control at the OS level. That is a project rather than a config file, and
it is tracked separately in `TASKS.md`. Do not conflate the two.

## The three tiers

**deny** — never, and a rule here should be justifiable as unrecoverable or as
contradicting a written convention.

- Force-push (`git push --force`, `-f`, `--force-with-lease`). `spec.md` § Change
  records requires a backup branch and `git notes` first, and a rewrite does not
  un-publish. `--force-with-lease=<ref>` needs its own rule; see below.
- Credential stores and secret files. These are read-denies, and Claude Code
  extends a Read deny to Edit and Write on the same path.

**ask** — legitimate, but irreversible or outward-facing. The prompt is the
point: it is the moment a human sees what is about to happen.

Publishing (`git push`, `gh`), machine mutation (`brew`/`pip`/`npm` installs,
`launchctl`, `./run-role.sh`), destruction (`rm`, `git reset --hard`), network
egress (`curl`, `wget`), secret access (`op`), history rewriting
(`git filter-repo`/`filter-branch`), large or destructive model operations
(`ollama pull`/`rm`), and `chezmoi apply` — from `main` only, after
`chezmoi status` and `chezmoi diff`, with the prompt as the author's approval.

**allow** — read-only inspection, and changes that git can undo.

Reading and searching, git operations that stay local, running tests, the
validators, `chezmoi` read commands plus `add` (which only moves deployed
content into a git-tracked source), and the interpreters.

Carve-outs from an `ask` family:

- **`git worktree add`** is allowed; `remove`, `prune`, `move` and the rest
  still ask. Creating a worktree only adds a checkout, and agents here work one
  worktree per session (`docs/WORKTREES.md`), so the prompt was pure friction.
  Deleting one can lose uncommitted work.
- **Read-only `gh`** is allowed: `list`/`view`/`status` forms of `pr`, `issue`,
  `repo`, `run`, `workflow`, `release` and `label`, plus `gh search` and
  `gh status`. `gh api` is allowed only as a GET: a method (`-X`, `--method`),
  a field (`-f`, `-F`, `--field`, `--raw-field`), a body (`--input`) or
  `graphql` makes it ask, because each can write. `gh auth` stays at ask, since
  it can print a token.

Claude Code has the worktree carve-out but not the `gh` one. Its precedence is
deny > ask > allow regardless of order, so an allow cannot carve an exception
out of the `Bash(gh *)` ask; that needs the broad rule split first.

## Interpreters are allowed, deliberately

`python3`, `uv run` and friends are in **allow**. Given the threat model above
this is the honest position: they cannot be meaningfully denied while the test
and provisioning commands exist, and a rule that pretends otherwise buys nothing.

It has a consequence worth stating plainly. **Every `ask` rule is bypassable
from an interpreter.** A script can open a socket without invoking `curl`. The
`ask` tier therefore stops an agent that is not trying to get around it, which
is exactly the agent this layer is designed for.

## Rules name intent, not syntax

An allow that names a command prefix grants everything reachable from that
prefix. `Bash(uv run *)` reads as "run the test suite" and means "run anything".
This is the sudoers shell-escape problem, and it is how the previous list
reached 177 rules across three files with nothing denied.

Two working habits follow. Add the narrowest rule that does the job. And when a
rule needs widening for the third time, that is evidence the intent was wrong,
not that the rule was too tight.

## Three ways a rule quietly fails to match

All three were found in use, and all matter because the failure is silent:
the narrow rule never fires, and a broader rule, or none, decides instead.

**A flag before the subcommand changes the string.** `Bash(git push *)` does not
match `git -C /some/path push`, because matching is against the whole command
text and that text no longer begins with `git push`. Twenty-seven of the rules
this config replaced used the `git -C` form, so this is not hypothetical. It is
closed here by putting **all** `git -C` invocations in `ask`. A broad allow would
have been the natural-looking fix and would have let `git -C <path> push --force`
past both `ask` and `deny` at once.

**A flag written with `=` does too.** `git push --force-with-lease *` needs a
space after the flag, so `git push --force-with-lease=main:<sha> origin main`
matched no deny rule. It fell through to `git push *`, which asks at the top
level and allows in the autonomous agent. Found on 2026-09-24, when an
approved `=`-form force-push went through with no prompt, because `git push *`
had been set to always-allow for that session. Closed with a second pattern,
`git push --force-with-lease=*`.

**An environment prefix does the same.** `FOO=1 pytest` matches no `pytest` rule.
Left alone deliberately: an unmatched command prompts, which is the correct
direction to fail, and an env prefix can change what a command does.

The general lesson is that prefix matching describes command *text*, not command
*intent*, and any rule can be stepped around by writing the same operation
differently. That is another reason this layer is described above as catching
accidents rather than as a boundary.

## Which file (Claude Code)

Settings are **per project directory**, and this machine has two directories
that both look like "the dotfiles project":

- `~/.local/share/chezmoi` — the git repository and the chezmoi source. This is
  the project these rules govern.
- `~/dotfiles` — the chezmoi **deploy target**. Not a git repository. It is a
  separate Claude project scope with its own `.claude/settings.local.json`,
  holding 80 allow rules that are in no repository and that no review has seen.
  One of them is `Bash(chezmoi apply *)` — an unreviewed allow, strictly wider
  than the `ask` the source now applies.

Running an agent in `~/dotfiles` therefore gets none of this and all of that.
Work happens in `~/.local/share/chezmoi`; `~/dotfiles` is output.

Within a project the cascade is `~/.claude/settings.json` (user, all projects) →
`.claude/settings.json` (project, committed, team-shared) →
`.claude/settings.local.json` (project, personal, gitignored).

- **Committed** holds the repository's position: every `deny`, every `ask`, and
  the allows any agent working here needs. It is reviewed.
- **Local** holds one-off personal approvals. Nothing here is reviewed, so
  nothing here should be load bearing.

The previous arrangement had this inverted — personal one-off approvals had
accumulated in the committed file, which is how it grew to 88 rules that no
review ever saw as a whole.

## The opencode layer

opencode's rules live in two files, both versioned here:

- `home/dot_config/opencode/opencode.jsonc.tmpl` — the **global** config, deployed by
  chezmoi to `~/.config/opencode/opencode.jsonc`. Baseline: reads free, git
  allowed, everything else asks, and `external_directory` is deny-first /
  allow-last so only the chezmoi source, `~/code`, and the agent-skill trees
  are reachable outside a project.
- `opencode.jsonc` — the **project** config for sessions run in this repo. It
  sets the bash tier and defines the `autonomous` agent. It is deploy-ignored
  (`.chezmoiignore`) — repo tooling, not a home file.

The two scopes are **deep-merged, project overrides global**. Within a
`permission` map, opencode takes the **last matching rule**, so every map here
puts the catch-all `*` first and the narrowest rules (denies) last. The global
template's bash map had this backwards — `*` at the end — which would have
turned every command into an `ask` at the next restart; it was fixed alongside
the project rewrite.

### The autonomy dial

The default agent is conservative: git read ops, the test/lint toolchain,
interpreters and read-only shell utilities are `allow`; commit/push, network
egress, installs and history rewriting are `ask`; `chezmoi apply` is `ask`
so an agent can help converge a reviewed tree; force-push and credential paths
are `deny`.

`autonomous` (Tab to switch) is the opt-in widening: a complete, self-contained
map that additionally allows commit/push, `gh`, `curl`/`wget`, package installs
and model pulls, plus `webfetch`/`websearch`. Its deny tier is identical to the
default's — force-push and credentials stay blocked no matter which agent is
running. `chezmoi apply` stays `ask`: the author must approve applying the
reviewed tree from main. The agent block is written as a full map so it is
correct whether opencode replaces or merges it over the base.

opencode also ships a built-in dial: `opencode --auto` (or the TUI
"auto-approve permissions" toggle) approves every `ask` that is not explicitly
`deny`. It is coarser than the `autonomous` agent — it widens everything, not the
chosen operations — but it has no config to maintain, so it cannot drift. Prefer
the agent when you want to name what gets widened; use `--auto` for a one-off
unattended run.

The boundary holds for the agent too: `external_directory` and `read`/`edit` are
not widened by `autonomous`, so it cannot read or write outside the chezmoi
source, `~/code`, and the agent-skill trees, however many bash commands it may
run.

### The external-directory boundary and skills (2026-10-16)

Two mechanisms keep skill directories readable, and they fail differently:

- **Runtime auto-allow.** opencode adds an `external_directory` allow for every
  external-skill directory it registered at session start (observed live in the
  permission dump 2026-10-16: the `.claude/skills/…` and `.agents/skills/…`
  entries for each registered skill). This is why almost every session can read
  its own skills without a rule for them.
- **Static allows for the whole trees.** `$HOME/.agents/skills/*` and
  `$HOME/.claude/skills/*` are allowed in the global template. They
  cover what the auto-allow misses: a skill installed after the session
  started (the motivating case — `aboyeur` was unreadable mid-session on
  2026-10-14), and a directory whose `SKILL.md` never registers because its
  frontmatter is missing or invalid.

Neither widening is sent to `ask` by another tier; skills tree content is
agent-authored local files, and the boundary still denies everywhere else.

## Verifying a change

Permission changes could not be verified from inside the session that made them.
Adding a deny rule for a harmless command did not block it, and the cause was
not distinguishable from inside: settings may not reload mid-session, the session
may run in a mode that bypasses rules, or the pattern may not have matched.

**A refusal and a failure look nothing alike, and confusing them costs a test.**
When a rule denies a command, Claude Code refuses the tool call: a permission
message, and no command output whatsoever. When a command merely fails, it ran —
there is output, an exit status, an error from the program itself.

The first attempt at testing this read `chezmoi apply --dry-run` erroring with
`could not open a new TTY` as a successful denial. It was not. The command had
been permitted, executed, and failed for its own unrelated reasons. This is
`spec.md` § Verification — a mechanism that can decline is proven to relent,
wearing a new disguise: a guard that never fired and a command that broke on
its own produce the same feeling of "it didn't work".

So always pair the check with the relenting direction, and prefer a relenting
check that doubles as proof the settings loaded at all. `git checkout` is in
allow here: if it prompts, the session is running some other configuration and
the denial result means nothing.

**Settings load at session start and do not reload.** Checking out a branch
mid-session leaves the old rules in force, which is how the first attempt ended
up testing the configuration it was meant to replace. Put the file in place
first, then start the session.

Be specific about where. "Open a fresh session" is not an instruction — the
first attempt at this test was run in `~/dotfiles`, against a branch that was
not checked out, and could not have passed either way. Name the directory, name
the branch, name the expected outcome for both directions.

So: **verify in a fresh session started in `~/.local/share/chezmoi`, with the
branch carrying the change checked out**, and verify both directions — that the denied
thing is refused, and that ordinary work still runs. A permission file that
denies everything and a permission file that is never read both look like a
quiet session.
