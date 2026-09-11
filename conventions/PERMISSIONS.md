# PERMISSIONS.md

How agent permissions are set in this repository, and — more importantly — what
they do not protect against.

The rules live in `.claude/settings.json`, which is JSON and cannot carry
comments. This file is the reasoning behind them. Change them together.

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

- `chezmoi apply` in any form. `AGENTS.md` § Applying is main-only says agents
  never apply; there is one deployed tree and it cannot be branched. This rule
  existed as an **allow** until today, which is why the convention and the
  configuration disagreed, and the configuration is what actually decides.
- Force-push and history rewriting tools. `spec.md` § Change records requires a
  backup branch and `git notes` first, and a rewrite does not un-publish.
- Credential stores and secret files. These are read-denies, and Claude Code
  extends a Read deny to Edit and Write on the same path.

**ask** — legitimate, but irreversible or outward-facing. The prompt is the
point: it is the moment a human sees what is about to happen.

Publishing (`git push`, `gh`), machine mutation (`brew`/`pip`/`npm` installs,
`launchctl`, `./run-role.sh`), destruction (`rm`, `git reset --hard`), network
egress (`curl`, `wget`), secret access (`op`), and large or destructive model
operations (`ollama pull`/`rm`).

**allow** — read-only inspection, and changes that git can undo.

Reading and searching, git operations that stay local, running tests, the
validators, `chezmoi` read commands plus `add` (which only moves deployed
content into a git-tracked source), and the interpreters.

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

## Two ways a rule quietly fails to match

Both were found while writing these rules, and both matter because the failure
is silent — the command runs, and no tier claims it.

**A flag before the subcommand changes the string.** `Bash(git push *)` does not
match `git -C /some/path push`, because matching is against the whole command
text and that text no longer begins with `git push`. Twenty-seven of the rules
this config replaced used the `git -C` form, so this is not hypothetical. It is
closed here by putting **all** `git -C` invocations in `ask`. A broad allow would
have been the natural-looking fix and would have let `git -C <path> push --force`
past both `ask` and `deny` at once.

**An environment prefix does the same.** `FOO=1 pytest` matches no `pytest` rule.
Left alone deliberately: an unmatched command prompts, which is the correct
direction to fail, and an env prefix can change what a command does.

The general lesson is that prefix matching describes command *text*, not command
*intent*, and any rule can be stepped around by writing the same operation
differently. That is another reason this layer is described above as catching
accidents rather than as a boundary.

## Which file

The cascade is `~/.claude/settings.json` (user, all projects) →
`.claude/settings.json` (project, committed, team-shared) →
`.claude/settings.local.json` (project, personal, gitignored).

- **Committed** holds the repository's position: every `deny`, every `ask`, and
  the allows any agent working here needs. It is reviewed.
- **Local** holds one-off personal approvals. Nothing here is reviewed, so
  nothing here should be load bearing.

The previous arrangement had this inverted — personal one-off approvals had
accumulated in the committed file, which is how it grew to 88 rules that no
review ever saw as a whole.

## Verifying a change

Permission changes could not be verified from inside the session that made them.
Adding a deny rule for a harmless command did not block it, and the cause was
not distinguishable from inside: settings may not reload mid-session, the session
may run in a mode that bypasses rules, or the pattern may not have matched.

So: **verify in a fresh session**, and verify both directions — that the denied
thing is refused, and that ordinary work still runs. A permission file that
denies everything and a permission file that is never read both look like a
quiet session.
