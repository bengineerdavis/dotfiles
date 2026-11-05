### Changed

- `apps/mise` now advertises `rust`, `rustup`, and `cargo` in
  `topic_provides`, so a topic can depend on the Rust toolchain with
  `topic_requires: [cargo]` instead of installing a compiler itself. The
  install was already happening: mise's `rust` entry runs the `core:rust`
  backend, which downloads and runs `rustup-init`. Only the declaration was
  missing. `docs/TOPIC-RECIPES.md` records why rust is a mise entry rather
  than a toolchain topic, and why there is no `mise sync rust` to call.
