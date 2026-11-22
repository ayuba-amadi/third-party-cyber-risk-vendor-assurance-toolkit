
import re
from src.validation import is_blank, is_valid_date

def validate_evidence_id(evidence_id):
    """
    Validate the evidence ID format.

    Expected format: EV-001
    """
    if not isinstance(evidence_id, str):
        return False

    pattern = r"^EV-\d{3}$"

    return re.fullmatch(pattern, evidence_id) is not None

def validate_assessment_id(assessment_id):
    """
    Validate the assessment ID format.

    Expected format: ASMT-001
    """
    if not isinstance(assessment_id, str):
        return False

    pattern = r"^ASMT-\d{3}$"

    return re.fullmatch(pattern, assessment_id) is not None

def validate_question_id(question_id):
    """
    Validate the question ID format.

    Expected format: AM-01, DP-02, IN-03, BC-04, SC-01, GV-02.
    """
    if not isinstance(question_id, str):
        return False

    pattern = r"^(AM|DP|IN|BC|SC|GV)-\d{2}$"

    return re.fullmatch(pattern, question_id) is not None

VALID_EVIDENCE_STATUSES = {
    "Missing",
    "Received",
    "Accepted",
    "Rejected",
    "Expired"
}


def validate_evidence_status(status):
    """
    Check whether an evidence status is recognised.
    """
    if not isinstance(status, str):
        return False

    return status.strip() in VALID_EVIDENCE_STATUSES


def validate_evidence_record(evidence):
    """
    Validate the basic structure and required fields
    of an evidence record.

    Returns a list of validation errors.
    """
    errors = []

    if not isinstance(evidence, dict):
        return ["Evidence record must be a dictionary."]

    # Validate identifiers
    if not validate_evidence_id(evidence.get("evidence_id")):
        errors.append("Invalid evidence_id format.")

    if not validate_assessment_id(evidence.get("assessment_id")):
        errors.append("Invalid assessment_id format.")

    if not validate_question_id(evidence.get("question_id")):
        errors.append("Invalid question_id format.")

    # Define required fields for each evidence status
    required_fields = {
        "Missing": [],
        "Received": ["received_date", "reference_path"],
        "Accepted": [
            "received_date",
            "review_period_end",
            "expiry_date",
            "reviewer_role"
        ],
        "Rejected": [
            "received_date",
            "reviewer_role",
            "reason"
        ],
        "Expired": [
            "received_date",
            "review_period_end",
            "expiry_date",
            "reviewer_role"
        ]
    }

    # Validate evidence status
    status = evidence.get("status")

    if not validate_evidence_status(status):
        errors.append("Invalid evidence status.")
    else:
        for field in required_fields[status]:
            if is_blank(evidence.get(field)):
                errors.append(
                    f"{field} is required for {status} evidence."
                )

    # Validate dates independently of evidence status
    date_fields = [
        "received_date",
        "review_period_end",
        "expiry_date"
    ]

    for field in date_fields:
        value = evidence.get(field)

        if not is_blank(value) and not is_valid_date(value):
            errors.append(
                f"{field} must use a valid YYYY-MM-DD date."
            )

    return errors
