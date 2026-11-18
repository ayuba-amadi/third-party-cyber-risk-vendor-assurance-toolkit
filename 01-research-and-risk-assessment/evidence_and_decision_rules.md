# Evidence and Decision Rules

Project: Third-Party Cyber Risk Assessment and Vendor Assurance Toolkit
Owner: Foka Averil. Subgroup: Research and Risk Assessment.
Version: Day 2 v0.1 DRAFT, 17 November 2026. Status: Draft, pending review.
All vendors and data are fictional. Rules marked PROPOSED need team-lead approval before the toolkit uses them.

## 1. Purpose and scope
This document defines how evidence is recorded and reviewed, how each evidence state affects completeness, score and flags, and how the authorised approver records a decision. It uses the field names in `data_dictionary.md` and the weights (1 to 5) and risk values (0 to 4) in `risk_scoring_method.md`. It does not change either document. Requirements covered: R04, R06 and R07.

## 2. Supplier claim versus reviewer-verified answer
| Field (response table) | Meaning | Who sets it |
|---|---|---|
| vendor_claim | The answer the vendor gave, recorded as received | Assessor, from the vendor |
| reviewer_verified | Yes, No or Not reviewed | Reviewer |
| verified_answer | The answer the reviewer confirms from evidence | Reviewer |
| reviewer_note | The reviewer's reason or observation | Reviewer |

1. A vendor claim is never a verified control. It is shown in reports as "Claimed".
2. reviewer_verified may be set to Yes only when the linked evidence item has status Accepted and is not past its expiry date.
3. verified_answer must be one of the answer choices in `question_bank.csv`. Its risk value comes from that choice, not from the vendor's claim.
4. A verified_answer worse than the vendor_claim is allowed and is recorded with a reviewer_note. A verified_answer better than the claim is not allowed unless the evidence supports it, and the note says why.

## 3. Evidence states
| State | Meaning | Fields required (evidence_item) |
|---|---|---|
| Missing | Evidence is required but has not been provided | evidence_id, assessment_id, question_id, status |
| Received | Evidence provided, not yet reviewed | Above, plus received_date, reference_path |
| Accepted | Reviewer checked it against the acceptance criteria and accepts it | Above, plus review_period_end, expiry_date, reviewer_role |
| Rejected | Reviewer checked it and it fails the criteria | Above, plus reviewer_role, reason |
| Expired | Accepted evidence whose expiry_date has passed | Same as Accepted |

**Allowed changes of state**
- Missing to Received (vendor supplies it).
- Received to Accepted or Rejected (reviewer decides).
- Accepted to Expired (automatic, by date).
- Rejected: the vendor sends a replacement. A new evidence_item row is created with status Received. The Rejected row is kept as history and is never edited.
- Expired: a new evidence_item row is created for the replacement. The expired row is kept.

**Timestamps and reviewer identity**
- received_date is the date the evidence arrived. It is required for every state except Missing.
- The review itself (who and when) is recorded as a reviewer_audit_entry with action Verified or Rejected, and the reviewer's role is stored in reviewer_role. Role titles only, no personal names or student IDs.
- reference_path points to the stored file, using a fictional path in the public repository (for example `evidence/VEN-001/mfa-export.pdf`).
- A reason is mandatory for Rejected. It must state what failed, for example "report covers 2024 only, outside the last 12 months".

**Expiry (PROPOSED)**
- expiry_date is the earlier of (a) review_period_end plus the validity period in the Evidence column of `question_bank.csv` (12 months for policies and reports, 90 days for technical exports and scans), and (b) any expiry printed on the artifact itself, such as a certificate date.
- The toolkit compares expiry_date with the report date every time it runs. If the report date is later, the evidence is treated as Expired even if the stored status still says Accepted.
- Evidence whose review period ends outside the allowed window is rejected, not accepted with a short expiry.

## 4. Effect of each state on completeness, score and flags
All questions in `question_bank.csv` require evidence. The scoring rule below follows the principle that unknown evidence is never favourable. Item 1 depends on the scoring owner confirming that the denominator includes every question (raised in review of `risk_scoring_method.md`).

| Situation | Completeness | Score (PROPOSED) | Flag raised |
|---|---|---|---|
| Missing | Not complete | Question counts at the worst risk value (4); stays in the denominator | MISSING EVIDENCE with question_id |
| Received, not reviewed | Not complete | Worst risk value (4) until reviewed | AWAITING REVIEW |
| Accepted, valid | Complete | Risk value of the verified_answer | None |
| Rejected | Not complete | Worst risk value (4) until replaced | REJECTED EVIDENCE with reason |
| Expired | Not complete | Worst risk value (4) until replaced | EXPIRED EVIDENCE with expiry date |
| No vendor response | Not complete | Worst risk value (4) | UNANSWERED |

Additional rules
1. If the question has critical_failure_flag = Yes and its evidence is Missing, Received, Rejected or Expired, the assessment shows INCOMPLETE and CRITICAL QUESTION UNRESOLVED. No risk band is shown as final.
2. A confirmed critical failure (a verified_answer at risk value 3 or 4 on a critical-failure question) shows CRITICAL FAILURE with the question_id and reviewer_note. Minimum rating treatment is High (PROPOSED, to be confirmed by the scoring owner).
3. An assessment is Complete only when every question has a vendor_claim, valid Accepted evidence and reviewer_verified = Yes.
4. Any percentage shown for an Incomplete assessment is labelled PROVISIONAL.

## 5. Approval decisions
**Outcomes:** Approved, Conditionally Approved, Rejected. The toolkit never records an outcome. It shows the calculated rating, flags and a recommended range. The authorised approver records the outcome.

**Required fields (decision table)**
| Outcome | Always required | Also required |
|---|---|---|
| Approved | decision_maker_role, justification, decision_date, expiry_date, review_date | None |
| Conditionally Approved | Same as Approved | conditions, condition_deadline, and at least one corrective action linked to a finding |
| Rejected | decision_maker_role, justification, decision_date | Reason tied to a finding, rating or flag; review_date for any resubmission |

**Rules**
1. The decision_maker_role must differ from the assessor_role of the same assessment.
2. calculated_rating is copied into the decision record at decision time, so later recalculation does not change the history.
3. review_date is on or before expiry_date. For Conditionally Approved, review_date is on or before condition_deadline.
4. Approval validity, counted from decision_date (PROPOSED): Critical 6 months, High 12 months, Medium 12 months, Low 24 months. Conditionally Approved never exceeds 6 months.
5. Each condition must have a deadline and a responsible party in the linked corrective_action.

## 6. Decision constraints by calculated state
"Not permitted" means the toolkit refuses to save that outcome. "Exception" means the approver may record it only with a written exception justification, and the report shows the exception.

| Calculated state | Approved | Conditionally Approved | Rejected |
|---|---|---|---|
| Incomplete, critical question unresolved | Not permitted | Exception | Permitted |
| Incomplete, no critical question affected | Not permitted | Permitted, with conditions covering every missing item | Permitted |
| Confirmed critical failure | Not permitted | Exception, with a dated corrective action | Permitted |
| Complete, Critical or High rating, no failure | Permitted | Permitted | Permitted |
| Complete, Medium or Low rating, no failure | Permitted | Permitted | Exception |
| No decision recorded | Vendor shown as Awaiting decision | | |

## 7. Overdue, expired and change-triggered flags
Report date is the date the toolkit runs (2026-11-18 for the demonstration data).

| Flag | Rule |
|---|---|
| Overdue review | vendor.next_review_date is earlier than the report date |
| Expired approval | decision.expiry_date is earlier than the report date |
| Overdue condition or action | condition_deadline or action due_date is earlier than the report date and action status is not Closed |
| Expired evidence | evidence expiry_date is earlier than the report date |
| Material change | A change_event with material = Yes has no reassessment yet |

Each flag triggers a reassessment entry. A reassessment creates a new assessment_id, marks the previous one Superseded and keeps all its decisions, findings and evidence for comparison.

## 8. Management report counts
1. Each vendor is counted once in each breakdown: by category, by criticality band, and by decision status (Approved, Conditionally Approved, Rejected, Awaiting decision).
2. Every breakdown must total the number of vendors in the register. The report shows both the totals and the vendor IDs behind them.
3. Flag lists (overdue review, expired approval, overdue action, incomplete, critical failure, expired evidence) list vendor IDs. A vendor can appear on several lists, so flag totals are not expected to add up to the vendor count.
4. Concentration: a service is reported when more than one vendor supports it, and a vendor is reported when it supports several services. Both are listed by service_id and vendor_id.
5. Each figure in the report can be traced to source IDs in the underlying tables.

## 9. Open policy choices for the team lead
1. Evidence validity: 12 months for policies and reports and 90 days for technical exports (this replaces the earlier proposal of 6 months for incident response testing, which is covered by the 12-month test window in question IN-02).
2. Worst-value treatment (4) for unverified questions, and the denominator including every question (depends on `risk_scoring_method.md`).
3. Minimum rating of High for a confirmed critical failure.
4. Approval validity periods in section 5.
5. Whether the Approver can also act as the Reviewer. Current rule: the approver cannot be the assessor.
