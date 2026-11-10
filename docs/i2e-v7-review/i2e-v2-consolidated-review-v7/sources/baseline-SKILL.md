---
name: i2e-team
description: Run the updated PM-to-delivery I2E workflow with Sol 6.1 Max by default, independent reviews, durable failure reuse and a concise engineering learning brief. Use for a full implementation workstream; preserve read-only requests and explicitly selected legacy profiles.
metadata:
  profile: i2e-team/v1
---

# I2E Team

Use one continuing delivery record with explicit acceptance and allowed actions. The PM owns objectives, priorities and material tradeoffs. The development owner returns actual evidence and a concise learning brief. Review never grants release authority.

## Models and profile selection

| Responsibility | Model |
| --- | --- |
| Read-only probe, default development owner, ordinary challenge, code/security/test audits | `gpt-6.1-sol` / `max` |
| Development owner for P0 priority or Critical technical risk | `gpt-6-astra` / `max` |
| Independent exact-plan approval, architecture/Critical challenge, repeated-failure diagnosis | `gpt-6-astra` / `max` |
| Independent final review when a named trigger applies | `gpt-6-astra` / `max` |

Verify actual model, effort and session identity before dispatch. A skill cannot switch the running model. Use fresh reviewer context with the artifact, contract and neutral question, without the author's conclusion. Preserve actual invocation and raw response evidence. Record residual PM/coordinator usage honestly.

This distinct profile uses owner-led planning. It does not require the old Pro transport stages or certify old-v3 completion. If the user explicitly selects `i2e-chat-astra-sol`, use that installed profile and its unchanged mandatory stages. Do not mix their receipts or waive their gates. Luna is not part of this initial runtime profile.

There is no individual-run budget, cost ceiling or budget-approval gate. Available usage is optional telemetry; unknown usage is not zero. No automatic provider, remote-sharing, commit, push, PR or deployment authority follows from this workflow.

## Intake and routing

1. Establish the task, project/repository, owned paths, allowed actions and observable acceptance. Inspect local instructions and current worktree; preserve others' edits.
2. Retrieve current objectives/decisions and applicable canonical failure cases. A missing store is a gap, not a search with no matches.
3. Dispatch a read-only Sol probe to inspect the relevant code path, dependencies, existing proof and unknowns. The PM checks its evidence and assesses priority and technical risk separately.
4. Use the runtime policy to select the owner. Unknown priority/risk or any unassessed trigger blocks routing. Sol continues from its probe unless P0 or Critical selects Astra. P1 alone does not select Astra.

Assess all seven final-review triggers explicitly with supporting evidence:

- Consequential authorization or tenant changes.
- Destructive migrations.
- Critical financial behavior.
- Uncertain cross-system interactions.
- Material redesign.
- Conflicting reviews.
- User or project requirements.

Any true trigger requires independent Astra final review. P0 author routing is separate from that decision. Reassess if scope, risk, evidence or review findings change; do not silently retain an earlier no-review decision.

## Delivery and assurance

Read [the runtime guide](references/runtime.md) before creating records or using helpers. Load the existing private storage settings using [settings discovery](references/settings.md) so later sessions reuse the same ledger and canonical case store. Settings supply paths, never project scope or authority. Keep runtime data in a private store outside source and installed skills. Use the installed canonical `i2e-failure-cases` helper and its own guide for case mechanics; never create a competing case schema or execute stored reproduction instructions.

1. Consult cases before planning. The selected owner prepares the plan, acceptance checks, scope, risks, alternatives and decision artifacts. Record actual contributors and immutable revisions.
2. Obtain separate fresh Astra approval of the exact plan. Preserve rejections; the latest qualifying verdict governs later starts. Plan approval does not discharge an unresolved architecture decision.
3. Challenge non-trivial decisions before dependent work. Use fresh Sol for ordinary claims and fresh Astra for significant architecture/Critical risks. A meaningful RED can challenge its mapped ordinary behavioral claim. Resolve findings with evidence; three unresolved substantive cycles of the same decision stop dependent work and surface it to the PM/user.
4. Use source-preserving VERIFY to collect existing applicable regression CHECK proof before ordinary writes, and refresh it when authorized test edits make it stale. VERIFY grants an empty source write scope; it can collect evidence while findings stay OPEN. Ordinary writes still require current applicable proof and resolved findings, except for an exact approved bounded remediation of its named obligations. Pass TEST_ONLY before test edits. For behavioral work, preserve an intended assertion RED on the current before-candidate. Syntax, import and setup failures do not qualify. Pass PRODUCTION before implementing the behavior, then obtain GREEN with unchanged test identity/content and relevant checks. VERIFY cannot supply RED/GREEN, replace the production cycle, clear a capture/lookup gap or reset phase history. Justified nonbehavior work uses actual applicable proof without inventing RED. The initial helper supports no behavioral waiver.
5. Preserve every real failure before repair: broken-state identity, sanitized reproduction evidence, stable defect identity and immutable canonical case digest. Consult scoped cases before each repair and carry known digests regardless of ranking. After two failed repairs of one defect, obtain Astra diagnosis before another attempt. Expected RED is not a failed repair.
6. Give the current source, contract, callers/dependencies and proof to three mutually distinct independent Sol audit sessions: code, security and tests. Exclude implementation/design contributors. The test audit checks assertion quality and actual proof, not only a green summary. Reviews may run concurrently against one frozen candidate.
7. Resolve actionable findings and refresh affected proof/reviews after changes. If any named trigger applies, obtain fresh Astra final approval. Exclude every contributor, plan/doubt reviewer, auditor and escalation participant from final review.
8. Consult cases for the final candidate, run relevant regression checks and run `check`. Report COMPLETED only after it returns `ready`; then record the brief and run `check` again for the completion PASS. Preflight evidence is replayed at its original position; later approvals, lookups or escalations cannot authorize earlier work. Missing/stale proof, capture/lookup gaps and unresolved findings prevent completion.

Helpers verify consistency, ordering and local evidence bytes. They do not authenticate model identity, inspect human intent, enforce OS write permissions or replace independent judgment. Inspect actual source and raw invocations. Do not report a structural checker pass as delivery, browser proof or release approval.

Keep a preflight call, inspection of its actual exit/state, and any dependent edit sequential. A BLOCK or failed command stops the affected write. Do not queue a write after a preflight in an unconditional batch. Preserve a rejected attempt and any premature work honestly; later success cannot authorize it retrospectively.

## Handoff and learning

Report result/readiness first, including actual proof, routing, known failure obligations and remaining gaps. Then immediately provide the brief described in [engineering learning](references/teaching.md): the important decisions, actual rejected alternatives, accepted tradeoffs, proof/limits and one transferable engineering principle with a concrete example. Keep the first pass concise; deeper discussion is optional.

Persist source/evidence links, run observations and teaching references in the private ledger. Preserve corrections, withdrawal and supersession visibly alongside history. A lesson remains a proposal until evaluated. Do not infer user mastery, treat silence as agreement or automatically modify global policy.

Interrupted or failed work receives an honest status, continuation checkpoint and brief about known facts and the next investigation. Never invent an alternative, verified root cause, successful check or completion claim to fill the report.
