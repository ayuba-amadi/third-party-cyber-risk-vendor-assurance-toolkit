


import csv
from pathlib import Path

from src.assessment import (
    validate_assessment_record,
    validate_assessment_id,
)


EXPECTED_ASSESSMENT_COLUMNS = [
    "assessment_id",
    "vendor_id",
    "version_no",
    "assessment_date",
    "trigger",
    "assessor_role",
    "status",
    "supersedes_id",
]


def find_duplicate_assessment_ids(assessments):
    """Find assessment IDs that occur more than once."""
    seen = set()
    duplicates = set()

    for assessment in assessments:
        assessment_id = assessment.get("assessment_id")

        if not validate_assessment_id(assessment_id):
            continue

        if assessment_id in seen:
            duplicates.add(assessment_id)
        else:
            seen.add(assessment_id)

    return duplicates


def import_assessment_csv(file_path):
    """
    Import assessment records from a CSV file.

    Returns:
        valid_records
        rejected_records
        duplicate_ids
        file_errors
    """
    valid_records = []
    rejected_records = []
    duplicate_ids = []
    file_errors = []

    path = Path(file_path)

    if not path.exists():
        file_errors.append(f"File not found: {file_path}")
        return valid_records, rejected_records, duplicate_ids, file_errors

    if not path.is_file():
        file_errors.append(f"Path is not a file: {file_path}")
        return valid_records, rejected_records, duplicate_ids, file_errors

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)

            if reader.fieldnames is None:
                file_errors.append("CSV file is empty or has no header.")
                return valid_records, rejected_records, duplicate_ids, file_errors

            if len(reader.fieldnames) != len(set(reader.fieldnames)):
                file_errors.append("CSV contains duplicate column headings.")
                return valid_records, rejected_records, duplicate_ids, file_errors

            missing_columns = [
                column for column in EXPECTED_ASSESSMENT_COLUMNS
                if column not in reader.fieldnames
            ]

            unexpected_columns = [
                column for column in reader.fieldnames
                if column not in EXPECTED_ASSESSMENT_COLUMNS
            ]

            if missing_columns or unexpected_columns:
                if missing_columns:
                    file_errors.append(
                        "Missing CSV columns: " + ", ".join(missing_columns)
                    )

                if unexpected_columns:
                    file_errors.append(
                        "Unexpected CSV columns: " + ", ".join(unexpected_columns)
                    )

                return valid_records, rejected_records, duplicate_ids, file_errors

            rows = list(reader)

            # Identify rows with extra or missing CSV values.
            structurally_valid_rows = []

            for row_number, row in enumerate(rows, start=2):

                if None in row:
                    rejected_records.append({
                        "row_number": row_number,
                        "record": row,
                        "errors": ["CSV row contains extra values."]
                    })
                    continue

                missing_values = [
                    column
                    for column in EXPECTED_ASSESSMENT_COLUMNS
                    if row.get(column) is None
                ]

                if missing_values:
                    rejected_records.append({
                        "row_number": row_number,
                        "record": row,
                        "errors": [
                            "CSV row contains missing values: "
                            + ", ".join(missing_values)
                        ]
                    })
                    continue

                structurally_valid_rows.append(row)

            # Identify duplicate assessment IDs.
            duplicates = find_duplicate_assessment_ids(
                structurally_valid_rows
            )
            duplicate_ids = sorted(duplicates)

            seen_ids = set()

            for row_number, row in enumerate(rows, start=2):

                if None in row:
                    continue

                if any(
                    row.get(column) is None
                    for column in EXPECTED_ASSESSMENT_COLUMNS
                ):
                    continue

                # Convert version_no from CSV text to integer.
                version_no = row.get("version_no")

                if isinstance(version_no, str) and version_no.strip().isdigit():
                    row["version_no"] = int(version_no.strip())

                assessment_id = row.get("assessment_id")

                # Reject later occurrences of duplicate IDs.
                if validate_assessment_id(assessment_id):
                    if assessment_id in seen_ids:
                        rejected_records.append({
                            "row_number": row_number,
                            "record": row,
                            "errors": [
                                f"Duplicate assessment_id: {assessment_id}"
                            ]
                        })
                        continue

                    seen_ids.add(assessment_id)

                # Validate the assessment record.
                errors = validate_assessment_record(row)

                if errors:
                    rejected_records.append({
                        "row_number": row_number,
                        "record": row,
                        "errors": errors
                    })
                else:
                    valid_records.append(row)

    except UnicodeDecodeError:
        file_errors.append("CSV file must use UTF-8 encoding.")

    except csv.Error as error:
        file_errors.append(f"CSV reading error: {error}")

    except OSError as error:
        file_errors.append(f"File access error: {error}")

    return valid_records, rejected_records, duplicate_ids, file_errors
