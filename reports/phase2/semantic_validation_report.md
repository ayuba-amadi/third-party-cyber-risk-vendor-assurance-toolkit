# Phase 2 semantic validation

Phase 2 implements semantic validation and vendor criticality calculation only. Risk scoring, evidence scoring, decision workflow, remediation workflow, management reporting and the Streamlit interface are later-phase work.

Status: **PASS**

Execution date (UTC): 2026-11-26

Report date: 2026-11-18

Source directory: /home/amadi/Documents/GitHub/third-party-cyber-risk-vendor-assurance-toolkit/sample-data

## Summary

| Measure | Count |
|---|---:|
| files loaded | 13 |
| source tables | 13 |
| valid tables | 13 |
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

## Overdue corrective actions

| Action | Finding | Vendor | Due date | Status |
|---|---|---|---|---|
| ACT-001 | FND-003 | VEN-003 | 2026-10-31 | Open |

## Validation errors

NONE

## Limitations

- Validation checks the supplied CSV state; it cannot recover a prior file version that was never preserved.
- Evidence record IDs, audit events and assessment versions provide the available history trail.
- This phase does not calculate security risk, evidence scores or decisions.
