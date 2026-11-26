# Testing and Quality Assurance

**27 November–1 December 2026, inclusive. Deadline 1 December 2026, 23:59 WAT (UTC+1).**

Group 3 coordinates coverage, assignment, defect triage and independent QA review. Every project member is encouraged to test and report observations. Testers record what they observe on the candidate commit and link evidence for every PASS.

The Streamlit web application is the primary operational toolkit and the mandatory surface for manual QA. It is the working vendor-assurance toolkit using fictional data. Start with the hosted toolkit. If it is unavailable, use the local Streamlit app at `http://127.0.0.1:8502` and record the outage and fallback URL. [Hosted toolkit](https://icdfa-vendor-assurance-toolkit.streamlit.app)

Use the browser controls for all manual workflows, including validation, downloads, reporting, accessibility and responsive behaviour. Terminal and Python checks provide supplementary regression and integrity evidence only. PASS requires observable browser evidence for the case.

1. Choose cases and an independent reviewer in the [workplan](WORKPLAN.md).
2. Follow the [test execution guide](TEST_EXECUTION_GUIDE.md). Copy the [test case template](TEST_CASE_TEMPLATE.md) for each run and use the [defect report template](DEFECT_REPORT_TEMPLATE.md) when a check fails.
3. Record each version-specific run in the [execution log](../reports/qa/TEST_EXECUTION_LOG.csv) and every failure in the [current defect register](../reports/qa/DEFECT_REGISTER.md). Link the run from the QA handoff. Keep prior test, defect, retest and sign-off records intact.
4. Deliver the completed register, defect register, retest evidence and independent recommendation to Group 4 and the team lead. If access is missing, follow the [upload guide](../UPLOAD_GUIDE.md).

Release requires zero unresolved Critical or High defects, documented reviewer acceptance of Medium defects, retesting of every correction and sign-off that identifies the tested commit. Every handoff includes the **file path, commit SHA, test result, reviewer, acceptance status and known limitations**.

## Project links

- [GitHub repository](https://github.com/ayuba-amadi/third-party-cyber-risk-vendor-assurance-toolkit) · [Live Streamlit application](https://icdfa-vendor-assurance-toolkit.streamlit.app)
- [User guide](../docs/user_guide.md) · [Project documentation](../docs/project_documentation.md) · [Deployment guide](../docs/deployment_guide.md)
- [Test register](../tests/TEST_REGISTER.md) · [Defect register](../tests/DEFECT_REGISTER.md) · [QA sign-off](../tests/QA_SIGNOFF.md)
- [Acceptance matrix](../reports/phase6/final_acceptance_matrix.md) · [Management reconciliation](../reports/phase6/reconciliation_report.md)
- [Presentation outline](../docs/presentation_outline.md) · [Demonstration script](../docs/demonstration_script.md)
- [Contribution record](../governance/FINAL_CONTRIBUTIONS.md) · [Submission rules](../governance/SUBMISSION_RULES.md)
