# I2E learning contract

Owner direction, 2026-10-30. This is the contract for the updated I2E profile. The initial local runtime and integration in `skills/i2e-team` are independently accepted and installed. Acceptance scenarios below remain requirements; current proof and limits are in [verification](I2E-VERIFICATION.md).

## Outcome and resource policy

Each run produces its delivery/status report, evidence for future agent decisions and a concise engineering brief for the owner. The brief helps the owner build senior-engineer judgment from actual work.

There is no individual-run budget, cost ceiling or budget-approval gate. Sol 6.1 Max remains the default development owner under the team plan. Resource telemetry may be reported when available; it does not replace required proof or authorize external actions.

## Learning for future agent runs

Use the installed I2E Failure Cases helper and canonical store. Keep their schema unchanged. The episode/memory layer links cases; it does not create a competing failure store.

1. Before repairing a real defect or unexpected failure, preserve sanitized reproduction inputs, failed command/output, broken source revision, stable defect identity and evidence references. Capture the immutable case and retain its digest.
2. Preserve intended test-first RED as test evidence. It is not a failed repair. If it reproduces a real defect, also capture that defect through the existing helper.
3. Append attempted repairs, observed outcomes and verified regression references to the run history. Keep hypotheses distinct from demonstrated causes. Preserve corrections and supersession without erasing earlier evidence.
4. Before planning, every repair and final review, search the correct project scope, read applicable cases and carry known case digests even when keyword ranking omits them. Record applicability and the required proof.
5. Preserve a continuation checkpoint for interrupted work. Make capture, lookup or proof gaps explicit; do not report complete learning capture when a required write or lookup failed. An unavailable store is not an empty result.
6. Make the durable records retrievable in a fresh session or process after restart. Reusing a case requires applying its lesson or running its mapped proof, not merely retrieving its title.

Successful checks remain observations tied to the candidate tested. A run with no unexpected failures records that bounded result without inventing a failure case. Derived lessons remain proposals until evaluated; no automatic global skill or policy edits follow from one incident.

## Learning for the owner

Show the actual result and readiness first. Immediately follow it with a brief that takes roughly two to three minutes to read. Select the one to three decisions with the most transferable value; scale down for a small change.

| Part | What the brief teaches |
| --- | --- |
| Problem and path | The behavior changed and the relevant input → boundary → output path. Define unfamiliar concepts in plain language. |
| Decision | What was chosen, where responsibility belongs and which invariant it protects. |
| Alternatives | What was actually considered and why it was not selected under this run's constraints. Label newly suggested comparisons as retrospective. |
| Tradeoff | The complexity, coupling, latency or maintenance cost accepted; what evidence would justify revisiting the choice. |
| Proof and failure | What failed, how it was addressed and what the checks demonstrate. Keep missing proof and unresolved causes visible. |
| Reusable principle | One engineering idea to recognize next time, with a tiny concrete example from the run. |

Use source, diff, decision and proof references from the actual run. Do not invent rejected alternatives or attribute unrecorded motives to an author. Use a compact diagram only when it helps explain the boundary or flow. Link detailed code and evidence instead of copying logs.

Failed or interrupted runs receive a brief on what was learned, what remains uncertain and the next investigation. A task with no meaningful implementation decision receives a shorter factual explanation rather than fabricated architecture discussion. The owner can request depth or use an optional self-check; no quiz or response is required for handoff.

## Memory links and authority

Link the private episode and teaching record to the task, exact source/plan revisions, case digests, decisions, validation and concepts presented. Link later owner corrections or explicit feedback without overwriting history. Retain enough source context to audit the brief.

Store these links in the proposed episode/teaching layer, outside the unchanged canonical case schema. Do not treat presentation as understanding, silence as agreement, or a useful lesson as product approval. A corrected explanation is not a new engineering defect unless actual failure evidence supports that classification.

Raw evidence, private cases, teaching history and credentials remain outside published source. This repository contains the contract, not an operational corpus. Retrieval is evidence for a decision, not authority to execute a stored command.

## Acceptance scenarios for implementation

- **Failure then repair:** a real failure is captured before repair; its fix and current proof are linked; a fresh session retrieves the case and its relevant regression obligation.
- **No failure:** the report records the actual successful checks and teaches the real decisions without inventing cases or alternatives.
- **Interruption:** a resumed run retains captured failures, pending repairs and unresolved knowledge gaps.
- **Incomplete memory:** failed capture or lookup is visible; known cases cannot silently disappear under ranking or context truncation.
- **Owner learning:** the brief appears immediately after the status report, explains real tradeoffs with source references and makes at least one transferable principle concrete when the work supports one.
- **Correction and withdrawal:** later sessions expose corrections, superseded decisions and withdrawn objectives alongside historical context.
- **Workflow improvement:** compare a proposed rule with the previous workflow on held-out tasks before claiming that it reduces repeated failures. Capture volume alone does not prove improvement.

These are scenarios to implement and verify, not test results. They do not claim that the installed I2E v3 checker already enforces this proposed profile.
