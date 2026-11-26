# Defect report template

Create one record per independently reproducible defect. Link it to the test case. Use only fictional data in the report and its attachments.

| Field | Entry |
|---|---|
| Defect ID | Unique ID, such as DEF-001 |
| Date discovered | Date and time in WAT (UTC+1) |
| Reporter | Name or role |
| Commit SHA | Exact affected version |
| Page or command | Page name or full command |
| Severity | Critical, High, Medium or Low |
| Preconditions | Environment, report date, session state and fictional IDs |
| Reproduction steps | Numbered actions from a clean or specified session |
| Expected result | Required outcome |
| Actual result | Observed outcome and exact error, if any |
| Evidence | Sanitised screenshot, log or export path |
| Impact | Affected workflow, records, results or demonstration |
| Proposed correction | Suggested change or investigation |
| Owner | Person responsible for the correction |
| Correction commit | SHA containing the fix |
| Retest date | Date and time in WAT |
| Retest result | Actual result, tested SHA and evidence for original and related cases |
| Closure decision | Open, reopened, closed or accepted with limitation, with reviewer and rationale |

## Severity and release rules

- **Critical** blocks use, causes data loss or invalidates risk results.
- **High** breaks a required workflow or required demonstration.
- **Medium** materially affects usability or reporting.
- **Low** is cosmetic or a minor documentation issue.

Release requires no unresolved Critical or High defects. Medium defects must be documented and accepted by the reviewer. Retest every corrected defect and link the evidence. QA sign-off must reference the tested commit SHA.

Every handoff includes the **file path, commit SHA, test result, reviewer, acceptance status and known limitations**.

## Project links

- [GitHub repository](https://github.com/ayuba-amadi/third-party-cyber-risk-vendor-assurance-toolkit) · [Live Streamlit application](https://icdfa-vendor-assurance-toolkit.streamlit.app)
- [User guide](../docs/user_guide.md) · [Project documentation](../docs/project_documentation.md) · [Deployment guide](../docs/deployment_guide.md)
- [Test register](../tests/TEST_REGISTER.md) · [Defect register](../tests/DEFECT_REGISTER.md) · [QA sign-off](../tests/QA_SIGNOFF.md)
- [Acceptance matrix](../reports/phase6/final_acceptance_matrix.md) · [Management reconciliation](../reports/phase6/reconciliation_report.md)
- [Presentation outline](../docs/presentation_outline.md) · [Demonstration script](../docs/demonstration_script.md)
- [Contribution record](../governance/FINAL_CONTRIBUTIONS.md) · [Submission rules](../governance/SUBMISSION_RULES.md)
