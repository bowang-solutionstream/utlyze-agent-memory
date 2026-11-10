---
name: i2e-team-v2-draft
description: Proposed coordinator entrypoint for a bounded engineering workflow with three execution lanes.
metadata:
  proposed_profile: i2e-team/v2
  proposal_revision: v8
  status: DESIGN_ONLY_NOT_INSTALLED
---

# I2E coordinator entrypoint

**Reader: the root coordinator.** This file is a draft for later adoption. Reviewing or publishing it does not authorize execution. Use the active installed workflow until the owner selects a validated replacement.

After adoption, use this profile for authorized engineering work in one project. Preserve read-only requests and explicitly selected legacy profiles. The coordinator owns progress and evidence. It cannot provide independent approval of its own work.

## Select the lane

Read [policy](references/policy.md). Establish the objective, authority, repository, current worktree, acceptance, technical risk, and relevant triggers. Use read-only investigation when classification is unclear. Queue urgency orders work; it does not select a model.

| Lane | Plan and build | Independent assurance |
|---|---|---|
| Direct | One clearly bounded Low-risk ticket. The worker records an inline contract and builds. | One fresh Sol verifier |
| Standard | Sol planning-only lead; fresh Astra plan approval; separate workers | Eligible Low risk: one verifier. Otherwise: three distinct Sol audits |
| Critical | High/Critical technical risk or significant architecture. Astra lead, separate plan reviewer, and worker | Three Sol audits and fresh Astra final |

Apply the full eligibility and specialist rules. Direct is the only lead/plan-approval exception. Unknown risk never authorizes writes. Max effort remains required. Requested settings and effective host evidence are separate.

## Run the work

1. **Prepare.** Read [execution](references/execution.md). Select the exact qualified controller. Record instructions, dirty state, dependencies, known cases, and permitted actions.
2. **Plan.** Bind acceptance, exclusions, risk, tests, authority, and an explicit write boundary. For Standard or Critical, obtain exact-plan approval with [the plan-review prompt](prompts/plan-review.md).
3. **Dispatch.** Verify actor identity, model/effort, selected tier policy, contribution history, and the supported write mode. Give the worker [its prompt](prompts/implementation.md) and only relevant context.
4. **Build.** Inspect preflights. Preserve VERIFY, TEST_ONLY, and PRODUCTION order. A behavior change needs meaningful assertion RED and unchanged-test GREEN.
5. **Integrate.** Accept a named commit only from the current authorized attempt. Record the actual combined candidate, base, harness, dependencies, and checks.
6. **Verify.** Use [the verification prompt](prompts/verification.md). Reviewers execute key checks and inspect source. Complete required specialists, finding rechecks, final case regressions, and triggered final review.
7. **Deliver.** Read [delivery](references/delivery.md). Check current evidence and authority. Enforce source and target conditions through the selected adapter. Read back the actual result.
8. **Finish.** Report local acceptance, PR, CI, merge, deployment, and customer acceptance separately. Give a concise engineering brief. Complete safe cleanup and record any unfinished obligation.

## Apply these controls

Expected file lists help planning. Before adding a file, check the approved boundary and semantic impact. A changed contract needs renewed approval before dependent writes.

Batch decomposed work into at most five bounded tickets. Preserve per-ticket proof and interaction checks. A smaller delivered subset does not complete the original request.

Read [verification](references/verification.md) for failure classification. Save first-failure evidence before correction. Canonical defects retain their cases, regressions, and repair counts. Two failed repairs require Astra diagnosis before a third.

Report material findings with evidence. Keep Low observations compact. Retain the distinct independent rechecker for fixed findings. Three unresolved cycles of one decision stop dependent work.

Worktrees and pushed commits do not prove isolation or safe cleanup. Preserve recoverable evidence, account for local files and dependencies, and confirm writer quiescence.

A relevant source, base, harness, or profile change invalidates affected proof. Unknown evidence stays unknown. No per-run budget gate is added.

For capability tests, exploratory trials, and profile activation, use [adoption](references/adoption.md). Proposal approval is a design verdict only.
