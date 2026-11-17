---
id: draft-19
title: Build /jot and a safe inbox loop in ai-prompt-library
status: Draft
created_date: 2026-11-16 06:06
labels:
- idea
- inbox
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ideas arrive mid-session and either derail the work or get lost. The author wants a two-stage cycle: capture with no discussion, then a safe automatic tidy, then an interactive finish with ask-matt.

Ship:

- `/jot <thought>`: a skill that writes the message as one backlog draft labelled `inbox`, commits it, replies with the draft id, and returns to the session's work
- a safe loop, run on demand, that reshapes inbox drafts into the Why/Ship/Constraints form, keeps the author's original words in the notes, adds `related:` and dependency suggestions as notes, and commits one draft per commit
- a short pointer in /jot's docs to the stage-2 path: /grill-with-docs on a draft, then /to-spec and /to-tickets or `draft promote`

Constraints:

- this is a build: home is ai-prompt-library, installed everywhere through dotagents, not here
- the loop never promotes, deletes, merges or splits a draft; anything that changes what the work is stays with the author in stage 2
- the loop runs on demand and becomes scheduled only after it earns trust (docs/TRUST-LADDER.md)
- the loop starts on the current session model; DOT-347 is related, not a blocker; switching models later needs a measured run first
- repos without a backlog need a fallback, settled in the skill's own grill

Grill decisions, 2026-11-15:
- Q1: parked ideas become drafts labelled `inbox`, so raw ideas are never claimable
- Q2: the skill lives in ai-prompt-library; named `/jot`. Runner-up `/inbox` was a strong second (it matches the label and reads well as `/inbox sort`); revisit if `/jot` doesn't stick. Rejected: /park (author), /capture, /note, /stash (clash with chezmoi/lore capture, git notes, git stash)
- Q3: the loop is on demand first, scheduled only after it earns trust
- Q4: the loop's writes are limited as stated in the Constraints above
- Q5: the current model to start with, DOT-347 as a later upgrade
- Q6: stage 2 reuses the ask-matt flow, for now
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
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
