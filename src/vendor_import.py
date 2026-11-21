

import csv
from pathlib import Path

from validation import (
    validate_vendor_fields,
    find_duplicate_vendor_ids
)


# These headings must match the vendor data dictionary exactly.
EXPECTED_COLUMNS = [
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


def import_vendor_csv(file_path):
    """
    Import and validate vendor records from a CSV file.

    Returns a dictionary containing:
        valid_records: Records that pass validation.
        rejected_records: Records that fail validation.
        duplicate_ids: Information about duplicate vendor IDs.
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

            # 4. Check whether the headings match the expected schema.
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

            # 5. Read all records and preserve their CSV row numbers.
            records = []

            for row_number, row in enumerate(reader, start=2):

                # Extra values beyond the expected headings.
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

                records.append({
                    "row_number": row_number,
                    "record": row
                })

            # 6. Detect duplicate vendor IDs.
            vendor_ids = [
                item["record"].get("vendor_id", "")
                for item in records
            ]

            duplicates = find_duplicate_vendor_ids(vendor_ids)

            # The duplicate detection function counts data rows
            # starting at 1. CSV data rows start at 2 because
            # row 1 contains the headings.
            duplicate_rows = {
                item["duplicate_row"]: item
                for item in duplicates
            }

            for duplicate in duplicates:
                result["duplicate_ids"].append({
                    "vendor_id": duplicate["vendor_id"],
                    "first_row": duplicate["first_row"] + 1,
                    "duplicate_row": duplicate["duplicate_row"] + 1
                })

            # 7. Validate each record.
            for item in records:

                row_number = item["row_number"]
                record = item["record"]

                errors = []

                # Convert CSV row number to data-row number
                # for matching duplicate detection results.
                data_row_number = row_number - 1

                if data_row_number in duplicate_rows:
                    duplicate = duplicate_rows[data_row_number]

                    errors.append(
                        f"Duplicate vendor ID '{duplicate['vendor_id']}'. "
                        f"First occurrence is on CSV row "
                        f"{duplicate['first_row'] + 1}."
                    )

                # Run the normal field validation.
                field_errors = validate_vendor_fields(record)

                errors.extend(field_errors)

                # Store valid or rejected record.
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
