# Codex

Preview:

```bash
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install codex
```

Apply after review:

```bash
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install codex --apply
```

This safely merges `[mcp_servers.cyber_junshi]` into `~/.codex/config.toml`, preserving existing
TOML and backing up the file. Restart the Codex client or inspect its MCP server settings after
installation.
