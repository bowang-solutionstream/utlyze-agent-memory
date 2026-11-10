# Claude's review of I2E v2 (proposal revision 7)

- **Reviewer:** Claude (Fable 5.2), asked by the owner on 2026-11-10.
- **Question asked:** Will this produce reliable work, and is it the right size? Quality first, cost second, no over-engineering.
- **Reviewed:** branch `codex/i2e-v7-review-20261110` at `bc6e28f`. All 30 files in `PACKET-MANIFEST.json` match their recorded hashes, and the three hashes in `REVIEW-RESULT.json` match.
- **Method:** I read the whole packet. A second Claude session, briefed separately and not shown my draft, read it independently and reached the same main conclusions. Finding 2 and several pieces of evidence came from that read; I checked each against the text before including it.
- **Standing:** an outside review at the owner's request. It does not follow `REVIEW-PROMPT.md`, it is not the packet's "independent verdict", and it leaves the recorded v7 status and the frozen packet untouched.
- **File references:** `S` is `SKILL-DRAFT.md` and `P` is `PROPOSAL.md`. Both are in `docs/i2e-v7-review/i2e-v2-consolidated-review-v7/`, where `REVIEW-PROMPT.md`, `CHECKS.json` and `PACKET-MANIFEST.json` also live. A number after a colon is a line number in the frozen v7 file. Baseline, direction and earlier-review files are in that folder's `sources/`. `REVIEW-RESULT.json`, `INDEPENDENT-REVIEW.md` and `STATUS.md` are in `docs/i2e-v7-review/i2e-v2-revision7-evidence/`.

## Bottom line

The part of this design that produces good code is sound, and I would keep it nearly as written: a test that really fails before the fix, checks run on the exact commit being delivered, a fresh reviewer who runs things and says what it ran, findings that need evidence, and status reports that never claim more than what happened.

The structure around that core is too large for what it buys, and I would not build revision 7 as specified. There are six reasons. The first three bear on quality, the last three on cost and on whether it runs at all:

1. The text that will steer the models has not been written. What was approved is a contract.
2. Plans are bound to file lists, which pushes a worker toward worse code when a fix needs one more file.
3. The strongest model is assigned by urgency, not by where a mistake is likely or expensive.
4. Routing and isolation depend on host capabilities the packet never demonstrates, and two hold rules depend on them.
5. There is no light path. A one-line fix costs at least four model sessions plus a coordinator, all at max effort.
6. The runtime re-creates in new code what git and GitHub already guarantee.

Nothing in the packet has been run. My recommendation is to stop revising the proposal, cut it to three lanes on top of the v1 helper, write the real prompts, and put the next ten real tasks through it. The later sections say how.

The earlier reviews answered a narrower question well: is the contract consistent, and does it handle the listed cases? None was asked whether it is the right size. That is the gap this review covers.

## What a task costs

Minimum sessions for a clean pass: no findings, no challenged decisions, no specialists. These are counted from the role tables, not measured.

| Route | Coordinator | Plans | Approves plan | Builds | Independent check | Sessions besides the coordinator |
|---|---|---|---|---|---|---|
| v1 as installed | root session | Sol owner | Astra | the same Sol owner | 3 Sol audits | 5 |
| v1, P0 or Critical | root session | Astra owner, after a Sol probe | Astra | the same Astra owner | 3 Sol audits | 6 |
| v2, Low risk with all seven eligibility conditions | Sol | Sol lead | Astra | Sol or Terra worker | 1 Sol verifier | 4 |
| v2, Medium or High risk, or eligibility unknown | Sol | Sol lead | Astra | Sol or Terra worker | 3 Sol audits | 6 |
| v2, High priority | Astra | Astra lead | Astra | Astra worker | 1 or 3 Sol | 4 or 6 |
| v2, Critical risk | Astra | Astra lead | Astra | Astra worker | 3 Sol audits, plus Astra final when triggered | 6 or 7 |

Each fixed finding adds a fresh recheck session, each challenged decision a fresh challenger, and each trigger a specialist or a final review.

Two things stand out:

- The single-verifier route drops two auditors, and the new lead/worker split spends one of them back. v2 is one session cheaper than v1 at best, and one session dearer for anything not shown to be Low risk.
- The top route went from two Astra sessions to four. Its trigger also widened, from "P0 or Critical" to "High priority, or a High finding, or Critical".

Sources: `baseline-SKILL.md`:14–19, 31–32, 55; S:17, 38, 42, 52; P:70–75, 142–150.

## Findings

High means I would not build without changing it. Medium means fix it in the same pass. Each finding has a stable ID so its disposition can be tracked; the text below refers to them as finding 1 to finding 10.

### CLAUDE-V7-01. The prompts that will steer the models are unwritten (High)

**Affects.** The entrypoint draft as a whole and the packaging plan in §10 (P:315–345).

**Evidence.** The entrypoint routes to seven reference files and seven role prompts that are "design targets, not files installed by this packet" (S:21–30; P:319–341). The draft entrypoint itself runs 2,389 words, twice v1's 1,148. It contains 77 negations and restrictions, and about 20 pointers into PROPOSAL sections that will not ship with the skill. It never says which role the session reading it holds. Its ten lifecycle steps average 57 words and pack several obligations each. Step 6 alone covers artifact capture, private staging, fencing, ledger sequencing, stale-write rejection, provenance, check execution and proof invalidation (S:51), and no existing tool provides the fencing it asks for (P:260). Its last paragraph is build and adoption policy, not task instruction (S:93).

**Why it matters.** A model follows an instruction it can find at the moment it acts. Seven reviews checked the contract for consistency. None could test whether a model reading it behaves as intended, because the text a model will read has not been written. That text is where output quality will be won or lost.

**Smallest change.** Write the entrypoint for the session that loads it, and say so. Give it: when to use the skill, the lane table, the steps per lane (who does what and hands off what), the handful of rules that are never negotiable, each stated as what to do and why, and pointers. About 600 words. Move rare-path material into references that load only on that path: restart reconciliation, chained local batches, squash trace retention, rule retirement, formal checking, adoption. Then draft the three prompts that carry the quality (plan review, implementation, verification) and judge them by running them.

**Validate.** Give a fresh session the new entrypoint alone and a small real task. It should be able to say which role it holds, pick a lane and name its next action without opening the proposal. Run each of the three prompts once on a real change.

### CLAUDE-V7-02. Plans are bound to file lists (High)

**Affects.** REQ-01, REQ-02 and O5; lifecycle stages L1 to L3 and L5.

**Evidence.** A plan is an "immutable contract" over owned paths (S:46–47), and in v1's runtime the scope is a literal list of files (`baseline-runtime.md`:54, 81, 161). Any change to that contract needs a new revision and a fresh Astra approval (S:61; P:232) from a reviewer who has not seen the plan before (`baseline-runtime.md`:128, 145). There is no retrospective authorization (S:79), and integration checks each output against the approved scope (P:295).

**Scenario.** Ticket B of a three-ticket batch turns out to need a small change to a shared validator that the plan did not list. The worker has three options. It can stop and send the whole batch plan back for a cold Astra approval. It can edit the helper and fail admission. Or it can copy the logic into a file it owns, pass every gate, and leave the codebase worse.

**Why it matters.** This is the one place where the process pushes directly against the quality of the code. The third option is the cheapest for the worker, and the proposal's answer to duplicated logic is a non-blocking observation (P:424). v2 inherits the rule from v1. I can't tell from the packet how often it bites.

**Smallest change.** Approve intent, not a file list. The contract is the acceptance criteria, the exclusions, the risk tier and the ticket membership, and only a change to one of those needs re-approval. A worker who has to touch a file the plan did not name does so and says so in its handoff. The verifier judges whether the change is within intent. File lists stay useful as a hint for splitting parallel work.

**Validate.** Replay the scenario. The worker edits the unlisted helper and reports it, the verifier accepts or rejects it on intent, and no re-approval is triggered. A change to an acceptance criterion still triggers one.

### CLAUDE-V7-03. Astra is assigned by urgency (High)

**Affects.** D02, D17 and O1; the ownership table in §3.

**Evidence.** The proposal defines priority as "the business urgency of authorized work" (P:66). High priority alone is enough for an Astra manager, an Astra lead and an Astra worker (P:72; S:38). Difficulty does not route (P:77). High technical risk short of Critical stays Sol-led (P:73, 150). Astra runs on the Standard speed tier; Sol and Terra run on Fast (P:58–60).

Three cases show the mismatch:

- An urgent one-line copy fix gets three Astra roles and a fresh Astra plan approval, on the slower tier.
- A Medium-priority change to retry and locking logic, assessed High risk, is planned and built by Sol. Astra only reads the plan.
- A verifier finds one High-severity bug with a three-line fix in a Sol-run batch. The route flips to an Astra manager, an Astra lead, a new plan revision with a fresh Astra approval, and an Astra worker (P:68–72, 79). The sessions that know the batch are replaced, and the proposal describes no handoff. It also says a role prompt "cannot change the running model" (P:62).

The manager's model is also an output of a classification the manager helps make. Intake belongs to "Manager + tech lead" (P:125), their models come from the intake classification (P:70–75), and technical risk can't be known until someone reads the code. v1 handled this with a Sol probe before routing (`baseline-SKILL.md`:31–32). v2 folds the probe into the lead (P:52), so the lead's own investigation decides whether the lead and the manager should have been a different model. Separately, "one project manager" whose context continues across the project (P:38, 349) cannot be Sol for one task and Astra for the next.

**Smallest change.** Route on one input: a tier the lead assesses from blast radius and difficulty. Set the lead at intake and keep it. The manager is the root session in every tier. Priority orders the queue and does nothing else. A High finding sends its repair to Astra and changes nothing else.

**Owner's call.** The direction was "severity as high, priority as high, we would use Astra" (`severity-routing-direction.md`:16). The proposal's reading of priority as a scheduling field (line 20 of that file) is what makes this expensive. If the intent was importance, that is the same axis as risk, and it still comes down to one input.

**Validate.** Route four cases on paper. An urgent trivial fix gets no Astra role. A Medium-priority, High-risk change gets an Astra lead. A High finding in a Sol-run batch sends its repair to Astra and leaves the manager and lead in place. A project with mixed tasks keeps one manager throughout.

### CLAUDE-V7-04. Routing and isolation rest on host capabilities the packet never demonstrates (High)

**Affects.** O7 and the isolation contract in §9.1; lifecycle stage L3.

**Evidence.** Dispatch must hold unless the host attests the effective model, effort and tier; "prompt labels and self-reports are insufficient" (S:36; P:62; O7 at P:464). No reviewer dispatch recorded in this packet passes that test. For v7, `effective_model`, `effective_effort` and `effective_service_tier` are all `UNVERIFIED` (`REVIEW-RESULT.json`:19–21; `INDEPENDENT-REVIEW.md`:45; `STATUS.md`:11). Reviews v3 to v6 report the same (`independent-review-v3.md`:27, `-v4.md`:25, `-v5.md`:45, `-v6.md`:47). The packet shows no host path that selects a model per role or reports which one ran.

Isolation has the same shape. Dispatch holds unless the adapter can validate that a worker has no write access to the integration destination or to another attempt's output (S:49; P:293, 299, 408). The proposal concedes that worktrees do not prove this (P:247) and names no mode that does.

**Why it matters.** Followed literally, v2 holds at its first dispatch. Followed loosely, the agent learns that a hold can be stepped over, and every other gate in the skill is written the same way. And if the host cannot select a model per spawned agent at all, the routing table in §3 has nothing to act on.

**Smallest change.** Find out first; it is a five-minute probe. Spawn one agent per requested configuration (Astra at max on Standard, Sol at max on Fast, Terra at max on Fast) and look at what the host lets you request and what it reports back. Then pin model and effort per role in whatever the host offers for configuring spawned agents, so the host does the enforcing. Record what was requested and whatever the host returns. Treat "effective settings unverified" as a limit written on the receipt. Hold only when the host cannot run the requested model or reports a different one. Finding 6 removes the isolation requirement.

**Validate.** The probe record shows, per configuration, what was requested and what the host returned. A dispatch whose model was requested but cannot be verified proceeds with "unverified" on its receipt. A reported mismatch holds.

### CLAUDE-V7-05. No light path (High)

**Affects.** O4, O2 and D01; §11.

**Evidence.** "Tiny nonbehavior edits still encounter the preserved exact-plan gate" (P:353), and the exemption is parked as an open decision (O4, P:461). Every plan needs a fresh Astra approval (S:42). The lead never builds (S:17). Anything of unknown eligibility falls back to three audits (P:150). Reviews v1 and v2 both called this gate costly for trivial work (`independent-review-v1.md`:47; `independent-review-v2.md`:36).

**Why it matters.** Cost is the obvious part. The quality part is that a process this heavy for a typo gets skipped for small work, and skipped work gets no independent check at all. A light lane that is always used protects more than a heavy lane that is sometimes bypassed.

**Smallest change.** Add a direct lane.

- Entry: one ticket; low risk; none of the seven triggers and no security trigger; an observable check exists or ships with the change; nothing unclear about scope. When unsure, use the standard lane.
- Shape: one worker plans inline and builds, test-first when behavior changes. One fresh verifier runs the check and reads the diff. No lead and no Astra plan approval.
- Exit: any surprise moves the task to the standard lane with its history. Scope grows, a trigger appears, or a finding survives one repair.

**Validate.** A typo fix completes with two sessions besides the coordinator: the worker and the verifier. A direct-lane task whose scope grows moves to the standard lane with its history.

### CLAUDE-V7-06. The runtime rebuilds what git and GitHub already guarantee (High)

**Affects.** D11, D12, O8 and O9; §9.1, §9.2 and §13; prior findings I2E-V2-01 and I2E-V2-02.

**Evidence.** §9.1 specifies leases, fencing tokens, immutable artifact capture, atomic admission against a ledger sequence, and proof that an old process tree has stopped writing (P:289–301; S:49, 51). §9.2 specifies an adapter contract for conditional external actions with four-way outcome reconciliation (P:303–313; S:54). O9 proposes formal models of that machinery (P:466), and §13 lists 43 probes to build against it (P:384–428). The draft notes that the current helper enforces none of this (S:91; P:260). Both gaps entered as a reviewer's counterexamples, "not reproduced defects" (`independent-review-v1.md`:36). Closing them was right. The size of the fix is the issue.

**Why it matters.** This is a large body of new code to write, test and maintain before the first task runs, and every part of it is another place for the workflow itself to fail. With one worktree per attempt, I can't find a case where it makes the delivered diff more correct than the version below. What it adds is a record of which attempt wrote which bytes.

**Smallest change.**

- Admit commits, not directories. This closes I2E-V2-01. Each attempt gets its own fresh worktree and branch, and hands in a commit SHA. Integration merges or cherry-picks named SHAs. The candidate is the resulting SHA, and checks, review and merge all name it. A commit is already immutable and content-addressed, so a stale worker can keep writing to its abandoned worktree and nothing will read it. Where a host offers only a shared worktree, run one attempt at a time and reset to the last commit before replacing a worker.
- Let GitHub enforce delivery. This closes I2E-V2-02. Protect `main` with required checks and "require branches to be up to date". Merge with `gh pr merge --match-head-commit <reviewed SHA>` and read the merge commit back. If `main` moved, update the branch and let CI re-run; ask for a fresh model review only when the update conflicted or touched the same files. After a timeout, ask GitHub for the PR's state; a merged PR cannot merge twice. That covers §9.2 for the one delivery route the proposal defines (P:244–252).
- Put deterministic gates in CI. GitHub enforces a required status check. Nothing enforces a rule in a prompt.
- Drop the formal-model targets, which exist to verify the machinery this removes. Write a deploy adapter when there is a deploy target.
- Settle worktree cleanup, which the owner has asked for twice and which is still pending (`revision-direction.md`:9; `docs/i2e-v7-review/README.md`:14). One worktree per attempt makes it necessary, and it fits in one rule: remove a worktree once its branch tip is pushed.

Review v2 suggested starting with one isolation mode and one delivery mechanism (`independent-review-v2.md`:48). These are the ones already in hand.

**Validate.** Three probes cover what §9.1 and §9.2 were for. Expire a worker, start its replacement in a new worktree and let the old one keep writing: the integrated SHA contains none of the late writes. Push a commit to the PR after review: `--match-head-commit` refuses the merge. Move `main` after review: branch protection asks for an update and CI re-runs.

### CLAUDE-V7-07. On the top route, the last independent look comes from the weaker model (Medium)

**Affects.** The final-review triggers in §6 (P:164).

**Evidence.** When Astra plans and builds, assurance still comes from Sol (S:42; P:81). A fresh Astra final review happens only when one of seven triggers fires, and being on the High route is not one of them (P:164). The packet treats Astra as the stronger model throughout.

**Why it matters.** This is the route for work where a miss costs most, and quality is the first concern.

**Smallest change.** Make the critical lane itself a final-review trigger. With finding 3 that lane is rare, so the added cost is small.

**Validate.** A critical-lane task with none of the seven triggers still gets a fresh Astra final review.

### CLAUDE-V7-08. "Real failure" has no boundary (Medium)

**Affects.** REQ-04 and D07.

**Evidence.** "Capture every real failure before repair" (S:71; P:88). A capture means a canonical case, a snapshot of every scoped file in its broken state, and a new case consultation before each repair (`baseline-runtime.md`:171–198). The only stated exception is the expected failing test.

**Why it matters.** A worker iterating toward a passing test hits failures constantly: a type error, a neighboring test it broke. Read literally, each one needs a capture and a consultation before the next edit. That is either a heavy tax on the inner loop or a rule that gets quietly skipped, and a rule that is quietly skipped teaches the agent that rules are optional.

**Smallest change.** Capture failures seen once a worker has handed in a candidate: integration checks, independent verification, CI, anything after merge. Add any failure that survives one repair attempt. Leave ordinary iteration alone.

**Validate.** A type error fixed during iteration creates no capture. A failure found by the verifier or by CI creates one, and so does a failure that survives one repair attempt.

### CLAUDE-V7-09. One vocabulary for three axes (Medium)

**Affects.** D17 and O1; §3 and §6.

**Evidence.** Finding severity, task priority and technical risk all use High, Medium and Low, with Critical added to risk only (P:66; S:38–42, 52). "Low" then has three consequences: a Low finding is dropped, a Low-priority task is still done, and Low risk unlocks the single-verifier route. The draft spends about half a dozen sentences telling the model not to swap them (S:38–42). v1 used P0–P3 for priority and Low to Critical for risk, so the words could not collide (`baseline-runtime.md`:79).

**Why it matters.** The naming invites the exact mistake the guards exist to prevent: "Low priority" read as "Low risk", choosing the cheap route for a risky change.

**Smallest change.** With finding 3, priority stops routing and most of the collision goes away. Keep High, Medium and Low for findings, which is what the owner's direction was about. Name the lanes with different words. If priority is kept for ordering the queue, give it its own words too.

**Validate.** In the new entrypoint no word names two axes. A task described as low priority and high risk lands in the critical lane.

### CLAUDE-V7-10. The five-ticket cap grew its own machinery (Medium)

**Affects.** D06 and O5; §8.1; prior finding I2E-V3-01.

**Evidence.** The direction was phrased as a question: "no more than 5 edits into one batch?" (`batching-git-direction.md`:5). The proposal turned it into a runtime-validated invariant with a reviewer duty to look for a hidden sixth scope (P:224), a protocol for chaining local-only batches through pinned predecessors (P:228–230; S:65), and a rule that even removing a ticket needs a fresh Astra plan approval (P:232). One failed ticket holds the other four (P:236).

**Smallest change.** Keep "batch related tickets, five at most" as a planning rule that the lead applies and the plan reviewer sees. A batch that depends on an earlier one branches from that batch's accepted commit and is reviewed as its own diff, which needs no protocol. Let the lead drop a stuck ticket with a note and a re-verification of the smaller candidate, with no new plan approval unless another ticket depended on it.

**Validate.** Six dependent local-only tickets run as two batches, the second branching from the first's accepted commit, with no extra protocol. Dropping a stuck ticket takes a note and a re-verification, not a plan approval.

## Why I'd stop revising the document

Seven revisions and seven reviews have produced no run. The proposal says so plainly: implementation, the pilot and any savings are "NOT_RUN / UNVERIFIED" (P:508; also P:23). `CHECKS.json` covers hashes, links and preservation. The v7 review prompt lists the cases to challenge, stated as the outcomes expected, and applies the proposed Low filter to the review itself (`REVIEW-PROMPT.md`:9–15). The review confirms those cases and byte-level integrity (`INDEPENDENT-REVIEW.md`:47), from a reviewer whose model is unknown. So the approval shows that the v7 delta is consistent. It does not show more than that.

The open risks are all empirical: whether the gates catch real defects, whether models follow the text, what a task costs. Another revision cannot answer those, and each one enlarges the contract the next review must certify. The adoption plan in §12 is rigorous, and heavy for a one-owner project: preregistered thresholds, shadow arms, concealed seeded faults, adjudication (P:370–378). If it never runs, every "defer until measured" position (O2 to O5) stays in force indefinitely.

A trial that can actually run:

1. Put the next ten real tasks through the three lanes below.
2. Write one row per task: lane, sessions, wall-clock, findings that turned out to be real, defects found after acceptance.
3. For direct-lane and single-verifier tasks, run the three v1 audits afterwards on the accepted commit. Note anything material they catch that the verifier missed.
4. Adjust the lane rules from what the table shows.

This is weaker evidence than §12 would give. It is enough to show a lane that leaks, and it will exist.

## The shape I'd build

| Lane | Use when | Plan | Build | Independent check |
|---|---|---|---|---|
| Direct | One ticket, low risk, no trigger, and an observable check exists or ships with the change | The worker, inline | The same worker | One fresh verifier runs the check and reads the diff |
| Standard | Everything else below critical, including batches | Sol lead; a fresh Astra approves | Separate workers, one worktree each | Low risk: one fresh verifier who executes. Medium risk: the three audits, until the trial shows one verifier plus triggered specialists is enough |
| Critical | High or Critical technical risk, or hard architecture | Astra lead; a fresh Astra approves | Astra or Sol, as planned | Three audits, triggered specialists, and a fresh Astra final review every time |

The security triggers and the seven final-review triggers stay as explicit yes-or-no checks in every lane (P:154–164).

Rules that hold in every lane:

1. A behavior change starts with a test that fails on an assertion, then passes with the test unchanged. Setup and import failures don't count (S:50; P:190–204).
2. Whoever verifies did not plan or build, runs the acceptance checks itself, and says what it executed and what it only read (P:144, 208).
3. A finding needs evidence, a consequence and the smallest fix, and "no findings" is a valid result (P:168). Low items go to a notes file, one line each, and stay out of the loop. That record can be simpler than P:178 asks: no IDs and no revisit triggers.
4. Two failed repairs of one defect: stronger-model diagnosis before a third. Three unresolved rounds on one decision: ask the owner (P:89).
5. Report the actual state (accepted locally, PR open, CI passed, merged) and name anything not run (P:136).
6. Approval is not authority. Merge or deploy only where the owner has allowed it (P:85).
7. The plan fixes intent: acceptance, exclusions, risk and ticket membership. A worker who needs a file the plan did not name touches it and says so, and the verifier judges it.
8. The candidate is a commit SHA. Checks, review and merge all name it, a new commit means new checks, and merges use `--match-head-commit`. Remove a worktree once its branch tip is pushed.
9. One manager, the root session, in every lane. Priority orders the queue.

The first six are in the proposal already and should stay as they are. So should the v1 helper's `check`, which refuses to report COMPLETED without current proof, reviews and resolved findings (`baseline-runtime.md`:206). It is the one piece of bookkeeping enforced by code.

Cut relative to revision 7: §9.1, §9.2, O9 and most of §13's probes; manager routing and the mid-run route flip; both dispatch holds from finding 4; file-list scope; hidden-scope policing; the chained-batch protocol; and §12's adoption machinery, in favor of the trial above.

## Suggested order of work

If the owner accepts this direction:

1. Run the host probe from finding 4 and record the result. The routing design depends on it.
2. Write the new entrypoint and the three prompts (finding 1).
3. Produce a shorter proposal as a new versioned candidate, leaving v7 frozen, with a change record that maps each finding to a change or a reasoned disagreement.
4. Prepare the trial sheet, and start the trial when the owner says to.

None of this needs anything installed or activated.

## Decisions for the owner

Each of these changes something the owner directed, or relaxes a gate that v1 or the proposal treats as preserved. The choice is the owner's. My recommendation is given for each.

1. **What selects Astra** (finding 3; O1). Recommended: a risk tier the lead sets from blast radius and difficulty. Priority orders the queue. A High finding sends its repair to Astra and changes nothing else.
2. **A direct lane with no lead and no Astra plan approval** (finding 5; O4, P:461). Recommended: add it.
3. **How many reviewers above Low risk** (O2, P:459). The owner's first description had one independent review, escalating to security by risk (`user-direction-excerpts.md`:21). The proposal defers that route and keeps three audits for anything above Low risk (P:150). Recommended: keep three audits for Medium risk only until the trial's after-the-fact audits show what one verifier misses. The critical lane keeps three audits and always gets a fresh Astra final review (finding 7).
4. **What a plan approval binds** (finding 2; REQ-01, REQ-02, O5). Recommended: intent, not a file list.
5. **Who rechecks a fixed finding** (O3, P:460). Today a third fresh session must, distinct from the reviewer who raised it (P:182). The fix is re-verified along with the changed candidate anyway. Recommended: the reviewer who raised the finding closes it, which saves a session per finding.
6. **When dispatch holds on model settings** (finding 4; O7, P:464). Recommended: only when the host cannot run the requested model or reports a different one.
7. **Which failures get a canonical capture** (finding 8; REQ-04). Recommended: those seen after a worker hands in a candidate, plus any that survive one repair attempt.
8. **The five-ticket cap** (finding 10; O5). Recommended: a planning rule, not a runtime-enforced invariant.
9. **"The tech lead never implements"** (`user-direction-excerpts.md`:15). Recommended: keep it in the standard and critical lanes, where a written plan is reviewed before anyone builds. The direct lane is the one exception.
10. **Max effort on every role** (P:56–60), including the manager and routine Terra edits. I can't judge these models. Recommended: keep max on lead, plan approval, worker and verifier, and test one level lower on the other two during the trial.
11. **How the next version is judged** (O10; §12, P:370–378). Recommended: by the ten-task trial above, not by another document review.

## What I did not check

- Nothing was executed. Every claim here rests on the packet's text.
- `i2e.py` and the failure-case helper are not in the packet, so statements about v1 come from `baseline-SKILL.md` and `baseline-runtime.md`.
- I have no independent knowledge of GPT-6 Astra, GPT-6.1 Sol or GPT-6.1 Terra, or of what the Codex host can configure per agent. Where I call Astra the stronger model, I am following the packet.
- Session counts come from the role tables. They are not measured usage.
- Case consultation looks as if it grows with history: each consultation shows up to 100 cases, every shown case needs a recorded decision, and a saturated search counts as incomplete (`baseline-runtime.md`:99, 105). I could not inspect the helper, so this is a question to answer, not a finding.
- This view would change if several fleets will write to the same repositories at once, or if delivery targets beyond GitHub pull requests are close. Parts of §9 earn their place then, and that is the time to build them.
