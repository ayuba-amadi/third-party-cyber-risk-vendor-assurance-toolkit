# Browser QA execution guide

**27 November–1 December 2026, inclusive. Deadline 1 December 2026, 23:59 WAT (UTC+1).**

The Streamlit web application is the primary operational toolkit and the mandatory surface for manual QA. It is the working vendor-assurance toolkit using fictional data. Use the browser to navigate, enter or import fictional vendor records, validate inputs, review criticality, process questionnaire responses, review evidence, inspect risk, record decisions, track remediation, compare reassessments, generate reports, review data quality and test responsive behaviour and usability.

## Getting started

1. Group 3 assigns a tester and reviewer and identifies the candidate commit. Ask the deployment owner which revision is hosted if the interface does not show it. Record an unknown version explicitly and establish the exact commit before sign-off.
2. Open the hosted toolkit at `https://icdfa-vendor-assurance-toolkit.streamlit.app`. If unavailable, save what the browser shows, record the time and reason, and open `http://127.0.0.1:8502` after starting the local app. UI-016 requires the hosted URL. [Hosted toolkit](https://icdfa-vendor-assurance-toolkit.streamlit.app)
3. Ask the QA coordinator to start the local app for you, or follow the [quick start](../README.md#quick-start). From the candidate checkout with dependencies installed, run `./.venv/bin/python -m streamlit run app/streamlit_app.py --server.headless true --server.port 8502`, then open the local URL in your browser.
4. Use the sidebar **Report date** of **18 November 2026** for baseline scenarios. Use **Reset session** between independent cases. Use the application controls first. You do not need to edit CSV files for browser QA. Use an approved fictional input file when testing the import control.
5. Use fictional data only. Keep real supplier evidence, credentials, personal data and confidential screenshots out of uploads, logs, downloads and attachments.

## Recording results

Use the [test case template](TEST_CASE_TEMPLATE.md) and append a row to the [execution log](../reports/qa/TEST_EXECUTION_LOG.csv) for every attempt. Include the test ID, tester name or role, WAT date and time, browser and device size, URL used, commit or deployment version, preconditions, exact browser steps, expected and actual results, status, screenshot or downloaded evidence path, defect ID if applicable, and retest result. Include both URLs and the reason if you switch to local.

Save screenshots as `QA-<TEST-ID>-<short-description>.png`. Save downloads with their original extension. Keep the original capture when retesting. [Evidence folders and examples](../reports/qa/evidence/)

- **PASS** requires observable browser evidence that the expected result occurred.
- **FAIL** means an observed result differs from the expected result. Record every failure in the current defect register and link its ID from the execution row.
- **BLOCKED** means a prerequisite prevents execution. Record the reason and any evidence, and identify who can unblock it.
- **NOT APPLICABLE** requires a specific reason the check does not apply.

Chat can alert the team. The defect register is the required record. Retest every correction in the browser and append a new execution row with its evidence and tested commit. Release requires zero unresolved Critical or High defects and documented acceptance of Medium defects. Independent sign-off must identify the exact tested commit. Preserve previous QA and completed phase records. [Current defect register](../reports/qa/DEFECT_REGISTER.md) · [Defect template](DEFECT_REPORT_TEMPLATE.md) · [QA handoff](../governance/HANDOFFS.md)

## Browser test matrix

Each case follows the same eight steps. Use the controls available in the candidate. If required coverage needs a prepared fictional record, ask the QA coordinator for one and record any blocked coverage.

### UI-001 — Open the toolkit

1. **What this test checks**. The application opens and shows its starting page.
2. **Where to go**. Open the hosted toolkit first. If it is unavailable, record the attempt, start the local app using Getting started and open the fallback URL.
3. **What to select**. Wait for **Dashboard**. Find the project title, sidebar and fictional-data notice.
4. **What to enter**. No values are needed.
5. **What should happen**. The Dashboard loads without a traceback. The title, sidebar and fictional-data notice are visible.
6. **What screenshot or file to save**. Save `QA-UI-001-dashboard-loaded.png`. If you used the fallback, also capture the hosted error.
7. **How to record the result**. Log the URL, version, load result, and the outage and fallback details if applicable.
8. **What to do if it fails**. Capture the failed page, record the result and link the startup or display defect.

### UI-002 — Navigate all pages

1. **What this test checks**. Each sidebar page opens.
2. **Where to go**. Start on **Dashboard** with the sidebar open.
3. **What to select**. Open these pages in order and wait for each heading and main content: **Dashboard**, **Vendor Register**, **Assessment**, **Evidence Review**, **Decisions**, **Remediation**, **Reassessment**, **Reports**, then **Data Quality**.
4. **What to enter**. No values are needed. If a page needs a vendor, use a fictional baseline record.
5. **What should happen**. All nine pages load without an application error.
6. **What screenshot or file to save**. Save one screenshot per page, such as `QA-UI-002-vendor-register-loaded.png`.
7. **How to record the result**. List all nine page results and evidence paths in UI-002.
8. **What to do if it fails**. Record the affected page and the preceding navigation step in the defect register.

### UI-003 — Vendor search and filtering

1. **What this test checks**. Search and filters narrow the vendor table.
2. **Where to go**. Open **Vendor Register**.
3. **What to select**. Use **Search vendors** first. Clear search before testing **Category**, **Criticality** and **Assessment status** separately. Then apply them together.
4. **What to enter**. Search for `VEN-003`, then `SalaryBridge`. Choose **Payroll**, the criticality shown for VEN-003 and **Reassessment due**. Try an incompatible combination too.
5. **What should happen**. Each result matches the search and active filters. Excluding all rows shows an empty result.
6. **What screenshot or file to save**. Save `QA-UI-003-filtered-table.png` and captures of the separate searches and filters.
7. **How to record the result**. Log search text, filter choices and returned vendor IDs.
8. **What to do if it fails**. Record the unexpected or missing rows and the exact filter combination.

### UI-004 — New vendor validation

1. **What this test checks**. The toolkit rejects missing required fields and duplicate vendor IDs.
2. **Where to go**. Open **Vendor Register**.
3. **What to select**. Choose **Add vendor** under **Record entry**. Complete the other required fields, leave the vendor name blank and select **Validate vendor**. Then try **Save vendor to session** and check the table. Fill in the name, replace the ID with an existing one, validate and repeat the save check.
4. **What to enter**. Use `VEN-011` first, then duplicate `VEN-001`. Use fictional information for all other fields.
5. **What should happen**. Both invalid entries show an error and are rejected. The vendor table and source data remain unchanged.
6. **What screenshot or file to save**. Save `QA-UI-004-required-field-rejected.png` and `QA-UI-004-duplicate-vendor-rejected.png`.
7. **How to record the result**. Log the exact errors and verify a search shows zero copies of VEN-011 and one unchanged VEN-001.
8. **What to do if it fails**. Record any missing message, accepted invalid save or unexpected row.

### UI-005 — Criticality recalculation

1. **What this test checks**. A change in vendor access or dependency changes criticality when the scoring warrants it.
2. **Where to go**. Open **Vendor Register**.
3. **What to select**. Choose **Add vendor** and select **Calculate criticality**. Record the first result and explanation. Change access and dependency one at a time and calculate after each change.
4. **What to enter**. Use fictional VEN-011 with **Internal** sensitivity, **None** access, dependency **2** and **Moderate** replaceability. Change access to **Privileged**, then dependency to **4**.
5. **What should happen**. The classification changes only when a threshold is crossed. The explanation identifies the changed factor. The baseline is 5 points (Medium) and the final combination is 9 points (High).
6. **What screenshot or file to save**. Save `QA-UI-005-criticality-before.png` and `QA-UI-005-criticality-explanation.png`.
7. **How to record the result**. Log each input change, score, band and explanation.
8. **What to do if it fails**. Record the settings and the unexpected score, band or explanation.

### UI-006 — Questionnaire and completeness

1. **What this test checks**. Missing and unverified questionnaire responses remain visible.
2. **Where to go**. Open **Assessment** and select VEN-002 / ASMT-002.
3. **What to select**. Use **Question domain** and **Question results** to review responses. Open **Questions needing completion or review** and **Domain counts**. Inspect AM-01 and DP-01 and the overall completeness result.
4. **What to enter**. Use the baseline responses. If testing entry, select a fictional vendor claim and choose **Save answer to session**, then review its verification status.
5. **What should happen**. Missing, incomplete and unverified responses remain visible and do not count as favourable evidence. ASMT-002 shows Incomplete with AM-01 and DP-01 needing attention.
6. **What screenshot or file to save**. Save `QA-UI-006-incomplete-responses.png` with the completeness and review details.
7. **How to record the result**. Log the assessment, questions, verification state and displayed completeness.
8. **What to do if it fails**. Record which question or count was missing or incorrectly credited.

### UI-007 — Evidence review

1. **What this test checks**. Vendor claims, reviewer answers and effective evidence status are distinct.
2. **Where to go**. Open **Evidence Review**, then select a vendor and assessment.
3. **What to select**. Select an **Evidence question** and review the vendor claim, reviewer-verified answer and reviewer note. Use **Evidence status** to show **Missing**, **Accepted**, **Rejected** and **Expired** one at a time. Check each row's effective status. Switch among fictional assessments as needed.
4. **What to enter**. Use baseline entries or a prepared fictional assessment. To check effective expiry, move **Report date** past the recorded expiry and restore it afterward.
5. **What should happen**. The display separates what the vendor said from what the reviewer verified. Each filter returns only its effective status at the selected date.
6. **What screenshot or file to save**. Save at least two different states, such as `QA-UI-007-missing-evidence.png` and `QA-UI-007-expired-evidence.png`.
7. **How to record the result**. Log all four filter results and the claims, reviewer values and effective statuses you observed.
8. **What to do if it fails**. Record the assessment, question, report date and incorrect status or unclear display.

### UI-008 — Critical weakness protection

1. **What this test checks**. A confirmed critical failure sets a minimum risk rating.
2. **Where to go**. Open **Assessment** and choose VEN-009 and its current assessment.
3. **What to select**. Open **Why this assessment result?** and find the confirmed critical weakness. Review other question results with strong responses and compare the calculated and final ratings.
4. **What to enter**. Use the baseline at 18 November 2026 and inspect DP-01.
5. **What should happen**. DP-01 is listed in the explanation and imposes at least High even when unrelated responses are strong.
6. **What screenshot or file to save**. Save `QA-UI-008-critical-weakness-floor.png`.
7. **How to record the result**. Log the question, raw and final ratings, and displayed reason.
8. **What to do if it fails**. Record any missing weakness or rating below the required floor as a defect.

### UI-009 — Human decision workflow

1. **What this test checks**. A human must confirm a decision, and conditional approval requires conditions and a deadline.
2. **Where to go**. Open **Decisions** and choose a current assessment awaiting a decision, such as VEN-004 / ASMT-011 with linked corrective action ACT-004.
3. **What to select**. Review the calculated result and existing decision state. Choose **Conditionally Approved** to exercise the required fields. Select **Review decision summary** with conditions blank, then try with a deadline missing. Complete the valid preview and verify no decision exists yet. Select **Confirm decision in session** and review the record. Inspect the **Approved** and **Rejected** choices without replacing the baseline.
4. **What to enter**. For ASMT-011, enter **Fictional Approver**, role **Risk director**, and justification **Fictional exception pending review of the subcontractor register**. Set decision date to `2026-11-18`, expiry date to `2027-01-01` and review date to `2026-12-01`. Select ACT-004. For the valid preview, enter **Review the subcontractor register and notification clause** as the condition and `2026-12-15` as the deadline.
5. **What should happen**. Calculation and preview create no decision. The form rejects missing conditions or deadline. Explicit confirmation records the valid decision.
6. **What screenshot or file to save**. Save `QA-UI-009-conditional-validation.png` and `QA-UI-009-confirmed-decision.png`, plus the preview state.
7. **How to record the result**. Log the selected assessment, missing-field results, preview state and confirmed outcome.
8. **What to do if it fails**. Record any automatic decision, missing validation or failure to save the confirmed decision.

### UI-010 — Remediation tracking

1. **What this test checks**. Open findings, overdue actions, closed actions and unresolved conditions are visible.
2. **Where to go**. Open **Remediation**.
3. **What to select**. Under **Show records**, choose **Open findings**, **Overdue actions**, **Closed actions** and **Unresolved conditions** in turn. Read each action's responsible party and deadline.
4. **What to enter**. Use 18 November 2026 and look for overdue action ACT-001.
5. **What should happen**. The filters show matching records. ACT-001 is overdue, and unresolved conditions are clearly identified.
6. **What screenshot or file to save**. Save `QA-UI-010-overdue-action-visible.png` and capture unresolved conditions.
7. **How to record the result**. Log each filter result and the relevant action IDs, parties and deadlines.
8. **What to do if it fails**. Record any incorrectly included or omitted record, with the report date.

### UI-011 — Reassessment and history

1. **What this test checks**. A new assessment version preserves the previous assessment.
2. **Where to go**. Open **Reassessment**.
3. **What to select**. Select VEN-004. Find **Assessment version comparison** and **Criticality factors and evidence differences**. Compare the current and previous versions, risk, criticality, history and material-change triggers.
4. **What to enter**. Use ASMT-004 and ASMT-011 and inspect CHG-001 and CHG-002.
5. **What should happen**. Both versions remain available with their own results and decision history. The current version has a distinct ID. The browser displays saved versions and comparisons.
6. **What screenshot or file to save**. Save `QA-UI-011-version-comparison.png` and the material-change details.
7. **How to record the result**. Log both assessment IDs, their results and the associated event IDs.
8. **What to do if it fails**. Record any missing version, mistaken change or overwritten historical result.

### UI-012 — Report generation

1. **What this test checks**. Reports show traceable tables and consistent downloads.
2. **Where to go**. Open **Reports**.
3. **What to select**. Choose **Individual vendor assessment**, select a vendor and assessment and choose **Generate report**. Review metadata, risk, findings, actions and decisions. Download CSV, JSON, Markdown and HTML and inspect them. Repeat for **Management summary** with **Include all vendors** selected. Trace management totals to their listed record IDs. Change **Report date** and regenerate to check the date and time-sensitive results.
4. **What to enter**. Use VEN-003 and the baseline date first, then choose a different report date.
5. **What should happen**. The tables and downloads agree on record IDs and report date. Management totals reconcile to the listed records without double-counting.
6. **What screenshot or file to save**. Save `QA-UI-012-individual-report.png`, `QA-UI-012-management-report.png` and all four formats for both reports.
7. **How to record the result**. Log the dates, vendor and assessment IDs, reconciled totals and download paths.
8. **What to do if it fails**. Record the report type, date, format and exact mismatching rows or IDs.

### UI-013 — Data quality

1. **What this test checks**. Validation shows source-table checks and actionable error and warning details.
2. **Where to go**. Open **Data Quality**.
3. **What to select**. Choose **Run validation**. Review **Source table checks**, summary counts and **Validation findings**. Use the severity and category filters. Open issue groups and read the field, record and correction. Repeat using a coordinator-prepared fictional dataset with an invalid record if the valid baseline has no errors.
4. **What to enter**. Start with the baseline. Use prepared fictional error or warning states where needed. Record any state you cannot reach.
5. **What should happen**. The page distinguishes Valid, Invalid, Incomplete and warnings and gives actionable correction guidance for issues.
6. **What screenshot or file to save**. Save `QA-UI-013-validation-result.png` and captures of each available issue state.
7. **How to record the result**. Log the counts, affected source tables and exact correction guidance. Mark unavailable required coverage BLOCKED.
8. **What to do if it fails**. Record missing or misleading guidance or incorrect states, including the record and field.

### UI-014 — Session isolation

1. **What this test checks**. Session edits clear when the session resets.
2. **Where to go**. Open **Vendor Register** and start with a reset session.
3. **What to select**. Choose **Add vendor**, validate and choose **Save vendor to session**. Search for the new ID and download the vendor record if available. Choose **Reset session**, reload **Vendor Register** and search again. Clear the search and compare the table with its starting state. If you downloaded a single-record CSV, choose **Import one CSV record**, upload it under **Fictional vendor CSV**, choose **Validate vendor**, and save it to the session. Confirm the record reappears, then reset again.
4. **What to enter**. Use a new fictional ID such as VEN-011 and complete the required fields.
5. **What should happen**. The fictional edit is visible before reset and absent afterward. The browser returns to the baseline. When a download is available, the exported one-record CSV can be imported through the browser and remains session-local.
6. **What screenshot or file to save**. Save `QA-UI-014-vendor-before-reset.png`, `QA-UI-014-vendor-after-reset.png` and the available export.
7. **How to record the result**. Log the ID, the results before and after reset, and the import and second reset if exercised. Source hashes can supplement the browser observations.
8. **What to do if it fails**. Record any lost edit before reset or surviving edit afterward.

### UI-015 — Mobile and accessibility review

1. **What this test checks**. The toolkit works at mobile width and communicates statuses with readable labels.
2. **Where to go**. Open the toolkit on a phone or set your browser to a viewport about 375 CSS pixels wide.
3. **What to select**. Open the sidebar, navigate to **Vendor Register** and **Remediation**, and scroll the page and wide tables. Check readable labels, status text, wrapping and clipping. On a keyboard, use Tab, Shift+Tab, Enter and Space to check focus and controls.
4. **What to enter**. Use a 375 px viewport and pick a view with status text and a wide table.
5. **What should happen**. Critical content stays reachable, tables scroll horizontally, focus is visible and statuses are understandable without relying on colour alone.
6. **What screenshot or file to save**. Save `QA-UI-015-mobile-layout.png` and any evidence of focus or clipping.
7. **How to record the result**. Log the viewport dimensions, browser, pages checked and what worked with keyboard and touch or pointer.
8. **What to do if it fails**. Record the size, page and exact control or content that becomes inaccessible.

### UI-016 — Public deployment smoke test

1. **What this test checks**. The public deployment serves the working toolkit.
2. **Where to go**. Open `https://icdfa-vendor-assurance-toolkit.streamlit.app`.
3. **What to select**. Load **Dashboard**, then open **Vendor Register**, **Evidence Review** and **Reports**. Check that each page renders its main controls and fictional data. Record the deployed version and any displayed deployment time.
4. **What to enter**. Use baseline records. Record the WAT time you observed the deployment and the exact hosted URL.
5. **What should happen**. The public toolkit renders all four pages without a traceback.
6. **What screenshot or file to save**. Save page captures, including `QA-UI-016-hosted-dashboard.png`. Capture any hosted error.
7. **How to record the result**. Log the observation time, page results, URL and deployed revision. Record separately if the deployment time is unavailable.
8. **What to do if it fails**. Record an observed hosted error as FAIL or a missing prerequisite that prevents execution as BLOCKED. The local fallback cannot pass UI-016.

## Supplementary terminal verification

Terminal and Python commands provide regression and integrity evidence only. A passing terminal test does not replace the required browser test for the same workflow.

Run the management report in a disposable copy of the tested revision because the command writes to `reports/phase4/`. Run the local health check with Streamlit running on port 8502.

```bash
source .venv/bin/activate
./.venv/bin/python -m unittest discover -s tests -v
./.venv/bin/python sample-data/validate_fixture.py
./.venv/bin/python -m src.cli management-report --as-of 2026-11-18
git diff --check
curl http://127.0.0.1:8502/_stcore/health
```

Record the WAT time, tested commit, exit status, test count and relevant output. Expect 33 passing management comparisons. To check that browser sessions preserve source data, run the following from the candidate checkout before and after testing.

```bash
hash_manifest=$(mktemp /tmp/toolkit-qa-csv.XXXXXX)
git ls-files -z -- '*.csv' ':!reports/**' | xargs -0 sha256sum > "$hash_manifest"
# Run the browser cases, then verify using the same manifest.
sha256sum -c "$hash_manifest"
```
