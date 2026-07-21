# Security Policy

## Supported version

Security fixes target the latest release and the current `main` branch.

## Report a vulnerability

Use GitHub's private vulnerability reporting for this repository. Do not open a public issue for
a suspected vulnerability, secret exposure, or privacy leak. Include the affected version,
reproduction steps, impact, and a minimal synthetic proof of concept.

Do not include real conversations, access tokens, personal identifiers, or private database files
in a report. Replace them with fictional values.

## Security boundary

Cyber Junshi reads only arguments supplied through its MCP tools. It does not capture chats,
decrypt messaging databases, access accounts, or upload decisions. `record_outcome` is the only
public data-writing tool and stores data in the configured local SQLite file.

Adapter installation is preview-only by default. `--apply` is required; existing file-based
configurations receive a timestamped backup and unrelated keys are retained.
