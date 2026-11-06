# Utlyze memory

Local product knowledge and success/failure observations for fresh sessions. The standalone core uses Python 3.11+ and its bundled SQLite. Canonical-case operations additionally require the existing installed I2E `shared_cases.py` helper, its initialized local store, Git/POSIX prerequisites and the documented local paths; that helper is not bundled or installed here. This release uses no LLM, embedding, provider, network service or background process.

Product knowledge and learning are separate: immutable objective/feature/decision/task revisions explain why work exists; append-only episodes link attempts, candidates and checks to observations. Lessons and comparison records remain inert proposals. Recorded authority is an attested source claim. Hash identity and passing checks do not establish human approval, verified product success or measured improvement.

This is an **unseeded local prototype**. No real product scope, operational knowledge corpus or global skill installation has been created. The user declined an initial product pack. Synthetic demonstration and test fixtures are separate from operational data. Initialize/register a real scope only after the user identifies its project, product and source authority; do not invent a roadmap.

Run from this repository, or use the installed skill launcher:

```sh
python3 -m utlyze_memory --db /absolute/private/memory.sqlite3 --scope example-project --product example-product context <<'JSON'
{"query":"failure learning","max_chars":12000,"carry":[]}
JSON
```

Both project (`--scope`) and product are explicit on every operation. Registration fixes local evidence roots and an optional canonical case scope/store; another product never supplies fallback context. Scope filtering organizes one private user's data. It does not enforce same-user authorization.

The example assumes an explicitly registered real scope; this package does not create one automatically. For an authorized new private database, use `init` with `{}`, then `register` with `{"roots":["/absolute/private/source-root"],"case_store":null}`. Initialization refuses existing files/journals and data inside this source, installed skills or the canonical case store. The database parent must be private (0700); a new parent is created privately and existing permissions are never changed. New files use 0600. Roots must already exist, be absolute and contain no symlink/traversal components. A missing or incompatible store is reported, never reset.

`python3 -m utlyze_memory --help` lists commands. Each accepts one strict bounded JSON object from stdin or `--input /absolute/input.json`. Duplicate keys, nonfinite numbers, unknown fields and oversized input are rejected. Output is `{"ok":true,"result":...}` with exit 0, or `{"ok":false,"error":{"code":...,"message":...}}` with exit 2. `INCOMPLETE` is a successful retrieval response describing insufficient context; inspect its reasons and exact fetch IDs.

The main commands are:

| Command | JSON input |
| --- | --- |
| `append` | `kind`, `entity_id`, `data`, stable `event_id`, `expected_revision` |
| `get` | `kind`, `entity_id`, optional exact `revision` |
| `history` | `kind`, `entity_id`, optional `offset` and `limit` (1–100) |
| `context` / `search` | optional `query`, `max_chars`, `carry`, `task`, `task_revision` |
| `consult` | optional `query`, `carry`; returns full canonical search/show execution receipts |
| `integrity` | `{}`; SQLite and stored-record digest checks, not source truth |

Fact data contains `kind` (`objective`, `feature`, `decision`, `constraint`, `task`), `text`, logical topic `key`, `sources` (local `path` + exact `sha256`), `status` (defaults proposed), optional `authority` reference, `links` to same-product fact IDs, `acceptance`, `anchor`, `conflicts_with`, `expires_at` and task `candidate`. `authoritative` needs an authority reference, still an unverified attestation. Tasks need objective/feature links, acceptance IDs/descriptions/check IDs/evidence and a candidate SHA-256. Link revisions are captured in the write transaction; mandatory anchors and requested tasks retain their exact transitive historical revisions. Historical items are explicitly labeled and include an inspectable current head. A latest withdrawal or supersession prevents a historical claim from appearing as current authority or a ready context; the task is never silently upgraded. Changed source bytes never become current merely because the statement sounds plausible. No expiry date means no time-based freshness claim.

Revisions need the expected current revision; the first is 0. Each record contains timestamp, source identity, exact linked revisions and its superseded digest. Competing active values for a declared subtype/topic must explicitly list every other conflicting ID in `conflicts_with`; bootstrap keeps both disputed claims. This is a declared-topic model, not semantic contradiction detection. Resolution appends a compatible revision or withdrawal; timestamps never select a winner. Withdrawing an anchor remains visible as incomplete context.

Episodes require task/revision/candidate/attempt, separate hypothesis and observed cause, scoped outcome (`observed_success`, `observed_failure`, `unknown`), checks with outcome/evidence, sources, canonical case digests and `claim_level: observation`. A success observation requires the task's named checks to have recorded passing evidence; their factual validity still requires inspection. Episodes, feedback, lessons, comparison records and case links cannot be overwritten. Corrections append a new ID and retain history.

Feedback names the pack hash, query, actual retrieved/used/missed-known IDs, task revision/candidate, rating/note and resulting action/check/evidence references. A submitted feedback hash is provenance supplied by the caller, not proof that an agent used the result. Lesson data names text, supporting episode IDs, proposed change, sources and optional case IDs, limitations and intended validation. Comparison data names a lesson, distinct baseline/candidate hashes, immutable comparison/regression/independent-review references and nonregressing failure counts. `baseline_cases` is the legacy field name for development/training examples; these must be disjoint from `heldout_cases`. **Both the OLD and NEW candidate run the same single frozen `heldout_cases` evaluation set**, and both failure counts must describe that set. Comparison references should identify both candidates and their results on that shared set. Comparing OLD on one set and NEW on another does not establish improvement. IDs and counts are attested; the tool cannot judge semantic disjointness, report truth or reviewer independence. Stale references cannot establish a current recorded validation. `improvement_proven` stays false and there is no promotion/edit-policy operation.

Designated anchors, requested task lineage, unresolved conflicts and every exact known case bypass ranking. Unknown product fields stay visible. Keyword matching uses Unicode normalization and stable tie breaks. The historical name `max_chars` limits the **entire serialized UTF-8 byte envelope**, including warnings/manifests (4096–64000; default 12000), not model tokens. Mandatory overflow returns `INCOMPLETE`, no partial mandatory claim set, and exact `fetch_ids`. If even that complete manifest cannot fit, the budget is refused. Optional omissions are counted. `get` fetches fact/revision and local `case_link` metadata IDs; `consult` fetches exact canonical cases. Overflow manifests retain every contributing local metadata revision as well as canonical digests, so applicability/regression duties remain recoverable. A source-read budget can also leave context unverified.

The canonical helper remains unchanged at `/Users/studio6/.codex-cli/skills/i2e-failure-cases/scripts/shared_cases.py`, with `/Users/studio6/.local/share/i2e-chat-astra-sol/failure-cases` and the configured canonical project scope. The adapter runs only fixed argument-vector `search`/`show`, with drafts. It shows the returned/carried union, checks canonical digest/scope/shape, preserves actual execution output in its response and continues exact show attempts after search failure. Empty/punctuation-only queries use the disclosed keyword `memory`. Full consultation output can be retained as private immutable task evidence; pack summaries/digests are not full receipts. The SQLite store holds only links/applicability/regression metadata, never canonical case records. Every ever-applicable regression remains linked despite later NOT_APPLICABLE or ranking misses. No case command is executed, and no sync/publish/capture wrapper exists.

Limits are deliberate: 64-character safe IDs, 64 KiB input, 16 KiB records, 512 entities/10000 events per product, 16 designated anchors, 16 exact carried case obligations, 64 exact task-lineage nodes, 8 configured roots and bounded regular evidence files (8 MiB each, 64 MiB source budget per pack). These limits fail explicitly. Text is concise reviewed content, not raw logs. Secret detection is heuristic; sanitize before submission. No source content is ingested automatically. The owner can alter local SQLite/evidence files; digest checks and append-only triggers do not replace OS security or backups.

Transactions use bounded locking and durable SQLite journaling. Same intent ID/payload replays the original result; a different payload fails, and expected-revision races have one winner. The actual precommit kill test verifies application rows and replay keys roll back together. Interrupted initial database creation remains visibly incomplete and is not silently overwritten. For backups use SQLite's backup API while writers run; copying only a live WAL database file can lose committed data. Keep evidence files with the backup and inspect recovery in a disposable copy.

Run local proof with:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/demo.py --workdir /absolute/new/private/demo
python3 scripts/verify.py --workdir /absolute/new/private/boundaries
python3 /Users/studio6/.codex-cli/skills/.system/skill-creator/scripts/quick_validate.py skill/utlyze-memory
```

The greenfield RED boundary in `tests/protocol.py` returns explicit UNSUPPORTED only for the wholly empty application baseline. The roundtrip assertion fails because the new session cannot recover its persisted source-linked objective. Once any production module exists, the unchanged harness verifies its actual repository origin and executes it; import/setup/runtime errors are never converted into baseline results. Later direct CLI proof checks real application exit codes and stderr as well as JSON. No tests are skipped or substituted.

The maintained skill source is under `skill/utlyze-memory/`; no global installation or activation has been performed. From a relocated/new checkout, run the core CLI from that checkout. The optional skill launcher has a current-Mac default source path; set `UTLYZE_MEMORY_REPO=/absolute/reviewed/checkout` to select the relocated source. Its package README link is relative; an independently installed skill must use the README in its selected source checkout. The canonical case adapter remains bound to this Mac's installed helper/store paths. On another machine the standalone core can run with `case_store:null`; do not assume the helper or private case store is present, copy private data, or silently use another product. Adapting those case paths is a separate reviewed configuration change, not automatic setup.

The code supplies scoped knowledge revisions, observations, retrieval feedback and inert lesson proposals. Tests use isolated synthetic data and include source drift, exact lifecycle history, recoverable overflow duties, concurrency/replay and actual application crash rollback. The direct CLI demo retains subprocess exit codes/stdout/stderr. Validation and independent-review results are supplied with the private handoff notes; raw receipts and cases stay outside this source repository. Existing I2E routing/skills remain unchanged.

Canonical native-v2 coverage is incomplete: its global behavioral-contract flag cannot encode the proportionate wording-only documentation exception allowed by the user's instructions, and that step has no backdated preflight/current-before-write review. Actual source/check/review receipts remain preserved, and all current behavioral proof and independent reviews are still required. No full-profile consistency pass or deployed/seeded product is claimed. Publication is a separate private snapshot/handoff, not a running memory service.
