from copy import deepcopy
import streamlit as st

from app.state import put
from app.ui_helpers import (assessment_label, download_csv, question_label, save, select_assessment,
                            select_vendor, show_criticality, show_rows, start)
from src.risk_scoring import parse_options

ws = start("Assessment", "Choose a vendor and assessment. Record the vendor’s answers here. Open Evidence Review to record reviewer checks.")
if ws.operations is None:
    st.stop()
vendors, assessments, criticality, risks, _, _ = ws.operations
vid = select_vendor(ws, "assessment")
aid = select_assessment(ws, vid, "assessment")
if not aid:
    if vid:
        role = st.text_input("Assessor role *", help="Use a fictional role.")
        if st.button("Start draft assessment", disabled=not role.strip()):
            candidate, new_id = ws.draft_assessment(vendors[vid], role.strip())
            ws.assessment_id = new_id
            save(ws, candidate, "Draft assessment created with 24 unanswered questions.")
    st.stop()

assessment = assessments[aid]
result, questions, domains = risks[aid]
bank = {row["question_id"]: row for row in ws.rows("question")}
st.subheader(assessment_label(assessment))
st.write(f"Assessor role · {assessment['assessor_role']}")
with st.expander("Why this criticality?"):
    show_criticality(criticality[aid])

total = len(questions)
accepted = sum(row["effective_evidence_status"] == "Accepted" for row in questions)
st.progress(result["verified_count"] / total, text=f"Verified: {result['verified_count']} of {total}")
st.write(f"Answered: {result['answered_count']} of {total}  |  Evidence accepted: {accepted} of {total}")
st.write(f"Completeness: **{result['completeness']}**  |  Risk rating: **{result['final_rating']}**")
with st.expander("Why this assessment result?", expanded=True):
    for reason in result["calculation_trace"]:
        st.write(reason)
    for question in questions:
        if question["flags"]:
            st.warning(f"{question_label(bank[question['question_id']])} · {', '.join(question['flags']).title()}")
with st.expander("Progress by domain"):
    show_rows([dict(domain=bank[f"{row['domain']}-01"]["domain"], total=row["total_questions"],
                    answered=row["answered_count"], verified=row["verified_count"]) for row in domains])

domain = st.selectbox("Question domain", ["All domains", *sorted({row["domain"] for row in bank.values()})])
search = st.text_input("Search question wording or ID").strip().casefold()
choices = [qid for qid, question in bank.items()
           if domain in ("All domains", question["domain"]) and search in question_label(question).casefold()]
if choices:
    qid = st.selectbox("Question", choices, format_func=lambda key: question_label(bank[key]))
    question = bank[qid]
    score = next(row for row in questions if row["question_id"] == qid)
    st.write(f"{question['domain']} · Weight {question['weight']} · Essential safeguard: {question['critical_failure_flag']}")
    st.write(f"Required evidence: {question['evidence_description']}")
    st.write(f"Acceptance criteria: {question['acceptance_criteria']}")
    st.write(f"Answer choices: {question['response_options']}")
    st.write(f"Reviewer verification: {score['reviewer_verified']}")
    st.write(f"Reviewer answer: {score['verified_answer'] or 'Not recorded'}")
    st.write(f"Evidence status: {score['effective_evidence_status']}")
    with st.expander("Why this result?", expanded=True):
        st.write(f"Risk value: {score['risk_value']} of 4")
        st.write(score["calculation_reason"])
    responses = [row for row in ws.rows("response") if row["assessment_id"] == aid]
    old = next(row for row in responses if row["question_id"] == qid)
    options = ["Blank", *parse_options(question["response_options"])]
    with st.form(f"claim_{aid}_{qid}"):
        claim = st.selectbox("Vendor claim", options, index=options.index(old["vendor_claim"] or "Blank"),
                             disabled=assessment["status"] == "Superseded")
        if st.form_submit_button("Save answer to session", disabled=assessment["status"] == "Superseded"):
            candidate = deepcopy(ws.tables)
            if claim != old["vendor_claim"]:
                put(candidate, "response", dict(old, vendor_claim=claim, reviewer_verified="Not reviewed",
                                               verified_answer="", reviewer_note=""), replace=True)
            save(ws, candidate, "Answer saved. A changed answer requires reviewer verification.")
else:
    st.info("No questions match your search.")
download_csv(ws, "response", [row for row in ws.rows("response") if row["assessment_id"] == aid],
             "Download updated questionnaire")
