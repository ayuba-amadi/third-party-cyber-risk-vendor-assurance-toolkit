from copy import deepcopy
import streamlit as st

from app.state import audit, next_id, put
from app.ui_helpers import (assessment_label, download_csv, label, question_label, save, select_assessment,
                            select_vendor, show_issues, show_rows, start, decision_badge,
                            severity_badge, status_badge)
from src.config import ALLOWED_VALUES
from src.decision_workflow import APPROVALS, evaluate_decision

ws = start("Decisions", "Review the calculated result, then record a fictional authorised decision separately. Check the summary before confirming the session record.")
if ws.operations is None:
    st.stop()
vid = select_vendor(ws, "decision")
aid = select_assessment(ws, vid, "decision")
if not aid:
    st.stop()
vendors, assessments, _, risks, decisions, actions = ws.operations
assessment = assessments[aid]
result, scores, _ = risks[aid]
bank = {row["question_id"]: row for row in ws.rows("question")}
st.subheader("Assessment summary")
if result["final_rating"] in ("Critical", "High", "Medium", "Low"):
    severity_badge(result["final_rating"])
status_badge("Incomplete" if result["completeness"] == "Incomplete" else "Valid")
st.write(f"{assessment_label(assessment)} · Rating **{result['final_rating']}** · Completeness **{result['completeness']}**")
for reason in result["calculation_trace"]:
    st.write(reason)
for score in scores:
    if score["flags"]:
        st.warning(f"{question_label(bank[score['question_id']])} · {', '.join(score['flags']).title()}")
if result["completeness"] == "Incomplete":
    st.warning("The assessment is incomplete. Ordinary approval is prohibited.")
if result["confirmed_critical_failures"]:
    st.warning("There is a confirmed critical failure. Ordinary approval is prohibited.")

st.subheader("Authorised human decision")
st.caption("A person with the required authority must review, enter and confirm the decision. No decision is made automatically.")
records = [row for row in ws.rows("decision") if assessments[row["assessment_id"]]["vendor_id"] == vid]
recorded = next((row for row in records if row["assessment_id"] == aid), {})
outcome_label = recorded.get("outcome", "Awaiting decision")
decision_badge(outcome_label)
st.write(f"Selected assessment decision · **{outcome_label}**")
if aid in decisions and decisions[aid]["expired_approval"]:
    status_badge("Expired")
    st.warning("Expired approval")
if recorded and recorded["decision_date"] > ws.report_date.isoformat():
    st.info("The recorded decision is dated after the selected report date.")
if recorded:
    audit = next((event for event in ws.rows("reviewer_audit_entry")
                  if event["table_name"] == "decision" and event["record_id"] == recorded["decision_id"]
                  and event["action"] == "Decided" and event["note"].startswith("Fictional decision-maker")), None)
    decision_maker = audit["note"].split(". Selected actions:", 1)[0].removeprefix("Fictional decision-maker: ") if audit else "Name unavailable in source CSV"
    st.markdown("**Decision record details**")
    show_rows([dict(decision_maker=decision_maker, role=recorded["decision_maker_role"],
                    justification=recorded["justification"], conditions=recorded["conditions"] or "None recorded",
                    condition_deadline=recorded["condition_deadline"] or "Not applicable",
                    review_date=recorded["review_date"] or "Not recorded",
                    expiry_date=recorded["expiry_date"] or "Not recorded")], name="Decision record details")
with st.expander("Current and historical decision records", expanded=True):
    show_rows([dict(row, selection="Current" if row["assessment_id"] == vendors[vid]["current_assessment_id"]
                    else "Historical", decision_maker=next((event["note"] for event in ws.rows("reviewer_audit_entry")
                        if event["table_name"] == "decision" and event["record_id"] == row["decision_id"]
                        and event["action"] == "Decided" and event["note"].startswith("Fictional decision-maker")),
                        "Name unavailable in source CSV")) for row in records])
download_csv(ws, "decision", records, "Download decision records")
ids = {row["decision_id"] for row in records}
download_csv(ws, "reviewer_audit_entry", [row for row in ws.rows("reviewer_audit_entry")
             if row["table_name"] == "decision" and row["record_id"] in ids], "Download decision audit records")
if recorded or aid != vendors[vid]["current_assessment_id"]:
    st.info("Decision entry is available for current assessments awaiting a decision.")
    st.stop()

linked = [row for row in actions if row["assessment_id"] == aid and row["action_id"]]
action_labels = {row["action_id"]: row["action_text"] for row in linked}
with st.form(f"decision_{aid}"):
    outcome = st.selectbox("Decision outcome *", ("", *ALLOWED_VALUES[("decision", "outcome")]))
    name = st.text_input("Fictional decision-maker *").strip()
    role = st.text_input("Decision-maker role *", help=f"Choose a role different from {assessment['assessor_role']}.").strip()
    record = dict(assessment_id=aid, calculated_rating=result["final_rating"], outcome=outcome,
                  decision_maker_role=role)
    record["justification"] = st.text_area("Justification *").strip()
    for field in ("decision_date", "expiry_date", "review_date", "condition_deadline"):
        record[field] = st.text_input(label(field) + (" *" if field != "condition_deadline" else ""),
                                     ws.report_date.isoformat() if field == "decision_date" else "",
                                     help="Use YYYY-MM-DD. The condition deadline is required for conditional approval.").strip()
    record["conditions"] = st.text_area("Conditions", help="Required for conditional approval.").strip()
    selected_actions = st.multiselect("Linked corrective actions", list(action_labels),
                                      format_func=lambda key: f"{key} · {action_labels[key]}")
    preview = st.form_submit_button("Review decision summary")
if preview:
    ws.pending_decision = None
    if not name:
        st.warning("Enter the fictional decision-maker’s name.")
    elif name.casefold() == assessment["assessor_role"].casefold():
        st.warning("The decision-maker must be independent of the assessor.")
    elif not outcome or not role or not record["justification"]:
        st.warning("Enter an outcome, decision-maker role and justification.")
    elif outcome == "Conditionally Approved" and not selected_actions:
        st.warning("Select a linked corrective action for conditional approval.")
    elif record["decision_date"] > ws.report_date.isoformat():
        st.warning("The decision date must be on or before the report date.")
    else:
        record["decision_id"] = next_id(ws.rows("decision"), "decision_id", "DEC-")
        candidate = deepcopy(ws.tables)
        put(candidate, "decision", record)
        note = f"Fictional decision-maker: {name}"
        if selected_actions:
            note += ". Selected actions: " + ", ".join(selected_actions)
        audit(candidate, "decision", record["decision_id"], "Decided", role, note)
        issues = ws.check(candidate)
        if issues:
            show_issues(issues)
        else:
            try:
                evaluate_decision(record, assessment, result, scores,
                                  [row for row in linked if row["action_id"] in selected_actions]
                                  if outcome == APPROVALS[1] else linked, ws.report_date)
            except ValueError as exc:
                st.warning(str(exc))
            else:
                ws.pending_decision = dict(record=record, note=note, tables=candidate)
pending = ws.pending_decision
if pending and pending["record"]["assessment_id"] == aid:
    st.subheader("Confirm the decision record")
    st.write(pending["note"])
    for field, value in pending["record"].items():
        st.write(f"{label(field)} · {value or 'None'}")
    if st.button("Confirm decision in session"):
        save(ws, pending["tables"], "Authorised decision recorded in this session. Download the records to retain them.")
