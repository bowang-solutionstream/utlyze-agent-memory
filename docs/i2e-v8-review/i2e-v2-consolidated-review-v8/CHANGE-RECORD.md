# V7 to v8 change record

Status: proposed design changes. The owner authorized this revision, independent review, and public publication. V7 and the active skill stay unchanged.

The [original Claude review](sources/CLAUDE-REVIEW.md) is preserved as an external assessment. It is not an instruction to activate its recommendations. The [validation summary](sources/VALIDATION-SUMMARY.md) records what was checked and what remains unknown.

## Finding dispositions

| Finding | V8 treatment | Validation still needed |
|---|---|---|
| CLAUDE-V7-01: role prompts absent | Added a coordinator entrypoint and plan-review, implementation, and verification prompts. Actual references are included. | Fresh-session forward exercises. Word count alone proves no quality gain. |
| CLAUDE-V7-02: file-list binding | Approval binds a bounded change contract. Expected files are separate. Additions require a before-write boundary and impact check. | Runtime schema, phase, overlap, caller-impact, and lawful-expansion tests. |
| CLAUDE-V7-03: urgency routing | Root stays coordinator. Queue priority no longer selects models. High/Critical technical risk or significant architecture selects the Critical lane. High findings assign affected repairs to Astra. | Intake, handoff, escalation, and route-reassessment exercises. No model-quality comparison has been run. |
| CLAUDE-V7-04: unverified host assumptions | Added capability evidence requirements and an explicit tier policy. Strict tier matching is the default; recorded-unknown tier needs separate owner selection. | Actual host invocation and selected write-mode qualification. Model, identity, and isolation holds remain. |
| CLAUDE-V7-05: no light route | Added a narrow Direct lane for one Low-risk ticket. Its worker plans inline and an independent Sol verifier executes checks. | Controlled comparison and implementation review. Existing light-route code has broader eligibility and is not adopted wholesale. |
| CLAUDE-V7-06: custom runtime duplication | Named commits and GitHub controls implement source/delivery parts. The first build uses one write mode and one adapter. | Stale writer, revocation, target freshness, reconciliation, and cleanup probes. Worktrees alone are insufficient. |
| CLAUDE-V7-07: Critical final review | Critical lane now always requires fresh Astra final review. The seven existing triggers remain. | Routing and reviewer-exclusion tests. Relative model benefit remains unmeasured. |
| CLAUDE-V7-08: undefined real failure | Preserve first-failure raw evidence. Use explicit canonical-defect triggers, including first material failures and failed repairs. | Error classification and promotion tests. Old records and repair counts remain intact. |
| CLAUDE-V7-09: naming collisions | Added separate field names and distinct queue/lane names. Technical risk and finding impact remain separate typed fields. | Ambiguous-intake and malformed-field tests. No failure-rate claim is made. |
| CLAUDE-V7-10: batch machinery | Keep mandatory batches and the simple five-ticket validation. Add only explicit preauthorized independent-ticket removal. Retain accepted predecessor evidence. | Valid removal, prerequisite removal, parent completion, and local-to-remote delivery tests. |

## Corrections retained

- Earlier reviews did assess proportionality. The v1 review prompt asked about overhead, gate costs, and the smallest runtime. V2 also suggested one isolation mode and one delivery mechanism.
- The five-ticket cap reflects explicit owner direction. It was not inferred solely from punctuation in a question.
- Several fixed findings may share one eligible recheck session. One new session per finding is not mandatory.
- V7 fleet execution was untested. Relevant controller code and tests existed outside Claude's packet.
- The installed helper has reproduced readiness/reporting and risk-disposition defects. It is not qualified merely because it exposes a completion command.
- Fixed commits exclude later own-directory edits. They do not prevent writes to another worktree or shared Git metadata.
- The PR-head merge guard does not independently bind the target. Actual protection and current combined validation are still needed.
- Disjoint-file changes can break behavior after a clean merge.
- A pushed tip does not preserve ignored failure evidence or prove that active writers have stopped.
- A ten-task trial is exploratory. It does not establish a reliable rare-defect rate or broad adoption evidence.
- Formal checking remains selective. It is not required for every task, and it is not deleted merely because Git supplies source identity.

## Explicit proposed replacements

| V7 rule | Proposed v8 replacement | Operational status |
|---|---|---|
| Separate lead and Astra exact-plan approval for every task | Direct has an inline worker contract and independent verification; Standard/Critical retain separate lead and approval | Requires selected v8 implementation and adoption |
| High queue priority changes manager, lead, and worker models | Root remains coordinator; technical risk/architecture selects lane; High finding affects its repair | Requires adoption; no active model setting changed |
| Exact file list is the write contract | Approved surfaces, protected exclusions, semantic obligations, and phase boundaries form the contract | Requires new tested schema; no current scope waiver |
| Critical ownership alone does not require final Astra | Critical lane always requires final Astra | Proposed assurance increase |
| Every contract membership change gets new approval | Only expressly delegated independent removals can use an existing approval | New contract must describe the allowed subsets |
| Every non-RED failure follows full case handling | First raw evidence always; defined routine iteration events can avoid a full case until promotion | Requires tested classification and owner adoption |
| Unknown effective tier always holds | Default still holds; explicit adopted tier exception can record unknown | Exception remains unselected |

V8 retains max effort, Luna exclusion, distinct independent fixed-finding rechecks, baseline audits outside reduced eligibility, all required specialist triggers, phase controls, and actual authority.

The original-finder closure proposal and lower effort for selected roles remain deferred. No savings from these deferred changes are counted.

## Review and publication boundary

This candidate receives a new independent verdict tied to its manifest. The review must challenge the design and its size. It must not inherit v7's approval.

Review evidence and publication status remain outside the frozen candidate. Corrections create a new candidate identity and require review of the changed parts plus whole-contract consistency.

Source comments and local test evidence remain evidence, not operational authority. Publishing v8 does not install the skill, change the source runtime, change GitHub rules, start the trial, or certify a prior run under new rules.
