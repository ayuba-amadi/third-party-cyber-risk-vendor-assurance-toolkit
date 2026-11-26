"""Compare explicitly designated assessment versions and identify triggers."""
from .loader import load_report_date

FACTORS = ("data_sensitivity", "system_access", "dependency_impact", "replaceability")
TRIGGER_CHANGE_TYPES = {"New subcontractor", "Scope increase", "Access increase", "Data type added"}


def review_status(vendor, report_date):
    days = max(0, (report_date - load_report_date(vendor["next_review_date"])).days)
    return dict(vendor_id=vendor["vendor_id"], vendor_name=vendor["vendor_name"],
                current_assessment_id=vendor["current_assessment_id"], next_review_date=vendor["next_review_date"],
                report_date=report_date.isoformat(), days_overdue=days, source_id=vendor["vendor_id"])


def compare_versions(vendor, assessments, criticality, risk, decisions, changes, report_date,
                     remediation=()):
    vid = vendor["vendor_id"]
    aid = vendor["current_assessment_id"]
    current = assessments.get(aid, {})
    previous = assessments.get(current.get("supersedes_id"), {})
    events = sorted((event for event in changes if event["vendor_id"] == vid and
                     load_report_date(event["change_date"]) <= report_date), key=lambda row: row["change_id"])
    version_rows = []
    for assessment in (previous, current):
        if not assessment:
            continue
        key = assessment["assessment_id"]
        crit = criticality[key]
        result, questions, _ = risk[key]
        decision = decisions.get(key, {})
        related = [row for row in remediation if row["assessment_id"] == key]
        findings = sorted({row["finding_id"] for row in related})
        actions = sorted({row["action_id"] for row in related if row["action_id"]})
        evidence = sorted({row["evidence_id"] for row in questions if row["evidence_id"]})
        version_rows.append(dict(assessment, selection="Current" if key == aid else "Historical",
                                 **{field: getattr(crit, field) for field in FACTORS},
                                 criticality_score=crit.total_points, criticality_band=crit.final_band,
                                 risk_numerator=result["weighted_points"], risk_percent=result["risk_percent"],
                                 completeness=result["completeness"], evidence_flags=result["evidence_flags"],
                                 decision_status=decision.get("outcome", "Awaiting decision"),
                                 decision_id=decision.get("decision_id", ""),
                                 finding_ids=findings, corrective_action_ids=actions, evidence_ids=evidence,
                                 source_ids=[key, vid] + ([decision["decision_id"]] if decision else [])
                                 + findings + actions + evidence))
    relevant = [event for event in events
                if event["material"] == "Yes" or event["change_type"] in TRIGGER_CHANGE_TYPES]
    covered = []
    pending = []
    for event in relevant:
        linked_id = event["reassessment_assessment_id"]
        if not linked_id:
            pending.append(event["change_id"])
        elif not assessments[linked_id]["supersedes_id"]:
            raise ValueError(f"{event['change_id']}: change must link to a new assessment version")
        else:
            covered.append(event)
    if vendor["material_change_flag"] == "Yes" and not covered and not pending:
        pending.append(f"{vid}: material change flag")
    triggers = [f"Unlinked material change {item}" for item in pending]
    if aid:
        for field in FACTORS:
            if vendor[field] != getattr(criticality[aid], field):
                triggers.append(f"Vendor register changed: {field}")
        for question in risk[aid][1]:
            if question["critical_failure_flag"] and question["effective_evidence_status"] == "Expired":
                triggers.append(f"Critical evidence expired: {question['evidence_id']}")
        if decisions.get(aid, {}).get("expired_approval"):
            triggers.append(f"Expired approval {decisions[aid]['decision_id']}")
    if review_status(vendor, report_date)["days_overdue"]:
        triggers.append("Vendor review overdue")
    changed = [field for field in FACTORS if len(version_rows) == 2 and
               version_rows[0][field] != version_rows[1][field]]
    return dict(vendor_id=vid, current_assessment_id=aid, previous_assessment_id=previous.get("assessment_id", ""),
                versions=version_rows, changed_factors=changed, change_events=events,
                linked_reassessment_change_ids=[event["change_id"] for event in covered],
                reassessment_required=bool(triggers), pending_triggers=triggers,
                source_ids=[vid] + [row["assessment_id"] for row in version_rows] +
                [event["change_id"] for event in events])
