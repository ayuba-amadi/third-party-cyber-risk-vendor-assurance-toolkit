# Streamlit user guide

Use Python 3.10 or later and run these commands from the repository root.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r app/requirements.txt
streamlit run app/streamlit_app.py
```

Open the local URL printed by Streamlit. The report date starts at 2026-11-18.
Change it in the sidebar to recalculate current overdue and expiry flags.

| Page | What to do |
| --- | --- |
| Dashboard | Expand a count to inspect the underlying records. Review overdue work, expired approvals, incomplete assessments and supplier concentration. |
| Vendor Register | Search or filter vendors. Enter a fictional vendor or import a one-row CSV using vendor headers. Validate, calculate criticality and save to the session. |
| Assessment | Select an assessment or start a draft for an unassessed vendor. Record claims and check progress across the 24 questions. |
| Evidence Review | Select a question, check the evidence requirements and record the reviewer’s conclusion. |
| Decisions | Review the calculated result. For a current assessment awaiting a decision, enter an authorised human decision and confirm the summary. |
| Remediation | Filter findings, actions and conditions. Record action ownership, dates and status. |
| Reassessment | Compare saved historical and current versions, material changes and evidence flags. |
| Reports | Generate a report and download CSV, JSON, Markdown, HTML or a ZIP package where offered. |
| Data Quality | Run validation and inspect the file, row, field and correction for each issue. |

## Working copies and downloads

The loader reads 13 source CSV files from `sample-data/`. Each browser session
has its own working copy. Saving a change reruns validation and calculations
on that copy. Reset session clears your edits. Historical assessment factors
remain in their snapshots, while live vendor factors appear on the register
and can trigger reassessment. Date-based reporting uses the current assessment
pointer even when you choose an earlier report date.

Download records from the relevant page. Keep evidence and decision audit
files alongside the related CSV records. Assessment and management ZIP packages
include the generated report, all changed rows from the session and a manifest
with the report date, validation summary, UTC export time and Git commit when
available. The app only reads source CSV files. Reconcile exported changes by
primary key if using them outside the app.

Use fictional data only, including in any public demonstration. Use fictional
names, roles and evidence paths. The app displays reference paths as text.
The schema stores roles, so the app keeps new fictional decision-maker names
and selected action IDs in decision audit notes. Evidence review dates come
from audit timestamps. Incompatible changes to reviewed evidence are blocked
by the retained review history. The reassessment page compares existing versions.
If an edit makes an existing decision fail a workflow check, its record remains
available and the app flags it for review. Due soon means due on the report
date or within the following 30 days.

The application uses CSVs and session memory. SQLite is unused. Deployment
and production access control remain for a later phase.

For terminal commands, see the [engine and CLI guide](../src/README.md).
For verification, see [Phase 5 status](../02-toolkit-development/PHASE_5_STATUS.md).
