# Toolkit Development — 72-hour work package

**Window:** Thursday 19 November to Saturday 21 November 2026, 23:59 WAT. **Input:** accepted research-spec-v1.0 and fictional sample data. **Handoff:** runnable tagged candidate to Testing and Quality Assurance. Record contributors in `governance/CONTRIBUTIONS.md`.

## Day 1 — Thursday: executable foundation

1. Confirm the accepted data dictionary, scoring methods and acceptance cases. Log ambiguities in `governance/HANDOFFS.md`; do not silently invent policy thresholds.
2. Choose and document the implementation: Python CLI, Excel workbook, or other suitable method. A web app is optional. If using GitHub Pages, remember it is public static hosting; no real supplier evidence, secrets or access-controlled case files belong there.
3. Build input/import validation: immutable unique vendor IDs, connected assessment IDs, required fields, allowed enumerations, valid dates, duplicate IDs, orphan references, and an error report that identifies record and field. Preserve original assessment versions.
4. Implement the vendor register and multi-service dependency data, criticality rules, questionnaire response and evidence registers using the approved schema.
5. Commit source code, sample input, dependency versions and execution commands. Keep inputs, calculations and reports separate.

**Day 1 exit:** a fresh checkout can import the ten fictional vendors, reject invalid inputs, calculate criticality and display reasons.

## Day 2 — Friday: assurance workflow and calculations

1. Implement evidence review separately from vendor claims. Only accepted, current evidence can support a verified favourable response; missing, received-only, rejected and expired evidence produce the documented incomplete/adverse treatment.
2. Calculate weighted risk, completeness and critical-failure flags exactly as specified; expose each factor and source IDs in a vendor report. Test a critical failure with otherwise excellent responses.
3. Implement authorised decisions (Approved, Conditionally Approved, Rejected) with reviewer, justification, conditions, deadline, review and expiry. The score informs but never automatically makes the final decision.
4. Implement corrective actions, owners, deadlines, previous assessment history, material-change flag, reassessment comparison, expired approval, overdue review and overdue condition.
5. Generate a management summary of critical vendors, unresolved findings, overdue assessments/actions, outstanding conditions and supplier concentration. Include a source-ID drilldown or reconciliation list behind every count.

**Day 2 exit:** a user can run the ten-vendor data end to end and inspect an individual report and consolidated totals.

## Day 3 — Saturday: complete, package, hand over

1. Fix deviations from the accepted research cases; add focused unit/integration tests for calculations and edge cases.
2. Provide a one-command or clearly sequenced run path and a reproducible sample run. Pin dependencies or state supported version; no real service credentials should be required for the demo.
3. Produce output examples under `reports/examples/` (individual vendor and management report). Add a visible “fictional demonstration data” notice.
4. Document storage/access control: operational files in a restricted organisation location; authorised reviewers record decisions; evidence referenced by protected path, not embedded in public repo; versioned exports and backups. Public GitHub contains only synthetic examples.
5. Conduct the ten demonstration actions in the root README and record result, command/screen and remaining defects. Tag or identify candidate commit `dev-candidate-v1`; hand off by **23:59 WAT**.

## Acceptance gate

QA must be able to clone/download and run without undocumented manual edits; every required output is generated from connected source IDs; all ten vendors and all question rows process; critical weaknesses remain visible; previous assessments survive reassessment; invalid data is reported rather than silently scored; calculations reconcile to reports. Unfinished features must be listed with severity and owner.

## File layout target

`src/` or `workbook/` for implementation; `sample-data/` for fictional inputs; `tests/` for automated checks; `reports/examples/` for generated examples; `docs/USER_GUIDE.md` for run and operating instructions. Keep the build approach flexible until research handoff is approved.
