
import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "..")

from src.evidence_import import import_evidence_csv


class TestEvidenceImport(unittest.TestCase):

    EXPECTED_COLUMNS = [
        "evidence_id",
        "assessment_id",
        "question_id",
        "status",
        "received_date",
        "review_period_end",
        "expiry_date",
        "reviewer_role",
        "reference_path",
        "reason"
    ]

    def create_csv(self, headers, rows):
        """
        Create a temporary CSV file for testing.
        """
        temporary_file = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            suffix=".csv",
            delete=False
        )

        writer = csv.DictWriter(
            temporary_file,
            fieldnames=headers
        )

        writer.writeheader()
        writer.writerows(rows)
        temporary_file.close()

        return Path(temporary_file.name)

    def valid_evidence_record(self):
        """
        Return a fictional valid evidence record.
        """
        return {
            "evidence_id": "EV-001",
            "assessment_id": "ASMT-001",
            "question_id": "AM-01",
            "status": "Received",
            "received_date": "2026-11-20",
            "review_period_end": "",
            "expiry_date": "",
            "reviewer_role": "",
            "reference_path": "evidence/EV-001.pdf",
            "reason": ""
        }

    def test_valid_evidence_csv(self):
        csv_path = self.create_csv(
            self.EXPECTED_COLUMNS,
            [self.valid_evidence_record()]
        )

        try:
            result = import_evidence_csv(csv_path)

            self.assertEqual(len(result["valid_records"]), 1)
            self.assertEqual(len(result["rejected_records"]), 0)
            self.assertEqual(result["file_errors"], [])

        finally:
            csv_path.unlink()

    def test_invalid_evidence_id(self):
        record = self.valid_evidence_record()
        record["evidence_id"] = "INVALID-001"

        csv_path = self.create_csv(
            self.EXPECTED_COLUMNS,
            [record]
        )

        try:
            result = import_evidence_csv(csv_path)

            self.assertEqual(len(result["valid_records"]), 0)
            self.assertEqual(len(result["rejected_records"]), 1)

            self.assertIn(
                "Invalid evidence_id format.",
                result["rejected_records"][0]["errors"]
            )

        finally:
            csv_path.unlink()

    def test_duplicate_evidence_ids(self):
        first_record = self.valid_evidence_record()
        second_record = self.valid_evidence_record()

        second_record["received_date"] = "2026-11-21"

        csv_path = self.create_csv(
            self.EXPECTED_COLUMNS,
            [first_record, second_record]
        )

        try:
            result = import_evidence_csv(csv_path)

            self.assertEqual(len(result["valid_records"]), 1)
            self.assertEqual(len(result["rejected_records"]), 1)
            self.assertEqual(len(result["duplicate_ids"]), 1)

            self.assertEqual(
                result["duplicate_ids"][0]["evidence_id"],
                "EV-001"
            )

        finally:
            csv_path.unlink()

    def test_missing_csv_column(self):
        record = self.valid_evidence_record()

        incomplete_columns = [
            column
            for column in self.EXPECTED_COLUMNS
            if column != "assessment_id"
        ]

        csv_path = self.create_csv(
            incomplete_columns,
            [{
                key: value
                for key, value in record.items()
                if key != "assessment_id"
            }]
        )

        try:
            result = import_evidence_csv(csv_path)

            self.assertIn(
                "Missing columns: assessment_id",
                result["file_errors"]
            )

            self.assertEqual(len(result["valid_records"]), 0)

        finally:
            csv_path.unlink()

    def test_unexpected_csv_column(self):
        record = self.valid_evidence_record()

        columns_with_extra = self.EXPECTED_COLUMNS + [
            "unauthorized_field"
        ]

        record["unauthorized_field"] = "unexpected value"

        csv_path = self.create_csv(
            columns_with_extra,
            [record]
        )

        try:
            result = import_evidence_csv(csv_path)

            self.assertIn(
                "Unexpected columns: unauthorized_field",
                result["file_errors"]
            )

            self.assertEqual(len(result["valid_records"]), 0)

        finally:
            csv_path.unlink()

    def test_duplicate_csv_column_headings(self):
        record = self.valid_evidence_record()

        duplicate_columns = (
            self.EXPECTED_COLUMNS + ["evidence_id"]
        )

        csv_path = self.create_csv(
            duplicate_columns,
            [record]
        )

        try:
            result = import_evidence_csv(csv_path)

            self.assertIn(
                "The CSV contains duplicate column headings.",
                result["file_errors"]
            )

            self.assertEqual(len(result["valid_records"]), 0)

        finally:
            csv_path.unlink()

    def test_row_with_extra_values(self):
        record = self.valid_evidence_record()

        csv_path = self.create_csv(
            self.EXPECTED_COLUMNS,
            [record]
        )

        try:
            with csv_path.open(
                mode="a",
                encoding="utf-8",
                newline=""
            ) as csv_file:
                csv_file.write(
                    "EV-002,ASMT-002,AM-02,Received,"
                    "2026-11-21,,,,evidence/EV-002.pdf,,EXTRA\n"
                )

            result = import_evidence_csv(csv_path)

            self.assertEqual(len(result["valid_records"]), 1)
            self.assertEqual(len(result["rejected_records"]), 1)

            self.assertIn(
                "This row contains more values "
                "than the CSV header defines.",
                result["rejected_records"][0]["errors"]
            )

        finally:
            csv_path.unlink()

    def test_missing_csv_file(self):
        missing_path = (
            Path(tempfile.gettempdir())
            / "nonexistent_evidence_file.csv"
        )

        result = import_evidence_csv(missing_path)

        self.assertEqual(len(result["valid_records"]), 0)
        self.assertEqual(len(result["rejected_records"]), 0)

        self.assertTrue(
            any(
                "File not found:" in error
                for error in result["file_errors"]
            )
        )

    def test_empty_csv_file(self):
        temporary_file = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            suffix=".csv",
            delete=False
        )

        temporary_file.close()
        csv_path = Path(temporary_file.name)

        try:
            result = import_evidence_csv(csv_path)

            self.assertIn(
                "The CSV file is empty or has no header row.",
                result["file_errors"]
            )

            self.assertEqual(len(result["valid_records"]), 0)

        finally:
            csv_path.unlink()

    def test_row_with_missing_values(self):
        csv_path = (
            Path(tempfile.gettempdir())
            / "evidence_missing_values_test.csv"
        )

        try:
            with csv_path.open(
                mode="w",
                encoding="utf-8",
                newline=""
            ) as csv_file:

                writer = csv.writer(csv_file)

                writer.writerow(self.EXPECTED_COLUMNS)

                # Write only 6 values instead of the required 10.
                writer.writerow([
                    "EV-001",
                    "ASMT-001",
                    "AM-01",
                    "Received",
                    "2026-11-20",
                    ""
                ])

            result = import_evidence_csv(csv_path)

            self.assertEqual(len(result["valid_records"]), 0)
            self.assertEqual(len(result["rejected_records"]), 1)

            self.assertIn(
                "This row contains fewer values than the CSV header defines.",
                result["rejected_records"][0]["errors"][0]
            )

        finally:
            if csv_path.exists():
                csv_path.unlink()


if __name__ == "__main__":
    unittest.main()
