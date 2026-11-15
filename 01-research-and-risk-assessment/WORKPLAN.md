# Research and Risk Assessment — 72-hour work package

**Window:** Monday 16 November to Wednesday 18 November 2026, 23:59 WAT. **Owner:** Research and Risk Assessment subgroup. **Handoff:** reviewed, versioned specification to Toolkit Development. The team lead signs off the acceptance checklist. Record each member's contribution in `governance/CONTRIBUTIONS.md`.

## Mission

Define a practical, reproducible vendor assurance process and its exact data and calculation rules. This is a specification for a functioning toolkit, not a collection of generic templates. Use only fictional vendor and person data in public files.

## Day 1 — Monday: requirements and data model

1. Read the capstone brief in the root README. Build a requirements traceability table with IDs R01–R08 for the eight required components, D01–D08 for the demonstration scenarios, and Q01–Q10 for the live demonstration actions. For each, name the input, calculation or workflow, expected output, and test.
2. Define the lifecycle: new vendor → criticality → questionnaire → evidence review → risk calculation → authorised decision → actions → periodic or change-triggered reassessment → reporting. Specify who creates, reviews and approves records; a calculated score never grants approval.
3. Specify connected tables/CSV sheets and fields with type, required/optional status, allowed values, and keys. Minimum: vendor, business service/dependency, assessment version, question, response, evidence item, finding, corrective action, decision/exception, change event, and reviewer audit entry. All joins use a unique immutable vendor_id and assessment_id. Define duplicate and orphan checks.
4. Define the vendor register fields: service/category, business owner, data types and sensitivity, system/privileged access, dependency/impact, replaceability, subcontractor use, assessment status, next review, and material change indicator. Support multiple business services per vendor for concentration reporting.
5. Draft a fictional 10-vendor scenario matrix across at least five categories; mark three business-critical dependencies, missing evidence for a critical vendor, rejected/expired evidence, overdue conditional action, multi-service concentration, and before/after material-change reassessment.

**Day 1 output:** `requirements_matrix.md`, `data_dictionary.md`, `workflow.md`, `demo_scenarios.md` in this folder.

## Day 2 — Tuesday: methodology and questionnaire

1. Define criticality inputs with enumerated values, weights, threshold bands for Low/Medium/High/Critical, treatment of missing input, and worked examples. Cover sensitive data, privileged access, disruption, and replaceability. Explain any automatic Critical override.
2. Write at least 24 answerable, uniquely numbered questions: access management, data protection, incident notification, continuity/recovery, subcontractors, and governance. For every question provide response options, weight/severity, evidence requirement, acceptance criteria, and critical-failure flag. Evidence requirements must describe an artifact and relevant review period, not just “provide documentation.”
3. Specify evidence states Missing, Received, Accepted, Rejected, Expired and timestamps/expiry, reviewer identity, reference/path, and reason. Distinguish supplier claim from reviewer-verified answer. Define how missing, received-but-unverified, rejected and expired evidence affect completeness, score, and flags.
4. Define an explainable risk calculation with denominators, weights, unknown handling, critical-failure overrides, severity thresholds, and reasons displayed in individual reports. Specify invalid-input behavior. A strong aggregate score must not conceal a critical control failure.
5. Define approval states Approved, Conditionally Approved, Rejected and required decision-maker, justification, conditions, deadlines, decision/expiry/review dates. Define overdue reviews, expired approvals, overdue conditions, service-change triggers and historical comparison. Define management counts so each vendor is counted once and every total reconciles to source IDs.
6. Review the proposed rules against at least three worked vendor cases: favourable, adverse critical failure, and incomplete evidence. Log unresolved policy choices for team-lead decision by end of day.

**Day 2 output:** `criticality_method.md`, `question_bank.csv` (24+ rows), `risk_scoring_method.md`, `evidence_and_decision_rules.md`, `worked_examples.md`.

## Day 3 — Wednesday: sample data and acceptance handoff

1. Create complete fictional source records for ten vendors and 24+ questionnaire answers for **each** vendor (at least 240 response rows). Populate evidence states and decisions, findings/actions, dates and service links to exercise every required scenario. Do not claim an artifact has been reviewed if it is only vendor-supplied.
2. Review IDs, referential integrity, allowed values, scoring examples, dates and scenario coverage. Make sample inputs compatible with the chosen build format (CSV is portable). Put files under `sample-data/` with a README explaining each table.
3. Write at least ten expected-result acceptance cases with input changes and exact expected outputs, including duplicate IDs, missing values, invalid statuses, critical weakness override, rejected/expired evidence, overdue action, expired approval, concentration and material-change reassessment.
4. Walk Toolkit Development through the schema, rules, examples, and open decisions. Resolve contradictions and record approved version `research-spec-v1.0` in `governance/HANDOFFS.md`.

**Day 3 output:** the specification and populated source data; `acceptance_cases.md` with explicit expected results; signed handoff by **23:59 WAT**.

## Acceptance gate

The team lead accepts the handoff only when every brief requirement maps to a named file and acceptance case; all 10 fictional vendors have complete questionnaire rows; all six evidence/decision/demo edge scenarios are represented; formulas and thresholds are unambiguous; unknown evidence is never favourable; a critical failure cannot be averaged away; and a second analyst can reproduce the worked calculations. If a requirement is unmet, log the gap and owner in `governance/HANDOFFS.md`; development can begin on accepted parts while the gap is corrected.

## Reference material

- [NIST SP 800-161 Rev. 1 Update 1 — Cybersecurity Supply Chain Risk Management](https://csrc.nist.gov/pubs/sp/800/161/r1/upd1/final)
- [NIST SP 1305 — CSF 2.0 C-SCRM Quick-Start Guide](https://csrc.nist.gov/pubs/sp/1305/final)
- [NIST CSF 2.0](https://www.nist.gov/publications/nist-cybersecurity-framework-csf-20)
- [NIST SP 800-53 Rev. 5 — Security and Privacy Controls](https://csrc.nist.gov/pubs/sp/800/53/r5/final)

These are design references, not a claim of certification or compliance. Cite the specific section used in methodology notes.
