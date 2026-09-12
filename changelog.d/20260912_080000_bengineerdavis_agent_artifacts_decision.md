**Added**

- `dotfiles/docs/AGENT-ARTIFACTS.md` — the agent-artifact manager decision:
  skills follow the agentskills.io open format, dotagents installs them
  (pinned refs, committed lock, symlinked canonical store), skills.sh is a
  discovery channel only. Records the survey, the rejected candidates with
  reasons, and the exit path if the manager needs replacing. The queued
  dotagents topic consumes it.

**Changed**

- `docs/REFERENCES.md` gains rows for the Agent Skills spec and dotagents
  (both verified 2026-09-12), updates AGENTS.md's row with its Linux
  Foundation stewardship, and adds a watch list for MCP, ACP, Agent Plugins
  v1 and skills.sh — tracked, deliberately not followed today.
