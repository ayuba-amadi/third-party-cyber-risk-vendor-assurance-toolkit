


import csv
from pathlib import Path

from src.evidence import (
    validate_evidence_record,
    validate_evidence_id
)


# These headings must match the evidence data dictionary.
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


def import_evidence_csv(file_path):
    """
    Import and validate evidence records from a CSV file.

    Returns:
        valid_records: Records that pass validation.
        rejected_records: Records that fail validation.
        duplicate_ids: Information about duplicate evidence IDs.
        file_errors: Errors affecting the CSV file as a whole.
    """

    result = {
        "valid_records": [],
        "rejected_records": [],
        "duplicate_ids": [],
        "file_errors": []
    }

    path = Path(file_path)

    # 1. Check whether the file exists.
    if not path.exists():
        result["file_errors"].append(
            f"File not found: {path}"
        )
        return result

    if not path.is_file():
        result["file_errors"].append(
            f"The supplied path is not a file: {path}"
        )
        return result

    try:
        with path.open(
            mode="r",
            encoding="utf-8-sig",
            newline=""
        ) as csv_file:

            reader = csv.DictReader(csv_file)

            # 2. Check whether the CSV has a header.
            if reader.fieldnames is None:
                result["file_errors"].append(
                    "The CSV file is empty or has no header row."
                )
                return result

            # 3. Check for duplicate column headings.
            if len(reader.fieldnames) != len(set(reader.fieldnames)):
                result["file_errors"].append(
                    "The CSV contains duplicate column headings."
                )
                return result

            # 4. Check whether headings match the expected schema.
            missing_columns = [
                column
                for column in EXPECTED_COLUMNS
                if column not in reader.fieldnames
            ]

            unexpected_columns = [
                column
                for column in reader.fieldnames
                if column not in EXPECTED_COLUMNS
            ]

            if missing_columns or unexpected_columns:

                if missing_columns:
                    result["file_errors"].append(
                        "Missing columns: "
                        + ", ".join(missing_columns)
                    )

                if unexpected_columns:
                    result["file_errors"].append(
                        "Unexpected columns: "
                        + ", ".join(unexpected_columns)
                    )

                return result

            # 5. Read records and preserve CSV row numbers.
            records = []

            for row_number, row in enumerate(reader, start=2):

                # Reject rows containing more values than headings.
                if None in row:
                    result["rejected_records"].append({
                        "row_number": row_number,
                        "record": row,
                        "errors": [
                            "This row contains more values "
                            "than the CSV header defines."
                        ]
                    })
                    continue

                # Reject rows containing fewer values than headings.
                missing_values = [
                    column
                    for column, value in row.items()
                    if value is None
                ]

                if missing_values:
                    result["rejected_records"].append({
                        "row_number": row_number,
                        "record": row,
                        "errors": [
                            "This row contains fewer values "
                            "than the CSV header defines. "
                            "Missing values for: "
                            + ", ".join(missing_values)
                        ]
                    })
                    continue

                records.append({
                    "row_number": row_number,
                    "record": row
                })

            # 6. Detect duplicate evidence IDs.
            evidence_id_rows = {}

            for item in records:
                evidence_id = item["record"].get(
                    "evidence_id", ""
                )

                if validate_evidence_id(evidence_id):
                    evidence_id_rows.setdefault(
                        evidence_id, []
                    ).append(item["row_number"])

            duplicate_rows = set()

            for evidence_id, row_numbers in evidence_id_rows.items():

                if len(row_numbers) > 1:
                    first_row = row_numbers[0]

                    for duplicate_row in row_numbers[1:]:
                        result["duplicate_ids"].append({
                            "evidence_id": evidence_id,
                            "first_row": first_row,
                            "duplicate_row": duplicate_row
                        })

                        duplicate_rows.add(duplicate_row)

            # 7. Validate each evidence record.
            for item in records:

                row_number = item["row_number"]
                record = item["record"]

                errors = []

                if row_number in duplicate_rows:

                    for duplicate in result["duplicate_ids"]:

                        if duplicate["duplicate_row"] == row_number:
                            errors.append(
                                f"Duplicate evidence ID "
                                f"'{duplicate['evidence_id']}'. "
                                f"First occurrence is on CSV row "
                                f"{duplicate['first_row']}."
                            )

                field_errors = validate_evidence_record(record)
                errors.extend(field_errors)

                if errors:
                    result["rejected_records"].append({
                        "row_number": row_number,
                        "record": record,
                        "errors": errors
                    })
                else:
                    result["valid_records"].append(record)

    except UnicodeDecodeError:
        result["file_errors"].append(
            "The CSV file could not be decoded as UTF-8."
        )

    except csv.Error as error:
        result["file_errors"].append(
            f"CSV reading error: {error}"
        )

    except OSError as error:
        result["file_errors"].append(
            f"File access error: {error}"
        )

    return result
