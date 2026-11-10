# Validation supporting v8

Date: 2026-11-10. This is a publication summary of the owner's preceding validation. Raw execution receipts and private case data remain outside this repository.

## Checked inputs

The external Claude review examined v7 at published commit `bc6e28f267aa9847bb38e13fef63d76421a5134a`.

Validation confirmed all 30 v7 packet manifest entries and the three review-bound hashes. It read the proposal, skill draft, original directions, prior review prompts, current source, and installed helper.

The assessment did not treat Claude's document as an instruction to change policy.

## Executed tests

| Artifact | Result | Limit |
|---|---|---|
| Current source at `d4dd80c93004a9831093fd34869cf4ebb70b2f46` | 118 runtime tests passed | Synthetic fixtures; not a v8 fleet exercise |
| Installed helper | Three selected existing regressions failed | Readiness field absent; FAILED report allowed completion PASS; valid scoped human risk disposition remained blocked |
| Corrected frozen baseline at `a8374b7b299000ac27eed167e78e159b0c84ddd4` | Those same three regressions passed | Only the three selected checks rerun in that comparison |
| Named-commit handoff | Later edits in the worker's own directory did not enter the integrated commit | Does not establish worker isolation |
| Worktree write boundary | An old-worker process changed replacement files and its branch ref | Same-user disposable fixture; no production sandbox was tested |
| Pushed-tip cleanup predicate | Pushed source and clean normal status coexisted with local ignored failure evidence | Demonstrates an incomplete cleanup predicate; no real worktree removed |
| Disjoint-file base change | Clean Git merge changed passing acceptance into assertion failure | File overlap alone cannot establish review freshness |

Runtime SHA-256 identities:
- Installed: `0494341b84efca48d310a377f63654cc7903e7021d129be808de797dc24c6963`.
- Corrected frozen baseline: `289e09912b0c4c9fc29796f9fb1f4160e5d5a13c986cab91af67e065fb8e0972`.
- Current source: `419a0812ef6d651b94ff0b75acf509e034ce1f3d57f0be4ebc2a31572b7f84cf`.

The separate isolated four-behavior repair has retained successful test and review evidence. Its full suite was not rerun in this validation. It remains a separate candidate, not the installed helper.

## Read-only capability and provider checks

The exposed host interface accepted model and effort request fields. It had no per-agent service-tier argument. No fresh three-model dispatch probe was run. Effective tiers remain UNVERIFIED.

GitHub readback found `main` unprotected, required checks off, and no matching rules or repository rulesets. That is an observed state, not a proposed configuration. No settings were changed.

The GitHub CLI documents `--match-head-commit` as a PR-head condition. Strict required checks, review freshness, trusted check producers, and bypass settings are separate controls. [CLI manual](https://cli.github.com/manual/gh_pr_merge) · [Branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

Git documents shared refs and configuration across linked worktrees. [Git worktree documentation](https://git-scm.com/docs/git-worktree)

## Limits

No v8 role prompt, fleet runtime, live merge race, effective service tier, OS isolation mode, ten-task comparison, or model-quality benchmark was validated.

The validation report came from the coordinating session. It was not a fresh independent approval. V8 requires its own independent review.

All inspected installed/source bytes and existing worktree states remained unchanged during that validation. Temporary Git fixtures were removed after results were retained. No canonical record, active workflow, or memory was changed.

The source manifest binds this summary to the retained validation report and receipts by hash. Those private receipts are not included in the public packet.
