**Changed**

- The global mise config is now a regular chezmoi-managed copy rather than a
  symlink into the source checkout. Source changes no longer change the live
  config until you apply them. Local `mise use -g` edits need deliberate capture
  before a later apply; DOT-240 retains that capture-trigger design.
