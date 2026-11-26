import unittest

from src.config import DEFAULT_DATA_DIR
from src.loader import load_source_tables
from src.risk_reports import collect_rows, compare_fixture
from src.risk_scoring import calculate_all_assessment_risk


class FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_source_tables(DEFAULT_DATA_DIR)
        cls.rows = collect_rows(calculate_all_assessment_risk(cls.data, "2026-11-18"))

    def test_all_oracle_fields(self):
        comparisons = compare_fixture(self.rows, DEFAULT_DATA_DIR)
        for name, count in (("risk_results", 11), ("question_scores", 264), ("domain_completeness", 66)):
            with self.subTest(name=name):
                self.assertEqual(comparisons[name], dict(status="PASS", rows=count, errors=[]))

    def test_demonstration_cases(self):
        expected = {1: (6, 24, "Low"), 2: (59, 22, "Incomplete"), 3: (28, 24, "High"),
                    5: (22, 23, "Incomplete"), 6: (19, 23, "Incomplete"), 9: (20, 24, "High"),
                    10: (141, 14, "Incomplete"), 11: (39, 23, "Incomplete")}
        for row in self.rows["risk_results"]:
            number = int(row["assessment_id"].split("-")[1])
            if number in expected:
                self.assertEqual((row["weighted_points"], row["verified_count"], row["final_rating"]), expected[number])
            if number in (3, 9):
                self.assertEqual(row["raw_band"], "Low")
                self.assertTrue(row["confirmed_critical_failures"])
            if number == 10:
                self.assertEqual(len(row["unanswered_questions"]), 10)
