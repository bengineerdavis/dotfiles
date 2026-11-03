**Added**

- `tests/backlog/test_queue_integrity.py::test_no_shadowed_task_ids` fails when
  a read command reports a duplicate task id. `checkActiveBranches` loads task
  files from other local branches, so a stale branch holding an older copy of a
  task shadows the on-disk one: the newer commit wins and the loser is skipped.
  `doctor` never scans branch snapshots, so it reported clean for hours on
  2026-11-02 while `task` and `board` warned that DOT-108 was invisible.
