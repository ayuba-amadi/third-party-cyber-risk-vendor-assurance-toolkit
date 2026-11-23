
import csv
import tempfile
import unittest
from pathlib import Path

from src.response_import import (
    EXPECTED_RESPONSE_COLUMNS,
    find_duplicate_response_keys,
    import_response_csv,
)


class TestResponseImport(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = Path(self.temp_dir.name) / "responses.csv"

        self.valid_response = {
            "assessment_id": "ASMT-001",
            "question_id": "AM-01",
            "vendor_claim": "All privileged accounts are reviewed.",
            "reviewer_verified": "Yes",
            "verified_answer": "All privileged accounts are reviewed.",
            "reviewer_note": "Evidence reviewed.",
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_csv(self, records, columns=None):
        if columns is None:
            columns = EXPECTED_RESPONSE_COLUMNS

        with self.csv_path.open(
            "w",
            newline="",
            encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=columns,
                extrasaction="ignore"
            )
            writer.writeheader()
            writer.writerows(records)

        return self.csv_path

    def test_valid_response_csv(self):
        self.write_csv([self.valid_response])

        result = import_response_csv(self.csv_path)

        self.assertEqual(len(result["valid_records"]), 1)
        self.assertEqual(result["rejected_records"], [])
        self.assertEqual(result["file_errors"], [])

    def test_missing_file(self):
        result = import_response_csv(
            Path(self.temp_dir.name) / "missing.csv"
        )

        self.assertIn("File does not exist.", result["file_errors"])

    def test_empty_csv(self):
        self.csv_path.write_text("", encoding="utf-8")

        result = import_response_csv(self.csv_path)

        self.assertTrue(result["file_errors"])

    def test_missing_columns(self):
        columns = EXPECTED_RESPONSE_COLUMNS[:-1]
        self.write_csv([self.valid_response], columns)

        result = import_response_csv(self.csv_path)

        self.assertTrue(
            any("Missing required columns" in error
                for error in result["file_errors"])
        )

    def test_unexpected_columns(self):
        columns = EXPECTED_RESPONSE_COLUMNS + ["extra_column"]
        self.write_csv([self.valid_response], columns)

        result = import_response_csv(self.csv_path)

        self.assertTrue(
            any("Unexpected columns" in error
                for error in result["file_errors"])
        )

    def test_duplicate_response_key(self):
        second_response = self.valid_response.copy()
        second_response["vendor_claim"] = "Different vendor claim."

        self.write_csv([
            self.valid_response,
            second_response
        ])

        result = import_response_csv(self.csv_path)

        self.assertEqual(len(result["valid_records"]), 1)
        self.assertEqual(len(result["rejected_records"]), 1)
        self.assertEqual(
            result["duplicate_keys"],
            [("ASMT-001", "AM-01")]
        )

    def test_invalid_response_is_rejected(self):
        invalid_response = self.valid_response.copy()
        invalid_response["reviewer_verified"] = "Maybe"

        self.write_csv([invalid_response])

        result = import_response_csv(self.csv_path)

        self.assertEqual(result["valid_records"], [])
        self.assertEqual(len(result["rejected_records"]), 1)

    def test_extra_row_values(self):
        with self.csv_path.open(
            "w",
            newline="",
            encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(EXPECTED_RESPONSE_COLUMNS)
            writer.writerow([
                "ASMT-001",
                "AM-01",
                "Claim",
                "No",
                "",
                "Note",
                "Unexpected value",
            ])

        result = import_response_csv(self.csv_path)

        self.assertEqual(len(result["rejected_records"]), 1)
        self.assertIn(
            "Row contains extra values.",
            result["rejected_records"][0]["errors"]
        )

    def test_duplicate_response_keys_helper(self):
        records = [
            {"assessment_id": "ASMT-001", "question_id": "AM-01"},
            {"assessment_id": "ASMT-001", "question_id": "AM-01"},
            {"assessment_id": "ASMT-001", "question_id": "DP-01"},
        ]

        duplicates = find_duplicate_response_keys(records)

        self.assertEqual(
            duplicates,
            [("ASMT-001", "AM-01")]
        )


if __name__ == "__main__":
    unittest.main()
