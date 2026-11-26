"""Structural validation of the approved CSVs. Does not calculate or change data."""

import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime

from .config import ALLOWED_VALUES, SOURCE_TABLES
from .loader import load_report_date
from .schema import IDENTIFIER_PATTERNS, SCHEMAS, ValidationIssue


@dataclass
class ValidationResult:
    issues: list[ValidationIssue]
    summary: dict

    @property
    def passed(self):
        return self.summary["errors"] == 0


def validate_tables(data):
    """Validate every raw row and retain all rows for inspection.

    Errors make a row unsuitable for later processing; Phase 1 does not select
    accepted rows or resolve conflicting duplicates. Joins always use identifiers.
    """
    issues = [issue for table in data.values() for issue in table.issues]

    def add(name, number, field, value, rule, correction, category="invalid_values"):
        issues.append(ValidationIssue(
            str(data[name].path), number, field, str(value or ""), rule, "ERROR",
            correction, category,
        ))

    def required(name, number, row, field, context="Required field must not be blank"):
        if not row.get(field, "") or not row[field].strip():
            add(name, number, field, row.get(field), context,
                f"Supply {field} using the approved data dictionary.", "missing_fields")

    def records(name):
        return zip(data[name].row_numbers, data[name].rows)

    # Use only unambiguous identifiers as join targets. Never choose a duplicate
    # parent according to row order.
    indexes = {}
    key_counts = {}
    for name, schema in SCHEMAS.items():
        table = data[name]
        counts = Counter(tuple(row.get(k) for k in schema.primary_key) for row in table.rows)
        key_counts[name] = counts
        indexes[name] = {
            tuple(row.get(k) for k in schema.primary_key): row for row in table.rows
            if counts[tuple(row.get(k) for k in schema.primary_key)] == 1
        }
        for key_fields in (schema.primary_key,) + schema.extra_unique_keys:
            seen = {}
            for number, row in records(name):
                key = tuple(row.get(k) for k in key_fields)
                if not all(key):
                    continue
                if key in seen:
                    add(name, number, ", ".join(key_fields), " | ".join(key),
                        f"{', '.join(key_fields)} must be unique; also at CSV row {seen[key]}",
                        "Remove the duplicate from a working copy or assign a new immutable "
                        "identifier for a distinct record; inspect both rows.", "duplicates")
                else:
                    seen[key] = number

    for name, schema in SCHEMAS.items():
        for number, row in records(name):
            for field in schema.required_fields:
                required(name, number, row, field)
            for field in schema.columns:
                value = row.get(field)
                if not value or not value.strip():
                    continue
                allowed = ALLOWED_VALUES.get((name, field))
                if allowed and value not in allowed:
                    add(name, number, field, value, "Value must be in the dictionary's allowed values",
                        "Use one of: " + ", ".join(allowed) + ".")
                pattern = IDENTIFIER_PATTERNS.get(field)
                if pattern and not re.fullmatch(pattern, value):
                    add(name, number, field, value, f"Identifier must match {pattern}",
                        "Use the approved identifier format and update references consistently.")
                if field in schema.date_fields:
                    try:
                        load_report_date(value)
                    except ValueError:
                        add(name, number, field, value, "Date must be a real ISO date (YYYY-MM-DD)",
                            "Supply a valid calendar date such as 2026-11-18.", "date_errors")
            for field, parent, parent_field in schema.foreign_keys:
                value = row.get(field)
                if not value or not value.strip():
                    continue
                count = key_counts[parent].get((value,), 0)
                if count == 0:
                    add(name, number, field, value, f"Reference must exist in {parent}.{parent_field}",
                        f"Restore the referenced {parent} row or correct {field}.", "orphans")
                elif count > 1:
                    add(name, number, field, value, f"Reference to {parent}.{parent_field} is ambiguous",
                        "Resolve duplicate parent identifiers before using this reference.")
            if name == "vendor" and len(row.get("service_description") or "") > 200:
                add(name, number, "service_description", row["service_description"],
                    "Service description must be at most 200 characters",
                    "Shorten the description to 200 characters or fewer.")
            if name == "assessment" and not re.fullmatch(r"[1-9][0-9]*", row.get("version_no") or ""):
                add(name, number, "version_no", row.get("version_no"),
                    "Assessment version must be a positive integer",
                    "Use 1 for the first assessment, then increase by 1.")
            if name == "reviewer_audit_entry":
                timestamp = row.get("timestamp") or ""
                try:
                    if not re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}", timestamp):
                        raise ValueError
                    datetime.fromisoformat(timestamp)
                except ValueError:
                    add(name, number, "timestamp", timestamp, "Timestamp must use ISO 8601 date and time",
                        "Supply a timestamp such as 2026-11-17T09:30:00+01:00.", "date_errors")

    def parent(name, value):
        return indexes[name].get((value,), {})

    def compare_dates(name, number, row, earlier, later, strict=False, reference_field=None):
        try:
            # Absent/invalid dates already have a dedicated field error.
            if not row.get(earlier) or not row.get(later):
                return
            first = load_report_date(row[earlier])
            second = load_report_date(row[later])
        except ValueError:
            return
        if first > second or (strict and first == second):
            relationship = "after" if strict else "on or after"
            field = reference_field or later
            correction = (f"Correct {field} or the linked assessment's {later} ({row[later]}); "
                          f"check {earlier} ({row[earlier]})." if reference_field else
                          f"Check {earlier} ({row[earlier]}) and correct {later}.")
            add(name, number, field, row.get(field), f"{later} must be {relationship} {earlier}",
                correction, "date_errors")

    def same_vendor(name, number, field, row, assessment):
        if assessment and row.get("vendor_id") != assessment.get("vendor_id"):
            add(name, number, field, row.get(field), "Linked assessment must belong to the same vendor",
                "Use an assessment for this vendor or correct the vendor identifier.")

    for number, row in records("vendor"):
        same_vendor("vendor", number, "current_assessment_id", row,
                    parent("assessment", row.get("current_assessment_id")))
    for number, row in records("assessment"):
        predecessor = parent("assessment", row.get("supersedes_id"))
        same_vendor("assessment", number, "supersedes_id", row, predecessor)
        version = row.get("version_no") or ""
        if re.fullmatch(r"[1-9][0-9]*", version):
            if int(version) > 1:
                required("assessment", number, row, "supersedes_id",
                         "Assessment versions after 1 must reference their predecessor")
            if predecessor:
                previous_version = predecessor.get("version_no") or ""
                if previous_version.isascii() and previous_version.isdigit():
                    if int(previous_version) + 1 != int(version):
                        add("assessment", number, "version_no", version,
                            "Version must immediately follow the superseded assessment version",
                            "Correct the version or link to its immediate predecessor.")
                dates = {"previous_date": predecessor.get("assessment_date"),
                         "assessment_date": row.get("assessment_date")}
                compare_dates("assessment", number, dates, "previous_date", "assessment_date", strict=True)
    for number, row in records("change_event"):
        reassessment = parent("assessment", row.get("reassessment_assessment_id"))
        same_vendor("change_event", number, "reassessment_assessment_id", row, reassessment)
        compare_dates("change_event", number,
                      {**row, "assessment_date": reassessment.get("assessment_date")},
                      "change_date", "assessment_date", reference_field="reassessment_assessment_id")
    for number, row in records("corrective_action"):
        finding = parent("finding", row.get("finding_id"))
        same_vendor("corrective_action", number, "finding_id", row,
                    parent("assessment", finding.get("assessment_id")))
        if row.get("status") == "Closed":
            required("corrective_action", number, row, "closed_date",
                     "Closed actions must include a closed date")
        # No creation date exists. Closing before a due date is valid early completion.
    for number, row in records("decision"):
        if row.get("outcome") == "Conditionally Approved":
            for field in ("conditions", "condition_deadline"):
                required("decision", number, row, field,
                         "Conditional approval must include conditions and their deadline")
            compare_dates("decision", number, row, "decision_date", "condition_deadline")
            compare_dates("decision", number, row, "review_date", "condition_deadline")
        compare_dates("decision", number, row, "decision_date", "review_date")
        compare_dates("decision", number, row, "decision_date", "expiry_date", strict=True)
        compare_dates("decision", number, row, "review_date", "expiry_date")

    options = {}
    for number, row in records("question"):
        labels = []
        for option in (row.get("response_options") or "").split(" | "):
            parts = option.rsplit(" = ", 1)
            if len(parts) != 2 or not parts[0].strip() or parts[1] not in ("0", "1", "2", "3", "4"):
                add("question", number, "response_options", option,
                    "Options must use label = value, separated by ' | ', with values 0 to 4",
                    "Restore the canonical question options from the approved question bank.")
            else:
                labels.append(parts[0])
        if len(labels) != len(set(labels)):
            add("question", number, "response_options", row.get("response_options"),
                "Option labels must be unique within a question",
                "Give each answer choice a distinct approved label.")
        if key_counts["question"].get((row.get("question_id"),)) == 1:
            options[row.get("question_id")] = set(labels)

    for number, row in records("response"):
        choices = options.get(row.get("question_id"))
        for field in ("vendor_claim", "verified_answer"):
            value = row.get(field)
            if choices is not None and value and value not in choices:
                if field == "vendor_claim" and value == "Blank":
                    continue
                add("response", number, field, value,
                    "Answer must use an option label from the referenced question",
                    "Use one of: " + ", ".join(sorted(choices)) +
                    ("; or Blank for an unanswered vendor claim." if field == "vendor_claim" else "."))
        if row.get("reviewer_verified") == "Yes":
            required("response", number, row, "verified_answer",
                     "Reviewer-verified responses must include a verified answer")

    response_pairs = key_counts["response"]
    for number, row in records("evidence_item"):
        pair = (row.get("assessment_id"), row.get("question_id"))
        if all(pair) and pair not in response_pairs:
            add("evidence_item", number, "assessment_id, question_id", " | ".join(pair),
                "Evidence must reference an existing assessment-question response combination",
                "Restore the response row for this pair or correct the evidence references.", "orphans")
        status = row.get("status")
        fields = []
        if status in ("Received", "Accepted", "Rejected", "Expired"):
            fields += ["received_date", "reference_path"]
        if status in ("Accepted", "Expired"):
            fields += ["review_period_end", "expiry_date", "reviewer_role"]
        if status == "Rejected":
            fields += ["reviewer_role", "reason"]
        for field in fields:
            required("evidence_item", number, row, field,
                     f"{status} evidence must include {field}")
        compare_dates("evidence_item", number, row, "received_date", "expiry_date")

    for number, row in records("reviewer_audit_entry"):
        target = row.get("table_name")
        record_id = row.get("record_id")
        if target in SCHEMAS and record_id:
            if len(SCHEMAS[target].primary_key) != 1:
                add("reviewer_audit_entry", number, "record_id", record_id,
                    "Baseline audit record_id cannot identify a composite-key target",
                    "Resolve the audit reference representation with the schema owner; do not guess a key.")
            elif (record_id,) not in key_counts[target]:
                add("reviewer_audit_entry", number, "record_id", record_id,
                    f"Audit record must exist in {target}",
                    "Restore the referenced record or correct table_name and record_id.", "orphans")
    summary = {"files_loaded": sum(t.loaded for t in data.values()),
               "source_tables": len(SOURCE_TABLES),
               "valid_tables": sum(t.loaded and not any(
                   i.severity == "ERROR" and i.file == str(t.path) for i in issues
               ) for t in data.values()),
               "errors": sum(i.severity == "ERROR" for i in issues),
               "warnings": sum(i.severity == "WARNING" for i in issues)}
    for category in ("duplicates", "orphans", "missing_fields", "invalid_values", "date_errors", "files"):
        summary[category] = sum(i.severity == "ERROR" and i.category == category for i in issues)
    # Counts below are distinct affected rows, rather than counts of rule violations.
    summary["duplicate_records"] = len({(i.file, i.row) for i in issues if i.category == "duplicates"})
    summary["orphan_records"] = len({(i.file, i.row) for i in issues if i.category == "orphans"})
    return ValidationResult(issues, summary)
