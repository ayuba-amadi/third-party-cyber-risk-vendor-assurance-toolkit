# Research → Development handoff — proposed Day 3 v0.9.1

Prepared 21 Nov 2026. Original deadline: 18 Nov 2026, 23:59 WAT (passed). Status: **Committed on research-day3-olasubomi-olakunle; ready for review; not yet accepted** The lead, not the preparer, records the gate decision and approved `research-spec-v1.0`.

## Walkthrough and implementation order

1. Read requirements_matrix.md, data_dictionary.md, workflow.md and demo_scenarios.md (Day 1), then criticality_method.md, question_bank.csv, evidence_and_decision_rules.md, Risk Scoring Method.md; the separate Day 2 worked_examples.md is outstanding and remains outside this Day 3 submission. Source versions reported by team: 999f980 and 866a009 for the two Averil submissions. The checked main-branch criticality and risk source blobs were e893a13d65e726638b487b4e83d38c59d83a449d and 8cd40a57fc6762cdd3c39055bc785c837a9fd2d0, respectively.
2. Import the 12 source CSV tables in sample-data/ using question.csv derived from the canonical Day 2 bank. Validate keys and allowed values before calculation. Use assessment and question composite keys to match responses and evidence. Distinguish workflow status from calculated completeness.
3. Calculate criticality using four factors and service overrides. Calculate risk using all 24 weights; assign worst value 4 when not verified or when a confirmed critical failure applies. Keep provisional results separate from final ratings. Do not equate risk and criticality.
4. Apply human approval constraints, dated corrective actions, expiry and change triggers. Preserve submitted assessment versions. Use current pointers for report totals and retain prior decision snapshots. For historical criticality, a factor snapshot is required (see expected_criticality.csv for proposed fixture). Do not treat expired approval as a currently valid authorization.
5. Run acceptance_cases.md T01–T16 against the build. Compare calculated values with expected_risk.csv, expected_question_scores.csv, expected_criticality.csv, expected_domain_completeness.csv and expected_management.csv. Record actuals and failures via QA template. Reference calculation verification is not toolkit QA.

## Gate checklist

| Gate item | Status |
|---|---|
| R01–R08, D01–D08, Q01–Q10 mapped to tests | Draft covered |
| Ten vendor records, 5 categories; 24 response rows each | Fixture checks passed; 264 including history |
| Evidence/approval edge cases represented | Fixture checks passed |
| Calculation reproducible from inputs | Reference checks passed for 11 risk and criticality outcomes, 264 question scores, 66 domain summaries and all management counts; lead approval pending |
| No favourable credit for unknown evidence; failure cannot be averaged away | Reference check passed |
| Exact expected results, invalid rows separated | Draft ready |
| Canonical source question parent | Canonical wording and criteria included; regeneration script provided; source fields verified against Git blob c9b525df9c46f133e83329ed12bd793b90cfd67f |
| Independent second analyst review and Development walkthrough | Pending |
| Lead acceptance and approved version/commit | Pending |

## Open decisions / corrections to upstream documents

| Gap | Proposed treatment in fixture | Proposed owner / due |
|---|---|---|
| G01 — thresholds and unresolved evidence (R02/R05) | Use latest draft bands and 4 for unknown; Day 1 wording “zero” means zero favourable credit, not zero risk. Confirm all thresholds, date validity and policy choices formally. | Scoring owner + lead; before acceptance |
| G02 — critical failure value (R05/R06) | AM-01 partial coverage has raw 3; scoring method requires 4 after confirmed critical failure. Use 4, minimum High. Confirm whether any critical question with value 2 against criteria triggers failure, not exercised in dataset. | Scoring and questionnaire owners + lead; before acceptance |
| G03 — report scenario totals (R08/D04/D07) | Day 1 targets 2 incomplete; Day 2 yields 5 current vendors (002,004,005,006,010). SVC-06 also has 2 supporting vendors; use all links. Four business-critical vendors, not only three. | Requirements owner + lead; before acceptance |
| G04 — encryption evidence (D03/Q04) | Missing evidence cannot establish actual failure. VEN-009 uses accepted configuration demonstrating no encryption; report explicitly distinguishes from VEN-002 missing evidence. | Requirements/evidence owners; before acceptance |
| G05 — historical factor inputs / evidence versions (R07) | Day 1 schema stores factors only in current vendor table. Historical VEN-004 factors in expected_criticality.csv are proposed snapshot reference; Development must version factors and evidence events. VEN-006 historical Low approval used valid GV-02 at decision date; current expiry is separate. | Schema owner + Development; before historical implementation |
| G06 — evidence sufficiency vs control effectiveness (R04) | Accepted can verify an adverse answer; cannot claim a failed control is effective. Clarify evidence acceptance criteria accordingly. | Evidence owner + lead; before acceptance |
| G07 — decision policy (R06) | Confirm exception rules, reviewer/approver separation, approval validity, rejected decision dates, and `Incomplete` in decision.calculated_rating. Conditional VEN-005 uses non-critical gap and resubmission; VEN-003 is a written exception. | Lead + evidence owner; before approval workflow |
| G08 — naming and citations (R03/R05) | BC domain uses dictionary name; repository file is currently `Risk Scoring Method.md`, expected name `risk_scoring_method.md`; lead to decide rename. Specific NIST method citations still pending as reported by Day 2 owners. | Day 2 owners; before final specification |
| G09 — demo date versus delivery date | Frozen 18 Nov date for reproducibility, actual preparation 21 Nov. Do not backdate submission or simulated review signoff. | Subgroup owner + lead; immediately |

## Handoff Status and Approval

The Research to Development handoff has been recorded in governance/HANDOFFS.md.

The Day 3 deliverables have been committed to the research-day3-olasubomi-olakunle branch and submitted for review.

Final acceptance remains subject to team-lead review, confirmation of outstanding methodology decisions, and the Development walkthrough.

Any approved changes, outstanding gaps or acceptance decisions must be recorded in the handoff register with the relevant date, approver and commit reference.

The outstanding Day 2 worked examples remain outside the scope of this Day 3 submission.
