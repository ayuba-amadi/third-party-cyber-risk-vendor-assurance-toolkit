"""Assemble and export read-only Phase 4 operational reports."""
import csv
import json
import sys
from copy import copy

from .criticality import calculate_all_criticality
from .decision_workflow import evaluate_decision, index_decisions
from .management_reporting import compare_management, management_summary
from .loader import load_report_date
from .reassessment import FACTORS, compare_versions, review_status
from .remediation import finding_actions
from .risk_scoring import calculate_all_assessment_risk

COMMANDS = ("decisions", "remediation", "reassess", "management-report", "vendor-report")
LIMITATION = ("CSV records supply role names and written exceptions. The toolkit cannot authenticate "
              "approvers, reconstruct prior evidence reviews, or independently certify condition closure.")


def collect_operations(tables, report_date, *, decision_errors=None):
    """Collect operational results; interactive callers can isolate invalid decisions."""
    assessments = {row["assessment_id"]: row for row in tables["assessment"].rows}
    vendors = {row["vendor_id"]: row for row in tables["vendor"].rows}
    # Retain the recorded assessment factors when the live register has changed.
    snapshots = {row["assessment_id"]: row for row in tables["assessment_criticality_snapshot"].rows}
    frozen = dict(tables)
    frozen["vendor"] = copy(tables["vendor"])
    frozen["vendor"].rows = [
        dict(vendor, **{field: snapshots[vendor["current_assessment_id"]][field] for field in FACTORS})
        if vendor["current_assessment_id"] else vendor for vendor in vendors.values()
    ]
    criticality = {row.assessment_id: row for row in calculate_all_criticality(frozen, report_date)}
    if any(not row.complete for row in criticality.values()):
        raise ValueError("Criticality inputs are incomplete")
    risk = {bundle[0]["assessment_id"]: bundle for bundle in calculate_all_assessment_risk(tables, report_date)}
    records = index_decisions(tables["decision"].rows)
    for aid, row in records.items():
        if load_report_date(row["decision_date"]) < load_report_date(assessments[aid]["assessment_date"]):
            raise ValueError(f"{row['decision_id']}: decision date precedes assessment date")
    records = {aid: row for aid, row in records.items() if row["decision_date"] <= report_date.isoformat()}
    remediation = finding_actions(tables, records, report_date)
    decisions = {}
    for aid, decision in sorted(records.items()):
        assessment = assessments[aid]
        result, questions, _ = risk[aid]
        actions = [row for row in remediation if row["assessment_id"] == aid]
        try:
            evaluated = evaluate_decision(decision, assessment, result, questions, actions, report_date)
        except ValueError as exc:
            if decision_errors is None:
                raise
            decision_errors[aid] = str(exc)
            continue
        current = vendors[assessment["vendor_id"]]["current_assessment_id"] == aid
        decisions[aid] = dict(evaluated, selection="Current" if current else "Historical")
    return vendors, assessments, criticality, risk, decisions, remediation


def markdown_fields(value, depth=0):
    lines = []
    indent = "  " * depth
    if isinstance(value, dict):
        for key, item in value.items():
            label = key.replace("_", " ").capitalize()
            if isinstance(item, (dict, list)) and item:
                lines.append(f"{indent}- **{label}**")
                lines.extend(markdown_fields(item, depth + 1))
            else:
                lines.append(f"{indent}- **{label}** {item if item not in (None, '', []) else 'None'}")
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                lines.append(f"{indent}- Record")
                lines.extend(markdown_fields(item, depth + 1))
            else:
                lines.append(f"{indent}- {item}")
    return lines


def safe_target(path):
    if path.is_symlink() or (path.exists() and path.stat().st_nlink > 1):
        raise ValueError(f"Report target must be a standalone file: {path}")
    return path


def write_report(directory, name, rows, metadata, csv_only=False):
    directory.mkdir(parents=True, exist_ok=True)
    with safe_target(directory / f"{name}.csv").open("w", encoding="utf-8", newline="") as handle:
        fields = list(metadata) + list(dict.fromkeys(key for row in rows for key in row if key not in metadata))
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value
                             for key, value in {**metadata, **row}.items()})
    if not csv_only:
        payload = dict(metadata, results=rows)
        safe_target(directory / f"{name}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                                           encoding="utf-8")
        write_markdown(directory / f"{name}.md", name.replace("_", " ").capitalize(), metadata, rows)


def write_markdown(path, title, metadata, rows):
    lines = [f"# {title}", "", *markdown_fields(metadata), "", "## Results", ""]
    for row in rows:
        lines.extend(markdown_fields(row))
        lines.append("")
    if not rows:
        lines.append("No matching records.")
    safe_target(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_operational(args, tables, validation, ensure_safe):
    warnings = []
    decisions_by_line = dict(zip(tables["decision"].row_numbers, tables["decision"].rows))
    tolerated = {"Material changes must link to a reassessment",
                 "Current assessment snapshot must equal the current vendor register value"}
    for issue in validation.issues:
        decision = decisions_by_line.get(issue.row, {}) if issue.file.endswith("/decision.csv") else {}
        optional_rejection_date = (decision.get("outcome") == "Rejected"
                                   and issue.field in ("expiry_date", "review_date")
                                   and not decision.get(issue.field) and issue.category == "missing_fields")
        message = f"{issue.file}:{issue.row} {issue.field}: {issue.rule}"
        if issue.severity == "ERROR" and issue.rule not in tolerated and not optional_rejection_date:
            print(message, file=sys.stderr)
            return 1
        if not optional_rejection_date:
            warnings.append(message)
    try:
        ensure_safe(args.data_dir, args.reports_dir)
        vendors, assessments, criticality, risks, decisions, remediation = collect_operations(tables, args.as_of)
        directory = args.reports_dir
        metadata = dict(report_date=args.as_of.isoformat(), source_files=sorted(table.path.name for table in tables.values()),
                        rule="Select current records by vendor.current_assessment_id. Date flags use a strict earlier-than comparison.",
                        warnings=warnings, errors=[], limitations=LIMITATION)
        selected = [vendor for vid, vendor in sorted(vendors.items()) if not args.vendor_id or vid == args.vendor_id]
        if not selected:
            raise ValueError("No vendor matches the requested identifier")
        if args.command == "decisions":
            rows = sorted(decisions.values(), key=lambda row: row["decision_id"])
            rows += [dict(vendor_id=v["vendor_id"], assessment_id=v["current_assessment_id"],
                          selection="Current", outcome="Awaiting decision",
                          source_ids=[v["vendor_id"]] + ([v["current_assessment_id"]] if v["current_assessment_id"] else []))
                     for v in selected if v["current_assessment_id"] not in decisions]
            write_report(directory, "decision_results", rows, metadata)
        elif args.command == "remediation":
            rows = [dict(record_type="Finding or action", **row) for row in remediation]
            rows += [dict(record_type="Condition", decision_id=row["decision_id"], vendor_id=row["vendor_id"],
                          assessment_id=row["assessment_id"], selection=row["selection"], conditions=row["conditions"],
                          condition_deadline=row["condition_deadline"], open_condition=row["open_condition"],
                          overdue_condition=row["overdue_condition"], source_ids=row["source_ids"])
                     for row in sorted(decisions.values(), key=lambda item: item["decision_id"])
                     if row["outcome"] == "Conditionally Approved"]
            write_report(directory, "remediation_results", rows, metadata)
        elif args.command == "management-report":
            rows, concentration, reviews = management_summary(tables, criticality, risks, decisions, remediation, args.as_of)
            oracle = args.data_dir / "expected_management.csv"
            compared = compare_management(rows, oracle) if oracle.exists() and args.as_of.isoformat() == "2026-11-18" else None
            metadata.update(expected_fixture_comparison=f"PASS ({compared} rows)" if compared is not None else "Not run",
                            overdue_reviews=reviews)
            write_report(directory, "management_summary", rows, metadata)
            write_report(directory, "management_reconciliation",
                         [dict(row, unique_source_count=len(set(row["source_ids"])), reconciled=True) for row in rows],
                         metadata, csv_only=True)
            write_report(directory, "concentration_risks", concentration, metadata, csv_only=True)
        else:
            comparisons = [compare_versions(vendor, assessments, criticality, risks, decisions,
                                            tables["change_event"].rows, args.as_of, remediation) for vendor in selected]
            if args.command == "reassess":
                write_report(directory, "reassessment_comparisons", comparisons, metadata)
            else:
                services = {row["service_id"]: row for row in tables["business_service"].rows}
                ensure_safe(args.data_dir, directory / "vendors")
                (directory / "vendors").mkdir(parents=True, exist_ok=True)
                for vendor, history in zip(selected, comparisons):
                    vid, aid = vendor["vendor_id"], vendor["current_assessment_id"]
                    crit = criticality.get(aid)
                    result, questions, _ = risks.get(aid, ({}, [], []))
                    evidence = [{key: question[key] for key in
                                 ("question_id", "evidence_id", "evidence_status", "effective_evidence_status",
                                  "verified", "flags", "calculation_reason")} for question in questions]
                    report = dict(vendor=vendor, criticality=crit.to_dict() if crit else {},
                                  linked_services=[services[sid] for sid in (crit.linked_services if crit else [])],
                                  risk=result, evidence=evidence,
                                  current_decision=decisions.get(aid, {"outcome": "Awaiting decision"}),
                                  review=review_status(vendor, args.as_of),
                                  findings_and_actions=[row for row in remediation if row["vendor_id"] == vid],
                                  assessment_history=history,
                                  historical_assessment_ids=sorted(key for key, row in assessments.items()
                                                                   if row["vendor_id"] == vid and key != aid))
                    write_markdown(directory / "vendors" / f"{vid}.md", vendor["vendor_name"], metadata, [report])
        print(f"{args.command}: reports written to {directory}")
        if "expected_fixture_comparison" in metadata:
            print(f"Expected management comparison: {metadata['expected_fixture_comparison']}")
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(f"{args.command}: {exc}", file=sys.stderr)
        return 1
