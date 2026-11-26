"""Serialize CSV records and reports without touching the source directory."""
from collections import Counter
import csv
from dataclasses import asdict
from datetime import datetime, timezone
from html import escape
from io import BytesIO, StringIO
import json
from zipfile import ZIP_DEFLATED, ZipFile

from app.ui_helpers import TABLE_CSS, label, table_html
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


SOURCE_PURPOSES = {
    "vendor": "Supplier profiles and review dates",
    "business_service": "Business services and service tiers",
    "vendor_service_link": "Supplier-to-service relationships",
    "assessment": "Assessment dates, versions and status",
    "assessment_criticality_snapshot": "Criticality inputs by assessment version",
    "question": "Questionnaire, weights and evidence criteria",
    "response": "Vendor claims and reviewer answers",
    "evidence_item": "Evidence records and review status",
    "finding": "Assessment findings",
    "corrective_action": "Action owners, deadlines and closure",
    "decision": "Human approvals, rejections and conditions",
    "change_event": "Material changes and reassessment links",
    "reviewer_audit_entry": "Review and editing history",
}

EVIDENCE_NOTES = {
    "Missing": "Evidence is unavailable.",
    "Received": "Evidence is awaiting review.",
    "Accepted": "The reviewer accepted the evidence.",
    "Rejected": "The evidence failed review.",
    "Expired": "The evidence is out of date.",
}


def field_rows(fields):
    return [dict(field=label(key), value=value) for key, value in fields.items()]


def finding_rows(rows):
    return [
        dict(finding_id=row["finding_id"], vendor_id=row["vendor_id"], assessment_id=row["assessment_id"],
             severity=row["severity"], description=row["description"], action=row["action_text"],
             responsible_party=row["responsible_party"], deadline=row["due_date"],
             status=row["action_status"] or row["finding_status"],
             overdue="Overdue" if row["action_overdue"] else "No")
        for row in rows
    ]


def decision_rows(rows, *, include_ids=False):
    result = []
    for row in rows:
        recorded = row.get("recorded_decision", row)
        details = dict(decision=row.get("outcome", row.get("status")),
                       decision_maker=recorded.get("decision_maker_role"),
                       justification=recorded.get("justification"), conditions=recorded.get("conditions"),
                       deadline=recorded.get("condition_deadline"), review_date=recorded.get("review_date"))
        if include_ids:
            details = dict(vendor_id=row["vendor_id"], assessment_id=row["assessment_id"], **details)
        result.append(details)
    return result


def reassessment_rows(history, risks, *, include_ids=False):
    result = []
    previous = ""
    for version in history["versions"]:
        aid = version["assessment_id"]
        current = risks[aid][0]["final_rating"] if aid in risks else ""
        changes = [event["change_type"] for event in history["change_events"]
                   if event["reassessment_assessment_id"] == aid]
        pending = version["selection"] == "Current" and history["reassessment_required"]
        details = dict(version=version["version_no"], assessment_date=version["assessment_date"],
                       material_change=changes or (version["trigger"] if version["trigger"] == "Material change" else "None linked"),
                       previous_rating=previous, current_rating=current,
                       reassessment_status="Reassessment due" if pending else version["status"])
        if include_ids:
            details = dict(vendor_id=history["vendor_id"], assessment_id=aid, **details)
        result.append(details)
        previous = current
    return result


def report_sections(metadata, rows, *, workspace=None, vendor_id="", assessment_id=""):
    """Project an existing report payload into display tables without altering its exports."""
    kind = metadata["report"]
    individual = rows[0] if kind == "Individual vendor assessment" and rows else None
    vendor = (individual["vendor"] if individual else
              next((row for row in workspace.rows("vendor") if row["vendor_id"] == vendor_id), {})
              if workspace and vendor_id else {})
    vendor_scope = f"{vendor['vendor_name']} ({vendor['vendor_id']})" if vendor else vendor_id or "Portfolio-wide"
    assessment_scope = individual["assessment"]["assessment_id"] if individual else assessment_id or "All in scope"
    risks = workspace.operations[3] if workspace and workspace.operations else {}

    sections = []

    def add(title, records, columns=None):
        sections.append((title, records, columns))

    add("Report metadata", [dict(report_item=key, value=value) for key, value in (
        ("Report type", kind), ("Vendor", vendor_scope), ("Assessment", assessment_scope),
        ("Report date", metadata["report_date"]), ("Fictional-data status", "Fictional data"),
        ("Source commit", metadata["source_commit"] or "Unavailable"), ("Toolkit version", metadata["version"]),
    )])
    if vendor:
        add("Vendor profile", field_rows(vendor))

    findings_columns = ("finding_id", "vendor_id", "assessment_id", "severity", "description",
                        "action", "responsible_party", "deadline", "status", "overdue")
    reassessment_columns = ("version", "assessment_date", "material_change", "previous_rating",
                            "current_rating", "reassessment_status")
    if individual:
        criticality, risk, questions = (individual[key] for key in ("criticality", "risk", "questions"))
        counts = Counter(row["effective_evidence_status"] for row in questions)
        total = len(questions)
        failures = risk["confirmed_critical_failures"]
        add("Risk and assessment summary", [dict(measure=key, result=value, explanation=note)
            for key, value, note in (
                ("Criticality score", criticality["total_points"], "Total points across the criticality factors."),
                ("Criticality band", criticality["final_band"], criticality["override_reasons"] or "Based on the total points."),
                ("Risk percentage", f"{float(risk['risk_percent']):.2f}%", risk["calculation_trace"][0]),
                ("Risk rating", risk["final_rating"], risk["score_label"]),
                ("Completeness", risk["completeness"], f"{risk['verified_count']} of {total} questions verified."),
                ("Verified responses", risk["verified_count"], "Reviewer-verified answers supported by accepted evidence."),
                ("Accepted evidence", counts["Accepted"], f"Effective status on {risk['evidence_as_of']}."),
                ("Confirmed critical failures", len(failures), failures or "No confirmed failures."),
            )])
        add("Evidence summary", [dict(evidence_status=status, count=counts[status],
                                      percentage=f"{counts[status] / total:.1%}" if total else "0.0%", notes=note)
                                 for status, note in EVIDENCE_NOTES.items()])
        add("Findings and corrective actions", finding_rows(individual["findings_and_actions"]), findings_columns)
        add("Decision record", decision_rows([individual["authorised_decision"]]))
        if workspace:
            try:
                history = workspace.history(vendor["vendor_id"])
            except ValueError as exc:
                add("Reassessment information", [dict(reassessment_status=str(exc))], reassessment_columns)
            else:
                add("Reassessment information", reassessment_rows(history, risks), reassessment_columns)
                if history["change_events"]:
                    add("Material changes and review triggers", history["change_events"])
                if history["pending_triggers"]:
                    add("Outstanding review triggers", [dict(trigger=value) for value in history["pending_triggers"]])
        add("Domain completeness", individual["domain_progress"])
        add("Question results", [{key: row[key] for key in (
            "question_id", "question_text", "vendor_claim", "verified_answer", "effective_evidence_status",
            "risk_value", "calculation_reason")} for row in questions])
        add("Linked services", individual["linked_services"])
        add("Source records", [dict(record_ids=individual["source_ids"])])
    elif kind == "Decision report":
        add("Decision record", decision_rows(rows, include_ids=True))
    elif kind == "Remediation report":
        add("Findings and corrective actions", finding_rows([row for row in rows if "finding_id" in row]), findings_columns)
        add("Conditional decisions", decision_rows([row for row in rows if "outcome" in row], include_ids=True))
    elif kind == "Reassessment comparison":
        add("Reassessment information", [record for history in rows
                                         for record in reassessment_rows(history, risks, include_ids=True)],
            ("vendor_id", "assessment_id", *reassessment_columns))
        add("Material changes", [event for history in rows for event in history["change_events"]])
        add("Outstanding review triggers", [dict(vendor_id=history["vendor_id"], trigger=trigger)
                                            for history in rows for trigger in history["pending_triggers"]])
    else:
        add(kind if kind != "Data quality" else "Source table checks", rows)
        if kind == "Management summary":
            add("Overdue reviews", metadata["overdue_reviews"])

    counts = {table.path.name: len(table.rows) for table in workspace.tables.values()} if workspace else {}
    add("Source files", [dict(file=file, rows=counts.get(file), purpose=SOURCE_PURPOSES.get(file.removesuffix(".csv"), ""))
                         for file in metadata["source_files"]])
    if metadata["warnings"]:
        add("Warnings", [warning if isinstance(warning, dict) else dict(warning=warning)
                         for warning in metadata["warnings"]])
    return sections


def render_report(metadata, rows, *, sections=None):
    title = metadata["report"]
    markdown = "\n".join([f"# {title}", "", *markdown_fields(metadata), "", "## Records", "",
                           *markdown_fields(rows), "" if rows else "No matching records."])
    if sections is None:
        sections = report_sections(metadata, rows)
    tables = "".join(f"<h2>{escape(heading)}</h2>{table_html(records, columns=columns, name=heading)}"
                     for heading, records, columns in sections)
    notes = "".join(f"<p>{escape(metadata[key])}</p>" for key in ("limitations", "scope", "calculation_reason")
                    if metadata.get(key))
    return {
        "csv": csv_text([{**metadata, **row} for row in rows] or [metadata]),
        "json": json_text(dict(metadata, results=rows)),
        "md": markdown,
        "html": ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
                 "<meta name='viewport' content='width=device-width, initial-scale=1'>"
                 f"<title>{escape(title)}</title><style>{TABLE_CSS}"
                 "body { max-width:90rem; margin:1.5rem auto; padding:0 1rem; color:#1F2937;"
                 "font:15px/1.45 sans-serif; } h1,h2 { color:#123B5D; }"
                 "aside { background:#F3F4F6; border-left:3px solid #64748B; padding:.2rem .8rem; }"
                 f"</style></head><body><h1>{escape(title)}</h1><aside>{notes}</aside>{tables}</body></html>"),
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
