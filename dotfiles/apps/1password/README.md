# 1password

Marker topic for the [1Password CLI](https://developer.1password.com/docs/cli/) (`op`)
on Debian-family work machines. The actual `op` binary is installed and
upgraded by the [mise](../mise) topic via `apps/mise/files/config.toml`:

```toml
"1password-cli" = "latest"
```

This topic exists so other topics can declare a dependency on the **concept**
"1password" and so the parent playbook's sanity check can verify `op` is on
PATH before topics that need it try to fetch secrets.

## Verification

```bash
./run-role.sh 1password
```

This fails loudly with a clear next-step message if `op` is not on PATH.

To use 1Password as the secrets source for another topic, pass
`-e debget_secrets_manager=1password` (example: deb-get).

## Tests

```bash
mise exec -- ansible-playbook apps/1password/tests/topic-metadata.yaml
```
