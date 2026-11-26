import csv
from io import StringIO
import streamlit as st

from app.ui_helpers import (download_csv, label, save, select_vendor, severity_badge,
                            show_criticality, show_issues, show_rows, start, status_badge, vendor_label)
from src.config import ALLOWED_VALUES
from src.criticality import FACTORS
from src.schema import PHASE2_SCHEMAS

ws = start("Vendor register", "Search and filter the fictional supplier list. Select a vendor to review records or edit its details in this session.")
search_col, category_col, criticality_col, status_col = st.columns((2, 1, 1, 1))
with search_col: search = st.text_input("Search vendors", placeholder="Vendor ID or name").strip().casefold()
all_vendors = [dict(row, criticality=ws.criticality_preview(row).final_band) for row in ws.rows("vendor")]
with category_col:
    selected_category = st.multiselect("Category", sorted({row["category"] for row in all_vendors}), key="register_category")
with criticality_col:
    selected_criticality = st.multiselect("Criticality", ("Critical", "High", "Medium", "Low"), key="register_criticality")
with status_col:
    selected_status = st.multiselect("Assessment status", sorted({row["assessment_status"] for row in all_vendors}), key="register_assessment_status")
register = [row for row in all_vendors
            if search in f"{row['vendor_id']} {row['vendor_name']}".casefold()
            and (not selected_category or row["category"] in selected_category)
            and (not selected_criticality or row["criticality"] in selected_criticality)
            and (not selected_status or row["assessment_status"] in selected_status)]
show_rows([{key: row[key] for key in ("vendor_id", "vendor_name", "category", "criticality", "assessment_status")}
           for row in register])
download_csv(ws, "vendor", [next(row for row in ws.rows("vendor") if row["vendor_id"] == item["vendor_id"])
                             for item in register], "Download filtered vendor list", "filtered_vendor_export")
vid = select_vendor(ws, "register", [row["vendor_id"] for row in register])
selected = next((row for row in ws.rows("vendor") if row["vendor_id"] == vid), {})
if selected:
    current_criticality = ws.criticality_preview(selected)
    severity_badge(current_criticality.final_band)
    status_badge(selected["assessment_status"])
    st.caption(f"{selected['vendor_name']} · {selected['category']} · Current assessment {selected['current_assessment_id'] or 'not started'}")
    st.page_link("pages/3_Assessment.py", label="Open selected vendor for assessment")
    with st.expander("Linked business services"):
        service_ids = {row["service_id"] for row in ws.rows("vendor_service_link") if row["vendor_id"] == vid}
        show_rows([row for row in ws.rows("business_service") if row["service_id"] in service_ids])
    with st.expander("Why this criticality?"):
        show_criticality(current_criticality)
    download_csv(ws, "vendor", [selected], "Download vendor record", "selected_vendor_export")

st.subheader("Vendor details")
st.caption("Add a fictional supplier, import one complete vendor row, or edit the selected record. Changes stay in this session until downloaded.")
modes = ["Add vendor", "Import one CSV record"] + (["Edit selected vendor"] if selected else [])
mode = st.radio("Record entry", modes)
schema = PHASE2_SCHEMAS["vendor"]
replace = mode == "Edit selected vendor"
base = selected if replace else {"assessment_status": "Not started", "material_change_flag": "No"}
generation = st.session_state.get("vendor_form_generation", 0)
prefix = f"vendor_form_{mode}_{vid if replace else ''}_{generation}"
record = {}
if mode == "Import one CSV record":
    file = st.file_uploader("Fictional vendor CSV", type="csv", key=prefix)
    if file:
        try:
            reader = csv.DictReader(StringIO(file.getvalue().decode("utf-8-sig")), strict=True)
            rows = list(reader)
            if len(rows) != 1 or None in rows[0] or None in rows[0].values():
                raise ValueError("The CSV must contain exactly one complete vendor row.")
            if (set(reader.fieldnames or []) - set(schema.columns) or
                    len(reader.fieldnames or []) != len(set(reader.fieldnames or []))):
                raise ValueError("Use the vendor CSV headers. Unknown or repeated headers were found.")
            record = {field: rows[0].get(field, "").strip() for field in schema.columns}
        except (UnicodeError, csv.Error, ValueError) as exc:
            st.error(str(exc))
else:
    for field in schema.columns:
        if field == "current_assessment_id" or (replace and field == "vendor_id"):
            record[field] = base.get(field, "")
            continue
        title = label(field) + " *"
        options = ALLOWED_VALUES.get(("vendor", field))
        value = base.get(field, "")
        if options:
            record[field] = st.selectbox(title, ("", *options),
                index=options.index(value) + 1 if value in options else 0, key=f"{prefix}_{field}")
        else:
            record[field] = st.text_input(title, value, key=f"{prefix}_{field}",
                help="Enter YYYY-MM-DD." if field == "next_review_date" else None).strip()

if st.button("Clear form"):
    st.session_state.vendor_form_generation = generation + 1
    st.rerun()
validate = st.button("Validate vendor", disabled=not record)
calculate = st.button("Calculate criticality", disabled=not record)
submit = st.button("Save vendor to session", disabled=not record)
if validate or calculate or submit:
    candidate = ws.vendor_candidate(record, replace=replace)
    issues = ws.check(candidate)
    if issues:
        show_issues(issues)
    if not record.get("data_types"):
        st.error("Data types is required. Enter the fictional types of data involved, or None.")
    elif not issues:
        st.success("Vendor record passed validation.")
        if calculate or submit:
            result = ws.criticality_preview(record)
            show_criticality(result)
            changed = [field for field, _, _ in FACTORS if replace and record[field] != selected[field]]
            if changed:
                before = ws.criticality_preview(selected)
                delta = result.total_points - before.total_points
                st.write(f"Criticality comparison · {before.total_points} ({before.final_band}) → "
                         f"{result.total_points} ({result.final_band}) · {delta:+d} points")
                show_rows([dict(factor=label(field), previous=selected[field], updated=record[field])
                           for field in changed])
                if selected["current_assessment_id"]:
                    st.warning("Reassessment required. The saved assessment retains its original criticality factors.")
        download_csv(ws, "vendor", [record], "Download vendor record", "draft_vendor_export")
        if submit:
            ws.select_vendor(record["vendor_id"])
            st.session_state.pop("register_vendor", None)
            save(ws, candidate, f"Saved {record['vendor_name']} to this session.")
