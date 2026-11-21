
import re
from datetime import date


# --------------------------------------------------
# 1. APPROVED VALUES FROM THE RESEARCH DATA DICTIONARY
# --------------------------------------------------

ALLOWED_CATEGORIES = {
    "Cloud hosting",
    "Payroll",
    "Payment processing",
    "Technical support",
    "Collaboration SaaS"
}

ALLOWED_DATA_SENSITIVITY = {
    "None",
    "Internal",
    "Confidential",
    "Regulated"
}

ALLOWED_SYSTEM_ACCESS = {
    "None",
    "Standard",
    "Privileged"
}

ALLOWED_REPLACEABILITY = {
    "Easy",
    "Moderate",
    "Hard",
    "Very hard"
}

ALLOWED_SUBCONTRACTOR_USE = {
    "Yes",
    "No",
    "Unknown"
}

ALLOWED_ASSESSMENT_STATUS = {
    "Not started",
    "In progress",
    "Assessed",
    "Reassessment due"
}

ALLOWED_MATERIAL_CHANGE_FLAG = {
    "Yes",
    "No"
}


# --------------------------------------------------
# 2. VENDOR ID VALIDATION
# --------------------------------------------------

def validate_vendor_id(vendor_id):
    """
    Check whether a vendor ID follows the required format.

    Expected format: VEN-001, VEN-002, etc.
    """

    if not isinstance(vendor_id, str):
        return False

    return bool(re.fullmatch(r"VEN-\d{3}", vendor_id))


# --------------------------------------------------
# 3. DUPLICATE VENDOR ID DETECTION
# --------------------------------------------------

def find_duplicate_vendor_ids(vendor_ids):
    """
    Identify duplicate vendor IDs and their row numbers.

    The first occurrence is retained.
    Later occurrences are reported as duplicates.
    """

    seen = {}
    duplicates = []

    for row_number, vendor_id in enumerate(vendor_ids, start=1):

        if vendor_id in seen:
            duplicates.append({
                "vendor_id": vendor_id,
                "first_row": seen[vendor_id],
                "duplicate_row": row_number
            })

        else:
            seen[vendor_id] = row_number

    return duplicates


# --------------------------------------------------
# 4. HELPER FUNCTIONS
# --------------------------------------------------

def is_blank(value):
    """Check whether a value is missing or contains only whitespace."""

    return value is None or (
        isinstance(value, str) and value.strip() == ""
    )


def is_valid_date(value):
    """
    Check whether a date is valid and follows YYYY-MM-DD format.
    """

    if isinstance(value, date):
        return True

    if not isinstance(value, str):
        return False

    try:
        parsed_date = date.fromisoformat(value.strip())

        return parsed_date.isoformat() == value.strip()

    except ValueError:
        return False


# --------------------------------------------------
# 5. COMPLETE VENDOR FIELD VALIDATION
# --------------------------------------------------

def validate_vendor_fields(vendor):
    """
    Validate a vendor record against the Research data dictionary.

    The vendor record must contain the 15 documented fields.

    Returns a list of validation errors.
    An empty list means the record passed these checks.

    Foreign-key existence checks and onboarding-date comparisons
    are handled separately by the application.
    """

    errors = []

    if not isinstance(vendor, dict):
        return ["vendor record must be a dictionary"]

    # Required vendor fields
    required_fields = [
        "vendor_id",
        "vendor_name",
        "category",
        "service_description",
        "business_owner",
        "data_sensitivity",
        "system_access",
        "dependency_impact",
        "replaceability",
        "subcontractor_use",
        "assessment_status",
        "next_review_date",
        "material_change_flag"
    ]

    # Optional vendor fields
    optional_fields = [
        "data_types",
        "current_assessment_id"
    ]

    # Check required fields
    for field in required_fields:

        if field not in vendor or is_blank(vendor[field]):
            errors.append(f"{field} is required")

    # Check vendor ID format
    vendor_id = vendor.get("vendor_id")

    if not is_blank(vendor_id):
        if not validate_vendor_id(vendor_id):
            errors.append(
                "vendor_id must follow the VEN-### format"
            )

    # Check vendor name
    vendor_name = vendor.get("vendor_name")

    if not is_blank(vendor_name) and not isinstance(vendor_name, str):
        errors.append("vendor_name must be text")

    # Check category
    category = vendor.get("category")

    if not is_blank(category):
        if category not in ALLOWED_CATEGORIES:
            errors.append(
                f"category must be one of: {', '.join(sorted(ALLOWED_CATEGORIES))}"
            )

    # Check service description
    description = vendor.get("service_description")

    if not is_blank(description):

        if not isinstance(description, str):
            errors.append("service_description must be text")

        elif len(description.strip()) > 200:
            errors.append(
                "service_description must not exceed 200 characters"
            )

    # Check business owner
    business_owner = vendor.get("business_owner")

    if not is_blank(business_owner):
        if not isinstance(business_owner, str):
            errors.append("business_owner must be text")

    # Check data sensitivity
    sensitivity = vendor.get("data_sensitivity")

    if not is_blank(sensitivity):
        if sensitivity not in ALLOWED_DATA_SENSITIVITY:
            errors.append(
                f"data_sensitivity must be one of: "
                f"{', '.join(sorted(ALLOWED_DATA_SENSITIVITY))}"
            )

    # Check optional data types
    data_types = vendor.get("data_types")

    if not is_blank(data_types):
        if not isinstance(data_types, str):
            errors.append("data_types must be text")

    # Check system access
    system_access = vendor.get("system_access")

    if not is_blank(system_access):
        if system_access not in ALLOWED_SYSTEM_ACCESS:
            errors.append(
                f"system_access must be one of: "
                f"{', '.join(sorted(ALLOWED_SYSTEM_ACCESS))}"
            )

    # Check dependency impact
    impact_value = vendor.get("dependency_impact")

    if not is_blank(impact_value):

        if isinstance(impact_value, bool):
            errors.append(
                "dependency_impact must be a whole number"
            )

        elif isinstance(impact_value, int):
            if impact_value not in {1, 2, 3, 4}:
                errors.append(
                    "dependency_impact must be between 1 and 4"
                )

        elif isinstance(impact_value, str) and re.fullmatch(
            r"\d+", impact_value.strip()
        ):

            impact = int(impact_value.strip())

            if impact not in {1, 2, 3, 4}:
                errors.append(
                    "dependency_impact must be between 1 and 4"
                )

        else:
            errors.append(
                "dependency_impact must be a whole number"
            )

    # Check replaceability
    replaceability = vendor.get("replaceability")

    if not is_blank(replaceability):
        if replaceability not in ALLOWED_REPLACEABILITY:
            errors.append(
                f"replaceability must be one of: "
                f"{', '.join(sorted(ALLOWED_REPLACEABILITY))}"
            )

    # Check subcontractor use
    subcontractor_use = vendor.get("subcontractor_use")

    if not is_blank(subcontractor_use):
        if subcontractor_use not in ALLOWED_SUBCONTRACTOR_USE:
            errors.append(
                "subcontractor_use must be Yes, No or Unknown"
            )

    # Check assessment status
    assessment_status = vendor.get("assessment_status")

    if not is_blank(assessment_status):
        if assessment_status not in ALLOWED_ASSESSMENT_STATUS:
            errors.append(
                "assessment_status is not an approved option"
            )

    # Check optional assessment ID format
    assessment_id = vendor.get("current_assessment_id")

    if not is_blank(assessment_id):

        if not isinstance(assessment_id, str) or not re.fullmatch(
            r"ASMT-\d{3}", assessment_id
        ):
            errors.append(
                "current_assessment_id must follow the ASMT-### format"
            )

    # Check next review date
    review_date = vendor.get("next_review_date")

    if not is_blank(review_date):
        if not is_valid_date(review_date):
            errors.append(
                "next_review_date must be a valid YYYY-MM-DD date"
            )

    # Check material change flag
    material_change = vendor.get("material_change_flag")

    if not is_blank(material_change):
        if material_change not in ALLOWED_MATERIAL_CHANGE_FLAG:
            errors.append(
                "material_change_flag must be Yes or No"
            )

    # Ensure only documented fields are accepted as vendor columns
    documented_fields = set(required_fields + optional_fields)

    for field in vendor:
        if field not in documented_fields:
            errors.append(
                f"{field} is not a documented vendor field"
            )

    return errors
