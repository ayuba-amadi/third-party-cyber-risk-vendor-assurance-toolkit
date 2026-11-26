# QA workplan

**27 November–1 December 2026, inclusive. Deadline 1 December 2026, 23:59 WAT (UTC+1).**

Group 3 coordinates assignments and independent review. Every project member is encouraged to run cases and report observations. Assign an owner and reviewer to each case before starting. Use the [execution guide](TEST_EXECUTION_GUIDE.md) and the [test case](TEST_CASE_TEMPLATE.md) and [defect](DEFECT_REPORT_TEMPLATE.md) templates.

| Date | Work | Required output |
|---|---|---|
| 27 Nov | Pin the candidate SHA. Install from a clean checkout, run automated checks, verify hashes and load all nine pages. | Environment record, command logs, baseline hashes and page-load evidence |
| 28 Nov | Exercise vendor registration, criticality, questionnaires, evidence and human decision outcomes. | Expected and actual results, screenshots and defect IDs |
| 29 Nov | Test remediation, reassessment, invalid input, reporting, exports and source-ID reconciliation. | Edge-case records, export samples and reconciled totals |
| 30 Nov | Run all ten demonstrations and review desktop, mobile, keyboard and fictional-data controls. Retest fixes and related workflows. | Demo coverage, privacy and accessibility findings, and retest evidence |
| 1 Dec | Close or escalate defects, repeat checks for changed code and review the exact candidate SHA. | Completed test and defect registers, retest evidence and QA recommendation |

Release requires no unresolved Critical or High defects. Document and obtain reviewer acceptance for Medium defects. Retest every corrected defect and record the correction SHA and result. If evidence is missing, record the case as BLOCKED and identify the owner and next action. The sign-off must identify the tested commit. Preserve the prior evidence and its original dates and results.

Send the team lead and Group 4 the completed [handoff entry](../governance/HANDOFFS.md) with the **file path, commit SHA, test result, reviewer, acceptance status and known limitations**.

## Project links

- [GitHub repository](https://github.com/ayuba-amadi/third-party-cyber-risk-vendor-assurance-toolkit) · [Live Streamlit application](https://icdfa-vendor-assurance-toolkit.streamlit.app)
- [User guide](../docs/user_guide.md) · [Project documentation](../docs/project_documentation.md) · [Deployment guide](../docs/deployment_guide.md)
- [Test register](../tests/TEST_REGISTER.md) · [Defect register](../tests/DEFECT_REGISTER.md) · [QA sign-off](../tests/QA_SIGNOFF.md)
- [Acceptance matrix](../reports/phase6/final_acceptance_matrix.md) · [Management reconciliation](../reports/phase6/reconciliation_report.md)
- [Presentation outline](../docs/presentation_outline.md) · [Demonstration script](../docs/demonstration_script.md)
- [Contribution record](../governance/FINAL_CONTRIBUTIONS.md) · [Submission rules](../governance/SUBMISSION_RULES.md)
