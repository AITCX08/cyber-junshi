# Cyber Junshi / 赛博军师

[中文说明](README.md)

> Your personal Agent does not need more tactics. It needs better judgment.

Cyber Junshi is an agent-native, local-first decision-support core. It gives MCP-compatible
personal Agents a small, explainable framework for safety routing, fact layering, option costs,
and stop conditions. The host Agent handles language and context; Cyber Junshi validates the
decision structure and can persist explicitly approved outcomes to local SQLite.

This is decision support, not mental-health diagnosis, emergency response, legal advice, or a
guarantee of outcomes.

## Four mechanisms

| Mechanism | Question it answers |
| --- | --- |
| Safety routing | Is this a normal, elevated-risk, or emergency situation? |
| Fact layering | What is observed, inferred, and still unknown? |
| Option costs | What are the gains, long-term costs, reversibility, risk, and information value? |
| Stop conditions | When should an action continue, downgrade, or stop? |

## Run directly from GitHub

[uv](https://docs.astral.sh/uv/) is the only launcher you need:

```bash
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi demo
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi doctor
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi serve
```

After a PyPI release, the shorter server command is:

```bash
uvx cyber-junshi serve
```

The MCP transport in v0.1 is stdio. The client launches and manages the server process.

## One-command Agent setup

Setup previews the exact change and writes nothing by default. Add `--apply` to modify only the
target Agent configuration. Existing files are backed up and unrelated settings are preserved.

```bash
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install hermes
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install openclaw
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install codex
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install claude-desktop
```

Apply one integration after reviewing its preview:

```bash
uvx --from git+https://github.com/AITCX08/cyber-junshi cyber-junshi install hermes --apply
```

Guides: [Hermes](adapters/hermes/README.md), [OpenClaw](adapters/openclaw/README.md),
[Codex](adapters/codex/README.md), and
[Claude Desktop](adapters/claude-desktop/README.md).

## MCP tools

| Tool | Effect |
| --- | --- |
| `assess_safety` | Read-only risk screening with reasons and next steps |
| `structure_case` | Read-only fact/inference/unknown normalization |
| `compare_options` | Read-only explainable option ranking |
| `create_action_plan` | Read-only observation window and exit-rule validation |
| `record_outcome` | Explicit local SQLite write |
| `review_decision` | Read-only review of one stored outcome |
| `search_knowledge` | Read-only local search with evidence and source identifiers |
| `remember_question` | Explicitly save one question and selected memory under a subject alias |
| `recall_subject` | Read only one named subject's recent questions and active memory |
| `list_subjects` | List aliases and counts without returning question text |
| `forget_subject` | Hard-delete one subject and linked memory after confirmation |

The server instructions tell the Agent to run safety first when relevant, keep evidence layers
separate, expose option costs, and define stop conditions before acting.

## Independently authored knowledge pack

The repository includes 19 core decision notes and 15 practical communication notes under
[`knowledge/`](knowledge/). Every item is connected to a registered source and evidence level in
[`knowledge/catalog.yaml`](knowledge/catalog.yaml). The upstream `goutoujunshi` repository was
used only as a discovery-only topic lead; none of its prose, examples, templates, prompts, or
code is included.

Read the [content provenance policy](CONTENT_PROVENANCE.md) and run the audit before publishing
knowledge changes:

```bash
uv run cyber-junshi audit-knowledge --root .
```

## Real Skill workflow case (fictional)

This is a synthetic example, not a real chat or consultation record. It does not diagnose
anyone or guarantee a relationship outcome. A user asks: “Subject A cancelled two meetings at
the last minute. Should I keep trying to schedule one?” The host Agent understands the request
and writes the response; Cyber Junshi validates the decision structure. The tool snippets below
illustrate a workflow and do not determine Subject A's motive.

1. **Select the Skill and route safety.** The host Agent selects the `relationship` Skill and
   calls `assess_safety` first. With no self-harm, violence, threat, coercion, stalking, or
   privacy-exposure signal, the result is `level: "normal"`, so analysis can continue. A safety
   signal would take priority over message optimization.
2. **Search without claiming certainty.** `search_knowledge("communication boundary one
   clarification")` returns local material such as
   `{"id":"core-07","evidence_level":"E1","source_ids":["cdc-healthy-communication","project-four-mechanisms"]}`.
   Evidence level and source identifiers make the basis reviewable; cancellations alone do not
   prove avoidance, disinterest, or a personality label.
3. **Separate facts, inferences, and unknowns.** `structure_case` keeps: facts (two last-minute
   cancellations and no proposed new time); an inference (Subject A may not be available to
   schedule now, not a proven motive); and unknowns (why, whether they want to meet, and when).
4. **Compare option costs.** `compare_options` weighs waiting for a proposed time, sending one
   clarification, and no further contact. This example chooses one clarification because it is
   reversible and informative; no further contact remains a valid option instead of repeated
   follow-ups.
5. **Define stop conditions before acting.** `create_action_plan` sets a 48-hour observation
   window: continue only if Subject A offers a specific time; stop if they decline; and stop if
   there is no reply after 48 hours. Send only: “You cancelled at the last minute twice. We can
   reschedule when it works for you; if you do not want to continue, please say so directly. I
   will respect that and will not keep asking.” Do not send follow-ups, use another account, or
   recruit someone else to contact them.
6. **Memory is explicit and subject-isolated.** The host Agent asks whether the user explicitly
   agrees to save this question and “one clarification; no reply means stop” under Subject A.
   Only after the user explicitly agrees does it call `remember_question`; a later
   `recall_subject("Subject A")` returns only that subject's questions and active memory. It does
   not search across subjects or save anything in the background.

The host Agent owns language, context, and presentation. Cyber Junshi owns safety routing,
evidence layers, option comparison, stop conditions, and local memory only after explicit user
authorization.

## Skills

- `skills/cyber-junshi`: generic decision workflow for Agent Skills-compatible hosts.
- `skills/relationship`: consent-aware relationship example that rejects coercion, stalking,
  diagnosis by label, impersonation, and boundary bypass.

## Local data and privacy

- Default database: `~/.cyber-junshi/cyber-junshi.db`
- Override path: `CYBER_JUNSHI_DB=/path/to/file.db`
- No cloud account, telemetry, model gateway, conversation capture, or automatic chat import.
- Decision input is not logged. `record_outcome` writes only when explicitly called.
- `remember_question` explicitly stores the submitted question, summary, and selected memory
  under one local subject alias; it is never called in the background.
- `recall_subject` never searches across subjects, and `forget_subject` requires confirmation
  before cascading deletion.
- Repository examples are fictional and marked synthetic.

## Develop locally

```bash
git clone https://github.com/AITCX08/cyber-junshi.git
cd cyber-junshi
uv sync --extra dev
uv run pytest
uv run ruff check .
```

## Docker

```bash
docker build -t cyber-junshi .
docker run --rm -i -v cyber-junshi-data:/data cyber-junshi
```

Because v0.1 uses stdio, keep stdin open (`-i`) and configure the Docker command in the MCP
client rather than running it as a background HTTP service.

## Deliberate limits

v0.1 does not decrypt or capture chats, inspect user accounts, ship a web dashboard, call an LLM,
sync to a cloud service, depend on OpenViking, or automate social-media/community operations.

Licensed under [Apache-2.0](LICENSE).
