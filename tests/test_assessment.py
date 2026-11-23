
import sys
import unittest

sys.path.insert(0, "..")

from src.assessment import (
    validate_assessment_id,
    validate_vendor_id,
    validate_assessment_record,
)


class TestAssessmentValidation(unittest.TestCase):

    def setUp(self):
        self.valid_assessment = {
            "assessment_id": "ASMT-001",
            "vendor_id": "VEN-001",
            "version_no": 1,
            "assessment_date": "2026-05-18",
            "trigger": "Initial",
            "assessor_role": "GRC Analyst",
            "status": "Draft",
            "supersedes_id": "",
        }

    def test_valid_assessment_id(self):
        self.assertTrue(validate_assessment_id("ASMT-001"))

    def test_invalid_assessment_id(self):
        self.assertFalse(validate_assessment_id("ASMT-1"))

    def test_valid_vendor_id(self):
        self.assertTrue(validate_vendor_id("VEN-001"))

    def test_invalid_vendor_id(self):
        self.assertFalse(validate_vendor_id("VEN-1"))

    def test_valid_assessment_record(self):
        errors = validate_assessment_record(self.valid_assessment)
        self.assertEqual(errors, [])

    def test_invalid_assessment_id_in_record(self):
        assessment = self.valid_assessment.copy()
        assessment["assessment_id"] = "BAD-001"

        errors = validate_assessment_record(assessment)

        self.assertTrue(any("assessment_id" in error for error in errors))

    def test_invalid_vendor_id_in_record(self):
        assessment = self.valid_assessment.copy()
        assessment["vendor_id"] = "BAD-001"

        errors = validate_assessment_record(assessment)

        self.assertTrue(any("vendor_id" in error for error in errors))

    def test_version_number_must_be_integer(self):
        assessment = self.valid_assessment.copy()
        assessment["version_no"] = "1"

        errors = validate_assessment_record(assessment)

        self.assertTrue(any("version_no" in error for error in errors))

    def test_version_number_must_be_positive(self):
        assessment = self.valid_assessment.copy()
        assessment["version_no"] = 0

        errors = validate_assessment_record(assessment)

        self.assertTrue(any("at least 1" in error for error in errors))

    def test_boolean_is_not_valid_version_number(self):
        assessment = self.valid_assessment.copy()
        assessment["version_no"] = True

        errors = validate_assessment_record(assessment)

        self.assertTrue(any("version_no" in error for error in errors))

    def test_invalid_assessment_date(self):
        assessment = self.valid_assessment.copy()
        assessment["assessment_date"] = "18-05-2026"

        errors = validate_assessment_record(assessment)

        self.assertTrue(any("assessment_date" in error for error in errors))

    def test_missing_assessment_date(self):
        assessment = self.valid_assessment.copy()
        assessment["assessment_date"] = ""

        errors = validate_assessment_record(assessment)

        self.assertTrue(any("assessment_date is required" in error for error in errors))

    def test_invalid_trigger(self):
        assessment = self.valid_assessment.copy()
        assessment["trigger"] = "Emergency"

        errors = validate_assessment_record(assessment)

        self.assertTrue(any("trigger" in error for error in errors))

    def test_invalid_status(self):
        assessment = self.valid_assessment.copy()
        assessment["status"] = "Approved"

        errors = validate_assessment_record(assessment)

        self.assertTrue(any("status" in error for error in errors))

    def test_missing_assessor_role(self):
        assessment = self.valid_assessment.copy()
        assessment["assessor_role"] = ""

        errors = validate_assessment_record(assessment)

        self.assertTrue(any("assessor_role" in error for error in errors))

    def test_invalid_supersedes_id(self):
        assessment = self.valid_assessment.copy()
        assessment["supersedes_id"] = "OLD-001"

        errors = validate_assessment_record(assessment)

        self.assertTrue(any("supersedes_id" in error for error in errors))

    def test_valid_supersedes_id(self):
        assessment = self.valid_assessment.copy()
        assessment["version_no"] = 2
        assessment["supersedes_id"] = "ASMT-001"

        errors = validate_assessment_record(assessment)

        self.assertEqual(errors, [])

    def test_non_dictionary_assessment(self):
        errors = validate_assessment_record("not a dictionary")

        self.assertEqual(
            errors,
            ["Assessment record must be a dictionary."]
        )


if __name__ == "__main__":
    unittest.main()
