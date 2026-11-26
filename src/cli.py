"""Terminal entry point and Phase 1 structural validation reports."""

import argparse
import csv
import json
import shlex
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .config import (
    APPLICATION_NAME, APPLICATION_VERSION, CRITICALITY_SNAPSHOT_TABLE, DEFAULT_DATA_DIR,
    DEFAULT_PHASE2_REPORTS_DIR, DEFAULT_REPORTS_DIR, PHASE2_NOTICE, PHASE_NOTICE,
)
from .loader import get_table_inventory, load_report_date, load_source_tables, load_table
from .validation import validate_tables
from .criticality import calculate_all_criticality

LIMITATIONS = [
    PHASE_NOTICE,
    "Expected outputs, negative-test cases and validation_results.txt are reference files, not source inputs.",
    "All rows remain in memory, including invalid rows. An error means the data is not ready for later processing.",
    "Dates are checked for format and ordering; overdue, expiry and completeness flags are later-phase behavior.",
    "The schema has no onboarding, finding-creation or action-creation dates; comparisons requiring these dates cannot be checked. Closing an action before its due date is valid.",
    "Evidence review time is held in reviewer_audit_entry.timestamp; review_period_end is the covered period, not the review date. Fictional evidence paths are not opened.",
    "Evidence pairs are unique in this fixture, as enforced by its research validator. Replacement-evidence history and composite-key audit references need schema-owner resolution before later workflow work.",
    "Historical criticality factors exist only in an expected-output file; that file is not loaded as a source.",
    "Scoring, approval authority and independence, workflow transitions, remediation management, vendor/management reports and GUI are outside Phase 1. A structural pass is not policy approval.",
]


def report_date_argument(value):
    try:
        return load_report_date(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def display_issue(issue):
    return (
        f"{issue.severity}\nFile: {issue.file}\nRow: {issue.row}\n"
        f"Field: {issue.field}\nValue: {issue.value!r}\nRule: {issue.rule}\n"
        f"Correction: {issue.correction}"
    )


def markdown_cell(value):
    """Keep CSV text from altering a Markdown table's structure."""
    text = str(value if value is not None else "n/a")
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace("|", "&#124;").replace("\r", " ").replace("\n", "<br>"))


def inventory_markdown(inventory):
    lines = ["| Table | File | Rows | Columns | Primary identifier | Classification | Loaded |",
             "|---|---|---:|---:|---|---|---|"]
    fields = ("table", "file", "row_count", "column_count", "primary_identifier", "classification", "loaded")
    for item in inventory:
        lines.append("| " + " | ".join(markdown_cell(item[key]) for key in fields) + " |")
    return "\n".join(lines)


def build_report(data, result, report_date, data_dir, command):
    now = datetime.now(timezone.utc)
    return {
        "application": APPLICATION_NAME, "version": APPLICATION_VERSION,
        "execution_date": now.date().isoformat(), "executed_at_utc": now.isoformat(),
        "report_date": report_date.isoformat(), "data_directory": str(Path(data_dir).resolve()),
        "command": command, "scope": PHASE_NOTICE,
        "status": "PASS" if result.passed else "FAIL",
        "inventory": get_table_inventory(data), "summary": result.summary,
        "errors": [asdict(i) for i in result.issues if i.severity == "ERROR"],
        "warnings": [asdict(i) for i in result.issues if i.severity == "WARNING"],
        "limitations": LIMITATIONS,
        "row_number_convention": "Physical CSV line (last line for a multiline record); 1 = header; 0 = file-level issue.",
        "research_fixture_validator": {
            "status": "NOT_RUN_BY_THIS_COMMAND",
            "command": "python3 sample-data/validate_fixture.py",
            "note": "Run separately; recorded verification result is in 02-toolkit-development/PHASE_1_STATUS.md.",
        },
    }


def write_reports(report, reports_dir):
    directory = Path(reports_dir)
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "validation_report.json"
    md_path = directory / "validation_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Phase 1 structural CSV validation", "", report["scope"], "",
             f"Status: **{report['status']}**", "",
             f"Execution date (UTC): {report['execution_date']}", "",
             f"Executed at (UTC): {report['executed_at_utc']}", "",
             f"Report date used: {report['report_date']}", "",
             f"Repository data directory: {markdown_cell(report['data_directory'])}", "",
             f"Command used: `{report['command']}`", "",
             report["row_number_convention"], "", "## Source-table inventory", "",
             inventory_markdown(report["inventory"]), "", "## Validation summary", "",
             "| Measure | Count |", "|---|---:|"]
    lines.extend(f"| {key.replace('_', ' ')} | {value} |" for key, value in report["summary"].items())
    for key in ("errors", "warnings"):
        lines += ["", "## " + key.title(), ""]
        if not report[key]:
            lines.append("NONE")
        for issue in report[key]:
            lines += [f"### {issue['severity']}", ""]
            for field in ("file", "row", "field", "value", "rule", "severity", "correction", "category"):
                lines.append(f"- {field.title()}: {markdown_cell(issue[field])}")
            lines.append("")
    lines += ["", "## Research fixture validator", "",
              "Run separately with `python3 sample-data/validate_fixture.py`. "
              "This CLI does not execute it. See PHASE_1_STATUS.md for the recorded result.",
              "", "## Limitations", ""]
    lines.extend("- " + limit for limit in report["limitations"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def ensure_report_directory_is_safe(data_dir, reports_dir):
    source_dir = Path(data_dir).resolve()
    report_dir = Path(reports_dir).resolve()
    if report_dir == source_dir or source_dir in report_dir.parents:
        raise ValueError("Reports directory must be outside the source data directory.")


def build_semantic_report(data, result, report_date, data_dir, command):
    now = datetime.now(timezone.utc)
    errors = [asdict(issue) for issue in result.issues if issue.severity == "ERROR"]
    warnings = [asdict(issue) for issue in result.issues if issue.severity == "WARNING"]
    return {
        "application": APPLICATION_NAME,
        "version": APPLICATION_VERSION,
        "execution_date": now.date().isoformat(),
        "executed_at_utc": now.isoformat(),
        "report_date": report_date.isoformat(),
        "source_directory": str(Path(data_dir).resolve()),
        "command": command,
        "scope": PHASE2_NOTICE,
        "status": "PASS" if result.passed else "FAIL",
        "summary": result.summary,
        "overdue_actions": result.overdue_actions,
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "Validation checks the supplied CSV state; it cannot recover a prior file version that was never preserved.",
            "Evidence record IDs, audit events and assessment versions provide the available history trail.",
            "This phase does not calculate security risk, evidence scores or decisions.",
        ],
    }


def write_semantic_reports(report, reports_dir):
    directory = Path(reports_dir)
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "semantic_validation_report.json"
    md_path = directory / "semantic_validation_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                         encoding="utf-8")
    lines = ["# Phase 2 semantic validation", "", report["scope"], "",
             f"Status: **{report['status']}**", "",
             f"Execution date (UTC): {report['execution_date']}", "",
             f"Report date: {report['report_date']}", "",
             f"Source directory: {markdown_cell(report['source_directory'])}", "",
             "## Summary", "", "| Measure | Count |", "|---|---:|"]
    lines.extend(f"| {markdown_cell(key.replace('_', ' '))} | {value} |"
                 for key, value in report["summary"].items())
    lines += ["", "## Overdue corrective actions", ""]
    if report["overdue_actions"]:
        lines += ["| Action | Finding | Vendor | Due date | Status |", "|---|---|---|---|---|"]
        for action in report["overdue_actions"]:
            lines.append("| " + " | ".join(markdown_cell(action[field]) for field in
                         ("action_id", "finding_id", "vendor_id", "due_date", "status")) + " |")
    else:
        lines.append("NONE")
    lines += ["", "## Validation errors", ""]
    if not report["errors"]:
        lines.append("NONE")
    for issue in report["errors"]:
        lines += [f"### {markdown_cell(issue['file'])}, row {issue['row']}", "",
                  f"- Field: {markdown_cell(issue['field'])}",
                  f"- Value: {markdown_cell(issue['value'])}",
                  f"- Rule: {markdown_cell(issue['rule'])}",
                  f"- Correction: {markdown_cell(issue['correction'])}", ""]
    lines += ["", "## Limitations", ""]
    lines.extend("- " + limit for limit in report["limitations"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def _criticality_rows(results, data):
    vendors = {row.get("vendor_id"): row for row in data["vendor"].rows}
    rows = []
    for result in results:
        row = result.to_dict()
        vendor = vendors.get(result.vendor_id, {})
        row["vendor_name"] = vendor.get("vendor_name", "")
        rows.append(row)
    return rows


def compare_expected_criticality(rows, data_dir):
    """Read the expected-output oracle only for explicit result comparison."""
    expected_path = Path(data_dir) / "expected_criticality.csv"
    if not expected_path.exists():
        return {"status": "NOT_AVAILABLE", "expected_rows": 0, "compared_rows": 0,
                "mismatches": [f"Expected-output oracle not found: {expected_path.name}"]}
    with expected_path.open(encoding="utf-8", newline="") as handle:
        expected = {row["assessment_id"]: row for row in csv.DictReader(handle)}
    mismatches = []
    fields = ("vendor_id", "data_sensitivity", "system_access", "dependency_impact",
              "replaceability", "total_points", "base_band", "final_band")
    for row in rows:
        reference = expected.get(row["assessment_id"])
        if reference is None:
            mismatches.append(f"{row['assessment_id']}: no expected row")
            continue
        for field in fields:
            value = row.get(field)
            if str(value if value is not None else "") != reference[field]:
                mismatches.append(f"{row['assessment_id']}.{field}: calculated {value!r}, expected {reference[field]!r}")
        expected_overrides = set(filter(None, reference.get("override_reasons", "").split(";")))
        actual_overrides = set(row.get("override_reasons", []))
        if actual_overrides != expected_overrides:
            mismatches.append(f"{row['assessment_id']}.override_reasons: calculated "
                              f"{sorted(actual_overrides)!r}, expected {sorted(expected_overrides)!r}")
    status = "PASS" if not mismatches and len(rows) == len(expected) else "FAIL"
    if not mismatches and len(rows) != len(expected):
        mismatches.append(f"Compared {len(rows)} rows; expected oracle contains {len(expected)} rows")
    return {"status": status, "expected_rows": len(expected), "compared_rows": len(rows),
            "mismatches": mismatches}


def build_criticality_report(rows, validation_report, comparison, report_date, data_dir, command):
    now = datetime.now(timezone.utc)
    return {
        "application": APPLICATION_NAME,
        "version": APPLICATION_VERSION,
        "execution_date": now.date().isoformat(),
        "executed_at_utc": now.isoformat(),
        "report_date": report_date.isoformat(),
        "source_directory": str(Path(data_dir).resolve()),
        "command": command,
        "scope": PHASE2_NOTICE,
        "methodology": {
            "formula": "Data sensitivity + system access + dependency impact + replaceability",
            "thresholds": {"2-3": "Low", "4-6": "Medium", "7-9": "High", "10-13": "Critical"},
            "overrides": [
                "Business-critical service sets a minimum band of High.",
                "Regulated data plus Privileged access sets Critical.",
                "Dependency impact 4 plus Very hard replacement sets Critical.",
            ],
        },
        "results": rows,
        "validation_status": validation_report["status"],
        "validation_errors": validation_report["errors"],
        "expected_criticality_comparison": comparison,
        "historical_snapshot_treatment": (
            "Every assessment uses its own assessment_criticality_snapshot row. ASMT-004 uses "
            "the historical values retained in that snapshot; current VEN-004 fields are used "
            "only for ASMT-011 and are never substituted for ASMT-004."
        ),
        "limitations": [
            "Phase 2 implements criticality calculation and semantic validation only.",
            "Risk scoring, evidence scoring, decisions, remediation, management reporting and GUI remain later-phase work.",
            "Assessment factors are only as reliable as their supplied snapshot source.",
            "The expected_criticality.csv file is read only for this explicit comparison; it does not supply calculation inputs.",
        ],
    }


def write_criticality_reports(report, reports_dir):
    directory = Path(reports_dir)
    directory.mkdir(parents=True, exist_ok=True)
    csv_path = directory / "criticality_results.csv"
    json_path = directory / "criticality_results.json"
    md_path = directory / "criticality_results.md"
    fields = ("assessment_id", "vendor_id", "vendor_name", "data_sensitivity",
              "data_sensitivity_points", "system_access", "system_access_points",
              "dependency_impact", "dependency_points", "replaceability",
              "replaceability_points", "total_points", "base_band", "linked_services",
              "highest_service_tier", "override_reasons", "final_band", "complete",
              "errors", "calculation_trace")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for result in report["results"]:
            row = {key: result.get(key) for key in fields}
            for key in ("linked_services", "override_reasons", "errors", "calculation_trace"):
                row[key] = json.dumps(row[key], ensure_ascii=False, sort_keys=True)
            writer.writerow(row)
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                         encoding="utf-8")
    lines = ["# Phase 2 criticality results", "", report["scope"], "",
             f"Execution date (UTC): {report['execution_date']}", "",
             f"Report date: {report['report_date']}", "",
             f"Source directory: {markdown_cell(report['source_directory'])}", "",
             "## Calculation methodology", "",
             report["methodology"]["formula"], "",
             "| Total points | Base band |", "|---:|---|"]
    lines.extend(f"| {score} | {band} |" for score, band in report["methodology"]["thresholds"].items())
    lines += ["", "Overrides:", ""]
    lines.extend("- " + value for value in report["methodology"]["overrides"])
    lines += ["", "## Assessment results", "",
              "| Vendor | Name | Assessment | Factors (points) | Total | Base | Overrides | Final | Complete |",
              "|---|---|---|---|---:|---|---|---|---|"]
    for row in report["results"]:
        factor_text = (f"{row['data_sensitivity']} ({row['data_sensitivity_points']}), "
                       f"{row['system_access']} ({row['system_access_points']}), "
                       f"{row['dependency_impact']} ({row['dependency_points']}), "
                       f"{row['replaceability']} ({row['replaceability_points']})")
        lines.append("| " + " | ".join(markdown_cell(value) for value in (
            row["vendor_id"], row["vendor_name"], row["assessment_id"], factor_text,
            row["total_points"], row["base_band"], "; ".join(row["override_reasons"]) or "None",
            row["final_band"], row["complete"])) + " |")
        lines.append("")
        lines.append("**Calculation trace**")
        lines.extend("- " + markdown_cell(item) for item in row["calculation_trace"])
    lines += ["", "## Incomplete-input errors", ""]
    incomplete = [row for row in report["results"] if not row["complete"]]
    if not incomplete and not report["validation_errors"]:
        lines.append("NONE")
    for row in incomplete:
        lines.append(f"### {row['assessment_id']} / {row['vendor_id']}")
        for error in row["errors"]:
            lines.append(f"- {markdown_cell(error['field'])}: {markdown_cell(error['message'])}; "
                         f"value={markdown_cell(error['value'])}; correction={markdown_cell(error['correction'])}")
    if report["validation_errors"]:
        lines += ["", "Semantic validation errors:"]
        for issue in report["validation_errors"]:
            lines.append(f"- {markdown_cell(issue['file'])}, row {issue['row']}, "
                         f"{markdown_cell(issue['field'])}: {markdown_cell(issue['rule'])}")
    lines += ["", "## Historical snapshot treatment", "", report["historical_snapshot_treatment"],
              "", "## Comparison with expected_criticality.csv", "",
              f"Status: **{report['expected_criticality_comparison']['status']}**", "",
              f"Compared rows: {report['expected_criticality_comparison']['compared_rows']} / "
              f"{report['expected_criticality_comparison']['expected_rows']}", ""]
    if report["expected_criticality_comparison"]["mismatches"]:
        lines.extend("- " + markdown_cell(item) for item in report["expected_criticality_comparison"]["mismatches"])
    else:
        lines.append("All selected assessment results and override reasons match the expected output oracle.")
    lines += ["", "## Limitations", ""]
    lines.extend("- " + value for value in report["limitations"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csv_path, json_path, md_path


def display_criticality_result(row):
    print(f"Vendor: {row['vendor_id']} — {row['vendor_name']}")
    print(f"Assessment: {row['assessment_id']}")
    print("Factors: " + "; ".join((
        f"Data sensitivity {row['data_sensitivity']} ({row['data_sensitivity_points']})",
        f"System access {row['system_access']} ({row['system_access_points']})",
        f"Dependency impact {row['dependency_impact']} ({row['dependency_points']})",
        f"Replaceability {row['replaceability']} ({row['replaceability_points']})")))
    print(f"Total score: {row['total_points']}; base band: {row['base_band']}")
    print("Override reasons: " + ("; ".join(row["override_reasons"]) or "None"))
    print(f"Final band: {row['final_band']}; complete: {row['complete']}")
    if row["errors"]:
        print("Validation errors:")
        for error in row["errors"]:
            print(f"- {error['field']}={error['value']!r}: {error['message']} "
                  f"Correction: {error['correction']}")
    for trace in row["calculation_trace"]:
        print(f"  {trace}")


def phase2_source_report(args, command):
    data = load_source_tables(args.data_dir, include_criticality_snapshot=True)
    result = validate_tables(data, args.as_of)
    report = build_semantic_report(data, result, args.as_of, args.data_dir, command)
    return data, result, report


def main(argv=None):
    from .operational_reports import COMMANDS, run_operational
    from .risk_reports import run_risk

    parser = argparse.ArgumentParser(description=f"{APPLICATION_NAME}: CSV assurance toolkit.")
    parser.add_argument("--version", action="version", version=APPLICATION_VERSION)
    commands = parser.add_subparsers(dest="command", required=True)
    inventory_parser = commands.add_parser("inventory", help="List source and reference file inventories.")
    validate_parser = commands.add_parser("validate", help="Validate source CSV structure and relationships.")
    semantic_parser = commands.add_parser("semantic-validate", help="Validate Phase 2 relationships and business rules.")
    criticality_parser = commands.add_parser("criticality", help="Calculate assessment criticality from stored snapshots.")
    for command in (inventory_parser, validate_parser):
        command.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR,
                             help="CSV directory (default: repository sample-data).")
    validate_parser.add_argument("--as-of", type=report_date_argument, default=load_report_date(),
                                 help="Report date in YYYY-MM-DD (default: 2026-11-18).")
    validate_parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR,
                                 help="Validation report directory (default: reports/phase1).")
    for command in (semantic_parser, criticality_parser):
        command.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR,
                             help="CSV directory (default: repository sample-data).")
        command.add_argument("--as-of", type=report_date_argument, default=load_report_date(),
                             help="Report date in YYYY-MM-DD (default: 2026-11-18).")
        command.add_argument("--reports-dir", type=Path, default=DEFAULT_PHASE2_REPORTS_DIR,
                             help="Phase 2 report directory (default: reports/phase2).")
    selection = criticality_parser.add_mutually_exclusive_group()
    selection.add_argument("--assessment-id", help="Calculate one assessment version.")
    selection.add_argument("--vendor-id", help="Calculate all assessment versions for a vendor.")
    selection.add_argument("--all", action="store_true", help="Calculate every assessment (the default).")
    for name in ("risk", "question-scores"):
        risk_parser = commands.add_parser(name, help="Evaluate questionnaire evidence and calculate risk.")
        risk_parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
        risk_parser.add_argument("--as-of", type=report_date_argument, default=load_report_date())
        risk_parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR.parent / "phase3")
        filters = risk_parser.add_mutually_exclusive_group()
        filters.add_argument("--assessment-id")
        filters.add_argument("--vendor-id")
        filters.add_argument("--all", action="store_true")
    for name in COMMANDS:
        operational = commands.add_parser(name, help="Validate and report recorded operational results.")
        operational.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
        operational.add_argument("--as-of", type=report_date_argument, default=load_report_date())
        operational.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR.parent / "phase4")
        if name in ("reassess", "vendor-report"):
            operational.add_argument("--vendor-id")
        else:
            operational.set_defaults(vendor_id=None)
    args = parser.parse_args(argv)
    if args.command in COMMANDS:
        data = load_source_tables(args.data_dir, include_criticality_snapshot=True)
        return run_operational(args, data, validate_tables(data, args.as_of), ensure_report_directory_is_safe)
    if args.command in ("risk", "question-scores"):
        data = load_source_tables(args.data_dir, include_criticality_snapshot=True)
        return run_risk(args, data, validate_tables(data, args.as_of), ensure_report_directory_is_safe)
    if args.command == "inventory":
        data = load_source_tables(args.data_dir)
        snapshot_path = Path(args.data_dir) / f"{CRITICALITY_SNAPSHOT_TABLE}.csv"
        if snapshot_path.exists():
            data[CRITICALITY_SNAPSHOT_TABLE] = load_table(snapshot_path)
    elif args.command == "validate":
        data = load_source_tables(args.data_dir)
    else:
        data = load_source_tables(args.data_dir, include_criticality_snapshot=True)
    if args.command == "inventory":
        print(inventory_markdown(get_table_inventory(data, include_references=True)))
        errors = [i for t in data.values() for i in t.issues if i.severity == "ERROR"]
        for issue in errors:
            print(display_issue(issue), file=sys.stderr)
        return 1 if errors else 0
    command = "python -m src.cli " + shlex.join(sys.argv[1:] if argv is None else argv)
    if args.command == "validate":
        result = validate_tables(data, args.as_of)
        report = build_report(data, result, args.as_of, args.data_dir, command)
        print(PHASE_NOTICE)
        print(f"Report date used: {args.as_of.isoformat()}")
        for key, value in result.summary.items():
            print(f"{key.replace('_', ' ').capitalize()}: {value}")
        for issue in result.issues:
            print("\n" + display_issue(issue))
        try:
            ensure_report_directory_is_safe(args.data_dir, args.reports_dir)
            paths = write_reports(report, args.reports_dir)
        except ValueError as exc:
            print(f"ERROR: {exc} Correction: choose --reports-dir reports/phase1.", file=sys.stderr)
            return 2
        except OSError as exc:
            print(f"ERROR: Cannot write validation reports in {args.reports_dir}: {exc}. "
                  "Correction: choose a writable --reports-dir.", file=sys.stderr)
            return 2
        for path in paths:
            print(f"Report: {path}")
        return 0 if result.passed else 1

    data, result, validation_report = phase2_source_report(args, command)
    if args.command == "semantic-validate":
        print(PHASE2_NOTICE)
        print(f"Report date used: {args.as_of.isoformat()}")
        for key, value in result.summary.items():
            print(f"{key.replace('_', ' ').capitalize()}: {value}")
        print(f"Overdue corrective actions: {len(result.overdue_actions)}")
        for issue in result.issues:
            print("\n" + display_issue(issue))
        try:
            ensure_report_directory_is_safe(args.data_dir, args.reports_dir)
            paths = write_semantic_reports(validation_report, args.reports_dir)
        except ValueError as exc:
            print(f"ERROR: {exc} Correction: choose --reports-dir reports/phase2.", file=sys.stderr)
            return 2
        except OSError as exc:
            print(f"ERROR: Cannot write semantic validation reports in {args.reports_dir}: {exc}. "
                  "Correction: choose a writable --reports-dir.", file=sys.stderr)
            return 2
        for path in paths:
            print(f"Report: {path}")
        return 0 if result.passed else 1

    all_results = calculate_all_criticality(data, args.as_of)
    if args.assessment_id:
        selected = [row for row in all_results if row.assessment_id == args.assessment_id]
    elif args.vendor_id:
        selected = [row for row in all_results if row.vendor_id == args.vendor_id]
    else:
        selected = all_results
    if (args.assessment_id and not selected) or (args.vendor_id and not selected):
        issue = {"file": "assessment.csv", "row": 0,
                 "field": "assessment_id" if args.assessment_id else "vendor_id",
                 "value": args.assessment_id or args.vendor_id,
                 "rule": "Requested identifier must exist in the loaded source records",
                 "severity": "ERROR", "correction": "Check the identifier against assessment.csv and vendor.csv.",
                 "category": "orphans"}
        validation_report["errors"].append(issue)
        validation_report["status"] = "FAIL"
    rows = _criticality_rows(selected, data)
    comparison_rows = _criticality_rows(all_results, data)
    comparison = compare_expected_criticality(comparison_rows, args.data_dir)
    report = build_criticality_report(rows, validation_report, comparison,
                                      args.as_of, args.data_dir, command)
    print(PHASE2_NOTICE)
    print(f"Report date used: {args.as_of.isoformat()}")
    for row in rows:
        display_criticality_result(row)
    for issue in validation_report["errors"]:
        print("\nSEMANTIC VALIDATION ERROR")
        print(f"File: {issue['file']}\nRow: {issue['row']}\nField: {issue['field']}\n"
              f"Value: {issue['value']!r}\nRule: {issue['rule']}\n"
              f"Correction: {issue['correction']}")
    print(f"Expected criticality comparison: {comparison['status']} "
          f"({comparison['compared_rows']}/{comparison['expected_rows']} rows)")
    try:
        ensure_report_directory_is_safe(args.data_dir, args.reports_dir)
        paths = write_criticality_reports(report, args.reports_dir)
    except ValueError as exc:
        print(f"ERROR: {exc} Correction: choose --reports-dir reports/phase2.", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERROR: Cannot write criticality reports in {args.reports_dir}: {exc}. "
              "Correction: choose a writable --reports-dir.", file=sys.stderr)
        return 2
    for path in paths:
        print(f"Report: {path}")
    complete = all(row.complete for row in selected)
    return 0 if result.passed and complete and comparison["status"] in ("PASS", "NOT_AVAILABLE") else 1


if __name__ == "__main__":
    raise SystemExit(main())
