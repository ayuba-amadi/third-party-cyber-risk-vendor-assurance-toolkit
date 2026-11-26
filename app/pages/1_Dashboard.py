import streamlit as st

from app.ui_helpers import (decision_badge, metric_card, section_header, severity_badge,
                            show_rows, start, status_badge, vendor_label)

ws = start("Dashboard", "Open a count to see the records behind it. Use the page list to review or update individual records.")
if ws.operations is None:
    st.stop()

vendors, assessments, criticality, risks, decisions, actions = ws.operations
management, concentration, reviews = ws.management()
groups = {row["group"]: row for row in management if row["breakdown"] in ("total", "criticality", "decision", "flag")}
current_actions = [row for row in actions if row["current"]]
current_decisions = [row for row in decisions.values() if row["selection"] == "Current"]
services = [row for row in concentration if row["kind"] == "Service" and row["concentration"]]


def named(rows):
    return [dict(row, vendor=vendor_label(ws, row["vendor_id"])) for row in rows]


def measure(title, rows, id_field=None):
    ids = list(dict.fromkeys(row[id_field] for row in rows)) if id_field else []
    count = len(ids) if id_field else len(rows)
    with st.expander(f"{title} · {count}"):
        if title in ("Critical", "High", "Medium", "Low"):
            severity_badge(title)
        elif title in ("Approved", "Conditionally Approved", "Rejected", "Awaiting decision"):
            decision_badge(title)
        elif "Overdue" in title:
            status_badge("Overdue")
        elif "Expired" in title:
            status_badge("Expired")
        st.metric(title, count)
        if ids:
            st.write("Source records · " + ", ".join(ids))
        show_rows(rows)


def population(group):
    return named([dict(vendor_id=vid, assessment_id=vendors[vid]["current_assessment_id"],
                       service=vendors[vid]["service_description"])
                  for vid in groups.get(group, {}).get("vendor_ids", [])
                  if group != "Awaiting decision" or vendors[vid]["current_assessment_id"] not in ws.decision_errors])


section_header("Portfolio snapshot", "Current counts match the management report for the selected report date.")
criticality_counts = {band: len(groups.get(band, {}).get("vendor_ids", [])) for band in ("Critical", "High", "Medium", "Low")}
decision_counts = {outcome: len(groups.get(outcome, {}).get("vendor_ids", [])) for outcome in ("Approved", "Conditionally Approved", "Rejected", "Awaiting decision")}
for col, band in zip(st.columns(4), ("Critical", "High", "Medium", "Low")):
    with col:
        severity_badge(band)
        metric_card(f"{band} vendors", criticality_counts[band])
with st.expander("Risk distribution", expanded=True):
    st.bar_chart({"Criticality": list(criticality_counts),
                  "Current vendors": list(criticality_counts.values())},
                 x="Criticality", y="Current vendors", color="#C2410C")
for col, outcome in zip(st.columns(4), ("Approved", "Conditionally Approved", "Rejected", "Awaiting decision")):
    with col:
        decision_badge(outcome)
        metric_card(outcome, decision_counts[outcome])
with st.expander("Decision status distribution", expanded=True):
    st.bar_chart({"Decision status": list(decision_counts),
                  "Current vendors": list(decision_counts.values())},
                 x="Decision status", y="Current vendors", color="#1D4ED8")
for col, title, count in zip(st.columns(4), ("Current vendors", "Confirmed critical failures", "Overdue actions", "Expired approvals"), (len(population("Current vendors")), len(population("Confirmed critical failure")), sum(bool(a["action_overdue"]) for a in current_actions), sum(bool(d["expired_approval"]) for d in current_decisions))):
    with col: metric_card(title, count)
st.caption("Counts use each vendor’s current assessment. Recorded decision totals include expired outcomes, shown separately below.")
measure("Current vendors", population("Current vendors"), "vendor_id")
section_header("Attention required", "Open a list to review the source records behind each count.")
if ws.decision_errors:
    measure("Recorded decisions requiring review", named([
        dict(row, vendor_id=assessments[row["assessment_id"]]["vendor_id"],
             workflow_issue=ws.decision_errors[row["assessment_id"]])
        for row in ws.rows("decision") if row["assessment_id"] in ws.decision_errors
        and vendors[assessments[row["assessment_id"]]["vendor_id"]]["current_assessment_id"] == row["assessment_id"]
    ]), "decision_id")
measure("Confirmed critical failures", population("Confirmed critical failure"), "vendor_id")
measure("Unresolved critical questions", population("Unresolved critical question"), "vendor_id")
measure("Overdue reviews", named(reviews), "vendor_id")
measure("Open findings", named([row for row in current_actions if row["finding_status"] == "Open"]), "finding_id")
measure("Open conditions", named([row for row in current_decisions if row["open_condition"]]), "decision_id")

st.subheader("Overdue actions")
measure("Overdue corrective actions", named([row for row in current_actions if row["action_overdue"]]), "action_id")
st.subheader("Expired approvals")
measure("Expired approvals", named([row for row in current_decisions if row["expired_approval"]]), "decision_id")
st.subheader("Incomplete assessments")
measure("Incomplete assessments", population("Incomplete"), "assessment_id")

st.subheader("Supplier concentration")
measure("Concentration-risk services", [
    dict(service_id=row["source_id"], service_name=row["name"], tier=row["tier"],
         linked_vendors=[vendor_label(ws, vid) for vid in row["linked_ids"]])
    for row in services], "service_id")

st.subheader("Recent reassessments")
recent = sorted((row for row in assessments.values() if row["supersedes_id"]
                 and row["assessment_date"] <= ws.report_date.isoformat()),
                key=lambda row: row["assessment_date"], reverse=True)
show_rows(named(recent[:10]))
