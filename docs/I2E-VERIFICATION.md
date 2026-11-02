# Updated I2E local verification

Current state: candidate 4 has CODE, SECURITY and TEST scope approval plus a new fresh independent Astra FINAL APPROVE. The accepted profile is installed locally and is the default engineering route for `I2E Mode`. Earlier rejected candidates and failing evidence remain preserved. This document records the updated I2E implementation, separate from the earlier product-memory progress notes.

The [profile](../skills/i2e-team/SKILL.md) implements owner-led planning, Sol 6.1 Max default delivery, P0/Critical Astra ownership, independent Astra exact-plan approval and the seven conditional Astra final-review triggers. It has no per-run budget gate. The [implementation plan](I2E-IMPLEMENTATION-PLAN.md) defines scope and authority; the [learning contract](I2E-LEARNING-CONTRACT.md) defines durable failure reuse and the immediate engineering brief.

## Current evidence

- 141 combined tests pass: 96 runtime tests and 45 installer tests.
- The latest counter regression suite produced 15 intended assertion failures and zero setup errors, then all 96 runtime tests passed with unchanged test bytes. The earlier completion regression and its unchanged-test repair remain separate retained evidence.
- The current 32-command CLI demonstration passes with actual assertion RED, unchanged GREEN, empty-write-scope VERIFY, canonical capture and fresh-process retrieval of a carried case omitted by ranking.
- An independent 58-command installed forward exercise covers real RED/GREEN and post-production VERIFY/CHECK on components unchanged by the counter repair. A current eight-command fresh-process exercise verifies that obsolete support stays blocked and properly qualified active-revision support can resolve the cycle, without editing source.
- Source syntax, skill format and diff hygiene pass. After activation, all six installed payload files match the reviewed manifest, the router has exactly the reviewed default addition, and its other 51 baseline files remain unchanged. Explicit legacy selection is preserved.
- Three separate Sol reviewer sessions approve the exact current CODE, SECURITY and TEST scopes. Their earlier rejected candidates, original counterexamples, repairs and current closures remain retained.
- A new fresh Astra final reviewer approves the exact candidate after 19 focused checks, the retained counterexample replay and fresh-process guards. The earlier Astra rejection remains preserved.
- Actual installed initialization, private record writes and fresh-process retrieval pass using the persistent settings, ledger and existing canonical case store. The bootstrap record is explicitly observational and supplies no fabricated historical work-start or completion certificate.

The release identity is runtime `0494341b84efca48d310a377f63654cc7903e7021d129be808de797dc24c6963`, runtime tests `db6bced02461aa79fc753b05859d9dfb604190b4e4d0808316706dddfad8b30e`, and approved plan `1f654c9fe3845657a49a83543ea1869aa8430f8f038c5c1d670de6a17f37c06f`. Raw manifests, native review responses, commands, failure snapshots and canonical cases remain private outside this checkout.

## Engineering brief

The installer now binds ownership to an installation generation and actual filesystem objects. An earlier byte-only ownership check could act on another installation containing identical files. Private inode anchors and exclusive publication protect the objects the installer may move. Review approvals also bind to the decision active at their historical position; obsolete or unqualified support cannot clear the current stop. The tradeoff is retained recovery data, explicit version checks and a requirement for supported macOS primitives on the same filesystem.

VERIFY gives existing checks an empty source-write scope while findings remain open. Blanket proof deferral allowed ordinary writes too early; demanding completed proof at every start created a repair cycle. The explicit read-only phase lets `VERIFY → CHECK(U) → bounded repair(F)` proceed while unrelated writes and completion stay gated. This adds state and regression tests, and keeps evidence collection separate from permission to change source.

Failure cases continue through the existing canonical helper, while a private ledger records run observations and teaching references. This avoids a competing failure schema. The extra boundary requires durable intent, exact retries and current regression proof. Retrieval carries known digests through ranking misses; a stored lesson remains a proposal until evaluated.

## Limits and publication boundary

Model-shaped receipts inside tests and demonstrations are explicitly synthetic. The actual independent source audits use separate native reviewer sessions. Local helper consistency checks do not authenticate model or human identity, enforce OS write permissions or prove future agent compliance.

The rejected bootstrap attempt and incomplete early replay remain invalid historical evidence. Current source verification does not claim an old-v3 full-profile certificate. The explicitly selected legacy profile and canonical helper remain unchanged. No remote sharing, product-memory corpus import, commit, push, hosted rollout or measured throughput improvement is claimed.
