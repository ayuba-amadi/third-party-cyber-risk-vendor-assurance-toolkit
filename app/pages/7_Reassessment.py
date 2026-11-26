import streamlit as st

from app.ui_helpers import select_vendor, show_rows, start

ws = start("Reassessment", "Select a vendor and compare the saved versions, material changes, evidence and decision records.")
if ws.operations is None:
    st.stop()
vid = select_vendor(ws, "reassessment")
try:
    history = ws.history(vid)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

st.write("The previous assessment has been preserved. The new assessment does not overwrite historical records.")
st.subheader("Previous and current assessments")
show_rows([{field: row[field] for field in ("selection", "assessment_id", "version_no", "assessment_date",
           "criticality_score", "criticality_band", "risk_percent", "completeness", "decision_status", "decision_id")}
           for row in history["versions"]])
eligibility = ws.decision_errors.get(history["current_assessment_id"])
if eligibility:
    st.warning(f"The current recorded decision requires review. {eligibility}")
with st.expander("Criticality factors and evidence differences", expanded=True):
    bank = {row["question_id"]: row["question_text"] for row in ws.rows("question")}
    for version in history["versions"]:
        st.write(f"**{version['selection']} · {version['assessment_id']} · Version {version['version_no']}**")
        st.write(f"Data sensitivity {version['data_sensitivity']} · Access {version['system_access']} · "
                 f"Dependency {version['dependency_impact']} · Replaceability {version['replaceability']}")
        if version["evidence_flags"]:
            for flag in version["evidence_flags"]:
                qid, status = flag.split(":", 1)
                st.write(f"{qid} · {bank[qid]} · {status}")
        else:
            st.write("No flagged evidence.")
st.subheader("Material changes and review triggers")
show_rows(history["change_events"])
for trigger in history["pending_triggers"]:
    st.warning(trigger)
if not history["pending_triggers"]:
    st.write("No outstanding reassessment trigger on the selected report date.")
