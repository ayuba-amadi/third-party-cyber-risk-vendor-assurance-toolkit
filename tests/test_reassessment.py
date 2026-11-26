import unittest

from src.config import DEFAULT_DATA_DIR
from src.loader import load_source_tables, load_report_date
from src.operational_reports import collect_operations
from src.reassessment import compare_versions


class ReassessmentTests(unittest.TestCase):
    def test_linked_and_pending_changes_preserve_versions(self):
        data = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)
        date = load_report_date()
        vendors, assessments, criticality, risk, decisions, _ = collect_operations(data, date)
        args = vendors["VEN-004"], assessments, criticality, risk, decisions
        events = data["change_event"].rows
        result = compare_versions(*args, events, date)
        self.assertEqual(result["linked_reassessment_change_ids"], ["CHG-001", "CHG-002"])
        old, new = result["versions"]
        self.assertEqual((old["assessment_id"], old["selection"], old["decision_id"], old["criticality_score"],
                          old["risk_numerator"]), ("ASMT-004", "Historical", "DEC-003", 9, 3))
        self.assertEqual((new["assessment_id"], new["selection"], new["decision_status"], new["criticality_score"],
                          new["risk_numerator"]), ("ASMT-011", "Current", "Awaiting decision", 12, 39))
        self.assertFalse(result["reassessment_required"])
        pending = [dict(events[0], reassessment_assessment_id=""), events[1]]
        self.assertTrue(compare_versions(*args, pending, date)["reassessment_required"])
