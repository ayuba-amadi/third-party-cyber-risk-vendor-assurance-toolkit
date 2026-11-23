
import sys
import unittest

sys.path.insert(0, "..")

from src.evidence import (
    validate_evidence_id,
    validate_assessment_id,
    validate_question_id,
    validate_evidence_status,
    validate_evidence_record
)


class TestEvidenceValidation(unittest.TestCase):

    def test_valid_evidence_id(self):
        self.assertTrue(validate_evidence_id("EV-001"))

    def test_invalid_evidence_id(self):
        self.assertFalse(validate_evidence_id("EV-1"))
        self.assertFalse(validate_evidence_id("EV-ABC"))

    def test_valid_assessment_id(self):
        self.assertTrue(validate_assessment_id("ASMT-001"))

    def test_invalid_assessment_id(self):
        self.assertFalse(validate_assessment_id("ASMT-1"))
        self.assertFalse(validate_assessment_id("ASMT-ABC"))

    def test_valid_question_id(self):
        self.assertTrue(validate_question_id("AM-01"))

    def test_invalid_question_id(self):
        self.assertFalse(validate_question_id("XX-01"))
        self.assertFalse(validate_question_id("AM-1"))

    def test_valid_evidence_status(self):
        self.assertTrue(validate_evidence_status("Missing"))
        self.assertTrue(validate_evidence_status("Received"))
        self.assertTrue(validate_evidence_status("Accepted"))
        self.assertTrue(validate_evidence_status("Rejected"))
        self.assertTrue(validate_evidence_status("Expired"))

    def test_invalid_evidence_status(self):
        self.assertFalse(validate_evidence_status("Pending"))

    def test_valid_received_evidence_record(self):
        evidence = {
            "evidence_id": "EV-001",
            "assessment_id": "ASMT-001",
            "question_id": "AM-01",
            "status": "Received",
            "received_date": "2026-11-21",
            "reference_path": "evidence/EV-001.pdf"
        }

        self.assertEqual(validate_evidence_record(evidence), [])

    def test_invalid_evidence_record(self):
        evidence = {
            "evidence_id": "EV-1",
            "assessment_id": "ASMT-ABC",
            "question_id": "XX-01",
            "status": "Pending",
            "received_date": "invalid-date"
        }

        errors = validate_evidence_record(evidence)

        self.assertEqual(len(errors), 5)

    def test_received_evidence_missing_required_fields(self):
        evidence = {
            "evidence_id": "EV-001",
            "assessment_id": "ASMT-001",
            "question_id": "AM-01",
            "status": "Received"
        }

        errors = validate_evidence_record(evidence)

        self.assertIn(
            "received_date is required for Received evidence.",
            errors
        )

        self.assertIn(
            "reference_path is required for Received evidence.",
            errors
        )

    def test_valid_missing_evidence_record(self):
        evidence = {
            "evidence_id": "EV-002",
            "assessment_id": "ASMT-001",
            "question_id": "DP-01",
            "status": "Missing"
        }

        self.assertEqual(validate_evidence_record(evidence), [])

    def test_valid_accepted_evidence_record(self):
        evidence = {
            "evidence_id": "EV-003",
            "assessment_id": "ASMT-001",
            "question_id": "IN-01",
            "status": "Accepted",
            "received_date": "2026-11-01",
            "review_period_end": "2026-10-31",
            "expiry_date": "2027-10-31",
            "reviewer_role": "IT Security Reviewer"
        }

        self.assertEqual(validate_evidence_record(evidence), [])

    def test_valid_rejected_evidence_record(self):
        evidence = {
            "evidence_id": "EV-004",
            "assessment_id": "ASMT-001",
            "question_id": "BC-01",
            "status": "Rejected",
            "received_date": "2026-11-01",
            "reviewer_role": "IT Security Reviewer",
            "reason": "Evidence does not meet acceptance criteria."
        }

        self.assertEqual(validate_evidence_record(evidence), [])

    def test_valid_expired_evidence_record(self):
        evidence = {
            "evidence_id": "EV-005",
            "assessment_id": "ASMT-001",
            "question_id": "SC-01",
            "status": "Expired",
            "received_date": "2025-01-01",
            "review_period_end": "2024-12-31",
            "expiry_date": "2025-12-31",
            "reviewer_role": "IT Security Reviewer"
        }

        self.assertEqual(validate_evidence_record(evidence), [])

    def test_accepted_evidence_missing_required_fields(self):
        evidence = {
            "evidence_id": "EV-006",
            "assessment_id": "ASMT-001",
            "question_id": "AM-01",
            "status": "Accepted"
        }

        errors = validate_evidence_record(evidence)

        self.assertEqual(len(errors), 4)

    def test_rejected_evidence_missing_required_fields(self):
        evidence = {
            "evidence_id": "EV-007",
            "assessment_id": "ASMT-001",
            "question_id": "DP-01",
            "status": "Rejected"
        }

        errors = validate_evidence_record(evidence)

        self.assertEqual(len(errors), 3)

    def test_expired_evidence_missing_required_fields(self):
        evidence = {
            "evidence_id": "EV-008",
            "assessment_id": "ASMT-001",
            "question_id": "SC-01",
            "status": "Expired"
        }

        errors = validate_evidence_record(evidence)

        self.assertEqual(len(errors), 4)


if __name__ == "__main__":
    unittest.main()
