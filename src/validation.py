"""Structural and cross-table validation of approved CSVs; never changes inputs."""

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime

from .config import ALLOWED_VALUES
from .loader import load_report_date
from .schema import IDENTIFIER_PATTERNS, PHASE2_SCHEMAS, SCHEMAS, ValidationIssue


@dataclass
class ValidationResult:
    issues: list[ValidationIssue]
    summary: dict
    overdue_actions: list[dict] = field(default_factory=list)

    @property
    def passed(self):
        return self.summary["errors"] == 0


def validate_tables(data, as_of_date=None):
    """Validate every raw row and retain all rows for inspection.

    Errors make a row unsuitable for later processing. No duplicate winner is
    selected. Joins always use identifiers. The optional report date is used only
    to classify open actions as overdue; overdue actions are not validation errors.
    """
    as_of_date = load_report_date(
        as_of_date.isoformat() if hasattr(as_of_date, "isoformat") else as_of_date
    )
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
    active_schemas = {name: schema for name, schema in PHASE2_SCHEMAS.items() if name in data}
    for name, schema in active_schemas.items():
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

    for name, schema in active_schemas.items():
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
        current = parent("assessment", row.get("current_assessment_id"))
        same_vendor("vendor", number, "current_assessment_id", row, current)
        if current and current.get("status") == "Superseded":
            add("vendor", number, "current_assessment_id", row.get("current_assessment_id"),
                "Current assessment must not be marked Superseded",
                "Point the vendor to its latest non-superseded assessment.")
    for number, row in records("assessment"):
        predecessor = parent("assessment", row.get("supersedes_id"))
        same_vendor("assessment", number, "supersedes_id", row, predecessor)
        version = row.get("version_no") or ""
        if re.fullmatch(r"[1-9][0-9]*", version):
            if int(version) > 1 and row.get("trigger") == "Initial":
                add("assessment", number, "trigger", row.get("trigger"),
                    "A reassessment must use a reassessment trigger",
                    "Use Periodic, Material change or Expiry for a version after 1.")
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
                if predecessor.get("status") != "Superseded":
                    add("assessment", number, "supersedes_id", row.get("supersedes_id"),
                        "A superseded assessment must have status Superseded",
                        "Mark the prior version Superseded while retaining its row.")
                dates = {"previous_date": predecessor.get("assessment_date"),
                         "assessment_date": row.get("assessment_date")}
                compare_dates("assessment", number, dates, "previous_date", "assessment_date", strict=True)
    for number, row in records("change_event"):
        reassessment = parent("assessment", row.get("reassessment_assessment_id"))
        if row.get("material") == "Yes" and not (row.get("reassessment_assessment_id") or "").strip():
            add("change_event", number, "reassessment_assessment_id", "",
                "Material changes must link to a reassessment",
                "Create and link the vendor's reassessment assessment_id.", "missing_fields")
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
        elif (row.get("closed_date") or "").strip():
            add("corrective_action", number, "closed_date", row.get("closed_date"),
                "Open or in-progress actions must not have a closed date",
                "Clear closed_date until the action status is Closed.")
        # No creation date exists. Closing before a due date is valid early completion.
    for number, row in records("decision"):
        assessment = parent("assessment", row.get("assessment_id"))
        if assessment and (row.get("decision_maker_role") or "").strip().casefold() == \
                (assessment.get("assessor_role") or "").strip().casefold():
            add("decision", number, "decision_maker_role", row.get("decision_maker_role"),
                "Decision-maker role must differ from the assessment assessor role",
                "Record an authorised decision-maker who is independent of the assessor.")
        if row.get("outcome") == "Rejected":
            required("decision", number, row, "justification",
                     "Rejected decisions must contain a justification")
        if row.get("outcome") == "Conditionally Approved":
            for field in ("conditions", "condition_deadline"):
                required("decision", number, row, field,
                         "Conditional approval must include conditions and their deadline")
            compare_dates("decision", number, row, "decision_date", "condition_deadline")
            compare_dates("decision", number, row, "review_date", "condition_deadline")
            assessment_id = row.get("assessment_id")
            related_findings = {f.get("finding_id") for _, f in records("finding")
                                if f.get("assessment_id") == assessment_id}
            related_actions = [a for _, a in records("corrective_action")
                               if a.get("finding_id") in related_findings]
            if not related_actions or not any((a.get("responsible_party") or "").strip()
                                              for a in related_actions):
                add("decision", number, "conditions", row.get("conditions"),
                    "Conditional approval requires a linked corrective action with a responsible party",
                    "Link a finding and corrective action for this assessment and assign its responsible_party.")
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

    # Questionnaire coverage is assessed against the complete approved question bank.
    question_ids = {row.get("question_id") for _, row in records("question") if row.get("question_id")}
    response_pairs = {(row.get("assessment_id"), row.get("question_id"))
                      for _, row in records("response")}
    for number, row in records("assessment"):
        missing_questions = sorted(qid for qid in question_ids
                                   if (row.get("assessment_id"), qid) not in response_pairs)
        if missing_questions:
            add("assessment", number, "questionnaire_coverage", ", ".join(missing_questions),
                f"Assessment must have one response for each of {len(question_ids)} approved questions",
                "Add the missing assessment-question response rows; retain unanswered claims as Blank.",
                "missing_fields")

    # An evidence item's immutable ID and audit trail make its recorded state reviewable.
    # Replacement evidence uses a distinct evidence_id and a retained assessment version.
    audit_events = {}
    for _, audit in records("reviewer_audit_entry"):
        if audit.get("table_name") == "evidence_item":
            audit_events.setdefault(audit.get("record_id"), set()).add(audit.get("action"))
    for number, row in records("evidence_item"):
        events = audit_events.get(row.get("evidence_id"), set())
        if "Created" not in events:
            add("evidence_item", number, "evidence_id", row.get("evidence_id"),
                "Evidence item must have a creation event in the audit table",
                "Append an audit record documenting the evidence item creation.", "orphans")
        if row.get("status") in ("Accepted", "Expired") and "Verified" not in events:
            add("evidence_item", number, "status", row.get("status"),
                "Accepted or expired evidence must retain its reviewer verification event",
                "Append a reviewer audit event before recording this reviewed evidence state.")
        if row.get("status") == "Rejected" and "Rejected" not in events:
            add("evidence_item", number, "status", row.get("status"),
                "Rejected evidence must retain its reviewer rejection event",
                "Append a reviewer audit event before recording this rejected evidence state.")
        contradictory = (
            row.get("status") in ("Missing", "Received") and bool(events & {"Verified", "Rejected"})
        ) or (
            row.get("status") in ("Accepted", "Expired") and "Rejected" in events
        ) or (
            row.get("status") == "Rejected" and "Verified" in events
        )
        if contradictory:
            add("evidence_item", number, "status", row.get("status"),
                "Current evidence status conflicts with its retained review audit history",
                "Preserve each review state with its audit record; use a new evidence_id for replacement evidence.")

    # Assessment snapshots are mandatory and intentionally independent of current
    # vendor fields so historical assessment factors cannot drift over time.
    if "assessment_criticality_snapshot" in data:
        snapshots = {row.get("assessment_id"): row for _, row in records("assessment_criticality_snapshot")
                     if row.get("assessment_id")}
        current_assessments = {row.get("current_assessment_id"): row for _, row in records("vendor")}
        for number, row in records("assessment"):
            snapshot = snapshots.get(row.get("assessment_id"))
            if not snapshot:
                add("assessment_criticality_snapshot", 0, "assessment_id", row.get("assessment_id"),
                    "Every assessment requires its own criticality factor snapshot",
                    "Add an explicit snapshot row for this assessment version.", "missing_fields")
                continue
            if snapshot.get("vendor_id") != row.get("vendor_id"):
                # The generic FK check catches missing vendors; this catches a valid but wrong vendor.
                snap_number = next((n for n, s in records("assessment_criticality_snapshot")
                                    if s.get("assessment_id") == row.get("assessment_id")), 0)
                add("assessment_criticality_snapshot", snap_number, "vendor_id", snapshot.get("vendor_id"),
                    "Snapshot vendor must match the linked assessment vendor",
                    "Use the vendor_id recorded on the referenced assessment.")
            vendor = current_assessments.get(row.get("assessment_id"))
            if vendor:
                for field in ("data_sensitivity", "system_access", "dependency_impact", "replaceability"):
                    if snapshot.get(field) != vendor.get(field):
                        snap_number = next((n for n, s in records("assessment_criticality_snapshot")
                                            if s.get("assessment_id") == row.get("assessment_id")), 0)
                        add("assessment_criticality_snapshot", snap_number, field, snapshot.get(field),
                            "Current assessment snapshot must equal the current vendor register value",
                            "Refresh this current snapshot from the vendor register; do not alter historical snapshots.")

    # A material-change assessment must be backed by a material event for the same
    # vendor and reassessment ID; an unrelated event is not a valid trigger.
    material_links = {(r.get("vendor_id"), r.get("reassessment_assessment_id"))
                      for _, r in records("change_event") if r.get("material") == "Yes"}
    for number, row in records("assessment"):
        if row.get("trigger") == "Material change" and \
                (row.get("vendor_id"), row.get("assessment_id")) not in material_links:
            add("assessment", number, "trigger", row.get("trigger"),
                "Material-change reassessment must link to a material change event for the same vendor",
                "Link a material change_event to this vendor and reassessment assessment_id.", "orphans")

    overdue_actions = []
    for _, action in records("corrective_action"):
        try:
            due = load_report_date(action.get("due_date"))
        except ValueError:
            continue
        if action.get("status") != "Closed" and due < as_of_date:
            overdue_actions.append({"action_id": action.get("action_id"),
                                    "finding_id": action.get("finding_id"),
                                    "vendor_id": action.get("vendor_id"),
                                    "due_date": action.get("due_date"),
                                    "status": action.get("status")})

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
               "source_tables": len(data),
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
    return ValidationResult(issues, summary, sorted(overdue_actions, key=lambda x: x["action_id"]))
