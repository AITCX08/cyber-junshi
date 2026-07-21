# Contributing

Thanks for improving Cyber Junshi.

1. Open an issue before a large behavioral or schema change.
2. Use fictional examples only. Never submit real chats, identities, account data, or outcomes.
3. Add a failing test before production-code behavior changes.
4. Run `uv run ruff check .` and `uv run pytest`.
5. Keep the core deterministic and explainable. Do not add a required cloud, model, telemetry, or
   account dependency.
6. Preserve the safety-first priority and explicit-write boundary.
7. For knowledge changes, register the original source and allowed use in
   `knowledge/sources.yaml`, add the item to `knowledge/catalog.yaml`, and run
   `uv run cyber-junshi audit-knowledge --root .`.
8. Treat `powerycy/goutoujunshi` as discovery-only. Do not submit paraphrased prose, examples,
   dialogue templates, exercises, headings/order, prompts, or workflow wording from it.

By contributing, you agree that your contribution is licensed under Apache-2.0.
