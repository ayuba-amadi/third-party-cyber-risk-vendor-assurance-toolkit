# Testing and Quality Assurance — 72-hour work package

**Window:** Sunday 22 November to Tuesday 24 November 2026, 23:59 WAT. **Input:** development candidate and approved research acceptance cases. **Handoff:** tested release candidate and defect register to Documentation and Presentation/team lead.

## Day 1 — Sunday: independent setup and baseline

1. Download a clean copy and follow only the supplied user guide. Record environment, commands, dependencies, actual outputs and any setup defect.
2. Verify file inventory, ten unique fictional vendors across five categories, three critical dependencies and 24+ answered questions per vendor.
3. Independently calculate at least one Low, Medium, High and Critical criticality example and compare threshold/reason output.
4. Verify duplicate IDs, missing required values, invalid enumerations, malformed dates and orphan references produce actionable errors without corrupting valid records.
5. Start `tests/TEST_REGISTER.md`: case ID, requirement ID, input/precondition, expected result, actual result, pass/fail, evidence path/screenshot, defect ID, retest result.

## Day 2 — Monday: security and workflow edge cases

1. Check vendor claim versus reviewer verification, all evidence states (Missing, Received, Accepted, Rejected, Expired), expiry date logic and incomplete flags.
2. Use the high-scoring vendor with a critical failure to prove that the weakness and approval restriction remain visible.
3. Record approved, conditional and rejected decisions, decision-maker and justification. Confirm score does not automatically approve.
4. Create overdue corrective action, condition and review; expire an approval; change access/dependency to trigger criticality change; perform material-change reassessment and confirm previous version remains readable.
5. Validate report reasons, source IDs and period dates. Log defects with severity, reproduction steps, expected/actual, owner and commit fixing it. Retest only after a fix is available.

## Day 3 — Tuesday: reporting, regression and release gate

1. Reconcile every management total to a list of underlying distinct vendor IDs, findings, actions or conditions. Check the concentrated supplier supports several services without inflating unique-vendor totals.
2. Run the complete live demonstration checklist in the README from a clean state. Capture actual outputs and screenshots for the PDF.
3. Rerun automated tests and the cases affected by fixes. Record expected, actual, correction and retest evidence; do not mark an unrun case Pass.
4. Publish a concise QA sign-off with pass/fail counts, unresolved blockers, known limitations, tested commit/version, reviewer and date by **23:59 WAT**.

## Release criteria

No unresolved blocker or high-severity defect in ID uniqueness, scoring, critical-failure flags, evidence treatment, history, decisions or report reconciliation. All required demonstration actions must pass, or the team lead records a visible limitation and corrective plan before presentation. QA does not approve its own unverified assertions.

## Test files

Use `tests/TEST_REGISTER.md`, `tests/DEFECT_REGISTER.md`, `tests/QA_SIGNOFF.md` and reproducible synthetic fixtures. Suggested severity: Blocker (cannot use/report), High (misleading assurance outcome), Medium (workflow impaired), Low (cosmetic).
