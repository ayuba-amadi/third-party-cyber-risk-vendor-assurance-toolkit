import streamlit as st

from app.ui_helpers import select_vendor, show_rows, start, severity_badge, status_badge

ws = start("Reassessment", "Select a vendor and compare the saved versions, material changes, evidence and decision records.")
if ws.operations is None:
    st.stop()
vid = select_vendor(ws, "reassessment")
try:
    history = ws.history(vid)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

st.info("The previous assessment has been preserved. A reassessment creates a new version and never overwrites historical records.")
st.subheader("Assessment version comparison")
for version in history["versions"]:
    with st.container(border=True):
        st.markdown(f"**{version['selection']} assessment · {version['assessment_id']} · Version {version['version_no']}**")
        cols = st.columns(4)
        for col, label, value in zip(cols, ("Assessment date", "Criticality", "Risk", "Completeness"),
                                     (version["assessment_date"],
                                      f"{version['criticality_score']} · {version['criticality_band']}",
                                      f"{version['risk_percent']}%", version["completeness"])):
            with col:
                st.metric(label, value)
        if version["criticality_band"] in ("Critical", "High", "Medium", "Low"):
            severity_badge(version["criticality_band"])
        status_badge("Incomplete" if version["completeness"] == "Incomplete" else "Valid")
        st.write(f"Decision · {version['decision_status']} · {version['decision_id'] or 'No recorded decision'}")
if len(history["versions"]) > 1:
    previous, current = history["versions"][-2], history["versions"][-1]
    st.subheader("Change since previous assessment")
    change_cols = st.columns(3)
    change_cols[0].metric("Criticality change", f"{previous['criticality_band']} → {current['criticality_band']}")
    change_cols[1].metric("Risk change", f"{previous['risk_percent']}% → {current['risk_percent']}%")
    change_cols[2].metric("Version", f"{previous['version_no']} → {current['version_no']}")
st.caption("Assessment record details")
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
status_badge("Reassessment due" if history["pending_triggers"] else "Valid")
for trigger in history["pending_triggers"]:
    st.warning(trigger)
if not history["pending_triggers"]:
    st.write("No outstanding reassessment trigger on the selected report date.")
