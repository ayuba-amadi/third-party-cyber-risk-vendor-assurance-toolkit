import streamlit as st

from app.export_helpers import REPORT_TYPES, export_package, render_report, report_payload
from app.ui_helpers import select_assessment, select_vendor, start

ws = start("Reports", "Choose a report, check the report date and scope, then generate and download the results.")
kind = st.selectbox("Report type", REPORT_TYPES)
vid = aid = ""
if kind in ("Individual vendor assessment", "Decision report", "Remediation report", "Reassessment comparison"):
    portfolio = kind != "Individual vendor assessment" and st.checkbox("Include all vendors", value=True)
    if not portfolio:
        vid = select_vendor(ws, "report")
        if kind != "Reassessment comparison":
            aid = select_assessment(ws, vid, "report")
st.write(f"Report date · {ws.report_date.isoformat()}")
possible = (kind == "Data quality" or ws.operations is not None) and (
    kind != "Individual vendor assessment" or bool(aid))
key = (kind, vid, aid)
if st.button("Generate report", disabled=not possible):
    try:
        ws.reports[key] = render_report(*report_payload(ws, kind, vid, aid))
    except (KeyError, ValueError) as exc:
        st.error(str(exc))
if key in ws.reports:
    formats = ws.reports[key]
    slug = kind.lower().replace(" ", "-")
    st.markdown(formats["md"])
    for extension, mime, name in (("csv", "text/csv", "CSV"), ("json", "application/json", "JSON"),
                                   ("md", "text/markdown", "Markdown"), ("html", "text/html", "HTML")):
        st.download_button(f"Download {name}", formats[extension], f"{slug}.{extension}", mime)
    if kind in ("Individual vendor assessment", "Management summary"):
        package = "assessment" if kind == "Individual vendor assessment" else "management"
        st.caption("The package contains this report and all changed CSV rows from this session.")
        st.download_button(f"Download {package} package", export_package(ws, {slug: formats}),
                           f"{package}-package.zip", "application/zip")
