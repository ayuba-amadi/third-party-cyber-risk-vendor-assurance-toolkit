import unittest

from src.config import DEFAULT_DATA_DIR
from src.loader import load_source_tables, load_report_date
from src.management_reporting import compare_management, management_summary, reconcile
from src.operational_reports import collect_operations


class ReconciliationTests(unittest.TestCase):
    def test_all_fixture_counts_and_vendor_ids(self):
        data = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)
        date = load_report_date()
        _, _, criticality, risks, decisions, actions = collect_operations(data, date)
        rows, _, _ = management_summary(data, criticality, risks, decisions, actions, date)
        oracle = DEFAULT_DATA_DIR / "expected_management.csv"
        self.assertEqual(compare_management(rows, oracle), 33)
        row = next(row for row in rows if row["group"] == "Expired approval")
        row["vendor_ids"] = ["VEN-001"]
        with self.assertRaisesRegex(ValueError, "Expired approval"):
            compare_management(rows, oracle)

    def test_duplicate_source_ids_fail(self):
        with self.assertRaisesRegex(ValueError, "does not reconcile"):
            reconcile([dict(count=2, source_ids=["VEN-001", "VEN-001"])], {"VEN-001"})
