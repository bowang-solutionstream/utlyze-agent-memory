# Policy

Status: proposed v8 rules. The active profile remains unchanged.

## Roles and classification

The root session is the project coordinator. It keeps the objective, authority, current state, and continuation links. It does not count as an independent reviewer. A model change does not create independence.

Record four separate fields:

- `queue_priority`: urgent, normal, or deferred. This orders authorized work only.
- `technical_risk`: Low, Medium, High, or Critical. Assess blast radius, reversibility, uncertainty, and likely failure cost.
- `finding_severity`: High, Medium, or Low. This describes an observed defect's impact.
- `execution_lane`: Direct, Standard, or Critical.

Significant architecture includes unresolved trust, concurrency, recovery, or cross-system design decisions that need Astra judgment. Do not infer it from file count. Unknown material risk requires read-only investigation; it never qualifies for Direct.

The coordinator performs the initial read-only screen. When source investigation is needed, a Sol lead or bounded Sol probe performs it. If that investigation selects Critical, transfer planning to a separate Astra lead before plan approval. Preserve the investigation and contributor identities. This makes intake possible before the final route is known.

## Lane table

| Lane | Entry | Plan | Worker | Independent assurance |
|---|---|---|---|---|
| Direct | One bounded ticket; Low risk; clear authority and boundary; observable acceptance; adequate regression coverage; reproducible checks; no specialist or final trigger; no unexplained failed or unrun required check | Worker records an inline contract before writes; no separate lead or Astra plan approval | Sol by default; Terra for explicitly bounded routine edits | One fresh Sol verifier executes relevant checks and inspects the diff, assertions, and callers |
| Standard | Classified work below Critical-lane entry that is not eligible for Direct; includes batches | Sol planning-only lead; fresh independent Astra approves the exact contract | Separate Sol worker; Terra for planned bounded routine edits | Fully eligible Low-risk candidates may use one fresh Sol verifier; other candidates use distinct Sol code, security, and test audits |
| Critical | High or Critical technical risk, or significant architecture needing Astra ownership | Astra planning-only lead; a different fresh Astra approves the exact contract | Separate Astra worker; explicitly approved bounded Sol parts allowed | Three distinct Sol audits, required specialists, and a fresh Astra final review |

Reduced assurance requires the Direct eligibility conditions except the single-ticket and separate-lead conditions. Assess combined batch risk and interaction coverage. Unknown reduced-route eligibility selects baseline audits, but those audits cannot waive a missing required check.

The planning-only lead never implements in Standard or Critical. Direct is the explicit proposed exception: its worker plans inline and builds. A baseline route does not add a fourth generic verifier.

## Changes during work

Reassess risk and eligibility when evidence changes. A new trigger, material uncertainty, added ticket, changed authority, or unplanned semantic dependency ends Direct eligibility. A correction within the recorded boundary does not automatically create a new ticket. One failed repair of the same finding also moves a Direct task to Standard or Critical.

Before more dependent writes, preserve the prior history, obtain the receiving lane's plan and reviews, and renew affected proof. Do not relabel earlier work as if the new route authorized it.

A High finding assigns the affected repair to Astra. The coordinator stays in place. Reassess technical risk; transfer the lead to Astra only if Critical-lane entry now applies. A Standard lead may retain the rest of a batch when its risk stays below that threshold. Replanning still follows the contract-change rules.

A handoff records objective, acceptance, current candidate, plan revision, allowed writes, dependencies, open findings, repair counts, cases, proof limits, and exact next action. Keep the former actor as a historical contributor. Do not pretend the existing session changed its model.

## Requested settings and evidence

Astra: max effort, Standard tier. Sol and Terra: max effort, Fast tier. Luna remains excluded. These are requested settings, not a statement of host availability.

Record requested and host-recorded model, effort, session identity, and context provenance separately. Collect host evidence from the actual dispatch and session. Self-reports and prompt labels are insufficient. A bounded read-only setup interaction may collect missing evidence before any production assignment.

Hold production dispatch on an unavailable model, a reported model/effort mismatch, absent required identity evidence, or an unvalidated write mode. Hold an independent review assignment if its required identity or contribution history cannot be established.

The adopted profile must select `tier_policy`:

- `require_match` is the default. Unknown or mismatched effective tier holds the affected operational dispatch.
- `record_unknown` is an explicit owner-selected exception. A known requested tier may remain effectively UNVERIFIED. Record that limit. A reported mismatch still holds unless the owner authorizes that exact alternate tier.

A tier exception does not relax model, effort, independence, authority, or write-safety requirements. Read-only design review is distinct from qualifying an operational v8 role. Record its actual provenance without claiming v8 runtime compliance.

The currently available host interface accepts model and effort requests. It has no explicit per-agent tier argument. A capability test must establish the selected adapter's actual behavior. Do not assume that “priority” means the requested Fast or Standard tier.

## Specialists and final review

Assess all seven final triggers: consequential authorization or tenant changes; destructive migrations; critical financial behavior; uncertain cross-system interactions; material redesign; conflicting reviews; user or project requirements.

Any true trigger requires a fresh Astra final review after all other obligations. Critical-lane entry independently requires that review. An unknown trigger blocks the dependent decision.

Security review applies to authentication, tenants, secrets, sensitive data, and trust boundaries. Test expertise applies to weak assertions, substantial behavior changes, concurrency, retries, or unclear reproduction. Significant architecture and repeated-repair diagnosis use Astra.

An eligible baseline audit may cover a matching specialist obligation when its evidence demonstrates that coverage. Keep the three baseline auditors distinct. Do not create duplicate sessions only because one obligation has two names.

Reviewers exclude all relevant planners, coordinators, implementers, and other contributors. Final Astra also excludes prior relevant plan, doubt, audit, verification, and escalation participants.
