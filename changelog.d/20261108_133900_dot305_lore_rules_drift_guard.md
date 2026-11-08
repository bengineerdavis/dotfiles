### Added

- A drift guard (`tests/docs/test_lore_md_rules_survive.py`) now fails the
  suite when a load-bearing rule vanishes from `.lore.md`. The Lore daemon's
  re-distillation has repeatedly corrupted entries — a title/body swap that
  deleted the `uv run --frozen` safety rule, a heal that deleted a correct
  entry and wrote a false trap, and a wrong decision pointer (DOT-305). The
  guard greps each known rule's distinctive anchor after every rewrite so a
  loss is caught in the suite instead of in a review. `.lore.md` stays
  captures-only; the fix direction is upstream (DOT-298 pattern).