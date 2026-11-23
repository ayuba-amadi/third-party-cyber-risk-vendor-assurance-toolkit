
import re

from src.validation import is_blank


VALID_REVIEW_STATUSES = {
    "Yes",
    "No",
    "Not reviewed",
}


def validate_response_assessment_id(assessment_id):
    """Check ASMT-### format."""
    if not isinstance(assessment_id, str):
        return False

    return bool(
        re.fullmatch(r"ASMT-\d{3}", assessment_id.strip())
    )


def validate_response_question_id(question_id):
    """Check question ID format, such as AM-01 or DP-12."""
    if not isinstance(question_id, str):
        return False

    return bool(
        re.fullmatch(
            r"(AM|DP|IN|BC|SC|GV)-\d{2}",
            question_id.strip()
        )
    )


def validate_response_record(response):
    """
    Validate one response record against the Data Dictionary.

    Returns a list of validation errors.
    An empty list means the record passed field-level checks.
    """

    if not isinstance(response, dict):
        return ["Response record must be a dictionary."]

    errors = []

    # Validate assessment ID
    assessment_id = response.get("assessment_id")

    if not validate_response_assessment_id(assessment_id):
        errors.append(
            "Invalid assessment_id format. Expected ASMT-###."
        )

    # Validate question ID
    question_id = response.get("question_id")

    if not validate_response_question_id(question_id):
        errors.append(
            "Invalid question_id format. Expected a valid domain code "
            "followed by a two-digit number."
        )

    # Validate vendor claim
    vendor_claim = response.get("vendor_claim")

    if is_blank(vendor_claim):
        errors.append("vendor_claim is required.")

    # Validate reviewer verification status
    reviewer_verified = response.get("reviewer_verified")

    if is_blank(reviewer_verified):
        errors.append("reviewer_verified is required.")
    elif reviewer_verified not in VALID_REVIEW_STATUSES:
        errors.append(
            "Invalid reviewer_verified value. Allowed values: "
            + ", ".join(sorted(VALID_REVIEW_STATUSES))
        )

    # Validate verified answer
    verified_answer = response.get("verified_answer")

    if reviewer_verified == "Yes" and is_blank(verified_answer):
        errors.append(
            "verified_answer is required when reviewer_verified is Yes."
        )

    return errors
