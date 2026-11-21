
"""Load and validate the vendor risk assessment question bank."""

import csv
from pathlib import Path


EXPECTED_COLUMNS = [
    "question_id",
    "Domain",
    "Wording",
    "Answer choices",
    "Weight / severity",
    "Evidence artifact and period",
    "Reviewer acceptance criteria",
    "Critical failure?"
]


ALLOWED_DOMAINS = {
    "Access management",
    "Data protection",
    "Incident notification",
    "Continuity and recovery",
    "Subcontractors",
    "Governance"
}

ALLOWED_CRITICAL_FLAGS = {"Yes", "No"}


def load_question_bank(file_path):
    """Load questions from a CSV file and validate its headings."""

    path = Path(file_path)

    if not path.exists():
        return {
            "questions": [],
            "errors": [f"Question bank not found: {path}"]
        }

    if not path.is_file():
        return {
            "questions": [],
            "errors": [f"Question bank path is not a file: {path}"]
        }

    try:
        with path.open(
            mode="r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                return {
                    "questions": [],
                    "errors": ["Question bank has no header row."]
                }

            missing_columns = [
                column for column in EXPECTED_COLUMNS
                if column not in reader.fieldnames
            ]

            unexpected_columns = [
                column for column in reader.fieldnames
                if column not in EXPECTED_COLUMNS
            ]

            if missing_columns or unexpected_columns:
                errors = []

                if missing_columns:
                    errors.append(
                        f"Missing columns: {missing_columns}"
                    )

                if unexpected_columns:
                    errors.append(
                        f"Unexpected columns: {unexpected_columns}"
                    )

                return {
                    "questions": [],
                    "errors": errors
                }

            questions = list(reader)

            return {
                "questions": questions,
                "errors": []
            }

    except (OSError, UnicodeDecodeError, csv.Error) as error:
        return {
            "questions": [],
            "errors": [f"Could not read question bank: {error}"]
        }

def validate_question(question):
    """Validate the required fields of one questionnaire record."""

    errors = []

    if not isinstance(question, dict):
        return ["Question must be a dictionary."]

    # Check question ID
    question_id = question.get("question_id", "").strip()

    if not question_id:
        errors.append("Question ID is required.")

    elif len(question_id) != 5 or question_id[2] != "-":
        errors.append(
            f"Invalid question ID format: {question_id}"
        )

    # Check domain
    domain = question.get("Domain", "").strip()

    if domain not in ALLOWED_DOMAINS:
        errors.append(f"Invalid domain: {domain}")

    # Check question wording
    wording = question.get("Wording", "").strip()

    if not wording:
        errors.append("Question wording is required.")

    # Check answer choices
    answer_choices = question.get("Answer choices", "").strip()

    if not answer_choices:
        errors.append("Answer choices are required.")

    # Check question weight
    weight = question.get("Weight / severity", "").strip()

    try:
        weight_value = int(weight)

        if weight_value < 1 or weight_value > 5:
            errors.append("Question weight must be between 1 and 5.")

    except (ValueError, TypeError):
        errors.append("Question weight must be a whole number.")

    # Check evidence requirements
    evidence = question.get(
        "Evidence artifact and period", ""
    ).strip()

    if not evidence:
        errors.append("Evidence artifact and period is required.")

    # Check reviewer acceptance criteria
    criteria = question.get(
        "Reviewer acceptance criteria", ""
    ).strip()

    if not criteria:
        errors.append("Reviewer acceptance criteria is required.")

    # Check critical failure flag
    critical_flag = question.get("Critical failure?", "").strip()

    if critical_flag not in ALLOWED_CRITICAL_FLAGS:
        errors.append("Critical failure must be Yes or No.")

    return errors

def find_duplicate_question_ids(questions):
    """Find duplicate question IDs and report their row positions."""

    seen = {}
    duplicates = []

    for row_number, question in enumerate(questions, start=2):
        question_id = question.get("question_id", "").strip()

        if not question_id:
            continue

        if question_id in seen:
            duplicates.append({
                "question_id": question_id,
                "first_row": seen[question_id],
                "duplicate_row": row_number
            })
        else:
            seen[question_id] = row_number

    return duplicates

def parse_answer_choices(answer_choices):
    """Convert answer choices into structured answer and risk-value records."""

    parsed_choices = []
    errors = []

    if not isinstance(answer_choices, str) or not answer_choices.strip():
        return {
            "choices": [],
            "errors": ["Answer choices must not be empty."]
        }

    choices = answer_choices.split("|")

    for position, choice in enumerate(choices, start=1):
        choice = choice.strip()

        if "=" not in choice:
            errors.append(
                f"Choice {position} does not contain an '=' separator."
            )
            continue

        answer_text, risk_text = choice.rsplit("=", 1)

        answer_text = answer_text.strip()
        risk_text = risk_text.strip()

        if not answer_text:
            errors.append(
                f"Choice {position} has no answer description."
            )
            continue

        try:
            risk_value = int(risk_text)

        except ValueError:
            errors.append(
                f"Choice {position} has an invalid risk value: {risk_text}"
            )
            continue

        if risk_value < 0 or risk_value > 4:
            errors.append(
                f"Choice {position} risk value must be between 0 and 4."
            )
            continue

        parsed_choices.append({
            "answer": answer_text,
            "risk_value": risk_value
        })

    return {
        "choices": parsed_choices,
        "errors": errors
    }

def validate_question_bank(questions):
    """Run all question-bank validation checks."""

    errors = []

    if not isinstance(questions, list):
        return {
            "valid": False,
            "question_count": 0,
            "errors": ["Question bank must be a list."]
        }

    # Validate each question.
    for row_number, question in enumerate(questions, start=2):

        question_errors = validate_question(question)

        for error in question_errors:
            errors.append({
                "row": row_number,
                "question_id": question.get("question_id", ""),
                "error": error
            })

        # Validate the answer-choice structure.
        if isinstance(question, dict):
            parsed = parse_answer_choices(
                question.get("Answer choices", "")
            )

            for error in parsed["errors"]:
                errors.append({
                    "row": row_number,
                    "question_id": question.get("question_id", ""),
                    "error": error
                })

    # Check duplicate question IDs.
    duplicates = find_duplicate_question_ids(questions)

    for duplicate in duplicates:
        errors.append({
            "row": duplicate["duplicate_row"],
            "question_id": duplicate["question_id"],
            "error": (
                f"Duplicate question ID. "
                f"First occurrence is on row {duplicate['first_row']}."
            )
        })

    return {
        "valid": len(errors) == 0,
        "question_count": len(questions),
        "errors": errors
    }
