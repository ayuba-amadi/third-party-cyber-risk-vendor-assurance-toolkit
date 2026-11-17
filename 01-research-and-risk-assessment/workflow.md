# Vendor Assurance Workflow

Version: Day 1 v1.0, ready for review. Date: 16 November 2026.

## Roles
| Role | Responsibility |
|---|---|
| Business owner | Requests the vendor; supplies service, data and dependency facts |
| Assessor (GRC analyst) | Creates the vendor and assessment records; sends the questionnaire; logs vendor claims |
| Reviewer | Verifies evidence; sets evidence status and reviewer-verified answers |
| Approver | Authorised decision-maker; records the final outcome. Must differ from the assessor |
| Toolkit (automation) | Validates, calculates, flags and reports. Never records a decision |

Rule: a calculated score never grants approval. It is an input to the Approver.

## Lifecycle
| Step | Stage | Who creates | Who reviews | Who approves | Output |
|---|---|---|---|---|---|
| 1 | New vendor | Business owner and Assessor | Assessor | n/a | Vendor register row, service links |
| 2 | Criticality | Toolkit | Assessor confirms inputs | n/a | Band with reasons |
| 3 | Questionnaire | Assessor issues; vendor claims logged | Assessor checks completeness | n/a | Response rows |
| 4 | Evidence review | Vendor supplies artifacts | Reviewer | n/a | Evidence status per item |
| 5 | Risk calculation | Toolkit | Assessor | n/a | Score, rating, flags, calculation trail |
| 6 | Decision | Approver | Reviewer | Approver | Approved, Conditionally Approved or Rejected |
| 7 | Actions | Assessor raises findings and actions | Reviewer | Approver for risk acceptance | Corrective action tracker |
| 8 | Reassessment | Assessor | Reviewer | Approver | New assessment version; old one retained |
| 9 | Reporting | Toolkit | Assessor | Team lead or risk owner | Vendor reports, management report |

## Triggers for reassessment
1. next_review_date is earlier than the report date (overdue review).
2. Decision expiry_date is earlier than the report date (expired approval).
3. A change_event with material = Yes is logged.
4. A corrective action passes its due date without closure on a conditional approval.
5. Accepted evidence for a critical-failure question expires.

## Evidence handling in the flow
- A vendor claim is recorded in response.vendor_claim. It is not verified.
- Only evidence with status Accepted lets a response be marked reviewer_verified = Yes.
- Missing, Received (unreviewed), Rejected and Expired evidence all leave the response unverified, so it earns no credit.

## Version retention
- Every assessment gets a new assessment_id. Submitted assessments are never edited; changes create a new version and mark the old one Superseded.
- Decisions, findings and actions stay linked to the assessment they were raised in.
- Every create, edit, verify and decide action writes a reviewer_audit_entry.

## Storage and access (specification for Development)
- Source tables live in the repository sample-data/ folder as CSV. Production-style use would be a restricted shared location.
- Approver and Reviewer roles write to decision and evidence tables; Assessors cannot write decisions.
- Worksheet protection is not an access control. File-level permissions and repository permissions are the access control.
- Version retention uses repository commits plus the assessment version rows.

## Duplicate and orphan handling
- Duplicate vendor_id: the second row is rejected, both row numbers are logged, calculation continues for the first.
- Orphan response, evidence, finding or action: row excluded from calculation and listed in the validation report.

## Open decisions for the team lead (to log in HANDOFFS.md)
1. Whether the build format is an Excel workbook or Python scripts, since the CSV layout stays the same either way.
2. Whether the Approver role may also be the Reviewer.
3. Standard evidence validity period (proposal: 12 months, 6 months for incident-response testing).
