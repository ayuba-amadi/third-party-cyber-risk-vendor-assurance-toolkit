"""Validate recorded human decisions and calculate effective approval status."""
from .loader import load_report_date
from .remediation import condition_status

APPROVALS = ("Approved", "Conditionally Approved")


def index_decisions(rows):
    decisions = {}
    for row in rows:
        aid = row["assessment_id"]
        if aid in decisions:
            raise ValueError(f"{aid}: multiple decisions with no explicit current decision selector")
        decisions[aid] = row
    return decisions


def evaluate_decision(decision, assessment, risk, questions, actions, report_date):
    did = decision["decision_id"]
    outcome = decision["outcome"]
    decision_date = load_report_date(decision["decision_date"])
    if decision_date < load_report_date(assessment["assessment_date"]):
        raise ValueError(f"{did}: decision date precedes assessment date")
    if decision_date > report_date:
        return None
    if decision["calculated_rating"] not in ("Low", "Medium", "High", "Critical", "Incomplete"):
        raise ValueError(f"{did}: invalid recorded calculated rating")
    expiry = decision.get("expiry_date")
    expired = outcome in APPROVALS and load_report_date(expiry) < report_date
    warnings = []
    if outcome in APPROVALS:
        failures = {row["question_id"] for row in questions if row["confirmed_critical_failure"]}
        gaps = {row["question_id"] for row in questions if not row["verified"]}
        later_expiry = {row["question_id"] for row in questions
                        if row["effective_evidence_status"] == "Expired" and row["evidence_expiry_date"]
                        and load_report_date(row["evidence_expiry_date"]) >= decision_date and row["answered"]}
        if later_expiry & gaps and decision["calculated_rating"] != "Incomplete":
            warnings.append("Evidence expired on or after the decision date. The recorded decision-time rating is preserved.")
            gaps -= later_expiry
        if outcome == "Approved" and (gaps or failures or decision["calculated_rating"] == "Incomplete"):
            raise ValueError(f"{did}: ordinary approval is prohibited with incomplete items or confirmed critical failures")
        if outcome == "Conditionally Approved":
            coverage = {row["question_id"] for row in actions if row["action_id"] and row["due_date"]}
            if not (gaps | failures) <= coverage:
                raise ValueError(f"{did}: missing dated corrective actions for {sorted((gaps | failures) - coverage)}")
            if (failures or set(risk["unresolved_critical_questions"]) & gaps) and "exception" not in decision["justification"].casefold():
                raise ValueError(f"{did}: critical failures or unresolved critical questions require a written exception")
    outstanding, overdue = condition_status(decision, actions, report_date)
    return dict(decision, vendor_id=assessment["vendor_id"], report_date=report_date.isoformat(),
                current_risk_rating=risk["final_rating"], expired_approval=expired,
                active_approval=outcome in APPROVALS and not expired,
                open_condition=outstanding, overdue_condition=overdue, warnings=warnings,
                source_ids=[did, assessment["assessment_id"], assessment["vendor_id"]] +
                [row["action_id"] for row in actions if row["action_id"]])
