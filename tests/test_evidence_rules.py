import unittest
from datetime import date

from src.risk_scoring import score_question


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.question = dict(question_id="AM-01", response_options="All = 0 | Some = 3",
                             weight="5", evidence_required="Yes", critical_failure_flag="Yes")
        self.response = dict(vendor_claim="All", verified_answer="All", reviewer_verified="Yes")
        self.evidence = dict(status="Accepted", expiry_date="2026-11-18", reviewer_role="Reviewer")

    def score(self):
        return score_question(self.question, self.response, self.evidence, date(2026, 11, 18))

    def test_accepted_expiring_today_is_valid(self):
        self.assertTrue(self.score()["verified"])
        self.assertEqual(self.score()["risk_value"], 0)

    def test_expiry_before_report_date(self):
        self.evidence["expiry_date"] = "2026-11-17"
        result = self.score()
        self.assertEqual(result["effective_evidence_status"], "Expired")
        self.assertEqual(result["evidence_status"], "Accepted")
        self.assertFalse(result["verified"])

    def test_non_accepted_evidence_receives_worst_risk_even_with_yes(self):
        for state in ("Missing", "Received", "Rejected", "Expired"):
            self.evidence["status"] = state
            result = self.score()
            self.assertEqual(result["risk_value"], 4)
            self.assertFalse(result["verified"])
            self.assertTrue(result["unresolved_critical_question"])
            self.assertIn(state.upper() + " EVIDENCE", result["flags"])

    def test_blank_and_invalid_claims(self):
        self.response["vendor_claim"] = "Blank"
        self.assertIn("UNANSWERED", self.score()["flags"])
        self.response["vendor_claim"] = "Unknown"
        with self.assertRaisesRegex(ValueError, "vendor_claim"):
            self.score()

    def test_better_answer_requires_note(self):
        self.response["vendor_claim"] = "Some"
        with self.assertRaisesRegex(ValueError, "reviewer note"):
            self.score()
        self.response["reviewer_note"] = "Reviewer checked every account."
        self.assertTrue(self.score()["verified"])

    def test_accepted_evidence_needs_reviewer(self):
        self.evidence["reviewer_role"] = " "
        self.assertFalse(self.score()["verified"])
