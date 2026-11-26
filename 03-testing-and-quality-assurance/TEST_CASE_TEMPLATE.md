# Browser test case template

Use one entry per attempt and append a row to the [execution log](../reports/qa/TEST_EXECUTION_LOG.csv). All manual steps take place in the Streamlit browser interface.

| Field | Entry |
|---|---|
| Test ID | Matrix ID, such as UI-001 |
| Tester name or role | |
| Date and time in WAT (UTC+1) | |
| Browser and device size | Browser and version, device or viewport width × height in CSS pixels |
| URL used | Include the hosted failure and local URL if you switch |
| Exact repository commit or deployment version | Record an unknown hosted revision explicitly |
| Preconditions | Starting page, session state, report date and fictional record IDs |
| Exact browser steps | Number each click, selection and value entered |
| Expected result | |
| Actual result | Include the exact message, record ID or displayed result |
| Status | PASS, FAIL, BLOCKED or NOT APPLICABLE |
| Screenshot or download evidence path | Use `QA-<TEST-ID>-<short-description>.png` for screenshots |
| Defect ID, if applicable | |
| Retest result | Status, WAT time, tested commit and evidence path, or pending if applicable |

Mark PASS only with observable browser evidence. Record the reason for BLOCKED or NOT APPLICABLE. Keep the first observation and log retests as new attempts. Use fictional data only and link every failure to the [current defect register](../reports/qa/DEFECT_REGISTER.md). [Execution guide](TEST_EXECUTION_GUIDE.md) · [Defect template](DEFECT_REPORT_TEMPLATE.md)
