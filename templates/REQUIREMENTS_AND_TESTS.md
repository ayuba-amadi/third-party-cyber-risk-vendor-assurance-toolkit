# Research and QA working templates

Copy these tables into the phase files and fill them with actual values. Do not replace expected outputs with “works as designed.”

## Requirements traceability

| Requirement ID | Brief requirement / demo action | Input fields | Processing rule | Output / report field | Acceptance case ID | Owner | Status |
|---|---|---|---|---|---|---|---|
| R01 | Vendor register | Pending | Pending | Pending | T01 | Pending | Draft |

Use R01–R08 for required components; D01–D08 for mandatory demo-data scenarios; Q01–Q10 for live demonstration actions.

## Data dictionary

| Table | Field | Type | Required | Allowed values / constraint | Key or relationship | Example (fictional) |
|---|---|---|---|---|---|---|
| vendor | vendor_id | text | Yes | unique, immutable, nonblank | primary key | VEN-001 |

## Questionnaire row

| question_id | Domain | Wording | Answer choices | Weight / severity | Evidence artifact and period | Reviewer acceptance criteria | Critical failure? |
|---|---|---|---|---|---|---|---|
| AM-01 | Access management | Pending | Pending | Pending | Pending | Pending | Pending |

## Worked scoring case

| Case ID | Vendor/version | Raw inputs and evidence states | Rule and arithmetic | Expected criticality | Expected risk/completeness | Critical flags | Expected decision constraint |
|---|---|---|---|---|---|---|---|

## QA case and correction

| Test ID | Requirement ID | Input/precondition | Expected result | Actual result | Pass/fail | Defect/correction | Retest result and evidence |
|---|---|---|---|---|---|---|---|
