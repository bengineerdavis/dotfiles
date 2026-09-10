# chrome

Google Chrome, the extension set this workstation should have, and a CLI that
manages the manifest and reports where reality has drifted from it.

```bash
ansible-playbook apps/chrome/playbook.yaml               # provision
ansible-playbook apps/chrome/playbook.yaml --tags upgrade  # refresh git sources
ansible-playbook apps/chrome/playbook.yaml --tags remove

browser-ext status                       # manifest vs reality
browser-ext drift --strict               # exit 1 on unclaimed extensions
browser-ext add store <id-or-url>        # append a marketplace entry
browser-ext add git <repo-url>           # append a git entry (pins latest tag)
browser-ext sync                         # clone/checkout/build without Ansible
```

The manifest is [`defaults/main.yaml`](defaults/main.yaml). Everything follows
from it.

## The manifest schema

Every extension is one entry in `chrome_extensions`, discriminated by `source`:

| `source` | Comes from | How it is installed |
|---|---|---|
| `store` | Chrome Web Store | Seeded via an External Extensions JSON; Chrome installs it at next launch |
| `git`   | A git repository | Cloned to a fixed path, built, then loaded by hand once |

The schema is deliberately browser-agnostic — `source`, `name`, `why` and the
git fields mean the same thing for any browser, and only the mechanism that
consumes them is Chrome-specific. A firefox or edge topic can reuse it verbatim
with its own installer tasks. The same idea for editors is written up in
[`TODO-ide-extensions.md`](TODO-ide-extensions.md), deferred rather than
forgotten.

## What this topic can and cannot do

Chrome is deliberately hostile to programmatic extension management, and three
of its defences shape every decision here. Each has already been tried.

**1. `--load-extension` is gone.** Chrome 137 removed the flag from *branded*
builds — it was too useful for sideloading malware. It still works in Chromium
and Chrome for Testing, neither of which is what you browse with. This machine
runs Chrome 152, so there is no command-line route to loading an extension.

**2. macOS refuses off-store external installs.** The External Extensions
mechanism can seed an extension from a JSON file, but "as of Chrome 44, no
external installs are allowed from a path to a local CRX file on Mac OS". On
macOS the `external_update_url` must point at the Web Store. This is precisely
why `source: git` exists as a separate path rather than a variation of seeding.

**3. `Secure Preferences` is HMAC-signed.** Extension state — enabled, disabled,
granted permissions — lives under per-entry MACs plus a `super_mac` over the
whole block, so that software other than Chrome cannot edit it. Copying that
file between machines does not migrate your extensions; it produces a profile
Chrome resets on next launch. This is why the CLI only ever reports.

The one lever that would force an install is `ExtensionInstallForcelist`,
mandatory-level policy. This machine is enrolled in Chrome Browser Cloud
Management (`CloudManagementEnrollmentMandatory = 1` in
`/Library/Managed Preferences/com.google.Chrome.plist`), so that belongs to
the org's IT admin console. A local `defaults write` lands as merely
*recommended* and is outranked anyway. Not a gap here — not ours to set.

## `source: store` — seeding

`install.yaml` writes one `<extension-id>.json` per store entry into

```
~/Library/Application Support/Google/Chrome/External Extensions/
```

Chrome reads that directory at launch and installs each from the store. No admin
rights, nothing under `/Library`, and — unlike a forcelist — you stay free to
disable or remove any of them afterwards. Expect a one-time "new extension
added" prompt, and note seeds apply to the Chrome *user*, so they are offered
across all profiles rather than just the work one.

Deleting an entry prunes its seed on the next run. It does **not** uninstall an
already-installed extension; Chrome treats it as yours from that point on, and
the teardown says so rather than leaving you to find out.

## `source: git` — clone, build, load once

For extensions that are not in the marketplace. Fintastic is the working
example, and it demonstrates why this path needs a build step: a bare clone is
**not** loadable. `scripts/build.mjs` (esbuild) bundles `@sentry/browser` into
`src/telemetry.js` and writes the loadable extension to `dist/`, which is
gitignored. Its GitHub releases are source-only tags with no attached assets, so
there is no prebuilt zip to fetch — building is the only route.

`install.yaml` clones to `{{ chrome_unpacked_root }}/<slug>`, runs `build`, and
Chrome loads `<slug>/<load_subdir>`. The build is skipped when the checkout did
not move and the load directory already has a `manifest.json`, so re-runs do not
pay for npm.

**Why the path is the whole game.** Chrome derives an unpacked extension's ID by
hashing its absolute load path. Loading `fintastic-1.0.1`, then `1.1.1`, then
`1.1.2` from three different folders does not upgrade anything — it registers
three unrelated extensions with three IDs, all claiming the same content-script
matches. That already happened here; two of those IDs now point at deleted
`~/Downloads` folders and show as error cards. Cloning to one fixed path per
slug and updating in place ends it: the path never changes, so the ID never
changes, and a version bump replaces the extension rather than forking a new one.

**Refs are pinned, not tracked.** `ref` is required and `--tags upgrade`
re-checks-out whatever the manifest names rather than pulling latest. For an
extension running content scripts on a page full of customer data, moving
versions should be an edit you make, not a side effect of provisioning. Bump the
tag, re-run, then reload once in `chrome://extensions` — Chrome does not watch
the filesystem, so a rebuilt `dist/` is invisible to a running browser until
told.

The initial "Load unpacked" is still one manual click, once. Nothing can
automate it; see constraint 1 above.

## The audit CLI

`files/browser-ext` is a uv single-file script, symlinked to `~/bin` by
`install.yaml`, mirroring how `apps/ollama` ships `ollama-models`.

`drift` distinguishes three cases, which is why it is useful rather than noisy:

- **it-owned / built-in** — silently excluded. Endpoint Verification and the
  Okta plugin come from the admin console; competing with them would create
  double-install state.
- **review** — listed every run. An unresolved decision (two password managers,
  two link-copiers, a coupon extension on the profile that views customer data)
  is a standing question, not a settled exclusion.
- **unclaimed** — real drift. `--strict` exits 1 here, for a loop or CI.

Chrome's own bundled components (Web Store, PDF Viewer, Hangouts, Gemini, the
TTS engine) sit in the same `extensions.settings` block as real extensions and
would otherwise flood the report. They are filtered on `from_webstore`, which is
false for the furniture and true for anything a person installed — location
alone does not separate them, because components and seeded extensions both land
on location 5.

`add` edits the manifest as text rather than round-tripping it through a YAML
dumper, because this file is more comment than data and every comment explains a
constraint someone paid to discover.

## Teardown

`--tags remove` deletes the seed JSONs and the CLI symlink, and removes the
External Extensions directory only if this topic left nothing else in it.

Two things are guarded off by default:

- **The browser.** `chrome_remove_browser: false` — Chrome came from Google's
  installer, is updated by Keystone under MDM, and carries the cloud-management
  enrollment. `install.yaml` is symmetric: the Homebrew cask runs only when
  Chrome is genuinely absent, so a fresh machine gets a browser and this one
  keeps its single updater.
- **Git clones.** `chrome_remove_git_clones: false` — a clone is a working tree
  that may hold uncommitted work. Deleting one during a teardown is not a
  surprise anyone should get.
