# Test case template

Copy this table into the register for the candidate run. Use a new case ID or an explicit rerun entry. **No test may be marked PASS without observed evidence.**

| Field | Description | Entry |
|---|---|---|
| Test ID | Unique identifier, such as QA-E-01 | |
| Category | Functional, regression, security, usability or deployment | |
| Requirement | Related requirement or demonstration | |
| Tester | Name or role | |
| Date and time | Date and time in WAT (UTC+1) | |
| Commit SHA | Exact version tested | |
| Preconditions | Required setup, environment, report date and session state | |
| Test data | Fictional vendor, assessment or fixture IDs | |
| Steps | Exact numbered actions or commands | |
| Expected result | Required outcome, established before execution | |
| Actual result | Observed outcome, including messages and values | |
| Status | PASS, FAIL, BLOCKED or NOT APPLICABLE | |
| Evidence | Screenshot, log or export path | |
| Defect ID | Linked defect if failed | |
| Retest result | Result after correction, with date, commit SHA and evidence | |

Record why a case is BLOCKED or NOT APPLICABLE. Keep the first observation when adding a retest. Follow the [execution guide](TEST_EXECUTION_GUIDE.md) and [defect template](DEFECT_REPORT_TEMPLATE.md).

Every handoff includes the **file path, commit SHA, test result, reviewer, acceptance status and known limitations**.

## Project links

- [GitHub repository](https://github.com/ayuba-amadi/third-party-cyber-risk-vendor-assurance-toolkit) · [Live Streamlit application](https://icdfa-vendor-assurance-toolkit.streamlit.app)
- [User guide](../docs/user_guide.md) · [Project documentation](../docs/project_documentation.md) · [Deployment guide](../docs/deployment_guide.md)
- [Test register](../tests/TEST_REGISTER.md) · [Defect register](../tests/DEFECT_REGISTER.md) · [QA sign-off](../tests/QA_SIGNOFF.md)
- [Acceptance matrix](../reports/phase6/final_acceptance_matrix.md) · [Management reconciliation](../reports/phase6/reconciliation_report.md)
- [Presentation outline](../docs/presentation_outline.md) · [Demonstration script](../docs/demonstration_script.md)
- [Contribution record](../governance/FINAL_CONTRIBUTIONS.md) · [Submission rules](../governance/SUBMISSION_RULES.md)
