# I2E empirical verification proposal v1

Frozen at the user's explicit request on 2026-11-03 at 21:12 UTC.
Status: FROZEN PROPOSAL FOR LATER REVIEW. This is a saved design reference, not an installed workflow or evidence that the proposed verification has run.
Owner request: "lock this proposal as empirical verification piece here and we will come back to this later."
Scope: the independent review's revised empirical plus selective formal verification proposal. This does not adopt Za's original proposal verbatim or change the live I2E skill being updated elsewhere.

## Purpose

Use empirical verification as the default. Add formal verification for specific properties where exploration of state transitions, concurrency, retries, or permissions adds useful coverage. Preserve the distinction between tested implementation behavior, test fault-detection ability, and properties checked in an abstract model.

## Evidence and findings

- Require auditable evidence proportional to a finding's impact. Prefer reproducible failures, deterministic checks, precise source-level arguments, or relevant formal counterexamples.
- Do not require a runnable exploit for every blocking concern. A credible authorization, tenant-isolation, secret, or other material risk can block pending investigation when reproduction is unsafe or impractical.
- Record uncertainty explicitly. Unsupported preferences remain advisory. Implementers address validated findings and explain disagreements instead of automatically accepting every suggestion.
- Record whether an auditor executed a check or inspected another actor's evidence. They are distinct claims.

## Empirical verification

- Preserve meaningful TEST_ONLY -> assertion RED -> PRODUCTION -> unchanged-test GREEN, real failure capture before repair, canonical cases, and applicable regression checks.
- At RED, preserve the source snapshot and verification manifest: assertion/test bytes, runner, configuration, relevant fixtures, dependency lockfile, environment/tool versions, exact commands, and outputs.
- Verify the actual changed surface and observable acceptance criteria. Fixture/setup failures do not establish a behavioral RED. Artifact hashes establish identity, not adequacy or correctness.
- For bug fixes, demonstrate that the regression detects the broken behavior and passes after repair.
- For important new behavior, use relevant negative tests, fault injection, or targeted mutation testing to establish that checks detect plausible defects.
- Target critical behaviors and changed logic. Do not require a unique mutation for every new test or a universal 100 percent mutation score. Distinguish equivalent mutants, invalid mutants, assertion failures, and timeouts.
- Reviewers may share full-suite evidence tied to one immutable candidate, then run targeted independent checks. Never imply that inspecting a report means rerunning it.

## Selective formal verification

- The plan names the requirement, precise invariant or progress property, assumptions, bounds, implementation mapping, and the reason formal checking adds value.
- Preserve model and configuration hashes, tool versions, the exact command, completion state, explored bounds, coverage/reachability observations, and results or counterexamples.
- Check that intended transitions and successful progress remain possible; a model that disables real behavior can pass safety checks vacuously.
- A passing TLC check applies to its finite model and assumptions. It is not a proof of the entire implementation or production environment.
- Connect models to actual behavior with mapped scenario tests, replayable counterexamples where representable, or execution-trace validation. State remaining gaps; observed traces do not cover all executions.
- A synchronization commit is bookkeeping, not proof of model-to-code alignment. Preserve source identity including uncommitted changes when relevant, covered paths/dependencies/configuration, and the evidence supporting the mapping.
- Relevant changes require reassessment before alignment is renewed. Do not satisfy drift control by merely advancing a commit field.
- Ordinary UI/CRUD work usually starts with integration, property-based, and negative tests; formal modeling needs a specific justified target.

## Fleet responsibilities

- Tech lead: acceptance criteria, risks, and candidate properties for formal checking.
- Independent plan challenger: assumptions, missing cases, and whether proposed checks can detect plausible failures.
- Implementation worker: code and required test evidence.
- Independent verifier: exercise the candidate and run targeted negative or mutation checks.
- Specialists: security and formal inspection when required by the selected workflow and task risk.
- Manager: bind findings and proof to the current candidate, resolve obligations, and advance delivery only within existing authority.

## Evaluation before policy adoption

- First pilot one bounded non-P0 stateful task, such as the proposed orchestrator's task-claim/retry/approval lifecycle.
- Candidate properties: exclusive valid task ownership; expired workers cannot publish; old candidate approval cannot authorize changed code; crash/retry does not duplicate publication.
- Compare existing verification with the strengthened approach using known defects and deliberate faults. Keep model routing and approval gates fixed to avoid confounding the comparison.
- Measure defects caught/missed, false alarms, unnecessary rework, latency, usage, and maintenance effort. No per-run budget approval gate.
- One pilot establishes feasibility only. A later mix of routine fixes and stateful features is needed before claiming daily usefulness.
- This proposal does not itself remove, add, or waive any installed I2E review or Astra gate, grant release authority, or modify global policy.

## Evidence consulted when freezing

- Frozen I2E baseline: ../reviewed-commit/skills/i2e-team/SKILL.md, commit a8374b7b299000ac27eed167e78e159b0c84ddd4.
- Historical public-pilot review: /Users/bow/.local/share/grok-pilot/2026-11-02-pstack-sol-e2e/roles/review-03/result.json explicitly says it performed no commands/reruns and assessed separately executed verifier evidence. This does not characterize every current audit.
- https://lamport.azurewebsites.net/tla/model-popup.html
- https://tla.msr-inria.inria.fr/tlatoolbox/doc/model/results-page.html
- https://stryker-mutator.io/docs/mutation-testing-elements/equivalent-mutants/
- https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/
- https://arxiv.org/abs/2404.16075

The X exchanges supplied through Za were not independently verified. No formal tools were run for this evaluation. Future revisions should use a new versioned proposal and retain this snapshot.
