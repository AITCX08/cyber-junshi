# Clean-room Knowledge and Subject Memory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish an independently authored, provenance-audited knowledge pack and add explicit local memory isolated by subject alias.

**Architecture:** The upstream repository is a discovery-only topic map. Cyber Junshi content comes from verified official/primary sources or declared project-original material, while a separate SQLite store owns subjects, questions, and memory items. Four explicit MCP tools expose memory without background capture or cross-subject recall.

**Tech Stack:** Python 3.10+, SQLite, FastMCP, PyYAML, Typer, pytest, Ruff.

## Global Constraints

- Preserve Apache-2.0 compatibility and future commercial use.
- Do not copy or paraphrase upstream prose, examples, templates, headings, ordering, prompts, or workflow wording.
- Public availability is not permission to copy; copyrighted sources support factual synthesis only.
- Every knowledge item has provenance, evidence level, commercial-use status, creation mode, and review date.
- No real chat, identity, private outcome, or private dataset enters source control or fixtures.
- Memory is local-only, explicit-write, subject-isolated, and hard-deletable with confirmation.
- Knowledge and runtime memory never share an ingestion path.

---

### Task 1: Governance and knowledge inventory

**Files:** Create `CONTENT_PROVENANCE.md`, `THIRD_PARTY_NOTICES.md`, `knowledge/audit/topic-map.yaml`, `knowledge/sources.yaml`, `knowledge/catalog.yaml`, 19 `knowledge/core/*.md` documents, and 15 `knowledge/practical/*.md` documents. Modify both READMEs.

**Interfaces:** Produce exactly 34 catalog entries with `id`, `path`, `topic`, `evidence_level`, `source_ids`, `source_type`, `commercial_allowed`, `creation_mode`, and `reviewed_at`.

- [ ] Create a neutral 19-core/15-practical topic map with upstream marked `discovery_only`.
- [ ] Register verified official/primary/project-original sources and their reuse rules.
- [ ] Author each document in the Cyber Junshi structure: purpose, fact layer, inference limits, options, costs, stop conditions, sources.
- [ ] Publish clean-room governance and notices.
- [ ] Document provenance and local-memory separation in both READMEs.

### Task 2: Catalog validation with TDD

**Files:** Create `src/cyber_junshi/knowledge/__init__.py`, `src/cyber_junshi/knowledge/catalog.py`, `src/cyber_junshi/knowledge/search.py`, `tests/knowledge/test_catalog.py`, and `tests/knowledge/test_search.py`. Modify `pyproject.toml` and `tests/test_public_artifacts.py`.

**Interfaces:** Produce `validate_catalog(root: Path) -> CatalogReport` plus `search_knowledge(query: str, limit: int = 5, root: Path | None = None) -> list[dict[str, object]]`; package the checked-in knowledge directory in the wheel.

- [ ] Write tests for valid catalogs, required fields, unknown sources, missing files, disallowed upstream content sources, and exactly 34 checked-in items.
- [ ] Run `uv run pytest tests/knowledge/test_catalog.py -q` and observe the missing-module RED failure.
- [ ] Implement safe YAML parsing, enum checks, path containment, source resolution, commercial-use checks, upstream-source rejection, and deterministic local keyword search.
- [ ] Run focused tests and `uv run pytest -q`.

### Task 3: Subject-isolated memory with TDD

**Files:** Create `src/cyber_junshi/storage/memory.py` and `tests/storage/test_memory.py`. Modify `src/cyber_junshi/storage/__init__.py`.

**Interfaces:** Produce `SubjectMemoryStore` with `remember_question`, `recall_subject`, `list_subjects`, and `forget_subject`.

- [ ] Write tests for alias reuse, normalization, allowed kinds, confidence bounds, source linkage, limited recall, strict isolation, listing, invalid input, and confirmed cascade deletion.
- [ ] Run `uv run pytest tests/storage/test_memory.py -q` and observe the missing-module RED failure.
- [ ] Implement constrained SQLite tables with foreign keys, UTC timestamps, UUIDs, transactions, and `ON DELETE CASCADE`.
- [ ] Run focused tests and `uv run pytest -q`.

### Task 4: MCP and CLI integration with TDD

**Files:** Modify `src/cyber_junshi/mcp/server.py`, `src/cyber_junshi/cli.py`, `tests/mcp/test_server.py`, and `tests/test_cli.py`.

**Interfaces:** Add MCP tools `search_knowledge`, `remember_question`, `recall_subject`, `list_subjects`, and `forget_subject`; add CLI command `audit-knowledge`; update doctor from 6 to 11 tools.

- [ ] Write failing exact-surface, memory-cycle, confirmation, and CLI audit tests.
- [ ] Run the focused tests and observe RED failures.
- [ ] Implement minimal wrappers and JSON audit output.
- [ ] Run focused tests and `uv run pytest -q`.

### Task 5: Verification and publication

**Files:** Modify `CONTRIBUTING.md` and finalize both READMEs.

- [ ] Run `uv run cyber-junshi audit-knowledge` and require 34 items with no errors.
- [ ] Run `uv run pytest -q`, `uv run ruff check .`, and `uv build`.
- [ ] Search for private paths, raw-chat keys, identifiers, inappropriate upstream references, and large files; inspect `git diff --check` and the final diff.
- [ ] Commit and push `codex/clean-room-knowledge-memory` to the GitHub origin.
