"""Terminal-to-report checks using temporary output folders and fixture copies."""

import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.config import DEFAULT_DATA_DIR, PHASE_NOTICE, REPOSITORY_ROOT, SOURCE_TABLES


class Phase1SmokeTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "src.cli", *map(str, args)],
                              cwd=REPOSITORY_ROOT, capture_output=True, text=True, check=False)

    def test_help_and_inventory(self):
        help_result = self.run_cli("--help")
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        inventory = self.run_cli("inventory")
        self.assertEqual(inventory.returncode, 0, inventory.stderr)
        for name in SOURCE_TABLES:
            self.assertIn(name + ".csv", inventory.stdout)
        for label in ("source", "expected-output", "negative-test", "reference"):
            self.assertIn(label, inventory.stdout)

    def test_report_round_trip_default_and_custom_dates(self):
        with tempfile.TemporaryDirectory() as folder:
            for args, expected in (((), "2026-11-18"), (("--as-of", "2027-01-20"), "2027-01-20")):
                with self.subTest(date=expected):
                    result = self.run_cli("validate", "--reports-dir", folder, *args)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    report = json.loads((Path(folder) / "validation_report.json").read_text())
                    self.assertEqual(report["status"], "PASS")
                    self.assertEqual(report["report_date"], expected)
                    self.assertEqual(report["summary"]["files_loaded"], 12)
                    self.assertEqual(report["summary"]["valid_tables"], 12)
                    self.assertEqual(report["errors"], [])
                    self.assertEqual(len(report["inventory"]), 12)
                    self.assertEqual(report["research_fixture_validator"]["status"], "NOT_RUN_BY_THIS_COMMAND")
                    self.assertIn(PHASE_NOTICE, (Path(folder) / "validation_report.md").read_text())

    def test_cli_rejects_duplicate_and_retains_baseline_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            data_dir = Path(folder) / "data"
            reports_dir = Path(folder) / "reports"
            shutil.copytree(DEFAULT_DATA_DIR, data_dir)
            vendor = data_dir / "vendor.csv"
            with vendor.open(encoding="utf-8", newline="") as handle:
                first = next(csv.reader(handle))
                row = next(csv.reader(handle))
            with vendor.open("a", encoding="utf-8", newline="") as handle:
                csv.writer(handle).writerow(row)
            result = self.run_cli("validate", "--data-dir", data_dir, "--reports-dir", reports_dir)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            report = json.loads((reports_dir / "validation_report.json").read_text())
            self.assertEqual(report["summary"]["duplicate_records"], 1)
            self.assertEqual(next(t["row_count"] for t in report["inventory"] if t["table"] == "vendor"), 11)
            issue = next(i for i in report["errors"] if i["category"] == "duplicates")
            self.assertEqual(issue["row"], 12)
            self.assertIn("row 2", issue["rule"])
            self.assertEqual(first[0], "vendor_id")

    def test_missing_sources_report_errors_without_traceback(self):
        with tempfile.TemporaryDirectory() as folder:
            result = self.run_cli("validate", "--data-dir", Path(folder) / "absent",
                                  "--reports-dir", Path(folder) / "reports")
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            report = json.loads((Path(folder) / "reports/validation_report.json").read_text())
            self.assertEqual(report["summary"]["files_loaded"], 0)
            self.assertEqual(report["summary"]["errors"], 12)

    def test_bad_report_date_is_actionable(self):
        result = self.run_cli("validate", "--as-of", "2026-02-30")
        self.assertEqual(result.returncode, 2)
        self.assertIn("not a real calendar date", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_sample_data_unchanged_after_loading_validation_and_reports(self):
        def hashes():
            return {str(p.relative_to(DEFAULT_DATA_DIR)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in DEFAULT_DATA_DIR.rglob("*") if p.is_file()}

        before = hashes()
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(self.run_cli("inventory").returncode, 0)
            result = self.run_cli("validate", "--data-dir", DEFAULT_DATA_DIR,
                                  "--reports-dir", folder, "--as-of", "2026-11-18")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(hashes(), before)

    def test_reports_cannot_be_written_into_source_data(self):
        with tempfile.TemporaryDirectory() as folder:
            data_dir = Path(folder) / "data"
            shutil.copytree(DEFAULT_DATA_DIR, data_dir)
            result = self.run_cli("validate", "--data-dir", data_dir,
                                  "--reports-dir", data_dir / "reports")
            self.assertEqual(result.returncode, 2)
            self.assertIn("outside the source data directory", result.stderr)
            self.assertFalse((data_dir / "reports").exists())


if __name__ == "__main__":
    unittest.main()
