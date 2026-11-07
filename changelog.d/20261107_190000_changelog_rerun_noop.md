### Fixed

- Re-running the changelog collection a second time is now a no-op instead of
  a failure. The collector deletes a PR's fragments as it collects them, so a
  second manual re-run found `test -f` failing on a file that was gone, and
  `set -e` turned that into a red run for a PR whose entry was already correct.
  Pressing Re-run twice is the natural response to not knowing whether the
  first one worked, so the old behaviour taught that a red collection run is
  noise. Running it once still collects normally, and a PR with two fragments
  where only one was collected still collects the other.