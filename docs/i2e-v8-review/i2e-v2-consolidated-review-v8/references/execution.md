# Execution

Status: proposed v8 rules. Existing runs keep their recorded profile.

## Intake and controller base

Record the repository and client boundary, original request, instructions, dirty state, allowed actions, acceptance, dependencies, and known cases. Do not change a repository's visibility or branch rules as an intake side effect.

Select an exact controller version. The installed helper, corrected frozen baseline, current source branch, and isolated four-behavior repair are different artifacts. Passing tests in one does not qualify another.

The selected controller must reject false completion and unsupported proof. Verify readiness/reporting, real command receipts, acceptance coverage, current plan/source binding, and lawful narrow repairs. Do not adopt the current light-route branch wholesale as v8.

The controller used to govern a runtime implementation must be fixed independently of the changing candidate. A proposal hash is not that selection.

## Plan contract

Before writes, record an immutable contract with:

- Original objective, ticket IDs, acceptance and required checks.
- Exclusions, allowed actions, release and rollback intent.
- Lane, risk, triggers, contributor identities, and required review.
- Concrete authorized write surfaces and protected exclusions.
- Dependencies, test areas, relevant callers, and interaction obligations.
- Batch membership and any explicitly detachable tickets.
- Current source/base and the governing instruction/profile identity.

Standard and Critical require fresh Astra approval of this exact revision. Direct requires the inline contract and authority record, but omits that independent plan approval.

The contract describes what changes are allowed. A separate expected-file list helps planning and parallel ownership. It is not permission to edit everything in the repository.

Before adding an unlisted file, the worker records it in the actual-write manifest. The coordinator checks that its resolved path is inside the approved surface and outside protected exclusions. Check overlapping ownership, callers, dependencies, risk, tests, and authority before the write.

No new plan approval is needed when those obligations and the immutable contract are unchanged. Refresh affected proof. If an addition changes a dependency, protected surface, risk, acceptance, authority, or other contract term, stop dependent writes and obtain a revised contract and required approval. Disclosure after editing is not authorization.

This is a new contract model. The existing literal-file scope schema cannot implement it through a prompt exception. Its runtime representation and migration require tests.

## Ordered phases

VERIFY has no source-write permission. It collects checks on the existing candidate.

TEST_ONLY changes the approved test area while production bytes remain unchanged. Preserve a meaningful behavioral assertion failure and its full harness identity.

PRODUCTION changes approved production files. The RED test bytes stay fixed for the corresponding GREEN result. Changing those tests starts a new authorized test cycle and invalidates affected proof.

Direct uses these semantics too. Its smaller plan route is not a behavioral-test waiver. Nonbehavior changes use proportionate checks without fabricating RED.

Inspect actual preflight results before their dependent actions. A later approval cannot authorize an earlier edit. VERIFY cannot close an unfinished test or production cycle. Bounded remediation may defer only its named failed obligations; it retains all unrelated prerequisites.

An approved write surface does not authorize test edits during PRODUCTION. The actual-write manifest, test identity, and phase guard remain explicit.

## Batches

Decomposed requests use batches with at most five bounded tickets. A single ticket is a batch of one. Do not wait to fill five. Count logical accepted tickets, not files, commits, or tool calls.

Use compatible tickets with coherent dependencies and rollback. Runtime code checks unique IDs, membership, count, and mappings. The existing independent reviewer checks the actual diff against the original request. This adds no separate scope-review role.

Preserve per-ticket checks and applicable RED/GREEN. Test the combined candidate and interactions. One failed ticket holds that batch until repair or a valid split.

A plan may explicitly delegate removal of named independent tickets. Its approved contract retains the full request and defines the permitted nonempty candidate subsets. Record the current subset in a versioned membership manifest; do not rewrite the approved contract. The lead may use that delegation without another full approval only if:

1. Remaining acceptance, authority, lane, risk, and write boundaries are unchanged.
2. No remaining ticket depends on the removed work, its checks, or its rollback behavior.
3. Removed code is absent from the candidate, and remaining interactions are rechecked.
4. Findings, cases, repair counts, and the removed ticket remain linked to explicit continuation work.
5. The delivery scope permits the subset. The original parent request remains incomplete.

Record the decision and new candidate membership. An unplanned removal or failed condition requires a revised plan and its required approval. The rule does not permit silent cancellation or a false parent completion.

A dependent local batch starts from an exact accepted predecessor commit. Retain its acceptance receipt and unresolved inherited obligations. Review the new delta against that base. A changed or superseded predecessor invalidates affected proof.

For later GitHub delivery, merge predecessors first. Reconcile the dependent branch against the real target and refresh affected proof. Its delivery diff cannot hide unmerged predecessor tickets. Stacked-PR automation is outside the first implementation.

## State and orchestration

Use the existing ledger for append-only events, immutable evidence references, expected-sequence updates, and one current attempt identity per ticket. Use a small policy evaluator. Derive readiness from required obligations.

The useful states are DRAFT, PLAN_REVIEW, READY, RUNNING, VERIFYING, ACCEPTED_LOCAL, DELIVERING, DELIVERED, REWORK, HOLD, FAILED, and CANCELLED. A repair, withdrawal, or relevant source change can revoke readiness. Evidence states such as UNKNOWN and NOT_RUN are separate.

One default worker keeps the first implementation small. Parallel workers require compatible ownership and a validated write mode. A coordinator restart reconciles existing attempts, artifacts, and external results before redispatch. An expired or revoked attempt cannot submit newly accepted output.

A terminal model turn is not task completion. Technical readiness precedes the completion report. The brief and final consistency result must agree with the actual candidate and remaining obligations.
