"""Assessment-level criticality calculation using stored CSV snapshots."""

from dataclasses import asdict, dataclass, field

from .loader import load_report_date

DATA_POINTS = {"None": 0, "Internal": 1, "Confidential": 2, "Regulated": 3}
ACCESS_POINTS = {"None": 0, "Standard": 1, "Privileged": 2}
DEPENDENCY_POINTS = {"1": 1, "2": 2, "3": 3, "4": 4}
REPLACEABILITY_POINTS = {"Easy": 1, "Moderate": 2, "Hard": 3, "Very hard": 4}
SERVICE_TIER_RANK = {"Standard": 1, "Important": 2, "Business-critical": 3}
FACTORS = (
    ("data_sensitivity", DATA_POINTS, "data_sensitivity_points"),
    ("system_access", ACCESS_POINTS, "system_access_points"),
    ("dependency_impact", DEPENDENCY_POINTS, "dependency_points"),
    ("replaceability", REPLACEABILITY_POINTS, "replaceability_points"),
)


@dataclass
class CriticalityResult:
    assessment_id: str
    vendor_id: str
    data_sensitivity: str | None = None
    data_sensitivity_points: int | None = None
    system_access: str | None = None
    system_access_points: int | None = None
    dependency_impact: str | None = None
    dependency_points: int | None = None
    replaceability: str | None = None
    replaceability_points: int | None = None
    total_points: int | None = None
    base_band: str | None = None
    linked_services: list[str] = field(default_factory=list)
    highest_service_tier: str | None = None
    override_reasons: list[str] = field(default_factory=list)
    final_band: str = "PROVISIONAL — INCOMPLETE INPUTS"
    complete: bool = False
    errors: list[dict] = field(default_factory=list)
    calculation_trace: list[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


def _records(value):
    """Accept a row mapping, a sequence of mappings, or a loaded CSV Table."""
    if value is None:
        return []
    if hasattr(value, "rows"):
        return list(value.rows)
    if isinstance(value, dict):
        return [value]
    return list(value)


def _error(result, field_name, value, message, correction):
    result.errors.append({"field": field_name, "value": "" if value is None else str(value),
                          "message": message, "correction": correction})


def _base_band(total):
    if 2 <= total <= 3:
        return "Low"
    if 4 <= total <= 6:
        return "Medium"
    if 7 <= total <= 9:
        return "High"
    if 10 <= total <= 13:
        return "Critical"
    raise ValueError(f"Criticality total {total} is outside the approved 2–13 range.")


def calculate_criticality(assessment_id, vendor_record, service_records,
                          vendor_service_links, criticality_snapshot):
    """Calculate one assessment from its immutable snapshot and linked services.

    Factors are read only from ``criticality_snapshot``. The vendor row supplies
    identity and name context; it is never a fallback for missing snapshot values.
    """
    vendor_rows = _records(vendor_record)
    vendor = vendor_rows[0] if len(vendor_rows) == 1 else {}
    result = CriticalityResult(str(assessment_id or ""), str(vendor.get("vendor_id", "")))
    if len(vendor_rows) != 1:
        _error(result, "vendor_record", len(vendor_rows),
               "Exactly one unambiguous vendor record is required",
               "Resolve missing or duplicate vendor_id records before calculating.")

    snapshots = _records(criticality_snapshot)
    if len(snapshots) != 1:
        value = len(snapshots)
        _error(result, "assessment_id", assessment_id,
               "Exactly one criticality snapshot is required for this assessment; "
               f"found {value}.",
               "Add one snapshot row or remove duplicate assessment snapshot rows.")
    snapshot = snapshots[0] if len(snapshots) == 1 else {}
    if snapshot and snapshot.get("assessment_id") != assessment_id:
        _error(result, "assessment_id", snapshot.get("assessment_id"),
               "Snapshot assessment_id must match the requested assessment",
               "Use the snapshot row for this assessment version.")
    if snapshot and vendor and snapshot.get("vendor_id") != vendor.get("vendor_id"):
        _error(result, "vendor_id", snapshot.get("vendor_id"),
               "Snapshot vendor_id must match the assessment vendor",
               "Correct snapshot vendor_id to the vendor recorded on the assessment.")
    if snapshot and vendor and vendor.get("current_assessment_id") == assessment_id:
        for field_name, _, _ in FACTORS:
            if snapshot.get(field_name) != vendor.get(field_name):
                _error(result, field_name, snapshot.get(field_name),
                       "Current assessment snapshot conflicts with the vendor register",
                       "Reconcile the current snapshot and vendor register value before confirming criticality.")

    values = {}
    factor_points = {}
    for field_name, allowed, points_field in FACTORS:
        raw = snapshot.get(field_name)
        if raw is None or not str(raw).strip():
            _error(result, field_name, raw, f"Required criticality factor {field_name} is missing",
                   f"Supply one approved {field_name} value in the assessment snapshot.")
            continue
        value = str(raw).strip()
        if value not in allowed:
            _error(result, field_name, raw, f"Value is outside the approved {field_name} enumeration",
                   f"Use one of: {', '.join(allowed)}.")
            continue
        values[field_name] = value
        factor_points[field_name] = allowed[value]
        setattr(result, field_name, value)
        setattr(result, points_field, allowed[value])

    service_index = {}
    for service in _records(service_records):
        service_id = service.get("service_id")
        if service_id in service_index:
            _error(result, "service_id", service_id, "Duplicate service_id makes service tier ambiguous",
                   "Retain one business_service row per service_id.")
        else:
            service_index[service_id] = service
    links = [link for link in _records(vendor_service_links)
             if link.get("vendor_id") == result.vendor_id]
    link_ids = [link.get("service_id") for link in links]
    if len(link_ids) != len(set(link_ids)):
        _error(result, "vendor_service_link", ", ".join(str(x) for x in link_ids),
               "Duplicate vendor-service links are not allowed",
               "Retain one row for each unique vendor_id and service_id pair.")
    services = []
    for service_id in sorted(set(link_ids), key=lambda x: str(x)):
        service = service_index.get(service_id)
        if not service:
            _error(result, "service_id", service_id, "Linked business service does not exist",
                   "Restore the referenced business_service row or correct the service_id.")
            continue
        tier = service.get("service_tier")
        if tier not in SERVICE_TIER_RANK:
            _error(result, "service_tier", tier, "Linked service tier is invalid or missing",
                   "Use Business-critical, Important or Standard in business_service.service_tier.")
            continue
        result.linked_services.append(service_id)
        services.append(service)
    if services:
        result.highest_service_tier = max(
            (service["service_tier"] for service in services),
            key=lambda tier: SERVICE_TIER_RANK[tier],
        )

    result.calculation_trace = [f"Assessment: {result.assessment_id}",
                                f"Vendor: {result.vendor_id}"]
    factor_lines = []
    for field_name, _, points_field in FACTORS:
        value = values.get(field_name)
        points = getattr(result, points_field)
        factor_lines.append(f"{field_name.replace('_', ' ').title()}: "
                            f"{value if value is not None else '<missing/invalid>'} = "
                            f"{points if points is not None else 'not scored'}")
    result.calculation_trace.extend(factor_lines)
    if len(factor_points) == len(FACTORS):
        result.total_points = sum(factor_points.values())
        result.base_band = _base_band(result.total_points)
        result.calculation_trace.append(
            "Base score: " + " + ".join(str(factor_points[field]) for field, _, _ in FACTORS)
            + f" = {result.total_points}")
        result.calculation_trace.append(f"Base band: {result.base_band}")

    if not result.errors and result.total_points is not None:
        final_band = result.base_band
        if result.highest_service_tier == "Business-critical":
            result.override_reasons.append("Business-critical service floor")
            if final_band in ("Low", "Medium"):
                final_band = "High"
        if values["data_sensitivity"] == "Regulated" and values["system_access"] == "Privileged":
            result.override_reasons.append("Regulated plus privileged")
            final_band = "Critical"
        if values["dependency_impact"] == "4" and values["replaceability"] == "Very hard":
            result.override_reasons.append("Severe dependency plus very hard replacement")
            final_band = "Critical"
        result.final_band = final_band
        result.complete = True
        result.calculation_trace.append(
            "Linked services: " + (", ".join(result.linked_services) or "none"))
        result.calculation_trace.append(f"Highest linked service tier: {result.highest_service_tier}")
        result.calculation_trace.append(
            "Overrides: " + ("; ".join(result.override_reasons) if result.override_reasons else "none"))
        result.calculation_trace.append(f"Final band: {result.final_band}")
    else:
        result.final_band = "PROVISIONAL — INCOMPLETE INPUTS"
        result.calculation_trace.append("Final band: PROVISIONAL — INCOMPLETE INPUTS")
        for error in result.errors:
            result.calculation_trace.append(
                f"Input error: {error['field']}={error['value']!r}: {error['message']} "
                f"Correction: {error['correction']}")
    return result


def calculate_all_criticality(source_tables, as_of_date=None):
    """Calculate every assessment in stable assessment_id order."""
    # Date parsing is explicit even though criticality itself is not date-scored;
    # callers get the same strict report-date handling as the CSV validation CLI.
    load_report_date(as_of_date.isoformat() if hasattr(as_of_date, "isoformat") else as_of_date)

    def rows(name):
        table = source_tables.get(name)
        return list(table.rows) if hasattr(table, "rows") else list(table or [])

    vendors = {}
    for row in rows("vendor"):
        vendors.setdefault(row.get("vendor_id"), []).append(row)
    snapshots = {}
    for row in rows("assessment_criticality_snapshot"):
        snapshots.setdefault(row.get("assessment_id"), []).append(row)
    assessments = sorted(rows("assessment"), key=lambda row: row.get("assessment_id", ""))
    results = []
    for assessment in assessments:
        vendor_rows = vendors.get(assessment.get("vendor_id"), [])
        vendor = vendor_rows[0] if len(vendor_rows) == 1 else None
        results.append(calculate_criticality(
            assessment.get("assessment_id"), vendor,
            rows("business_service"), rows("vendor_service_link"),
            snapshots.get(assessment.get("assessment_id"), []),
        ))
    return results
