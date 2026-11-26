import unittest

from src.config import DEFAULT_DATA_DIR
from src.loader import load_source_tables
from src.risk_scoring import calculate_all_assessment_risk


class DomainTests(unittest.TestCase):
    def test_six_domains_and_counts_reconcile(self):
        for assessment, _, domains in calculate_all_assessment_risk(load_source_tables(DEFAULT_DATA_DIR), "2026-11-18"):
            self.assertEqual({row["domain"] for row in domains}, {"AM", "BC", "DP", "GV", "IN", "SC"})
            self.assertEqual(len(domains), 6)
            self.assertTrue(all(row["total_questions"] == 4 for row in domains))
            for field in ("answered_count", "verified_count"):
                self.assertEqual(sum(row[field] for row in domains), assessment[field])
