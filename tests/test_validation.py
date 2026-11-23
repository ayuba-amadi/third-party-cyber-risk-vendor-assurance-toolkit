
import sys
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from validation import (
    validate_vendor_id,
    find_duplicate_vendor_ids,
    validate_vendor_fields
)


class TestVendorIdValidation(unittest.TestCase):

    def test_valid_vendor_id(self):
        self.assertTrue(validate_vendor_id("VEN-001"))
        self.assertTrue(validate_vendor_id("VEN-025"))

    def test_invalid_vendor_id(self):
        self.assertFalse(validate_vendor_id("VEN-1"))
        self.assertFalse(validate_vendor_id("VEN-ABC"))
        self.assertFalse(validate_vendor_id("VENDOR-001"))
        self.assertFalse(validate_vendor_id("VEN-001\n"))


class TestDuplicateVendorIds(unittest.TestCase):

    def test_no_duplicates(self):
        vendor_ids = ["VEN-001", "VEN-002", "VEN-003"]

        result = find_duplicate_vendor_ids(vendor_ids)

        self.assertEqual(result, [])

    def test_duplicate_vendor_id(self):
        vendor_ids = [
            "VEN-001",
            "VEN-002",
            "VEN-001",
            "VEN-003"
        ]

        result = find_duplicate_vendor_ids(vendor_ids)

        self.assertEqual(
            result,
            [{
                "vendor_id": "VEN-001",
                "first_row": 1,
                "duplicate_row": 3
            }]
        )


class TestVendorFieldValidation(unittest.TestCase):

    def setUp(self):

        self.valid_vendor = {
            "vendor_id": "VEN-001",
            "vendor_name": "NimbusCloud Hosting",
            "category": "Cloud hosting",
            "service_description": "Hosts customer portal and ERP",
            "business_owner": "Head of IT Operations",
            "data_sensitivity": "Regulated",
            "data_types": "customer;payment",
            "system_access": "Privileged",
            "dependency_impact": 4,
            "replaceability": "Very hard",
            "subcontractor_use": "Yes",
            "assessment_status": "Assessed",
            "current_assessment_id": "ASMT-001",
            "next_review_date": "2027-05-18",
            "material_change_flag": "No"
        }

    def test_valid_vendor_fields(self):
        result = validate_vendor_fields(self.valid_vendor)

        self.assertEqual(result, [])

    def test_missing_required_field(self):
        vendor = self.valid_vendor.copy()
        vendor["vendor_name"] = ""

        result = validate_vendor_fields(vendor)

        self.assertIn("vendor_name is required", result)

    def test_invalid_category(self):
        vendor = self.valid_vendor.copy()
        vendor["category"] = "Unknown"

        result = validate_vendor_fields(vendor)

        self.assertTrue(
            any("category must be one of" in error for error in result)
        )

    def test_invalid_dependency_impact(self):
        vendor = self.valid_vendor.copy()
        vendor["dependency_impact"] = 8

        result = validate_vendor_fields(vendor)

        self.assertIn(
            "dependency_impact must be between 1 and 4",
            result
        )

    def test_decimal_dependency_impact(self):
        vendor = self.valid_vendor.copy()
        vendor["dependency_impact"] = 3.5

        result = validate_vendor_fields(vendor)

        self.assertIn(
            "dependency_impact must be a whole number",
            result
        )

    def test_invalid_subcontractor_use(self):
        vendor = self.valid_vendor.copy()
        vendor["subcontractor_use"] = "Maybe"

        result = validate_vendor_fields(vendor)

        self.assertIn(
            "subcontractor_use must be Yes, No or Unknown",
            result
        )

    def test_invalid_assessment_status(self):
        vendor = self.valid_vendor.copy()
        vendor["assessment_status"] = "Completed"

        result = validate_vendor_fields(vendor)

        self.assertIn(
            "assessment_status is not an approved option",
            result
        )

    def test_invalid_review_date(self):
        vendor = self.valid_vendor.copy()
        vendor["next_review_date"] = "31-12-2027"

        result = validate_vendor_fields(vendor)

        self.assertIn(
            "next_review_date must be a valid YYYY-MM-DD date",
            result
        )

    def test_invalid_material_change_flag(self):
        vendor = self.valid_vendor.copy()
        vendor["material_change_flag"] = "Maybe"

        result = validate_vendor_fields(vendor)

        self.assertIn(
            "material_change_flag must be Yes or No",
            result
        )

    def test_long_service_description(self):
        vendor = self.valid_vendor.copy()
        vendor["service_description"] = "A" * 201

        result = validate_vendor_fields(vendor)

        self.assertIn(
            "service_description must not exceed 200 characters",
            result
        )

    def test_invalid_assessment_id_format(self):
        vendor = self.valid_vendor.copy()
        vendor["current_assessment_id"] = "ASSESSMENT-001"

        result = validate_vendor_fields(vendor)

        self.assertIn(
            "current_assessment_id must follow the ASMT-### format",
            result
        )

    def test_optional_fields_can_be_blank(self):
        vendor = self.valid_vendor.copy()
        vendor["data_types"] = ""
        vendor["current_assessment_id"] = ""

        result = validate_vendor_fields(vendor)

        self.assertEqual(result, [])

    def test_unknown_field_is_rejected(self):
        vendor = self.valid_vendor.copy()
        vendor["unapproved_field"] = "Example"

        result = validate_vendor_fields(vendor)

        self.assertIn(
            "unapproved_field is not a documented vendor field",
            result
        )


if __name__ == "__main__":
    unittest.main()
