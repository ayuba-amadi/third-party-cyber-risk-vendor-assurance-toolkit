
import unittest

from src.response import (
    validate_response_assessment_id,
    validate_response_question_id,
    validate_response_record,
)


class TestResponseValidation(unittest.TestCase):

    def setUp(self):
        self.valid_response = {
            "assessment_id": "ASMT-001",
            "question_id": "AM-01",
            "vendor_claim": "All privileged accounts are reviewed.",
            "reviewer_verified": "Yes",
            "verified_answer": "All privileged accounts are reviewed.",
            "reviewer_note": "Evidence reviewed.",
        }

    def test_valid_assessment_id(self):
        self.assertTrue(validate_response_assessment_id("ASMT-001"))

    def test_invalid_assessment_id(self):
        self.assertFalse(validate_response_assessment_id("ASMT-1"))

    def test_valid_question_id(self):
        self.assertTrue(validate_response_question_id("AM-01"))

    def test_invalid_question_id(self):
        self.assertFalse(validate_response_question_id("XX-01"))

    def test_valid_response_record(self):
        self.assertEqual(
            validate_response_record(self.valid_response),
            []
        )

    def test_non_dictionary_response(self):
        errors = validate_response_record("invalid")
        self.assertIn(
            "Response record must be a dictionary.",
            errors
        )

    def test_missing_vendor_claim(self):
        response = self.valid_response.copy()
        response["vendor_claim"] = ""

        errors = validate_response_record(response)

        self.assertIn("vendor_claim is required.", errors)

    def test_missing_reviewer_verified(self):
        response = self.valid_response.copy()
        response["reviewer_verified"] = ""

        errors = validate_response_record(response)

        self.assertIn("reviewer_verified is required.", errors)

    def test_invalid_reviewer_verified(self):
        response = self.valid_response.copy()
        response["reviewer_verified"] = "Maybe"

        errors = validate_response_record(response)

        self.assertTrue(
            any("Invalid reviewer_verified value" in error for error in errors)
        )

    def test_verified_answer_required_when_yes(self):
        response = self.valid_response.copy()
        response["verified_answer"] = ""

        errors = validate_response_record(response)

        self.assertIn(
            "verified_answer is required when reviewer_verified is Yes.",
            errors
        )

    def test_verified_answer_allowed_when_yes(self):
        response = self.valid_response.copy()

        errors = validate_response_record(response)

        self.assertEqual(errors, [])

    def test_verified_answer_optional_when_no(self):
        response = self.valid_response.copy()
        response["reviewer_verified"] = "No"
        response["verified_answer"] = ""

        errors = validate_response_record(response)

        self.assertEqual(errors, [])

    def test_verified_answer_optional_when_not_reviewed(self):
        response = self.valid_response.copy()
        response["reviewer_verified"] = "Not reviewed"
        response["verified_answer"] = ""

        errors = validate_response_record(response)

        self.assertEqual(errors, [])

    def test_invalid_assessment_id_in_record(self):
        response = self.valid_response.copy()
        response["assessment_id"] = "INVALID"

        errors = validate_response_record(response)

        self.assertTrue(
            any("Invalid assessment_id format" in error for error in errors)
        )

    def test_invalid_question_id_in_record(self):
        response = self.valid_response.copy()
        response["question_id"] = "XX-01"

        errors = validate_response_record(response)

        self.assertTrue(
            any("Invalid question_id format" in error for error in errors)
        )


if __name__ == "__main__":
    unittest.main()
