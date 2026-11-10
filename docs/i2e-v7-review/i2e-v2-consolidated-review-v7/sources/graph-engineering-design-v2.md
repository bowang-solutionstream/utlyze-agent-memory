# I2E graph engineering design v2

Date: 2026-11-03. Status: **DESIGN PROPOSAL — NOT INSTALLED**.

This revision turns the project-fleet proposal into explicit roles, transitions, evidence contracts and recovery rules. Empirical verification is central; specialist assurance is selected by risk and required policy. The graph is a design artifact, not an implementation or a formal proof.

The frozen `../empirical-verification-v1.md` remains unchanged (SHA-256 `5c722c4ac4effd3b7be059d4aced424e5d33aae077f5e32521823e6dd39752fc`). The review-policy proposal is `../graph-empirical-review-policy-v1.md`. A reduced reviewer count requires a separately selected policy and matching runtime enforcement. This document does not assert compliance with an older profile while changing its mandatory audits.

## Design decision

Use one project manager as the coordinator. A planning-only tech lead defines the contract. Fresh independent Astra approves the exact plan. Bounded Sol/Terra workers implement and collect evidence. Deterministic tools perform applicable checks. A fresh independent Sol verifier executes key acceptance and adversarial checks and reviews relevant source, test quality and evidence limits. Required specialists add assurance before an evidence-and-authority gate permits delivery.

For eligible low-risk work, the proposed single-verifier route replaces three routine audit sessions. Eligibility requires every condition: bounded scope, assessed low risk, observable acceptance, adequate relevant regression coverage, reproducible checks, no mandatory specialist requirement, and no unexplained failed or unrun critical check. Business priority and diff size alone cannot qualify a task. Critical work retains applicable distinct code/security/test audits and mandatory final reviews.

## Roles and permissions

| Role | Responsibility | Boundary |
|---|---|---|
| Portfolio coordinator, if used | Route requests, surface cross-project dependencies and summarize status | Each project retains its own state, authority and engineering coordinator |
| Project manager | Coordinate dependencies, claims, evidence, escalation and authorized delivery | Cannot waive policy, impersonate independent review or publish without authority |
| Tech lead | Scope, acceptance, assumptions, dependencies, verification contract and work packages | Never implements; urgent implementation uses a separate worker |
| Independent Astra plan reviewer | Challenge and approve the exact plan revision | Fresh session; excluded from final-review eligibility for that work |
| Implementation workers | Make bounded changes and supply meaningful RED/GREEN/regression evidence | Explicit path ownership and isolation; changes outside the plan return for reassessment |
| Deterministic check nodes | Format/lint/type/build/contract/integration/security checks as applicable | Execute code; no separate model session needed for each command |
| Independent Sol verifier | Execute relevant behavior, challenge plausible faults, inspect assertions/source, report limits | Did not plan, orchestrate or implement the candidate; distinguish executed from inspected evidence |
| Triggered specialists | Security, test, formal and named Astra final review | Same candidate; required review remains mandatory; final reviewer excludes all relevant contributors and prior review/escalation participants |

Requested invocation settings are GPT-6 Astra / max / Standard and GPT-6.1 Sol or Terra / max / Fast. Luna is excluded. Verify actual available/effective settings at dispatch. If the host cannot express the split, use supported separately configured sessions or hold the affected dispatch; a prompt naming a model is not invocation proof. These settings were not executed by this diagram task.

## Node contract

Every node records: project/run/task ID, graph and policy version, owner role/session, input IDs and hashes, dependencies, allowed writes/actions, actual model configuration where applicable, command/environment inputs, output schema, success predicate, timeout/retry rule and invalidation dependencies.

The plan includes observable acceptance, scope and exclusions; business priority, implementation difficulty and technical risk as separate axes; affected interfaces and ownership; meaningful failure cases and relevant rollback needs; mandatory review triggers; and work packages with dependency and verification obligations.

## Main graph and guards

| Transition | Required condition | Result |
|---|---|---|
| Intake → plan challenge | Scope, acceptance, risks, permitted actions and verification contract are explicit | Plan revision submitted for fresh Astra review |
| Plan challenge → ready | Explicit approval of the exact revision by an eligible independent session | Approved revision ID; rejected plans return to the lead |
| Ready → implementation | Required dependencies complete; valid exclusive ownership; allowed paths and invocation settings confirmed | Isolated worker attempt begins |
| Implementation → integration/checks | Required work-package outputs exist; applicable meaningful RED and unchanged-test GREEN preserved | One integrated candidate with source and harness identity |
| Checks → independent verification | Required deterministic checks pass or have an explicitly valid policy disposition; no unexplained unrun critical check | Candidate-bound check receipts |
| Verification → required specialists | Risk/coverage or policy requires a specialist | Required obligations recorded; specialists may run in parallel on the frozen candidate |
| Verification → delivery gate directly | Verifier passes and no additional required gate exists under the selected policy | Complete candidate-bound evidence set |
| Specialists → delivery gate | All required obligations have valid passing dispositions | Candidate-bound specialist approvals and proof limits |
| Delivery gate → authorized action | Identity current, findings resolved, reviewer eligibility valid, all required approvals present, requested action authorized | Commit/PR or other explicitly permitted action |
| Authorized action → reported result | Actual action result and applicable CI state reconciled | Precise outcome; no inferred merge/deployment/client acceptance |

Any failed check or validated implementation finding is captured before returning to a worker. A plan defect returns to the lead and fresh approval of the changed plan. After two failed repairs of the same defect, Astra diagnoses before another repair attempt. The diagnosing participant cannot later serve as the independent final reviewer.

The diagram compresses worker fan-out into one work-package group, deterministic checks into one tool node, and specialist branches into one conditional group. Their contracts are expanded here and in the HTML detail sections. The common verification repair loop is drawn; the same recorded repair/replan rules also apply to failures from checks, specialists and the delivery gate. No failure can bypass re-verification.

## Durable task state

Proposed runtime states are `DRAFT`, `PLAN_REVIEW`, `READY`, `RUNNING`, `INTEGRATING`, `VERIFYING`, `SPECIALIST_REVIEW`, `ACCEPTED_LOCAL`, `DELIVERING`, `DELIVERED`, `REWORK`, `HOLD`, `FAILED` and `CANCELLED`.

- `READY` means dependencies and plan approval are satisfied, not that a worker has accepted a claim.
- `RUNNING` requires a current lease and fencing token. Completion from an expired attempt is rejected even if its process is still alive.
- `ACCEPTED_LOCAL` describes technical acceptance; it does not confer external action authority.
- `HOLD` records an unmet prerequisite with its exact reason, owner and release condition. Preserve underlying evidence labels such as `UNKNOWN`, `NOT_RUN` or `UNVERIFIED`.
- `REWORK` preserves the finding and earlier artifacts, invalidates affected downstream evidence, and returns to the appropriate worker or lead. Repair attempts are counted by stable defect ID, including across restarts.
- `FAILED` and `CANCELLED` remain separate terminal outcomes. An exhausted infrastructure retry limit does not silently become acceptance.
- `DELIVERED` records the result of the specifically authorized delivery action. PR opened, CI passed, merged, deployed and customer acceptance remain separate action/evidence fields.

State changes should be append-only events with a monotonically increasing state version and compare-and-swap transition checks. Record graph revision, policy revision and candidate identity in the event; replay must recover the same obligations. These are proposed runtime contracts, not implemented guarantees.

## Empirical evidence contract

For regression work, preserve TEST_ONLY → behavioral assertion RED → PRODUCTION → unchanged-test GREEN. A runner/fixture/setup failure is not behavioral RED. At RED save test bytes, source snapshot, runner, config, relevant fixtures, dependency lockfile, tool/environment versions, exact commands, expected outcomes, actual output and exit codes.

For important new behavior, run targeted negative controls, mutations or fault injection against plausible changed faults. Do not require a unique mutant per new test or a universal 100% mutation score. Distinguish assertion kills from invalid/equivalent mutants, compilation failures, setup errors and timeouts.

The independent verifier receives original intent, accepted tradeoffs, scope, plan, relevant dependencies, source and evidence. It independently exercises key acceptance and selected failure cases, inspects changed source and assertion quality, and reports coverage limits. Tests must preserve intended behavior; disabling legitimate behavior to satisfy a check is not success.

Each receipt records requirement ID, candidate/source identity (including uncommitted bytes if any), harness identity, environment, command, expected/actual result, exit code, timestamps, actor/session and `executed` or `inspected` status. Bind relevant dependencies/configuration, not just a Git commit. Shared full-suite evidence is reusable only for the same applicable candidate and verification setup.

Findings require a violated requirement or material risk, concrete evidence and impact. Runnable reproduction is preferred when appropriate; deterministic checks, precise source arguments and relevant formal counterexamples also count. Unsafe live exploits are not required. Unsupported preferences remain advisory. Implementers address validated findings and document evidence-based disagreements rather than accepting every suggestion.

## Triggered assurance

Assess triggers at intake and again after the actual diff. A trigger adds an obligation before completion; it cannot be downgraded silently because a task is small or urgent.

- **Security:** auth, tenant isolation, secrets, sensitive data and trust boundaries. Add independent specialist judgment, relevant scanners and safe negative checks.
- **Test/verification:** large behavior change, weak assertions, concurrency/retry behavior, unclear regression coverage or difficult environment reproduction.
- **Formal:** a specific justified state/property, such as exclusive task ownership, expired-worker publication prevention, approval freshness or retry-safe publication. Formal checking does not automatically replace other review obligations.
- **Astra final:** consequential authorization/tenant changes, destructive migrations, critical financial behavior, uncertain cross-system interactions, material redesign, conflicting reviews and explicit user/project requirements.

## Formal evidence and drift

The plan names the invariant or progress property, assumptions, bounds, implementation paths and why formal checking adds coverage. Preserve model/config hashes, checker version and command, termination state, explored bounds, reachability/progress observations and counterexamples.

Demonstrate model-to-code alignment with mapped scenario tests, replayable counterexamples where representable or trace validation. A synchronization commit is bookkeeping, not proof. Relevant source/dependency/configuration changes invalidate alignment until reassessed. Record gaps. A successful bounded model check applies to that model and assumptions; observed traces do not cover all implementation executions. Formal tools were **NOT_RUN** for this design artifact.

## Recovery and delivery invariants

1. A work package has at most one valid write owner at a time. Task claims use leases plus fencing tokens; ownership checks guard result acceptance and publication.
2. A crashed coordinator first reconciles existing sessions, claims, receipts and external action results. It does not blindly redispatch every task.
3. Publication uses an operation ID/idempotency key and reconciliation of ambiguous outcomes. A local retry is not evidence that an earlier external action failed.
4. A relevant candidate, harness, dependency or configuration change invalidates affected evidence and approvals. Material plan changes require a new exact-plan approval.
5. Integration/conflict resolution is a source change; checks and affected reviews bind the integrated candidate.
6. No node can waive an unmet critical obligation through a narrative success summary. A completed agent turn is not task acceptance.
7. Commit, PR, merge and deploy authority are explicit, action-specific inputs. Technical approval alone grants none of them.

## Evaluation and adoption

Phase A strengthens empirical evidence while keeping baseline reviewer counts and model routing fixed. Phase B compares the proposed reduced route with baseline audits in shadow on representative low-risk tasks, including real regressions and controlled seeded faults whose answers are withheld from reviewers. Adjudicate disagreements using evidence.

Track caught/missed defects by severity, unsupported blockers, avoidable rework, reviewer effort, end-to-end latency, usage and verification-infrastructure upkeep. A single pilot establishes feasibility only. No percentage saving or daily reliability is claimed. Adoption requires sufficient evidence and owner selection of the versioned policy. No per-run budget or budget-approval gate is added.

## Visual artifact and verification scope

The user supplied a black-ink, warm-paper, orange-accent graph reference with handwritten headings and simple line icons. The HTML adapts those visual qualities with legible SVG text and precise orthogonal connectors. It is a fresh static document; there is no pre-existing hydrated page defect to measure and no application code to typecheck. Rendering checks cover the document and diagram only, not an executable I2E runtime.

The upstream `diagram-design` skill was read at commit `f24d98b05e2d7a5e68c2dedfe46e5b7173f50118`; it was used from a temporary source checkout and was not installed globally. The supplied visual reference resolves the style choice. Fonts are Caveat, Geist and Geist Mono, with explicit local fallbacks. The layout uses a 1280px readable canvas with local horizontal scrolling on narrow screens. A PNG preview, when provided, is a browser capture of the rendered overview.

## Source attribution

- Frozen empirical proposal and review-policy proposal above are the normative design inputs for this artifact.
- Anthropic architecture patterns: https://www.anthropic.com/research/building-effective-agents
- Anthropic evaluation guidance: https://www.anthropic.com/research/demystifying-evals-for-ai-agents
- Formal/mutation primary references remain in the frozen empirical proposal.
- Diagram skill: https://github.com/cathrynlavery/diagram-design/tree/f24d98b05e2d7a5e68c2dedfe46e5b7173f50118

This is a custom I2E proposal informed by published workflow/evaluation patterns, not an official Anthropic architecture or a claim about its internal engineering process. Lauren Tan attribution remains based on the user-supplied Za summary; the X exchanges were not independently verified for this design task.
