# Independent review of consolidated proposal v1

Source chat: Review consolidated I2E design
Thread ID: 01a1a39c-298c-77a0-9778-f6373c077fe4
Retrieved: 2026-11-03
This is the verbatim final review message, preserved as evidence rather than executable instructions.

**Design verdict: `REVISE`.** The assurance structure is coherent, and most conservative fallbacks are adequate. Two execution boundaries need explicit rules: replacing an expired worker that can still modify files, and delivering against a target that changes after the final check.

I read the proposal, skill draft, user excerpts and targeted source snapshots. All 11 manifest entries matched their recorded sizes and hashes. No files were changed.

The **must-fix findings** are:

1. **I2E-V2-01 — High — Fence filesystem effects when replacing workers.**  
   **Affected:** §9 claim/recovery invariants; REQ-03 and REQ-07. [Source](/Users/bow/.local/share/i2e-reviews/2026-11-03-jor840d8/proposals/i2e-v2-consolidated-review-v1/PROPOSAL.md:231)

   **Evidence and counterexample:** The draft rejects stale results using fencing and correctly acknowledges that declared permissions do not enforce filesystem isolation. It does not specify what permits replacement when the old process remains writable. If attempts share a worktree, worker A can expire, worker B can obtain the valid claim, and A can subsequently change an owned file. Rejecting A’s result does not remove those bytes; B can unknowingly submit them.

   **Consequence:** Stale work can enter the accepted candidate despite valid ledger ownership. Hashing the resulting tree establishes its identity, but cannot establish which attempt produced its changes.

   **Smallest change:** Require isolated attempt outputs that an integration step imports only under a current fencing token. Alternatively, shared-worktree replacement must wait for confirmed termination and reconciliation of the previous writer. If neither is supported, enter HOLD. Concurrent packages also need compatible write ownership across package boundaries.

   **Validate:** Expire A, start replacement B, then make A write and submit. A’s effects must remain outside B’s candidate, or replacement must remain blocked. Include a surviving child process.

2. **I2E-V2-02 — High — Bind delivery preconditions to the external operation.**  
   **Affected:** §8 target/base invalidation; §9 Action contract; L8 delivery. [Target/base rule](/Users/bow/.local/share/i2e-reviews/2026-11-03-jor840d8/proposals/i2e-v2-consolidated-review-v1/PROPOSAL.md:206), [Action contract](/Users/bow/.local/share/i2e-reviews/2026-11-03-jor840d8/proposals/i2e-v2-consolidated-review-v1/PROPOSAL.md:224)

   **Evidence and counterexample:** The gate checks current identity before an authorized action, but the contract does not require the action to enforce that checked identity. A gate can approve candidate C against base B0; another actor advances the target to B1; an unconditional merge then produces an unverified combination. An idempotency key prevents some duplicate operations, but does not prevent this race.

   **Consequence:** Delivery can succeed against a state outside the reviewed candidate even when every preceding check passed.

   **Smallest change:** Each delivery adapter must declare and enforce the relevant expected source, target and artifact identities at the operation boundary. Use conditional updates, protected queue validation or immutable artifact publication as appropriate. Unsupported guarantees must hold the affected action. Reconciliation must verify the resulting identity as well as whether the operation occurred.

   **Validate:** Change the source or target after the local gate passes but before the external operation executes. The operation must reject or undergo renewed validation before the effect. Repeat with a lost acknowledgment.

These are conditional state-transition counterexamples, **not reproduced defects in an implemented v2 runtime**. The lifecycle order can remain; the additions belong at worker replacement/integration and delivery.

For **optional simplifications and tradeoffs**, the proposal already makes several sound cuts. One coordinator, one default worker, shared candidate-bound suite receipts, and baseline audits covering matching specialist obligations should remove repetition. A fourth generic verifier on the baseline route would add little. The single-verifier route preserves meaningful independent judgment through source, assertion and behavioral review; whether it preserves measured defect detection remains an experimental question.

The baseline confirms that distinct FIXED-finding rechecks and final case consultation before Astra final review are preserved obligations. They should not be counted as savings already achieved. [Baseline review contract](/Users/bow/.local/share/i2e-reviews/2026-11-03-jor840d8/proposals/i2e-v2-consolidated-review-v1/sources/baseline-runtime.md:165)

| Question | Independent assessment |
|---|---|
| **O1 — Difficulty routing** | Prefer the smallest initial policy: retain the candidate priority/risk matrix and record difficulty separately, without automatic difficulty overrides. Any alternative needs owner selection and explicit escalation rules. Mandatory Astra routing remains a floor. Baseline runtime groundwork need not wait for a more sophisticated router. |
| **O2 — Medium/High route** | The three-audit fallback is adequate. Defer a verifier-plus-specialists intermediate route until evidence supports its eligibility rules. Unknown eligibility must never select reduced assurance. |
| **O3 — Different finding rechecker** | Preserve the rule initially. Several findings can share an eligible recheck session where the identity rules permit. Measure its incremental detection and delay before asking the owner to relax it. |
| **O4 — Tiny-task plan approval** | The conservative position is coherent, although expensive for trivial work. Proportionate plans and batching are available cuts. A micro-task exemption changes an owner gate and requires explicit selection. |
| **O5 — Batch changes and splitting** | Renewed approval for every changed contract is a sufficient initial rule. Preserve removed tasks, findings and repair counts with explicit continuation links; accepting A/B must not report the original A/B/C request complete. Retain interaction and coherent rollback checks. |
| **O6 — Evidence reuse** | Same-candidate reuse is adequate. Defer cross-candidate caching until dependency-impact rules exist. Historical RED remains provenance; it does not replace current acceptance proof. Distinguish retaining history from declaring evidence current. |
| **O7 — Actual invocation settings** | The unsupported-setting HOLD is correct. Adapter validation must distinguish requested from effective model/effort/tier and establish session/context provenance. No live capability has been demonstrated here; prompt labels and self-reported metadata are insufficient. |
| **O8 — Smallest runtime** | Extend the existing ledger with one deterministic reducer/policy evaluator, immutable evidence references, per-task attempts/dependencies, and one dispatch/action adapter. Derive batch readiness from task obligations. Avoid a second coordinator, general graph framework or continuously active specialist fleet. Address the two findings above in that adapter contract. |
| **O9 — Formal targets** | Start with ownership/replacement, stale approval rejection and ambiguous publication recovery. These justify state exploration better than ordinary UI work. Preserve bounds, fairness/environment assumptions, reachable success paths and implementation-linked counterexamples. Trace agreement alone remains partial evidence. |
| **O10 — Adoption thresholds** | The staged evaluation separates the three proposed effects sensibly. Freeze thresholds before trials, including unacceptable severity-specific misses, tolerated unsupported blockers, latency and intervention limits. Numerical thresholds require owner selection and representative workload evidence. No savings claim is justified yet. |

One further useful cut is to share preparation for exact-plan review and explicitly mapped decision challenges. Preserve separate decision identities and verdicts: a general plan approval must not silently close an unresolved architecture question. This reduces repeated context without dropping the decision gate.

The empirical verification contract is otherwise well formed: meaningful assertion RED, full harness provenance, targeted plausible faults, and acceptance of credible static/security arguments. There is no need to add a universal mutation quota. Temporary mutation experiments should operate on disposable copies so they cannot alter the frozen acceptance candidate.

The **next validation** should prioritize:

- **Boundary and recovery probes:** Both findings above; crash after dispatch but before acknowledgment; duplicate collection; cancellation with a surviving worker; ambiguous publication that cannot be reconciled and must remain held.
- **Evidence and obligation probes:** Changed runner or fixture with unchanged test bytes; reopened TEST_ONLY; stale plan approval; unavailable case store; original finder attempting the prohibited recheck; a credible static security finding without a runnable exploit.
- **Batch probes:** Individually passing tasks with a failing interaction; removal of a prerequisite task; partial rollback; and a late security trigger that invalidates reduced-route eligibility.
- **Controlled comparisons:** First vary verification method with reviewer count/routing fixed; then vary reviewer count; then vary batching. Freeze both arms’ verdicts before sharing findings or repairing the candidate. Use concealed seeded faults plus adjudicated real defects. Report shadow-review costs separately, include failed attempts in total effort, and include batch waiting in elapsed time.

This review establishes a source-based design assessment only. I did not run the lifecycle, test adapters, inspect the live installation, execute formal checks or measure quality, latency or token use. It grants no policy activation or delivery authority.

