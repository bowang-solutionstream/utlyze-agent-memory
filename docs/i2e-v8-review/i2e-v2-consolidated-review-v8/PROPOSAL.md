# I2E v2 — proposal revision 8

Date: 2026-11-10. Proposed profile: `i2e-team/v2`. Status: **DESIGN CANDIDATE. NOT INSTALLED.**

The owner requested v8, an independent review, and publication. The owner also required v7 and the active skill to remain unchanged. This request authorizes proposal work and its publication. It does not activate the proposed operating rules.

The [v7 packet](../../i2e-v7-review/i2e-v2-consolidated-review-v7/PROPOSAL.md) remains frozen. This candidate replaces v7 as the proposed design only after its own recorded review. The review result belongs outside the candidate, under the publication's `review` directory.

## 1. Objective

Produce reliable changes with a process small enough for routine use. Keep the checks that establish behavior, independent judgment, source identity, and authority. Use ordinary Git and GitHub mechanisms where their guarantees fit.

The first implementation has one coordinator, one default worker, one selected worker-write mode, and one GitHub delivery route. It extends the existing ledger and canonical case helper. It adds no general graph framework, second coordinator, new case store, or permanent specialist fleet.

The design has three routes: Direct, Standard, and Critical. These are execution lanes. They are distinct from finding severity, technical risk, and queue priority.

## 2. Proposed changes

| Change | V8 position |
|---|---|
| Small tasks | A narrowly eligible Direct lane uses one worker and one independent verifier. It omits a separate lead and Astra plan approval. |
| Model routing | Queue urgency orders work. Technical risk and significant architecture select planning and implementation models. The root remains coordinator. |
| Plans | Approval binds acceptance, risk, authority, dependencies, tests, and an explicit write boundary. Expected file names are an aid, not the entire boundary. |
| Critical assurance | The Critical lane always receives a fresh independent Astra final review. Existing final triggers also apply. |
| Prompts | The short entrypoint and three main role prompts are included as actual draft files. Their forward exercise remains NOT_RUN. |
| Host settings | Model, effort, and identity require host evidence. Service tier is a separately declared policy; strict matching remains the default. |
| Git handoff | Workers submit named commits. Current-attempt authority, write containment, proof freshness, and integration checks remain required. |
| Failure records | Save first-failure evidence immediately. Use a defined boundary between routine iteration events and canonical defects. |
| Batches | Keep mandatory batches of at most five tickets. Permit only preauthorized removal of independent tickets without another full approval. |
| Cleanup | Remove completed worktrees only after recoverable preservation, local-file accounting, dependency checks, and writer quiescence. |

These changes are proposed replacements for specific v7 rules. They require an explicit profile adoption before operational use. They cannot be used to certify an in-flight v1 run.

The [change record](CHANGE-RECORD.md) maps all ten Claude findings and the validation corrections. It also names deferred proposals.

## 3. Contract and packaging

The following files form one design contract. The references contain the rules. Prompts explain how a role applies them.

| File | Purpose |
|---|---|
| [SKILL-DRAFT.md](SKILL-DRAFT.md) | Entrypoint for the coordinator |
| [Policy](references/policy.md) | Roles, classification, model settings, and lane changes |
| [Execution](references/execution.md) | Plans, write boundaries, batches, and state |
| [Verification](references/verification.md) | Tests, independent review, failures, and findings |
| [Delivery](references/delivery.md) | Worker handoff, GitHub controls, recovery, and cleanup |
| [Adoption](references/adoption.md) | Implementation order, probes, trial, and activation |
| [Plan-review prompt](prompts/plan-review.md) | Independent challenge of the exact plan |
| [Implementation prompt](prompts/implementation.md) | Worker contract |
| [Verification prompt](prompts/verification.md) | Independent executed verification |
| [Validation summary](sources/VALIDATION-SUMMARY.md) | Evidence supporting this revision and its limits |

A conflict between files is a design defect. An entrypoint or prompt cannot silently weaken a reference. The manager and lead use the entrypoint and applicable references; they do not need separate copies of the entire contract. Specialist and final-review assignments use the same input/output envelope and the explicit verification rules.

This packet contains no runtime implementation or installation metadata. An implementation must map the draft file names to a validated package. It must provide the actual CLI and schema references before use.

## 4. Preserved requirements

1. User and project authority govern edits and external actions. Approval does not create new authority.
2. Preserve unrelated changes, client boundaries, credentials, raw failure evidence, and canonical cases.
3. Behavioral work uses meaningful assertion RED followed by unchanged-test GREEN. Nonbehavior work uses applicable checks.
4. Required checks, findings, and known case obligations remain visible. A generic passing command cannot replace missing acceptance coverage.
5. Reviewers are independent by actual session and contribution history. Role labels alone do not establish independence.
6. Relevant source, base, harness, instruction, profile, or dependency changes invalidate affected proof.
7. Two failed repairs of one defect require Astra diagnosis before a third. Three unresolved substantive cycles of one decision stop dependent work.
8. Report local acceptance, PR, CI, merge, deployment, and customer acceptance separately.
9. Provide a concise factual engineering brief. Preserve observations and evaluate reusable rule changes before adoption.
10. Add no per-run budget gate. Unknown usage is not zero.

The [frozen empirical reference](../../i2e-v7-review/i2e-v2-consolidated-review-v7/sources/empirical-verification-v1.md) remains unchanged. V8 proposes an implementation and evaluation sequence around it. It does not claim that the empirical proposal is active.

## 5. Evidence level

The preceding validation checked all v7 packet hashes, ran 118 current-source tests, and reproduced three installed-helper regressions. Those three tests passed against the corrected frozen baseline. Disposable Git probes demonstrated both useful commit behavior and limits in Claude's proposed replacements.

These results support the design choices. They do not qualify a v8 runtime. Actual role-prompt exercises, adapter enforcement, effective service tiers, the real-task trial, and comparative quality or cost results remain **NOT_RUN / UNVERIFIED**.

An independent review must assess correctness, proportionality, lawful success paths, and the proposed cuts. Its design verdict is not implementation acceptance, installation approval, or release authority.
