# Content provenance and clean-room policy

Cyber Junshi is Apache-2.0 software intended to remain usable in commercial and non-commercial settings. Its public knowledge pack is therefore built from project-original analysis plus independently verified official or primary sources.

## Clean-room rule

`powerycy/goutoujunshi` may be inspected by an auditor only to discover broad topics and source leads. It is not a content source. Writers must not copy or paraphrase its prose, examples, dialogue, exercises, document structure, prompt text, or selection and ordering of material.

The working process is:

1. Record a neutral topic name and source lead without upstream prose.
2. Open and verify the original source.
3. Record publisher, URL, use rule, review date, and evidence role in `knowledge/sources.yaml`.
4. Write from the source and Cyber Junshi's own four-mechanism model.
5. Validate the catalog and review the result for expressive similarity.

Similarity checks are quality controls, not a legal safe harbor. Public access to a page is not permission to copy it.

## Allowed creation modes

- `project_original`: independently designed Cyber Junshi method or template.
- `primary_source_rewrite`: new factual synthesis based on registered primary research.
- `official_source_rewrite`: new operational summary based on an official source.

`upstream_paraphrase`, unverified copying, and source-free imported text are prohibited.

## Evidence levels

- `E0`: project-original heuristic; useful for structuring a decision, not a factual claim.
- `E1`: official guidance or a single relevant study.
- `E2`: multiple studies, a systematic review, or convergent authoritative guidance.
- `E3`: current law, binding rule, or directly controlling official text. Jurisdiction and review date still matter.

## Runtime memory is not knowledge

Questions and memory items written through the MCP memory tools remain in the user's local SQLite database. They are never imported into the public knowledge catalog, analytics, examples, or training material. Every write is explicit, subjects are isolated by alias, and confirmed deletion is a hard cascade.

## Review and removal

Legal and crisis-safety entries should be reviewed at least every 90 days before release. Other entries should be reviewed annually or when a cited source materially changes. Open an issue identifying the catalog ID and concern; maintainers should disable a disputed item until provenance is resolved.
