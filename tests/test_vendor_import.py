
import csv
import tempfile
import unittest

from pathlib import Path

from vendor_import import import_vendor_csv


class TestVendorImport(unittest.TestCase):

    def setUp(self):
        """Prepare temporary files and valid vendor data."""

        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_folder = Path(self.temp_dir.name)
        self.csv_file = self.test_folder / "vendors.csv"

        self.columns = [
            "vendor_id",
            "vendor_name",
            "category",
            "service_description",
            "business_owner",
            "data_sensitivity",
            "data_types",
            "system_access",
            "dependency_impact",
            "replaceability",
            "subcontractor_use",
            "assessment_status",
            "current_assessment_id",
            "next_review_date",
            "material_change_flag"
        ]

        self.valid_vendor = {
            "vendor_id": "VEN-001",
            "vendor_name": "NimbusCloud Hosting",
            "category": "Cloud hosting",
            "service_description": "Hosts customer portal and ERP",
            "business_owner": "Head of IT Operations",
            "data_sensitivity": "Regulated",
            "data_types": "customer;payment",
            "system_access": "Privileged",
            "dependency_impact": "4",
            "replaceability": "Very hard",
            "subcontractor_use": "Yes",
            "assessment_status": "Assessed",
            "current_assessment_id": "ASMT-001",
            "next_review_date": "2027-05-18",
            "material_change_flag": "No"
        }

    def tearDown(self):
        """Remove temporary test files."""

        self.temp_dir.cleanup()

    def write_csv(self, records, columns=None):
        """Create a CSV file with the supplied records."""

        if columns is None:
            columns = self.columns

        with self.csv_file.open(
            mode="w",
            encoding="utf-8",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=columns
            )

            writer.writeheader()
            writer.writerows(records)

        return self.csv_file

    def test_import_valid_vendor(self):
        """A valid vendor should be accepted."""

        self.write_csv([self.valid_vendor])

        result = import_vendor_csv(self.csv_file)

        self.assertEqual(len(result["valid_records"]), 1)
        self.assertEqual(len(result["rejected_records"]), 0)
        self.assertEqual(result["file_errors"], [])

    def test_reject_invalid_vendor(self):
        """A vendor with an invalid category should be rejected."""

        invalid_vendor = self.valid_vendor.copy()
        invalid_vendor["category"] = "Unknown"

        self.write_csv([invalid_vendor])

        result = import_vendor_csv(self.csv_file)

        self.assertEqual(len(result["valid_records"]), 0)
        self.assertEqual(len(result["rejected_records"]), 1)

        errors = result["rejected_records"][0]["errors"]

        self.assertTrue(
            any("category" in error for error in errors)
        )

    def test_detect_duplicate_vendor_ids(self):
        """Duplicate vendor IDs should be detected."""

        first_vendor = self.valid_vendor.copy()

        second_vendor = self.valid_vendor.copy()
        second_vendor["vendor_name"] = "Duplicate Vendor"

        self.write_csv([
            first_vendor,
            second_vendor
        ])

        result = import_vendor_csv(self.csv_file)

        self.assertEqual(len(result["valid_records"]), 1)
        self.assertEqual(len(result["rejected_records"]), 1)
        self.assertEqual(len(result["duplicate_ids"]), 1)

        self.assertEqual(
            result["duplicate_ids"][0]["vendor_id"],
            "VEN-001"
        )

        self.assertEqual(
            result["duplicate_ids"][0]["first_row"],
            2
        )

        self.assertEqual(
            result["duplicate_ids"][0]["duplicate_row"],
            3
        )

    def test_missing_file(self):
        """A missing CSV file should produce a file error."""

        missing_file = self.test_folder / "missing.csv"

        result = import_vendor_csv(missing_file)

        self.assertEqual(len(result["file_errors"]), 1)

        self.assertIn(
            "File not found",
            result["file_errors"][0]
        )

    def test_incorrect_csv_headings(self):
        """A CSV with incorrect headings should be rejected."""

        incorrect_columns = [
            "vendor_id",
            "vendor_name",
            "category"
        ]

        # Only write fields included in the incorrect headings.
        incomplete_vendor = {
            column: self.valid_vendor[column]
            for column in incorrect_columns
        }

        self.write_csv(
            [incomplete_vendor],
            columns=incorrect_columns
        )

        result = import_vendor_csv(self.csv_file)

        self.assertEqual(len(result["file_errors"]), 1)

        self.assertIn(
            "Missing columns",
            result["file_errors"][0]
        )

    def test_reject_extra_csv_values(self):
        """A row with more values than its header should be rejected."""

        with self.csv_file.open(
            mode="w",
            encoding="utf-8",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow(self.columns)

            writer.writerow([
                self.valid_vendor[column]
                for column in self.columns
            ] + ["EXTRA VALUE"])

        result = import_vendor_csv(self.csv_file)

        self.assertEqual(len(result["valid_records"]), 0)
        self.assertEqual(len(result["rejected_records"]), 1)

        errors = result["rejected_records"][0]["errors"]

        self.assertTrue(
            any(
                "more values" in error
                for error in errors
            )
        )

    def test_empty_csv_file(self):
        """An empty CSV file should report a missing header."""

        self.csv_file.write_text(
            "",
            encoding="utf-8"
        )

        result = import_vendor_csv(self.csv_file)

        self.assertEqual(len(result["file_errors"]), 1)

        self.assertIn(
            "no header",
            result["file_errors"][0]
        )


if __name__ == "__main__":
    unittest.main()
