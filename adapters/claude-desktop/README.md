# Claude Desktop

Preview:

```bash
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install claude-desktop
```

Apply after review:

```bash
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install claude-desktop --apply
```

This safely merges `mcpServers.cyber-junshi` into the platform-specific Claude Desktop JSON
configuration, retaining other keys and backing up an existing file. Restart Claude Desktop
after installation.
