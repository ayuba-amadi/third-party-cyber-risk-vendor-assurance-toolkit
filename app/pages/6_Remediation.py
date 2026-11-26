from copy import deepcopy
from datetime import timedelta
import streamlit as st

from app.state import put
from app.ui_helpers import (assessment_label, download_csv, filters, label, question_label, save, show_rows, start,
                            vendor_label)
from src.config import ALLOWED_VALUES
from src.loader import load_report_date

ws = start("Remediation", "Filter findings and corrective actions, then choose a record to review or update. Enter a closure date when closing an action.")
if ws.operations is None:
    st.stop()
_, assessments, _, _, decisions, actions = ws.operations
bank = {row["question_id"]: row for row in ws.rows("question")}
records = [dict(row, overdue="Yes" if row["action_overdue"] else "No") for row in actions]
records = filters(records, ("vendor_id", "severity", "finding_status", "action_status", "overdue",
                            "assessment_id", "responsible_party"), "remediation",
                  {"vendor_id": lambda vid: vendor_label(ws, vid),
                   "assessment_id": lambda aid: assessment_label(assessments[aid])})
view = st.radio("Show records", ("All findings and actions", "Open findings", "Overdue actions",
                                "Actions due soon", "Closed actions", "Unresolved conditions"))
if view == "Unresolved conditions":
    filtered_aids = {row["assessment_id"] for row in records}
    show_rows([dict(row, vendor=vendor_label(ws, row["vendor_id"])) for row in decisions.values()
               if row["open_condition"] and row["assessment_id"] in filtered_aids])
    st.stop()
if view == "Open findings":
    records = [row for row in records if row["finding_status"] == "Open"]
elif view == "Overdue actions":
    records = [row for row in records if row["action_overdue"]]
elif view == "Actions due soon":
    st.caption("Due soon covers the report date and the next 30 days.")
    records = [row for row in records if row["action_id"] and row["action_status"] != "Closed"
               and ws.report_date <= load_report_date(row["due_date"]) <= ws.report_date + timedelta(days=30)]
elif view == "Closed actions":
    records = [row for row in records if row["action_status"] == "Closed"]

show_rows([dict(vendor=vendor_label(ws, row["vendor_id"]),
                question=question_label(bank[row["question_id"]]) if row["question_id"] in bank else "Assessment-wide",
                **{field: row[field] for field in ("finding_id", "assessment_id", "severity", "description",
                   "finding_status", "action_id", "action_text", "responsible_party", "due_date", "action_status",
                   "closed_date", "overdue")}) for row in records])
finding_ids = {row["finding_id"] for row in records}
action_ids = {row["action_id"] for row in records if row["action_id"]}
findings = {row["finding_id"]: row for row in ws.rows("finding") if row["finding_id"] in finding_ids}
action_records = {row["action_id"]: row for row in ws.rows("corrective_action") if row["action_id"] in action_ids}
download_csv(ws, "finding", list(findings.values()), "Download finding records")
download_csv(ws, "corrective_action", list(action_records.values()), "Download corrective-action records")

with st.expander("Add a fictional finding"):
    current = {row["current_assessment_id"] for row in ws.rows("vendor")}
    with st.form("new_finding"):
        aid = st.selectbox("Assessment for finding", [key for key in assessments if key in current],
                           format_func=lambda key: f"{vendor_label(ws, assessments[key]['vendor_id'])} · "
                                                   f"{assessment_label(assessments[key])}")
        qid = st.selectbox("Question for finding", ["", *bank],
                           format_func=lambda key: question_label(bank[key]) if key else "Assessment-wide")
        severity = st.selectbox("Finding severity", ALLOWED_VALUES[("finding", "severity")])
        description = st.text_area("Finding description *").strip()
        if st.form_submit_button("Save new finding to session", disabled=not aid):
            candidate = deepcopy(ws.tables)
            put(candidate, "finding", dict(finding_id=next_id(ws.rows("finding"), "finding_id", "FND-"),
                assessment_id=aid, question_id=qid, severity=severity, description=description, status="Open"))
            save(ws, candidate, "Finding saved to this session.")

if not findings:
    st.stop()
fid = st.selectbox("Finding", list(findings), format_func=lambda key: f"{key} · {findings[key]['description']}")
finding = findings[fid]
if assessments[finding["assessment_id"]]["status"] == "Superseded":
    st.info("This historical finding remains available for reference.")
    st.stop()
with st.form(f"finding_{fid}"):
    states = ALLOWED_VALUES[("finding", "status")]
    status = st.selectbox("Finding status", states, index=states.index(finding["status"]))
    if st.form_submit_button("Save finding status to session"):
        candidate = deepcopy(ws.tables)
        put(candidate, "finding", dict(finding, status=status), replace=True)
        save(ws, candidate, "Finding saved to this session.")

related = {action["action_id"]: action for action in ws.rows("corrective_action") if action["finding_id"] == fid}
act = st.selectbox("Corrective action", ["", *related],
                   format_func=lambda key: f"{key} · {related[key]['action_text']}" if key else "Add corrective action")
old = related.get(act, {})
with st.form(f"action_{fid}_{act}"):
    values = {}
    for field in ("action_text", "responsible_party", "due_date", "closed_date"):
        values[field] = st.text_input(label(field) + (" *" if field != "closed_date" else ""), old.get(field, ""),
                                     help="Enter YYYY-MM-DD. Closed actions require a closure date."
                                     if field.endswith("date") else None).strip()
    states = ALLOWED_VALUES[("corrective_action", "status")]
    values["status"] = st.selectbox("Action status", states, index=states.index(old.get("status", "Open")))
    if st.form_submit_button("Save corrective action to session"):
        candidate = deepcopy(ws.tables)
        action_id = act or next_id(ws.rows("corrective_action"), "action_id", "ACT-")
        put(candidate, "corrective_action", dict(values, action_id=action_id, finding_id=fid,
            vendor_id=assessments[finding["assessment_id"]]["vendor_id"]), replace=True)
        save(ws, candidate, "Corrective action saved to this session.")
