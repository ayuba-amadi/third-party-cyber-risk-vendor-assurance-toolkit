
import csv
from pathlib import Path

from src.response import validate_response_record


EXPECTED_RESPONSE_COLUMNS = [
    "assessment_id",
    "question_id",
    "vendor_claim",
    "reviewer_verified",
    "verified_answer",
    "reviewer_note",
]


def find_duplicate_response_keys(records):
    """Find duplicate assessment_id and question_id combinations."""

    seen = set()
    duplicates = []

    for record in records:
        assessment_id = record.get("assessment_id")
        question_id = record.get("question_id")

        if not assessment_id or not question_id:
            continue

        key = (assessment_id, question_id)

        if key in seen:
            if key not in duplicates:
                duplicates.append(key)
        else:
            seen.add(key)

    return duplicates


def import_response_csv(file_path):
    """
    Import and validate response records from a CSV file.

    Returns valid records, rejected records, duplicate keys,
    and file-level errors.
    """

    valid_records = []
    rejected_records = []
    duplicate_keys = []
    file_errors = []

    path = Path(file_path)

    if not path.exists():
        return {
            "valid_records": [],
            "rejected_records": [],
            "duplicate_keys": [],
            "file_errors": ["File does not exist."],
        }

    if not path.is_file():
        return {
            "valid_records": [],
            "rejected_records": [],
            "duplicate_keys": [],
            "file_errors": ["The supplied path is not a file."],
        }

    try:
        with path.open(
            mode="r",
            encoding="utf-8-sig",
            newline=""
        ) as csv_file:

            reader = csv.DictReader(csv_file)

            if not reader.fieldnames:
                file_errors.append("CSV file is empty or has no header.")
                return {
                    "valid_records": [],
                    "rejected_records": [],
                    "duplicate_keys": [],
                    "file_errors": file_errors,
                }

            headers = reader.fieldnames

            if len(headers) != len(set(headers)):
                file_errors.append("CSV contains duplicate column names.")
                return {
                    "valid_records": [],
                    "rejected_records": [],
                    "duplicate_keys": [],
                    "file_errors": file_errors,
                }

            missing_columns = [
                column for column in EXPECTED_RESPONSE_COLUMNS
                if column not in headers
            ]

            unexpected_columns = [
                column for column in headers
                if column not in EXPECTED_RESPONSE_COLUMNS
            ]

            if missing_columns:
                file_errors.append(
                    "Missing required columns: "
                    + ", ".join(missing_columns)
                )

            if unexpected_columns:
                file_errors.append(
                    "Unexpected columns: "
                    + ", ".join(unexpected_columns)
                )

            if file_errors:
                return {
                    "valid_records": [],
                    "rejected_records": [],
                    "duplicate_keys": [],
                    "file_errors": file_errors,
                }

            seen_keys = set()

            for row_number, row in enumerate(reader, start=2):

                if None in row:
                    rejected_records.append({
                        "row_number": row_number,
                        "record": row,
                        "errors": ["Row contains extra values."],
                    })
                    continue

                missing_values = [
                    column for column in EXPECTED_RESPONSE_COLUMNS
                    if row.get(column) is None
                ]

                if missing_values:
                    rejected_records.append({
                        "row_number": row_number,
                        "record": row,
                        "errors": [
                            "Row has missing values for columns: "
                            + ", ".join(missing_values)
                        ],
                    })
                    continue

                key = (
                    row.get("assessment_id"),
                    row.get("question_id"),
                )

                if key in seen_keys:
                    if key not in duplicate_keys:
                        duplicate_keys.append(key)

                    rejected_records.append({
                        "row_number": row_number,
                        "record": row,
                        "errors": [
                            "Duplicate response key: "
                            f"{key[0]} / {key[1]}."
                        ],
                    })
                    continue

                seen_keys.add(key)

                errors = validate_response_record(row)

                if errors:
                    rejected_records.append({
                        "row_number": row_number,
                        "record": row,
                        "errors": errors,
                    })
                else:
                    valid_records.append(row)

    except UnicodeDecodeError:
        file_errors.append("File must use UTF-8 encoding.")
    except csv.Error as error:
        file_errors.append(f"CSV reading error: {error}")
    except OSError as error:
        file_errors.append(f"File access error: {error}")

    return {
        "valid_records": valid_records,
        "rejected_records": rejected_records,
        "duplicate_keys": duplicate_keys,
        "file_errors": file_errors,
    }
