# Phase 1 structural CSV validation

Phase 1 validates data structure and relationships only. Risk scoring, criticality, decision workflow and Streamlit user pages are implemented in later phases.

Status: **PASS**

Execution date (UTC): 2026-11-26

Executed at (UTC): 2026-11-26T10:12:46.951449+00:00

Report date used: 2026-11-18

Repository data directory: /home/amadi/Documents/GitHub/third-party-cyber-risk-vendor-assurance-toolkit/sample-data

Command used: `python -m src.cli validate --data-dir sample-data --as-of 2026-11-18`

Physical CSV line (last line for a multiline record); 1 = header; 0 = file-level issue.

## Source-table inventory

| Table | File | Rows | Columns | Primary identifier | Classification | Loaded |
|---|---|---:|---:|---|---|---|
| vendor | sample-data/vendor.csv | 10 | 15 | vendor_id | source | True |
| business_service | sample-data/business_service.csv | 8 | 4 | service_id | source | True |
| vendor_service_link | sample-data/vendor_service_link.csv | 13 | 3 | vendor_id, service_id | source | True |
| assessment | sample-data/assessment.csv | 11 | 8 | assessment_id | source | True |
| question | sample-data/question.csv | 24 | 9 | question_id | source | True |
| response | sample-data/response.csv | 264 | 6 | assessment_id, question_id | source | True |
| evidence_item | sample-data/evidence_item.csv | 264 | 10 | evidence_id | source | True |
| finding | sample-data/finding.csv | 7 | 6 | finding_id | source | True |
| corrective_action | sample-data/corrective_action.csv | 4 | 8 | action_id | source | True |
| decision | sample-data/decision.csv | 8 | 11 | decision_id | source | True |
| change_event | sample-data/change_event.csv | 2 | 6 | change_id | source | True |
| reviewer_audit_entry | sample-data/reviewer_audit_entry.csv | 535 | 7 | audit_id | source | True |

## Validation summary

| Measure | Count |
|---|---:|
| files loaded | 12 |
| source tables | 12 |
| valid tables | 12 |
| errors | 0 |
| warnings | 0 |
| duplicates | 0 |
| orphans | 0 |
| missing fields | 0 |
| invalid values | 0 |
| date errors | 0 |
| files | 0 |
| duplicate records | 0 |
| orphan records | 0 |

## Errors

NONE

## Warnings

NONE

## Research fixture validator

Run separately with `python3 sample-data/validate_fixture.py`. This CLI does not execute it. See PHASE_1_STATUS.md for the recorded result.

## Limitations

- Phase 1 validates data structure and relationships only. Risk scoring, criticality, decision workflow and Streamlit user pages are implemented in later phases.
- Expected outputs, negative-test cases and validation_results.txt are reference files, not source inputs.
- All rows remain in memory, including invalid rows. An error means the data is not ready for later processing.
- Dates are checked for format and ordering; overdue, expiry and completeness flags are later-phase behavior.
- The schema has no onboarding, finding-creation or action-creation dates; comparisons requiring these dates cannot be checked. Closing an action before its due date is valid.
- Evidence review time is held in reviewer_audit_entry.timestamp; review_period_end is the covered period, not the review date. Fictional evidence paths are not opened.
- Evidence pairs are unique in this fixture, as enforced by its research validator. Replacement-evidence history and composite-key audit references need schema-owner resolution before later workflow work.
- Historical criticality factors exist only in an expected-output file; that file is not loaded as a source.
- Scoring, approval authority and independence, workflow transitions, remediation management, vendor/management reports and GUI are outside Phase 1. A structural pass is not policy approval.
