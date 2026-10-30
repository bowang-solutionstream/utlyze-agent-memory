# Agent-team direction

This is the agreed design direction, not an installed replacement for the existing full I2E workflow.

The user manages objectives, priorities and material tradeoffs through a PM chat. A development owner receives a bounded task contract and returns evidence, findings, status and usage. The PM explains consequential architecture choices, reasons, alternatives, cost/security tradeoffs and reversibility before dependent work.

## Model allocation

Every issue starts with a bounded Sol 6.1 Max probe of scope, urgency, technical risk and uncertainty.

| Classification | Proposed implementation ownership |
| --- | --- |
| P0 priority OR Critical technical risk | Astra Max plans and implements |
| Other sufficiently classified work | Sol 6.1 Max continues from the probe |
| Explicit, bounded, lower-priority and Low-risk edits | Optional experimental Luna 6 Max worker under Sol ownership |

P1 alone does not select Astra. Priority and risk are separate scales. Unknown risk is investigated rather than silently treated as low. Luna is an unbenchmarked worker option, not a replacement for the default Sol owner or an independent approver.

## Shared lifecycle

Use one I2E-derived lifecycle per deliverable: contract and probe, selected-owner plan, fresh independent Sol doubt, meaningful failing assertion, implementation, unchanged-test pass, three distinct Sol code/security/test reviews, conditional additional final review, and evidence-linked PM handoff.

For the proposed profile, additional final review is triggered by consequential authorization/tenant changes, destructive migrations, critical financial behavior, uncertain cross-system interactions, material redesign, conflicting reviews, or user/project requirements. Initially use a fresh independent Astra Max reviewer when triggered. Author routing and final-review triggering are separate decisions.

## Skill incorporation

- Derive a delivery skill from I2E Astra Sol for triage, routing, proof-driven edits and repair.
- Derive an assurance skill/checker from I2E Quality Gates for independent reviews, current proof and conditional final review.
- Preserve the existing I2E Failure Cases helper and canonical store.
- Reuse I2E Reporting conventions for compact, evidence-linked handoffs.
- Add a PM skill for objectives, assignments, progress, budgets and decision communication.

The installed native-v2 master/checker have fixed roles and mandatory final review. They cannot be relabeled as certifying the proposed tiered profile. The new profile must be implemented and evaluated separately.

Cost controls target repeated context, duplicate coordination, unnecessary review renewal and unconditional extra final review. Required evidence and review independence remain. Savings and equivalent quality are hypotheses until measured end to end; the Luna tier has no local benchmark result.
