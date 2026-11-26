# Phase 1 status

Phase 1 objective: provide a readable, standard-library Python foundation for
loading the approved fictional CSVs and validating their structure and relationships.
Status: Phase 1 verified locally; later phases have not been started. This is not
a claim that the complete toolkit is finished or independently accepted.

Repository: `third-party-cyber-risk-vendor-assurance-toolkit`

Branch: `main`

Starting commit: `a06ca9afafc4685414337b05183185264c340278`

Ending commit: `a06ca9afafc4685414337b05183185264c340278`

Changes are uncommitted. No commit, push, deployment or external publication was performed.

## Files created

- `.gitignore` (Python bytecode only)
- `src/__init__.py`
- `src/config.py`
- `src/schema.py`
- `src/loader.py`
- `src/validation.py`
- `src/cli.py`
- `src/README.md`
- `app/README.md`
- `tests/README.md`
- `tests/test_loader.py`
- `tests/test_validation.py`
- `tests/test_phase1_smoke.py`
- `reports/README.md`
- `reports/phase1/validation_report.json`
- `reports/phase1/validation_report.md`
- `docs/README.md`
- `02-toolkit-development/PHASE_1_STATUS.md`

No pre-existing repository file was modified or deleted. The clean starting
checkout matched the requested baseline. All 50 pre-existing tracked files were
compared byte for byte with `a06ca9a`, including all research and sample data,
the research validator, and both excluded phase directories. No files were added
under `01-research-and-risk-assessment/`, `sample-data/`,
`03-testing-and-quality-assurance/` or `04-documentation-and-presentation/`.

## Commands and environment

Python 3.12.3 was used; the implementation requires Python 3.10 or later.
This host has `python3` but no `python` executable. For the requested commands
only, a temporary shell function was used:

```sh
python() { python3 "$@"; }
```

It does not modify the repository or install anything. On this host analysts can
use `python3 -m src.cli ...` directly. The sandbox intermittently failed to start
with `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`; affected
commands were retried with approved execution outside the sandbox. An initial
literal `python` invocation reported `command not found`; the function above
resolved that environment issue for the final verification.

Required inspection and verification commands executed:

```sh
pwd
git status --short
git log -1 --oneline
rg --files
git branch --show-current
git rev-parse HEAD
python -m src.cli --help
python -m src.cli inventory
python -m src.cli validate
python -m src.cli validate --data-dir sample-data
python -m src.cli validate --data-dir sample-data --as-of 2026-11-18
python -m unittest discover -s tests -v
python3 sample-data/validate_fixture.py
git diff --check
git status --short
```

The authoritative specification, existing validator, project guidance and actual
CSV headers were read before implementation using `cat` and read-only
`python3 -c` inspections. Ancestor guidance was checked; no applicable AGENTS.md
was found. A read-only `/tmp/phase1_repository_audit.py` additionally ran Git
baseline comparisons, checked excluded paths, inspected database extensions and
SQLite file signatures, checked whitespace in the new untracked files, and
reconciled the generated reports. No temporary audit helper is part of the toolkit.

## Verification results

| Check | Result |
|---|---|
| `unittest` | PASS: 34 deterministic tests, no network; all pass |
| Existing research fixture validator | PASS, unchanged and executed separately |
| Structural validation | PASS: 12 files loaded, 12 valid tables, 1,150 total source rows |
| Errors / warnings | 0 / 0 |
| Duplicate / orphan records | 0 / 0 |
| Missing fields / invalid values / date errors | 0 / 0 / 0 |
| Inventory | PASS: 12 sources, 5 expected-output files, 2 negative-test files, 1 reference text file |
| Reports | JSON and Markdown generated under `reports/phase1/`; default report date 2026-11-18 |
| Custom report date | PASS: loader and CLI/report tests accept another ISO date |
| Data preservation | PASS: baseline byte comparison and before/after sample-data hash test |
| Git whitespace check | PASS; new untracked files also checked for whitespace |
| Database/dependencies | No database files, SQLite use, third-party dependency or dependency manifest added |
| Scope | No scoring engine, decision workflow, remediation workflow, Streamlit pages or deployment |

Source row counts:

| Table | Rows |
|---|---:|
| vendor | 10 |
| business_service | 8 |
| vendor_service_link | 13 |
| assessment | 11 |
| question | 24 |
| response | 264 |
| evidence_item | 264 |
| finding | 7 |
| corrective_action | 4 |
| decision | 8 |
| change_event | 2 |
| reviewer_audit_entry | 535 |
| Total | 1,150 |

The separate research validator reported four PASS lines: source keys/FKs,
evidence states and expected risk calculations; fixture counts and history;
and independent criticality, question-score, domain-completeness, management,
audit-reference and version-link cross-checks. Its LIMIT notice still applies:
fixture verification is not independent toolkit QA or complete policy approval.
The new CLI never executes that validator or implements its scoring arithmetic.

## Limitations and Phase 2 prerequisites

Phase 1 validates data structure and relationships only. Risk scoring, criticality, decision workflow and Streamlit user pages are implemented in later phases.

- Only structural validation reports are implemented. Risk/criticality scoring,
  decisions, remediation management, individual vendor/management reports and GUI
  are later-phase work. Existing decision and action rows are read only.
- The actual source headers are retained. The complete header difference table
  is in [`src/README.md`](../src/README.md). Evidence review time is in the audit
  timestamp; `review_period_end` is the evidence coverage date and `reason` is
  the rejection explanation. No schema or CSV was rewritten.
- All raw rows remain visible, including invalid ones. Errors make a dataset
  unsuitable for further processing; no accepted-row export or duplicate winner
  is implemented. Dates record structure/order only; report-date expiry and
  completeness calculations are later work.
- There are no onboarding, finding-creation or action-creation date fields, so
  comparisons needing them are unavailable. Early action closure is valid.
- The fixture/research validator enforce unique evidence assessment/question
  pairs, while replacement-evidence history is described in research workflow
  rules. Resolve that schema representation before implementing history.
- Composite-key audit target references have no defined baseline encoding and
  are flagged rather than guessed. Current audit fixture targets have scalar IDs.
- Historical criticality factor snapshots exist only in an expected-output file.
  It remains excluded from source loading; resolve historical input handling
  before historical scoring, without treating expected outputs as production data.
- Evidence paths are fictional and are not opened. Role authority, policy
  approval, audit completeness and immutable history enforcement are later work.
- Later phases must reuse this foundation and add independent tests against the
  approved methods and worked examples. Phase 1 success does not approve draft
  policy choices noted in the research handoff.

Remaining Phase 1 errors: NONE.

Recommended next phase: **Phase 2 — Validation completion and criticality engine**.
Proceed only under a separate instruction after this Phase 1 result is reported.
