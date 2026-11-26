"""CSV file boundary and reproducible date tests."""

import csv
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from src.config import DEFAULT_DATA_DIR, SOURCE_TABLES
from src.loader import get_table_inventory, load_report_date, load_source_tables, load_table
from src.schema import SCHEMAS


class LoaderTests(unittest.TestCase):
    def test_all_approved_sources_load_with_original_headers(self):
        data = load_source_tables(DEFAULT_DATA_DIR)
        self.assertEqual(set(data), set(SOURCE_TABLES))
        for name, table in data.items():
            with self.subTest(table=name):
                self.assertTrue(table.loaded)
                self.assertEqual(table.headers, list(SCHEMAS[name].columns))
                self.assertEqual(table.issues, [])

    def test_fixture_counts(self):
        data = load_source_tables(DEFAULT_DATA_DIR)
        for name, count in (("vendor", 10), ("question", 24), ("assessment", 11)):
            with self.subTest(table=name):
                self.assertEqual(len(data[name].rows), count)

    def test_inventory_separates_references(self):
        data = load_source_tables(DEFAULT_DATA_DIR)
        inventory = get_table_inventory(data, include_references=True)
        self.assertEqual(len(data), 12)
        self.assertEqual(len(inventory), 20)
        by_name = {item["table"]: item for item in inventory}
        self.assertEqual(by_name["expected_risk"]["classification"], "expected-output")
        self.assertEqual(by_name["invalid_vendor_cases"]["classification"], "negative-test")
        self.assertEqual(by_name["validation_results"]["classification"], "reference")
        self.assertEqual(by_name["response"]["primary_identifier"], "assessment_id, question_id")

    def test_default_and_custom_dates(self):
        self.assertEqual(load_report_date(), date(2026, 11, 18))
        self.assertEqual(load_report_date("2027-02-28"), date(2027, 2, 28))
        for value in ("2026-2-01", "2026-02-30", "20261118", "", "2026-11-18T00:00:00"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                load_report_date(value)

    def test_preserves_columns_empty_cells_and_unicode(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "example.csv"
            path.write_text('Exact Header,Optional\n"Fictional café, Ltd",\n', encoding="utf-8")
            table = load_table(path)
            self.assertEqual(table.headers, ["Exact Header", "Optional"])
            self.assertEqual(table.rows, [{"Exact Header": "Fictional café, Ltd", "Optional": ""}])
            self.assertEqual(table.row_numbers, [2])

    def test_missing_unreadable_and_invalid_utf8_files(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "vendor.csv"
            missing = load_table(path)
            self.assertFalse(missing.loaded)
            self.assertIn("must exist", missing.issues[0].rule)
            path.write_bytes(b"vendor_id\n\xff\n")
            invalid = load_table(path)
            self.assertFalse(invalid.loaded)
            self.assertTrue(any(i.field == "encoding" for i in invalid.issues))
            with patch.object(Path, "open", side_effect=PermissionError("test denied read")):
                unreadable = load_table(path)
            self.assertFalse(unreadable.loaded)
            self.assertIn("must be readable", unreadable.issues[0].rule)

    def test_header_and_csv_shape_errors(self):
        cases = (
            ("", "header"),
            ("vendor_id,\nVEN-001,x\n", "Header names must not be empty"),
            ("vendor_id,vendor_id\nVEN-001,VEN-002\n", "Header names must be unique"),
            ("vendor_id\nVEN-001,extra\n", "Row has more cells than headers"),
            ("vendor_id,vendor_name\nVEN-001\n", "Every row must match the header width"),
            ('vendor_id\n"unterminated\n', "CSV syntax must be readable"),
        )
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "vendor.csv"
            for content, rule in cases:
                with self.subTest(content=content):
                    path.write_text(content, encoding="utf-8")
                    table = load_table(path)
                    self.assertTrue(any(rule in i.rule.lower() or rule in i.rule for i in table.issues))

    def test_missing_required_header_is_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "vendor.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                csv.writer(handle).writerow([c for c in SCHEMAS["vendor"].columns if c != "category"])
            table = load_table(path)
            self.assertTrue(any(i.field == "category" and i.row == 1 for i in table.issues))


if __name__ == "__main__":
    unittest.main()
