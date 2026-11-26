from collections import Counter
from dataclasses import asdict
import streamlit as st

from app.ui_helpers import filters, show_issues, show_rows, start

ws = start("Data quality", "Run validation to check the working CSV records. Use the issue filters to find the exact file, row and correction.")
if st.button("Run validation"):
    ws.refresh()
    if ws.validation.passed and not ws.decision_errors:
        st.success("Validation passed.")
    else:
        st.warning("Validation found issues. Review the records below.")
st.write(f"Last validation (UTC) · {ws.validated_at}")
st.write(f"Working data · **{'Passed' if ws.validation.passed and not ws.decision_errors else 'Issues found'}**")
issues_by_file = Counter(issue.file for issue in ws.validation.issues if issue.severity == "ERROR")
show_rows([dict(file=table.path.name, source_rows=len(ws.source[name].rows),
                working_rows=len(table.rows), loaded=table.loaded, errors=issues_by_file[str(table.path)])
           for name, table in ws.tables.items()])
st.subheader("Validation issue counts")
issues = ws.validation.issues
categories = {
    "Duplicate records": lambda issue: issue.category == "duplicates",
    "Missing fields": lambda issue: issue.category == "missing_fields",
    "Invalid values or dates": lambda issue: issue.category in ("invalid_values", "date_errors"),
    "Orphan relationships": lambda issue: issue.category == "orphans",
    "Evidence inconsistencies": lambda issue: issue.file.endswith("/evidence_item.csv"),
    "Decision inconsistencies": lambda issue: issue.file.endswith("/decision.csv"),
    "Reassessment inconsistencies": lambda issue: issue.file.endswith(("/change_event.csv", "/assessment_criticality_snapshot.csv",
                                                                       "/assessment.csv")),
}
for caption, matches in categories.items():
    relevant = [issue for issue in issues if matches(issue)]
    extra = list(ws.decision_errors.values()) if caption == "Decision inconsistencies" else []
    with st.expander(f"{caption} · {len(relevant) + len(extra)}"):
        show_issues(relevant)
        for error in extra:
            st.error(error)
        if not relevant and not extra:
            st.write("No issues found.")
st.subheader("All validation records")
rows = filters([asdict(issue) for issue in issues], ("severity", "category"), "quality")
show_rows(rows)
