"""Read finding, action and condition records without changing their status."""
from .loader import load_report_date


def action_overdue(action, report_date):
    return action["status"] != "Closed" and load_report_date(action["due_date"]) < report_date


def finding_actions(tables, decisions, report_date):
    assessments = {row["assessment_id"]: row for row in tables["assessment"].rows}
    current = {row["current_assessment_id"] for row in tables["vendor"].rows}
    rows = []
    for finding in sorted(tables["finding"].rows, key=lambda row: row["finding_id"]):
        aid = finding["assessment_id"]
        decision = decisions.get(aid, {})
        actions = sorted((row for row in tables["corrective_action"].rows
                          if row["finding_id"] == finding["finding_id"]), key=lambda row: row["action_id"])
        for action in actions or [{}]:
            rows.append(dict(finding, finding_status=finding["status"],
                             vendor_id=assessments[aid]["vendor_id"], current=aid in current,
                             decision_id=decision.get("decision_id", ""),
                             **{key: action.get(key, "") for key in
                                ("action_id", "action_text", "responsible_party", "due_date", "closed_date")},
                             action_status=action.get("status", ""),
                             action_overdue=bool(action and action_overdue(action, report_date)),
                             source_ids=[value for value in
                                         (aid, assessments[aid]["vendor_id"], finding["finding_id"],
                                          action.get("action_id"), decision.get("decision_id")) if value]))
    return rows


def condition_status(decision, actions, report_date):
    if decision["outcome"] != "Conditionally Approved":
        return False, False
    linked = [row for row in actions if row["action_id"]]
    outstanding = not linked or any(row["action_status"] != "Closed" or
                                    load_report_date(row["closed_date"]) > report_date for row in linked)
    return outstanding, outstanding and load_report_date(decision["condition_deadline"]) < report_date
