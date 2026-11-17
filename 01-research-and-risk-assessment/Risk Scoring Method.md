# Vendor Risk Scoring Method

**Project:** Third-Party Cyber Risk Assessment and Vendor Assurance Toolkit  
**Document Owner:** Saadu Shukurat Titilayo  
**Subgroup:** Research and Risk Assessment  
**Version:** 0.1 DRAFT  
**Date:** 17 November 2026  
**Status:** Draft – Pending Team Review

---

## 1. Purpose

This document defines a proposed method for calculating and interpreting vendor security risk assessment results.

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
| Missing | Evidence has not been provided | No verified credit |
| Received | Evidence has been submitted but not yet accepted | No verified credit |
| Accepted | Evidence has been reviewed and accepted | Eligible for verified credit |
| Rejected | Evidence has been reviewed and rejected | No verified credit |
| Expired | Evidence is no longer valid | No verified credit |

For evidence to be Accepted:

- A reviewer role must be recorded.
- An expiry date must be recorded.
- The evidence must satisfy the relevant acceptance criteria.

Rejected evidence must include a reason.

An Accepted evidence status does not automatically mean that the vendor's control is effective. The reviewer must still record the verified answer based on the evidence.

## 6. Proposed Scoring Approach

The project requires a weighted score with a denominator.

The following is a proposed calculation structure for team review.

Each question is assigned a verified risk value based on the reviewed answer and the question's acceptance criteria.

For the proposed model:

| Verified Risk Value | Interpretation |
|---|---|
| 0 | No identified control weakness |
| 1 | Minor control weakness |
| 2 | Moderate control weakness |
| 3 | Significant control weakness |
| 4 | Severe control weakness |

The reviewer must assign the value based on the question's documented acceptance criteria. The value must not be assigned merely because the vendor selected a particular response.

### Proposed Weighted Formula

For each eligible question:

**Weighted Risk Points = Question Weight × Verified Risk Value**

The maximum possible weighted risk points for a question are:

**Maximum Question Points = Question Weight × 4**

The overall proposed risk percentage is:

**Risk Percentage = (Total Weighted Risk Points ÷ Total Maximum Eligible Question Points) × 100**

A higher percentage represents a greater level of identified control weakness.

This formula and the interpretation of the risk values are proposals. The team must approve them before they are used in the toolkit.

## 7. Assessment Completeness

The toolkit must calculate assessment completeness separately from the risk percentage.

**Completion Percentage = (Number of Questions with Reviewed Responses ÷ Total Questions in Assessment) × 100**

The toolkit should also identify:

- Questions with no vendor response.
- Questions awaiting reviewer verification.
- Questions requiring evidence.
- Questions with Missing evidence.
- Questions with Received evidence awaiting review.
- Questions with Rejected evidence.
- Questions with Expired evidence.

An assessment must not be presented as fully assessed merely because the vendor has submitted responses.

## 8. Critical-Failure Rules

Some questionnaire questions are marked with:

`critical_failure_flag = Yes`

A critical-failure question identifies a control weakness that cannot be treated as an ordinary scoring issue.

Where a critical-failure condition is confirmed:

- The toolkit must flag the issue clearly.
- The issue must be linked to the relevant question.
- Supporting evidence and reviewer notes must be retained.
- The overall assessment must not be treated as favourable merely because other questions have good scores.
- The calculated rating must reflect the approved critical-failure rule.
- The authorised approver must consider the finding before making a decision.

A critical failure must not be averaged away by strong performance in other questionnaire areas.

Where required evidence is Missing, Received, Rejected, or Expired for a critical-failure question, the assessment must be flagged as incomplete or unresolved until the issue is reviewed.

The team must confirm the exact rating treatment for confirmed critical failures before implementation.

## 9. Proposed Risk Rating Bands

The following percentage bands are proposed for team review.

| Risk Percentage | Proposed Rating |
|---|---|
| 0–19% | Low |
| 20–39% | Medium |
| 40–59% | High |
| 60–100% | Critical |

These thresholds are not yet approved.

The final thresholds must be agreed by the scoring owner and project lead before the toolkit uses them.

## 10. Incomplete Assessments

An incomplete assessment must be identified separately from a completed risk assessment.

Examples include:

- Required questions have not been answered.
- Evidence required for a question has not been received.
- Evidence has been received but has not been reviewed.
- Critical-failure questions remain unresolved.
- The reviewer has not verified the relevant response.

An incomplete assessment must not be reported as a favourable completed assessment.

Where the available information is insufficient to calculate a reliable final score, the toolkit should display the assessment as incomplete and identify the outstanding items.

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
- Calculated risk rating.
- Critical-failure findings.
- Missing, rejected, or expired evidence.
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

---

