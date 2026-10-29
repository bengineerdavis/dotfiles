# Backup host, install and recovery research (BK1)

**Checked 2026-09-23.** Public-source research only. No account, purchase,
installation, credentials or backup operation was performed. This report follows
the approved configuration-backup boundary in the [PRD](../../PRD.md#configuration-backups):
customer data stays on work machines; work configuration is held only in work
1Password; personal configuration may be backed up encrypted from an explicit
allowlist. The work Mac gets no Borg.

## Recommendation

1. **Host:** Prefer BorgBase for the home Linux machine. It is purpose-built for
   Borg, exposes append-only keys, alerts when backups go stale, supports account
   2FA, and has an explicit route for maintenance compaction. Its free tier is
   10 GB; the smallest paid tier is $30/year for 250 GB. Choose the provider and
   authorize any purchase separately.
2. **Install:** Pin Borg to **1.4.x**, currently **1.4.5**. Use mise's GitHub
   release backend with a version and per-platform SHA-256 lock for the
   Debian/Linux binary and Borg's macOS 15 binary after confirming that the
   personal Mac supports that artifact. Install **borgmatic 2.1.8** using the
   upstream `uv tool` method at that exact version on Debian and personal macOS.
Homebrew is the compatibility fallback when the direct Mac artifact does not
fit; its current formula is Borg 1.4.5, but the Ansible Homebrew module has no
pinned state, so a strict version pin needs an author-approved `brew pin` /
`brew unpin` fallback.
3. **Recovery:** Keep a `Backups/Borg` folder in the personal Bitwarden vault,
   with one Secure Note for each repository's identifier, location and exported
   Borg key, and a separate Secure Note for its passphrase. Keep Bitwarden's
   two-step recovery code offline, outside the vault and away from the phone.
   The recovery code also requires the Bitwarden master password; confirm that
   the master password is available without the lost device.
4. **Retention:** A reasonable starting proposal is an 8-hour home schedule
   while the GNOME keyring is unlocked, with a 12-hour stale warning, and
   14 daily / 8 weekly / 12 monthly restore points. This gives a short recovery
   window for recent edits and about a year of history. The newest archive must
   always remain. Keep this as a recommendation pending the author's cadence and
   retention choice; no space use has been measured.

## Host comparison

All three candidates document Borg over SSH and append-only behavior. The
comparison gives no invented reliability scores.

| Rank | Host | Verified price and commitment | Fit and trade-off |
|---|---|---|---|
| **1** | [BorgBase](https://www.borgbase.com/) | 10 GB and 2 repositories free forever, no card required. Paid Small: **$30/year**, billed annually, includes 250 GB; flexible usage to 1 TB is charged at $0.015/GB/month. Prices exclude VAT. | Best match: dedicated Borg service, append-only/delayed-delete mode, account 2FA, monitoring, EU/US repository regions, and a documented all-access key for prune/compact. Its append-only key can issue prune/delete markers but cannot permanently remove old segments. Permanently pruning requires an all-access key; compaction can then run with that key or through the control panel. One repository is not geographic redundancy. Storage use is unknown, so 10 GB suitability is not assumed. |
| **2** | [rsync.net Borg accounts](https://www.rsync.net/products/borg.html) | **$0.01/GB/month, 200 GB minimum, paid annually**: $2/month equivalent or **$24/year minimum**. The provider says no other costs or contracts; annual prepayment is still required. | Direct SSH/UNIX access, unlimited Borg repositories, and customer-controlled `authorized_keys` restrictions including append-only. A good alternative for more server-side control and a lower verified annual minimum. Borg-specific accounts do not include ZFS snapshots, extra logins/subaccounts, or Borg-specific integration support; key restrictions, alerts and maintenance need more operator setup. |
| **3** | [Hetzner Storage Box BX11](https://www.hetzner.com/storage/storage-box/bx11/) | 1 TB, 10 snapshots, no minimum contract term, cancel immediately. **The current exact price was not available in the public page's text/API response during this check**, so no amount is quoted. | First-party docs support Borg 1.4 using `--remote-path=borg-1.4`, port 23, and append-only mode. Germany/Finland locations are offered. The docs do not establish how to configure separate append-only and maintenance identities on this restricted SSH service; verify that before choosing. |

BorgBase ranks first on fit, not on price. Its free tier is the lowest entry
cost, while its paid tier has an annual commitment. rsync.net is the clearest
lower-cost paid alternative. Hetzner remains conditional until its live price
and separate-key workflow are confirmed. These figures are public prices, not
purchase authorization.

### Rejected storage patterns

- **Do not copy or sync a live Borg repository** to make a second backup. Borg
  recommends initializing a second independent repository and running a second
  `borg create`; using a repository and its copy can corrupt data and reuse
  AES-CTR counters. The FAQ points to a user incident where deleting from a
  hard-linked copy damaged the other repository ([issue #4272](https://github.com/borgbackup/borg/issues/4272)).
- **Do not put a live repository in a cloud-sync folder.** This is the same
  shared-repository/counter-reuse hazard, not independent redundancy.
- **Do not have multiple machines write to one repository.** Use one repository
  per client machine per destination.

For the approved home design, keep the local repository and the off-site host
repository independent, with a separate `borg create` to each. After losing a
machine, restore from its old repository, then initialize a new repository for
future writes; do not resume writing to the old one after losing the client's
local Borg security state. Export each repository's key with `borg key export`
and keep that and its passphrase off the source machine.

## Install path and Galaxy-role grade

### Borg and borgmatic

| Target | Recommendation | Why / boundary |
|---|---|---|
| Debian/Ubuntu home Linux | `mise` GitHub backend, **Borg 1.4.5**, with explicit Linux asset selection and a checksum recorded for each supported architecture; `uv tool install borgmatic==2.1.8` as the backup user. | Borg's official distribution-package page warns that distro packages can lag releases. APT is acceptable only when the target's candidate is verified to be Borg 1.4.x; no distro-specific candidate was inferred here. The upstream 1.4.5 release publishes Linux binaries and SHA-256 asset digests. `mise github:` supports pinned releases, platform-specific assets and checksums, matching this repo's GitHub-release convention. Borgmatic's current install guide recommends `uv tool`; it deliberately does not install Borg itself. |
| Personal macOS | Same pinned Borg 1.4.5 release asset targeting macOS 15, plus `uv tool install borgmatic==2.1.8`, after confirming compatibility with the target Mac. The official Homebrew formulas are the fallback when that artifact does not fit. | Homebrew currently bottles Borg **1.4.5** and borgmatic **2.1.8** for Apple Silicon and Intel. Borg's macOS 15 release binaries do not include FUSE, but the approved extract-based restore does not need `borg mount`. `community.general.homebrew` 13.0.1 has no `pinned` state; Homebrew itself has `brew pin`, but using that shell command in a topic needs author approval under [TOPIC-RECIPES](../TOPIC-RECIPES.md). |

The pinned versions observed on 2026-09-23 are Borg **1.4.5** (released
2026-07-18) and borgmatic **2.1.8** (released 2026-09-18). Borg's own 2.0.0b23
release says “do not use this on production backup repositories”; the approved
1.4.x choice remains correct. The Borg 1.4.5 GitHub tag is signed. The
[`mise` GitHub backend](https://mise.jdx.dev/dev-tools/backends/github.html)
supports platform asset patterns and pinned checksums; the later topic should
record the selected asset hashes in its lock/config and verify the installed
`borg --version` stays in 1.4.x.

**Rejected install paths:** `pipx:borgbackup` is not the thin route: PyPI
publishes Borg 1.4.5 as a source distribution, and Borg's install guide lists a
compiler plus ACL, OpenSSL, LZ4, Zstandard and xxhash development headers for a
source build. That adds platform-specific build state and upkeep. Unpinned APT
or `brew upgrade` alone does not guarantee the chosen Borg 1.4.x series.

The GitHub release entry for Borg 1.4.5 publishes distinct Linux x86-64,
Linux ARM64, macOS Intel and macOS Apple Silicon artifacts with asset digests.
The macOS artifacts target macOS 15; the Linux x86-64 asset is the glibc 2.31
build, while the published ARM64 binary targets glibc 2.35. Match the target's
OS, architecture and glibc before installing. No host facts were read for this
research.

`dotfiles/apps/mise/files/config.toml` is a cross-session hazard. The future
topic must claim it before adding a Borg entry, and remove its entry on teardown.
Backup scheduling and capture logic stay in borgmatic; Ansible only installs
the tools and owns their service/timer state, consistent with
[TOPICS.md](../TOPICS.md) and its CRUD teardown rule.

### Galaxy roles reviewed

| Role | Upstream support evidence | Fit against this task | Verdict |
|---|---|---|---|
| [`borgbase.ansible_role_borgbackup`](https://github.com/borgbase/ansible-role-borgbackup), v2.0.0 | Named maintainer; latest code commit 2026-05-23; MIT license; Molecule scenarios and CI. Role metadata lists Debian, Ubuntu and Arch Linux. It has `borg_version` / `borgmatic_version` constraints for `pip` and `uv`, but its borgmatic default is only `>=1.8.0`; the package method is not pinned. | No macOS support and no `tasks/remove.yml`, despite managing packages, user, SSH key, config and timer. Its install-only switches narrow side effects but do not provide topic teardown. | **Grade B upstream; reject as a complete topic role** because platform coverage and teardown do not meet the fleet/topic contract. |
| [`kliwniloc.borgbackup`](https://github.com/kliwniloc/ansible-role-borgbackup), v2.0.0 | Named maintainer; release 2026-09-01; MIT license; Molecule `default` and `delete` scenarios run by CI. Metadata lists Debian and Ubuntu. It has explicit `state: absent`, default-preserves repository data, optional per-repository append-only SSH keys, and a separate destructive data-delete flag. | It provisions and delegates to an Ansible-managed Borg server, installs unpinned APT `borgbackup`, requires a new `community.crypto` collection, and writes Borg commands/systemd timers itself; it does not install the already-chosen borgmatic. By default it exports decryption keys to an Ansible-repository YAML file. `state: absent` deliberately leaves Borg packages, server user/home, shared keys and known-hosts entries. It cannot configure an unmanaged BorgBase/rsync.net host through the documented delegation path. | **Grade B upstream; reject for BK1.** It is maintained and tested, but its self-hosted server workflow, version path, key destination and partial teardown miss the approved managed-host/Borgmatic/Bitwarden design. |

Older search results included archived or long-stale roles (for example,
`SphericalElephant/ansible-role-borgbackup`, archived with its last push in
2019). They do not beat the current candidates on maintenance. Neither reviewed
role is recommended wholesale. A thin topic is the better fit: native `mise`
and `uv` installation, explicit version checks, and removal of every
topic-created timer/config/key artifact, without reimplementing Borg or
borgmatic.

## Passphrases, config recovery and the exit-75 guard

The version thresholds are:

| Capability | First documented borgmatic version | Consequence |
|---|---:|---|
| `config bootstrap` | **1.7.15** | Can extract borgmatic's own saved configuration from an archive on a fresh machine. Version 2.1.8 includes the action. |
| `encryption_passcommand` run once per borgmatic invocation | **1.9.9** | A `secret-tool lookup ...` command can supply the passphrase once for that run. This is not a Bitwarden integration. |
| External credential syntax, including 1Password CLI and systemd credentials | **1.9.10** | Available in 2.1.8, but neither 1Password CLI access nor systemd credentials should be assumed on a work device or systemd 249. |

For the home Linux target, the approved runtime source is GNOME Keyring via
`secret-tool`, not `systemd-creds`; the handoff records systemd 249 and no
`systemd-creds` on that machine. Borg's FAQ says `secret-tool` needs the active
unlocked D-Bus/login-keyring session. The handoff also records `Linger=no`, so
the systemd user timer runs only during a login session; the timer and
passphrase lookup need a real logged-in-session test in BK2. For **personal
macOS only**, Borg's FAQ documents macOS Keychain via
`security find-generic-password`. Borg's install guide says recent macOS needs
Full Disk Access for any protected paths in the allowlist; running as root does
not bypass that permission. The work Mac does not install Borg or use this path.

**Exit 75 is not proved to protect both create and prune.** borgmatic 2.1.8's
source defines 75 as `SOFT_FAIL_EXIT_CODE` and logs “skipping remaining
repository actions.” But its current `commands` hook context manager catches a
soft failure in `Before_after_hooks.__enter__()` and returns normally; Python
then enters the wrapped action body. The outer repository loop only skips
remaining actions if that exception reaches it. This is source evidence of a
control-flow concern, not a runtime test of the deprecated `before_backup`
hook. The current docs mark `before_backup` deprecated in favor of `commands`.
Treat the handoff's “exit 75 skips create and prune” statement as **suspect**:
BK2 must prove both no archive creation and no prune with the intended hook on
the pinned version before relying on it. Do not replace the approved guard
requirement silently.

## Key organization and recovery

The initial personal allowlist is `~/.local/state/machine/`; only reviewed
personal machine configuration paths belong there. Home `machine.yaml` and
`private.yaml` are candidates. Work `work.yaml` goes only to work 1Password.
Machine-written discovery/sync records are rebuilt, and customer data is never
captured. Do not broaden this to “home minus exclusions.”

In Bitwarden, use the **personal vault**, not a shared Organization collection:
Bitwarden documents Secure Notes for freeform secrets and Folders for personal
organization, while Collections transfer items to organization ownership and
sharing. Create one recovery note for each repository with its Borg repository
ID/location and `borg key export` output; keep each passphrase in a separately
named Secure Note in `Backups/Borg`. A fresh machine needs the Borg encryption
key and passphrase, plus SSH access to the host. Follow BorgBase's one-key-per-
machine guidance: after a lost machine, either recover host-account access and
register a new SSH key or prove a separately held recovery-key path. Do not
confuse the SSH private key with Borg's exported encryption key.

Bitwarden says its offline two-step recovery code requires the account email and
master password; using it deactivates existing two-step methods and generates a
new recovery code. The author must confirm the master password is independently
available, then save a replacement offline after any recovery. If BorgBase is
selected, host-account 2FA/account recovery is an additional part of “host
access”; this research did not create or inspect an account.

The work 1Password service-account policy cannot be established from public
sources. **Question for the author/work owner:** does the work organization
approve a 1Password service account for automated, save-on-change configuration
updates, and to which approved vault? Until answered, BK4 must treat the work
1Password save as the approved path, use no Borg on that Mac, and keep any
service-account automation unapproved.

## Owner, cadence and retention choices

The approved owner is the backup topic. Live machine-file retention remains
until that machine is decommissioned. The personal backup repository owns only
the allowlisted configuration artifacts described above.

| Option | Cadence and stale alert | Bounded history | Reason |
|---|---|---|---|
| **Recommended start** | Every 8 hours; warn when last success is older than 12 hours. | 14 daily, 8 weekly, 12 monthly; always retain the newest archive. | Fits the handoff's 12-hour warning discipline and leaves a small margin for one missed run. |
| Lower activity | Daily; choose a warning threshold longer than the normal interval (for example, 36 hours). | 7 daily, 4 weekly, 6 monthly; newest remains. | Fewer runs, with about six months of named recovery history. |
| Longer history | Every 8 hours; 12-hour alert. | 30 daily, 12 weekly, 24 monthly; newest remains. | More time to recover a slowly noticed configuration regression, with more retained metadata/storage. |

These are policy options, not storage estimates. The local repository can apply
retention as part of its maintenance run. The append-only host cannot reclaim
pruned data using the backup key: use a **separate all-access maintenance key**
for deliberate prune/compact, after a check. With separate local/remote
passphrases and different actions, use separate borgmatic configuration files
or invocations: `encryption_passcommand` is global to a run and, since 1.9.9,
is executed once per invocation. The author still needs to choose the provider,
cadence, retention profile, whether repo passphrases are shared, and how
provider-account recovery works.

## Remaining proofs in BK2–BK4

- **BK2 — home Linux:** in a sandbox, remove or empty a required source and
  prove the next run creates no archive **and prunes nothing**; prove the guard
  fails when deliberately broken; prove a restore returns the files; prove
  allowlisted files are included and a planted customer-data path is excluded;
  exercise fresh/stale warning directions, actual user-timer + `secret-tool`
  behavior, and the monthly extract check. The code/source note above makes
  create **and** prune behavior the first proof to run.
- **BK3 — chosen host:** create an independent host repository; verify the
  ordinary SSH key is append-only and cannot permanently remove old data; use
  a separate all-access key for prune/compact; keep the Borg key export and
  passphrase in Bitwarden; restore from an empty HOME using only Bitwarden plus
  host-account access; then initialize a new repository for future writes.
- **BK4 — work Mac, on that machine:** store only its machine files in work
  1Password; prove save-on-change, stale-copy warning and a restore drill; prove
  no Borg is installed or run. If a service account is not approved, retain a
  manual 1Password workflow.

## Public sources checked 2026-09-23

- **Project scope and topic rules:** [PRD configuration-backup rule](../../PRD.md#configuration-backups), [TOPICS](../TOPICS.md), [TOPIC-RECIPES](../TOPIC-RECIPES.md).
- **Borg:** [1.4.5 installation](https://borgbackup.readthedocs.io/en/1.4.5/installation.html), [1.4.5 FAQ](https://borgbackup.readthedocs.io/en/1.4.5/faq.html), [append-only mode](https://borgbackup.readthedocs.io/en/1.4.5/usage/notes.html#append-only-mode-forbid-compaction), [serve](https://borgbackup.readthedocs.io/en/1.4.5/usage/serve.html), [key export](https://borgbackup.readthedocs.io/en/1.4.5/usage/key.html#borg-key-export), [1.4.5 signed release/assets](https://github.com/borgbackup/borg/releases/tag/1.4.5), [release asset SHA-256 data](https://api.github.com/repos/borgbackup/borg/releases/tags/1.4.5), [2.0.0b23 warning](https://github.com/borgbackup/borg/releases/tag/2.0.0b23).
- **borgmatic:** [releases (2.1.8)](https://projects.torsion.org/borgmatic-collective/borgmatic/releases), [install](https://torsion.org/borgmatic/how-to/install-borgmatic/), [passwords/version thresholds](https://torsion.org/borgmatic/how-to/provide-your-passwords/), [config bootstrap](https://torsion.org/borgmatic/reference/command-line/actions/config-bootstrap/), [1.7.15 changelog entry for bootstrap](https://raw.githubusercontent.com/borgmatic-collective/borgmatic/1.8.0/NEWS), [2.1.8 hook source](https://github.com/borgmatic-collective/borgmatic/blob/2.1.8/borgmatic/hooks/command.py), [2.1.8 action loop source](https://github.com/borgmatic-collective/borgmatic/blob/2.1.8/borgmatic/commands/borgmatic.py), [repository config behavior](https://torsion.org/borgmatic/reference/configuration/repositories/).
- **Providers:** [BorgBase pricing/features](https://www.borgbase.com/), [BorgBase docs/free tier](https://docs.borgbase.com/), [BorgBase append-only FAQ](https://docs.borgbase.com/faq/#append-only-mode), [BorgBase pricing details](https://docs.borgbase.com/pricing/), [BorgBase SSH keys](https://docs.borgbase.com/faq/ssh/), [rsync.net Borg pricing/features](https://www.rsync.net/products/borg.html), [rsync.net standard pricing](https://www.rsync.net/pricing.html), [Hetzner SSH/Borg/append-only docs](https://docs.hetzner.com/storage/storage-box/access/access-ssh-rsync-borg/), [Hetzner BX11 terms/capacity](https://www.hetzner.com/storage/storage-box/bx11/).
- **Install backends:** [mise GitHub backend](https://mise.jdx.dev/dev-tools/backends/github.html), [Homebrew Borg 1.4.5](https://formulae.brew.sh/formula/borgbackup), [Homebrew borgmatic 2.1.8](https://formulae.brew.sh/formula/borgmatic), [Homebrew pin command](https://docs.brew.sh/Manpage), [community.general.homebrew 13.0.1 source](https://github.com/ansible-collections/community.general/blob/13.0.1/plugins/modules/homebrew.py), [Borg 1.4.5 PyPI artifacts](https://pypi.org/pypi/borgbackup/1.4.5/json).
- **Galaxy roles:** [BorgBase role v2.0.0 and upstream files](https://github.com/borgbase/ansible-role-borgbackup/releases/tag/v2.0.0), [BorgBase CI/Molecule workflow](https://github.com/borgbase/ansible-role-borgbackup/blob/master/.github/workflows/main.yml), [BorgBase tasks tree](https://github.com/borgbase/ansible-role-borgbackup/tree/master/tasks), [Kliwniloc role v2.0.0/release](https://github.com/kliwniloc/ansible-role-borgbackup/commit/1680fd27ef032ea3f693b9e8fe4307e63aa31e2a), [Kliwniloc role README](https://github.com/kliwniloc/ansible-role-borgbackup), [Kliwniloc teardown task](https://github.com/kliwniloc/ansible-role-borgbackup/blob/master/tasks/absent.yml), [Kliwniloc Molecule CI workflow](https://github.com/kliwniloc/ansible-role-borgbackup/blob/master/.github/workflows/molecule.yml), [Kliwniloc role tests](https://github.com/kliwniloc/ansible-role-borgbackup/tree/master/molecule).
- **Bitwarden:** [Secure Notes/items](https://bitwarden.com/help/managing-items/), [Folders vs Collections](https://bitwarden.com/help/folders/), [two-step recovery code](https://bitwarden.com/help/two-step-recovery-code/).

The sources above establish public capabilities and advertised terms. No target
Linux package candidate, personal-Mac OS version, provider quote beyond the
published list prices, employer 1Password policy, account state, or runtime
behavior was checked.
