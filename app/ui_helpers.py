"""Shared navigation, selection, messages and display components."""
from html import escape

import streamlit as st

from app.export_helpers import table_csv
from app.state import Workspace
from src.config import APPLICATION_NAME, DEFAULT_DATA_DIR

PAGES = (
    ("Dashboard", "1_Dashboard"), ("Vendor Register", "2_Vendor_Register"),
    ("Assessment", "3_Assessment"), ("Evidence Review", "4_Evidence_Review"),
    ("Decisions", "5_Decisions"), ("Remediation", "6_Remediation"),
    ("Reassessment", "7_Reassessment"), ("Reports", "8_Reports"),
    ("Data Quality", "9_Data_Quality"),
)

PALETTE = {
    "Critical": ("#7F1D1D", "#FEE2E2", "#B91C1C"),
    "High": ("#7C2D12", "#FFEDD5", "#C2410C"),
    "Medium": ("#713F12", "#FEF3C7", "#A16207"),
    "Low": ("#14532D", "#DCFCE7", "#15803D"),
    "Approved": ("#14532D", "#DCFCE7", "#15803D"),
    "Conditionally Approved": ("#713F12", "#FEF3C7", "#A16207"),
    "Rejected": ("#7F1D1D", "#FEE2E2", "#B91C1C"),
    "Awaiting decision": ("#1E3A8A", "#DBEAFE", "#1D4ED8"),
    "Awaiting Decision": ("#1E3A8A", "#DBEAFE", "#1D4ED8"),
    "Overdue": ("#7F1D1D", "#FEE2E2", "#B91C1C"),
    "Expired": ("#7F1D1D", "#FEE2E2", "#B91C1C"),
    "Missing": ("#7C2D12", "#FFEDD5", "#C2410C"),
    "Missing Evidence": ("#7C2D12", "#FFEDD5", "#C2410C"),
    "Received": ("#1E3A8A", "#DBEAFE", "#1D4ED8"),
    "Accepted": ("#14532D", "#DCFCE7", "#15803D"),
    "Accepted Evidence": ("#14532D", "#DCFCE7", "#15803D"),
    "Rejected Evidence": ("#7F1D1D", "#FEE2E2", "#B91C1C"),
    "Incomplete": ("#713F12", "#FEF3C7", "#A16207"),
    "Valid": ("#14532D", "#DCFCE7", "#15803D"),
    "Invalid": ("#7F1D1D", "#FEE2E2", "#B91C1C"),
    "Reassessment due": ("#713F12", "#FEF3C7", "#A16207"),
    "In progress": ("#1E3A8A", "#DBEAFE", "#1D4ED8"),
    "Assessed": ("#14532D", "#DCFCE7", "#15803D"),
    "PASS": ("#14532D", "#DCFCE7", "#15803D"),
    "WARNING": ("#713F12", "#FEF3C7", "#A16207"),
    "ERROR": ("#7F1D1D", "#FEE2E2", "#B91C1C"),
    "Warning": ("#713F12", "#FEF3C7", "#A16207"),
    "Error": ("#7F1D1D", "#FEE2E2", "#B91C1C"),
    "INCOMPLETE": ("#713F12", "#FEF3C7", "#A16207"),
}


def _badge(label, default=("#1F2937", "#F3F4F6", "#9CA3AF")):
    value = str(label)
    text, bg, border = PALETTE.get(value, default)
    st.markdown(
        f'<span class="status-badge" aria-label="{escape(value)}" '
        f'style="--badge-text:{text};--badge-bg:{bg};--badge-border:{border}">'
        f'{escape(value)}</span>', unsafe_allow_html=True,
    )


def severity_badge(label):
    return _badge(label)


def decision_badge(label):
    return _badge(label)


def evidence_badge(label):
    aliases = {"Missing": "Missing Evidence", "Accepted": "Accepted Evidence",
               "Rejected": "Rejected Evidence"}
    return _badge(aliases.get(str(label), label))


def status_badge(label):
    return _badge(label)

def metric_card(label, value, help_text=None):
    st.metric(label, value, help=help_text)

def section_header(title, description=None):
    st.subheader(title)
    if description: st.caption(description)

def show_validation_message(result):
    passed = getattr(result, "passed", bool(result))
    (st.success if passed else st.error)("Valid · Validation passed" if passed else "Invalid · Validation issues found")

def show_source_ids(ids):
    ids = list(ids)
    if ids: st.caption("Source records · " + ", ".join(ids))

def show_calculation_explanation(lines):
    for line in lines: st.write(line)

HELP = {
    "Criticality": "How much the organisation depends on the vendor and what the vendor can access.",
    "Risk rating": "The level of risk supported by questionnaire answers and reviewed evidence.",
    "Evidence status": "Missing means unavailable. Received means awaiting review. Accepted means the reviewer accepted it. Rejected means it failed review. Expired means it is out of date.",
    "Incomplete assessment": "At least one question lacks a verified answer supported by accepted evidence.",
    "Critical failure": "A confirmed failure on a question that covers an essential safeguard.",
    "Conditional approval": "A human decision that requires specific corrective work by a deadline.",
    "Reassessment": "A new version of an assessment reviewed after a change or when a review is due.",
    "Concentration risk": "Several suppliers support the same service, or one supplier supports several services. Review the linked records to understand the dependency.",
}


def start(title, instructions):
    if "workspace" not in st.session_state:
        st.session_state.workspace = Workspace.load()
    ws = st.session_state.workspace
    with st.sidebar:
        st.header(APPLICATION_NAME)
        ws.set_report_date(st.date_input("Report date", ws.report_date, key="report_date",
                                         help="Changes overdue and expiry flags for this session."))
        st.caption(f"Fictional data directory · {DEFAULT_DATA_DIR.name}")
        st.write(f"Selected vendor · {vendor_label(ws, ws.vendor_id)}")
        status_badge("Valid" if ws.validation.passed and not ws.decision_errors else "Invalid")
        st.caption("Use the page list to move between tasks.")
        if st.button("Reset session", help="Clears your unsaved edits and reloads the fictional fixtures."):
            st.session_state.clear()
            st.rerun()
    st.title(title)
    with st.expander("How to use this page"):
        st.write(instructions)
    for message in ws.messages:
        st.success(message)
    ws.messages.clear()
    if ws.calculation_error:
        st.error(ws.calculation_error)
        show_issues(ws.validation.issues)
    for error in ws.decision_errors.values():
        st.warning(error)
    return ws


def label(field):
    return field.replace("_", " ").capitalize().replace(" id", " ID")


def vendor_label(ws, vid):
    return next((f"{vid} · {row['vendor_name']}" for row in ws.rows("vendor")
                 if row["vendor_id"] == vid), vid or "None")


def assessment_label(row):
    return f"{row['assessment_id']} · Version {row['version_no']} · {row['trigger']} · {row['status']}"


def question_label(row):
    return f"{row['question_id']} · {row['question_text']}"


def select_vendor(ws, key, ids=None):
    ids = ids if ids is not None else [row["vendor_id"] for row in ws.rows("vendor")]
    if not ids:
        st.info("No vendors match the current selection.")
        return ""
    widget_key = f"{key}_vendor"

    def update_selection():
        ws.select_vendor(st.session_state[widget_key])

    selected = st.selectbox("Vendor", ids, index=ids.index(ws.vendor_id) if ws.vendor_id in ids else 0,
                            format_func=lambda vid: vendor_label(ws, vid), key=widget_key,
                            on_change=update_selection)
    if selected != ws.vendor_id:
        ws.select_vendor(selected)
    return selected


def select_assessment(ws, vid, key):
    rows = {row["assessment_id"]: row for row in ws.rows("assessment") if row["vendor_id"] == vid}
    if not rows:
        st.info("This vendor has no assessment.")
        return ""
    ids = list(rows)
    aid = st.selectbox("Assessment", ids, index=ids.index(ws.assessment_id) if ws.assessment_id in ids else 0,
                       format_func=lambda value: assessment_label(rows[value]), key=f"{key}_{vid}_assessment")
    ws.assessment_id = aid
    return aid


def show_issues(issues):
    for issue in issues:
        display = st.error if issue.severity == "ERROR" else st.warning
        severity_badge(issue.severity.title())
        status_badge("Invalid" if issue.severity == "ERROR" else "Incomplete")
        display(f"{issue.file.rsplit('/', 1)[-1]}, row {issue.row}, {label(issue.field)} "
                f"({issue.value or 'blank'}) · {issue.rule}. Correction: {issue.correction}")


def save(ws, candidate, message):
    issues = ws.save(candidate)
    if issues:
        show_issues(issues)
    else:
        ws.messages.append(message)
        st.rerun()


def show_rows(rows):
    if rows:
        st.dataframe(rows, hide_index=True, column_config={
            name: label(name) for row in rows for name in row
        })
    else:
        st.info("No matching records.")


def filters(rows, fields, prefix, formatters=None):
    formatters = formatters or {}
    column_count = min(4, len(fields))
    columns = st.columns(column_count) if column_count else []
    for index, field in enumerate(fields):
        choices = sorted({row[field] for row in rows if row.get(field) not in (None, "")})
        with columns[index % column_count]:
            selected = st.multiselect(label(field), choices, key=f"{prefix}_{field}",
                                      format_func=formatters.get(field, str))
        if selected:
            rows = [row for row in rows if row.get(field) in selected]
    return rows


def download_csv(ws, name, rows, caption, key=None):
    st.download_button(caption, table_csv(ws, name, rows), f"{name}.csv", "text/csv", key=key)


def show_criticality(result):
    st.markdown("**Criticality classification**")
    severity_badge(result.final_band)
    st.write(f"Final classification · **{result.final_band}** · {result.total_points} points")
    for item in result.calculation_trace[2:]:
        st.write(item)
    for error in result.errors:
        st.error(error)
