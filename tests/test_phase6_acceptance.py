"""Check submission scenarios and rejected candidates against the real workspace."""
from copy import deepcopy
from pathlib import Path
import unittest

from app.state import Workspace
from src.management_reporting import compare_management


class Phase6Acceptance(unittest.TestCase):
    def setUp(self):
        self.workspace = Workspace.load()

    def test_invalid_candidates_do_not_change_workspace(self):
        cases = (
            ("vendor", "vendor_id", "VEN-001", True),
            ("vendor", "vendor_name", "", False),
            ("vendor", "category", "Unlisted category", False),
            ("vendor", "system_access", "Unlisted access", False),
            ("vendor", "next_review_date", "2026-02-30", False),
            ("evidence_item", "status", "Unknown", False),
            ("response", "assessment_id", "ASMT-999", False),
            ("decision", "outcome", "Unknown", False),
        )
        for table, field, value, append in cases:
            with self.subTest(table=table, field=field):
                original = deepcopy(self.workspace.rows(table))
                candidate = deepcopy(self.workspace.tables)
                rows = candidate[table].rows
                if append:
                    candidate = self.workspace.vendor_candidate(dict(rows[0]))
                else:
                    rows[0][field] = value
                issues = self.workspace.save(candidate)
                matching = [issue for issue in issues if issue.field == field and issue.value == value
                            and Path(issue.file).name == f"{table}.csv"]
                self.assertTrue(matching, issues)
                for issue in matching:
                    self.assertEqual(Path(issue.file).name, f"{table}.csv")
                    self.assertGreater(issue.row, 1)
                    self.assertTrue(issue.correction)
                self.assertEqual(self.workspace.rows(table), original)

    def test_missing_evidence_and_confirmed_critical_failure(self):
        _, _, _, risks, decisions, _ = self.workspace.operations
        incomplete, question_scores, _ = risks["ASMT-002"]
        self.assertEqual(incomplete["completeness"], "Incomplete")
        for score in (score for score in question_scores if score["question_id"] in {"AM-01", "DP-01"}):
            self.assertEqual(score["effective_evidence_status"], "Missing")
            self.assertEqual(score["risk_value"], 4)
        self.assertEqual(incomplete["verified_count"], 22)
        self.assertNotIn("ASMT-002", decisions)
        high, _, _ = risks["ASMT-009"]
        self.assertEqual(high["raw_band"], "Low")
        self.assertEqual(high["final_rating"], "High")
        self.assertEqual(high["confirmed_critical_failures"], ["DP-01"])
        self.assertEqual(decisions["ASMT-009"]["outcome"], "Rejected")

    def test_management_matches_research_fixture(self):
        rows, concentration, _ = self.workspace.management()
        self.assertEqual(compare_management(rows, Path("sample-data/expected_management.csv")), 33)
        self.assertEqual(next(row["count"] for row in rows if row["group"] == "Current vendors"), 10)
        self.assertGreater(next(row["count"] for row in concentration if row["source_id"] == "VEN-001"), 1)
