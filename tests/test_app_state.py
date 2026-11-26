from copy import deepcopy
from datetime import date
import unittest

from app.state import Workspace


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.ws = Workspace.load()
        self.assertIsNotNone(self.ws.operations, self.ws.calculation_error)

    def test_defaults_and_source_isolation(self):
        self.assertEqual(self.ws.report_date, date(2026, 11, 18))
        self.assertEqual(self.ws.assessment_id, "ASMT-001")
        self.assertEqual(len(self.ws.rows("vendor")), 10)
        record = dict(self.ws.rows("vendor")[0], vendor_id="VEN-011", vendor_name="Fictional Test",
                      current_assessment_id="", assessment_status="Not started")
        files = {table.path: table.path.read_bytes() for table in self.ws.source.values()}
        self.assertEqual(self.ws.save(self.ws.vendor_candidate(record)), [])
        self.assertEqual(len(self.ws.rows("vendor")), 11)
        self.assertEqual(len(self.ws.source["vendor"].rows), 10)
        self.assertEqual(self.ws.changed_rows("vendor"), [record])
        self.assertEqual(self.ws.changed_rows("decision"), [])
        draft, aid = self.ws.draft_assessment(record, "Fictional analyst")
        self.assertEqual(self.ws.save(draft), [])
        self.assertEqual(self.ws.operations[3][aid][0]["completeness"], "Incomplete")
        self.assertEqual(self.ws.changed_rows("decision"), [])
        self.assertEqual({path: path.read_bytes() for path in files}, files)

    def test_duplicate_and_invalid_vendor_never_save(self):
        record = deepcopy(self.ws.rows("vendor")[0])
        self.assertTrue(self.ws.save(self.ws.vendor_candidate(record)))
        invalid = dict(record, vendor_id="", system_access="Root", next_review_date="tomorrow")
        fields = {issue.field for issue in self.ws.save(self.ws.vendor_candidate(invalid))}
        self.assertTrue({"vendor_id", "system_access", "next_review_date"} <= fields)
        self.assertFalse(self.ws.changed_rows("vendor"))

    def test_criticality_preview_recalculates_without_rewriting_snapshot(self):
        vendor = next(row for row in self.ws.rows("vendor") if row["vendor_id"] == "VEN-003")
        before = self.ws.criticality_preview(vendor)
        changed = dict(vendor, system_access="Privileged")
        after = self.ws.criticality_preview(changed)
        self.assertGreater(after.total_points, before.total_points)
        self.assertIn("Regulated plus privileged", after.override_reasons)
        self.assertEqual(self.ws.save(self.ws.vendor_candidate(changed, replace=True)), [])
        self.assertEqual(self.ws.operations[2]["ASMT-003"].system_access, "Standard")
        self.assertFalse(self.ws.changed_rows("assessment_criticality_snapshot"))

    def test_report_date_recalculates_expiry(self):
        self.ws.set_report_date(date(2026, 10, 20))
        self.assertFalse(self.ws.operations[4]["ASMT-006"]["expired_approval"])
        self.ws.set_report_date(date(2026, 11, 18))
        self.assertTrue(self.ws.operations[4]["ASMT-006"]["expired_approval"])
