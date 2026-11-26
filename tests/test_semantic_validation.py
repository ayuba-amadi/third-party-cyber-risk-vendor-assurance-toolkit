"""Cross-table validation cases for the Phase 2 CSV data model."""

import copy
import csv
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.config import DEFAULT_DATA_DIR, REPOSITORY_ROOT
from src.loader import load_source_tables
from src.validation import validate_tables


class SemanticValidationTests(unittest.TestCase):
    def setUp(self):
        self.data = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)

    def errors(self):
        return [issue for issue in validate_tables(self.data).issues if issue.severity == "ERROR"]

    def assert_field_error(self, field, name=None):
        errors = self.errors()
        self.assertTrue(any(issue.field == field and (name is None or issue.file.endswith(name + ".csv"))
                            for issue in errors), [(issue.file, issue.field, issue.rule) for issue in errors])

    def test_approved_fixture_has_no_semantic_errors_and_reports_overdue_action(self):
        result = validate_tables(self.data)
        self.assertTrue(result.passed, [(issue.field, issue.rule) for issue in result.issues])
        self.assertEqual([row["action_id"] for row in result.overdue_actions], ["ACT-001"])

    def test_current_assessment_must_belong_to_vendor_and_not_be_superseded(self):
        vendor = self.data["vendor"].rows[0]
        vendor["current_assessment_id"] = "ASMT-004"
        self.assert_field_error("current_assessment_id", "vendor")

    def test_reassessment_trigger_and_material_event_link_are_checked(self):
        assessment = next(row for row in self.data["assessment"].rows
                          if row["assessment_id"] == "ASMT-011")
        assessment["trigger"] = "Initial"
        self.assert_field_error("trigger", "assessment")
        self.data = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)
        assessment = next(row for row in self.data["assessment"].rows
                          if row["assessment_id"] == "ASMT-011")
        assessment["trigger"] = "Material change"
        for event in self.data["change_event"].rows:
            event["reassessment_assessment_id"] = ""
        self.assert_field_error("reassessment_assessment_id", "change_event")

    def test_duplicate_service_link_and_questionnaire_gap_are_rejected(self):
        table = self.data["vendor_service_link"]
        table.rows.append(copy.deepcopy(table.rows[0]))
        table.row_numbers.append(999)
        self.assert_field_error("vendor_id, service_id", "vendor_service_link")
        self.data = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)
        self.data["response"].rows.pop(0)
        self.data["response"].row_numbers.pop(0)
        self.assert_field_error("questionnaire_coverage", "assessment")

    def test_response_must_use_option_defined_by_question(self):
        self.data["response"].rows[0]["vendor_claim"] = "Not an approved option"
        self.assert_field_error("vendor_claim", "response")

    def test_evidence_status_cannot_disagree_with_retained_review_history(self):
        evidence = next(row for row in self.data["evidence_item"].rows if row["status"] == "Accepted")
        evidence["status"] = "Received"
        self.assert_field_error("status", "evidence_item")

    def test_snapshot_relationship_factor_and_duplicates_are_checked(self):
        self.data["assessment_criticality_snapshot"].rows[0]["vendor_id"] = "VEN-002"
        self.assert_field_error("vendor_id", "assessment_criticality_snapshot")
        self.data = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)
        self.data["assessment_criticality_snapshot"].rows[0]["data_sensitivity"] = "Unknown"
        self.assert_field_error("data_sensitivity", "assessment_criticality_snapshot")
        self.data = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)
        self.data["assessment_criticality_snapshot"].rows.append(
            copy.deepcopy(self.data["assessment_criticality_snapshot"].rows[0]))
        self.data["assessment_criticality_snapshot"].row_numbers.append(99)
        self.assert_field_error("assessment_id", "assessment_criticality_snapshot")

    def test_decision_independence_justification_and_conditional_action_are_checked(self):
        self.data["decision"].rows[0]["decision_maker_role"] = "GRC analyst"
        self.assert_field_error("decision_maker_role", "decision")
        self.data = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)
        decision = next(row for row in self.data["decision"].rows if row["outcome"] == "Rejected")
        decision["justification"] = ""
        self.assert_field_error("justification", "decision")
        self.data = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)
        action = next(row for row in self.data["corrective_action"].rows if row["finding_id"] == "FND-004")
        action["responsible_party"] = ""
        self.assert_field_error("conditions", "decision")

    def test_open_action_cannot_have_close_date_and_material_change_dates_are_ordered(self):
        self.data["corrective_action"].rows[0]["closed_date"] = "2026-10-01"
        self.assert_field_error("closed_date", "corrective_action")
        self.data = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)
        self.data["change_event"].rows[0]["change_date"] = "2099-01-01"
        self.assert_field_error("reassessment_assessment_id", "change_event")

    def test_phase1_invalid_vendor_and_evidence_cases_remain_rejected(self):
        self.data["vendor"].rows[0]["category"] = "Invalid category"
        self.assert_field_error("category", "vendor")
        self.data = load_source_tables(DEFAULT_DATA_DIR, include_criticality_snapshot=True)
        self.data["evidence_item"].rows[0]["status"] = "Pending"
        self.assert_field_error("status", "evidence_item")

    def test_cli_returns_nonzero_for_incomplete_snapshot_without_rewriting_sources(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            data_dir = temp / "data"
            shutil.copytree(DEFAULT_DATA_DIR, data_dir)
            snapshot_path = data_dir / "assessment_criticality_snapshot.csv"
            with snapshot_path.open(encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                fieldnames = reader.fieldnames
                rows = list(reader)
            rows[0]["data_sensitivity"] = ""
            with snapshot_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            before = snapshot_path.read_bytes()
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "criticality", "--all",
                 "--data-dir", str(data_dir), "--reports-dir", str(temp / "reports")],
                cwd=REPOSITORY_ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("PROVISIONAL — INCOMPLETE INPUTS", result.stdout)
            self.assertEqual(snapshot_path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
