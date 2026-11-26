import csv
from io import BytesIO, StringIO
import json
import unittest
from zipfile import ZipFile

from app.export_helpers import REPORT_TYPES, export_package, render_report, report_payload, table_csv
from app.state import Workspace


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.ws = Workspace.load()

    def test_csv_record_roundtrip(self):
        record = self.ws.rows("vendor")[0]
        exported = table_csv(self.ws, "vendor", [record])
        self.assertEqual(list(csv.DictReader(StringIO(exported))), [record])

    def test_all_report_formats(self):
        for kind in REPORT_TYPES:
            with self.subTest(kind=kind):
                vendor = "VEN-001" if kind == "Individual vendor assessment" else ""
                aid = "ASMT-001" if vendor else ""
                formats = render_report(*report_payload(self.ws, kind, vendor, aid))
                self.assertEqual(set(formats), {"csv", "json", "md", "html"})
                self.assertEqual(json.loads(formats["json"])["report_date"], "2026-11-18")
                self.assertTrue(list(csv.DictReader(StringIO(formats["csv"]))))

    def test_changed_records_and_manifest(self):
        row = dict(self.ws.rows("vendor")[0], vendor_name="Fictional & Partners <Test>")
        self.assertEqual(self.ws.save(self.ws.vendor_candidate(row, replace=True)), [])
        report = render_report(*report_payload(self.ws, "Individual vendor assessment", "VEN-001", "ASMT-001"))
        self.assertIn("Fictional &amp; Partners &lt;Test&gt;", report["html"])
        with ZipFile(BytesIO(export_package(self.ws, {"assessment": report}))) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            self.assertTrue(manifest["fictional_data"])
            self.assertEqual(manifest["changed_row_counts"], {"vendor": 1})
            self.assertIn("reports/assessment.json", archive.namelist())
            self.assertIn("changes/vendor.csv", archive.namelist())
