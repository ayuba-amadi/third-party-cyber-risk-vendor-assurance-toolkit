"""Exact score thresholds, override behavior and fail-safe input handling."""

import copy
import unittest

from src.config import DEFAULT_DATA_DIR
from src.criticality import calculate_all_criticality, calculate_criticality
from src.loader import load_source_tables


class CriticalityBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.data = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)

    def evaluate(self, sensitivity, access, dependency, replacement, tier="Standard"):
        vendor = {"vendor_id": "VEN-TEST"}
        services = [{"service_id": "SVC-01", "service_tier": tier}]
        links = [{"vendor_id": "VEN-TEST", "service_id": "SVC-01"}]
        snapshot = {"assessment_id": "ASMT-TEST", "vendor_id": "VEN-TEST",
                    "data_sensitivity": sensitivity, "system_access": access,
                    "dependency_impact": str(dependency), "replaceability": replacement}
        return calculate_criticality("ASMT-TEST", vendor, services, links, snapshot)

    def test_exact_base_band_boundaries(self):
        cases = (
            ("None", "None", 1, "Easy", 2, "Low"),
            ("Internal", "None", 1, "Easy", 3, "Low"),
            ("Internal", "None", 1, "Moderate", 4, "Medium"),
            ("Confidential", "Standard", 1, "Moderate", 6, "Medium"),
            ("Regulated", "Standard", 1, "Moderate", 7, "High"),
            ("Regulated", "Standard", 2, "Hard", 9, "High"),
            ("Confidential", "Privileged", 2, "Very hard", 10, "Critical"),
            ("Regulated", "Privileged", 4, "Very hard", 13, "Critical"),
        )
        for sensitivity, access, dependency, replacement, total, band in cases:
            with self.subTest(total=total):
                result = self.evaluate(sensitivity, access, dependency, replacement)
                self.assertTrue(result.complete, result.errors)
                self.assertEqual((result.total_points, result.base_band), (total, band))

    def test_business_critical_service_floor_and_highest_service_tier(self):
        result = self.evaluate("Internal", "None", 1, "Easy", tier="Business-critical")
        self.assertEqual((result.total_points, result.base_band, result.final_band), (3, "Low", "High"))
        self.assertIn("Business-critical service floor", result.override_reasons)
        services = [
            {"service_id": "SVC-01", "service_tier": "Important"},
            {"service_id": "SVC-02", "service_tier": "Business-critical"},
        ]
        links = [{"vendor_id": "VEN-TEST", "service_id": "SVC-01"},
                 {"vendor_id": "VEN-TEST", "service_id": "SVC-02"}]
        snapshot = {"assessment_id": "ASMT-TEST", "vendor_id": "VEN-TEST",
                    "data_sensitivity": "Internal", "system_access": "None",
                    "dependency_impact": "1", "replaceability": "Easy"}
        multi = calculate_criticality("ASMT-TEST", {"vendor_id": "VEN-TEST"}, services, links, snapshot)
        self.assertEqual(multi.highest_service_tier, "Business-critical")
        self.assertEqual(set(multi.linked_services), {"SVC-01", "SVC-02"})

    def test_regulated_privileged_and_severe_dependency_overrides(self):
        regulated = self.evaluate("Regulated", "Privileged", 1, "Easy")
        severe = self.evaluate("Internal", "None", 4, "Very hard")
        self.assertEqual(regulated.final_band, "Critical")
        self.assertIn("Regulated plus privileged", regulated.override_reasons)
        self.assertEqual(severe.final_band, "Critical")
        self.assertIn("Severe dependency plus very hard replacement", severe.override_reasons)

    def test_missing_or_invalid_factor_never_defaults_to_a_favourable_value(self):
        missing = {"assessment_id": "ASMT-TEST", "vendor_id": "VEN-TEST",
                   "system_access": "None", "dependency_impact": "1", "replaceability": "Easy"}
        args = ("ASMT-TEST", {"vendor_id": "VEN-TEST"},
                [{"service_id": "SVC-01", "service_tier": "Standard"}],
                [{"vendor_id": "VEN-TEST", "service_id": "SVC-01"}])
        result = calculate_criticality(*args, missing)
        self.assertFalse(result.complete)
        self.assertIsNone(result.data_sensitivity_points)
        self.assertIsNone(result.total_points)
        self.assertEqual(result.final_band, "PROVISIONAL — INCOMPLETE INPUTS")
        self.assertEqual(result.errors[0]["field"], "data_sensitivity")
        invalid = dict(missing, data_sensitivity="Unknown")
        invalid_result = calculate_criticality(*args, invalid)
        self.assertFalse(invalid_result.complete)
        self.assertEqual(invalid_result.errors[0]["value"], "Unknown")
        self.assertIn("Use one of", invalid_result.errors[0]["correction"])

    def test_duplicate_snapshot_is_rejected(self):
        snapshot = {"assessment_id": "ASMT-TEST", "vendor_id": "VEN-TEST",
                    "data_sensitivity": "Internal", "system_access": "None",
                    "dependency_impact": "1", "replaceability": "Easy"}
        result = calculate_criticality(
            "ASMT-TEST", {"vendor_id": "VEN-TEST"},
            [{"service_id": "SVC-01", "service_tier": "Standard"}],
            [{"vendor_id": "VEN-TEST", "service_id": "SVC-01"}], [snapshot, snapshot])
        self.assertFalse(result.complete)
        self.assertTrue(any(error["field"] == "assessment_id" for error in result.errors))

    def test_historical_values_are_not_replaced_by_current_vendor_values(self):
        data = copy.deepcopy(self.data)
        vendor = next(row for row in data["vendor"].rows if row["vendor_id"] == "VEN-004")
        vendor.update(data_sensitivity="Internal", system_access="None",
                      dependency_impact="1", replaceability="Easy")
        result = {row.assessment_id: row for row in calculate_all_criticality(data)}
        self.assertEqual(result["ASMT-004"].total_points, 9)
        self.assertEqual(result["ASMT-011"].total_points, 12)
        self.assertTrue(result["ASMT-004"].complete)
        self.assertFalse(result["ASMT-011"].complete)
        self.assertEqual(result["ASMT-011"].final_band, "PROVISIONAL — INCOMPLETE INPUTS")

    def test_current_snapshot_conflict_blocks_final_band(self):
        data = copy.deepcopy(self.data)
        vendor = next(row for row in data["vendor"].rows if row["vendor_id"] == "VEN-001")
        vendor["data_sensitivity"] = "Internal"
        result = next(row for row in calculate_all_criticality(data) if row.assessment_id == "ASMT-001")
        self.assertFalse(result.complete)
        self.assertEqual(result.total_points, 13)
        self.assertEqual(result.final_band, "PROVISIONAL — INCOMPLETE INPUTS")
        self.assertTrue(any(error["field"] == "data_sensitivity" for error in result.errors))


if __name__ == "__main__":
    unittest.main()
