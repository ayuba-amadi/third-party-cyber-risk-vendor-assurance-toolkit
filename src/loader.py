"""Read-only UTF-8 CSV loading. No rows are silently removed or normalized."""

import csv
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .config import (
    DEFAULT_REPORT_DATE, EXPECTED_OUTPUT_FILES,
    NEGATIVE_TEST_FILES, PHASE2_SOURCE_TABLES, REFERENCE_FILES, SOURCE_TABLES,
)
from .schema import PHASE2_SCHEMAS, SCHEMAS, ValidationIssue


@dataclass
class Table:
    name: str
    path: Path
    headers: list[str] = field(default_factory=list)
    rows: list[dict] = field(default_factory=list)
    row_numbers: list[int] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)
    loaded: bool = False


def load_report_date(value=None):
    """Parse a strict YYYY-MM-DD date, defaulting to the frozen fixture date."""
    if value is None:
        return DEFAULT_REPORT_DATE
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("Report date must use YYYY-MM-DD, for example 2026-11-18.")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Report date {value!r} is not a real calendar date; use YYYY-MM-DD.") from exc


def load_table(path):
    """Return a Table with raw rows, physical CSV line numbers and file errors.

    Row 0 means a file-level issue; row 1 means the header. Even malformed rows
    remain available for inspection. A decoding/CSV failure marks loading incomplete.
    """
    path = Path(path)
    result = Table(path.stem, path)

    def issue(row, field_name, value, rule, correction, category="files", severity="ERROR"):
        result.issues.append(ValidationIssue(
            str(path), row, field_name, str(value), rule, severity, correction, category,
        ))

    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, strict=True)
            result.headers = reader.fieldnames or []
            if not result.headers:
                issue(1, "header", "", "CSV must contain a header row",
                      "Restore the approved column names as the first CSV row.", "missing_fields")
            for header in result.headers:
                if not header.strip():
                    issue(1, "header", header, "Header names must not be empty",
                          "Give every column its approved header name.", "missing_fields")
            if len(result.headers) != len(set(result.headers)):
                issue(1, "header", repr(result.headers), "Header names must be unique",
                      "Remove repeated header names; preserve each column's data.")
            schema = PHASE2_SCHEMAS.get(path.stem)
            if schema:
                for column in schema.columns:
                    if column not in result.headers:
                        issue(1, column, "", "Required column must exist",
                              f"Restore the {column} column from the approved schema.", "missing_fields")
                for column in result.headers:
                    if column and column not in schema.columns:
                        issue(1, column, column, "Column is outside the baseline schema",
                              "Check the spelling or document an approved schema extension.",
                              severity="WARNING")
            for row in reader:
                # line_num is the final physical line of this record, including multiline cells.
                number = reader.line_num
                result.rows.append(row)
                result.row_numbers.append(number)
                if None in row:
                    issue(number, "row", repr(row[None]), "Row has more cells than headers",
                          "Quote embedded commas or restore the missing column header.")
                for column, value in row.items():
                    if column is not None and value is None:
                        issue(number, column, "<absent cell>", "Every row must match the header width",
                              "Add the missing cell; use an empty cell for an optional value.", "missing_fields")
            result.loaded = True
    except FileNotFoundError:
        issue(0, "file", str(path), "Approved source file must exist",
              f"Restore {path.name} in the selected data directory.")
    except UnicodeError as exc:
        issue(0, "encoding", str(exc), "CSV must be valid UTF-8",
              "Save a copy of the file using UTF-8 encoding and retry.")
    except csv.Error as exc:
        issue(reader.line_num, "row", str(exc), "CSV syntax must be readable",
              "Correct CSV quoting and delimiters at the reported line.")
    except OSError as exc:
        issue(0, "file", str(exc), "Source file must be readable",
              "Check the path and file read permissions, then retry.")
    return result


def load_source_tables(data_dir, include_criticality_snapshot=False):
    """Load Phase 1 sources, optionally adding the Phase 2 snapshot source."""
    names = PHASE2_SOURCE_TABLES if include_criticality_snapshot else SOURCE_TABLES
    return {name: load_table(Path(data_dir) / f"{name}.csv") for name in names}


def get_table_inventory(data, include_references=False):
    """Describe sources and, optionally, known reference files without importing them."""
    inventory = []
    for name, table in data.items():
        inventory.append({
            "table": name, "file": str(table.path), "row_count": len(table.rows),
            "column_count": len(table.headers),
            "primary_identifier": ", ".join(PHASE2_SCHEMAS[name].primary_key),
            "classification": "source", "loaded": table.loaded,
        })
    if include_references and data:
        directory = next(iter(data.values())).path.parent
        groups = ((EXPECTED_OUTPUT_FILES, "expected-output"),
                  (NEGATIVE_TEST_FILES, "negative-test"), (REFERENCE_FILES, "reference"))
        for files, classification in groups:
            for filename in files:
                path = directory / filename
                if not path.exists():
                    continue
                table = load_table(path) if path.suffix == ".csv" else None
                inventory.append({
                    "table": path.stem, "file": str(path),
                    "row_count": len(table.rows) if table else None,
                    "column_count": len(table.headers) if table else None,
                    "primary_identifier": "", "classification": classification,
                    "loaded": table.loaded if table else None,
                })
    return inventory
