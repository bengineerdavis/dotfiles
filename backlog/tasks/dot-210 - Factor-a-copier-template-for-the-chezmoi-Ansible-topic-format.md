---
id: DOT-210
title: Factor a copier template for the chezmoi-Ansible topic format
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Factor a copier template for the chezmoi-Ansible topic format. **Its own
  repository at `~/code/personal/`**, same placement as the general template
  above. It **builds on the general template rather than duplicating it** — but
  by composition, not inheritance. Verified against copier 9.17.2: there is no
  `extends`, `inherit`, `parent_template` or `base_template` keyword anywhere in
  the source. Three primitives do the job instead:

  - `answers_file` lets each template record its answers somewhere other than
    the default `.copier-answers.yml`. That is what makes two templates on one
    project possible, and `copier update -a <file>` then updates each
    independently.
  - `_external_data` (a name-to-YAML-path map, exposed to Jinja as
    `external.<name>`) lets the topic template READ the general template's
    answers file and reuse those answers instead of re-asking. Note the path
    must resolve inside the generated project unless `--trust` is passed, so
    the parent's answers file has to be committed there — which it is by
    default.
  - `_tasks` can shell out to `copier copy` of the general template. Available,
    and the most fragile of the three; prefer the first two.

  So: apply the general template first writing `.copier-answers.general.yml`,
  then the topic template writing `.copier-answers.topic.yml` and declaring
  `_external_data` against the first. The topic template contributes only what
  is specific to a chezmoi-Ansible topic.

  **The trap to avoid:** if both templates write to the same default answers
  file, the second silently overwrites the first's tracking and the general
  template can never be updated in that project again. Separate answers files
  are the whole mechanism, not a detail — and getting them right is what
  delivers the actual goal, which is that improving the general template later
  flows into every project built from it, topic repos included. Purpose is that someone can build a topic from scratch with an
  agent, and borrow one piece of this configuration without adopting the whole
  repo — see `PRD.md` § Topics are installable modules. Overlaps refactor A:
  `topical new` scaffolds a topic INSIDE this repo and this template scaffolds one
  for a repo that is not this one. They should share the canonical template
  rather than diverge — decide which owns it before the second is built. The
  module boundary itself is deferred to `ROADMAP.md` and is not a blocker; build
  against the format as it stands.
  **Ownership decided 2026-10-20 (author):** topical owns the canonical
  template first — the skeleton and manager block templates live in the
  topical repo with the generator — and this template inherits from there
  rather than copying.
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
