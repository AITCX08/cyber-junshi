# Hermes

Preview:

```bash
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install hermes
```

Apply after review:

```bash
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install hermes --apply
```

This safely merges `mcp_servers.cyber_junshi` into `~/.hermes/config.yaml`, preserving unrelated
keys and backing up an existing file. Reload MCP servers in Hermes after installation.
