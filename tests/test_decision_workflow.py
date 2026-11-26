import unittest

from src.config import DEFAULT_DATA_DIR
from src.loader import load_source_tables, load_report_date
from src.operational_reports import collect_operations
from src.validation import validate_tables


class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.data = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)
        self.date = load_report_date()

    def test_recorded_outcomes(self):
        decisions = collect_operations(self.data, self.date)[4]
        self.assertTrue(decisions["ASMT-001"]["active_approval"])
        self.assertFalse(decisions["ASMT-009"]["active_approval"])
        self.assertFalse(decisions["ASMT-009"]["expired_approval"])
        self.assertTrue(decisions["ASMT-006"]["expired_approval"])
        self.assertEqual(decisions["ASMT-004"]["selection"], "Historical")
        self.assertNotIn("ASMT-011", decisions)

    def test_invalid_fields_and_dates(self):
        for field, value in (("conditions", ""), ("condition_deadline", ""), ("justification", ""),
                             ("review_date", "2026-11-01"), ("review_date", "2028-01-01"),
                             ("decision_maker_role", "GRC analyst")):
            with self.subTest(field=field, value=value):
                self.setUp()
                self.data["decision"].rows[1][field] = value
                self.assertFalse(validate_tables(self.data, self.date).passed)

    def test_ordinary_approval_cannot_bypass_risk_flags(self):
        for index in (1, 3):
            with self.subTest(index=index):
                self.setUp()
                self.data["decision"].rows[index]["outcome"] = "Approved"
                with self.assertRaisesRegex(ValueError, "ordinary approval"):
                    collect_operations(self.data, self.date)
