import sys
import unittest
import tempfile
import csv

from pathlib import Path

# Allow tests to import modules from the src folder.
sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src")
)

from questionnaire import (
    load_question_bank,
    validate_question,
    find_duplicate_question_ids,
    parse_answer_choices,
    validate_question_bank
)


class TestQuestionnaire(unittest.TestCase):

    def setUp(self):
        """Create a valid sample question for testing."""

        self.valid_question = {
            "question_id": "AM-01",
            "Domain": "Access management",
            "Wording": "Is MFA enabled for privileged accounts?",
            "Answer choices": (
                "All privileged accounts = 0 | "
                "Some privileged accounts = 3 | "
                "None = 4"
            ),
            "Weight / severity": "5",
            "Evidence artifact and period": "MFA configuration report",
            "Reviewer acceptance criteria": "Verify all privileged accounts.",
            "Critical failure?": "Yes"
        }
    def test_valid_question(self):
        """A correctly completed question should pass validation."""

        errors = validate_question(self.valid_question)

        self.assertEqual(errors, [])

    def test_missing_question_id(self):
        """A question without an ID should be rejected."""

        question = self.valid_question.copy()
        question["question_id"] = ""

        errors = validate_question(question)

        self.assertIn("Question ID is required.", errors)

    def test_invalid_domain(self):
        """A question with an unapproved domain should be rejected."""

        question = self.valid_question.copy()
        question["Domain"] = "Human Resources"

        errors = validate_question(question)

        self.assertTrue(any("Invalid domain" in error for error in errors))

    def test_invalid_weight(self):
        """A question weight outside the approved range should be rejected."""

        question = self.valid_question.copy()
        question["Weight / severity"] = "8"

        errors = validate_question(question)

        self.assertIn(
            "Question weight must be between 1 and 5.",
            errors
        )

    def test_invalid_critical_failure_flag(self):
        """Critical failure must be Yes or No."""

        question = self.valid_question.copy()
        question["Critical failure?"] = "Maybe"

        errors = validate_question(question)

        self.assertIn(
            "Critical failure must be Yes or No.",
            errors
        )
    def test_missing_question_wording(self):
        """Question wording must not be empty."""

        question = self.valid_question.copy()
        question["Wording"] = ""

        errors = validate_question(question)

        self.assertIn("Question wording is required.", errors)

    def test_invalid_answer_choice_risk_value(self):
        """Risk values must be between 0 and 4."""

        result = parse_answer_choices(
            "All accounts protected = 5"
        )

        self.assertEqual(len(result["choices"]), 0)
        self.assertTrue(len(result["errors"]) > 0)

    def test_parse_valid_answer_choices(self):
        """Valid answer choices should be converted into structured records."""

        result = parse_answer_choices(
            "All accounts protected = 0 | "
            "Some accounts protected = 3 | "
            "None protected = 4"
        )

        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["choices"]), 3)
        self.assertEqual(result["choices"][0]["risk_value"], 0)
        self.assertEqual(result["choices"][2]["risk_value"], 4)

    def test_duplicate_question_ids(self):
        """Duplicate question IDs should be detected."""

        questions = [
            self.valid_question.copy(),
            self.valid_question.copy()
        ]

        duplicates = find_duplicate_question_ids(questions)

        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0]["question_id"], "AM-01")
        self.assertEqual(duplicates[0]["first_row"], 2)
        self.assertEqual(duplicates[0]["duplicate_row"], 3)

    def test_validate_question_bank(self):
        """A valid question bank should pass validation."""

        questions = [
            self.valid_question.copy()
        ]

        result = validate_question_bank(questions)

        self.assertTrue(result["valid"])
        self.assertEqual(result["question_count"], 1)
        self.assertEqual(result["errors"], [])

    def test_load_actual_question_bank(self):
        """The actual research question bank should load successfully."""

        project_root = Path(__file__).resolve().parents[1]

        question_bank_path = (
            project_root
            / "01-research-and-risk-assessment"
            / "question_bank.csv"
        )

        result = load_question_bank(question_bank_path)

        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["questions"]), 24)
        self.assertEqual(
            result["questions"][0]["question_id"],
            "AM-01"
        )
    def test_missing_question_bank_file(self):
        """A missing question bank file should return an error."""

        result = load_question_bank("nonexistent_question_bank.csv")

        self.assertEqual(result["questions"], [])
        self.assertTrue(len(result["errors"]) > 0)

    def test_empty_question_bank_file(self):
        """An empty CSV file should report that the header is missing."""

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            encoding="utf-8",
            delete=False
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)

        try:
            result = load_question_bank(temporary_path)

            self.assertEqual(result["questions"], [])
            self.assertIn(
                "Question bank has no header row.",
                result["errors"]
            )

        finally:
            temporary_path.unlink(missing_ok=True)

    def test_invalid_question_bank_headings(self):
        """A CSV with incorrect headings should be rejected."""

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            encoding="utf-8",
            newline="",
            delete=False
        ) as temporary_file:
            writer = csv.writer(temporary_file)
            writer.writerow(["question_id", "Domain", "Wording"])
            temporary_path = Path(temporary_file.name)

        try:
            result = load_question_bank(temporary_path)

            self.assertEqual(result["questions"], [])
            self.assertTrue(len(result["errors"]) > 0)

        finally:
            temporary_path.unlink(missing_ok=True)