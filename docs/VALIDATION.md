# Validation of the preserved prototype

This is a sanitized summary of local execution evidence, not a replacement for the private raw receipts. Evidence was produced on 2026-10-30; source identity was rechecked for publication on 2026-11-06.

## Exact binding

- Original candidate SHA-256: `dddbcd1508c37d6296c76fb4ec55c00184c1ef84db134957a3590c754bbb3209`.
- Original instruction binding: `0cd5d279ceccbec6a14f1164df4fdc9ee676ed5546fd7fa8ee75dbaf06313d17`.
- Plan SHA-256: `36f58fc2fc8c5942f770a15984ac1061ab0c51f9633b25f5bcfd8af1bd77de8f`.
- Frozen specialist input SHA-256: `f17a7591e35041b2f68b61a7025dd60259766cb22b51d1506290511a34d66ad1`.
- Per-file identities: [SOURCE-MANIFEST.json](SOURCE-MANIFEST.json).

The candidate identity belongs to the original local worktree, including its instruction binding. It is not the Git commit ID of this separate publication repository. The original source HEAD was an empty application metadata baseline; the implementation was reviewed from the actual working files, including untracked files. Publication preserves those source bytes without rewriting that local evidence history.

## Executed checks

The original 18 acceptance tests passed. They cover fresh-process retrieval; objective/feature/task links; scope separation; exact history, idempotency and revision races; conflicts and withdrawal; source drift and unsafe paths; strict input; bounded context; observations and feedback; inert proposals; canonical failure lookup including drafts/carried cases; concurrent writes; and actual process-kill transaction rollback.

Two additional unchanged regression tests passed after intended failing assertions reproduced independently identified defects: overflow lost local regression-obligation metadata, and historical task context failed to make a current withdrawal visible. The repaired source keeps exact recovery IDs and separates historical facts from current lifecycle state. The retained total is **20 passing tests**, from the original suite plus the two regression tests.

A 12-step CLI demonstration retained actual subprocess arguments, input, output, error output and exit codes. Extended checks exercised exact transitive task revisions; symlink, hardlink, nonregular, oversized and changed evidence; duplicate/nonfinite JSON and UTF-8 byte limits; canonical scope/shape/digest validation; exact carried-case recovery after search failure; monotonic regression obligations; and refusal of incompatible database schemas.

The skill format validator and a relocated-source launcher exercise passed. The relocation check used a source copy on the same Mac, not a fresh Git clone or another platform. The standalone core works without canonical case integration; the optional adapter depends on the existing installed helper, store and documented Mac paths.

An independent Sol Max skill exercise made 14 CLI calls and exactly three authorized synthetic appends: an episode, retrieval feedback and an inert lesson proposal. Fresh reads recovered the appended data; original records and source were unchanged. Adversarial stored text did not create its requested marker. Product truth and measured improvement remained unproven. This exercise does not establish production retrieval quality or resistance to every prompt-injection attempt.

The final pre-audit seal verified 134 retained evidence references, 13 shown canonical cases, unchanged original/regression test bytes and the frozen source binding. Those reference checks establish the observed file identities, not the truth of every claim inside them.

## Review state

| Review | Result on frozen source |
| --- | --- |
| D1: persistence, provenance and authority decisions | PASS; no unresolved source finding in its scope |
| D2: bounded retrieval, exact history and failure obligations | PASS; both retained retrieval findings resolved |
| D3: skill behavior and scope, with forward exercise | No material doubt; forward exercise PASS |
| Independent code review | No completed report available |
| Independent security audit | No completed report available |
| Independent test/coverage audit | No completed report available |
| Separate independent Astra Max final review | Not completed |

Doubt reviewers were separate from authors and plan contributors. They are not substitutes for the three required specialist sessions. The previous session stopped at a service usage limit; absence of a completed report is not an approval or proof that no defect remains.

## Known proof limits

The earliest greenfield RED attempt did not reach the intended behavioral assertion and was superseded, with the original retained. Subsequent intended-assertion RED and unchanged-test GREEN evidence is preserved; not every early failed command is described as useful TDD proof.

A proportional README/skill wording clarification cannot be encoded as a per-work nonbehavioral exception in the installed native-v2 behavioral task record. Its historical preflight/current-before-write review is absent and has not been backdated. Current source proof and review records remain useful, but no canonical full-profile completion pass is claimed.

No real product knowledge corpus was used. There is no measured comparison with Gbrain/Mem0, no measured token or latency saving, no demonstrated reduction in recurring defects, no automatic learning/promotion, and no production or multi-user security certificate.
