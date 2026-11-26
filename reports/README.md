# Validation reports

`python -m src.cli validate` creates `phase1/validation_report.json` and
`phase1/validation_report.md`. Use `python3` if needed. Each run replaces these
generated reports so analysts can review structure, row counts and exact errors.
Use `--reports-dir /tmp/phase1-reports` to keep a separate run.

Reports record the actual execution date/time in UTC and the chosen report date
separately. The reproducible report-date default is 2026-11-18; use `--as-of
YYYY-MM-DD` to override it. A different report date does not change CSV data or
create later-phase overdue flags. Only the 12 approved source tables are validated.

JSON and Markdown contain the same inventory, summary, errors, warnings, limits
and command. File/header issues use rows 0/1. Duplicate/orphan record counts are
distinct affected rows; category totals count rule violations. Valid-table counts
are structural results, not evidence of vendor approval or assessment completeness.
The research validator runs separately, with its result in the Phase 1 status file.

Phase 1 validates data structure and relationships only. Risk scoring, criticality, decision workflow and Streamlit user pages are implemented in later phases.

Individual vendor and management reports belong to a later phase. Store fictional
data only; never include real vendor evidence, personal details or credentials.
