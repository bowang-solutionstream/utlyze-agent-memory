# Agent-team direction

This is the agreed design direction. Its initial Sol/Astra delivery profile is implemented in `skills/i2e-team`, independently accepted and installed locally. The broader product-memory system remains separate.

The user manages objectives, priorities and material tradeoffs through a PM chat. A development owner receives a bounded task contract and returns evidence, findings, status and available usage. The PM explains consequential architecture choices, reasons, alternatives, cost/security tradeoffs and reversibility before dependent work.

## Model allocation

Every issue starts with a bounded Sol 6.1 Max probe of scope, urgency, technical risk and uncertainty.

| Classification | Implementation ownership |
| --- | --- |
| P0 priority OR Critical technical risk | Astra Max plans and implements |
| Other sufficiently classified work | Sol 6.1 Max continues from the probe |
| Explicit, bounded, lower-priority and Low-risk edits | Optional experimental Luna 6 Max worker under Sol ownership |

P1 alone does not select Astra. Priority and risk are separate scales. Unknown risk is investigated rather than silently treated as low. Luna is an unbenchmarked worker option, not a replacement for the default Sol owner or an independent approver.

The initial `i2e-team/v1` runtime implements the Sol/Astra tiers. The optional Luna experiment remains future work and is not silently selected by this profile.

## Resource policy

Owner direction, 2026-10-30: the updated I2E has no per-run budget requirement, cost ceiling or budget-approval gate. Sol 6.1 Max is the default development owner. Usage may be reported when available, but missing usage is not a budget blocker and must not be reported as zero. Required proof, review and authorization still apply.

## Shared lifecycle

Use one I2E-derived lifecycle per deliverable: contract and probe, selected-owner plan, separate fresh Astra approval of that exact plan, fresh independent decision challenge, meaningful failing assertion, implementation, unchanged-test pass, three distinct Sol code/security/test reviews, conditional additional final review, and evidence-linked PM handoff followed by a concise engineering learning brief. Ordinary challenge uses Sol; significant architecture or Critical risk uses fresh Astra. Capture and reuse failures throughout the run.

For this profile, additional final review is triggered by consequential authorization/tenant changes, destructive migrations, critical financial behavior, uncertain cross-system interactions, material redesign, conflicting reviews, or user/project requirements. Use a fresh independent Astra Max reviewer when triggered. Author routing and final-review triggering are separate decisions.

## Two learning outcomes

- **For later agent runs:** preserve real failures before repair, link verified fixes and regression proof, and consult the existing canonical case store before planning, each repair and final review. Recording a case alone is not reuse.
- **For the owner:** immediately after the result/status report, explain the few decisions that mattered, the actual alternatives considered, accepted tradeoffs, validation and a reusable engineering principle. A short code or data-flow example should make the principle concrete. Deeper discussion is optional.

The [learning contract](I2E-LEARNING-CONTRACT.md) defines both outputs, failed/interrupted-run handling and acceptance scenarios. Neither output can turn incomplete implementation proof into completion or automatically modify global skills.

## Skill incorporation

- Derive a delivery skill from I2E Astra Sol for triage, routing, proof-driven edits and repair.
- Derive an assurance skill/checker from I2E Quality Gates for independent reviews, current proof and conditional final review.
- Preserve the existing I2E Failure Cases helper and canonical store.
- Reuse I2E Reporting conventions for compact, evidence-linked handoffs.
- Add a PM skill for objectives, assignments, progress and decision communication.
- Reuse Mentor Bo's evidence-grounded teaching approach for the post-run engineering brief.

As inspected on 2026-10-30, the existing master and quality-gate skills identify `i2e-chat-astra-sol/v3`. They require Pro reasoning, independent Astra plan approval and mandatory independent Astra final review. The distinct `i2e-team/v1` profile uses owner-led planning without mandatory Pro transport, retains independent Astra plan approval, and makes additional final review conditional. It has its own checker and cannot claim old-v3 completion. Explicit old-v3 selection retains the existing unchanged workflow.

The local default route is installed with a source/destination-bound receipt. This does not change project permissions, release authority, the old-v3 engine or the canonical failure-case schema.

Efficiency work targets repeated context, duplicate coordination and unnecessary review renewal. It does not introduce individual-run budget gates. The effect of the proposed routing on throughput and quality remains to be measured; the Luna tier has no local benchmark result.
