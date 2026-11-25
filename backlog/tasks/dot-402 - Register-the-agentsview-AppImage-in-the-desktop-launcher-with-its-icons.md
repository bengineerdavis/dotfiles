---
id: DOT-402
title: Register the agentsview AppImage in the desktop launcher, with its icons
status: To Do
created_date: 2026-11-25 03:27
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
On Linux the agentsview desktop app installs as
`~/Applications/AgentsView.AppImage` and runs by path, but never appears in
the desktop application launcher: no `.desktop` file sits in any XDG
applications directory, and no icons are registered under `hicolor`.
Measured 2026-11-24 on the Debian box — `~/.local/share/applications/` has
other applications but no agentsview entry, and
`~/.local/share/icons/hicolor/*/apps/` has no `agentsview-desktop.png`.

Ship:

- A `.desktop` template in `apps/agentsview`, rendering an **absolute**
  `Exec=` to the installed AppImage, category `Utility`, and
  `MimeType=x-scheme-handler/agentsview` carried but **not registered**.
- Icon extraction from the already-checksum-verified AppImage into
  `~/.local/share/icons/hicolor/{32x32,128x128,256x256}/apps/`, replacing
  any previously extracted set rather than accumulating it.
- `update-desktop-database` after install and after remove, so the launcher
  cache reflects the change without a logout.
- Teardown in `remove.yaml` for the `.desktop`, the three icons, and the
  cache refresh.
- Tests asserting: the rendered file passes `desktop-file-validate`; its
  `Exec=` is absolute (a relative one is spec-valid but broken in practice,
  which is the defect the bundled file ships with); the MIME declaration
  survives; the files land with the right mode; a second install run leaves
  exactly one copy of each; and teardown removes exactly what install
  created while leaving `~/.agentsview` untouched.

Constraints:

- Ansible owns the whole desktop surface — the `.desktop` is only meaningful
  alongside the AppImage Ansible installed, and splitting it into chezmoi
  would let a launcher be deployed pointing at a file that is not there.
- Extract icons from the AppImage the topic already verified by SHA256. No
  second download and no unverified input.
- Respect `agentsview_install_desktop_appimage=false`: no entry, no icons.
- Do not register the `agentsview://` handler — no `xdg-mime default`, no
  `mimeapps.list` write.
- `~/.agentsview` stays untouched by both directions, as in the parent topic.
- Tests skip with a named reason when `desktop-file-validate` or the AppImage
  is absent; they never pass silently.
- Visual appearance in a running desktop session is not assertable in CI and
  must be reported as unverified, not implied.

Agreed with the author 2026-11-24: launcher entry only, not a GNOME Shell
search provider or KRunner plugin — surfacing session content from shell
search is bespoke code and belongs upstream. Also agreed: delivered as a
follow-up PR, because the parent topic's Linux acceptance bar was settled as
webserver plus CLI service.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The topic installs a `.desktop` file whose `Exec=` is an absolute path to the installed AppImage, whose `Categories` includes `Utility`, and whose `MimeType` carries `x-scheme-handler/agentsview`
- [ ] #2 `desktop-file-validate` exits 0 against the rendered `.desktop` file, asserted by a test
- [ ] #3 A test asserts the rendered `Exec=` is absolute, separately from `desktop-file-validate`, so the bundled file's relative-`Exec` defect cannot reappear
- [ ] #4 Icons are extracted from the checksum-verified AppImage into `~/.local/share/icons/hicolor/` at 32x32, 128x128 and 256x256, with mode 0644
- [ ] #5 Re-running install replaces the extracted icon set instead of accumulating files, asserted by a test that runs install twice and counts the results
- [ ] #6 `update-desktop-database` runs after install and after remove
- [ ] #7 `remove.yaml` deletes the `.desktop`, the three extracted icons, and re-runs `update-desktop-database`
- [ ] #8 With `-e agentsview_install_desktop_appimage=false`, no `.desktop` and no icons are created
- [ ] #9 `~/.agentsview` still exists after running the topic's `remove`
- [ ] #10 Tests skip with a named reason when `desktop-file-validate` or the AppImage is absent, and never silently pass
- [ ] #11 The README records that visual appearance in a live desktop session is unverified, and why
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Measured 2026-11-24 on the Debian box, all from the installed artifacts:

- The AppImage's bundled `.desktop` contains `Exec=agentsview-desktop`
  (relative — unresolvable outside the AppImage), `Categories=` empty, and
  `MimeType=x-scheme-handler/agentsview`.
- The AppImage ships `agentsview-desktop.png` at 32×32, 128×128 and 256×256
  under `usr/share/icons/hicolor/`.
- `~/Applications/AgentsView.AppImage` exists at 142 MB. The topic's
  `get_url` re-downloads only when the checksum differs, so extraction can
  depend on that task having run.
- `desktop-file-validate`, `update-desktop-database` and
  `gtk-update-icon-cache` are present on the box. AppImage extraction uses
  the AppImage's own `--appimage-extract` (verified working, no FUSE
  needed), so `unsquashfs` is not a dependency.
- The CLI has no `install-desktop` subcommand — nothing upstream does this
  for us.
- An empty `Categories` leaves the entry in no app-grid section, which is
  why the template sets `Utility` rather than copying the bundled file.

A version bump re-extracts icons, so install must clear any previously
extracted set before writing the new one — otherwise a rename upstream
leaves stale files behind, which AC #5 pins.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
