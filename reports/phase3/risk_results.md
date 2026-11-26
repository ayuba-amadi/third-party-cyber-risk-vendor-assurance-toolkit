# Phase 3 assessment risk

Phase 3 implements questionnaire processing, evidence evaluation, domain completeness and risk scoring only. Approval decisions, corrective actions, reassessments, management reporting, Streamlit GUI and deployment remain later phases.

Report date: 2026-11-18
Source directory: sample-data

## Scoring methodology

Multiply assigned risk by question weight. Divide the sum by four times the sum of all weights.
Bands start at 0%, 20%, 40% and 60%. Thresholds use the unrounded percentage.

## Evidence and completeness rules

Verified credit requires an answered claim, accepted evidence with reviewer details and valid expiry,
and a valid reviewer verified answer. Expiry on the evidence evaluation date remains valid.
Unverified responses receive 4. Each question remains in the denominator.
Incomplete assessments display provisional percentages. Superseded assessments use their assessment date.

## Critical failure rules

A verified value of 3 or 4 on a critical question receives 4 and sets a High minimum for completed ratings.
An unverified critical question remains unresolved.

## Assessment results

### ASMT-001 / VEN-001

- 6/344 × 100 = 1.74%. Raw band Low.
- 24/24 verified. Complete. Final rating Low.

### ASMT-002 / VEN-002

- 59/344 × 100 = 17.15%. Raw band Low.
- 22/24 verified. PROVISIONAL — INCOMPLETE ASSESSMENT. Final rating Incomplete.
- Unresolved critical questions: AM-01, DP-01
- Evidence flags: AM-01:Missing, DP-01:Missing

### ASMT-003 / VEN-003

- 28/344 × 100 = 8.14%. Raw band Low.
- 24/24 verified. Complete. Final rating High.
- Confirmed critical failures impose a High minimum on completed ratings: AM-01

### ASMT-004 / VEN-004

- 3/344 × 100 = 0.87%. Raw band Low.
- 24/24 verified. Complete. Final rating Low.

### ASMT-005 / VEN-005

- 22/344 × 100 = 6.40%. Raw band Low.
- 23/24 verified. PROVISIONAL — INCOMPLETE ASSESSMENT. Final rating Incomplete.
- Evidence flags: IN-02:Rejected

### ASMT-006 / VEN-006

- 19/344 × 100 = 5.52%. Raw band Low.
- 23/24 verified. PROVISIONAL — INCOMPLETE ASSESSMENT. Final rating Incomplete.
- Evidence flags: GV-02:Expired

### ASMT-007 / VEN-007

- 0/344 × 100 = 0.00%. Raw band Low.
- 24/24 verified. Complete. Final rating Low.

### ASMT-008 / VEN-008

- 3/344 × 100 = 0.87%. Raw band Low.
- 24/24 verified. Complete. Final rating Low.

### ASMT-009 / VEN-009

- 20/344 × 100 = 5.81%. Raw band Low.
- 24/24 verified. Complete. Final rating High.
- Confirmed critical failures impose a High minimum on completed ratings: DP-01

### ASMT-010 / VEN-010

- 141/344 × 100 = 40.99%. Raw band High.
- 14/24 verified. PROVISIONAL — INCOMPLETE ASSESSMENT. Final rating Incomplete.
- Unresolved critical questions: SC-01
- Evidence flags: BC-03:Missing, BC-04:Missing, GV-01:Missing, GV-02:Missing, GV-03:Missing, GV-04:Missing, SC-01:Missing, SC-02:Missing, SC-03:Missing, SC-04:Missing
- Unanswered questions: BC-03, BC-04, GV-01, GV-02, GV-03, GV-04, SC-01, SC-02, SC-03, SC-04

### ASMT-011 / VEN-004

- 39/344 × 100 = 11.34%. Raw band Low.
- 23/24 verified. PROVISIONAL — INCOMPLETE ASSESSMENT. Final rating Incomplete.
- Unresolved critical questions: SC-01
- Evidence flags: SC-01:Received

## Question examples

- ASMT-002 / AM-01 — Effective evidence status is Missing. Awaiting evidence. Reviewer verification or verified answer is outstanding. Worst-risk treatment applies. 4 × 5 = 20 points.
- ASMT-002 / DP-01 — Effective evidence status is Missing. Awaiting evidence. Reviewer verification or verified answer is outstanding. Worst-risk treatment applies. 4 × 5 = 20 points.
- ASMT-003 / AM-01 — Confirmed critical failure receives risk value 4. 4 × 5 = 20 points.
- ASMT-005 / IN-02 — Effective evidence status is Rejected. Report outside required review window. Reviewer verification or verified answer is outstanding. Worst-risk treatment applies. 4 × 4 = 16 points.
- ASMT-006 / GV-02 — Effective evidence status is Expired. Previously accepted report no longer current. Reviewer verification or verified answer is outstanding. Worst-risk treatment applies. 4 × 4 = 16 points.
- ASMT-009 / DP-01 — Confirmed critical failure receives risk value 4. 4 × 5 = 20 points.
- ASMT-010 / BC-03 — Effective evidence status is Missing. Unanswered. Vendor claim is unanswered. Reviewer verification or verified answer is outstanding. Worst-risk treatment applies. 4 × 3 = 12 points.
- ASMT-010 / BC-04 — Effective evidence status is Missing. Unanswered. Vendor claim is unanswered. Reviewer verification or verified answer is outstanding. Worst-risk treatment applies. 4 × 3 = 12 points.

## Domain completeness

| Assessment | Domain | Answered | Verified | Complete |
|---|---|---:|---:|---:|
| ASMT-001 | AM | 4/4 | 4/4 | 100.00% |
| ASMT-001 | BC | 4/4 | 4/4 | 100.00% |
| ASMT-001 | DP | 4/4 | 4/4 | 100.00% |
| ASMT-001 | GV | 4/4 | 4/4 | 100.00% |
| ASMT-001 | IN | 4/4 | 4/4 | 100.00% |
| ASMT-001 | SC | 4/4 | 4/4 | 100.00% |
| ASMT-002 | AM | 4/4 | 3/4 | 75.00% |
| ASMT-002 | BC | 4/4 | 4/4 | 100.00% |
| ASMT-002 | DP | 4/4 | 3/4 | 75.00% |
| ASMT-002 | GV | 4/4 | 4/4 | 100.00% |
| ASMT-002 | IN | 4/4 | 4/4 | 100.00% |
| ASMT-002 | SC | 4/4 | 4/4 | 100.00% |
| ASMT-003 | AM | 4/4 | 4/4 | 100.00% |
| ASMT-003 | BC | 4/4 | 4/4 | 100.00% |
| ASMT-003 | DP | 4/4 | 4/4 | 100.00% |
| ASMT-003 | GV | 4/4 | 4/4 | 100.00% |
| ASMT-003 | IN | 4/4 | 4/4 | 100.00% |
| ASMT-003 | SC | 4/4 | 4/4 | 100.00% |
| ASMT-004 | AM | 4/4 | 4/4 | 100.00% |
| ASMT-004 | BC | 4/4 | 4/4 | 100.00% |
| ASMT-004 | DP | 4/4 | 4/4 | 100.00% |
| ASMT-004 | GV | 4/4 | 4/4 | 100.00% |
| ASMT-004 | IN | 4/4 | 4/4 | 100.00% |
| ASMT-004 | SC | 4/4 | 4/4 | 100.00% |
| ASMT-005 | AM | 4/4 | 4/4 | 100.00% |
| ASMT-005 | BC | 4/4 | 4/4 | 100.00% |
| ASMT-005 | DP | 4/4 | 4/4 | 100.00% |
| ASMT-005 | GV | 4/4 | 4/4 | 100.00% |
| ASMT-005 | IN | 4/4 | 3/4 | 75.00% |
| ASMT-005 | SC | 4/4 | 4/4 | 100.00% |
| ASMT-006 | AM | 4/4 | 4/4 | 100.00% |
| ASMT-006 | BC | 4/4 | 4/4 | 100.00% |
| ASMT-006 | DP | 4/4 | 4/4 | 100.00% |
| ASMT-006 | GV | 4/4 | 3/4 | 75.00% |
| ASMT-006 | IN | 4/4 | 4/4 | 100.00% |
| ASMT-006 | SC | 4/4 | 4/4 | 100.00% |
| ASMT-007 | AM | 4/4 | 4/4 | 100.00% |
| ASMT-007 | BC | 4/4 | 4/4 | 100.00% |
| ASMT-007 | DP | 4/4 | 4/4 | 100.00% |
| ASMT-007 | GV | 4/4 | 4/4 | 100.00% |
| ASMT-007 | IN | 4/4 | 4/4 | 100.00% |
| ASMT-007 | SC | 4/4 | 4/4 | 100.00% |
| ASMT-008 | AM | 4/4 | 4/4 | 100.00% |
| ASMT-008 | BC | 4/4 | 4/4 | 100.00% |
| ASMT-008 | DP | 4/4 | 4/4 | 100.00% |
| ASMT-008 | GV | 4/4 | 4/4 | 100.00% |
| ASMT-008 | IN | 4/4 | 4/4 | 100.00% |
| ASMT-008 | SC | 4/4 | 4/4 | 100.00% |
| ASMT-009 | AM | 4/4 | 4/4 | 100.00% |
| ASMT-009 | BC | 4/4 | 4/4 | 100.00% |
| ASMT-009 | DP | 4/4 | 4/4 | 100.00% |
| ASMT-009 | GV | 4/4 | 4/4 | 100.00% |
| ASMT-009 | IN | 4/4 | 4/4 | 100.00% |
| ASMT-009 | SC | 4/4 | 4/4 | 100.00% |
| ASMT-010 | AM | 4/4 | 4/4 | 100.00% |
| ASMT-010 | BC | 2/4 | 2/4 | 50.00% |
| ASMT-010 | DP | 4/4 | 4/4 | 100.00% |
| ASMT-010 | GV | 0/4 | 0/4 | 0.00% |
| ASMT-010 | IN | 4/4 | 4/4 | 100.00% |
| ASMT-010 | SC | 0/4 | 0/4 | 0.00% |
| ASMT-011 | AM | 4/4 | 4/4 | 100.00% |
| ASMT-011 | BC | 4/4 | 4/4 | 100.00% |
| ASMT-011 | DP | 4/4 | 4/4 | 100.00% |
| ASMT-011 | GV | 4/4 | 4/4 | 100.00% |
| ASMT-011 | IN | 4/4 | 4/4 | 100.00% |
| ASMT-011 | SC | 4/4 | 3/4 | 75.00% |

## Expected fixture comparison

- risk_results: PASS (11 oracle rows)
- question_scores: PASS (264 oracle rows)
- domain_completeness: PASS (66 oracle rows)

## Limitations

Phase 3 implements questionnaire processing, evidence evaluation, domain completeness and risk scoring only. Approval decisions, corrective actions, reassessments, management reporting, Streamlit GUI and deployment remain later phases.
The engine evaluates recorded reviewer judgments. Evidence artifacts are outside the supplied CSV data.
Fixture comparisons run for the fixture report date and cover the full input even when output is filtered.
