# Third Party Cyber Risk Assessment and Vendor Assurance Toolkit

ICSDF Certified GRC Engineering Group 3 capstone. This public repository is the team's working hub. **Status: planning/specification; no functioning toolkit has been delivered yet.** The final implementation may be a Python tool, automated workbook or another suitable approach. A web application is not required. All public examples must use fictional data.

## Work packages and handoffs

All times are **WAT (UTC+1)**. The 72-hour blocks below are internal working deadlines beginning Monday 16 November 2026. Work is measured by accepted outputs, not elapsed time alone. Documentation runs alongside the sequential technical handoffs.

| Group | Dates and deadline | Work package | Strict handoff |
|---|---|---|---|
| [1. Research and Risk Assessment](01-research-and-risk-assessment/WORKPLAN.md) | Mon 16–Wed 18 Nov; 18 Nov 23:59 | Requirements, schema, 24+ question bank, criticality/risk rules, fictional data and expected test results | Approved `research-spec-v1.0` and ten-vendor source dataset |
| [2. Toolkit Development](02-toolkit-development/WORKPLAN.md) | Thu 19–Sat 21 Nov; 21 Nov 23:59 | Validated import, working calculations, evidence/decision/action workflow, reports and examples | Reproducible `dev-candidate-v1`, code/workbook and run guide |
| [3. Testing and Quality Assurance](03-testing-and-quality-assurance/WORKPLAN.md) | Sun 22–Tue 24 Nov; 24 Nov 23:59 | Independent functional, edge-case, regression and reconciliation testing | Test/defect registers, retest evidence and QA sign-off |
| [4. Documentation and Presentation](04-documentation-and-presentation/WORKPLAN.md) | Mon 16–Wed 25 Nov; integrated package 25 Nov 23:59 | PDF, guide, abstract, presentation/demo and contribution record | Version-matched submission and rehearsed demonstration |

The [handoff register](governance/HANDOFFS.md) records the commit, reviewer, acceptance result and gaps. [Contribution record](governance/CONTRIBUTIONS.md) tracks all project members. [Working templates](templates/REQUIREMENTS_AND_TESTS.md) give the required fields. Subgroup membership must be confirmed against the final roster; folder creation does not assign people or grant repository write access.

## Scope and required outputs

1. **Vendor register:** unique vendor IDs, service/category, business owner, data/system access, dependency, subcontractors, assessment status and multiple business-service links.
2. **Criticality:** explainable Low/Medium/High/Critical method covering sensitive information, privileged access, disruption and replacement difficulty, with rules, thresholds and worked examples.
3. **Due diligence:** at least 20 questions covering access, data protection, incident reporting, continuity, subcontractors and governance, with important evidence requirements. The internal research target is 24 or more.
4. **Evidence:** separate supplier claim from reviewer-verified answer; Missing, Received, Accepted, Rejected and Expired states. Missing or unverified evidence cannot earn an automatic favourable verified score.
5. **Automated analysis:** validation, reproducible scores and reasons, critical weakness flags, incomplete assessments, overdue reviews and material changes.
6. **Decisions:** Approved, Conditionally Approved and Rejected with authorised decision-maker, justification, conditions, deadlines and review dates. Human decision is separate from calculation.
7. **Remediation and reassessment:** findings, actions, responsible parties, deadlines, expired approvals/conditions, previous assessment versions and material-change comparison.
8. **Management reporting:** critical suppliers, unresolved weaknesses, overdue assessments/conditions and concentration from service dependencies, with totals reconciled to source IDs.

Expected deliverables include the functioning toolkit, vendor register and completed questionnaire, scoring methodology, evidence/action registers, all three decision outcomes, individual and consolidated reports, test cases with expected/actual/corrections, user guide and contribution record. The E-Campus abstract must be approximately 200–300 words; its PDF must cover requirements, design, scoring, workflow, screenshots, tests, limits and operating instructions with an accessible toolkit download link.

## Minimum fictional demonstration data

At least ten vendors in five service categories; at least three supporting business-critical services; a critical vendor missing evidence; rejected or expired evidence; a conditionally approved vendor with an overdue action; one vendor supporting several important business services; and a material-change reassessment retaining the previous version. Complete the questionnaire for every vendor with favourable, unfavourable and incomplete responses.

## Ten live demonstration actions

1. Import or enter a new vendor and calculate criticality.
2. Change access or dependency and show why classification changes.
3. Process questionnaire responses and flag missing evidence.
4. Show that a critical weakness remains visible despite strong unrelated scores.
5. Generate a reasoned individual assessment report.
6. Record conditional approval and assigned corrective actions.
7. Display overdue actions and an expired assessment/approval.
8. Reassess after material change while preserving the prior assessment.
9. Reject invalid inputs, missing values and duplicate vendor IDs clearly.
10. Reconcile management report totals to underlying records.

## Working rules

- Commit work to the correct subgroup directory or agreed implementation directory, with readable changes and file references in the [handoff register](governance/HANDOFFS.md). The team lead reviews phase gates; a pending gate is not an accepted handoff.
- Use **fictional data only** in this public repository and any public deployment. Keep real assessments and evidence in an access-restricted organisational location with version retention and authorised reviewer decisions.
- If Excel is chosen, separate inputs/calculations/reports, validate inputs, protect formulas and document them; worksheet protection is not access control. If scripts are chosen, include source, sample inputs, dependencies and exact execution instructions.
- The scoring methodology is a team-defined design to be documented and tested. NIST resources below inform it; the project does not claim NIST certification.

## Official design references

- [NIST SP 800-161 Rev. 1 Update 1 — Cybersecurity Supply Chain Risk Management](https://csrc.nist.gov/pubs/sp/800/161/r1/upd1/final)
- [NIST SP 1305 — CSF 2.0 supply chain quick-start](https://csrc.nist.gov/pubs/sp/1305/final)
- [NIST Cybersecurity Framework 2.0](https://www.nist.gov/publications/nist-cybersecurity-framework-csf-20)
- [NIST SP 800-53 Rev. 5](https://csrc.nist.gov/pubs/sp/800/53/r5/final)
