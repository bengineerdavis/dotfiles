# gita

Registers the repos already on disk so `gita fetch` / `gita pull` work, and
owns the sync path on `--tags upgrade`. It is the stopgap while `redge-cli`
is built.

## What it manages

| Layer   | State | Owner |
|---------|-------|-------|
| mise    | installs the `gita` binary | `apps/mise` |
| this topic | owns the `pipx:gita` entry — `mise use -g pipx:gita` / `mise unuse --global pipx:gita` | `apps/gita` |
| this topic | the registration — gita's `repos.csv`/`groups.csv`, written from `config/repos.yaml` | `apps/gita` |
| this topic | sync on `--tags upgrade` (`gita fetch` + `gita pull`) | `apps/gita` |

The entry is owned the herdr way (TOPIC-RECIPES, tool-entry ownership): mise
installs the binary, but this topic claims and removes the `pipx:gita` entry
through mise's own first-party commands, so install and remove round-trip. The
commands write through the deployed symlink into the tracked
`apps/mise/files/config.toml`; a run that changes the entry leaves the repo
dirty by design and the change is committed as the capture.

## Stopgap scope, and what it deliberately does not do

- **Registers at current paths.** The repos live at `~/code/projects/…`, not
  yet the `docs/LAYOUT.md` type dirs. `install.yaml` registers each repo where
  it is and gives it the group the catalogue declares. The physical migration
  into `personal/`/`forks/`/`work/` is LAYOUT phase 4 — a separate step; gita
  re-registers a repo on move and nothing is deleted.
- **No catalogue discovery.** `config/repos.yaml` is the source of truth; a
  repo declared there but not cloned is skipped and reported.
- **`work/` is empty on the author's own machines.** The group exists in the
  catalogue but has no members here; it is exercised on the work machine.

## The catalogue

`config/repos.yaml` maps repo (path relative to `~/code`) to group
(`personal` / `forks` / `work`), split by **ownership** per `docs/LAYOUT.md`.
Employer strings are never committed — work repos are named only in a
machine-local overlay.

## Sync is not atomic

gita has no `sync`. The honest day-to-day is `gita fetch` (never touches the
working tree) then `gita pull` (pulls clean repos, leaves dirty/conflicted
ones alone). `upgrade.yaml` does exactly that, with `failed_when: false`:
repo problems are reported, the run exits 0. This is a deliberate deviation
from TOPIC-RECIPES' "fail once at the end" — the parent playbook's topic loop
has no rescue, so raising here would skip every later app topic.

No-remote repos (local experiments, tutorials) fetch/pull to nothing; gita
reports them, they do not abort the run.

## Teardown

`--tags remove` removes the `pipx:gita` mise entry (undoing its own claim) and
never deletes clones — gita only indexes repos, the clones are the author's.
Clearing the registration is opt-in behind `gita_remove_registration`:

```bash
ansible-playbook apps/gita/playbook.yaml --tags remove -e gita_remove_registration=true
```

`gita clear` removes every repo the user ever registered, including any added
by hand, so it is gated; the mise entry removal is ungated (it undoes exactly
what install claimed). The two `mise` shell-outs are the stopgap form — a
declarative mise module/role (call mise like apt/homebrew) is queued in
`TASKS.md` and replaces them.

## Known limits

- **Duplicate basenames.** `github/gitignore` was cloned twice; gita names
  repos by basename, so only one copy is in the catalogue. Two git repos with
  the same basename still collide in gita.
- **Stay out of `gita`'s file.** `repos.csv`/`groups.csv` are gita's own
  state; the topic writes them via gita's first-party `add`, never by editing
  the CSV directly.