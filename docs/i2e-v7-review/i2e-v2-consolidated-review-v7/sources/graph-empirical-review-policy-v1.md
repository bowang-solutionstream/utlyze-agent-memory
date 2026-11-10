# I2E graph workflow with empirical verification: review policy proposal v1

Date: 2026-11-03 (America/Denver)
Status: INDEPENDENT DESIGN PROPOSAL. This document integrates the user's project-fleet design with the frozen empirical verification reference. It does not install or alter the live I2E skill, inspect another editor's progress, or establish that a pilot passed.
Frozen foundation: empirical-verification-v1.md, SHA-256 5c722c4ac4effd3b7be059d4aced424e5d33aae077f5e32521823e6dd39752fc.

## Decision proposed

For bounded low-risk work with observable acceptance and reliable checks, replace the three default independent Sol audit sessions with one fresh independent Sol verifier. The verifier executes relevant acceptance and adversarial checks and performs focused source and test-quality review. Additional security, test, architecture, or formal specialists are selected by explicit risk and coverage triggers.

This is a proposed change to reviewer counts, not a claim that empirical testing replaces all code judgment. If adopted it requires a separately versioned policy and matching runtime validation; do not claim compliance with the frozen profile's mandatory three-audit rule while executing this reduced route. Repository-specific and user-required gates still apply.

## Preserved role and authority boundaries

- One project manager owns coordination and evidence collection; the tech lead scopes and plans but never implements.
- Workers implement and test within approved scope. Reviewers receive the original intent, accepted tradeoffs, scope, relevant dependencies, source, and evidence, without relying on the author's correctness conclusion.
- Default independent verification uses a fresh Sol session that did not plan, orchestrate, or implement the work. It may inspect shared candidate-bound full-suite evidence and must identify which checks it independently executed.
- Preserve fresh independent Astra exact-plan approval. A manager arranges the challenge/approval; its own participation does not supply independence.
- Preserve named Astra final-review triggers: consequential authorization/tenant changes, destructive migrations, critical financial behavior, uncertain cross-system interactions, material redesign, conflicting reviews, and user/project requirements. Final reviewers exclude all prior contributors and relevant review/escalation participants.
- Preserve failure capture, canonical-case obligations, and Astra diagnosis after two failed repairs of the same defect.
- Retain the selected model settings: GPT-6 Astra / max / Standard; GPT-6.1 Sol and GPT-6.1 Terra / max / Fast. Luna is excluded. Dispatch must verify actual available/effective settings; model names in a prompt are not invocation evidence.
- No per-run budget or budget-approval gate. Review approval does not grant external publishing, merge, or deployment authority.

## Execution graph

1. Intake establishes observable acceptance, business priority, implementation difficulty, technical risk, and allowed actions.
2. Tech lead creates the plan and a verification contract. Independent Astra challenges and approves the exact revision.
3. Manager assigns bounded packages under the selected routing policy; dependencies and writes are isolated.
4. Implementation workers collect applicable baseline checks, meaningful behavioral RED where required, implement, and collect unchanged-test GREEN plus regressions.
5. Deterministic check nodes run the applicable format, lint, type, build, contract, security-scan, and integration checks. These are code tasks and need not each consume an LLM session.
6. The independent verifier exercises the candidate's key acceptance behavior and selected plausible failure cases, checks assertion quality and changed code/dependencies, and records findings and proof limits.
7. Required specialist nodes run against the same frozen candidate. Security triggers are assessed before implementation and reassessed after the diff, not only after a reviewer happens to notice a defect.
8. A delivery gate checks current source/evidence identity, complete findings disposition, review eligibility, all required approvals, and publishing authority. The manager then performs authorized commit/PR operations and reports the actual resulting state.

Failures return to the appropriate worker or to the lead when the plan is wrong. Changed source or verification inputs invalidate affected proof and approvals. A completed agent turn is not task acceptance. Interrupted runs reconcile existing sessions and artifacts before redispatch.

## What routine code-review work is replaced

- Repeated style/format checks: formatter and lint rules.
- Type/interface checks: typechecker, contract tests, and relevant integration checks.
- Speculative behavioral claims: runnable acceptance, regression, negative, property-based, or fault-injection tests where feasible.
- Repeated checking of previously fixed defects: canonical regressions and narrowly justified static rules.
- Repeated narration of test logs: structured receipts bound to the current candidate.

## What focused independent judgment retains

- Whether behavior satisfies the user's actual objective and accepted scope.
- Whether the test oracle, inputs, environment, and assertions cover the important failure modes.
- Whether a patch disables legitimate behavior to satisfy a check, introduces unnecessary complexity, or violates an architectural constraint.
- Source-supported authorization, tenant, secret, data-loss, dependency, and operational risks beyond tool coverage.
- Material decisions when evidence is unavailable, contradictory, or inconclusive.

Every blocking finding needs an affected requirement/risk, concrete evidence, and impact. Accept executed reproductions, relevant deterministic checks, precise source-level arguments, or applicable formal counterexamples. Do not demand unsafe live exploits. Record uncertainty; unsupported preferences are advisory. The implementation worker does not automatically accept every suggestion.

## Eligibility and escalation

Reduced review route requires all of: bounded scope; assessed low risk; observable acceptance; adequate relevant regression coverage; reproducible checks; no mandatory specialist requirement; no unexplained failing or unrun critical check.

- Auth, tenant isolation, secrets, sensitive data, or trust-boundary changes: independent security specialist, in addition to baseline security consideration by the verifier.
- Large behavioral change, weak/ambiguous assertions, concurrency/retry logic, difficult environment reproduction, or unclear regressions: focused test/verification specialist and stronger investigation before completion.
- Critical risk or a required broader review: retain the applicable distinct code/security/test audits. Stronger execution evidence improves those audits instead of removing them.
- Architectural uncertainty or conflicting substantive findings: Astra challenge or diagnosis; apply the existing final-review triggers separately.
- A small diff or low business priority alone never qualifies a task for reduced assurance. A model or worker cannot silently downgrade the route or waive a failed check.

## Proof requirements

Use the frozen empirical proposal's full RED harness manifest and candidate binding. For a regression, show failure on broken behavior and success after repair. For critical new behavior, use targeted mutation or negative controls that test plausible faults; no mandatory unique mutant per test and no universal 100-percent mutation target.

Record commands, outputs, expected outcomes, exit codes, source and harness identities, environment/tool versions, and the identity of the executing actor. Separate execution from inspection of evidence. Shared full-suite evidence may be reused only for the same applicable candidate and verification configuration. Scanners, tests, and reviewers each have limited coverage; no green summary substitutes for the required checks.

Formal checking remains selective as described in the frozen proposal. A model's passing result, its bounds and assumptions, and evidence connecting it to implementation must remain distinguishable. A workflow graph is not itself a formal proof.

## Evaluation and rollout

Phase A: improve empirical evidence while retaining the baseline review counts and model routing. Measure the changed verification method without confounding it with fewer reviewers.
Phase B: on representative bounded low-risk tasks, compare the proposed one-verifier route with baseline audits run in shadow for evaluation. Include real regressions and controlled seeded faults; keep expected fault answers out of reviewer task inputs. Adjudicate disagreements with evidence. Do not use the reduced route to certify old-profile completion.
Track missed/caught defects by severity, unsupported blockers, avoidable rework, independent reviewer effort, overall latency, usage, and upkeep of the test/model infrastructure. Repeated runs and a mix of tasks are needed; one successful pilot proves feasibility only. There is no promised percentage reduction in review effort.

Only adopt the reduced route after evidence supports it and the owner selects the versioned policy. Until then, this is a reviewable proposal. The frozen reference remains unchanged.

## Sources and attribution limits

- Anthropic: https://www.anthropic.com/research/building-effective-agents
- Anthropic: https://www.anthropic.com/research/demystifying-evals-for-ai-agents
- The local frozen empirical-verification-v1.md contains the formal/mutation primary sources and prior artifact findings.

Anthropic's published guidance supports combinations of deterministic, model-based, and human evaluation. It does not establish that this specific I2E reduction is proven safe. The Lauren Tan interpretation is based on the user-supplied Za summary; her exact X exchanges were not independently verified here.
