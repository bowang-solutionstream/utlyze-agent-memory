# Local runtime — i2e-team/v1

`scripts/i2e.py` uses Python's standard library and private SQLite storage. It is a distinct consistency checker, not the old-v3 engine. It does not invoke agents, authenticate model/human identities, execute tests, inspect the meaning of raw responses, enforce operating-system write permissions, or grant external authority. Preserve and inspect the real invocations, responses, assertions and user authority separately.

The JSON examples below are **synthetic schema examples**, not evidence of a run, model review or approval. Replace every example identifier, path, digest and statement with actual evidence. Do not fill missing evidence with these examples.

## Private paths and dependency

Use absolute persistent paths outside the source checkout and installed skill package. For example, on this account a separately provisioned private run may use `/Users/bow/.local/share/i2e-team/runs.sqlite` and `/Users/bow/.local/share/i2e-team/failure-cases`. These examples do not assert that those stores exist. Never initialize an unrelated existing directory.

Read [persistent storage settings](settings.md) first. Reuse the configured ledger and existing canonical store; the example paths above are not a reason to replace them. Settings provide storage values only. CLI arguments and new intake scope remain explicit.

All runtime paths must use their canonical physical spelling. Symlinks in a path are refused, including macOS `/var` aliases; resolve a known local path before recording it. Arbitrary package, database, evidence and source symlinks remain refused. SQLite files must have no group/other permissions and one hard link. New database files use mode `0600`. Evidence is stored beside the private database under `evidence/`, not in the package.

Use the installed canonical helper, normally `/Users/bow/.codex/skills/i2e-failure-cases/scripts/shared_cases.py`. Read its `references/shared-cases.md` first. Provision a new authorized offline store with that helper's `init --store ABSOLUTE_PATH`. The runtime does not initialize stores or offer `sync`/`publish`. It invokes only local `validate`, `capture`, `search`, `show` and `status`, with argument arrays and no shell. The read-only validator uses `validate --kind case --input FILE`, without `--store`; capture/search/show/status retain their actual store arguments. Case reproduction text remains inert. The caller pins the observed helper file SHA-256; drift blocks use.

Inputs are strict bounded JSON: duplicate keys, non-finite literal constants and oversized inputs are refused. Records are limited to 512 KiB; individual local evidence/source files to 8 MiB. Literal source/instruction manifests contain at most 128 paths. Use one bounded deliverable per run; this initial runtime does not provide a task-dependency scheduler.

## Commands and Python helpers

Run from the package, or resolve the installed script's absolute path. `--input -` reads stdin. Inspect each result before the next dependent action. Exit `0` means the requested local operation succeeded; a JSON `state: BLOCK` returns `1`. CLI usage errors may return `2`. Success of `run append` is storage success, not work authorization or completion.

```sh
python3 scripts/i2e.py policy --input /PRIVATE/policy.json
python3 scripts/i2e.py run init --db /PRIVATE/runs.sqlite --input /PRIVATE/intake.json
python3 scripts/i2e.py run show --db /PRIVATE/runs.sqlite --run TASK
python3 scripts/i2e.py run append --db /PRIVATE/runs.sqlite --run TASK --expect 0 --input /PRIVATE/event.json
python3 scripts/i2e.py run search --db /PRIVATE/runs.sqlite --project PROJECT --query "boundary"
python3 scripts/i2e.py case consult --db /PRIVATE/runs.sqlite --run TASK --expect N --input /PRIVATE/consult.json
python3 scripts/i2e.py preflight --db /PRIVATE/runs.sqlite --run TASK --expect N --mode VERIFY --input /PRIVATE/verify.json
python3 scripts/i2e.py preflight --db /PRIVATE/runs.sqlite --run TASK --expect N --mode TEST_ONLY --input /PRIVATE/start.json
python3 scripts/i2e.py preflight --db /PRIVATE/runs.sqlite --run TASK --expect N --mode PRODUCTION --input /PRIVATE/start.json
python3 scripts/i2e.py case capture --db /PRIVATE/runs.sqlite --run TASK --expect N --input /PRIVATE/capture.json
python3 scripts/i2e.py check --db /PRIVATE/runs.sqlite --run TASK
python3 scripts/i2e.py brief --db /PRIVATE/runs.sqlite --run TASK
```

`N` is the actual current `seq` from `run show`, not a value copied from this guide. Immutable events receive server-assigned sequences and hash-chain bindings under a SQLite write transaction. Different writes cannot reuse one expected sequence. An identical event ID/content retry is idempotent; a changed retry is refused. `run show` returns the immutable contract, server `initial_source`/`initial_profile`, all events, current `seq`/`sha256`, and corrections/withdrawals/supersession in `current_annotations`. A fresh process reads the same history. `run search` filters project before matching text and validates individual bounded records without limiting the whole accumulated history to one record's size.

The public Python entry points are `canonical(value)`, `digest(value)`, `reference(path)`, `verify_reference(ref)`, `snapshot(repo, scope, instructions)`, `profile_identity()`, `evaluate_policy(request)` and `Ledger(db)`. Ledger methods are `init_run`, `append`, `show`, `search`, `preflight`, `capture`, `consult`, `check` and `brief`; their positional arguments follow the CLI. `digest` hashes sorted compact UTF-8 JSON with one trailing newline. `reference` returns an absolute local `path` and actual byte `sha256`; `verify_reference` checks the real file. `snapshot` returns `repo`, `files`, `instructions` and `sha256`, including `null` for absent scoped source files. Instruction files must exist.

The server observes the complete active profile, including its runtime, entrypoint and references. `initial_profile`, plan/proof/review `observed_profile`, and start `profile` are server metadata. Plan/proof/failure events also receive server `observed_source`. Project instruction identity is observed at the plan. A changed active profile, project instruction or pinned canonical helper requires reassessment; old completion cannot silently survive it. A new properly reviewed plan may observe changed instructions. Rejected old history is retained. Profile payload reads permit the installer's retained inode anchor; project source and private evidence refuse hardlink escapes.

## Intake and routing

The exact intake fields are:

```json
{
  "schema": "i2e-team-run-v1",
  "run_id": "synthetic-task",
  "project": "synthetic-project",
  "repo": "/PRIVATE/synthetic-project",
  "scope": ["src/feature.py", "tests/test_feature.py"],
  "test_scope": ["tests/test_feature.py"],
  "instructions": ["AGENTS.md"],
  "contributors": ["ACTUAL_OWNER_SESSION"],
  "authority": {"actions": ["edit"], "evidence": {"path": "/PRIVATE/user-request.txt", "sha256": "ACTUAL_SHA256"}},
  "policy": {
    "priority": "P2",
    "risk": "Low",
    "triggers": {
      "consequential_authorization_or_tenant": false,
      "destructive_migration": false,
      "critical_financial_behavior": false,
      "uncertain_cross_system_interaction": false,
      "material_redesign": false,
      "conflicting_reviews": false,
      "user_or_project_requirement": false
    }
  },
  "known_cases": [],
  "case_store": "/PRIVATE/failure-cases",
  "case_helper": "/Users/bow/.codex/skills/i2e-failure-cases/scripts/shared_cases.py",
  "case_helper_sha256": "ACTUAL_HELPER_SHA256"
}
```

Priority is `P0|P1|P2|P3`; risk is `Low|Medium|High|Critical`. All seven trigger keys require actual booleans. Unknown, missing or malformed assessments block. `policy` returns schema `i2e-team-policy-v1`, `state`, `owner: sol|astra|null`, `final_review: astra|null`, and `errors`. P0 or Critical selects the Astra owner; every true trigger selects Astra final review independently. No budget or usage field is required.

`test_scope` is the immutable literal subset of intake-owned source that TEST_ONLY may edit. Classify it explicitly; filenames do not grant test permissions. The reviewed plan binds its applicable subset. Production source must remain unchanged from intake through the first test phase and during every open TEST_ONLY phase.

Record a real read-only probe and selected owner before the owner plans. Use an `observation` event with this data:

```json
{
  "kind": "ROUTING",
  "owner": {"session": "ACTUAL_OWNER_SESSION", "model": "gpt-6.1-sol", "effort": "max", "evidence": {"path": "/PRIVATE/owner-invocation.json", "sha256": "ACTUAL_SHA256"}},
  "probe": {"session": "ACTUAL_PROBE_SESSION", "model": "gpt-6.1-sol", "effort": "max", "evidence": {"path": "/PRIVATE/read-only-probe.json", "sha256": "ACTUAL_SHA256"}}
}
```

The selected owner must contribute to the plan. Routing uses actual session identifiers; role labels do not replace identities. Reviewers exclude owner, probe and other substantive contributors. The evidence must show the actual invocation; recording a model string does not authenticate it.

## Event envelope and reviewed plan

An appended input has exactly `{"id":"STABLE_EVENT_ID","type":"TYPE","data":{...}}`. Do not supply `seq`, hashes, observed metadata or internal event types. The `i2e/` ID namespace is reserved. `start`, `consultation`, `lookup_intent`, `lookup_progress`, `capture_intent`, `case_link` and operation-gap records are created by their dedicated commands. Correction history never overwrites previous events.

First run a `case consult` request `{"id":"CONSULT_ID","stage":"plan","target":"PLAN_EVENT_ID","query":"ACTUAL_CHECK_AND_SYMPTOMS"}`. It searches the exact project with `--include-drafts --limit 100`, then shows the complete union of ranked and carried cases. A saturated search stays incomplete. Every shown case needs a `case_decision` event:

```json
{"consultation":"CONSULT_ID","digest":"ACTUAL_CASE_DIGEST","applicability":"APPLIES","reason":"Concrete current reason","checks":["REGRESSION_CHECK_ID"]}
```

`NOT_APPLICABLE` also requires a reason. Earlier applicable proof obligations survive later NA labels. A lookup gap is not an empty result. The runtime persists the lookup intent before helper invocation, then retains actual search/show invocation and result artifacts. Successful recovery uses a new consultation ID plus `recovery_for:ORIGINAL_REQUEST_ID` and `recovery_reason`, with the same stage, target and query; earlier failed records remain. Saturation cannot be waived by an unproved narrower retry.

A `plan` event's data is:

```json
{
  "revision": "DIGEST_OF_CONTENT_BELOW",
  "content": {
    "artifact": {"path":"/PRIVATE/plan.md","sha256":"ACTUAL_SHA256"},
    "scope": ["src/feature.py","tests/test_feature.py"],
    "test_scope": ["tests/test_feature.py"],
    "acceptance": [{"id":"observable-behavior","behavior":true}],
    "checks": ["unit"],
    "decisions": [],
    "decision_reason": "Concrete reason no additional non-trivial choice is involved",
    "contributors": ["ACTUAL_OWNER_SESSION"],
    "policy": "REPLACE_WITH_THE_COMPLETE_POLICY_OBJECT"
  },
  "consultation": "CONSULT_ID",
  "supersedes": null
}
```

`revision = digest(content)` binds scope, test roles, acceptance, checks, risk and triggers. Plan `test_scope` must be a subset of both its own `scope` and intake `test_scope`. Candidate snapshots still cover the full intake-owned source, including when a plan narrows its write scope. An amendment retains the immediate previous revision in `supersedes`, with its own preceding case consultation and fresh approval. Nonbehavior acceptance uses `behavior:false` and a concrete `reason`; do not relabel behavioral changes or manufacture RED.

Every reviewer object has exactly:

```json
{
  "session":"ACTUAL_FRESH_SESSION",
  "model":"gpt-6-astra",
  "effort":"max",
  "fresh":true,
  "excluded":["ALL_ACTUAL_EXCLUDED_SESSIONS"],
  "input":{"path":"/PRIVATE/neutral-input.json","sha256":"ACTUAL_SHA256"},
  "invocation":{"path":"/PRIVATE/invocation.json","sha256":"ACTUAL_SHA256"},
  "response":{"path":"/PRIVATE/unchanged-response.txt","sha256":"ACTUAL_SHA256"}
}
```

Append `plan_review` data `{plan:REVISION, verdict:APPROVE|REVISE|BLOCK, reviewer:OBJECT, findings:[]}`. Use fresh Astra Max, excluding contributors and earlier plan reviewers. Preserve all rejections; the latest qualifying verdict governs. A plan approval does not discharge an architecture decision.

## Decisions, tests and reviews

A `decision` contains `lineage`, `revision`, `kind:ordinary|architecture|critical`, `contributors`, `artifact`, `acceptance`, `strategy:REVIEW|TDD_RED`, `choice`, actual `alternatives:[{choice,reason}]`, `tradeoff`, and `supersedes`. Compute its revision from the complete data excluding `revision`. Keep stable lineage and predecessor across amendments. A `doubt_review` contains `decision:LINEAGE`, `revision`, `verdict:SUPPORTED|REVISE|BLOCK|TRADEOFF`, `reviewer`, and `findings`. Ordinary review uses fresh Sol Max; architecture/Critical uses fresh Astra Max. A declared ordinary `TDD_RED` strategy may defer its mapped challenge until meaningful RED. Three unresolved cycles stop dependent work and surface the lineage. Renamed records do not erase earlier required decisions or findings.

1. If carried cases apply, collect their current mapped CHECK evidence with source-preserving VERIFY first. Its request uses an actual ID and owned acceptance, like `{"id":"VERIFY_START_ID","acceptance":["observable-behavior"]}`. It grants no source writes. Findings may remain OPEN during this evidence collection, while ordinary writes and completion stay blocked. Capture/lookup gaps, missing approval and architecture obligations remain prerequisites.
2. Pass TEST_ONLY with input `{"id":"TEST_START_ID","acceptance":["observable-behavior"]}` before test edits. Inspect actual PASS before writing.
3. Run the intended test on the actual candidate. Preserve its exact test bytes, command, output and source state. An assertion failure is RED; import, syntax, setup or infrastructure failure is insufficient. Capture a real defect separately if RED reproduces one.
4. Append its RED proof. If test edits made existing case proof stale, use VERIFY/CHECK again without changing source or discarding the open test baseline. Map those existing regressions separately from the expected failing new test; never claim a failing full suite passed. Then pass PRODUCTION with a new start ID and the same owned acceptance. Inspect actual PASS before implementation.
5. Implement, run the unchanged test for GREEN, and append actual passing proof. Required nonbehavior work uses current relevant checks instead of RED.

A behavioral `proof` has `plan`, `candidate:ACTUAL_SNAPSHOT_SHA256`, `phase:RED|GREEN`, `acceptance`, `check`, `start:EARLIER_START_ID`, `test_id`, `test:LOCAL_REFERENCE`, `output:LOCAL_REFERENCE`, integer `exit`, `outcome`, and `failure_kind`. RED uses `INTENDED_ASSERTION_FAILURE`, nonzero exit and `ASSERTION`. GREEN uses `PASS`, exit `0` and `null` failure kind. Preserve immutable test/evidence files outside mutable source where future edits would otherwise destroy history. For a private test snapshot, also supply `test_path:RELATIVE_DECLARED_TEST_SOURCE`; the server compares its bytes with that actual declared source. A source-local test reference can supply its relative path directly. GREEN retains the exact RED test reference and identity. Required ordinary checks use phase `CHECK`, an earlier applicable VERIFY or PRODUCTION `start`, exact plan/current candidate, actual output, `outcome:PASS` and exit `0`. VERIFY additionally requires the full source, tests, instructions and profile to remain unchanged from its start. A bare PASS-shaped record cannot close a case or finding.

Preflight returns `state`, `errors` and the internally appended `start`. Starts bind the immutable plan, actual source/instruction/profile identity and earlier ledger prefix. Completion replays their prerequisites at their original position. A later approval, case lookup or escalation cannot authorize an earlier edit. A reopened TEST_ONLY cycle invalidates old completion until a subsequent production cycle, current proof and reviews close it.

Server `write_scope` is empty for VERIFY, plan `test_scope` for TEST_ONLY, or plan `scope` minus the immutable intake test ceiling for PRODUCTION. A bounded remediation intersects writing modes with its approved owned paths. VERIFY preserves the actual writing-cycle lineage; it cannot stand in for PRODUCTION or close an unfinished TEST_ONLY cycle. This records permission; it does not intercept OS writes.

The phase baseline continues across repeated TEST_ONLY starts, restart, narrower scope and plan amendments. Another start cannot hide a production edit made during the open test phase. The server observes source and test snapshots when proof is recorded; GREEN must preserve the declared test bytes from RED. A previously unauthorized transition remains invalid in history.

Use three `audit` events, with mutually distinct independent Sol Max sessions. Data is `{kind:code|security|tests, plan, candidate, verdict:APPROVE|REVISE|BLOCK, reviewer, findings}`. They follow current proof. A triggered `final_review` uses the same fields without `kind`, fresh Astra Max, and follows current audits and final case consultation. Exclude every contributor and earlier plan/doubt/audit/escalation participant. Record all actual identities, including rejected reviewers.

Findings use `{id,actionable:true|false,material:true|false,text}` on typed review records. Their nested finding/reviewer structures are validated before storage and consistently interpreted by finding, participant and remediation consumers. Arbitrary observation keys called `findings` or `reviewer` remain inert. A `disposition` links `review`, `finding`, `action:FIXED|NOT_APPLICABLE`, concrete `reason`, `evidence` and a current passing `recheck` proof event that follows the finding. FIXED additionally supplies `review_recheck`, the ID of a later `recheck` review event with `{proof:PASSING_PROOF_ID,plan,candidate,verdict:APPROVE,reviewer:OBJECT,findings:[]}`. That independent Sol reviewer excludes contributors and the original finding reviewer. The review follows current proof and precedes disposition. Empty later audits do not erase old actionable findings. Material tradeoff acceptance additionally requires an earlier actual human `human_decision` with `actor:human`, `kind:RISK_ACCEPTANCE`, exact `plan/review/finding`, `source` and explicit `statement`, then `action:RISK_ACCEPTED` referencing `human_decision`. Inspect the real human source. Astra cannot supply human intent or a TDD deviation; this helper supports no behavioral waiver.

## Real failures and repair

Use `case capture` before repair. Its input has exactly:

```json
{
  "id":"STABLE_CAPTURE_ID",
  "defect":"STABLE_DEFECT_ID",
  "case":"REPLACE_WITH_UNCHANGED_CANONICAL_CASE_OBJECT",
  "failure":{
    "command":["ACTUAL_EXECUTABLE","ACTUAL_ARGUMENT"],
    "output":{"path":"/PRIVATE/failed-output.txt","sha256":"ACTUAL_SHA256"},
    "inputs":[],
    "broken":"REPLACE_WITH_ACTUAL_SNAPSHOT_OBJECT",
    "broken_files":{"src/feature.py":{"path":"/PRIVATE/broken-feature.py","sha256":"ACTUAL_SHA256"},"AGENTS.md":{"path":"/PRIVATE/broken-AGENTS.md","sha256":"ACTUAL_SHA256"}}
  }
}
```

Preserve every existing scoped source/instruction file, including required uncommitted state, under `broken_files`; absent source files remain absent in the snapshot. Canonical case scope/task/broken identity must agree. Do not add defect or learning fields to the canonical case schema. The runtime ledger links them separately.

A public `failure` event records `{defect,broken:ACTUAL_SNAPSHOT,command:[ACTUAL_ARGV],output:LOCAL_REFERENCE,exit:NONZERO_INTEGER}`. Its event ID, or explicit `failure_id`, must match the canonical case's `origin.failure_id`, with the same failed output and broken source. A recorded real failure without that matching capture blocks dependent work. Expected test-first RED remains separate.

Before invoking capture, the runtime freezes the input and validates the complete canonical case through the pinned helper's read-only validator, binding the actual receipt to its digest. Invalid schema is an unstarted capture attempt and must not create an impossible operational intent. After validation, commit the frozen input, expected digest, stable defect and destination intent before the real helper capture. Schema validation does not guarantee store admission; an actual later capture failure stays a gap. A crash retry must submit the identical request, case UUID and captured timestamp. It reuses the same bytes, shows the exact digest, then idempotently links it; it does not regenerate a case. Pending/failed capture and missing proof remain blocking gaps. Inspect the actual local receipts, not just case `EXTERNAL_UNVERIFIED` pointers.

Artifact writes use owned staging, durable publication intent and atomic no-replace publication. Intent binds the stage/final names, content hash/size and actual device/inode before linking. Exact retry reconciles only its recorded owned two-link stage/final pair; foreign links, different identities, conflicting bytes and ambiguous ownership remain refused and preserved. Partial staging bytes remain retained. Long external capture IDs receive bounded internal link IDs. Inputs rejected before capture execution are recorded with `started:false`; they do not create an impossible pending capture. These distinctions never turn an actual begun capture failure into success.

Consult again with `stage:repair` and `target:ACTUAL_BROKEN_CANDIDATE_SHA256`; classify all shown/carried cases. A repair preflight may explicitly include `repair_defect` in its start request. The runtime also carries captured pending defects; omission does not waive their prerequisites. Preserve current broken state again after each failed repair.

A `repair` observation contains `{defect,outcome:PASS|FAIL,before:CANDIDATE_SHA256,after:CANDIDATE_SHA256,output:LOCAL_REFERENCE,start:EARLIER_PRODUCTION_START_ID}`. It must link an earlier authorized start, capture and repair consultation. Two failed attempts of the same stable defect require an earlier fresh Astra `escalation` with `{defect,verdict:DIAGNOSED,reviewer}` before another start. Changing role or event labels does not reset counts. Expected RED is not a failed repair.

When unresolved findings or applicable cases are the reason for the repair, use an explicit bounded `remediation` on the start request. It contains exactly `findings:[{review,finding}]`, `defects:[STABLE_DEFECT_IDS]`, `scope:[OWNED_PATHS]`, `acceptance:[IDS]`, `checks:[IDS]`, `before:CURRENT_CANDIDATE_SHA256` and `reason:CONCRETE_STRING`. Its first five fields must equal one reviewed `plan.content.remediations` entry; `acceptance` also equals the start request's acceptance. `defects` is nonempty and already canonically captured. This mapping limits the paths and obligations being repaired.

The exception defers only those named final fix/recheck obligations. Complete capture/consultation, current plan approval, decision challenge, phase/TDD and repeated-failure rules still apply. Omitted findings, unrelated work and blanket waivers remain blocked. An unrelated applicable regression U still needs current proof; VERIFY can collect U while finding F remains OPEN, including after authorized test edits make U stale. VERIFY does not fix or accept F. Ordinary dependent writes and completion stay blocked until current full proof and supported dispositions close the obligations. Do not demand the completed fix before authorizing its bounded repair.

## Completion, continuity and teaching

Run final `case consult` with `stage:final` and `target:CURRENT_CANDIDATE_SHA256`, classify every shown case and run all carried applicable regressions. Required final Astra review follows that consultation and the current audits. `check` returns schema `i2e-team-check-v1`, `state`, concrete `errors`, current candidate and sequence when available. Its PASS is a local consistency result; actual delivery, authenticated review, deployment and user acceptance remain separate facts.

Preserve `observation`, `checkpoint`, `correction`, `withdrawal` and `supersession` events with actual source links. A checkpoint can record interrupted status, pending work and next investigation. Corrections/withdrawals stay visible after restart and do not automatically change source, approve work or promote lessons into rules. Withdrawal of the current run, plan or acceptance blocks completion.

First append an `observation` report with `{status:COMPLETED|FAILED|INTERRUPTED,summary,candidate}`. Then append `teaching` data with `report:REPORT_EVENT_ID`, exact `plan` and `candidate`, factual `problem`, input-to-output `path`, actual `decisions:[DECISION_EVENT_IDS]`, matching recorded `alternatives`, `tradeoffs:[STRINGS]`, actual `proofs:[PROOF_EVENT_IDS]`, `sources:[LOCAL_REFERENCES]`, `principle`, tiny concrete `example`, and `limits`. Completed work requires actual proof; an interrupted/failed brief can honestly have no proof yet. Missing decisions or alternatives stay unrecorded. `brief` renders the stored status first, then that evidence-linked explanation and current annotations. It does not invent alternatives, root causes or learner mastery.

## Verification and bootstrap limits

The repository tests use disposable synthetic sources/stores and plainly synthetic model receipts. They demonstrate policy, ordered record validation, current evidence, continuity and local canonical-helper integration. They do not establish authenticated future agent runs, hosted sharing, measured quality improvement or old-v3 completion. Never execute case or retrieved episode content automatically.

Building a checker from an empty repository needs independently reviewed, explicitly scoped bootstrap preflights and inert interfaces for meaningful assertion RED. The build's procedural receipts are not an old-v3 pass or self-certification by the new helper. Keep rejected attempts and any invalid bootstrap history; later successful work cannot retrospectively authorize earlier writes. Actual user-only risk decisions and permissions remain outside a model's power to invent.
