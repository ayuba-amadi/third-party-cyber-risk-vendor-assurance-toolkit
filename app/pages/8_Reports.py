import streamlit as st

from app.export_helpers import REPORT_TYPES, export_package, render_report, report_payload, report_sections
from app.ui_helpers import select_assessment, select_vendor, start, show_rows

ws = start("Reports", "Choose a report and scope. Check the report date, review the result, then download the required formats.")
kind = st.selectbox("Report type", REPORT_TYPES)
vid = aid = ""
if kind in ("Individual vendor assessment", "Decision report", "Remediation report", "Reassessment comparison"):
    portfolio = kind != "Individual vendor assessment" and st.checkbox("Include all vendors", value=True)
    if not portfolio:
        vid = select_vendor(ws, "report")
        if kind != "Reassessment comparison":
            aid = select_assessment(ws, vid, "report")
st.write(f"Report date · {ws.report_date.isoformat()}")
st.caption("Overdue and expired states are calculated using this date. Changing it updates the working view for this session.")
if kind == "Management summary" and ws.operations is not None:
    management, concentration, reviews = ws.management()
    vendors, _, _, _, _, _ = ws.operations
    st.subheader("Management summary overview")
    totals = {row["group"]: row["count"] for row in management if row["breakdown"] == "total"}
    st.metric("Current vendors", totals.get("Current vendors", len(vendors)))
    st.subheader("Criticality, decisions and attention flags")
    summary_rows = [row for row in management if row["breakdown"] in ("criticality", "decision", "flag")]
    show_rows([dict(breakdown=row["breakdown"], group=row["group"], count=row["count"],
                    source_ids=row["source_ids"]) for row in summary_rows])
    st.subheader("Concentration risk")
    show_rows([dict(service=row["name"], tier=row["tier"], vendor_count=row["count"],
                    linked_vendors=row["linked_ids"])
               for row in concentration if row["kind"] == "Service" and row["concentration"]])
    st.subheader("Reconciliation")
    current_count = len(vendors)
    counts = {
        "Criticality groups": sum(row["count"] for row in management if row["breakdown"] == "criticality"),
        "Decision groups": sum(row["count"] for row in management if row["breakdown"] == "decision"),
        "Current vendor total": current_count,
    }
    show_rows([dict(measure=heading, count=count, expected=current_count,
                    status="Valid" if count == current_count else "Invalid")
               for heading, count in counts.items()], name="Management reconciliation")
    st.caption(f"Overdue reviews · {len(reviews)}. Counts reconcile by vendor ID.")
possible = (kind == "Data quality" or ws.operations is not None) and (
    kind != "Individual vendor assessment" or bool(aid))
key = (kind, vid, aid)
if st.button("Generate report", disabled=not possible):
    try:
        metadata, rows = report_payload(ws, kind, vid, aid)
        sections = report_sections(metadata, rows, workspace=ws, vendor_id=vid, assessment_id=aid)
        ws.reports[key] = (metadata, sections, render_report(metadata, rows, sections=sections))
    except (KeyError, ValueError) as exc:
        st.error(str(exc))
if key in ws.reports:
    metadata, sections, formats = ws.reports[key]
    slug = kind.lower().replace(" ", "-")
    st.subheader("Generated report")
    st.info("\n\n".join(metadata[field] for field in ("limitations", "scope", "calculation_reason")
                           if metadata.get(field)))
    for heading, rows, columns in sections:
        st.subheader(heading)
        show_rows(rows, columns=columns, name=heading)
    st.subheader("Download report")
    for col, (extension, mime, name) in zip(st.columns(4), (("csv", "text/csv", "CSV"), ("json", "application/json", "JSON"), ("md", "text/markdown", "Markdown"), ("html", "text/html", "HTML"))):
        with col: st.download_button(f"Download {name}", formats[extension], f"{slug}.{extension}", mime)
    if kind in ("Individual vendor assessment", "Management summary"):
        package = "assessment" if kind == "Individual vendor assessment" else "management"
        st.caption("The package contains this report and all changed CSV rows from this session.")
        st.download_button(f"Download {package} package", export_package(ws, {slug: formats}),
                           f"{package}-package.zip", "application/zip")
