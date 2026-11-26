# Reproducibility record

Execution date 26 November 2026. Frozen demonstration date 18 November 2026.

| Item | Expected | Actual |
|---|---|---|
| Operating system | Linux with Python 3.12 | Ubuntu 24.04.5 LTS, Python 3.12.3 |
| Dependency installation | Fresh virtual environment installs root requirements | `python -m pip install -r requirements.txt` installed Streamlit 1.67.0. `python -m pip check` found no broken requirements. pytest was installed separately. |
| Controlled copy | Code and fixtures load outside the developer checkout | Temporary copy included the uncommitted files and excluded Git metadata and Python caches. The app and CLI ran from that copy. |
| Research validator | `python3 sample-data/validate_fixture.py` returns 0 | Passed structural checks and independently matched expected criticality, question scores, risk, domains and management. |
| Test commands | `python -m unittest discover -s tests -v` and `python -m pytest -q` pass | Both reported 100 passed. Pytest reported 138 passing subtests. |
| App start | `streamlit run app/streamlit_app.py --server.headless true --server.port 8501` serves locally | Bound to loopback for QA. Health returned `ok`. Process stopped after testing. |
| CLI and reports | Validate and generate criticality, risk, decisions, actions, history and reports | Ten CLI commands exited 0. `python -m src.cli management-report --as-of 2026-11-18` matched 33 expected rows and all 36 Phase 4 rows. `python -m src.cli vendor-report --vendor-id VEN-009` regenerated the individual report. |
| Source integrity | The sample CSV bytes match the baseline | All 20 file hashes matched, including the earlier untracked assessment snapshot. |
| Local dependencies | Calculation does not require credentials, developer paths or network services | Engine uses Python standard-library CSV and local data. Calculation and reporting succeeded from the standalone copy. Dependency installation can require internet access. |

The [command log](evidence/commands.txt), [compiled files](evidence/compile.txt), [dependency check](evidence/dependency_check.txt) and [fixtures](../../sample-data/README.md) support this record. The [end-to-end procedure](../../tests/END_TO_END_TESTS.md) lists the exact test commands.
