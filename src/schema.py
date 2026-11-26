"""The baseline dictionary expressed using the actual source CSV headers."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TableSchema:
    columns: tuple[str, ...]
    required_fields: tuple[str, ...]
    primary_key: tuple[str, ...]
    foreign_keys: tuple[tuple[str, str, str], ...] = ()
    date_fields: tuple[str, ...] = ()
    extra_unique_keys: tuple[tuple[str, ...], ...] = ()


def table(columns, optional, primary_key, foreign_keys=(), dates="", unique=()):
    """All columns must exist; only dictionary-required cells must be nonblank."""
    columns = tuple(columns.split())
    optional = optional.split()
    return TableSchema(
        columns, tuple(c for c in columns if c not in optional),
        tuple(primary_key.split()), foreign_keys, tuple(dates.split()), unique,
    )


SCHEMAS = {
    "vendor": table(
        "vendor_id vendor_name category service_description business_owner data_sensitivity "
        "data_types system_access dependency_impact replaceability subcontractor_use "
        "assessment_status current_assessment_id next_review_date material_change_flag",
        "data_types current_assessment_id", "vendor_id",
        (("current_assessment_id", "assessment", "assessment_id"),), "next_review_date",
    ),
    "business_service": table(
        "service_id service_name service_tier service_owner", "", "service_id",
    ),
    "vendor_service_link": table(
        "vendor_id service_id dependency_note", "dependency_note", "vendor_id service_id",
        (("vendor_id", "vendor", "vendor_id"), ("service_id", "business_service", "service_id")),
    ),
    "assessment": table(
        "assessment_id vendor_id version_no assessment_date trigger assessor_role status supersedes_id",
        "supersedes_id", "assessment_id",
        (("vendor_id", "vendor", "vendor_id"), ("supersedes_id", "assessment", "assessment_id")),
        "assessment_date", (("vendor_id", "version_no"),),
    ),
    "question": table(
        "question_id domain question_text response_options weight evidence_required "
        "evidence_description acceptance_criteria critical_failure_flag",
        "evidence_description acceptance_criteria", "question_id",
    ),
    "response": table(
        "assessment_id question_id vendor_claim reviewer_verified verified_answer reviewer_note",
        "verified_answer reviewer_note", "assessment_id question_id",
        (("assessment_id", "assessment", "assessment_id"), ("question_id", "question", "question_id")),
    ),
    "evidence_item": table(
        "evidence_id assessment_id question_id status received_date review_period_end "
        "expiry_date reviewer_role reference_path reason",
        "received_date review_period_end expiry_date reviewer_role reference_path reason", "evidence_id",
        (("assessment_id", "assessment", "assessment_id"), ("question_id", "question", "question_id")),
        "received_date review_period_end expiry_date",
        (("assessment_id", "question_id"),),
    ),
    "finding": table(
        "finding_id assessment_id question_id severity description status", "question_id", "finding_id",
        (("assessment_id", "assessment", "assessment_id"), ("question_id", "question", "question_id")),
    ),
    "corrective_action": table(
        "action_id finding_id vendor_id action_text responsible_party due_date status closed_date",
        "closed_date", "action_id",
        (("finding_id", "finding", "finding_id"), ("vendor_id", "vendor", "vendor_id")),
        "due_date closed_date",
    ),
    "decision": table(
        "decision_id assessment_id calculated_rating outcome decision_maker_role justification "
        "conditions condition_deadline decision_date expiry_date review_date",
        "conditions condition_deadline", "decision_id",
        (("assessment_id", "assessment", "assessment_id"),),
        "condition_deadline decision_date expiry_date review_date",
    ),
    "change_event": table(
        "change_id vendor_id change_date change_type material reassessment_assessment_id",
        "reassessment_assessment_id", "change_id",
        (("vendor_id", "vendor", "vendor_id"),
         ("reassessment_assessment_id", "assessment", "assessment_id")), "change_date",
    ),
    "reviewer_audit_entry": table(
        "audit_id timestamp actor_role action table_name record_id note", "note", "audit_id",
    ),
}

# The separate snapshot is a Phase 2 input. Keep the Phase 1 SCHEMAS mapping
# stable for existing callers that iterate its original 12 source tables.
PHASE2_SCHEMAS = {
    **SCHEMAS,
    "assessment_criticality_snapshot": table(
        "assessment_id vendor_id data_sensitivity system_access dependency_impact "
        "replaceability snapshot_source", "", "assessment_id",
        (("assessment_id", "assessment", "assessment_id"),
         ("vendor_id", "vendor", "vendor_id")),
    ),
}

IDENTIFIER_PATTERNS = {
    "vendor_id": r"VEN-[0-9]{3}", "service_id": r"SVC-[0-9]{2}",
    "assessment_id": r"ASMT-[0-9]{3}", "question_id": r"(?:AM|DP|IN|BC|SC|GV)-[0-9]{2}",
    "evidence_id": r"EV-[0-9]{3}", "finding_id": r"FND-[0-9]{3}",
    "action_id": r"ACT-[0-9]{3}", "decision_id": r"DEC-[0-9]{3}",
    "change_id": r"CHG-[0-9]{3}", "audit_id": r"AUD-[0-9]{4}",
}


@dataclass(frozen=True)
class ValidationIssue:
    file: str
    row: int
    field: str
    value: str
    rule: str
    severity: str
    correction: str
    category: str
