# Testing the toolkit

The QA window is **27 November–1 December 2026, inclusive**, with a deadline of **1 December 2026, 23:59 WAT (UTC+1)**. Group 3 coordinates testing. Every project member is encouraged to test and report observations.

## Run the checks

Use Python 3.12 and the repository's `.venv`. Install dependencies using the [quick start](../README.md#quick-start). Run from the root of a clean QA checkout. The management report writes generated files under `reports/phase4/`. Use a disposable checkout of the tested SHA so that historical results and unrelated local edits are preserved.

```bash
source .venv/bin/activate
./.venv/bin/python -m unittest discover -s tests -v
./.venv/bin/python sample-data/validate_fixture.py
./.venv/bin/python -m src.cli management-report --as-of 2026-11-18
git diff --check
```

The suite covers loader and validation rules, criticality and risk calculations, workflow and history, reporting and exports, and Streamlit page behaviour. Record the actual test count and exit status. The fixture validator independently compares the fictional inputs and expected results. The dated management report should report a PASS for all 33 comparison rows. Inspect the report's source IDs as part of manual reconciliation.

## Complete the independent checks

- Follow the [execution guide](../03-testing-and-quality-assurance/TEST_EXECUTION_GUIDE.md) for setup, all nine pages, the ten demonstrations, edge cases, downloads, accessibility, privacy checks and source CSV hashes.
- Use the [test case template](../03-testing-and-quality-assurance/TEST_CASE_TEMPLATE.md) and [defect report template](../03-testing-and-quality-assurance/DEFECT_REPORT_TEMPLATE.md). Link observed evidence before marking PASS and retest every correction.
- Treat existing test, defect and sign-off records as historical evidence for the versions they identify. Record new runs separately and link the candidate evidence in the handoff.

Release requires no unresolved Critical or High defects and documented acceptance of Medium defects. The sign-off must name the tested commit. Every handoff includes the **file path, commit SHA, test result, reviewer, acceptance status and known limitations**.

## Project links

- [GitHub repository](https://github.com/ayuba-amadi/third-party-cyber-risk-vendor-assurance-toolkit) · [Live Streamlit application](https://icdfa-vendor-assurance-toolkit.streamlit.app)
- [User guide](../docs/user_guide.md) · [Project documentation](../docs/project_documentation.md) · [Deployment guide](../docs/deployment_guide.md)
- [Test register](TEST_REGISTER.md) · [Defect register](DEFECT_REGISTER.md) · [QA sign-off](QA_SIGNOFF.md)
- [Acceptance matrix](../reports/phase6/final_acceptance_matrix.md) · [Management reconciliation](../reports/phase6/reconciliation_report.md)
- [Presentation outline](../docs/presentation_outline.md) · [Demonstration script](../docs/demonstration_script.md)
- [Contribution record](../governance/FINAL_CONTRIBUTIONS.md) · [Submission rules](../governance/SUBMISSION_RULES.md)
