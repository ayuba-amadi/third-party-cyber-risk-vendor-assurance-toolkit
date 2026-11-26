"""Session-local working tables and transactions backed by the CSV engines."""
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
import subprocess

from src.config import DEFAULT_DATA_DIR, DEFAULT_REPORT_DATE, REPOSITORY_ROOT
from src.criticality import FACTORS, calculate_criticality
from src.loader import load_report_date, load_source_tables
from src.management_reporting import management_summary
from src.operational_reports import collect_operations
from src.reassessment import compare_versions
from src.schema import PHASE2_SCHEMAS
from src.validation import validate_tables

SNAPSHOT_DRIFT = "Current assessment snapshot must equal the current vendor register value"


def source_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPOSITORY_ROOT, text=True,
            stderr=subprocess.DEVNULL, timeout=2,
        ).strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def row_key(table, row):
    return tuple(row.get(name) for name in PHASE2_SCHEMAS[table].primary_key)


def put(tables, table, values, *, replace=False):
    target = tables[table]
    row = {header: values.get(header, "") for header in target.headers}
    if replace:
        for index, old in enumerate(target.rows):
            if row_key(table, old) == row_key(table, row):
                target.rows[index] = row
                return
    target.rows.append(row)
    target.row_numbers.append(max(target.row_numbers, default=1) + 1)


def next_id(rows, key, prefix, width=3):
    highest = max((int(row[key].removeprefix(prefix)) for row in rows), default=0)
    return f"{prefix}{highest + 1:0{width}d}"


def audit(tables, table, record, action, role, note):
    put(tables, "reviewer_audit_entry", dict(
        audit_id=next_id(tables["reviewer_audit_entry"].rows, "audit_id", "AUD-", 4),
        timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"), actor_role=role,
        action=action, table_name=table, record_id=record, note=note,
    ))


@dataclass
class Workspace:
    source: dict
    tables: dict
    report_date: date = DEFAULT_REPORT_DATE
    vendor_id: str = "VEN-001"
    assessment_id: str = ""
    commit: str = ""
    validation: object = field(init=False)
    validated_at: str = ""
    operations: tuple | None = None
    decision_errors: dict = field(default_factory=dict)
    calculation_error: str = ""
    reports: dict = field(default_factory=dict)
    messages: list = field(default_factory=list)
    pending_decision: dict | None = None

    @classmethod
    def load(cls):
        source = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)
        workspace = cls(source, deepcopy(source), commit=source_commit())
        workspace.refresh()
        workspace.select_vendor(workspace.vendor_id)
        return workspace

    def rows(self, name):
        return self.tables[name].rows

    def select_vendor(self, vendor_id):
        self.vendor_id = vendor_id
        vendor = next((row for row in self.rows("vendor") if row["vendor_id"] == vendor_id), {})
        self.assessment_id = vendor.get("current_assessment_id", "")

    def set_report_date(self, value):
        if self.report_date != value:
            self.report_date = value
            self.refresh()

    def refresh(self):
        self.validation = validate_tables(self.tables, self.report_date)
        self.validated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.operations = None
        self.decision_errors.clear()
        self.calculation_error = ""
        self.reports.clear()
        self.pending_decision = None
        tolerated = {"Material changes must link to a reassessment", SNAPSHOT_DRIFT}
        if any(issue.severity == "ERROR" and issue.rule not in tolerated
               for issue in self.validation.issues):
            self.calculation_error = "Resolve the listed validation errors before using calculated results."
            return
        try:
            self.operations = collect_operations(self.tables, self.report_date,
                                                 decision_errors=self.decision_errors)
        except (KeyError, ValueError) as exc:
            self.calculation_error = str(exc)

    def check(self, candidate):
        existing = set(self.validation.issues)
        return [issue for issue in validate_tables(candidate, self.report_date).issues
                if issue.severity == "ERROR" and issue not in existing and issue.rule != SNAPSHOT_DRIFT]

    def save(self, candidate):
        issues = self.check(candidate)
        if not issues:
            self.tables = candidate
            self.refresh()
        return issues

    def criticality_preview(self, vendor):
        inputs = {name: vendor.get(name, "") for name, _, _ in FACTORS}
        return calculate_criticality("", vendor, self.rows("business_service"),
                                     self.rows("vendor_service_link"),
                                     dict(inputs, assessment_id="", vendor_id=vendor.get("vendor_id", "")))

    def vendor_candidate(self, record, *, replace=False):
        candidate = deepcopy(self.tables)
        put(candidate, "vendor", record, replace=replace)
        return candidate

    def draft_assessment(self, vendor, role):
        candidate = deepcopy(self.tables)
        aid = next_id(self.rows("assessment"), "assessment_id", "ASMT-")
        put(candidate, "assessment", dict(assessment_id=aid, vendor_id=vendor["vendor_id"],
            version_no="1", assessment_date=self.report_date.isoformat(), trigger="Initial",
            assessor_role=role, status="Draft"))
        put(candidate, "assessment_criticality_snapshot",
            dict(assessment_id=aid, vendor_id=vendor["vendor_id"], snapshot_source="Vendor register",
                 **{name: vendor[name] for name, _, _ in FACTORS}))
        put(candidate, "vendor", dict(vendor, current_assessment_id=aid, assessment_status="In progress"),
            replace=True)
        for question in self.rows("question"):
            put(candidate, "response", dict(assessment_id=aid, question_id=question["question_id"],
                                             vendor_claim="Blank", reviewer_verified="Not reviewed"))
        return candidate, aid

    def management(self):
        _, _, criticality, risk, decisions, actions = self.operations
        return management_summary(self.tables, criticality, risk, decisions, actions, self.report_date)

    def history(self, vid):
        vendors, assessments, criticality, risk, decisions, actions = self.operations
        return compare_versions(vendors[vid], assessments, criticality, risk, decisions,
                                self.rows("change_event"), self.report_date, actions)

    def changed_rows(self, name):
        original = {row_key(name, row): row for row in self.source[name].rows}
        return [row for row in self.rows(name) if original.get(row_key(name, row)) != row]
