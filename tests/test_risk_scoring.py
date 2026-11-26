import unittest
from fractions import Fraction

from src.config import DEFAULT_DATA_DIR
from src.loader import load_source_tables
from src.risk_scoring import calculate_all_assessment_risk, parse_options, risk_band


class RiskTests(unittest.TestCase):
    def test_question_bank(self):
        data = load_source_tables(DEFAULT_DATA_DIR)
        questions = data["question"].rows
        self.assertEqual(len(questions), 24)
        self.assertEqual(len({row["domain"] for row in questions}), 6)
        for row in questions:
            self.assertIn(int(row["weight"]), range(1, 6))
            self.assertTrue(all(value in range(5) for value in parse_options(row["response_options"]).values()))

    def test_invalid_options(self):
        for definition in ("Label = 5", "Label", "Label = 0 | Label = 1", "Label = -1"):
            with self.subTest(definition=definition), self.assertRaises(ValueError):
                parse_options(definition)

    def test_unrounded_thresholds(self):
        for percent, band in ((Fraction(19999999, 1000000), "Low"), (20, "Medium"),
                              (40, "High"), (60, "Critical"), (100, "Critical")):
            self.assertEqual(risk_band(percent), band)

    def test_missing_response_retains_denominator(self):
        data = load_source_tables(DEFAULT_DATA_DIR)
        data["response"].rows = data["response"].rows[1:]
        result, _, _ = calculate_all_assessment_risk(data, "2026-11-18")[0]
        self.assertEqual(result["maximum_points"], 344)
        self.assertEqual(result["final_rating"], "Incomplete")
