---
id: DOT-393
title: Prove whether a subagent can write a file, since ours returned its own session
  log
status: To Do
created_date: 2026-11-19 19:00
updated_date: 2026-11-20 16:42
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Subagents are enabled and they run, but on 2026-11-19 a research subagent
returned **its own session log instead of the deliverable**, and wrote no file.
This is the failure mode already recorded in memory (observed twice in one
session, 2026-11-10): the completion notification reads as success and the
reply reads like a report.

**Measured, from `~/.local/share/opencode/opencode.db`:**

- The child session row exists (title "Research agent config across repos").
- `session_message` holds 3 rows: `user`, `assistant` (197,110 bytes),
  `idle`. Finish reason `stop` — a clean completion, not an error.
- Cost `$0.024`, output tokens **48,908**.
- Agent `general`, model `~deepseek/deepseek-flash-latest` — **identical to the
  parent session's model**.
- The 195,360-character assistant text begins `# Session Summary`,
  `## Conversation history`, `### Segment 1` — it is a distillation of the
  **parent's** history, ending in the parent's own skill boilerplate.
- The requested output path did not exist afterwards; `docs/research` appeared
  in the text 10 times only because the prompt named it.

**A second, distinct failure** in the same table: 193 child sessions exist and
119 have messages, so **74 children produced nothing at all** (session row, no
messages). Log-echo and never-started are different bugs; this task covers the
echo because it is the one that silently wastes money and yields no artifact.

**Working hypothesis (structural, not flaky):** the child inherits the
parent's distilled context — same model, Lore-compressed history — so instead
of doing the task it summarizes the history it was handed. The `research` skill
states the requirement it violates: "Start it with a fresh context window." A
child that inherits the parent's distillation is not a fresh context, and a
context-holding session asked for a report will produce a summary of that
context.

**This is a hypothesis, not a finding.** It fits all the observations but has
not been isolated — an alternative is that the prompt itself (long, structured,
ending in "Report back a summary") invited summarization, independent of
inherited context.

Ship:

- **A minimal probe task, run first**: spawn a subagent whose entire
  instruction is "write exactly `PONG` to `<path>` then reply with one line".
  Record whether the file appears. This is the cheapest discriminator between
  "cannot write files" and "chose to summarize instead".
- **A second probe isolating the context hypothesis**: the same probe spawned
  from a session with a large history versus one with almost none. If the
  large-history parent produces a log-echo and the small one does not, the
  hypothesis holds.
- **The result recorded either way** — including "cannot reproduce", which is a
  legitimate outcome. The probe exists to answer a question, not to justify a
  fix.
- **If the echo reproduces**, a documented workaround pattern for prompts:
  demand a filesystem artifact and a one-line reply, so a history-echoing child
  cannot satisfy the instruction. Explicitly *not* a fix — a workaround
  recorded as such.
- **A note on the 74 no-message children** as a separate observation, with the
  query that measured it, so the next reader does not conflate the two.

Constraints:

- **Probe before theorizing.** The hypothesis above is written down so it can
  be refuted; do not build a fix on it before the probe runs.
- Do not disable subagents. They work for 62% of children; the task is to
  characterise the failure, not to remove the capability.
- Do not treat the subagent's reply as evidence of its own work. Verify the
  artifact on disk, per the standing rule.
- The `message` table is legacy — the live table is `session_message`
  (`id, session_id, type, seq, time_created, time_updated, data`). Querying
  `message` returns 0 rows and reads as "the subagent never ran", which is
  false. Record this so the next investigation does not repeat the error.
- No fix is scoped here. This task produces a measurement and a workaround; the
  root cause may be upstream (OpenCode context inheritance, or Lore's
  distillation reaching child sessions) and belongs in its own task.

Scoped deliberately loose. The author asked for the probe as its own task for
now.

Decision 2026-11-19: measure whether a subagent can be made to write a file
before changing how subagents are used.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->

- [ ] #1 A minimal probe runs first: a subagent told only to write exactly PONG to a given path then reply with one line, with the file's existence recorded
- [ ] #2 A second probe isolates the context hypothesis: the same probe from a large-history parent versus a near-empty one
- [ ] #3 The result is recorded either way, including cannot-reproduce as a legitimate outcome
- [ ] #4 If the log-echo reproduces, a workaround pattern is documented (demand a filesystem artifact plus a one-line reply) and explicitly labelled a workaround, not a fix
- [ ] #5 The 74 no-message children are recorded as a separate observation with the query that measured it, not conflated with the log-echo
- [ ] #6 The session_message schema is recorded in the task so the next investigation does not query the legacy message table and conclude the subagent never ran
- [ ] #7 No fix is scoped here; if a root cause is found it is filed as its own task with the evidence
- [ ] #8 Subagents are not disabled as part of this work, since 119 of 193 children function
- [ ] #9 The artifact is verified on disk, never the subagent's reply
- [ ] #10 The board lists DOT-393 with the full description and every criterion: uvx --from backlog-md-py backlog-py board
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
