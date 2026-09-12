**Added**

- Agent work-routing policy (`AGENTS.md` § What agents do here): agents in
  this repo work the trunk — which tools, services and configurations belong
  on which machines, with per-machine granularity. Anything needing a build
  follows a three-step ladder: outsource it (AI work to `ai-prompt-library`,
  impromptu eventually), notify and ask, or refuse outright if the author
  declines. Probable builds hidden behind surface-valid config work are
  surfaced to the author for override; determinant detection functions are a
  recorded requirement on the future `topic` CLI / configuration CLI agent
  (`ROADMAP.md`), not something agents build here themselves.
