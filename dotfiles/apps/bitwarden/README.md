# bitwarden

Marker topic for the [Bitwarden CLI](https://bitwarden.com/help/cli/) (`bw`)
on personal machines. The actual `bw` binary is installed and upgraded by the
[mise](../mise) topic via `apps/mise/files/config.toml`:

```toml
"bitwarden" = "latest"
```

This topic exists so other topics can declare a dependency on the **concept**
"bitwarden" and so the parent playbook's sanity check can verify `bw` is on
PATH before topics that need it try to fetch secrets.

## Cross-platform

`topic_os` includes both `Darwin` and `Debian`. The CLI name is `bw` on every
platform.

## Verification

```bash
./run-role.sh bitwarden
```

This fails loudly with a clear next-step message if `bw` is not on PATH.

## Tests

```bash
mise exec -- ansible-playbook apps/bitwarden/tests/topic-metadata.yaml
```
