# Browser QA records

**27 November–1 December 2026, inclusive. Deadline 1 December 2026, 23:59 WAT (UTC+1).**

Run all manual QA in the Streamlit toolkit. Use the [browser matrix](../../03-testing-and-quality-assurance/TEST_EXECUTION_GUIDE.md#browser-test-matrix) and append one row per case attempt to the [execution log](TEST_EXECUTION_LOG.csv). Log the URL and tested version and record any use of the local fallback. Use the [test case template](../../03-testing-and-quality-assurance/TEST_CASE_TEMPLATE.md) for detailed notes and link supporting files from the log.

Save screenshots and downloads in [evidence](evidence/). Every PASS requires observable browser evidence. Keep every failure in the [defect register](DEFECT_REGISTER.md) with its case ID. Use a new execution row for each retest and link it to the original defect and evidence.

Release requires no unresolved Critical or High defects, documented reviewer acceptance of Medium defects and a browser retest of every correction. Record the exact tested commit and the independent reviewer's recommendation in the QA handoff. [QA workplan](../../03-testing-and-quality-assurance/WORKPLAN.md) · [Handoff register](../../governance/HANDOFFS.md)

Keep earlier test, defect, sign-off and completed phase records intact. [Historical QA index](../../tests/README.md) · [Completed phase records](../)
