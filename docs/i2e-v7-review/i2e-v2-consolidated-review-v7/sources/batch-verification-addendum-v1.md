# I2E bounded batch verification — proposal v1

Date: 2026-11-03. Status: **PROPOSED DESIGN ADDENDUM — NOT INSTALLED**.

User direction: consider grouping roughly three edits/tasks so they share verification and review overhead. This addendum extends `graph-engineering-design-v2.md`; it leaves the frozen empirical reference and the previously verified diagram files unchanged. No actual tasks, branches, PRs or merge actions were performed.

## Proposed rule

Group two or three small, related tasks into one reviewable batch when they share a repository/client boundary, a coherent outcome, compatible delivery timing and a manageable combined risk. Keep acceptance criteria and applicable local test evidence for every task. Approve one exact batch plan, integrate the outputs, and independently verify the complete candidate once before authorized delivery.

Three is a starting heuristic, not a required quota, a safety guarantee or a per-run budget gate. Do not wait to fill a batch, delay urgent work or bundle unrelated changes merely to reach three tasks. Total scope, interactions, reviewability and rollback needs determine whether to split.

This route uses the existing project manager and work-package mechanism. It introduces no second coordinator. A single implementation worker may complete the batch; parallel workers are useful only for work that can be isolated safely.

## Sequence

1. **Define the batch.** Record one shared outcome plus task IDs A/B/C, individual acceptance criteria, dependencies, scope/exclusions, risk, allowed actions and required assurance obligations.
2. **Approve the exact batch plan.** Fresh independent Astra approval covers all included tasks and their interaction risks. Adding material scope after approval requires a revised plan and renewed approval.
3. **Implement with local feedback.** Each task retains applicable meaningful TEST_ONLY → behavioral RED → PRODUCTION → unchanged-test GREEN, regression checks and saved failure/harness provenance. Run focused checks while working; do not defer all testing until the end.
4. **Integrate before final verification.** Combine outputs on a batch/feature branch against the intended base, resolve conflicts, and identify the complete source tree, dependency/configuration inputs and verification harness. Keep task-to-change/test mapping available. Squashing commits locally is optional and is not the source of token savings.
5. **Run shared checks.** Execute the required integrated suite, build/type/lint checks, relevant scans and cross-task interaction tests on the frozen combined candidate. Collect structured receipts once for that candidate. Earlier per-task passes do not establish combined correctness.
6. **Verify the batch independently.** One fresh Sol verifier, eligible across every included task, receives one shared context packet. It independently exercises every task's key acceptance behavior and relevant interactions, inspects changed source/assertions and targeted negative controls, and records an explicit disposition for each task plus the whole batch. It may retain context across repair rounds while remaining independent of implementation.
7. **Complete required assurance.** The union of the tasks' mandatory gates applies, augmented by interaction risks. Security, test, formal and Astra final obligations remain required when triggered. The low-risk one-verifier policy applies only if the whole batch is eligible; risk is never averaged down.
8. **Deliver the reviewed result.** The evidence gate verifies current candidate identity, findings disposition, reviewer eligibility, required approvals and action-specific authority. Open or complete the coherent PR as permitted. Squash-merge into the target branch only after required checks and approvals, if that merge is authorized and the repository permits it.

A draft PR may exist earlier for visibility; it does not authorize merging. The combined source and applicable verification inputs are what must be checked. If the merge base, source, conflict resolution, dependencies or verification setup changes materially after verification, refresh affected proof before delivery.

## What is shared, and what remains distinct

| Shared once per unchanged batch candidate | Preserved for each task |
|---|---|
| Planning context and exact-plan challenge/approval | Objective, scope and acceptance criteria |
| Environment setup and repository orientation | Work ownership and dependencies |
| Required full integration/build/check execution | Applicable focused tests and RED/GREEN provenance |
| Independent verifier context and batch review | Findings, evidence links and explicit acceptance status |
| Required specialist context where coverage overlaps | Any task-specific mandatory assurance requirement |
| Delivery preparation and PR description | Task-to-change/test traceability |

The verifier must also check interactions that no task considered alone. Shared full-suite receipts are reusable only for the same applicable candidate and verification setup, as required by v2. All blocking findings need evidence and impact; unsupported preferences remain advisory.

## Batch boundaries and failures

- Favor one user-facing outcome or tightly related behavior. For example, three fixes to validation, error display and retry behavior in the same form can be a candidate batch after risk assessment.
- Keep a cosmetic fix, a tenant-permission change and a destructive migration separate when their risk, ownership, release or rollback needs differ. Merely sharing a repository is insufficient.
- Keep unrelated refactoring out of the batch when it obscures functional changes. Preserve enough task-level history and evidence to diagnose which change introduced a failure.
- Any required failed or unrun critical check, unresolved blocker or missing approval holds batch acceptance. Two passing tasks do not overrule the third task's failed requirement.
- If one task stalls, either repair it within the approved scope or remove/split it. Removing a task creates a new candidate; the remaining pair is not automatically certified by an older combined run.
- A repair invalidates affected proof. Run the required checks on the new integrated candidate, reassess interactions and have the independent verifier renew the batch disposition. Review can focus on the changed portion and its effects; it must not reuse a stale batch approval.
- Preserve failures before repair and count repairs by defect ID across restarts. Two failed repairs of the same defect still trigger Astra diagnosis. Required final-review independence remains unchanged.
- Choose a batch that can be delivered and rolled back coherently. A squash commit makes the combined change one history unit on the target branch; that may be inconvenient when unrelated fixes later need separate rollback.

## Expected savings and measurement

The expected saving is repeated context/setup and orchestration overhead. Squashing commit history does not shrink the final code diff, eliminate acceptance requirements or establish correctness.

An explanatory model for three tasks is:

- Separate execution: `3 × fixed setup/review overhead + task-specific verification work`.
- Batch execution: `1 × shared setup/review overhead + task-specific verification work + interaction/rework overhead`.

This is a reasoning model, not a measured token estimate. A batch can cost more when integration, scope complexity or rework exceeds the shared overhead saved. Deterministic test execution also consumes runtime; avoid repeatedly feeding full logs into model context while retaining complete logs in artifacts.

Evaluate batching separately from reducing reviewer counts: hold the selected reviewer policy/model routing constant when comparing batched and separate work. Measure total model usage per accepted task, end-to-end elapsed time including batch waiting, user interventions, escaped defects, rework and interaction failures. Preserve all required checks during evaluation. No percentage saving is claimed.

## Relationship to policy adoption

This is a proposed refinement to v2's work-package and verification unit. It is not an installed exemption from existing per-task or project-specific gates. A policy requiring separate reviews cannot be silently reinterpreted as satisfied by one batch review. The runtime and selected policy must explicitly support batch plan/evidence identity and per-task dispositions before certifying completion under this route.

## Sources

- GitHub documents squash-and-merge as combining a PR's commits into one commit on the base branch and describes its fit for one logical change: https://docs.github.com/en/pull-requests/reference/pull-request-merges
- Google's engineering guidance favors small, self-contained changes, keeping related tests with their code and separating unrelated refactoring: https://google.github.io/eng-practices/review/developer/small-cls.html
- Local v2 contracts supply exact-plan approval, task isolation, empirical evidence, independence, candidate binding, triggered assurance and action authority requirements.

Neither public source establishes token savings for this I2E design. Batching two or three related tasks is the proposed experiment, not a provider-endorsed assurance guarantee.
