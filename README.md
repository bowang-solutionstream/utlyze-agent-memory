# Utlyze agent memory

Private progress and implementation repository for the Utlyze agent-team memory system.

The requested system preserves product objectives and feature context for new sessions, retains evidence-linked success/failure observations for later workflow improvement, and teaches the owner the engineering judgment behind each I2E run.

- [Current status and remaining work](STATUS.md)
- [Agreed agent-team direction](docs/TEAM-PLAN.md)
- [Memory architecture and alternatives](docs/MEMORY-DESIGN.md)
- [Failure reuse and post-run engineering learning](docs/I2E-LEARNING-CONTRACT.md)
- [Updated I2E profile](skills/i2e-team/SKILL.md)
- [I2E implementation contract](docs/I2E-IMPLEMENTATION-PLAN.md)
- [Current I2E verification and engineering brief](docs/I2E-VERIFICATION.md)

This checkout includes the distinct `i2e-team/v1` delivery profile, its local consistency helpers and a reversible installer. The reviewed profile is installed locally and is the default engineering route for `I2E Mode`; explicit legacy selection remains available. The broader product-knowledge memory implementation described in the original progress notes remains a separate workstream.

The profile uses Sol 6.1 Max by default, retains independent Astra plan approval, and requires separate Astra final review when any of the seven named triggers applies. It has no per-run budget gate. Canonical failure cases remain in the existing I2E case store; private run and teaching history use a separate local ledger.

## Local verification and installation

Use Python 3 and the already-installed `i2e-failure-cases` canonical helper. The installer requires the existing `i2e-mode` router, supported macOS exclusive-rename primitives and private recovery storage on the same filesystem. It preserves explicitly selected legacy profiles.

```sh
python3 -B -m unittest discover -s tests -v
python3 -B scripts/install.py manifest --help
python3 -B scripts/install.py install --help
python3 -B scripts/install.py rollback --help
```

Installation takes a reviewed source manifest and the expected current router digest. Keep receipts and recovery data in a private location outside this repository and the installed skills. A detected source/destination conflict must be investigated rather than forced through. Read the runtime guide linked from the profile before creating operational records. Local test fixtures do not establish authenticated model execution, a product delivery, hosted sharing or improvement over earlier workflows.

Private runtime databases, canonical failure cases, raw evidence, session transcripts and credentials are excluded from this repository.

Private storage settings are discoverable at `~/.config/i2e-team/runtime.json`. They connect the persistent ledger and existing canonical case store without supplying project scope, authority or a per-run budget. Current local proof is 141 passing tests, three independent Sol audit approvals, fresh Astra final approval, exact installed payload verification and fresh-process ledger retrieval. See the verification document for limits and the engineering brief.
