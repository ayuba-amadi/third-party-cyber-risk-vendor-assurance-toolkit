"""Serialize CSV records and reports without touching the source directory."""
import csv
from dataclasses import asdict
from datetime import datetime, timezone
from html import escape
from io import BytesIO, StringIO
import json
from zipfile import ZIP_DEFLATED, ZipFile

from src.config import APPLICATION_VERSION
from src.operational_reports import LIMITATION, markdown_fields

REPORT_TYPES = (
    "Individual vendor assessment", "Management summary", "Decision report",
    "Remediation report", "Reassessment comparison", "Concentration risk", "Data quality",
)


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def csv_text(rows, fields=None):
    if fields is None:
        fields = list(dict.fromkeys(key for row in rows for key in row))
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: json_text(value).strip() if isinstance(value, (list, dict)) else value
                         for key, value in row.items()})
    return buffer.getvalue()


def table_csv(workspace, name, rows):
    return csv_text(rows, workspace.tables[name].headers)


def report_payload(workspace, kind, vendor_id="", assessment_id=""):
    metadata = dict(report=kind, report_date=workspace.report_date.isoformat(), fictional_data=True,
                    source_commit=workspace.commit, version=APPLICATION_VERSION,
                    source_files=[table.path.name for table in workspace.tables.values()],
                    limitations=LIMITATION, warnings=[asdict(issue) for issue in workspace.validation.issues])
    if kind == "Data quality":
        metadata["validation_summary"] = workspace.validation.summary
        metadata["calculation_reason"] = "The validator checks CSV fields, values, relationships and review history."
        rows = [dict(file=table.path.name, source_rows=len(workspace.source[name].rows),
                     working_rows=len(table.rows), loaded=table.loaded)
                for name, table in workspace.tables.items()]
        return metadata, rows

    vendors, assessments, criticality, risks, decisions, actions = workspace.operations
    metadata["warnings"].extend(workspace.decision_errors.values())

    def matches(row):
        return ((not vendor_id or row["vendor_id"] == vendor_id) and
                (not assessment_id or row["assessment_id"] == assessment_id))

    if kind in ("Management summary", "Concentration risk"):
        management, concentration, reviews = workspace.management()
        rows = management if kind == "Management summary" else concentration
        if kind == "Management summary":
            metadata["overdue_reviews"] = reviews
        metadata["scope"] = "Portfolio-wide, using the current assessment for each vendor."
        metadata["calculation_reason"] = (
            "Vendor counts use the current assessment. Open findings count distinct finding records."
            if kind == "Management summary" else
            "The report counts distinct vendor links per service and distinct service links per vendor."
        )
    elif kind == "Reassessment comparison":
        rows = [workspace.history(vid) for vid in vendors if not vendor_id or vid == vendor_id]
    elif kind == "Remediation report":
        rows = [row for row in actions if matches(row)]
        rows += [row for row in decisions.values() if row["outcome"] == "Conditionally Approved" and matches(row)]
    elif kind == "Decision report":
        rows = []
        for assessment in assessments.values():
            if matches(assessment):
                aid = assessment["assessment_id"]
                recorded = next((row for row in workspace.rows("decision") if row["assessment_id"] == aid), {})
                status = ("Awaiting decision" if not recorded else
                          "Recorded decision after report date" if recorded["decision_date"] > metadata["report_date"]
                          else "Recorded decision requires review")
                rows.append(decisions.get(aid, dict(
                    vendor_id=assessment["vendor_id"], assessment_id=aid,
                    outcome=status,
                    recorded_decision=recorded, source_ids=[aid, assessment["vendor_id"]] +
                    ([recorded["decision_id"]] if recorded else []),
                )))
    elif kind == "Individual vendor assessment":
        result, scores, domains = risks[assessment_id]
        evidence_ids = [row["evidence_id"] for row in scores if row["evidence_id"]]
        questions = {row["question_id"]: row["question_text"] for row in workspace.rows("question")}
        services = {row["service_id"]: row for row in workspace.rows("business_service")}
        decision = decisions.get(assessment_id, {})
        rows = [dict(
            vendor=vendors[vendor_id], assessment=assessments[assessment_id],
            criticality=criticality[assessment_id].to_dict(), risk=result, domain_progress=domains,
            questions=[dict(row, question_text=questions[row["question_id"]]) for row in scores],
            linked_services=[services[sid] for sid in criticality[assessment_id].linked_services],
            authorised_decision=decision or {"status": "See decision register for recorded status"},
            findings_and_actions=[row for row in actions if matches(row)],
            source_ids=[vendor_id, assessment_id, *questions, *evidence_ids] +
            ([decision["decision_id"]] if decision else []),
        )]
    else:
        raise ValueError(f"Unknown report type: {kind}")
    rows = [dict(row) for row in rows]
    names = {row["source_id"]: row["name"] for row in rows if kind == "Concentration risk"}
    for row in rows:
        if "vendor_id" in row:
            row["vendor_name"] = vendors[row["vendor_id"]]["vendor_name"]
        if "vendor_ids" in row:
            row["vendor_names"] = [vendors[vid]["vendor_name"] for vid in row["vendor_ids"]]
        if "linked_ids" in row:
            row["linked_names"] = [names[identifier] for identifier in row["linked_ids"]]
    return metadata, rows


def render_report(metadata, rows):
    title = metadata["report"]
    markdown = "\n".join([f"# {title}", "", *markdown_fields(metadata), "", "## Records", "",
                           *markdown_fields(rows), "" if rows else "No matching records."])
    return {
        "csv": csv_text([{**metadata, **row} for row in rows] or [metadata]),
        "json": json_text(dict(metadata, results=rows)),
        "md": markdown,
        "html": ("<!doctype html><html lang='en'><meta charset='utf-8'>"
                 f"<title>{escape(title)}</title><h1>{escape(title)}</h1>"
                 f"<pre style='white-space:pre-wrap'>{escape(markdown)}</pre></html>"),
    }


def export_package(workspace, reports, *, changed=None):
    if changed is None:
        changed = {name: workspace.changed_rows(name) for name in workspace.tables}
    manifest = dict(
        report_date=workspace.report_date.isoformat(),
        exported_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        source_commit=workspace.commit, version=APPLICATION_VERSION, fictional_data=True,
        validation_summary=workspace.validation.summary, decision_errors=workspace.decision_errors,
        changed_row_counts={name: len(rows) for name, rows in changed.items() if rows},
    )
    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json_text(manifest))
        archive.writestr("validation.json", json_text([asdict(issue) for issue in workspace.validation.issues]))
        for name, rows in changed.items():
            if rows:
                archive.writestr(f"changes/{name}.csv", table_csv(workspace, name, rows))
        for name, formats in reports.items():
            for extension, content in formats.items():
                archive.writestr(f"reports/{name}.{extension}", content)
    return buffer.getvalue()
