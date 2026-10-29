# TODO: the same manifest idea for editor extensions

**Status: deferred, not designed.** Raised while building `apps/chrome`; parked
deliberately so the browser case could land first. Nothing here is decided.

Sequencing note: this sits *behind* `docs/ROADMAP-topic-cli.md`. The `topic` CLI
MVP (scaffolding + `ext add`) and the firefox topic both come first — they prove
the manifest schema generalises across two browsers before anyone tries to
stretch it to a third kind of host.

## Why it looks like the same problem

`apps/chrome/defaults/main.yaml` ended up with a schema that is not really about
Chrome. An entry says *what* the extension is, *why* this machine has it, and
*where it comes from* — marketplace or git:

```yaml
- source: store          # marketplace id
- source: git            # repo + pinned ref + build + load dir
```

Editors want exactly that shape. `apps/visual-studio-code` and `apps/cursor`
both exist and neither declares its extensions today, so the same drift the
`browser-ext drift` subcommand surfaces for Chrome is currently invisible there.

## Why it is not just a copy-paste

The mechanism differs enough that the shared part may only be the schema and the
CLI, not the tasks:

- **VS Code / Cursor** have a real CLI — `code --install-extension <id>` and
  `code --list-extensions` — so the store case is genuinely *installable*, not
  merely seedable. That is a better position than Chrome, and it means the
  reporting-only stance `browser-ext` takes would be needlessly weak there.
- **Marketplace licensing.** Cursor cannot use Microsoft's marketplace; it uses
  OpenVSX. The same extension has a different availability story per editor, so
  `id` may need an `openvsx:`/`ms:` qualifier or per-editor overrides.
- **`.vsix` from git.** The git case is a build-then-`--install-extension`
  rather than a load-from-directory, so `load_subdir` becomes `vsix_path` or a
  packaging command. Different enough to warrant its own field, not a reuse.
- **No path-derived ID problem.** The single ugliest Chrome constraint — that an
  unpacked extension's identity is a hash of its filesystem path — has no editor
  equivalent. A large part of why the Chrome topic is shaped as it is simply
  does not apply.
- **JetBrains** is a third mechanism again, and may not be worth covering.

## Open questions to settle before writing anything

1. Does the shared piece live as a schema convention that each topic implements,
   or as an actual shared role? The repo has no precedent for shared roles, and
   `docs/TOPICS.md` leans hard on self-contained topics.
2. Should `browser-ext` grow an `--topic vscode` mode, or should there be a
   sibling `ide-ext` with its own verbs? The audit half generalises cleanly; the
   install half does not.
3. Do Cursor and VS Code share one manifest with per-editor filters, or one
   manifest each with duplication? They share most extensions in practice.
4. Is drift detection even the valuable half for editors? Unlike Chrome, editor
   extensions are trivially reinstallable, so the payoff may be reproducibility
   on a fresh machine rather than catching unnoticed additions.

## What to reuse when it is picked up

- The `source:` discriminator and the `why:` field — the second one has already
  earned its place by making the `review`/`it-owned` distinction possible.
- The `<topic>_extensions_ignored` list with verdicts. Editors ship bundled
  extensions exactly like Chrome ships components, and the same noise problem
  will appear.
- `browser-ext`'s manifest append logic, which edits YAML as text specifically
  so the comments survive.
