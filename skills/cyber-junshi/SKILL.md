---
name: cyber-junshi
description: Use when a user or Agent faces a consequential or ambiguous choice, needs to separate observations from assumptions, compare multiple actions, define exit criteria, or review a prior decision.
---

# Cyber Junshi

## Overview

Turn ambiguous situations into bounded, explainable decisions. Keep the host Agent responsible
for language understanding; use Cyber Junshi MCP tools for structure, validation, and local
outcome records.

## Workflow

1. If harm, coercion, stalking, threats, or immediate danger may be present, call
   `assess_safety` first.
   - For `emergency`, stop tactical advice and prioritize immediate local emergency or crisis
     support.
   - For `elevated`, prioritize evidence preservation, reduced exposure, and professional help.
2. Call `structure_case` with three explicit lists:
   - `facts`: directly observed or documented.
   - `inferences`: interpretations that may be wrong.
   - `unknowns`: information that could change the decision.
   When domain guidance would help, call `search_knowledge` first and preserve its evidence
   level and source identifiers; do not present E0 project heuristics as research findings.
3. Call `compare_options` with at least two actions. Score short-term gain, long-term cost,
   reversibility, risk, and information gain from 0 through 10. Explain the tradeoff; do not
   present the score as objective truth.
4. Call `create_action_plan` for one bounded action. Include an observation window, success
   signals, downgrade signals, and at least one stop signal.
5. Call `record_outcome` only after the user explicitly asks to save the result. Never persist
   raw conversation content by default.
6. Call `review_decision` when the user asks to evaluate a saved outcome.
7. When the user names a recurring subject and explicitly asks to use prior context, call
   `recall_subject` for that alias only. Never search across subjects.
8. Call `remember_question` only when the user explicitly asks to remember the question or
   selected facts. Explain that the raw submitted question is stored locally.
9. Call `forget_subject` only after the user confirms permanent deletion.

## Response Contract

Return, in order:

1. Safety route and its evidence.
2. Facts, inferences, and unknowns.
3. Ranked options with visible costs and assumptions.
4. One next action, observation window, downgrade conditions, and stop conditions.
5. Remaining uncertainty and the next information worth collecting.

## Boundaries

- Do not diagnose personalities or treat labels as safety evidence.
- Do not help with coercion, stalking, impersonation, credential access, or bypassing a stated
  boundary.
- Do not invent facts to fill an unknown layer.
- Do not turn a ranking into a guarantee.
- Do not write an outcome record without explicit user intent.
- Do not write subject memory in the background or infer that mentioning a name grants consent.

## Example

For “My collaborator cancelled once; should I confront them or wait?”, route safety, separate
the cancellation from the inference that they are avoiding the user, compare a direct message
with a short observation period, then define what response continues, downgrades, or stops the
plan.
