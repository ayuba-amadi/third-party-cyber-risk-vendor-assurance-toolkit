"""Phase 3 report exports and fixture comparison."""
import csv
import json
import sys
from pathlib import Path

from .loader import load_table
from .risk_scoring import calculate_all_assessment_risk

SCOPE = ("Phase 3 implements questionnaire processing, evidence evaluation, "
         "domain completeness and risk scoring only. Approval decisions, corrective actions, "
         "reassessments, management reporting, Streamlit GUI and deployment remain later phases.")

ORACLES = {
    "risk_results": ("expected_risk.csv", ("assessment_id",)),
    "question_scores": ("expected_question_scores.csv", ("assessment_id", "question_id")),
    "domain_completeness": ("expected_domain_completeness.csv", ("assessment_id", "domain")),
}


def collect_rows(results):
    return {
        "risk_results": [result for result, _, _ in results],
        "question_scores": [row for _, scores, _ in results for row in scores],
        "domain_completeness": [row for _, _, domains in results for row in domains],
    }


def compare_fixture(rows, data_dir):
    comparisons = {}
    for name, (filename, keys) in ORACLES.items():
        path = Path(data_dir) / filename
        if not path.exists():
            comparisons[name] = dict(status="NOT_AVAILABLE", errors=[], rows=0)
            continue
        table = load_table(path)
        errors = [issue.rule for issue in table.issues]
        expected = {tuple(row[k] for k in keys): row for row in table.rows} if not errors else {}
        actual = {}
        for row in rows[name]:
            projected = dict(row)
            if name == "question_scores":
                projected.update(weight=row["question_weight"], assigned_value=row["risk_value"],
                                 weighted_points=row["weighted_risk_points"],
                                 evidence_status=row["effective_evidence_status"],
                                 confirmed_failure="Yes" if row["confirmed_critical_failure"] else "No",
                                 unresolved_critical="Yes" if row["unresolved_critical_question"] else "No")
            key = tuple(row[k] for k in keys)
            actual[key] = projected
        if len(expected) != len(table.rows):
            errors.append("Oracle contains duplicate keys or unreadable records")
        for key in sorted(expected.keys() | actual.keys()):
            if key not in actual or key not in expected:
                errors.append(f"{key}: missing {'calculated' if key not in actual else 'expected'} row")
                continue
            for field, value in expected[key].items():
                got = actual[key].get(field)
                if isinstance(got, list):
                    matches = sorted(got) == sorted(value.split(";") if value else [])
                elif field == "completeness_percent":
                    matches = got is not None and float(got) == float(value)
                else:
                    matches = str(got) == value
                if not matches:
                    errors.append(f"{key} {field}: expected {value!r}, actual {got!r}")
        comparisons[name] = dict(status="FAIL" if errors else "PASS", errors=errors, rows=len(expected))
    return comparisons


def write_reports(rows, comparisons, args):
    directory = args.reports_dir
    directory.mkdir(parents=True, exist_ok=True)
    filenames = [f"{name}.{extension}" for name in rows for extension in ("csv", "json")]
    for filename in filenames + ["risk_results.md"]:
        target = directory / filename
        if target.is_symlink() or (target.exists() and target.stat().st_nlink > 1):
            raise ValueError(f"Report target must be a standalone file: {target}")
    for name, records in rows.items():
        with (directory / f"{name}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
            writer.writeheader()
            for row in records:
                writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v
                                 for k, v in row.items()})
        payload = dict(report_date=args.as_of.isoformat(), results=records, fixture_comparison=comparisons[name])
        (directory / f"{name}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                                encoding="utf-8")
    lines = ["# Phase 3 assessment risk", "", SCOPE, "",
             f"Report date: {args.as_of.isoformat()}", f"Source directory: {args.data_dir}", "",
             "## Scoring methodology", "",
             "Multiply assigned risk by question weight. Divide the sum by four times the sum of all weights.",
             "Bands start at 0%, 20%, 40% and 60%. Thresholds use the unrounded percentage.", "",
             "## Evidence and completeness rules", "",
             "Verified credit requires an answered claim, accepted evidence with reviewer details and valid expiry,",
             "and a valid reviewer verified answer. Expiry on the evidence evaluation date remains valid.",
             "Unverified responses receive 4. Each question remains in the denominator.",
             "Incomplete assessments display provisional percentages. Superseded assessments use their assessment date.", "",
             "## Critical failure rules", "",
             "A verified value of 3 or 4 on a critical question receives 4 and sets a High minimum for completed ratings.",
             "An unverified critical question remains unresolved.", "", "## Assessment results", ""]
    for row in rows["risk_results"]:
        lines += [f"### {row['assessment_id']} / {row['vendor_id']}", ""]
        lines += [f"- {item}" for item in row["calculation_trace"]]
        for field in ("evidence_flags", "unanswered_questions"):
            if row[field]:
                lines.append(f"- {field.replace('_', ' ').capitalize()}: " + ", ".join(row[field]))
        lines.append("")
    lines += ["## Question examples", ""]
    examples = [row for row in rows["question_scores"] if row["flags"]] or rows["question_scores"]
    for row in examples[:8]:
        lines.append(f"- {row['assessment_id']} / {row['question_id']} — {row['calculation_reason']}")
    lines += ["", "## Domain completeness", "", "| Assessment | Domain | Answered | Verified | Complete |",
              "|---|---|---:|---:|---:|"]
    for row in rows["domain_completeness"]:
        lines.append(f"| {row['assessment_id']} | {row['domain']} | {row['answered_count']}/{row['total_questions']} | "
                     f"{row['verified_count']}/{row['total_questions']} | {float(row['completeness_percent']):.2f}% |")
    lines += ["", "## Expected fixture comparison", ""]
    for name, comparison in comparisons.items():
        lines.append(f"- {name}: {comparison['status']} ({comparison['rows']} oracle rows)")
        lines.extend(f"  - {error}" for error in comparison["errors"])
    lines += ["", "## Limitations", "", SCOPE,
              "The engine evaluates recorded reviewer judgments. Evidence artifacts are outside the supplied CSV data.",
              "Fixture comparisons run for the fixture report date and cover the full input even when output is filtered."]
    (directory / "risk_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_risk(args, data, validation, ensure_safe):
    if not validation.passed:
        for issue in validation.issues:
            print(f"{issue.file}:{issue.row} {issue.field}: {issue.rule}. {issue.correction}", file=sys.stderr)
        return 1
    try:
        ensure_safe(args.data_dir, args.reports_dir)
        results = calculate_all_assessment_risk(data, args.as_of)
        selected = [bundle for bundle in results
                    if (args.assessment_id is None or bundle[0]["assessment_id"] == args.assessment_id)
                    and (args.vendor_id is None or bundle[0]["vendor_id"] == args.vendor_id)]
        if not selected:
            raise ValueError("No assessment matches the requested identifier")
        comparisons = (compare_fixture(collect_rows(results), args.data_dir) if args.as_of.isoformat() == "2026-11-18"
                       else {key: dict(status="NOT_RUN_FOR_REPORT_DATE", errors=[], rows=0) for key in ORACLES})
        write_reports(collect_rows(selected), comparisons, args)
    except (ValueError, OSError, KeyError) as exc:
        print(f"Risk report error: {exc}", file=sys.stderr)
        return 1
    for result, questions, _ in selected:
        print(f"{result['assessment_id']} / {result['vendor_id']}")
        for line in result["calculation_trace"]:
            print(line)
        for row in questions:
            if args.command == "question-scores" or row["flags"]:
                print(f"{row['question_id']}: {', '.join(row['flags'])} {row['calculation_reason']}")
    for name, comparison in comparisons.items():
        print(f"{name}: {comparison['status']} ({comparison['rows']} oracle rows)")
        for error in comparison["errors"]:
            print(error, file=sys.stderr)
    return int(any(item["status"] == "FAIL" for item in comparisons.values()))
