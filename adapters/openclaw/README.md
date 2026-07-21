# OpenClaw

Preview the official CLI command:

```bash
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install openclaw
```

Apply after review:

```bash
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install openclaw --apply
```

Apply invokes `openclaw mcp add` with an argument list and no shell. Run
`openclaw mcp doctor cyber-junshi --probe` afterward to verify the stdio connection.
