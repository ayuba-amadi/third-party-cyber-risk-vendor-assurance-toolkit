# Fictional source dataset — Day 3 v0.9.1

Report date: **2026-11-18 (WAT)**. Prepared 2026-11-21. All organisations, records, reviewers, decisions and evidence references are fictional test fixtures. No actual evidence files, review or authorization are represented. Do not use real vendor information. Use UTF-8 CSV; empty optional fields are empty strings; the literal `Blank` denotes an unanswered questionnaire row.

## Source tables (12)

| File | Rows | Purpose |
|---|---:|---|
| vendor.csv | 10 | Current vendor register |
| business_service.csv | 8 | Services and tiers |
| vendor_service_link.csv | 13 | Many-to-many dependencies |
| assessment.csv | 11 | Current assessments and superseded ASMT-004 |
| question.csv | 24 | Question parent with all risk options; canonical question wording, options and evidence criteria |
| response.csv | 264 | 24 rows for each of 11 assessments; VEN-010 has 14 answered |
| evidence_item.csv | 264 | One evidence state per question per assessment |
| finding.csv | 7 | Scenario findings |
| corrective_action.csv | 4 | Remediation tracker |
| decision.csv | 8 | Human-decision fixtures including historical decision |
| change_event.csv | 2 | One material change event pair for SwiftPay |
| reviewer_audit_entry.csv | 535 | Synthetic event history |

Phase 2 adds `assessment_criticality_snapshot.csv` as a separate, explicit
assessment-level source with 11 rows, one for every assessment version. Current
assessment rows record the factor values from the vendor register at that
assessment; historical ASMT-004 retains its own 2026 factor values. The
criticality engine reads this snapshot and never substitutes current VEN-004
values into the superseded assessment. `snapshot_source` identifies how each
row was populated. Do not edit historical snapshot values in place; preserve a
new row under a new assessment ID for a reassessment.

The question.csv parent includes the canonical Day 2 question wording, evidence descriptions and acceptance criteria. Reconstructing the original bank in its original CSV format reproduced Git blob SHA `c9b525df9c46f133e83329ed12bd793b90cfd67f` exactly. To regenerate it after an upstream change, run `python sample-data/normalize_question_bank.py` from a repository checkout. No upstream question bank edit is required.

## Expected outputs and negative inputs

- `expected_domain_completeness.csv`: per-assessment verified and answered counts by domain, including the retained historical assessment. Management flag counts count vendors, not the number of findings. Seven open findings belong to six vendors; two decisions have open conditions.

- `expected_risk.csv`: exact integer numerator/denominator, percentage rounded to six decimals, raw provisional band and final displayed state. `expected_question_scores.csv`: question-level arithmetic. `expected_criticality.csv`: factor values, scores and override reasons for output comparison; it remains an expected-output oracle and is never used as a calculation source. Phase 2 uses `assessment_criticality_snapshot.csv` as its runtime factor input, then compares calculated results with the oracle.
- `invalid_vendor_cases.csv` and `invalid_evidence_cases.csv`: independent mutations, not source records. Reset the base data after each test. `expected_management.csv`: vendor IDs and totals to compare against a report.
- Join by keys, not row order. The current assessment pointer selects the current report; exclude Superseded from current counts; historical ASMT-004 evaluated at its own date, not at report date. Decision snapshot on VEN-006 remains Low although evidence later expired. Retain historical decisions separately from the current assessment's decision status.
- Unverified responses receive 4; confirmed critical failure receives 4 under the scoring-owner draft. A provisional numeric score is never a final risk rating. Approval is separate. See acceptance_cases.md for exact results and unresolved policy choices.

Run `python sample-data/validate_fixture.py` from the repository root (Python standard library only). The reference validator checks the fixture and expected results, not the Development toolkit or complete production-policy coverage.
