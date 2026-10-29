# roles/secrets-session/README.md

Shared helper role for obtaining unlocked password-manager sessions at
provision time. It does **not** store secrets on disk; it only produces
in-memory Ansible facts that downstream tasks can use for lookups.

## Usage

A topic that needs a vault session should import the relevant task file:

```yaml
- name: "Obtain Bitwarden session"
  ansible.builtin.include_role:
    name: roles/secrets-session
    tasks_from: bitwarden.yaml
  vars:
    secrets_session_bitwarden_keychain_service: "com.bitwarden.cli"
  when:
    - mytopic_secrets_source == 'bitwarden'
    - secrets_bitwarden_session is not defined
```

After the include, `secrets_bitwarden_session` holds a usable `BW_SESSION`
string, or the play fails if none could be obtained.

For 1Password:

```yaml
- name: "Obtain 1Password session"
  ansible.builtin.include_role:
    name: roles/secrets-session
    tasks_from: onepassword.yaml
  when:
    - mytopic_secrets_source == '1password'
    - secrets_onepassword_session is not defined
```

## Supported unlock sources

### Bitwarden

1. Existing `BW_SESSION` in the Ansible process environment (shell already
   unlocked).
2. `BW_SESSION` exported in `~/.localrc`.
3. macOS Keychain entry for the configured service/account.
4. Interactive prompt for the master password (`ansible.builtin.pause`).

### 1Password

1. `OP_SERVICE_ACCOUNT_TOKEN` environment variable.
2. Already-signed-in account via the desktop app / biometric integration.
3. Interactive prompt for the master password.

## Security notes

- Session facts are **not** written to disk. They live only in Ansible's
  in-memory fact cache for the current play.
- Tasks that touch sessions and passwords are marked `no_log: true`.
- The helper role intentionally stores nothing in the repo; credentials live
  in the OS-provided stores (Keychain, service-account tokens) or are typed
  interactively.
