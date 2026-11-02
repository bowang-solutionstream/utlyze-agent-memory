# Memory architecture

The two requested uses share provenance and explicit product scope but retain different authority levels.

| Memory area | Purpose | Boundary |
| --- | --- | --- |
| Product knowledge | Explain objectives, features, decisions and task acceptance to a fresh session | Sources, exact revisions, status, contradictions and withdrawals remain visible; an agent summary is not approval |
| Development experience | Preserve attempts, checks, success/failure observations and retrieval feedback | A passing command is a scoped observation, not automatic product success |
| Learning proposals | Connect experiences to candidate lessons and workflow changes | No automatic policy edit or claim of proven improvement |
| Owner learning | Retain the engineering concepts and decisions presented after a run | A presented explanation is not evidence of understanding or mastery |

The first implementation uses Python and SQLite for the core, exact lookup and deterministic keyword retrieval. Capture/search need no additional model or embedding API calls. Agent interpretation still consumes model tokens. The existing I2E helper is a separate prerequisite for canonical case operations.

Required context bypasses keyword ranking. When a compact pack cannot contain required information, it must expose incomplete status and exact recovery identifiers. Known failure obligations cannot be dropped because a search misses them. Raw source evidence stays separate from concise stored statements.

Task records preserve the exact objective/feature revisions used. Historical provenance must coexist with visible current withdrawal or supersession information. Product/project filters organize private local data; they are not an authentication boundary against a process running as the same OS user.

Learning records keep observations, hypotheses and proposed lessons distinct. Development/training examples must be separate from held-out evaluation examples. Both the old and proposed workflow must be compared on the same held-out set. Comparison metadata is attested evidence to inspect, not an automated evaluator or permission to promote a rule.

## Failure reuse and owner learning

The [I2E learning contract](I2E-LEARNING-CONTRACT.md) adds two requirements to the proposed delivery profile: durable failure capture with retrieval in later decisions, and an immediate concise engineering brief for the owner after each run's status report.

Canonical failure cases remain in the existing I2E case store and use its helper and unchanged schema. Development episodes link their case digests, source revisions and proof. Proposed teaching records link the episode, decisions and evidence; they remain separate from canonical cases and raw evidence. No additional record type is claimed to be implemented by this design amendment.

Corrections and applicability changes retain history. A successful fix requires its own current proof; a useful explanation does not establish that a fix worked. Capture or retrieval failures remain visible gaps. Learning proposals require evaluation before becoming workflow rules.

## Alternatives considered

[Gbrain](https://github.com/garrytan/gbrain) provides source-linked facts, correction/withdrawal, keyless keyword retrieval, and broader graph/MCP features. Its [memory-boundary documentation](https://github.com/garrytan/gbrain/blob/master/docs/guides/memory-boundaries.md) distinguishes durable knowledge from runtime authority and optional model-backed processing.

[Mem0](https://github.com/mem0ai/mem0) offers configurable model-backed extraction and retrieval with local deployment options. Its managed-platform benchmark claims do not establish the performance of the open-source SDK or this project.

The narrower local implementation avoids adding a runtime, provider account or service for this first contract. The tradeoff is maintaining custom code and initially lacking semantic retrieval, graph traversal and a shared remote service. Neither alternative is inherently cloud-only. Reconsider an adapter when measured retrieval misses, corpus scale or sharing needs justify it, using a version-pinned evaluation rather than advertised scores.

Sources were inspected on 2026-10-30. No framework was installed and no private memory data was sent to those services.
