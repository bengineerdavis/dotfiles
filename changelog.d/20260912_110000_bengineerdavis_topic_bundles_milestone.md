**Added**

- Topic bundles, as a milestone: data-first grouping (`apps/bundles/*.yml`)
  where the bundle config object owns member lists, run order, shared
  configuration, and machine targeting — relationships live in the bundle,
  not inside each topic, so grouping is visible without opening every topic
  and topics stay standalone-installable. Bundle-limited install, update and
  teardown land in the parent playbook first; the `topic` CLI consumes the
  same files after its MVP. First instance is an AI-strategy bundle composed
  per machine. Requirements in `PRD.md` § Bundles compose topics; three work
  items in `TASKS.md` § Topic bundles.
