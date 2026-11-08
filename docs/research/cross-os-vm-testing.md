# Testing macOS and Debian from one Linux workstation

**Written 2026-11-08.** Research for the dotfiles repo
(`github.com/bengineerdavis/dotfiles`): how to verify that Ansible topic roles
converge on **both** target operating systems, when the only development
workstation is Linux (Pop!_OS, amd64, KVM available).

**Confidence labels used throughout:**

- **(a) Verified** — read from a primary source this session. URL or file path given.
- **(b) Secondary** — reported by someone else, not first-party.
- **(c) Inference** — my reasoning from verified facts. Not a claim about the world.

---

## The short answer

**There is no supported, licensed way to run a macOS guest on a Linux host.**

Every Apple-supported mechanism for virtualising macOS requires a macOS host,
because they all sit on Apple's `Virtualization.framework`, which Apple ships
only for macOS. The one project that does boot macOS on Linux (`OSX-KVM`) is a
Hackintosh: its own README refuses to give a legal opinion and tells you to
consult a lawyer.

So the macOS half of the test matrix has exactly three honest options, and none
of them involve a macOS VM on the Linux box:

1. **Run the playbook directly on a macOS GitHub Actions runner.** Free, because
   this repo is public. One primary-source precedent does exactly this and is
   the closest thing to a house standard in the Ansible macOS world.
2. **Run it on the real Mac** over SSH (Molecule's delegated driver, or plain
   `ansible-playbook`).
3. **Run a macOS guest on the Mac**, via Lima `vmType: vz` or Tart — the repo
   already has a Lima adapter, and only the `vmType` and `os` fields change.

Separately, a whole class of the bugs this repo actually has — path and data
layout, not OS behaviour — **can** be tested entirely on Linux. That is a
different question from "test macOS", and conflating the two is the main trap
this document exists to prevent.

---

## 1. What actually runs a macOS guest?

### 1.1 Apple `Virtualization.framework` (a) VERIFIED

Source: `https://developer.apple.com/tutorials/data/documentation/virtualization.json`
(the docs JSON API; the HTML page is JavaScript-driven and returns empty).

> "The Virtualization framework provides high-level APIs for creating and
> managing virtual machines (VM) on Apple silicon and Intel-based Mac
> computers. Use this framework to boot and run macOS or Linux-based operating
> systems in custom environments that you define."

Platform availability: `{"introducedAt":"11.0","name":"macOS"}` — **macOS only**,
introduced at macOS 11.0.

**Conclusion:** this is a macOS host API. It cannot host anything on Linux. Every
Apple-native macOS virtualisation tool below is a thin layer over it, and so
inherits the same host requirement.

### 1.2 Tart (Cirrus Labs) — Apple Silicon host only (a) VERIFIED

Source: cloned `tart/README.md` (repo now redirects `cirruslabs/tart` →
`openai/tart`).

> "*Tart* is a virtualization toolset to build, run and manage macOS and Linux
> virtual machines (VMs) on Apple Silicon. … Tart uses Apple's own
> `Virtualization.Framework` for near-native performance."

> "Try running a Tart VM on your Apple Silicon device running macOS 13.0
> (Ventura) or later (will download a 25 GB image)"

**Runs on a Linux host: no.** The requirement is an Apple Silicon *device*
running macOS 13.0+. Tart's own docs confirm the split — only the *orchestration
controller* runs on Linux (`tart/docs/orchard/deploying-controller.md`:
"Compared to Worker, which can only be deployed on a macOS machine, Controller
can be also deployed on Linux"), and the Worker is the part that runs VMs.

**Licensing (a) VERIFIED** from `https://tart.run/licensing/` and `tart/LICENSE`:
Fair Source (Functional Source License 1.1, ALv2 future license). Free tier is
100 CPU cores; Gold $12,000/yr (500 cores); Platinum $36,000/yr (3,000 cores);
Diamond $12/core/yr. **Usage on personal workstations is royalty-free** — so this
repo would be inside the free tier by a wide margin.

**Nested virtualisation (a) VERIFIED**, `tart/docs/faq.md`:

> "`Virtualization.Framework` supports nested virtualization only on M3 or M4
> chips running macOS 15 (Sequoia) or later and [only for Linux VMs] … By
> default, it is disabled, but can be enabled by passing the `--nested` flag to
> `tart run`."

So you can never nest a macOS guest inside a macOS guest on any chip.

**Headless trap (a) VERIFIED**, `tart/docs/faq.md` — matters for CI:

> "Starting from macOS 15 (Sequoia), there's an undocumented requirement from
> Virtualization.Framework … to have an unlocked `login.keychain` available at
> the times when running a VM."

Without it: `SecKeyCreateRandomKey_ios failed`, `Failed to generate keypair`,
`Interaction is not allowed with the Security Server`. Workarounds documented
are a GUI login (not available on a headless runner) or
`security create-keychain -p '' login.keychain` +
`security unlock-keychain -p '' login.keychain`. **This is the single most likely
reason a Tart-based CI job fails mysteriously.**

### 1.3 Vetu (Cirrus Labs) — Linux host, but Linux guests only (a) VERIFIED

Source: cloned `vetu/README.md`.

> "vetu is virtualization toolset to effortlessly run Cloud Hypervisor-backed
> virtual machines on Linux hosts."

> "Try running a Vetu VM on your Linux machine with `arm64` processor"

The README and `INSTALL.md` contain **no** occurrence of "macOS" or "darwin".
Vetu is Tart's Linux-host sibling and shares its OCI image distribution — but it
runs Linux guests. **It does not solve the macOS-guest problem.**

### 1.4 UTM — macOS/iOS host only (a) VERIFIED

Source: `https://docs.getutm.app/`.

> "UTM is a full featured system emulator and virtual machine host for iOS and
> macOS. It is based off of QEMU."

From `https://docs.getutm.app/guest-support/macos/`:

> "**macOS 12+** — macOS guests are supported on Apple Silicon hosts running
> macOS 12 or higher."

**Runs on a Linux host: no.** The host list is macOS and iOS only.

### 1.5 Anka (Veertu) — macOS host only (a) VERIFIED

Source: `https://docs.veertu.com/anka/anka-virtualization-cli/getting-started/installing-the-anka-virtualization-package/`.

The documented install is a **universal PKG for macOS**, and the host support
matrix lists only macOS versions:

| macOS host | Intel Anka 3.x | Apple/ARM Anka 3.x |
|---|---|---|
| macOS 12.x | 🛑 | 🛑 |
| macOS 13.x | ✅ | ✅ |
| macOS 14.x | ✅ | ✅ |
| macOS 15.x | ✅ | ✅ |
| macOS 26.x | ✅ | ✅ |

`https://docs.veertu.com/anka/what-is-anka/`: "Anka Virtualization package can be
installed onto macOS hosts that match our host support matrix." The Build Cloud
*Controller & Registry* can run on Linux/Docker — but that is the scheduler, not
the hypervisor.

**Anka Develop (a) VERIFIED**, `https://docs.veertu.com/anka/anka-develop/` — the
free tier is narrower than "free":

> "Anka Develop is currently restricted to running a single VM at a time. It also
> does not include VM suspension, tagging, or use of the registry CLI commands.
> Finally, it will only function on Macbook, Macbook Pro, and Macbook Air
> hardware."

So if the Mac in this fleet is a Mac mini or Studio, Anka Develop does not apply;
you would be buying a Build Cloud licence.

### 1.6 VirtualBox — macOS guests only on macOS hosts (a) VERIFIED

Source: `https://www.virtualbox.org/manual/ch14.html` § 14.1 Experimental Features:

> "Mac OS X guests (**macOS hosts only**)"

Listed under *experimental*, "provided on an 'as-is' basis and are not formally
supported." Related known issues (§ 14.2): "Oracle VM VirtualBox does not provide
Guest Additions for Mac OS X at this time"; "Mac OS X guests only work with one
CPU assigned to the VM."

**Runs on a Linux host: no** — and even on a macOS host it is experimental,
single-CPU, and has no Guest Additions. Rejected.

### 1.7 Vagrant providers (a) VERIFIED, partly (c) INFERENCE

`vmware_desktop`: HashiCorp documents the provider's configuration
(`https://developer.hashicorp.com/vagrant/docs/providers/vmware/configuration`)
and the box format
(`https://developer.hashicorp.com/vagrant/docs/providers/vmware/boxes`), including
`nvram`, `vmsd`, `vmx`, `vmxf`, `vmdk` as the required files and
`vmware-vdiskmanager` for shrinking — a tool that ships inside
`/Applications/VMware Fusion.app`. The provider needs the local hypervisor and the
Vagrant VMware Utility service on the same machine.

*Inference (c):* because both the VMware Utility and Fusion are macOS/desktop
installs, `vmware_desktop` cannot drive a Mac's hypervisor from a Linux host.
Vagrant's remote-execution story is SSH provisioning into an existing VM, not
off-box hypervisor control.

`parallels`: Mac-host only. **Unverified this session** — I did not fetch the
Parallels provider docs, and I am not asserting details.

**Vagrant's real value here is not macOS guests.** It is the ability to boot a
Linux guest a different way, which this repo does not need (Lima already works).

### 1.8 OSX-KVM (kholia) — the only Linux-host option, and it is a Hackintosh (a) VERIFIED

Source: cloned `osx-kvm/README.md`.

Requirements (verbatim):

> "* A modern Linux distribution. E.g. Ubuntu 24.04 LTS 64-bit or later.
> * QEMU >= 8.2.2
> * A CPU with Intel VT-x / AMD SVM support is required (`grep -e vmx -e svm /proc/cpuinfo`)
> * A CPU with SSE4.1 support is required for >= macOS Sierra
> * A CPU with AVX2 support is required for >= macOS Ventura"

The README's own § *Is This Legal?*:

> "The 'secret' Apple OSK string is widely available on the Internet. … I am not a
> lawyer but it seems that Apple's attempt(s) to get the OSK string treated as a
> trade secret did not work out. …
> Note: It is your responsibility to understand, and accept (or not accept) the
> Apple EULA.
> Note: This is not legal advice, so please make the proper assessments yourself
> and discuss with your lawyers if any of your concerns (Text credit: Dortania)"

Also relevant: the project's own framing is "Virtual Hackintosh". Status is
best-effort community work — the README solicits PRs for documentation and calls
the OpenCV-automated installer a "(Not so) crazy idea".

**This is technically viable on this exact host** — `uname -m` is `x86_64`, the
CPU is an AMD Ryzen 9 5950X with SVM present (`grep -c -e vmx -e svm /proc/cpuinfo`
→ 32), and `/dev/kvm` exists (`crw-rw----+ 1 root kvm`). Verified this session.

**But it is almost certainly outside Apple's licence.** See § 1.9.

### 1.9 Apple's licensing position (a) VERIFIED

Source: downloaded `https://www.apple.com/legal/sla/docs/macOSSequoia.pdf` and
extracted with `pdftotext` (the fetch tool rejects `application/pdf`). Text is
`macos_sla.txt` locally; § 2B.

**§ 2B(i)** grants the personal, non-commercial licence:

> "to download, install, use and run for personal, non-commercial use, one (1)
> copy of the Apple Software directly on **each Apple-branded computer** running
> macOS Sonoma, macOS Ventura, … ("Mac Computer") that you own or control"

**§ 2B(iii)** — this is the virtualisation clause, quoted in full:

> "(iii) to install, use and run **up to two (2) additional copies or instances**
> of the Apple Software, or any prior macOS or OS X operating system software or
> subsequent release of the Apple Software, **within virtual operating system
> environments on each Apple-branded computer you own or control that is already
> running the Apple Software**, for purposes of: (a) software development;
> (b) testing during software development; (c) using macOS Server; or (d)
> personal, non-commercial use."

**What that grants:** up to **two** macOS VM instances per Apple-branded computer,
and explicitly for **development and testing during software development**. This
repo's use case is squarely inside the permitted purposes.

**What that does not grant:** running macOS on non-Apple hardware. The permission
is conditioned on the machine being "Apple-branded" and "already running the
Apple Software." A Linux desktop is neither. § 2B(iii) also adds that the grant
"does not permit you to use the virtualized copies or instances of the Apple
Software in connection with service bureau, time-sharing, terminal sharing, relay
service or other similar types of services."

**Conclusion, stated plainly:** a macOS guest on the Linux box is not licensed by
Apple's standard SLA, and Apple ships no virtualisation support for Linux. Any
OSX-KVM setup here is an unsupported Hackintosh. That is a legitimate finding,
not a gap in the research.

### 1.10 Hypervisor summary

| Mechanism | Runs a macOS guest? | Host required | Source |
|---|---|---|---|
| `Virtualization.framework` | yes | macOS 11.0+, Apple silicon or Intel Mac | (a) Apple docs JSON |
| Tart | yes | Apple Silicon device, macOS 13.0+ | (a) `tart/README.md` |
| Anka | yes | macOS 13.x+ (Intel or ARM) | (a) Veertu host matrix |
| UTM | yes | Apple Silicon Mac, macOS 12+ | (a) `docs.getutm.app` |
| Lima (`vmType: vz`) | yes, experimental | macOS host, ARM, ≥ guest OS | (a) `lima-vm.io/docs/usage/guests/macos/` |
| VirtualBox | yes, experimental | macOS host | (a) VirtualBox manual ch14 |
| Vagrant `vmware_desktop` / `parallels` | yes | macOS host w/ Fusion or Parallels | (a)/(c) |
| **Vetu** | **no — Linux guests only** | Linux arm64 | (a) `vetu/README.md` |
| **OSX-KVM** | **yes, unsupported** | **Linux x86_64 + KVM** | (a) `osx-kvm/README.md` |

---

## 2. What Ansible/Molecule practitioners actually do

### 2.1 Molecule has no macOS support at all (a) VERIFIED

Source: cloned `ansible/molecule` and `ansible-community/molecule-plugins`.

Core drivers present in `molecule/src/molecule/driver/`:
`base.py`, `delegated.py`, `__init__.py`. **That is the whole directory** — there
is no macOS or darwin driver.

`grep -rn -il "macos\|darwin" molecule/docs molecule/src` returns **nothing**.
The only mention anywhere in molecule-plugins is an unrelated Docker note
(`molecule_plugins/docker/driver.py:147`): "On some systems (macOS) you might
have to set `cgroupns_mode` to…".

`molecule-plugins/README.md` lists all supported plugins:

> "- azure - containers - docker - ec2 - gce - openstack - podman - vagrant"

No macOS entry.

Molecule's own CI (`molecule/.github/workflows/tox.yml`) delegates to
`ansible/team-devtools/.github/workflows/tox.yml@main` with a Linux matrix
(`default_python: "3.11"`, `min_python: "3.11"`, `max_python: "3.13"`). No macOS
runner appears.

**So Molecule cannot be the thing that tests macOS.** What Molecule *can* do is
drive a macOS target over SSH, because its default driver is `delegated`. From
`molecule/docs/configuration.md` § Driver, the instance-config API the create
playbook must produce:

```yaml
- address: ssh_endpoint
  identity_file: ssh_identity_file # mutually exclusive with password
  instance: instance_name
  port: ssh_port_as_string
  user: ssh_user
  shell_type: sh
  password: ssh_password
  become_method: valid_ansible_become_method # optional
  become_pass: password_if_required # optional
```

`molecule/src/molecule/driver/delegated.py:296` confirms `("shell_type", None)` is
one of the mappable instance params, so `shell_type: sh` reaches Ansible as
`ansible_shell_type`.

**This matters for this repo:** `home/dotfiles/apps/lima/molecule/shared/create.yml`
already produces exactly this structure —

```yaml
- instance: ...
  address: 127.0.0.1
  user: molecule
  port: <sshLocalPort>
  identity_file: <lima_home>/_config/user
```

— which means a `darwin-lima` scenario is a **change of backend, not a change of
harness.** (c)

### 2.2 `ansible-test --remote` does have a macOS target (a) VERIFIED

Source: `https://raw.githubusercontent.com/ansible/ansible/devel/test/lib/ansible_test/_data/completion/remote.txt`

```
macos/26.3 python=3.14 python_dir=/usr/local/bin become=sudo provider=mac arch=aarch64 alias=macos/26,macos/latest
macos python_dir=/usr/local/bin become=sudo provider=mac arch=aarch64
```

That is the **only** macOS entry, and it is **arm64-only**.

The docs (`https://docs.ansible.com/ansible-core/devel/dev_guide/testing_running_locally.html`)
say of `--remote`:

> "The `--remote` option runs tests in a cloud hosted ephemeral virtual machine.
> An API key is required to use this feature, unless running under an approved
> Azure Pipelines organization."

**Two caveats that make this a poor fit here:**

1. It requires an API key and a paid cloud relationship. *(c) inference: this is
   Red Hat's own test infrastructure, not a free service for arbitrary playbooks.*
2. `ansible-test integration` is designed for **collection** integration tests.
   This repo has topic roles and a chezmoi payload, not a collection. (a) — the
   docs' setup section is entirely about `/ansible_collections/{namespace}/{name}`.

Verdict: real capability, wrong shape for this repo. Reject for now.

### 2.3 pytest-testinfra on macOS: works, with one gap (a) VERIFIED

Source: cloned `pytest-dev/pytest-testinfra`.

Backends (`https://testinfra.readthedocs.io/en/latest/backends.html`): local,
paramiko, docker, podman, ssh, salt, ansible, kubectl, openshift, winrm, lxc.
All the remote ones are SSH-based, so **any POSIX target works, macOS included.**

Platform dispatch found in source:

- `testinfra/testinfra/modules/file.py:216` — `if host.system_info.type == "darwin": return DarwinFile`
  (`class DarwinFile(BSDFile)` at `file.py:309`).
- `testinfra/testinfra/modules/systeminfo.py:39` — `elif sysinfo["type"] == "darwin": _get_darwin_sysinfo()` (defined at `:105`).
- `testinfra/testinfra/modules/package.py` — **no darwin branch.** `get_module_class`
  dispatches on windows / freebsd / openbsd / netbsd / debian / rpm-family /
  arch, then falls back to `host.exists("dpkg-query")`, `host.exists("rpm")`,
  `host.exists("brew")` → `HomebrewPackage`.

**The `brew` fallback is a live false-positive risk on this repo's Linux box** —
`brew` exists here (`/home/linuxbrew/.linuxbrew/bin/brew`, Homebrew 7.0.11), so a
`host.package(...)` assertion written for macOS would silently resolve to
`HomebrewPackage` on Linux too. It would pass, and it would not be testing macOS.
That is the same shape as the repo's own "a test that can pass while testing
nothing" concern.

### 2.4 `geerlingguy/mac-dev-playbook` — the strongest precedent (a) VERIFIED

Source: cloned `geerlingguy/mac-dev-playbook`, file
`.github/workflows/ci.yml`. This is a real macOS provisioning playbook, used widely,
and its testing strategy is **run it on a real macOS GitHub runner, twice.**

```yaml
  integration:
    name: Integration
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os:
          - macos-15
          - macos-14
    steps:
      - name: Uninstall GitHub Actions' built-in Homebrew.
        run: tests/uninstall-homebrew.sh
      - name: Uninstall GitHub Actions' built-in browser installs.
        run: |
          sudo rm -rf /Applications/Firefox.app
          sudo rm -rf /Applications/Google\ Chrome.app
          sudo rm -rf /usr/local/bin/firefox
      - name: Install test dependencies.
        run: |
          sudo pip3 install --upgrade pip
          sudo pip3 install ansible
      - name: Set up the test environment.
        run: |
          cp tests/ansible.cfg ./ansible.cfg
          cp tests/inventory ./inventory
          cp tests/config.yml ./config.yml
          ansible-galaxy install -r requirements.yml
      - name: Test the playbook's syntax.
        run: ansible-playbook main.yml --syntax-check
      - name: Test the playbook.
        run: ansible-playbook main.yml
        env:
          ANSIBLE_FORCE_COLOR: '1'
      - name: Idempotence check.
        run: |
          idempotence=$(mktemp)
          ansible-playbook main.yml | tee -a ${idempotence}
          tail ${idempotence} | grep -q 'changed=0.*failed=0' && (echo 'Idempotence test: pass' && exit 0) || (echo 'Idempotence test: fail' && exit 1)
        env:
          ANSIBLE_FORCE_COLOR: '1'
```

Four things to copy from this, verbatim:

1. **`ansible-playbook --syntax-check` first.** Catches template and YAML errors
   without spending a full run.
2. **Deliberately break the runner's preinstalled state** before testing
   (`tests/uninstall-homebrew.sh`, `rm -rf` the browsers). Otherwise the playbook
   "passes" because macOS runners ship Homebrew and Chrome preinstalled — the
   install task never runs.
3. **Idempotence = run twice and grep for `changed=0.*failed=0`.**
4. **No Molecule, no VM.** One file, two runner versions.

The README (a) confirms the intent:

> "This project is continuously tested on GitHub Actions' macOS infrastructure."
> "You can also run macOS itself inside a VM, for at least some of the required
> testing (App Store apps and some proprietary software might not install
> properly). I currently recommend: UTM, Tart"

Note the author recommends UTM and Tart for *local* VM testing — both Mac-host
tools. The CI path is the runner, not a VM.

### 2.5 `geerlingguy/ansible-role-homebrew` — same pattern (a) VERIFIED

Source: cloned `geerlingguy/ansible-role-homebrew`, `.github/workflows/ci.yml`.
`integration` job, `matrix.os: [macos-10.15]`, identical step shape: uninstall
built-in Homebrew → `ansible-playbook tests/test.yml --syntax-check` → run →
grep `changed=0.*failed=0`. No Molecule.

(The `macos-10.15` label is stale — GitHub retired those images years ago. The
*pattern* is what to copy, not the runner label.)

### 2.6 `geerlingguy/dotfiles` and `mathiasbynens/dotfiles` — no CI at all (a) VERIFIED

- `geerlingguy/dotfiles`: `.github/` contains **only** `FUNDING.yml`. No workflows.
  Its README: "I use macOS, so I can only guarantee they'll work on a Mac."
- `mathiasbynens/dotfiles`: **no `.github` directory at all.** Top level is
  `.aliases`, `.bashrc`, `bin`, `bootstrap.sh`, `brew.sh`, `.macos`, `.osx`, etc.

**That is a real data point, honestly reported: two of the best-known dotfiles
repos verify nothing automatically.** This repo is already ahead of both. It also
means "what do dotfiles repos do" has no strong answer to copy — the Ansible
*role* repos are the better source.

### 2.7 `brew bundle` as a verification primitive (a) VERIFIED

Source: `https://docs.brew.sh/Brew-Bundle-and-Brewfile`.

The one command that makes a declarative macOS package check cheap:

> "You can check if a `brew bundle install` will do anything by running:
> `$ brew bundle check` — The Brewfile's dependencies are satisfied.
> You can use this behaviour in scripts like so: `brew bundle check || brew bundle install`"

Also useful for this repo: Brewfiles are evaluated as Ruby, so per-OS entries work
natively —

```ruby
brew "gnupg" if OS.mac?
brew "glibc" if OS.linux?
```

— and `brew bundle exec` / `brew bundle env` solve PATH problems:
`brew bundle env | grep node` → `export PATH="/opt/homebrew/opt/node/bin:${PATH:-}"`.

**Caveat (a):** "`brew bundle` does not and will not have a concept of a
'Brewfile lock file' that can be used to pin versions like e.g.
`package-lock.json` or `Gemfile.lock`." Homebrew is a rolling release. A
`brew bundle check` therefore verifies *presence*, never *version*. Do not build a
version-conformance test on it.

---

## 3. GitHub Actions macOS runners as the practical answer

### 3.1 What the runners actually are (a) VERIFIED

Source: `https://docs.github.com/en/actions/reference/runners/github-hosted-runners`

| Runner label | Arch | CPU | RAM | Storage |
|---|---|---|---|---|
| `macos-latest`, `macos-26`, `macos-15`, `xcode-27` | **arm64** | 3 (M1) | 7 GB | 14 GB |
| `macos-15-intel`, `macos-26-intel` | x86_64 | 4 | 14 GB | 14 GB |

GitHub's own image README
(`images/macos/macos-26-arm64-Readme.md`) pins the exact contents: **macOS 26.6.2
(25G83), Darwin kernel 25.6.0**, with **Homebrew 7.0.11**, Python 3.15.1,
Node 24.22.1, Clang/LLVM 21.0.0, Ruby 3.4.12 preinstalled.

**`macos-latest` is arm64.** That matches this fleet's Apple Silicon Mac, so an
arm64 runner is a better model of the real target than an Intel runner would be.

### 3.2 Can they run system-level provisioning? (a) VERIFIED — yes

HashiCorp and geerlingguy both rely on it: the macOS runner grants **passwordless
sudo**, which `mac-dev-playbook`'s `sudo rm -rf /Applications/...` and
`sudo pip3 install` steps depend on. The runner is a full VM with a real
filesystem, not a container — which is precisely why nothing can nest inside it:

> "While nested virtualization is technically possible while using runners, it is
> **not officially supported**. Any use of nested VMs is experimental and done at
> your own risk, we offer no guarantees regarding stability, performance, or
> compatibility."

Source: `https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners`.

**The consequence, and it is the pivotal architectural fact in this document:**
you cannot boot a macOS guest *inside* a macOS runner. So "use CI to run a macOS
VM" is a dead end. But you do not need one — **the runner already is macOS arm64.**
Run the playbook on it directly.

### 3.3 Limits and cost (a) VERIFIED

Source: `https://docs.github.com/en/billing/concepts/product-billing/github-actions`
and `https://docs.github.com/en/actions/reference/limits`.

Billing is **monetary, not minute-based** (older docs used a 10× minute
multiplier for macOS; the current page defines an included dollar amount):

- macOS standard runner: **$0.062/minute** (3-core, `actions_macos`).
- macOS larger runner `macos_l` (12-core): $0.077/min; `macos_xl` (5-core M2 Pro): $0.102/min.
- Minutes round **up** to the whole minute.

**Free for public repositories.** GitHub's billing docs state standard runners are
free for public repos (larger runners are not — they bill even on public repos).
This repo **is public** — verified via `gh repo view --json visibility` → `PUBLIC`.
So a macOS job here costs **$0**, within the concurrency caps.

Concurrency and storage limits that actually bind:

| Plan | Total concurrent jobs | Concurrent **macOS** jobs | Included storage | Included compute |
|---|---|---|---|---|
| Free | 20 | **5** | 500 MB artifacts / 10 GB cache | $12 |
| Pro | 40 | 5 | 1 GB | $18 |
| Team | 60 | 5 | 2 GB | $18 |
| Enterprise Cloud | 500 | 50 | 50 GB | $300 |

Other hard limits worth knowing:

- **Job execution limit: 6 hours.** Fine here; a provisioning run is minutes.
- A queued workflow is **discarded if no runner picks it up within 45 minutes**;
  a triggered run is discarded if not queued within 30 minutes.
- `macos-14` images were **deprecated July 2026 and unsupported by November 2**
  (runner-images issue #13518). Do not pin `macos-14`.

### 3.4 What a macOS runner does NOT give you (a) VERIFIED / (c) INFERENCE

- **No nested VM** (§ 3.2), so no Lima/Tart guest inside CI.
- **No persistent machine.** A Tart image pulled on one run is gone the next.
  Every job re-pays the uncacheable setup. (c)
- **Runner images change weekly.** Anything the playbook depends on being
  *absent* (the `uninstall-homebrew.sh` premise) can silently appear or vanish
  between runs, turning an idempotence test red for reasons unrelated to this
  repo. (c — this is why mac-dev-playbook pins `macos-15`/`macos-14` explicitly
  rather than `macos-latest`, and why pinning matters.)
- **No GUI.** Anything that needs a logged-in WindowServer session cannot be
  tested. That includes everything Tart's `login.keychain` FAQ is about.

---

## 4. The "simulate the layout, not the OS" pattern

This is the section most likely to be *acted on first*, because it addresses a
bug class this repo demonstrably has, and it needs no Mac and no VM.

### 4.1 The distinction, stated precisely

Two different questions get conflated:

| Question | What it needs | Can Linux answer it? |
|---|---|---|
| "Does this role converge on macOS?" | macOS kernel, launchd, Homebrew casks, `/Applications` | **No.** Needs real macOS. |
| "Does this committed file resolve on machine B's layout?" | machine B's directory tree and identity values | **Yes.** The OS is irrelevant. |

The second is a **path-and-data** problem. `~/.config/repos.yaml` hardcoding
`~/code/projects/personal/...` when the other machine has `~/code/personal/...`
is not an OS bug — it is a fact about a directory tree. A Linux process can stand
in a directory tree of any shape.

The repo has exactly this bug, tracked: **DOT-306**, "Adopt a per-machine repo
catalogue so one committed list serves both layouts." Its own measurements:

> "main's `config/repos.yaml` resolves 44/44 paths on the un-migrated Linux box;
> PR #92's re-pointed catalogue resolves 3/49 (authored on the migrated Mac).
> Neither version works on both machines."

That is a layout bug that a Linux fixture home would have caught, and a macOS VM
would have caught more slowly and less directly.

### 4.2 Precedent 1: chezmoi's own test suite fakes `$HOME` (a) VERIFIED

Source: cloned `twpayne/chezmoi`, `internal/cmd/main_test.go`.

`testscript.Run` is registered with a custom `chhome` command (`main_test.go:194`)
that creates a directory and then sets **five** environment variables:

```
HOME
CHEZMOICACHEDIR      <home>/.cache/chezmoi
CHEZMOICONFIGDIR     <home>/.config/chezmoi
CHEZMOISOURCEDIR     <home>/.local/share/chezmoi
USERPROFILE          (only when runtime.GOOS == "windows")
```

Test cases then assert on the *rendered result* in that fake home. Representative
case: `internal/cmd/testdata/scripts/unmanaged.txtar` — `mkhomedir`, `mksourcedir`,
`exec chezmoi unmanaged`, `cmp stdout golden/unmanaged`.

Upstream chezmoi ships dozens of these, run on Linux, macOS and Windows, and they
are the project's primary correctness mechanism. **A fake home is not a hack — it
is how the tool's own authors test the tool.**

### 4.3 Precedent 2: this repo already does it (a) VERIFIED

`tests/chezmoi/test_ansible_owned_paths.py` runs chezmoi against a disposable
destination:

```python
def unmanaged_in(disposable_home, *paths: str) -> set[str]:
    target = disposable_home / "home"
    ...
    result = subprocess.run(
        ["chezmoi", "-S", PAYLOAD_ROOT, "-D", target, "unmanaged"],
        capture_output=True, text=True, timeout=60, check=False,
    )
```

`-S`/`--source` and `-D`/`--destination` are both documented flags
(`https://www.chezmoi.io/reference/command-line-flags/global/`). The test's
non-vacuity guard is instructive and should be copied:

```python
assert UNDECLARED in found, "the ignore rules are too broad for this check to prove anything"
assert DECLARED not in found
```

The decoy proves the mechanism can still find things. Without it, an over-broad
`.chezmoiignore` would make the test pass while asserting nothing.

### 4.4 What I verified empirically on this Linux host (a) VERIFIED

Two probes, run this session on `chezmoi v2.72.2`, Linux amd64:

**Probe 1 — can a Linux host render the macOS template branch?**

```bash
$ chezmoi -S s -D d apply --override-data '{"chezmoi":{"os":"darwin"}}'
$ cat d/.testfile
DARWIN-BRANCH
```

**Yes.** `--override-data` with a *nested* `chezmoi.os` key overrides
`.chezmoi.os`. A top-level `{"os": "darwin"}` does **not** — it sets `.os`
(a user data key) while `.chezmoi.os` stays `linux`. The equivalent config-file
form also works:

```toml
[data.chezmoi]
os = "darwin"
```

`--exclude scripts` composes with this, which matters: without it, `run_` scripts
would execute on the Linux host even though the target is nominally Darwin.
**Rendering without `--exclude scripts` is actively dangerous.**

**Probe 2 — can Ansible select the Darwin branch on Linux?**

```bash
$ ansible-playbook pb.yml -e '{"ansible_facts":{"os_family":"Darwin"}}'
# with gather_facts: false → "DARWIN BRANCH SELECTED", ok=1, failed=0
```

**Yes**, with `gather_facts: false` plus injected facts.

**But the limit is immediate and hard** — same probe extended to a real
Darwin-only module:

```bash
$ ansible-playbook darwin_role.yml -e '{"ansible_facts":{"os_family":"Darwin"}}'
# community.general.homebrew_cask → FAILED (even in --check mode)
```

`homebrew_cask` and `launchd` fail on Linux regardless of injected facts, because
the *module* probes the real system, not `ansible_facts`. `.chezmoi.osRelease`,
`.chezmoi.kernel` and similar are also not fakeable this way.

**So the honest boundary is:**

- **What works on Linux:** template rendering, branch reachability, variable and
  path resolution, syntax and lint, chezmoi target-state computation.
- **What does not:** module execution, package operations, service management,
  anything that reads the real kernel.

That boundary is exactly right for the DOT-306 class of bug, and useless for
"does `homebrew_cask` install Chrome."

---

## 5. What existing repos in this space actually do

| Repo | Verifies macOS? | How | CI config path |
|---|---|---|---|
| `ansible/molecule` | no | Linux-only tox matrix; no macOS target anywhere | `.github/workflows/tox.yml` |
| `geerlingguy/mac-dev-playbook` | **yes** | `ansible-playbook` on `macos-15` + `macos-14`, run twice, grep `changed=0.*failed=0` | `.github/workflows/ci.yml` |
| `geerlingguy/ansible-role-homebrew` | **yes** | same shape, `macos-10.15` | `.github/workflows/ci.yml` |
| `geerlingguy/dotfiles` | no | no workflows at all | `.github/FUNDING.yml` only |
| `mathiasbynens/dotfiles` | no | no `.github` directory | — |
| `twpayne/chezmoi` | yes, in effect | `testscript` with a fake `$HOME` on all three OSes | `internal/cmd/main_test.go:194` |
| `pytest-dev/pytest-testinfra` | partial | SSH backends; `DarwinFile`, darwin sysinfo | `testinfra/modules/file.py:216` |

**The pattern across all of them:** nobody tests macOS with a VM in CI. The two
projects that do verify macOS behaviour either run on a real macOS runner
(geerlingguy) or do not touch macOS-specific modules at all and instead test
rendering against a fake home (chezmoi).

### 5.1 What is missing / unverified

Stated plainly, as required:

- **VMware Fusion macOS guest support on Apple Silicon** — I fetched Fusion Pro 13
  docs but did not find a definitive statement on macOS guests on Apple Silicon
  hosts. **Unverified.**
- **Vagrant Parallels provider details** — not fetched. **Unverified.**
- **The `provider=mac` ansible-test backend's actual cloud** (AWS EC2 Mac vs
  Azure) — `remote.txt` proves the target exists and its arch; it does not name
  the backend. **Unverified.**
- **Whether a `darwin-lima` scenario would work end-to-end** — I verified the
  requirements (macOS host, ARM, Lima ≥ 2.1, `vmType: vz`) and that this repo's
  `create.yml` already emits the delegated-driver instance shape, but I did not
  run it on a Mac. **Unverified — it has never been executed.**
- **`osx-ansible` / `macos-ansible` community patterns** — I did not locate a
  first-party project by those names that would be worth citing. **Not found**, so
  not cited, rather than cited from memory.

---

## 6. What this means for this repo

### 6.1 The finding, up front

**There is no legal, supported way to run a macOS guest on the Linux workstation.**
Not Tart, not UTM, not Anka, not VirtualBox, not Vetu, not Virtualization.framework.
OSX-KVM works technically and is a Hackintosh outside Apple's SLA. Every path that
tests real macOS requires the Mac, or a macOS GitHub runner.

That is not a blocker, because the two testing problems this repo actually has are
separable.

### 6.2 Ranked options

**Option 1 — Test layout on Linux, today. (RECOMMENDED FIRST)**

Extend the existing fixture-home pattern in `tests/chezmoi/` to seed the *other
machine's* directory tree, and assert the committed config resolves in both.
`-S`/`-D` already do the rendering; only the fixture contents are new.

- **Cost:** hours. No new dependency, no VM, no runner minutes. Runs in the
  existing suite.
- **Maintenance:** near zero — it is a fixture directory and a few assertions.
- **Covers:** DOT-306's entire bug class. Proves a committed `repos.yaml` resolves
  44/44 on *both* layouts, which today nothing proves.
- **Does not cover:** anything macOS-specific.
- **Guard to copy:** the `UNDECLARED` decoy from
  `tests/chezmoi/test_ansible_owned_paths.py`, so the check cannot pass vacuously.

**Option 2 — A macOS job in GitHub Actions. (RECOMMENDED SECOND)**

Add `macos-latest` to `.github/workflows/tests.yml` as a separate job, modelled
directly on `mac-dev-playbook/.github/workflows/ci.yml`: uninstall the
preinstalled Homebrew, `ansible-playbook --syntax-check`, run, re-run and grep
`changed=0.*failed=0`.

- **Cost:** under a day. The repo is public, so **$0** in minutes. 5 concurrent
  macOS jobs is ample.
- **Maintenance:** low but non-zero. Runner images change weekly; pin
  `macos-15` rather than `macos-latest`, and expect the occasional red run caused
  by an image change rather than by this repo.
- **Covers:** real macOS convergence for whatever topics fit a 6-hour job —
  Homebrew casks, launchd agents, `/Applications` state.
- **Does not cover:** GUI-session behaviour, anything needing a persistent VM.

**Option 3 — Molecule against the real Mac over SSH, on demand. (OPTIONAL THIRD)**

The `delegated` driver needs only `address`/`user`/`port`/`identity_file`, which
`create.yml` already emits for Lima. A `darwin` scenario pointing at the Mac is a
small backend change. Add `shell_type: sh`.

- **Cost:** a day, plus a disposable user and home on the Mac, plus deciding how
  the Mac is reachable and how it is reset between runs.
- **Maintenance:** medium. It mutates a real machine, so it needs a teardown story
  the repo does not have yet, and it cannot run in CI where the Mac is not.
- **Covers:** the same ground as Option 2, but with Molecule's `idempotence` action
  and full scenario lifecycle, and without runner-image drift.
- **Why not first:** it needs author-run access to the Mac and a reset policy.
  Option 2 gives most of the value with none of that.

**Option 4 — Lima `vmType: vz` macOS guest *on the Mac*. (LATER, IF EVER)**

The repo's Lima adapter already exists; the scenario differs only in `vmType: vz`
and `os: Darwin`, and Lima's macOS guest docs give the requirements (macOS host,
ARM, Lima ≥ 2.1).

- **Cost:** significant. Plus the Setup Assistant suppression
  (`osOpts.Darwin.suppressFirstLoginSetup`), no automatic port forwarding
  (`ssh -L` or vzNAT), and no serial boot logs under `vz`.
- **Maintenance:** highest of the four. Experimental upstream; two macOS VMs max
  per host under the SLA.
- **Only justified if** Options 2 and 3 prove insufficient — e.g. needing a
  reproducible *clean* macOS that survives more than one run.

### 6.3 What I would reject, and why

| Rejected | Reason |
|---|---|
| **OSX-KVM on the Linux box** | Outside Apple's SLA (§ 1.9: guests permitted only on Apple-branded hardware). Unsupported Hackintosh. The repo's own trust ladder and "verification must be evidence" standard would be undermined by a test environment that is itself unsanctioned. |
| **Tart / UTM / Anka as a Linux-hosted VM** | They do not run on Linux at all (§§ 1.2, 1.4, 1.5). This is not a preference — it is a category error. |
| **Vetu for the macOS half** | Linux host, Linux guests only (§ 1.3). Solves a problem this repo does not have. |
| **VirtualBox for macOS guests** | Experimental, single-CPU, no Guest Additions, macOS hosts only (§ 1.6). Worse than Tart on every axis. |
| **`ansible-test --remote` (macOS provider)** | Correct capability, wrong shape: it tests *collections* at `/ansible_collections/{ns}/{name}`, and needs an API key. This repo has topic roles, not a collection (§ 2.2). |
| **Molecule as the macOS test mechanism** | Molecule has no macOS driver and no macOS mention in its source or docs (§ 2.1). Using it to *drive* a macOS target over SSH is legitimate (Option 3); expecting it to *provide* a macOS machine is not. |
| **`brew bundle check` as a version-conformance test** | It verifies presence only; Homebrew explicitly will not ship a lockfile (§ 2.7). Use it to assert "these packages are installed", never "at these versions". |
| **Faking `ansible_facts['os_family']` and calling it macOS testing** | Verified to work for branch selection and to fail immediately on real modules (`homebrew_cask`, `launchd` fail on Linux even in check mode, § 4.4). Useful for rendering checks; a false comfort if reported as convergence. |

### 6.4 One caution about a plausible-looking shortcut

`host.package(...)` in pytest-testinfra resolves to `HomebrewPackage` whenever
`brew` is on `PATH` — and `brew` **is** on this Linux box. A macOS package
assertion therefore passes here while proving nothing about macOS (§ 2.3). If
macOS assertions are added, they must be gated on
`host.system_info.type == "darwin"` explicitly, not left to the backend's
fallback chain.

---

## 7. Summary of what was and was not verified

**Verified from primary sources this session (a):**

- Apple `Virtualization.framework` is macOS-host-only, macOS 11.0+.
- Tart: Apple Silicon host, macOS 13.0+; nested virt is Linux-guests-on-M3/M4 only;
  Sequoia's undocumented `login.keychain` requirement; Fair Source, free ≤ 100 cores.
- Vetu: Linux host, Linux guests only; no macOS mention.
- UTM: macOS/iOS host; macOS guests need Apple Silicon, macOS 12+.
- Anka: macOS 13.x+ host only; Anka Develop limited to laptops and one VM.
- VirtualBox: macOS guests supported only on macOS hosts, experimental, 1 CPU.
- OSX-KVM: Linux x86_64 + KVM, requires VT-x/SVM, own "Is This Legal?" section
  defers to the Apple EULA.
- Apple SLA § 2B(i)/(iii): up to **two** macOS VM instances per Apple-branded
  computer, for development and testing during development.
- Molecule: no macOS driver, no macOS mention in source or docs; `delegated`
  driver instance-config API and `shell_type`.
- `ansible-test`: exactly one macOS remote target (`macos/26.3`, arm64), API key required.
- pytest-testinfra: SSH backends, `DarwinFile`, darwin sysinfo, `brew` fallback in `package.py`.
- GitHub Actions: `macos-latest` = arm64 macOS 26, 3-core/7 GB; passwordless sudo;
  nested virt unsupported; $0.062/min; free for public repos; 5 concurrent macOS jobs.
- `mac-dev-playbook` and `ansible-role-homebrew` CI: real `ansible-playbook` runs
  plus `changed=0.*failed=0` idempotence on macOS runners.
- `geerlingguy/dotfiles` and `mathiasbynens/dotfiles`: no CI.
- chezmoi: `-S`/`-D` flags; `chhome` fake-home harness; and — empirically on this
  host — `--override-data '{"chezmoi":{"os":"darwin"}}'` renders the Darwin branch.
- Ansible: injected `os_family` facts select the Darwin branch; real Darwin modules
  still fail on Linux.

**Not verified (stated rather than asserted):**

- VMware Fusion macOS guests on Apple Silicon; Vagrant Parallels provider details;
  the cloud behind `provider=mac`; a `darwin-lima` scenario run end-to-end; any
  `osx-ansible` / `macos-ansible` community project worth citing.

**The one-line conclusion:** test the layout on Linux, test convergence on a macOS
runner, and do not spend effort trying to boot macOS on the Linux box — there is
no supported way to do it, and the repo's real bug class does not need it.
