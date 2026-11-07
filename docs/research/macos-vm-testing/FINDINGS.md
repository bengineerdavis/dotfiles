# macOS VM for local testing — findings

**Written 2026-11-07.** The question: how can we run a macOS VM locally for
testing config changes, from a Linux x86_64 host? Every claim below cites its
primary source. The short answer is a constraint, not a setup guide.

## Conclusion

**There is no legal way to run a macOS VM from this Linux x86_64 box.** macOS
is licensed only for Apple-branded hardware, and macOS VMs are supported only
on Apple silicon (or, historically, on Apple-badged Intel Macs). The "free"
path via Apple's beta programs is a *software* program, not a virtualization
license — it still runs on real Apple hardware, and the public-facing one
(AppleSeed for IT) is gated to enterprise/education organizations behind an
Apple Business/School Manager administrator.

The realistic local-testing paths are, in order of fit:

1. **A dedicated Mac** (Mac mini, Apple silicon) running the VZ.framework /
   Tart / UTM to host disposable macOS guests. This is the only first-class
   "local macOS VM" option and requires Apple hardware.
2. **CI macOS runners** (GitHub Actions `macos-*` labels) — Apple hardware
   in the cloud; the repo already runs tests on non-local hardware (the
   `tests.yml` workflow), so a macOS leg there is the natural extension.
3. **AppleSeed for IT / Apple Beta** — beta *software* on real Apple hardware,
   with a feedback requirement; not a path to a VM from this box.

## What the license actually says

- The current macOS SLA is headed **"For use on Apple-branded Systems"** and
  licenses the OS for use on Apple hardware. Source: Apple legal, "SOFTWARE
  LICENSE AGREEMENT FOR macOS Tahoe 26" — https://www.apple.com/legal/sla/docs/macOSTahoe.pdf
  (the "For use on Apple-branded Systems" heading; the single-copy terms apply
  to the OS "preinstalled on Apple-branded hardware"). The same heading guards
  every recent release (macOS 27, Tahoe 26, Sequoia 15).
- Apple's virtualization documentation scopes macOS guests to Apple silicon:
  "Running macOS in a virtual machine on Apple silicon" — Apple Developer,
  https://developer.apple.com/documentation/virtualization/running-macos-in-a-virtual-machine-on-apple-silicon
  (the sample project installs and runs macOS VMs "on Apple silicon").
- The guest-VM count is also bounded on Apple silicon (two macOS guests at
  once), documented by the open-source community against the EULA:
  https://khronokernel.com/macos/2023/08/08/AS-VM.html — "Apple Silicon hosts
  can only have a maximum of 2 macOS guest VMs active at once"; the limit "is
  written into the macOS EULA" (Hacker News thread on that article).

## The tools — all Apple-hardware-hosted

| Tool | Host requirement | Source |
|---|---|---|
| Apple Virtualization framework (VZ) | Apple silicon | https://developer.apple.com/documentation/virtualization |
| Tart (Cirrus Labs) | Apple silicon | https://github.com/cirruslabs/tart |
| UTM | Apple-only ("UTM was created for macOS and only for Apple platforms") | https://getutm.app/ |
| Anka | Apple silicon | https://veertu.com/ |

None of these run on non-Apple x86_64 hardware. macOS-on-x86 via OpenCore/QEMU
("hackintosh") is unlicensed — the macOS SLA's "Apple-branded Systems" term
covers it — and is explicitly **not** a path to take. Source for the general
point: https://www.apple.com/legal/sla/docs/macOSTahoe.pdf (scope-of-license
term); community confirmation that "a license restriction was that VMs, MacOS
must run on Apple Hardware (hackintosh's violates the EULA)":
https://the.fmsoup.org/t/apple-silicon-macos-vm-software/3025.

## The "free" testing path — what it actually is

Apple's beta programs provide **beta macOS software**, not a license to
virtualize off Apple hardware, and the feedback requirement is real:

- **AppleSeed for IT** is "specifically designed for enterprise and education
  customers committed to testing each new version of Apple beta software." An
  administrator in **Apple School Manager or Apple Business Manager** must
  "accept the terms and conditions on behalf of their organization for the
  current beta period." Feedback is submitted directly to Apple via a
  dedicated process. Source: Apple Platform Deployment,
  https://support.apple.com/guide/deployment/test-software-updates-appleseed-beta-program-depe8583cf10/web
  (Overview + Program participation sections).
- **Apple Public Beta Software Program** — the individual-facing analog, with
  its own agreement; feedback via Feedback Assistant.

Both programs gate *software* (on a real Apple device), and neither changes
the host-hardware requirement. Signing up does not make a Linux x86_64 box
able to run macOS legally.

## What to do instead for this repo

The Darwin leg of the topic-VM work is already documented as open in
`docs/research/topic-vm-tests/PLAN.md` ("no macOS Vagrant boxes exist"; the
Darwin leg needs "a different mechanism"). The concrete next steps, in order
of effort:

1. **CI macOS runner** — add a `macos-latest` (Apple silicon) job to
   `.github/workflows/tests.yml` that renders the chezmoi config with
   `chezmoi.os = darwin` and asserts the header. This is Apple hardware, so it
   is the legitimate spot for the darwin render check. It reuses the exact
   render the existing `test_opencode_config_layers.py` already performs
   host-side under overridden `chezmoi.os`.
2. **A Mac mini (or any Apple-silicon Mac) on the desk** — the only way to run
   a *local* macOS VM (Tart/VZ/UTM). Deciding to buy one is an author call;
   nothing here blocks it but nothing here substitutes for it either.

The short version for the current work: **the darwin leg cannot be
VM-tested from this box; the header change is os-independent, and the darwin
render is already proven by `chezmoi execute-template` under
`chezmoi.os=darwin` in the test suite (PR #134).** A CI macOS runner would be
the legitimate first site for a real darwin-machine render check.