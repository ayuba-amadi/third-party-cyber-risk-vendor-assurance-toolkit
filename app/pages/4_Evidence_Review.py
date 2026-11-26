from copy import deepcopy
import streamlit as st

from app.state import audit, next_id, put
from app.ui_helpers import (download_csv, label, question_label, save, select_assessment,
                            select_vendor, show_rows, start, vendor_label, evidence_badge,
                            severity_badge)
from src.config import ALLOWED_VALUES
from src.risk_scoring import parse_options, score_question
from src.schema import PHASE2_SCHEMAS

ws = start("Evidence review", "Compare the vendor’s claim with the reviewer’s answer and the effective evidence status. Record review changes for fictional evidence in this session.")
if ws.operations is None:
    st.stop()
vid = select_vendor(ws, "evidence")
aid = select_assessment(ws, vid, "evidence")
if not aid:
    st.stop()

_, assessments, _, risks, _, _ = ws.operations
historical = assessments[aid]["status"] == "Superseded"
assessment_risk = risks[aid][0]["final_rating"]
if assessment_risk in ("Critical", "High", "Medium", "Low"):
    st.markdown("**Assessment risk rating**")
    severity_badge(assessment_risk)
bank = {row["question_id"]: row for row in ws.rows("question")}
evidence = {row["question_id"]: row for row in ws.rows("evidence_item") if row["assessment_id"] == aid}
responses = {row["question_id"]: row for row in ws.rows("response") if row["assessment_id"] == aid}
statuses = ALLOWED_VALUES[("evidence_item", "status")]
st.caption("Evidence status legend")
legend = st.columns(5)
for col, status_label in zip(legend, ("Missing", "Received", "Accepted", "Rejected", "Expired")):
    with col:
        evidence_badge(status_label)
selected = st.multiselect("Evidence status", statuses, help="Filters by effective status on the report date.")
search = st.text_input("Search question ID").strip().casefold()
scores = {qid: score_question(question, responses.get(qid), evidence.get(qid), ws.report_date)
          for qid, question in bank.items()}
audit_rows = ws.rows("reviewer_audit_entry")


def review_date(record):
    reviews = [row["timestamp"] for row in audit_rows if row["table_name"] == "evidence_item"
               and row["record_id"] == record.get("evidence_id") and row["action"] in ("Verified", "Rejected", "Edited")]
    return max(reviews, default="")[:10]


choices = [qid for qid, score in scores.items() if search in qid.casefold() and
           (not selected or score["effective_evidence_status"] in selected)]
summary = []
for qid in choices:
    item = evidence.get(qid, {})
    summary.append(dict(
        vendor=vendor_label(ws, vid), assessment_id=aid, question=question_label(bank[qid]),
        evidence_id=item.get("evidence_id", ""), status=item.get("status", "Missing"),
        effective_status=scores[qid]["effective_evidence_status"], review_date=review_date(item),
        rejection_reason=item.get("reason", "") if item.get("status") == "Rejected" else "",
        **{field: item.get(field, "") for field in
           ("received_date", "expiry_date", "reviewer_role", "reference_path")},
    ))
st.subheader("Evidence records")
show_rows(summary)
download_csv(ws, "evidence_item", list(evidence.values()), "Download updated evidence records")
download_csv(ws, "reviewer_audit_entry", [row for row in audit_rows if row["record_id"] in
             {item["evidence_id"] for item in evidence.values()}], "Download evidence audit records")
if not choices:
    st.stop()

qid = st.selectbox("Evidence question", choices, format_func=lambda value: question_label(bank[value]))
question, old, response = bank[qid], evidence.get(qid, {}), responses[qid]
score = scores[qid]
st.write(f"Evidence required · {question['evidence_description']}")
st.write(f"Acceptance criteria · {question['acceptance_criteria']}")
st.subheader("Claim and reviewer assessment")
claim_col, review_col = st.columns(2)
with claim_col:
    st.markdown("**Vendor claim**")
    st.info(response["vendor_claim"] or "No vendor claim recorded")
with review_col:
    st.markdown("**Reviewer verification**")
    st.write(f"Verification · {response['reviewer_verified']}")
    st.write(f"Reviewer answer · {response['verified_answer'] or 'Not recorded'}")
    st.write(f"Reviewer note · {response['reviewer_note'] or 'None'}")
st.markdown("**Effective evidence status**")
evidence_badge(score["effective_evidence_status"])
if (score["effective_evidence_status"] == "Expired" and old.get("expiry_date") and
        old["expiry_date"] < ws.report_date.isoformat()):
    st.warning("Reason: expiry date is earlier than the report date.")
st.write(f"Effective status: **{score['effective_evidence_status']}** · {score['calculation_reason']}")
if historical:
    st.info("Historical evidence is preserved. The historical assessment score uses its assessment date.")
    st.stop()

with st.form(f"evidence_{aid}_{qid}"):
    status = st.selectbox("Recorded evidence status", statuses, index=statuses.index(old.get("status", "Missing")))
    st.caption("Received, accepted, rejected and expired evidence require a received date and reference. "
               "Accepted or expired evidence also requires reviewer details, a covered period end and expiry date. "
               "Rejected evidence requires a reviewer and rejection reason.")
    record = dict(old, status=status, assessment_id=aid, question_id=qid)
    for field in PHASE2_SCHEMAS["evidence_item"].columns[4:]:
        record[field] = st.text_input("Rejection reason or evidence note" if field == "reason" else label(field),
                                      old.get(field, ""), help="Enter YYYY-MM-DD when applicable."
                                      if field.endswith("date") or field == "review_period_end" else None).strip()
    answers = ["", *parse_options(question["response_options"])]
    verified = st.checkbox("Verify with accepted evidence", value=response["reviewer_verified"] == "Yes")
    answer = st.selectbox("Reviewer-verified answer", answers, index=answers.index(response["verified_answer"] or ""))
    note = st.text_area("Reviewer note", response["reviewer_note"])
    if st.form_submit_button("Save evidence review to session"):
        candidate = deepcopy(ws.tables)
        record["evidence_id"] = old.get("evidence_id") or next_id(ws.rows("evidence_item"), "evidence_id", "EV-")
        updated = dict(response, reviewer_verified="Yes" if verified else "Not reviewed",
                       verified_answer=answer if verified else "", reviewer_note=note.strip())
        put(candidate, "evidence_item", record, replace=True)
        put(candidate, "response", updated, replace=True)
        role = record["reviewer_role"] or "Fictional evidence intake"
        if not old:
            audit(candidate, "evidence_item", record["evidence_id"], "Created", role, "Fictional evidence record")
        if record != old or updated != response:
            action = {"Accepted": "Verified", "Expired": "Verified", "Rejected": "Rejected"}.get(status, "Edited")
            audit(candidate, "evidence_item", record["evidence_id"], action, role, "Session evidence review")
        try:
            preview = score_question(question, updated, record, ws.report_date)
            if verified and not preview["verified"]:
                raise ValueError("Verification requires a vendor answer, a reviewer answer and accepted, unexpired evidence. "
                                 + preview["calculation_reason"])
        except ValueError as exc:
            st.error(str(exc))
        else:
            save(ws, candidate, "Evidence review saved to this session.")
