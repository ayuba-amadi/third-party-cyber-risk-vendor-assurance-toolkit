# End-to-end execution

Run these commands from a temporary copy of the full working tree so generated Phase 1–4 reports stay in that copy. Include the uncommitted application, engine and assessment snapshot. Use the baseline date 18 November 2026. Keep invalid records in memory or in a separate copy.

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m pytest -q
python3 sample-data/validate_fixture.py
python -m src.cli inventory
python -m src.cli validate --data-dir sample-data --as-of 2026-11-18
python -m src.cli semantic-validate --data-dir sample-data --as-of 2026-11-18
python -m src.cli criticality --all --data-dir sample-data
python -m src.cli risk --all --data-dir sample-data --as-of 2026-11-18
python -m src.cli decisions --as-of 2026-11-18
python -m src.cli remediation --as-of 2026-11-18
python -m src.cli reassess --vendor-id VEN-004
python -m src.cli management-report --as-of 2026-11-18
python -m src.cli vendor-report --vendor-id VEN-009
python -m compileall src app tests
streamlit run app/streamlit_app.py --server.headless true --server.port 8501
```

Install pytest separately to reproduce the pytest run. From another terminal run `curl -fsS http://localhost:8501/_stcore/health` and expect `ok`. Stop Streamlit after testing. The browser capture script requires Playwright and Chromium as separate QA dependencies. AppTest runs from unittest with the regular Streamlit dependency.

See [command results](../reports/phase6/evidence/commands.txt), [test register](TEST_REGISTER.md), [browser evidence](../reports/phase6/evidence/browser.txt), [source integrity](../reports/phase6/evidence/source_after.txt) and [reconciliation](../reports/phase6/reconciliation_report.md).
