import streamlit as st

from app.ui_helpers import show_rows, start, vendor_label

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
        st.metric(title, count)
        if ids:
            st.write("Source records · " + ", ".join(ids))
        show_rows(rows)


def population(group):
    return named([dict(vendor_id=vid, assessment_id=vendors[vid]["current_assessment_id"],
                       service=vendors[vid]["service_description"])
                  for vid in groups.get(group, {}).get("vendor_ids", [])
                  if group != "Awaiting decision" or vendors[vid]["current_assessment_id"] not in ws.decision_errors])


st.caption("Counts use each vendor’s current assessment. Recorded decision totals include expired outcomes, shown separately below.")
st.subheader("Vendor overview")
for group in ("Current vendors", "Critical", "High", "Medium", "Low", "Awaiting decision",
              "Approved", "Conditionally Approved", "Rejected"):
    measure(group, population(group), "vendor_id")
if ws.decision_errors:
    measure("Recorded decisions requiring review", named([
        dict(row, vendor_id=assessments[row["assessment_id"]]["vendor_id"],
             workflow_issue=ws.decision_errors[row["assessment_id"]])
        for row in ws.rows("decision") if row["assessment_id"] in ws.decision_errors
        and vendors[assessments[row["assessment_id"]]["vendor_id"]]["current_assessment_id"] == row["assessment_id"]
    ]), "decision_id")
st.subheader("Critical attention required")
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
