

import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "..")

from src.assessment_import import (
    import_assessment_csv,
    find_duplicate_assessment_ids,
)


class TestAssessmentImport(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.csv_path = Path(self.temp_dir.name) / "assessments.csv"

        self.columns = [
            "assessment_id",
            "vendor_id",
            "version_no",
            "assessment_date",
            "trigger",
            "assessor_role",
            "status",
            "supersedes_id",
        ]

        self.valid_record = {
            "assessment_id": "ASMT-001",
            "vendor_id": "VEN-001",
            "version_no": "1",
            "assessment_date": "2026-05-18",
            "trigger": "Initial",
            "assessor_role": "GRC Analyst",
            "status": "Draft",
            "supersedes_id": "",
        }

    def write_csv(self, records, columns=None):
        if columns is None:
            columns = self.columns

        with self.csv_path.open(
            "w", newline="", encoding="utf-8"
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=columns,
                extrasaction="ignore"
            )
            writer.writeheader()
            writer.writerows(records)

    def test_valid_assessment_csv(self):
        self.write_csv([self.valid_record])

        valid, rejected, duplicates, errors = import_assessment_csv(
            self.csv_path
        )

        self.assertEqual(len(valid), 1)
        self.assertEqual(rejected, [])
        self.assertEqual(duplicates, [])
        self.assertEqual(errors, [])
        self.assertEqual(valid[0]["version_no"], 1)

    def test_invalid_assessment_id(self):
        record = self.valid_record.copy()
        record["assessment_id"] = "BAD-001"
        self.write_csv([record])

        valid, rejected, duplicates, errors = import_assessment_csv(
            self.csv_path
        )

        self.assertEqual(valid, [])
        self.assertEqual(len(rejected), 1)
        self.assertTrue(any(
            "assessment_id" in error
            for error in rejected[0]["errors"]
        ))

    def test_invalid_vendor_id(self):
        record = self.valid_record.copy()
        record["vendor_id"] = "BAD-001"
        self.write_csv([record])

        valid, rejected, duplicates, errors = import_assessment_csv(
            self.csv_path
        )

        self.assertEqual(valid, [])
        self.assertEqual(len(rejected), 1)
        self.assertTrue(any(
            "vendor_id" in error
            for error in rejected[0]["errors"]
        ))

    def test_duplicate_assessment_ids(self):
        first = self.valid_record.copy()

        second = self.valid_record.copy()
        second["vendor_id"] = "VEN-002"

        self.write_csv([first, second])

        valid, rejected, duplicates, errors = import_assessment_csv(
            self.csv_path
        )

        self.assertEqual(len(valid), 1)
        self.assertEqual(len(rejected), 1)
        self.assertEqual(duplicates, ["ASMT-001"])
        self.assertEqual(errors, [])

    def test_missing_csv_column(self):
        columns = self.columns.copy()
        columns.remove("assessor_role")

        self.write_csv([self.valid_record], columns)

        valid, rejected, duplicates, errors = import_assessment_csv(
            self.csv_path
        )

        self.assertEqual(valid, [])
        self.assertEqual(rejected, [])
        self.assertTrue(any(
            "Missing CSV columns" in error
            for error in errors
        ))

    def test_unexpected_csv_column(self):
        columns = self.columns + ["unexpected_column"]

        self.write_csv([self.valid_record], columns)

        valid, rejected, duplicates, errors = import_assessment_csv(
            self.csv_path
        )

        self.assertEqual(valid, [])
        self.assertTrue(any(
            "Unexpected CSV columns" in error
            for error in errors
        ))

    def test_duplicate_csv_column_headings(self):
        with self.csv_path.open(
            "w", newline="", encoding="utf-8"
        ) as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(self.columns + ["assessment_id"])

        valid, rejected, duplicates, errors = import_assessment_csv(
            self.csv_path
        )

        self.assertEqual(valid, [])
        self.assertTrue(any(
            "duplicate column headings" in error
            for error in errors
        ))

    def test_row_with_extra_values(self):
        with self.csv_path.open(
            "w", newline="", encoding="utf-8"
        ) as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(self.columns)

            writer.writerow([
                "ASMT-001",
                "VEN-001",
                "1",
                "2026-05-18",
                "Initial",
                "GRC Analyst",
                "Draft",
                "",
                "EXTRA VALUE",
            ])

        valid, rejected, duplicates, errors = import_assessment_csv(
            self.csv_path
        )

        self.assertEqual(valid, [])
        self.assertEqual(len(rejected), 1)
        self.assertTrue(any(
            "extra values" in error
            for error in rejected[0]["errors"]
        ))

    def test_row_with_missing_values(self):
        with self.csv_path.open(
            "w", newline="", encoding="utf-8"
        ) as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(self.columns)

            writer.writerow([
                "ASMT-001",
                "VEN-001",
                "1",
                "2026-05-18",
                "Initial",
                "GRC Analyst",
            ])

        valid, rejected, duplicates, errors = import_assessment_csv(
            self.csv_path
        )

        self.assertEqual(valid, [])
        self.assertEqual(len(rejected), 1)
        self.assertTrue(any(
            "missing values" in error.lower()
            for error in rejected[0]["errors"]
        ))

    def test_invalid_version_number(self):
        record = self.valid_record.copy()
        record["version_no"] = "one"

        self.write_csv([record])

        valid, rejected, duplicates, errors = import_assessment_csv(
            self.csv_path
        )

        self.assertEqual(valid, [])
        self.assertEqual(len(rejected), 1)
        self.assertTrue(any(
            "version_no" in error
            for error in rejected[0]["errors"]
        ))

    def test_missing_csv_file(self):
        missing_path = Path(self.temp_dir.name) / "missing.csv"

        valid, rejected, duplicates, errors = import_assessment_csv(
            missing_path
        )

        self.assertEqual(valid, [])
        self.assertEqual(rejected, [])
        self.assertEqual(duplicates, [])
        self.assertTrue(any(
            "File not found" in error
            for error in errors
        ))

    def test_empty_csv_file(self):
        self.csv_path.write_text("", encoding="utf-8")

        valid, rejected, duplicates, errors = import_assessment_csv(
            self.csv_path
        )

        self.assertEqual(valid, [])
        self.assertTrue(any(
            "empty" in error.lower()
            for error in errors
        ))

    def test_find_duplicate_assessment_ids(self):
        assessments = [
            {"assessment_id": "ASMT-001"},
            {"assessment_id": "ASMT-002"},
            {"assessment_id": "ASMT-001"},
        ]

        duplicates = find_duplicate_assessment_ids(assessments)

        self.assertEqual(duplicates, {"ASMT-001"})


if __name__ == "__main__":
    unittest.main()
