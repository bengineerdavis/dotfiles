<!-- managed by agentic-project-template -->
# Branch synchronization

Reusable owner: `bengineerdavis/agentic-project-template`, APT-32. This file
records the decentralized Git and GitHub behavior adopted here.

Start new work from current `main`; update open PR branches frequently. The
local rule uses ordinary Git. The optional scheduled adapter is GitHub-specific.
No part requires `redge`.

## New worktrees

`wt switch --create <task-id-slug>` invokes the blocking `pre-switch` hook.
The helper finds the `main` worktree, fetches `origin/main`, and fast-forwards
local `main` before Worktrunk creates the branch. A dirty, diverged, or missing
`main` checkout stops creation. Existing task worktrees are left alone; stacked
branches keep their parent. The source worktree may contain in-progress work.

Use `wt switch --create <child> --base <parent>` only for a real dependency.
Keep each PR to one outcome. A base update changes the PR's ancestry, not its
intended functional diff; it does not reduce a large feature.

## The GitHub adapter

`.github/workflows/branch-sync.yml` runs after pushes to `main` and every 15
minutes. GitHub schedules are best effort, so the push trigger supplies the
immediate pulse.

Enable Settings → Pull Requests → **Always suggest updating pull request
branches** before enabling the workflow. Scheduled and push-triggered runs
perform native clean merges. A manual **dry_run: true** run reports without
changing PRs. No PR is merged into `main` by this workflow.

The pulse uses the repository's default branch, GitHub's compare endpoint, and
`PUT /pulls/{number}/update-branch` with the listed head SHA. GitHub rejects an
update if that head moved concurrently. Conflicts or API errors make the run
fail; other eligible PRs are still processed.

The adapter handles only same-repository PRs targeting the default branch.
Fork PRs and stacked PRs are reported without an update. A stacked branch must
be reconciled with its parent explicitly. There is no automatic rebase,
force-push, or PR code execution.

## Other forges

The fresh-base helper is portable Git behavior. The scheduled workflow is not:
GitHub's `allow_update_branch` setting and update-branch endpoint have no Git
standard equivalent. Gitea, GitLab, and other forges need a separately verified
adapter. Do not present the GitHub workflow as portable across them.

Repository settings are not stamped by Copier. On GitHub, bootstrap them with:

```sh
gh api -X PATCH repos/OWNER/REPO -f allow_update_branch=true
```

A future centralized coordinator may provide more scheduling and stack-aware
updates, but removing it must leave these repository-local mechanisms usable.

## Decision record

Adopted 2026-11-05 after checking Worktrunk 0.81.0's `--help`, GitHub's REST
reference, and the real repository settings. GitHub's update-branch API is the
native clean-merge operation, with `expected_head_sha` concurrency protection;
the workflow never checks out PR code.

Rejected: a checkout-and-merge loop (unnecessary worktree and trust surface);
third-party auto-update actions (another dependency for a native capability);
scheduled rebases or force-pushes (rewrite reviewable history); and treating
the GitHub setting as a portable Git or Gitea/GitLab feature.

Verified before writing the adapter: GitHub PR `behind_by` can be null, so
behindness uses the compare endpoint. `gh api` supports the update operation;
the native setting is `allow_update_branch`. Worktrunk runs `pre-switch` before
creating a worktree.
