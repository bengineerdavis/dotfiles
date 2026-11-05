# Trust ladder

An agent earns wider autonomy by track record, **per task class and blast
radius**, never globally. Task classes: docs, tests, code, policy, deployed.
An agent may sit at rung 3 for code and rung 1 for policy at the same time.

### Rungs

| Rung | What the agent may do |
|---|---|
| 0 | Propose only. Every diff is reviewed before it is committed. |
| 1 | Commit to a branch and open a PR. Nothing reaches main unreviewed. |
| 2 | Self-merge docs and tests when § Merge gates pass. |
| 3 | Self-merge code inside a named blast radius when § Merge gates pass. |
| 4 | Work unattended on a task class and report async. |

A first-time agent starts at **rung 0 in every task class** — propose only —
until the ledger exists to promote against (queued: § Planned, Build the
LEDGER).

**Promotion** is a streak of clean items at the current rung: 5 to reach rung 2,
10 to reach rung 3, 20 to reach rung 4. Clean means merged with no author
correction of any class below. The counts rise because the cost of a mistake
rises with what the rung permits.

**Demotion** is by incident class. Rung 0 has no floor below it.

### Incident classes

Defined here, in advance, because a class invented to explain a particular
failure is not a class — it is an excuse with a name.

**Class A — disclosure or policy bypass. Drops to rung 0, every task class.**

- Work or customer data, employer-identifying strings, or machine-local usage
  figures committed, sent off-device, or written to a shared store.
- Egress without consulting the resolver, or treating unknown (2) as permitted.

One occurrence ends autonomy everywhere, not just in the class where it
happened. The reason is that the harm does not reverse: `spec.md` § Change
records already records that a history rewrite does not un-publish, so anything
fetched, forked or indexed is beyond recall. A ladder that let an agent climb
back after this would be pricing an irreversible harm as a recoverable one.
Reinstatement is an explicit author decision, not a streak.

**Class B — corrupted evidence. Drops two rungs.**

- A test that passes without exercising what it claims to: a grep over empty
  output, an `assume()` that filters away every generated input, a fixture too
  simple to reach the bug.
- A gate reported as passing that was not actually run — a mutation check
  claimed in a commit message but never performed.
- Work reported as done that is not, or a claim that something works without
  naming what was not checked.

This is worse than a plain bug and is deliberately punished harder. The ladder
runs on the evidence in the ledger; an agent that can misreport a gate makes the
whole instrument fiction. Every one of these has already happened here at least
once, which is why `spec.md` § Verification carries them.

**Class C — process violation. Drops one rung.**

- Editing a file under § Cross-session hazards without a claim, or running
  `chezmoi apply` at all.
- A commit whose contents do not match its message, staging not verified, or an
  intermediate state that leaves the tree broken.
- Shipping against a stated behavior in `spec.md` — a teardown not updated with
  the thing it creates, a measured number moved without its conditions.

**Class D — judgment. Drops one rung above rung 2; a recorded warning at or
below it.**

- Resolving a material ambiguity silently instead of asking.
- Doing work the task did not define, or quietly narrowing work it did.

Judgment errors are treated more gently at low rungs on purpose. An agent
learning the repository will misjudge scope, and demoting for it teaches
caution about *asking*, which is the opposite of what § Start here requires.

### What is not an incident

Stated explicitly, because a ladder that punishes these produces an agent that
hides things.

- A bug that review caught and the tests could not have caught. That is a
  coverage gap, and it becomes a test.
- A refusal that turned out to be unnecessary. Failing closed is the designed
  behaviour; being wrong about it costs nothing.
- Asking a question whose answer already existed. **Asking is never an
  incident.** If questions cost trust, the agent stops asking, and the prime
  directive dies quietly.
- An approach tried, reported honestly, and abandoned.

### Ageing

A Class C or D incident stops counting against promotion after five clean items,
but stays in the ledger permanently. Class B ages out after twenty. Class A does
not age out. The ledger is a record, not a scoreboard to be reset — its value is
that a pattern across months stays visible.

