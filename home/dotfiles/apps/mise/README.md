# mise App Module

_Template directory for dotfile or tool user/system tool config_

Welcome to my mise app module in my local machine provisioning setup!

## Rust ownership

This topic owns the Rust channel, and rustup owns the toolchain. There is no
separate rust topic, and there should not be one.

The `rust = "latest"` entry in `files/config.toml` is not just a version pin.
mise's `core:rust` backend downloads `rustup-init` and runs it, so this topic
installs rustup. Measured on a clean `HOME` (empty `.cargo`, `.rustup`,
`MISE_DATA_DIR`), 2026-11-04:

```
mise exec rust -- cargo --version
  rust@1.99.1  Downloading rustup-init
  mise rust@1.99.1 info: default toolchain set to 1.99.1-x86_64-unknown-linux-gnu
  cargo 1.99.1
```

Layout afterwards: rustup keeps toolchains in `~/.rustup` and its proxies in
`~/.cargo/bin`; mise points `installs/rust/<version>` at that directory instead
of copying it.

Two things that look like bugs and are not:

- **There is no `mise sync rust`.** `mise sync` offers `python`, `node`, and
  `ruby` only — the linking is inside the rust backend. A `sync rust` call does
  not exist, so do not add one.
- **The `installs/rust/<version>` symlink is deliberate.** Replacing it with a
  real install creates a second toolchain channel, which is the duplication this
  layout exists to prevent.

`cargo:` entries in `files/config.toml` (lychee, broot, eza, fd-find, ripgrep,
and the rest) compile with this toolchain, so they need a linker: `gcc` on
Debian, Xcode Command Line Tools on macOS. Nothing in this topic installs those.

## Links

- [project website](https://mise.jdx.dev/)
- [project git repository](https://github.com/jdx/mise)
- [homebrew package](https://formulae.brew.sh/formula/mise)



See more in https://github.com/holman/dotfiles