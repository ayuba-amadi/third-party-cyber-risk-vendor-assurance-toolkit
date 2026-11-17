# Data Dictionary

Version: Day 1 v1.0, ready for review. Date: 16 November 2026.
Req: R = required, O = optional. PK = primary key, FK = foreign key.

## Identifier rules
- vendor_id: VEN- plus 3 digits (VEN-001). Immutable. Never reused.
- assessment_id: ASMT- plus 3 digits (ASMT-001), unique across all vendors. One per assessment version.
- service_id: SVC- plus 2 digits (SVC-01).
- question_id: <domain code>-<2 digits> (AM-01). Domain codes: AM access management, DP data protection, IN incident notification, BC continuity and recovery, SC subcontractors, GV governance.
- evidence_id: EV- plus 3 digits. finding_id: FND- plus 3 digits. action_id: ACT- plus 3 digits.
- decision_id: DEC- plus 3 digits. change_id: CHG- plus 3 digits. audit_id: AUD- plus 4 digits.
- test case ID: T- plus 3 digits (T01).

## Data dictionary

Req column from earlier drafts is shown as Required (Yes or No). Examples are fictional and consistent with demo_scenarios.md where possible.

| Table | Field | Type | Required | Allowed values / constraint | Key or relationship | Example (fictional) |
|---|---|---|---|---|---|---|
| vendor | vendor_id | text | Yes | unique, immutable, nonblank, VEN-### pattern | primary key | VEN-001 |
| vendor | vendor_name | text | Yes | Fictional name |  | NimbusCloud Hosting |
| vendor | category | text | Yes | Cloud hosting, Payroll, Payment processing, Technical support, Collaboration SaaS |  | Cloud hosting |
| vendor | service_description | text | Yes | Free text, max 200 characters |  | Hosts customer portal and ERP |
| vendor | business_owner | text | Yes | Role title, no real names |  | Head of IT Operations |
| vendor | data_sensitivity | text | Yes | None, Internal, Confidential, Regulated |  | Regulated |
| vendor | data_types | text | No | Semicolon list (payroll, card data, HR, customer) |  | customer;payment |
| vendor | system_access | text | Yes | None, Standard, Privileged |  | Privileged |
| vendor | dependency_impact | integer | Yes | 1 to 4 (1 minor, 4 business-critical outage) |  | 4 |
| vendor | replaceability | text | Yes | Easy, Moderate, Hard, Very hard |  | Very hard |
| vendor | subcontractor_use | text | Yes | Yes, No, Unknown |  | Yes |
| vendor | assessment_status | text | Yes | Not started, In progress, Assessed, Reassessment due |  | Assessed |
| vendor | current_assessment_id | text | No | Must exist in assessment | foreign key to assessment | ASMT-001 |
| vendor | next_review_date | date | Yes | Not earlier than onboarding date |  | 2027-05-18 |
| vendor | material_change_flag | text | Yes | Yes, No |  | No |
| business_service | service_id | text | Yes | SVC-## pattern, unique | primary key | SVC-01 |
| business_service | service_name | text | Yes | Fictional business service |  | Customer portal |
| business_service | service_tier | text | Yes | Business-critical, Important, Standard |  | Business-critical |
| business_service | service_owner | text | Yes | Role title |  | Head of Digital |
| vendor_service_link | vendor_id | text | Yes | Must exist in vendor | foreign key to vendor; part of composite key | VEN-001 |
| vendor_service_link | service_id | text | Yes | Must exist in business_service | foreign key to business_service; part of composite key | SVC-01 |
| vendor_service_link | dependency_note | text | No | Free text |  | Hosts production database |
| assessment | assessment_id | text | Yes | ASMT-### pattern, unique | primary key | ASMT-001 |
| assessment | vendor_id | text | Yes | Must exist in vendor | foreign key to vendor | VEN-001 |
| assessment | version_no | integer | Yes | 1, 2, 3 in order per vendor |  | 1 |
| assessment | assessment_date | date | Yes | Valid date |  | 2026-05-18 |
| assessment | trigger | text | Yes | Initial, Periodic, Material change, Expiry |  | Initial |
| assessment | assessor_role | text | Yes | Role title |  | GRC analyst |
| assessment | status | text | Yes | Draft, Submitted, Superseded |  | Submitted |
| assessment | supersedes_id | text | No | Prior assessment_id for same vendor | foreign key to assessment | ASMT-009 (blank for version 1) |
| question | question_id | text | Yes | XX-## pattern (XX = domain code), unique | primary key | AM-01 |
| question | domain | text | Yes | AM Access management, DP Data protection, IN Incident notification, BC Continuity and recovery, SC Subcontractors, GV Governance |  | Access management |
| question | question_text | text | Yes | Answerable question |  | Is MFA enforced for all privileged vendor accounts? |
| question | response_options | text | Yes | Pipe-separated list |  | Yes, all|Partial|No |
| question | weight | integer | Yes | 1 to 5 |  | 5 |
| question | evidence_required | text | Yes | Yes, No |  | Yes |
| question | evidence_description | text | No | Artifact and review period |  | MFA policy and admin account export, last 12 months |
| question | acceptance_criteria | text | No | What the reviewer checks |  | Export shows MFA on 100% of admin accounts |
| question | critical_failure_flag | text | Yes | Yes, No |  | Yes |
| response | assessment_id | text | Yes | Must exist in assessment | foreign key to assessment; part of composite key | ASMT-001 |
| response | question_id | text | Yes | Must exist in question | foreign key to question; part of composite key | AM-01 |
| response | vendor_claim | text | Yes | One of the question's options, or Blank |  | Yes, all |
| response | reviewer_verified | text | Yes | Yes, No, Not reviewed |  | Yes |
| response | verified_answer | text | No | Required if reviewer_verified is Yes |  | Yes, all |
| response | reviewer_note | text | No | Free text |  | Export checked, all admins enrolled |
| evidence_item | evidence_id | text | Yes | EV-### pattern, unique | primary key | EV-001 |
| evidence_item | assessment_id | text | Yes | Must exist in assessment | foreign key to assessment | ASMT-001 |
| evidence_item | question_id | text | Yes | Must exist in question | foreign key to question | AM-01 |
| evidence_item | status | text | Yes | Missing, Received, Accepted, Rejected, Expired |  | Accepted |
| evidence_item | received_date | date | No | Required if status is not Missing |  | 2026-05-10 |
| evidence_item | review_period_end | date | No | End of period the evidence covers |  | 2026-04-30 |
| evidence_item | expiry_date | date | No | Required if status is Accepted |  | 2027-04-30 |
| evidence_item | reviewer_role | text | No | Required if status is Accepted or Rejected |  | Security reviewer |
| evidence_item | reference_path | text | No | Fictional file path or link |  | evidence/VEN-001/mfa-export.pdf |
| evidence_item | reason | text | No | Required if status is Rejected |  | Report period outside last 12 months (Rejected case) |
| finding | finding_id | text | Yes | FND-### pattern, unique | primary key | FND-001 |
| finding | assessment_id | text | Yes | Must exist in assessment | foreign key to assessment | ASMT-003 |
| finding | question_id | text | No | Source question | foreign key to question | AM-01 |
| finding | severity | text | Yes | Low, Medium, High, Critical |  | High |
| finding | description | text | Yes | Free text |  | MFA not enforced for 3 admin accounts |
| finding | status | text | Yes | Open, Remediating, Closed, Risk accepted |  | Open |
| corrective_action | action_id | text | Yes | ACT-### pattern, unique | primary key | ACT-001 |
| corrective_action | finding_id | text | Yes | Must exist in finding | foreign key to finding | FND-001 |
| corrective_action | vendor_id | text | Yes | Must match the finding's vendor | foreign key to vendor | VEN-003 |
| corrective_action | action_text | text | Yes | Free text |  | Enforce MFA on all admin accounts |
| corrective_action | responsible_party | text | Yes | Role title, vendor or internal |  | Vendor security lead |
| corrective_action | due_date | date | Yes | Valid date |  | 2026-10-31 |
| corrective_action | status | text | Yes | Open, In progress, Closed |  | Open |
| corrective_action | closed_date | date | No | Required if status is Closed |  | 2026-11-02 (Closed case) |
| decision | decision_id | text | Yes | DEC-### pattern, unique | primary key | DEC-001 |
| decision | assessment_id | text | Yes | Must exist in assessment | foreign key to assessment | ASMT-003 |
| decision | calculated_rating | text | Yes | Copied from calculation at decision time |  | Critical |
| decision | outcome | text | Yes | Approved, Conditionally Approved, Rejected |  | Conditionally Approved |
| decision | decision_maker_role | text | Yes | Authorised approver role, not the assessor |  | Head of Risk |
| decision | justification | text | Yes | Free text |  | Strong controls; MFA gap has a dated fix |
| decision | conditions | text | No | Required if Conditionally Approved |  | Enforce admin MFA |
| decision | condition_deadline | date | No | Required if Conditionally Approved |  | 2026-10-31 |
| decision | decision_date | date | Yes | Valid date |  | 2026-09-30 |
| decision | expiry_date | date | Yes | After decision_date |  | 2027-09-30 |
| decision | review_date | date | Yes | On or before expiry_date |  | 2027-06-30 |
| change_event | change_id | text | Yes | CHG-### pattern, unique | primary key | CHG-001 |
| change_event | vendor_id | text | Yes | Must exist in vendor | foreign key to vendor | VEN-004 |
| change_event | change_date | date | Yes | Valid date |  | 2026-09-15 |
| change_event | change_type | text | Yes | New subcontractor, Scope increase, Access increase, Data type added, Ownership change, Other |  | New subcontractor |
| change_event | material | text | Yes | Yes, No |  | Yes |
| change_event | reassessment_assessment_id | text | No | Filled once reassessment starts | foreign key to assessment | ASMT-011 |
| reviewer_audit_entry | audit_id | text | Yes | AUD-#### pattern, unique | primary key | AUD-0001 |
| reviewer_audit_entry | timestamp | datetime | Yes | ISO 8601 |  | 2026-11-17T09:30:00+01:00 |
| reviewer_audit_entry | actor_role | text | Yes | Role title |  | Security reviewer |
| reviewer_audit_entry | action | text | Yes | Created, Edited, Verified, Rejected, Decided, Closed |  | Verified |
| reviewer_audit_entry | table_name | text | Yes | One of the tables above |  | evidence_item |
| reviewer_audit_entry | record_id | text | Yes | ID of the affected record |  | EV-001 |
| reviewer_audit_entry | note | text | No | Free text |  | Accepted after review |

## Notes
- Composite keys: vendor_service_link is unique on vendor_id plus service_id; response is unique on assessment_id plus question_id.
- Criticality band is calculated, not stored in the input vendor table.
- Submitted assessments are never edited; a change creates a new assessment row and marks the old one Superseded.

## Integrity checks
| Check | Rule | Result on failure |
|---|---|---|
| Duplicate keys | Any PK or composite key appearing twice | Reject later row; log both row numbers |
| Orphan records | Any FK not found in the parent table | Reject row; list in validation report |
| Enumerations | Value not in allowed list | Reject row; show allowed values |
| Required fields | Required field blank | Reject row, or mark assessment Incomplete for response gaps |
| Date logic | expiry before decision, due before finding, review after expiry | Flag row |
| Version continuity | version_no gaps, or edits to Superseded rows | Flag assessment |
| Evidence consistency | Accepted without reviewer or expiry; Rejected without reason | Flag evidence row |
| Decision independence | decision_maker_role equals assessor_role | Flag decision |
