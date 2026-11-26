"""Score questionnaire responses against accepted evidence and the CSV question bank."""
from datetime import date
from fractions import Fraction

from .loader import load_report_date


def parse_options(definition):
    options = {}
    for option in definition.split(" | "):
        label, separator, value = option.rpartition(" = ")
        if not separator or not label.strip() or label in options or label == "Blank" or value not in "01234" or len(value) != 1:
            raise ValueError(f"Invalid answer option: {option!r}")
        options[label] = int(value)
    return options


def score_question(question, response, evidence, report_date):
    qid = question["question_id"]
    options = parse_options(question["response_options"])
    if str(question["weight"]) not in ("1", "2", "3", "4", "5"):
        raise ValueError(f"{qid}: invalid weight {question['weight']!r}")
    weight = int(question["weight"])
    response = response or {}
    evidence = evidence or {}
    claim = response.get("vendor_claim")
    answer = response.get("verified_answer")
    answered = claim not in (None, "", "Blank")
    for field, value in (("vendor_claim", claim if answered else None), ("verified_answer", answer)):
        if value and value not in options:
            raise ValueError(f"{qid}: invalid {field} {value!r}")
    reviewer = response.get("reviewer_verified", "Not reviewed")
    status = evidence.get("status", "Missing")
    if status not in ("Missing", "Received", "Accepted", "Rejected", "Expired"):
        raise ValueError(f"{qid}: invalid evidence status {status!r}")
    expiry = evidence.get("expiry_date")
    effective = status
    if status == "Accepted" and expiry and load_report_date(expiry) < report_date:
        effective = "Expired"
    required = question["evidence_required"] == "Yes"
    critical = question["critical_failure_flag"] == "Yes"
    reasons = []
    flags = []
    if effective != "Accepted":
        flags.append(effective.upper() + " EVIDENCE")
        reasons.append(f"Effective evidence status is {effective}")
        if evidence.get("reason"):
            reasons.append(evidence["reason"])
    elif not expiry or not (evidence.get("reviewer_role") or "").strip():
        reasons.append("Accepted evidence requires an expiry date and reviewer role")
    if not answered:
        flags.append("UNANSWERED")
        reasons.append("Vendor claim is unanswered")
    if reviewer != "Yes" or not answer:
        reasons.append("Reviewer verification or verified answer is outstanding")
    if answered and answer and reviewer == "Yes" and options[answer] < options[claim]:
        if not (response.get("reviewer_note") or "").strip():
            raise ValueError(f"{qid}: a better verified answer requires a reviewer note")
    verified = not reasons
    confirmed = critical and verified and options[answer] >= 3
    unresolved = critical and not verified
    value = options[answer] if verified and not confirmed else 4
    if confirmed:
        flags.append("CONFIRMED CRITICAL FAILURE")
    if unresolved:
        flags.append("UNRESOLVED CRITICAL QUESTION")
    explanation = ("Confirmed critical failure receives risk value 4" if confirmed else
                   f"Accepted evidence supports verified answer {answer!r}" if verified else
                   ". ".join(reasons) + ". Worst-risk treatment applies")
    return dict(assessment_id=response.get("assessment_id", evidence.get("assessment_id")),
                vendor_id=response.get("vendor_id"), question_id=qid, domain=qid.split("-")[0],
                vendor_claim=claim, answered=answered, reviewer_verified=reviewer, verified=verified,
                verified_answer=answer, reviewer_note=response.get("reviewer_note"),
                evidence_id=evidence.get("evidence_id"), evidence_status=status,
                effective_evidence_status=effective, evidence_expiry_date=expiry,
                risk_value=value, question_weight=weight, weighted_risk_points=value * weight,
                maximum_points=4 * weight, required_evidence=required, critical_failure_flag=critical,
                confirmed_critical_failure=confirmed, unresolved_critical_question=unresolved,
                completeness_effect="Complete" if verified else "Incomplete", flags=flags,
                calculation_reason=f"{explanation}. {value} × {weight} = {value * weight} points.")


def risk_band(percent):
    return "Low" if percent < 20 else "Medium" if percent < 40 else "High" if percent < 60 else "Critical"


def calculate_assessment_risk(assessment, questions, responses, evidence_items, report_date):
    aid = assessment["assessment_id"]
    vid = assessment["vendor_id"]
    effective_date = (load_report_date(assessment["assessment_date"])
                      if assessment["status"] == "Superseded" else report_date)

    def index(rows):
        result = {}
        for row in rows:
            if row["assessment_id"] == aid:
                qid = row["question_id"]
                if qid in result:
                    raise ValueError(f"{aid}/{qid}: duplicate assessment-question pair")
                result[qid] = row
        return result

    responses = index(responses)
    evidence_items = index(evidence_items)
    scores = []
    for question in sorted(questions, key=lambda row: row["question_id"]):
        qid = question["question_id"]
        try:
            score = score_question(question, responses.get(qid), evidence_items.get(qid), effective_date)
        except ValueError as exc:
            raise ValueError(f"{aid}/{qid}: {exc}") from exc
        scores.append(dict(score, assessment_id=aid, vendor_id=vid))
    domains = []
    for domain in sorted({row["domain"] for row in scores}):
        rows = [row for row in scores if row["domain"] == domain]
        verified = sum(row["verified"] for row in rows)
        domains.append(dict(assessment_id=aid, vendor_id=vid, domain=domain,
                            total_questions=len(rows), answered_count=sum(row["answered"] for row in rows),
                            verified_count=verified, completeness_percent=f"{100 * verified / len(rows):.6f}"))
    points = sum(row["weighted_risk_points"] for row in scores)
    maximum = sum(row["maximum_points"] for row in scores)
    percent = Fraction(100 * points, maximum)
    raw = risk_band(percent)
    verified = sum(row["verified"] for row in scores)
    failures = [row["question_id"] for row in scores if row["confirmed_critical_failure"]]
    unresolved = [row["question_id"] for row in scores if row["unresolved_critical_question"]]
    incomplete = verified != len(scores)
    final = "Incomplete" if incomplete else "High" if failures and raw in ("Low", "Medium") else raw
    label = "PROVISIONAL — INCOMPLETE ASSESSMENT" if incomplete else "Complete"
    trace = [f"{points}/{maximum} × 100 = {float(percent):.2f}%. Raw band {raw}.",
             f"{verified}/{len(scores)} verified. {label}. Final rating {final}."]
    if failures:
        trace.append("Confirmed critical failures impose a High minimum on completed ratings: " + ", ".join(failures))
    if unresolved:
        trace.append("Unresolved critical questions: " + ", ".join(unresolved))
    result = dict(assessment_id=aid, vendor_id=vid, answered_count=sum(row["answered"] for row in scores),
                  verified_count=verified, weighted_points=points, maximum_points=maximum,
                  risk_percent=f"{float(percent):.6f}", raw_band=raw, final_rating=final,
                  completeness="Incomplete" if incomplete else "Complete", score_label=label,
                  evidence_as_of=effective_date.isoformat(), confirmed_critical_failures=failures,
                  unresolved_critical_questions=unresolved,
                  evidence_flags=[f"{row['question_id']}:{row['effective_evidence_status']}" for row in scores
                                  if row["effective_evidence_status"] != "Accepted"],
                  unanswered_questions=[row["question_id"] for row in scores if not row["answered"]],
                  calculation_trace=trace)
    return result, scores, domains


def calculate_all_assessment_risk(source_tables, report_date):
    if not isinstance(report_date, date):
        report_date = load_report_date(report_date)
    questions = source_tables["question"].rows
    ids = [row["question_id"] for row in questions]
    expected = {f"{domain}-{number:02}" for domain in ("AM", "DP", "IN", "BC", "SC", "GV")
                for number in range(1, 5)}
    if set(ids) != expected or len(ids) != len(expected):
        raise ValueError("Question bank must contain each of the 24 approved question IDs exactly once")
    assessments = sorted(source_tables["assessment"].rows, key=lambda row: row["assessment_id"])
    if not assessments:
        raise ValueError("No assessments available to score")
    return [calculate_assessment_risk(row, questions, source_tables["response"].rows,
                                      source_tables["evidence_item"].rows, report_date)
            for row in assessments]
