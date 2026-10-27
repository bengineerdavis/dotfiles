---
id: TASK-144
title: 'Add voice-typing topics: `apps/openwhispr` and `apps/superwhisper`, macOS
  first, with a Linux path t'
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Add voice-typing topics: `apps/openwhispr` and `apps/superwhisper`, macOS
  first, with a Linux path that is not a cask.** Both exist as casks, verified
  2026-09-14: `openwhispr` 1.10.1 ("Privacy-first voice-to-text dictation with
  AI agents", open source, `OpenWhispr/openwhispr`) and `superwhisper` 2.18.3
  ("Dictation tool including LLM reformatting", commercial, macOS >= 14). Both
  declare `auto_updates`, so brew's recorded version drifts — the same
  `known_issues` entry `apps/claude-code` already carries for `Claude.app`.
  Start on Darwin because that is where the casks work; casks are macOS-only, so
  Debian needs a different mechanism and the honest first step is `topic_os:
  [Darwin]` rather than a half-built conditional, exactly as `apps/claude-code`
  did. For the Linux path, `whisper.cpp` is a cross-platform **formula** and is
  the likely base — note the handoff's "SoupaWhisper" sketch is essentially that.
  **An external briefing document exists for this work — not the session handoff
  above — and it does not describe this repo.** It assumes topics named `git/`, `zsh/`, `wayland/`, `macos/` and
  an `openrouter/` topic; this repo has Ansible roles under `dotfiles/apps/` with
  a fixed lifecycle, no `wayland` or `macos` topic, and OpenRouter reached
  through `apps/ori`. Translate it, do not follow it literally. What does carry
  over, and is worth keeping:
  - **No hardcoded credentials.** It wants `$OPENROUTER_API_KEY` from the
    environment rather than baked into a config file. That already matches
    practice here — `llm-openrouter` and `ori` both read it — and
    `AGENTS.md` § "Machine-specific values are resolved, never written out" is
    the rule it is reaching for.
  - **Wayland cannot be assumed.** Its text-injection rules (`ydotool`/`wtype`,
    `wl-clipboard`, adding the user to the `input` group for `/dev/uinput`)
    presuppose a Wayland desktop. **Verify the Debian box actually runs one
    before building any of it** — that is unconfirmed, and the whole Linux
    design rests on it.
  - **Hotkeys belong to the compositor, not the app**, with macOS parity via an
    Apple Shortcut or Automator action calling the same CLI. That shape is
    sound; it needs a real toggle command to exist first.
  **OpenWhispr on Linux is required, not optional** — Darwin-first is about
  sequence, not scope, and this one has to run on the Debian box too. Research
  it properly rather than assuming the cask story carries over; upstream already
  ships for Linux, verified 2026-09-14 against release `v1.10.1`:

      OpenWhispr-1.10.1-linux-amd64.deb        ← apt, matches apps/apt + become
      OpenWhispr-1.10.1-linux-x86_64.rpm
      OpenWhispr-1.10.1-linux-x86_64.AppImage
      OpenWhispr-1.10.1-linux-x64.tar.gz       ← tarball, the apps/ollama shape

  MIT, Electron, actively released. Prefer a package manager over a bare
  download — but note these are the *same* mechanism here, not alternatives:
  `ansible.builtin.apt` takes a `deb:` parameter and downloads it itself when
  given a URL, so "install via apt" and "fall back to the .deb" collapse into
  one task pointing at the release asset. Check first whether upstream publishes
  an actual apt *repository*, which would be better still since it makes
  upgrades ordinary; nothing in the v1.10.1 release assets suggests one, but
  that only rules out the release page. The tarball is the last resort and
  matches how `apps/ollama` already installs on Linux.

  **Architecture is confirmed: the Debian box is x86_64/amd64**, stated by the
  author 2026-09-14, so OpenWhispr's Linux builds apply and the `.deb` path
  stands. Worth keeping in view anyway, because it nearly went the other way:
  every OpenWhispr Linux artifact is x86_64 and there is **no arm64 Linux
  build**, while macOS ships both. Adopt the habit rather than the one-off
  answer — **check a release's actual architecture list before choosing a
  package format**, and prefer reading upstream's published metadata over
  assuming parity with macOS. `apps/ori` already does the honest version of
  this, resolving `arm64` vs `x64` from `ansible_facts` and verifying against a
  published `SHA256SUMS`. Second, the release carries
  `latest-linux.yml`, which is electron-updater metadata: the app self-updates,
  so it has the same two-owners question `apps/claude-code` answered for the
  desktop cask, and the answer has to be deliberate rather than inherited.

  Done when OpenWhispr installs, removes and upgrades cleanly on **both** this
  Mac and the Debian box — or, if the architecture rules it out, when that is
  recorded with the `whisper.cpp` alternative chosen — and superwhisper's
  Darwin-only status is stated as a decision rather than an omission.
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
