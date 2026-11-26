import unittest

from src.config import DEFAULT_DATA_DIR
from src.loader import load_source_tables, load_report_date
from src.operational_reports import collect_operations
from src.remediation import action_overdue
from src.validation import validate_tables


class RemediationTests(unittest.TestCase):
    def test_action_and_condition_boundaries(self):
        date = load_report_date()
        self.assertTrue(action_overdue(dict(status="Open", due_date="2026-11-17"), date))
        self.assertFalse(action_overdue(dict(status="Open", due_date="2026-11-18"), date))
        self.assertFalse(action_overdue(dict(status="Closed", due_date="2026-11-17"), date))
        data = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)
        decisions = collect_operations(data, date)[4]
        self.assertTrue(decisions["ASMT-003"]["overdue_condition"])
        self.assertTrue(decisions["ASMT-005"]["open_condition"])
        self.assertFalse(decisions["ASMT-005"]["overdue_condition"])

    def test_invalid_closure_and_vendor_links(self):
        for changes in (dict(status="Closed"), dict(closed_date="2026-11-17"), dict(vendor_id="VEN-001")):
            with self.subTest(changes=changes):
                data = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)
                data["corrective_action"].rows[0].update(changes)
                self.assertFalse(validate_tables(data).passed)
