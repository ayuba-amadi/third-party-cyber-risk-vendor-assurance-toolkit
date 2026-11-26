# QA test execution guide

**27 November–1 December 2026, inclusive. Deadline 1 December 2026, 23:59 WAT (UTC+1).** Group 3 coordinates testing and independent review. Every project member is encouraged to test and report observations.

Choose a candidate SHA and assign case IDs, testers and reviewers before running checks. Use the [QA workplan](WORKPLAN.md), [test case template](TEST_CASE_TEMPLATE.md) and [defect report template](DEFECT_REPORT_TEMPLATE.md). Set the report date to **18 November 2026** unless a case calls for a different date. Reset the session between independent cases. Record browser, viewport, OS, Python and Streamlit versions so reviewers can reproduce the run.

## A. Environment and startup

1. Use a clean checkout of the candidate SHA. Follow the [quick start](../README.md#quick-start) to create or activate `.venv` and install dependencies. Record `git rev-parse HEAD`, `git status --short` and the interpreter version. Use a disposable checkout for commands that write under `reports/`. Keep evidence outside that checkout until it is reviewed.
2. Run `./.venv/bin/python -c 'import streamlit; import app.streamlit_app; import src.cli'`. Expect exit status 0.
3. Start the app with `./.venv/bin/python -m streamlit run app/streamlit_app.py --server.headless true --server.port 8501`. In a separate Bash terminal, run the following. Expect HTTP success and an exact body of `ok`.

   ```bash
   set -o pipefail
   curl -fsS http://127.0.0.1:8501/_stcore/health | cmp - <(printf 'ok')
   ```

4. Open the local URL. Confirm that the app starts with the bundled CSVs and no secrets or configured external service. The dependency installation and hosted demo separately use network access. Complete the privacy checks in L.

## B. Automated regression

From the repository root, run the following commands. Capture stdout, stderr and each exit status separately. Use `TZ=Africa/Lagos date '+%Y-%m-%d %H:%M:%S %Z'` to timestamp the run.

```bash
source .venv/bin/activate
./.venv/bin/python -m unittest discover -s tests -v
./.venv/bin/python sample-data/validate_fixture.py
./.venv/bin/python -m src.cli management-report --as-of 2026-11-18
git diff --check
```

| Command | Expected result |
|---|---|
| unittest discovery | Exit 0, no failures or errors. Record totals and explain skips. |
| Fixture validator | Exit 0 and PASS for structural checks and independent fixture comparisons. |
| Dated management report | Exit 0 and PASS for 33 expected rows. Retain outputs from `reports/phase4/` as evidence for this run. |
| Git diff check | Exit 0 with no whitespace errors. Inspect the diff separately for expected changes. |

For each command record the **command, date and time in WAT, commit SHA, expected result, actual result, pass/fail status and evidence path**. Log missing dependencies or blocked environments and retest after correction.

## C. Page loads

Open every page from the sidebar. For each page verify the heading, sidebar, fictional data and absence of tracebacks or secrets. Set a filter or selection and check it survives ordinary reruns where supported. Verify the shared vendor and report date carry over on relevant pages. Revisit pages to confirm selections behave as documented for the session. Check the relevant download when offered and mark the download check NOT APPLICABLE with a reason on pages without one.

| Page | Quick check |
|---|---|
| Dashboard | Verify portfolio metrics and attention flags against the baseline. |
| Vendor Register | Find VEN-003 by search and filter, then open the vendor CSV. |
| Assessment | Select a current assessment and view the question and domain results. |
| Evidence Review | Open a missing or rejected item and check effective status. |
| Decisions | Check recorded outcomes and the current assessment selection. |
| Remediation | Filter overdue actions and open the corrective-action CSV. |
| Reassessment | Compare ASMT-004 and ASMT-011 for VEN-004. |
| Reports | Generate an individual and a management report. Open the exports. |
| Data Quality | Open source table checks and review correction guidance for any issue. |

Run all ten actions in the [demonstration script](../docs/demonstration_script.md) and the invalid-input demonstration in D and K. Map the observed results to the requirements in the [acceptance matrix](../reports/phase6/final_acceptance_matrix.md).

## D. Vendor Register

1. Search by existing vendor ID or name. Exercise category, criticality and assessment-status filters individually and together. Confirm matching IDs and the empty result when filters exclude all rows.
2. Add fictional VEN-011 with Internal sensitivity, None access, dependency 2 and Moderate replaceability. Expect 5 points and Medium. Change access and dependency separately, observing the factor points after each change. With Privileged access and dependency 4, expect 9 points and High under the demonstration setup.
3. Validate duplicate VEN-001 and a row with a missing required field. Expect rejection with a correction message and no new record. Exercise invalid options with the [invalid vendor cases](../sample-data/invalid_vendor_cases.csv) in a disposable fixture copy when the form restricts inputs to allowed choices.
4. Save a valid new vendor and check the record is available in the same session and vendor export. Open a fresh session or reset to confirm that the bundled baseline remains unchanged.

## E. Assessment and risk

1. Select a questionnaire domain and question. Save a valid response. Try an invalid response in a disposable copy if the selector prevents invalid entry. Verify rejection. Remove a response only in a disposable copy and verify missing-response detection.
2. Compare evidence completeness, verified question counts by domain, risk percentage, raw band and final rating with [expected risk](../sample-data/expected_risk.csv), [question scores](../sample-data/expected_question_scores.csv) and [domain completeness](../sample-data/expected_domain_completeness.csv).
3. Verify ASMT-002 remains Incomplete with missing AM-01 and DP-01. Use VEN-009 to confirm that a DP-01 critical failure produces at least High even when unrelated scores are strong. Record the displayed calculation and override reason.

## F. Evidence

1. Test Missing, Received, Accepted, Rejected and Expired. Use baseline records or isolated session edits. Confirm each effective status and its impact on verification at the selected report date.
2. Compare a vendor claim with a different reviewer answer. Check that the claim alone cannot verify a response. Try saving without the required reviewer note or required evidence reference. Expect an actionable rejection when the applicable rule requires either.
3. Try invalid expiry dates and date ordering. Move the report date past a valid expiry to check effective Expired status. Capture the underlying recorded state and the effective display.

## G. Decisions

1. Inspect Approved, Conditionally Approved and Rejected baseline outcomes. For new entry use a current assessment awaiting decision. Check required fictional decision-maker and justification fields, date validity, conditional deadline and corrective-action linkage.
2. Preview a valid decision. Verify that preview leaves the outcome unrecorded until explicit confirmation. Confirm and verify the decision record and the linked action where applicable.
3. Change a questionnaire or calculate a favourable rating. Verify the calculation does not grant approval. Attempt ordinary approval for a confirmed critical failure and verify the workflow rejects it.

## H. Remediation

1. Filter open findings, open and closed actions, overdue actions, actions due soon and unresolved conditions. Verify ACT-001 is overdue on the baseline report date. Due soon covers the report date through the next 30 days.
2. Enter or edit a fictional action in a session. Check responsible party and deadline, then attempt closure without a closure date. Record the corrective message, enter a valid closure date and verify the closed status.
3. Download corrective actions and match the action ID, linked finding, responsible party, due date, closure date and status to the selected record.

## I. Reassessment

1. Select VEN-004 and compare ASMT-004 and ASMT-011. Check CHG-001 and CHG-002, changed criticality/risk, prior assessment details and the historical decision.
2. Exercise a material-change trigger and reassessment due status. Use the existing events or a disposable fictional dataset for controlled version creation. Verify that the new current version links to the previous version, keeps its own result and leaves the earlier assessment and decision intact. Follow the controlled-entry steps in the [user guide](../docs/user_guide.md).

## J. Reporting

1. Generate an individual vendor report and a consolidated management report. Compare critical suppliers, unresolved weaknesses, overdue assessments and outstanding conditions to their source IDs. Check concentration for a supplier linked to multiple important services and reconcile each relevant total or distinct vendor set without double-counting.
2. Compare management totals and IDs with [expected management results](../sample-data/expected_management.csv) and the [management reconciliation](../reports/phase6/reconciliation_report.md). Record the exact IDs behind any difference.
3. Open CSV, JSON, Markdown and HTML downloads. Compare IDs, narrative and report dates across formats. Change the date and regenerate the report to verify overdue and expiry recalculation. Reset the date before comparing the baseline.

## K. Data quality

In a disposable copy, run one invalid case at a time. Check duplicate IDs, missing required values, invalid dates, invalid allowed values, broken foreign keys, incomplete assessments and invalid evidence states. Use the [validation and CLI guide](../src/README.md) and the bundled negative fixtures. Verify that error or warning messages identify the field or record, explain the issue and offer a correction.

To exercise management-report mismatch, alter one expected comparison value in the disposable copy and rerun the dated report command. Expect a failed comparison and identify the mismatching row. Keep the mismatch evidence separate from baseline output.

## L. Security and privacy

Review the candidate source, configuration, fixture references, logs, screenshots and downloads for fictional data only. Confirm there are no committed credentials or tokens, personal details or real vendor evidence. Review the app's inputs and storage. Confirm it uses local CSVs and session state, with no hidden database or network write required for the core workflow. Validate hosted content separately using the public demo and record whether the deployed revision could be identified.

Before running cases, capture hashes from the candidate checkout. Re-run the check afterward, including after a save, export and reset. Run both commands from the same repository root.

```bash
hash_manifest=$(mktemp /tmp/toolkit-qa-csv.XXXXXX)
git ls-files -z -- '*.csv' | xargs -0 sha256sum > "$hash_manifest"
# Run the QA scenarios, then verify.
sha256sum -c "$hash_manifest"
```

The management command generates report CSVs. To test source immutability inside the disposable checkout, use the same manifest procedure there with `git ls-files -z -- '*.csv' ':!reports/**'`. The all-CSV manifest for the original checkout should still match. If a secret is suspected, report through the team's private channel and keep the value out of the public artifact.

## M. Accessibility and usability

Use a desktop viewport and a mobile viewport, such as 375 px wide. Verify the light-grey background, readable contrast, clear project title, navigation groups and understandable instructions. Navigate with Tab, Shift+Tab, Enter and Space. Check visible focus and written labels alongside colour cues. Confirm cards align on desktop and stack or wrap on mobile, including Remediation badges. Confirm the page stays within its viewport and wide tables can be scrolled horizontally without clipping. Check consistent table-column alignment, centred headings and left-aligned long descriptions, questions and mixed report Value columns.

## Evidence, defects and sign-off

1. Keep evidence in a new run location named for the candidate SHA and WAT date. Use the case ID in filenames and link the log, screenshot or export. Keep the expected result and initial observation when adding retest results. The existing [test register](../tests/TEST_REGISTER.md), [defect register](../tests/DEFECT_REGISTER.md) and [QA sign-off](../tests/QA_SIGNOFF.md) remain evidence for their recorded versions.
2. Use PASS only with observed evidence. Use FAIL for a mismatch, BLOCKED when a prerequisite prevents execution, and NOT APPLICABLE with a reason when a check is outside the case. Record defects with impact and severity. Retest every correction on its correction SHA and repeat related checks on the release candidate.
3. Obtain independent sign-off against the tested commit SHA. Record the run environment, case totals, defects, retest evidence, limitations, reviewer and recommendation. Release requires no unresolved Critical or High defects and documented reviewer acceptance of Medium defects.
4. Send Group 4 and the team lead the **file path, commit SHA, test result, reviewer, acceptance status and known limitations**. Link the evidence through the [handoff register](../governance/HANDOFFS.md).

## Project links

- [GitHub repository](https://github.com/ayuba-amadi/third-party-cyber-risk-vendor-assurance-toolkit) · [Live Streamlit application](https://icdfa-vendor-assurance-toolkit.streamlit.app)
- [User guide](../docs/user_guide.md) · [Project documentation](../docs/project_documentation.md) · [Deployment guide](../docs/deployment_guide.md)
- [Test register](../tests/TEST_REGISTER.md) · [Defect register](../tests/DEFECT_REGISTER.md) · [QA sign-off](../tests/QA_SIGNOFF.md)
- [Acceptance matrix](../reports/phase6/final_acceptance_matrix.md) · [Management reconciliation](../reports/phase6/reconciliation_report.md)
- [Presentation outline](../docs/presentation_outline.md) · [Demonstration script](../docs/demonstration_script.md)
- [Contribution record](../governance/FINAL_CONTRIBUTIONS.md) · [Submission rules](../governance/SUBMISSION_RULES.md)
