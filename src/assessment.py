
import re

from src.validation import is_blank, is_valid_date


VALID_ASSESSMENT_TRIGGERS = {
    "Initial",
    "Periodic",
    "Material change",
    "Expiry",
}

VALID_ASSESSMENT_STATUSES = {
    "Draft",
    "Submitted",
    "Superseded",
}


def validate_assessment_id(assessment_id):
    """Check whether an assessment ID follows ASMT-### format."""
    if not isinstance(assessment_id, str):
        return False

    return bool(re.fullmatch(r"ASMT-\d{3}", assessment_id.strip()))


def validate_vendor_id(vendor_id):
    """Check whether a vendor ID follows VEN-### format."""
    if not isinstance(vendor_id, str):
        return False

    return bool(re.fullmatch(r"VEN-\d{3}", vendor_id.strip()))


def validate_assessment_record(assessment):
    """
    Validate one assessment record against the current Data Dictionary.

    Returns a list of validation errors.
    An empty list means the record passed these field-level checks.
    """
    if not isinstance(assessment, dict):
        return ["Assessment record must be a dictionary."]

    errors = []

    # Validate assessment ID
    if not validate_assessment_id(assessment.get("assessment_id")):
        errors.append("Invalid assessment_id format. Expected ASMT-###.")

    # Validate vendor ID
    if not validate_vendor_id(assessment.get("vendor_id")):
        errors.append("Invalid vendor_id format. Expected VEN-###.")

    # Validate version number
    version_no = assessment.get("version_no")

    if isinstance(version_no, bool) or not isinstance(version_no, int):
        errors.append("version_no must be an integer.")
    elif version_no < 1:
        errors.append("version_no must be at least 1.")

    # Validate assessment date
    assessment_date = assessment.get("assessment_date")

    if is_blank(assessment_date):
        errors.append("assessment_date is required.")
    elif not is_valid_date(assessment_date):
        errors.append("assessment_date must use a valid YYYY-MM-DD date.")

    # Validate trigger
    trigger = assessment.get("trigger")

    if is_blank(trigger):
        errors.append("trigger is required.")
    elif trigger not in VALID_ASSESSMENT_TRIGGERS:
        errors.append(
            "Invalid trigger. Allowed values: "
            + ", ".join(sorted(VALID_ASSESSMENT_TRIGGERS))
        )

    # Validate assessor role
    assessor_role = assessment.get("assessor_role")

    if is_blank(assessor_role):
        errors.append("assessor_role is required.")

    # Validate status
    status = assessment.get("status")

    if is_blank(status):
        errors.append("status is required.")
    elif status not in VALID_ASSESSMENT_STATUSES:
        errors.append(
            "Invalid status. Allowed values: "
            + ", ".join(sorted(VALID_ASSESSMENT_STATUSES))
        )

    # Validate optional supersedes ID
    supersedes_id = assessment.get("supersedes_id")

    if not is_blank(supersedes_id):
        if not validate_assessment_id(supersedes_id):
            errors.append(
                "Invalid supersedes_id format. Expected ASMT-###."
            )

    return errors
