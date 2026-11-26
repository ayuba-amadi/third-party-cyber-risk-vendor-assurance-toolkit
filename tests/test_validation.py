"""Independent in-memory mutations; fictional source files are never edited."""

import copy
import unittest

from src.config import DEFAULT_DATA_DIR
from src.loader import load_source_tables
from src.schema import SCHEMAS
from src.validation import validate_tables


class ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = load_source_tables(DEFAULT_DATA_DIR)

    def setUp(self):
        self.data = copy.deepcopy(self.fixture)

    def errors(self):
        return validate_tables(self.data).issues

    def assert_issue(self, category, field=None):
        issues = self.errors()
        matches = [i for i in issues if i.category == category and (field is None or i.field == field)]
        self.assertTrue(matches, issues)
        return matches

    def test_baseline_has_no_structural_errors(self):
        result = validate_tables(self.data)
        self.assertTrue(result.passed, result.issues)
        self.assertEqual(result.summary["valid_tables"], 12)
        self.assertEqual(result.summary["warnings"], 0)

    def test_duplicate_vendor_retains_all_rows_and_identifies_both_lines(self):
        table = self.data["vendor"]
        table.rows.append(dict(table.rows[0]))
        table.row_numbers.append(12)
        issue = self.assert_issue("duplicates", "vendor_id")[0]
        self.assertEqual(issue.row, 12)
        self.assertIn("row 2", issue.rule)
        self.assertEqual(issue.value, "VEN-001")
        self.assertEqual(len(table.rows), 11)
        self.assertEqual(validate_tables(self.data).summary["duplicate_records"], 1)

    def test_all_primary_and_composite_duplicates_are_detected(self):
        for name in SCHEMAS:
            with self.subTest(table=name):
                self.data = copy.deepcopy(self.fixture)
                table = self.data[name]
                table.rows.append(dict(table.rows[0]))
                table.row_numbers.append(len(table.rows) + 1)
                self.assert_issue("duplicates")

    def test_missing_values_include_dictionary_required_fields(self):
        cases = (("vendor", "vendor_id"), ("vendor", "vendor_name"), ("vendor", "category"),
                 ("vendor", "data_sensitivity"), ("vendor", "system_access"),
                 ("vendor", "dependency_impact"), ("vendor", "replaceability"),
                 ("assessment", "assessment_id"), ("assessment", "vendor_id"),
                 ("question", "question_id"), ("evidence_item", "status"), ("decision", "outcome"))
        for name, field in cases:
            with self.subTest(table=name, field=field):
                self.data = copy.deepcopy(self.fixture)
                self.data[name].rows[0][field] = "   "
                self.assert_issue("missing_fields", field)

    def test_invalid_evidence_status(self):
        self.data["evidence_item"].rows[0]["status"] = "Pending"
        issue = self.assert_issue("invalid_values", "status")[0]
        self.assertIn("Missing, Received, Accepted, Rejected, Expired", issue.correction)

    def test_orphan_assessment_reference(self):
        self.data["evidence_item"].rows[0]["assessment_id"] = "ASMT-999"
        self.assert_issue("orphans", "assessment_id")

    def test_all_declared_foreign_keys(self):
        for name, schema in SCHEMAS.items():
            for field, _, _ in schema.foreign_keys:
                with self.subTest(table=name, field=field):
                    self.data = copy.deepcopy(self.fixture)
                    self.data[name].rows[0][field] = "UNKNOWN"
                    self.assert_issue("orphans", field)

    def test_evidence_requires_response_pair(self):
        table = self.data["response"]
        table.rows.pop(0)
        table.row_numbers.pop(0)
        self.assert_issue("orphans", "assessment_id, question_id")

    def test_invalid_dates_and_timestamp(self):
        for name, field, value in (("vendor", "next_review_date", "2026-02-30"),
                                   ("evidence_item", "received_date", "2026-2-01"),
                                   ("reviewer_audit_entry", "timestamp", "2026-13-01T09:00:00")):
            with self.subTest(table=name):
                self.data = copy.deepcopy(self.fixture)
                self.data[name].rows[0][field] = value
                self.assert_issue("date_errors", field)

    def test_decision_date_ordering(self):
        for field, value in (("review_date", "2020-01-01"), ("expiry_date", "2020-01-01"),
                             ("expiry_date", "2026-09-01")):
            with self.subTest(field=field, value=value):
                self.data = copy.deepcopy(self.fixture)
                self.data["decision"].rows[0][field] = value
                self.assert_issue("date_errors")

    def test_reassessment_cannot_precede_change(self):
        self.data["change_event"].rows[0]["change_date"] = "2099-01-01"
        self.assert_issue("date_errors", "reassessment_assessment_id")

    def test_same_vendor_required_for_linked_records(self):
        cases = (("vendor", "current_assessment_id", "ASMT-002"),
                 ("corrective_action", "vendor_id", "VEN-001"),
                 ("change_event", "reassessment_assessment_id", "ASMT-001"))
        for name, field, value in cases:
            with self.subTest(table=name):
                self.data = copy.deepcopy(self.fixture)
                self.data[name].rows[0][field] = value
                self.assert_issue("invalid_values")

    def test_conditional_approval_requires_conditions_and_deadline(self):
        row = next(r for r in self.data["decision"].rows if r["outcome"] == "Conditionally Approved")
        row["condition_deadline"] = ""
        row["conditions"] = ""
        self.assert_issue("missing_fields", "condition_deadline")
        self.assert_issue("missing_fields", "conditions")

    def test_evidence_state_required_fields(self):
        cases = (("Accepted", "reviewer_role"), ("Accepted", "expiry_date"),
                 ("Expired", "review_period_end"), ("Rejected", "reason"),
                 ("Received", "reference_path"))
        for status, field in cases:
            with self.subTest(status=status, field=field):
                self.data = copy.deepcopy(self.fixture)
                row = next(r for r in self.data["evidence_item"].rows if r["status"] == status)
                row[field] = ""
                self.assert_issue("missing_fields", field)

    def test_answer_labels_and_verification_values(self):
        self.data["response"].rows[0]["vendor_claim"] = "Invented option"
        self.data["response"].rows[0]["reviewer_verified"] = "Maybe"
        self.assert_issue("invalid_values", "vendor_claim")
        self.assert_issue("invalid_values", "reviewer_verified")

    def test_audit_orphan_is_reported(self):
        self.data["reviewer_audit_entry"].rows[0]["record_id"] = "ASMT-999"
        self.assert_issue("orphans", "record_id")

    def test_early_action_closure_is_valid_and_closed_date_required(self):
        row = self.data["corrective_action"].rows[0]
        row.update(status="Closed", closed_date="2026-10-01")
        self.assertTrue(validate_tables(self.data).passed)
        row["closed_date"] = ""
        self.assert_issue("missing_fields", "closed_date")

    def test_all_rows_can_be_reordered_without_changing_results(self):
        for table in self.data.values():
            table.rows.reverse()
            table.row_numbers.reverse()
        self.assertTrue(validate_tables(self.data).passed)

    def test_each_error_has_actionable_context(self):
        self.data["vendor"].rows[0]["category"] = "Other"
        for issue in self.errors():
            self.assertTrue(issue.file.endswith(".csv"))
            self.assertIsInstance(issue.row, int)
            self.assertTrue(issue.field)
            self.assertIsInstance(issue.value, str)
            self.assertTrue(issue.rule)
            self.assertEqual(issue.severity, "ERROR")
            self.assertTrue(issue.correction)


if __name__ == "__main__":
    unittest.main()
