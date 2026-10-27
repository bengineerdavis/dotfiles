**Added**

- `roles/guards/no-root-authority.yaml` refuses a run that would install a
  user-scoped tool as root. A whole play started through sudo cannot be
  corrected by `become: false`: that means "do not elevate", not "refuse to run
  as root". `apps/mise` calls it with `always`, and the tests prove it fires for
  root and relents for a normal user.
- `dot_functions` gains a `sudo` wrapper that refuses `mise`, `ansible` and
  `ansible-playbook` while passing every other command through. `command sudo`
  still bypasses it on purpose.
- The global opencode permissions, and the repo project config, deny `sudo`
  for agents.

**Changed**

- The mise commands carry explicit `become: false`, so a play-level `become`
  cannot elevate them even if the guard is bypassed.

**Known issues**

- `sudo -i` opens a root shell, and neither the wrapper nor Ansible can inspect
  what runs inside it. That is deliberate root work rather than an accidental
  `sudo mise`.
