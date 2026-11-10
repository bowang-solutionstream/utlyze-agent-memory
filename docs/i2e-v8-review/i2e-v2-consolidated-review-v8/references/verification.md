# Verification and learning

Status: proposed v8 rules.

## Evidence

Behavioral RED must fail on the intended assertion. Import, syntax, setup, and fixture errors are not behavioral RED. GREEN uses the same test bytes. Preserve source, test, runner, configuration, fixtures, dependencies, tool versions, command, output, and exit status.

Each acceptance criterion maps to an executed result. A generic successful command cannot establish aggregate coverage. Check the required acceptance IDs against the results actually produced.

Use targeted negative controls for important new behavior. Run destructive or mutation probes on disposable copies. Preserve the accepted candidate. No per-test mutation quota or universal mutation score is required.

Reuse applicable suite evidence for the same candidate and setup. Refresh affected evidence after source, base, dependency, harness, instruction, or profile changes. Different file names do not prove that behavior is independent.

Reviewers execute the key acceptance and selected failure cases themselves. They also inspect assertions, changed code, callers, and relevant dependencies. Distinguish EXECUTED from INSPECTED in the report. Shared suite receipts do not replace that targeted independent work.

Precise source or security evidence can support a finding when execution would be unsafe. Say what the evidence proves and what it does not.

## Decisions and review

Non-trivial decisions receive an independent challenge before dependent work. A meaningful RED may challenge its mapped ordinary behavioral claim. Significant architecture or Critical questions require Astra.

One plan-review preparation packet may serve both plan approval and mapped decision challenges. Each decision still needs its identity and verdict. General approval cannot silently resolve an unexamined architecture question. Direct omits separate plan approval, not a required decision challenge.

The independent verifier did not plan, coordinate, or implement the candidate. Baseline code, security, and test auditors are distinct eligible sessions. Apply the final-review exclusions in the policy reference.

Review findings need a stable ID, affected requirement, evidence, consequence, smallest correction, and validation. No-findings is valid. Do not invent issues to meet a quota.

High means serious harm to an essential workflow, security, integrity, or reliability. Medium means a concrete defect or maintenance problem with material bounded impact. Low is optional polish or preference without demonstrated material harm.

Record incidental Low observations compactly in existing artifacts: key, location, reason, and revisit trigger. Keep them out of routine repair loops. No new backlog, scheduled sweep, or mandatory cleanup follows. New evidence can promote an observation with its history intact. Required failures and prior obligations cannot disappear through relabeling.

FIXED actionable findings retain current passing proof and a Sol rechecker distinct from contributors and the original finder. One eligible session can recheck several findings. Allowing the original finder to close the fix remains deferred until comparison evidence and owner selection support it.

Empty later reviews do not erase older findings. NOT_APPLICABLE needs evidence. Material risk acceptance needs the actual human decision tied to the finding and candidate.

## Failure boundary

Save the first failing command's output, exit, command, and relevant broken-source/harness identity before any correction. Use the existing evidence store. Preserve enough bytes or a durable snapshot to reproduce the failure; a hash without recoverable content is insufficient.

Create a canonical case before repairing:

- An unexpected acceptance or regression failure.
- A substantive business-logic, security, integrity, or reliability defect, even during implementation.
- A failed repair of a known defect.
- A routine iteration problem that persists after one attempted correction.

Expected behavioral RED stays separate. An isolated syntax or setup error without an observed acceptance, regression, or material-risk failure may remain a compact iteration event. If impact is uncertain, investigate and use canonical capture when a real defect cannot be excluded. This proposed boundary cannot be retroactively applied to erase existing cases.

Keep the canonical helper and schema. Consult cases before planning, each canonical-defect repair, and final acceptance. Carry known cases and applicable regression obligations regardless of search ranking. A missing lookup or saturated search is a gap.

The controller must preserve the first iteration record when a problem becomes a canonical defect. Two failed repairs of one stable defect require Astra diagnosis before a third. Three unresolved substantive cycles of one decision stop dependent work and surface the decision to the owner. Do not reset counts through a new ticket or agent.

## Final acceptance and learning

Resolve findings, required specialist work, and final case regressions before required Astra final review. The final reviewer assesses the current candidate, prior dispositions, remaining uncertainty, and whether all intended behavior can succeed.

The final gate checks current proof, approvals, independence, complete findings, authority, and accurate status. A structural PASS alone is insufficient.

Return a brief account of the problem, decision, actual result, tradeoff, proof limits, and one useful engineering lesson. Do not invent alternatives or learner understanding.

Record useful maintainability observations even when tests pass. Prefer a local correction or deterministic check before a broad new rule. Compare a proposed reusable rule against motivating and held-out cases, including legitimate behavior it might block.

Adopt, narrow, consolidate, retire, or defer a rule through existing review and authority. Preserve history and still-applicable requirements. Retiring obsolete risk needs no replacement rule. A pending lesson does not block the original task unless it is also a material finding.
