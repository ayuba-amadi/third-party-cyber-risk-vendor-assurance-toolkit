# Vendor Risk Scoring Method

**Project:** Third-Party Cyber Risk Assessment and Vendor Assurance Toolkit  
**Document Owner:** Saadu Shukurat Titilayo  
**Subgroup:** Research and Risk Assessment  
**Version:** 0.2 DRAFT  
**Date:** 18 November 2026  
**Status:** Revised Draft – Pending Team Review

---

## 1. Purpose

This document defines the method for calculating and interpreting vendor security risk assessment results.

The scoring method uses responses to the third-party security due diligence questionnaire.

It considers:

- The weight assigned to each questionnaire question.
- The vendor's response.
- Whether the response has been verified by a reviewer.
- Whether the required supporting evidence has been accepted.
- Whether a question has been identified as a critical-failure question.
- The completeness of the assessment.

The purpose is to produce a consistent risk assessment result that supports informed decision-making.

The calculated result informs the authorised approver. It does not automatically approve or reject a vendor.

## 2. Questionnaire Structure

The questionnaire contains questions across six domains:

| Code | Domain |
|---|---|
| AM | Access Management |
| DP | Data Protection |
| IN | Incident Notification |
| BC | Business Continuity and Recovery |
| SC | Subcontractors |
| GV | Governance |

Each question must have:

- A unique question ID.
- A question domain.
- A clearly written question.
- Defined response options.
- A weight between 1 and 5.
- An evidence-required value.
- Acceptance criteria where applicable.
- A critical-failure flag.

The project requires at least 24 questionnaire questions.

## 3. Question Weighting

Each questionnaire question has a weight between 1 and 5.

| Weight | Meaning |
|---|---|
| 1 | Low importance |
| 2 | Limited importance |
| 3 | Moderate importance |
| 4 | High importance |
| 5 | Very high importance |

Higher-weight questions have a greater influence on the overall calculated result.

The question owner should assign weights based on the importance of the control to the organisation.

A question marked as a critical-failure question must also be handled under the critical-failure rules in this document.

## 4. Vendor Claims and Reviewer Verification

A vendor's response is initially recorded as a vendor claim.

The following fields must be distinguished:

- `vendor_claim`: The answer provided by the vendor.
- `reviewer_verified`: Whether the reviewer has verified the answer.
- `verified_answer`: The answer confirmed by the reviewer.
- `reviewer_note`: The reviewer's explanation or observation.

A vendor's claim must not automatically be treated as a verified control.

Only responses that have been reviewed and supported by acceptable evidence should receive verified credit where evidence is required.

## 5. Evidence Status Rules

The project data dictionary defines five evidence statuses.

| Evidence Status | Meaning | Scoring Treatment |
|---|---|---|
| Missing | Evidence has not been provided | Risk value 4 where evidence is required |
| Received | Evidence has been submitted but not yet accepted | Risk value 4 where evidence is required |
| Accepted | Evidence has been reviewed and accepted | Eligible for verified scoring |
| Rejected | Evidence has been reviewed and rejected | Risk value 4 where evidence is required |
| Expired | Evidence is no longer valid | Risk value 4 where evidence is required |

For evidence to be Accepted:

- A reviewer role must be recorded.
- An expiry date must be recorded.
- The evidence must satisfy the relevant acceptance criteria.

Rejected evidence must include a reason.

An Accepted evidence status does not automatically mean that the vendor's control is effective. The reviewer must still record the verified answer based on the evidence.

## 6. Proposed Scoring Approach

The project requires a weighted score with a denominator.

The proposed scoring approach assigns a verified risk value to every questionnaire question.

### 6.1 Verified Risk Values

| Verified Risk Value | Interpretation |
|---|---|
| 0 | No identified control weakness |
| 1 | Minor control weakness |
| 2 | Moderate control weakness |
| 3 | Significant control weakness |
| 4 | Severe control weakness or unresolved response/evidence requirement |

The reviewer must assign the value based on the question's documented acceptance criteria.

The value must not be assigned merely because the vendor selected a particular response.

### 6.2 Weighted Risk Points

For each question:

**Weighted Risk Points = Question Weight × Assigned Risk Value**

The maximum possible weighted risk points for each question are:

**Maximum Question Points = Question Weight × 4**

### 6.3 Denominator Rule

### 6.3 Denominator Rule

The denominator must include every question in the assessment, regardless of whether the vendor has answered it or supplied the required evidence.

No question may be excluded from the denominator because its response or evidence is incomplete.

**Total Maximum Question Points = Sum of (Question Weight × 4) for every question in the assessment.**
This ensures that missing responses or evidence do not reduce the denominator and artificially lower the risk percentage.

### 6.4 Risk Percentage Formula

**Risk Percentage = (Total Weighted Risk Points ÷ Total Maximum Question Points) × 100**

Where:

- Total Weighted Risk Points is the sum of the weighted risk points for every question.
- Total Maximum Question Points is the sum of the maximum possible points for every question.

A higher percentage represents a greater level of identified control weakness.

### 6.5 Treatment of Unreviewed Responses and Required Evidence

The following rules apply:

1. Where a question has no reviewed answer, assign a risk value of 4.
2. Where evidence is required but its status is Missing, Received, Rejected or Expired, assign a risk value of 4.
3. Where required evidence has been Accepted and the response has been reviewed, assign the risk value based on the verified answer and the question's acceptance criteria.
4. Where evidence is not required, the response must still be reviewed before a verified risk value can be assigned.
5. A vendor claim without reviewer verification must not receive verified credit.

These rules ensure that unanswered questions and unresolved evidence requirements remain visible in the calculated risk result.

## 7. Assessment Completeness

Assessment completeness must be calculated separately from the risk percentage.

An assessment is **Incomplete** if at least one of the following conditions applies:

- One or more questionnaire questions have no reviewer-verified answer.
- One or more questions requiring evidence have an evidence status other than Accepted.
- One or more critical-failure questions remain unresolved.
- A required response or evidence review is still outstanding.

An assessment may be treated as complete only when every questionnaire question has a reviewed answer, every required evidence item has been Accepted, and no critical-failure question remains unresolved.

The toolkit must display the assessment status separately from its calculated risk percentage.

An incomplete assessment must not be presented as a favourable completed assessment.
An assessment must not be marked Complete while any questionnaire response remains unreviewed or any required evidence remains in a status other than Accepted.

## 8. Critical-Failure Rules

Some questionnaire questions are marked with:

`critical_failure_flag = Yes`

A critical-failure question identifies a control weakness that cannot be treated as an ordinary scoring issue.

The following rules apply:

### 8.1 Confirmed Critical Failure

Where the reviewer has verified a failure against the acceptance criteria of a critical-failure question:

- The toolkit must flag the issue clearly as a Critical Failure.
- The issue must be linked to the relevant question.
- Supporting evidence and reviewer notes must be retained.
- The question must receive a risk value of 4.
- The overall risk rating must be at least High.
- If the calculated risk rating is already Critical, it must remain Critical.
- The authorised approver must consider the finding before making a decision.

A confirmed critical failure must not be averaged away by strong performance in other questionnaire areas.

### 8.2 Unresolved Critical-Failure Question

A critical-failure question is unresolved where:

- No reviewer-verified answer exists; or
- Required evidence is Missing, Received, Rejected or Expired; or
- The available information is insufficient for the reviewer to determine whether the required control is effective.

An unresolved critical-failure question must cause the assessment to be marked Incomplete.

The toolkit must not treat an unresolved critical-failure question as a confirmed passing control.

The assessment must remain Incomplete until the reviewer resolves the outstanding issue.

## 9. Proposed Risk Rating Bands

The following percentage bands are proposed for team review.

| Risk Percentage | Proposed Rating |
|---|---|
| 0% to less than 20% | Low |
| 20% to less than 40% | Medium |
| 40% to less than 60% | High |
| 60% to 100% | Critical |

These thresholds are not yet approved.

Where a confirmed critical failure exists, the final risk rating must be no lower than High, regardless of the calculated percentage.

Where an assessment is Incomplete, the toolkit must display the calculated percentage as provisional and clearly identify the outstanding questions or evidence requirements.

The final thresholds must be agreed by the scoring owner and project lead before implementation.

## 10. Incomplete Assessments

The toolkit must automatically mark an assessment as Incomplete whenever any of the conditions in Section 7 is met.

The toolkit must:

- Identify the unanswered or unreviewed questions.
- Identify questions with Missing evidence.
- Identify questions with Received evidence awaiting review.
- Identify questions with Rejected evidence.
- Identify questions with Expired evidence.
- Identify unresolved critical-failure questions.
- Display the calculated risk percentage as provisional.
- Prevent an incomplete assessment from being presented as a favourable completed assessment.

The assessment may be changed from Incomplete only after all outstanding review and evidence requirements have been resolved.

## 11. Risk Rating and Approval Decision

The calculated risk rating and the approval decision are separate records.

The project data dictionary defines the following decision outcomes:

- Approved.
- Conditionally Approved.
- Rejected.

The authorised approver makes the final decision.

The approver should consider:

- The calculated risk rating.
- Critical-failure findings.
- Evidence quality and completeness.
- Business criticality.
- Open corrective actions.
- Material changes.
- The business justification for using the vendor.

The toolkit must not automatically approve a vendor based on a favourable score.

An Incomplete assessment must not be treated as a completed favourable assessment. The approver must consider the outstanding issues before making an appropriate decision.

The decision must include:

- Decision outcome.
- Decision-maker role.
- Decision justification.
- Conditions, where applicable.
- Condition deadline, where applicable.
- Decision date.
- Expiry date.
- Review date.

The decision-maker must not be the same person as the assessor.

## 12. Reassessment

A new assessment should be created when:

- A scheduled review becomes due.
- A material change occurs.
- The vendor receives increased system access.
- A new data type is introduced.
- A new subcontractor is introduced.
- The vendor's service scope changes.
- Evidence expires.
- An existing approval expires.

Each new assessment must have a unique assessment ID.

Submitted assessments must not be edited. A new assessment version must be created, and the previous assessment must be retained and marked Superseded.

## 13. Audit and Reporting

The toolkit should retain the information used to calculate each result.

Reports should identify:

- Vendor ID and name.
- Assessment ID and version.
- Assessment completeness.
- Calculated risk percentage.
- Final risk rating.
- Critical-failure findings.
- Missing, rejected or expired evidence.
- Open findings.
- Overdue corrective actions.
- Approval outcome.
- Approval expiry date.
- Reassessment status.

Changes to assessment records, evidence verification and approval decisions should be recorded in the reviewer audit log.

## 14. Governance and Approval

The proposed scoring formula, risk values, rating thresholds and critical-failure treatment must be reviewed and approved before implementation.

The approved method should be version-controlled.

Any subsequent changes must be documented and reflected in the toolkit's calculation logic and test cases.
