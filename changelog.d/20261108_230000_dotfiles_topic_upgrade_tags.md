### Fixed

- `apps/dotagents` and `apps/lima` fail under `--tags upgrade`, which is what
  `./update.sh` runs. A fact-registering task carried `[install, provision]`
  while the tasks reading it also carried `upgrade`, so the reader ran without
  its producer and Ansible failed the `when` with
  `'dotagents_manifest' is undefined`. Both topics now tag every task that
  registers a fact with the same lifecycle tags as the tasks that read it.
  `tests/topics/test_task_tag_coverage.py` fails on any role where a variable's
  producer is not selected by every tag that selects a reader.
