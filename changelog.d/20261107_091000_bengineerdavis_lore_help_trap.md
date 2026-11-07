### Fixed

- The LoreAI README now documents that `lore --help` only works at the top
  level. On a subcommand it falls through to the argument parser, so `lore
  setup --help` and `lore data export --help` execute the command, and
  `lore recall --help` exits 0 after failing. `lore help` is the real help
  command.
