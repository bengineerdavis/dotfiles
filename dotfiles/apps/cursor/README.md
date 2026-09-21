# cursor

Installs the Cursor IDE on macOS via the Homebrew cask into
`~/Applications`, and removes it the same way. The cask self-updates, so
there is no topic-level upgrade work: `apps/homebrew`'s upgrade pass covers
what brew can move and Cursor's own updater covers the rest.

## Run

From `dotfiles/`:

```bash
./executable_run-role.sh cursor            # provision the topic
./executable_run-role.sh cursor install    # install only
./executable_run-role.sh cursor remove     # opt-in teardown (tagged never)
```

## Not in scope here

Extensions. Cursor is a VS Code fork and is expected to share its extension
set with VS Code and the other downstream IDEs; that design is queued in
`TASKS.md` § Now and will land as its own wiring, not as tasks here.
Extensions resolve through OpenVSX rather than Microsoft's marketplace, so
per-extension availability differs.
