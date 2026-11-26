# QA workplan

**27 November–1 December 2026, inclusive. Deadline 1 December 2026, 23:59 WAT (UTC+1).**

Group 3 coordinates assignments and independent review. Every project member is encouraged to run cases and report observations. Assign an owner and reviewer to each case before starting. Use the [execution guide](TEST_EXECUTION_GUIDE.md) and the [test case](TEST_CASE_TEMPLATE.md) and [defect](DEFECT_REPORT_TEMPLATE.md) templates.

Use the Streamlit browser interface for every manual test. Start on the hosted toolkit and record any switch to the local fallback at `http://127.0.0.1:8502`. Terminal checks are supplementary. The public deployment smoke test requires the hosted URL. [Hosted toolkit](https://icdfa-vendor-assurance-toolkit.streamlit.app)

| Date | Browser work | Required output |
|---|---|---|
| 27 Nov | Pin the candidate SHA and run UI-001, UI-002 and UI-016. | Browser setup, nine page captures and public deployment result |
| 28 Nov | Run UI-003 through UI-009 for vendor records, criticality, questionnaires, evidence, risk and decisions. | Execution rows, screenshots and defects |
| 29 Nov | Run UI-010 through UI-014 for remediation, reassessment, reports, validation and session isolation. | Comparison captures, download samples and log entries |
| 30 Nov | Run UI-015. Rehearse the ten presentation scenarios in the browser and retest fixes and related workflows. | Mobile and keyboard observations, coverage and retest evidence |
| 1 Dec | Retest on the release candidate, review defects and sign off by 23:59 WAT. | Completed execution log, defect register, evidence and independent recommendation |

Use the [current QA records](../reports/qa/) for results and [supplementary checks](../tests/README.md) for automated regression and source CSV integrity.

Release requires no unresolved Critical or High defects. Document and obtain reviewer acceptance for Medium defects. Retest every corrected defect and record the correction SHA and result. If evidence is missing, record the case as BLOCKED and identify the owner and next action. The sign-off must identify the tested commit. Preserve the prior evidence and its original dates and results.

Send the team lead and Group 4 the completed [handoff entry](../governance/HANDOFFS.md) with the **file path, commit SHA, test result, reviewer, acceptance status and known limitations**.

## Project links

- [GitHub repository](https://github.com/ayuba-amadi/third-party-cyber-risk-vendor-assurance-toolkit) · [Live Streamlit application](https://icdfa-vendor-assurance-toolkit.streamlit.app)
- [User guide](../docs/user_guide.md) · [Project documentation](../docs/project_documentation.md) · [Deployment guide](../docs/deployment_guide.md)
- [Test register](../tests/TEST_REGISTER.md) · [Defect register](../tests/DEFECT_REGISTER.md) · [QA sign-off](../tests/QA_SIGNOFF.md)
- [Acceptance matrix](../reports/phase6/final_acceptance_matrix.md) · [Management reconciliation](../reports/phase6/reconciliation_report.md)
- [Presentation outline](../docs/presentation_outline.md) · [Demonstration script](../docs/demonstration_script.md)
- [Contribution record](../governance/FINAL_CONTRIBUTIONS.md) · [Submission rules](../governance/SUBMISSION_RULES.md)
