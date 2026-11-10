# Worker handoff, delivery, and cleanup

Status: proposed v8 rules. The first implementation supports one tested worker-write mode and one GitHub route.

## Worker output

Use a named commit as the source handoff. Record repository, task, plan, current attempt, parent/base, commit, test/harness identity, and required proof. A branch name or worker-writable directory is not the handoff identity.

A fixed commit excludes later edits to that worker's directory. It does not establish authority, current-attempt validity, or isolation. Git worktrees share metadata and do not prevent same-user writes to other paths.

Qualify one of these modes before operational dispatch:

- Validated per-attempt write containment excludes other attempts, integration outputs, immutable evidence, shared metadata, and writable aliases.
- Serial execution permits replacement only after the whole prior writer tree is stopped or its writes are effectively revoked. Reconcile its changes and preserve evidence before the replacement starts.

A cancellation response, parent exit, or completed model turn alone does not prove quiescence. A surviving child is a writer. Unsupported modes HOLD dependent dispatch. Do not reset unknown changes to make the mode appear clean.

Use one integration executor. Import only output from a currently authorized attempt and its accepted dependency versions. Stage the named commit and check scope, provenance, and the current attempt generation. Admit it using the ledger's expected sequence. A revocation during staging rejects admission.

Integration edits create a new candidate. Run checks against that actual combination in the qualified write mode. A changing worktree cannot supply a frozen-candidate proof claim.

This uses Git objects and the existing ledger. It does not require a general lease service, distributed scheduler, or another artifact database.

## GitHub route

Each project identifies its code repository, target branch, permitted actions, and required checks. Use one PR per accepted batch. Ticket-linked commits preserve source traces; each intermediate commit does not require a full audit.

Map original worker commits to the integrated candidate. Bind review and checks to the final head plus the applicable base, harness, configuration, and dependencies.

Before relying on GitHub, verify the actual target rules. The route needs required checks from the expected producer, current-target validation, current review/approval evidence, and a defined bypass policy for the acting account. Being an administrator does not justify bypass.

Use strict up-to-date checks or another supported mechanism that validates the actual combined candidate at merge time. The adapter must show how the mechanism binds source and target. A prior local read is insufficient.

Use `gh pr merge --match-head-commit <reviewed-head>` or the equivalent conditional head mechanism. This flag checks the PR head only. It does not independently bind the target. Do not call `--admin` to skip required controls.

On a new head or target, refresh affected checks and review based on semantic dependency impact. A conflict always needs review of the resolution. A clean merge with disjoint files can still invalidate acceptance. Never use file overlap as the sole freshness test.

GitHub checks do not authenticate model-session independence. A required check must validate the applicable execution and review receipts. It must not report success when required acceptance was skipped or missing.

The adapter validates action authority at the effect boundary. After merge, read the resulting commit and verify the approved source/target relation. Squash and rebase require a supported relation and retained original commit/diff mapping.

## Timeouts and other targets

Record operation intent before sending it. After a lost acknowledgment, reconcile both occurrence and exact result:

- Intended result confirmed: record delivery.
- No effect confirmed: retry only with current authority and fresh preconditions.
- Unintended result confirmed: record failure and use only authorized remediation.
- Result unknown: HOLD. Do not retry blindly.

A PR's “merged” state alone does not prove that the intended candidate was delivered.

Deployment adapters are deferred until an actual target exists. A GitHub merge does not imply deployment or customer acceptance. Any future adapter must enforce the relevant immutable artifact and mutable-target preconditions.

## Cleanup

Cleanup follows completed verification and durable preservation. A pushed branch tip is necessary when remote source preservation is required, but is not sufficient.

Before removal:

1. Verify the intended source commits and original diffs are retained in the authorized repository or a recoverable archive.
2. Preserve raw test and failure evidence in the private evidence store. Check its recovery references.
3. Account for tracked changes, untracked files, ignored files, generated files, and external dependencies.
4. Confirm no active writer, replacement attempt, or dependent task still needs the worktree or its files.
5. Verify the retained revision and evidence can be read back. Preserve ambiguous or irreplaceable local files.

Remove only the completed worktree and artifacts demonstrated to be regenerable or durably retained. Do not force-remove unknown work. Delete branch refs only when separately authorized and required history remains reachable.

Record the retained source, evidence location, cleanup result, and measured reclaimed space. A cleanup blocker does not erase local acceptance, but it remains unfinished cleanup.

Repository visibility follows actual owner direction. Keep private evidence and credentials outside public source repositories.
