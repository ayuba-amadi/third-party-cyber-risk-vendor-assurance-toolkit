"""Terminal entry point and Phase 1 structural validation reports."""

import argparse
import json
import shlex
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .config import (
    APPLICATION_NAME, APPLICATION_VERSION, DEFAULT_DATA_DIR, DEFAULT_REPORTS_DIR,
    PHASE_NOTICE,
)
from .loader import get_table_inventory, load_report_date, load_source_tables
from .validation import validate_tables

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


def main(argv=None):
    parser = argparse.ArgumentParser(description=f"{APPLICATION_NAME}: Phase 1 CSV foundation.")
    parser.add_argument("--version", action="version", version=APPLICATION_VERSION)
    commands = parser.add_subparsers(dest="command", required=True)
    inventory_parser = commands.add_parser("inventory", help="List source and reference file inventories.")
    validate_parser = commands.add_parser("validate", help="Validate source CSV structure and relationships.")
    for command in (inventory_parser, validate_parser):
        command.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR,
                             help="CSV directory (default: repository sample-data).")
    validate_parser.add_argument("--as-of", type=report_date_argument, default=load_report_date(),
                                 help="Report date in YYYY-MM-DD (default: 2026-11-18).")
    validate_parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR,
                                 help="Validation report directory (default: reports/phase1).")
    args = parser.parse_args(argv)
    data = load_source_tables(args.data_dir)
    if args.command == "inventory":
        print(inventory_markdown(get_table_inventory(data, include_references=True)))
        errors = [i for t in data.values() for i in t.issues if i.severity == "ERROR"]
        for issue in errors:
            print(display_issue(issue), file=sys.stderr)
        return 1 if errors else 0
    result = validate_tables(data)
    command = "python -m src.cli " + shlex.join(sys.argv[1:] if argv is None else argv)
    report = build_report(data, result, args.as_of, args.data_dir, command)
    print(PHASE_NOTICE)
    print(f"Report date used: {args.as_of.isoformat()}")
    for key, value in result.summary.items():
        print(f"{key.replace('_', ' ').capitalize()}: {value}")
    for issue in result.issues:
        print("\n" + display_issue(issue))
    # Report options must never overwrite a source, including a source with the
    # same name as a report in an analyst's custom data directory.
    source_dir = args.data_dir.resolve()
    report_dir = args.reports_dir.resolve()
    if report_dir == source_dir or source_dir in report_dir.parents:
        print("ERROR: Reports directory must be outside the source data directory. "
              "Correction: choose --reports-dir reports/phase1.", file=sys.stderr)
        return 2
    try:
        paths = write_reports(report, args.reports_dir)
    except OSError as exc:
        print(f"ERROR: Cannot write validation reports in {args.reports_dir}: {exc}. "
              "Correction: choose a writable --reports-dir.", file=sys.stderr)
        return 2
    for path in paths:
        print(f"Report: {path}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
