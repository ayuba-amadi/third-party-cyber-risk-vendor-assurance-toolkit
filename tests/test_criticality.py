"""Approved fixture expectations for assessment-level criticality."""

import unittest

from src.config import DEFAULT_DATA_DIR
from src.criticality import calculate_all_criticality
from src.loader import load_source_tables


class CriticalityFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)
        cls.results = {row.assessment_id: row for row in calculate_all_criticality(cls.data)}

    def test_fixture_rows_match_approved_scores_bands_and_override_reasons(self):
        expected = {
            "ASMT-001": ("VEN-001", 13, "Critical", "Critical", {
                "Business-critical service floor", "Regulated plus privileged",
                "Severe dependency plus very hard replacement"}),
            "ASMT-002": ("VEN-002", 12, "Critical", "Critical", {
                "Business-critical service floor", "Regulated plus privileged"}),
            "ASMT-003": ("VEN-003", 12, "Critical", "Critical", {
                "Business-critical service floor", "Severe dependency plus very hard replacement"}),
            "ASMT-004": ("VEN-004", 9, "High", "High", {"Business-critical service floor"}),
            "ASMT-011": ("VEN-004", 12, "Critical", "Critical", {
                "Business-critical service floor", "Regulated plus privileged"}),
            "ASMT-009": ("VEN-009", 9, "High", "High", set()),
        }
        for assessment_id, values in expected.items():
            with self.subTest(assessment_id=assessment_id):
                result = self.results[assessment_id]
                self.assertTrue(result.complete, result.errors)
                self.assertEqual((result.vendor_id, result.total_points, result.base_band,
                                  result.final_band, set(result.override_reasons)), values)
        self.assertEqual(self.results["ASMT-009"].system_access, "Standard")
        self.assertNotIn("Regulated plus privileged", self.results["ASMT-009"].override_reasons)

    def test_historical_assessment_uses_its_own_snapshot(self):
        historical = self.results["ASMT-004"]
        current = self.results["ASMT-011"]
        self.assertEqual((historical.data_sensitivity, historical.system_access,
                          historical.dependency_impact, historical.replaceability,
                          historical.total_points),
                         ("Regulated", "Standard", "3", "Moderate", 9))
        self.assertEqual((current.data_sensitivity, current.system_access,
                          current.dependency_impact, current.replaceability,
                          current.total_points),
                         ("Regulated", "Privileged", "4", "Hard", 12))

    def test_all_results_are_sorted_and_have_analyst_trace(self):
        results = calculate_all_criticality(self.data)
        ids = [result.assessment_id for result in results]
        self.assertEqual(ids, sorted(ids))
        trace = "\n".join(self.results["ASMT-001"].calculation_trace)
        self.assertIn("Base score: 3 + 2 + 4 + 4 = 13", trace)
        self.assertIn("Regulated plus privileged", trace)
        self.assertIn("Final band: Critical", trace)


if __name__ == "__main__":
    unittest.main()
