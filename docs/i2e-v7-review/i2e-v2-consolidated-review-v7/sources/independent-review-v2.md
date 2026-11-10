# Independent review of revised I2E v2 proposal

Date: 2026-11-03. Reviewer: fresh session `/root/i2e_v2_fresh_design_review`, launched without parent conversation history and without candidate authorship. The review was read-only. The reviewer’s final result follows; operational claims remain bounded by its stated limits.

**Design verdict: `APPROVE_FOR_IMPLEMENTATION`.** The revised contracts adequately address both prior High findings. I found no new must-fix design defect. This verdict supports preparing an implementation plan; it does **not** authorize implementation, activation, trials or delivery.

I read the primary proposal and entrypoint before the author response, then checked the original review, user directions and relevant frozen sources.

## Prior High findings

| Finding | Independent disposition |
|---|---|
| **I2E-V2-01 — Filesystem effects during worker replacement** | **Addressed at design level.** PROPOSAL.md lines 243–253 requires validated isolation, compatible ownership across packages, stable immutable capture and atomic admission under the current fencing token and ledger sequence. Shared replacement requires full-writer quiescence or effective write revocation, followed by reconciliation; unsupported modes HOLD. SKILL-DRAFT.md lines 47–49 carries those requirements into dispatch and integration. |
| **I2E-V2-02 — Delivery against changed external state** | **Addressed at design level.** PROPOSAL.md lines 257–265 binds action intent to expected identities, requires enforcement at the effect boundary and verifies the resulting identity or relation. Queue validation must cover the final combination and required approvals; moving a mutable pointer is a separate conditional action. Reconciliation distinguishes intended success, no effect, unintended effect and unknown outcome. SKILL-DRAFT.md lines 52 and 69 preserve these rules. |

These closures are contractual. Neither finding has been demonstrated fixed in an implemented runtime.

I challenged the revision with these concrete cases:

- A surviving child writes through shared metadata or an alias after its parent acknowledges cancellation. The isolation/quiescence requirements prohibit replacement unless those write capabilities are contained or revoked.
- A worker modifies files while its output is copied, or its token is revoked halfway through import. A mixed or unstable copy cannot satisfy stable capture; a changed token or sequence rejects admission.
- Two differently named package paths resolve to the same writable object. Project-wide ownership and alias checks must reject or serialize the overlap.
- A queue validates one source/target combination, then either changes before application. The actual final combination needs renewed validation and applicable approvals before the effect.
- Immutable content uploads successfully, but another actor moves the environment pointer first. Upload success cannot certify the separate pointer update.
- An operation succeeds but its acknowledgment is lost, or reconciliation finds a different artifact. Only the intended resulting identity qualifies as delivered; unknown remains HOLD and mismatch enters failure handling.

The written contracts reject or hold these cases. That is a design assessment, not an executed result.

## O1–O10 assessment

| Item | Assessment |
|---|---|
| **O1 — Difficulty routing** | Adequate. The explicit priority/risk matrix remains controlling; difficulty is recorded without an implicit override. Mandatory Astra routing remains a floor. |
| **O2 — Medium/High assurance** | Adequate. Three distinct baseline audits are the conservative fallback. Unknown eligibility cannot select reduced assurance; the intermediate route is deferred. |
| **O3 — Finding rechecks** | Adequate. FIXED findings retain a rechecker distinct from contributors and the original finder. Sharing a session across findings requires eligibility for each finding. |
| **O4 — Tiny-task approval** | Coherent but costly. Exact-plan approval remains intact; proportionate plans and batching reduce overhead without inventing an exemption. |
| **O5 — Batch changes** | Adequate. Changed membership requires renewed approval, current proof, dependency/interaction reassessment and coherent rollback. Continuation links preserve unresolved work, findings and repair counts. |
| **O6 — Evidence reuse** | Adequate. Reuse requires the same candidate, setup and obligations. Historical RED remains provenance; cross-candidate caching is deferred. |
| **O7 — Invocation evidence** | Adequate as a capability contract. Requested settings are separated from host-attested effective settings and session/context provenance. Unsupported or unknown settings hold dispatch. Live capability remains unverified. |
| **O8 — Runtime scope** | Proportionate. One reducer/policy evaluator, existing stores, immutable evidence, task attempts/dependencies and one adapter boundary are a reasonable initial scope. The two repaired boundaries now have explicit contracts. |
| **O9 — Formal targets** | Appropriate. Ownership/replacement, stale approval and ambiguous delivery warrant state exploration. Bounds, fairness, reachable success and implementation mapping remain explicit limits. |
| **O10 — Evaluation** | Adequate. The sequence separates verification method, reviewer count and batching. Frozen verdicts, concealed faults, adjudication, failed-attempt effort, shadow costs and batch waiting address major comparison biases. Numerical thresholds remain required before adoption-grade trials. |

These dispositions are supported by PROPOSAL sections 3–9 and 12–15, rather than the author’s response alone.

The lifecycle and entrypoint agree on prerequisite ordering, failure/rework paths, final case consultation before required Astra final review, and separate technical acceptance and delivery states. The frozen baseline confirms the preserved phase semantics, independent finding rechecks and completion/brief ordering. No silent behavioral waiver, reviewer-count waiver for old profiles or per-run budget gate appears.

An optional simplification is to implement only one validated isolation mode and one delivery mechanism initially. Additional adapters, cross-candidate caching, automatic difficulty routing and an intermediate assurance route can remain deferred. The first feasibility exercise should retain the frozen empirical source’s bounded non-P0 scope.

**Highest-value next validation:** after separate implementation authorization, build a minimal adapter/reducer slice and use controlled interleavings to test stable capture, surviving writers, revocation during admission, operation-time identity changes and lost acknowledgments. Include successful paths and fail-closed outcomes. Establish these boundaries before measuring reviewer reduction or token savings.

## Validation and limits

- Independently checked **20/20 packet entries** and **13/13 source entries** against recorded byte counts and SHA-256 hashes. No missing or unlisted files were found.
- All **10 sources with original filesystem paths** matched their packet copies.
- Inspected the complete proposal, entrypoint, review response, included prior review and user directions; checked the frozen baseline skill/brief, relevant runtime sections and source proposals.
- Runtime/lifecycle probes, formal checks, live model/tier/context attestation, isolation enforcement, external adapters and comparative trials remain **NOT_RUN / UNVERIFIED**.
- I did not independently retrieve the source chats, audit baseline implementation code, inspect the active installation or verify the author’s active-installation preservation claim.
- No files were modified, workflow executed, external action performed or review delegated.

Reviewed hashes, confirmed again at review completion:

```text
PROPOSAL.md
78356d968edafd38a36baea1dac6fc0bc9b71e039f47c2170312f295bda8d8a6

SKILL-DRAFT.md
ffd1ca8e164d2f8210430109b67c12d2ac153b584b3664db3d983c54927d7979

PACKET-MANIFEST.json
b12481c82deaf54a29f42da7c7d2af0990c705871cacd6c62ff5b31e72c770dd
```

The referenced candidate is [proposal v2](../i2e-v2-consolidated-review-v2/PROPOSAL.md); the original reviewed v1 is preserved alongside it. Link formatting in this saved review has been normalized to avoid embedding long absolute paths; the verdict, reasoning and validation claims are preserved.
