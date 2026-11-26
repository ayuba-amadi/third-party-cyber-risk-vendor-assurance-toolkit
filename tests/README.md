# Phase 1 tests

From the repository root, using Python 3.10 or later:

```sh
python -m unittest discover -s tests -v
python3 sample-data/validate_fixture.py
```

Use `python3` for both commands if `python` is unavailable. Tests use standard
library `unittest`, do not access the network and write only to temporary folders.
Mutations use memory copies or temporary copies of the fictional CSVs.

- `test_loader.py`: all source files, fixture counts (10 vendors, 24 questions,
  11 assessments), reference classification, exact headers, empty cells, UTF-8,
  file errors, malformed CSV and default/custom report dates.
- `test_validation.py`: duplicates, required values, enums, foreign keys, response
  pairs, dates, evidence/decision conditional fields, ownership and row-order independence.
- `test_phase1_smoke.py`: CLI help/inventory, successful and failing validation,
  JSON/Markdown reports, custom report date, exit codes and unchanged sample data.

The research fixture validator is preserved and run separately; its expected
scoring checks are not a Phase 1 scoring implementation. Later phases must add
criticality/scoring boundary tests and worked-example reconciliation, workflow,
remediation/history, vendor/management report and GUI tests. Independent QA is
still required; this folder does not change `03-testing-and-quality-assurance/`.
