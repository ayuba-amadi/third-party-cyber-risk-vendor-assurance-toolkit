import unittest

from src.config import DEFAULT_DATA_DIR
from src.loader import load_source_tables, load_report_date
from src.management_reporting import management_summary
from src.operational_reports import collect_operations


class ManagementTests(unittest.TestCase):
    def test_current_population_and_concentration(self):
        data = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)
        date = load_report_date()
        _, _, criticality, risks, decisions, actions = collect_operations(data, date)
        rows, concentration, reviews = management_summary(data, criticality, risks, decisions, actions, date)
        groups = {(row["breakdown"], row["group"]): row for row in rows}
        self.assertEqual(groups["total", "Current vendors"]["count"], 10)
        for group in ("category", "criticality", "decision"):
            ids = [vid for row in rows if row["breakdown"] == group for vid in row["vendor_ids"]]
            self.assertEqual(len(ids), len(set(ids)))
            self.assertEqual(len(ids), 10)
        self.assertEqual(groups["total", "Open findings"]["count"], 7)
        self.assertEqual(groups["flag", "Open condition"]["count"], 2)
        self.assertEqual([row["vendor_id"] for row in reviews], ["VEN-003", "VEN-006"])
        counts = {row["source_id"]: row["count"] for row in concentration}
        for key, count in {"SVC-03": 3, "SVC-04": 2, "SVC-05": 2, "SVC-06": 2,
                           "VEN-001": 4, "VEN-006": 2}.items():
            self.assertEqual(counts[key], count)
