"""Reproducible defaults and dictionary enumerations; no scoring rules."""

from datetime import date
from pathlib import Path

APPLICATION_NAME = "Third-Party Cyber Risk Vendor Assurance Toolkit"
APPLICATION_VERSION = "0.1.0"
REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = REPOSITORY_ROOT / "sample-data"
DEFAULT_REPORTS_DIR = REPOSITORY_ROOT / "reports" / "phase1"
DEFAULT_PHASE2_REPORTS_DIR = REPOSITORY_ROOT / "reports" / "phase2"
DEFAULT_REPORT_DATE = date(2026, 11, 18)
DATE_FORMAT = "%Y-%m-%d"
SOURCE_TABLES = (
    "vendor", "business_service", "vendor_service_link", "assessment",
    "question", "response", "evidence_item", "finding", "corrective_action",
    "decision", "change_event", "reviewer_audit_entry",
)
CRITICALITY_SNAPSHOT_TABLE = "assessment_criticality_snapshot"
PHASE2_SOURCE_TABLES = SOURCE_TABLES + (CRITICALITY_SNAPSHOT_TABLE,)
EXPECTED_OUTPUT_FILES = (
    "expected_criticality.csv", "expected_domain_completeness.csv",
    "expected_management.csv", "expected_question_scores.csv", "expected_risk.csv",
)
NEGATIVE_TEST_FILES = ("invalid_vendor_cases.csv", "invalid_evidence_cases.csv")
REFERENCE_FILES = ("validation_results.txt",)

YES_NO = ("Yes", "No")
ALLOWED_VALUES = {
    ("vendor", "category"): (
        "Cloud hosting", "Payroll", "Payment processing", "Technical support",
        "Collaboration SaaS",
    ),
    ("vendor", "data_sensitivity"): ("None", "Internal", "Confidential", "Regulated"),
    ("vendor", "system_access"): ("None", "Standard", "Privileged"),
    ("vendor", "dependency_impact"): ("1", "2", "3", "4"),
    ("vendor", "replaceability"): ("Easy", "Moderate", "Hard", "Very hard"),
    ("assessment_criticality_snapshot", "data_sensitivity"): ("None", "Internal", "Confidential", "Regulated"),
    ("assessment_criticality_snapshot", "system_access"): ("None", "Standard", "Privileged"),
    ("assessment_criticality_snapshot", "dependency_impact"): ("1", "2", "3", "4"),
    ("assessment_criticality_snapshot", "replaceability"): ("Easy", "Moderate", "Hard", "Very hard"),
    ("vendor", "subcontractor_use"): YES_NO + ("Unknown",),
    ("vendor", "assessment_status"): (
        "Not started", "In progress", "Assessed", "Reassessment due",
    ),
    ("vendor", "material_change_flag"): YES_NO,
    ("business_service", "service_tier"): ("Business-critical", "Important", "Standard"),
    ("assessment", "trigger"): ("Initial", "Periodic", "Material change", "Expiry"),
    ("assessment", "status"): ("Draft", "Submitted", "Superseded"),
    ("question", "weight"): ("1", "2", "3", "4", "5"),
    ("question", "domain"): (
        "Access management", "Data protection", "Incident notification",
        "Continuity and recovery", "Subcontractors", "Governance",
    ),
    ("question", "evidence_required"): YES_NO,
    ("question", "critical_failure_flag"): YES_NO,
    ("response", "reviewer_verified"): YES_NO + ("Not reviewed",),
    ("evidence_item", "status"): ("Missing", "Received", "Accepted", "Rejected", "Expired"),
    ("finding", "severity"): ("Low", "Medium", "High", "Critical"),
    ("finding", "status"): ("Open", "Remediating", "Closed", "Risk accepted"),
    ("corrective_action", "status"): ("Open", "In progress", "Closed"),
    ("decision", "outcome"): ("Approved", "Conditionally Approved", "Rejected"),
    ("change_event", "material"): YES_NO,
    ("change_event", "change_type"): (
        "New subcontractor", "Scope increase", "Access increase", "Data type added",
        "Ownership change", "Other",
    ),
    ("reviewer_audit_entry", "action"): (
        "Created", "Edited", "Verified", "Rejected", "Decided", "Closed",
    ),
    ("reviewer_audit_entry", "table_name"): SOURCE_TABLES,
}

PHASE_NOTICE = (
    "The Phase 1 validate command checks CSV structure and relationships only. "
    "It does not calculate criticality or run risk scoring, decisions, remediation, "
    "management reporting or the Streamlit interface."
)
PHASE2_NOTICE = (
    "Phase 2 implements semantic validation and vendor criticality calculation only. "
    "Risk scoring, evidence scoring, decision workflow, remediation workflow, "
    "management reporting and the Streamlit interface are later-phase work."
)
