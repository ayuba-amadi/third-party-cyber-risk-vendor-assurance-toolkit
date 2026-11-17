# Requirements Traceability Matrix

Version: Day 1 v1.0, ready for review. Date: 16 November 2026.
All data is fictional. Acceptance test IDs (T01 to T13) are defined in the index at the end and get exact expected results on Day 3.

## Requirements traceability

R01 to R08: required components. D01 to D08: demonstration data scenarios. Q01 to Q10: live demonstration actions.

| Requirement ID | Brief requirement / demo action | Input fields | Processing rule | Output / report field | Acceptance case ID | Owner | Status |
|---|---|---|---|---|---|---|---|
| R01 | Vendor register with unique vendor IDs | vendor, business_service, vendor_service_link | Validate vendor_id format and uniqueness; check required fields and allowed values; check orphan links | Clean register; rejected rows listed with reason | T01, T02 | Foka Averil | Ready for review |
| R02 | Vendor criticality assessment (Low, Medium, High, Critical) | Register fields: data sensitivity, system access, dependency impact, replaceability | Weighted factor score mapped to threshold bands; documented overrides; missing input handling | Band, factor points, reasons text | T03, T04 | Foka Averil | Ready for review |
| R03 | Security due diligence questionnaire, 24+ questions | question_bank, response | One response per vendor per question per assessment; completeness count per domain | Response set per assessment; completeness percentage | T05, T13 | Foka Averil | Ready for review |
| R04 | Evidence assessment: claim versus reviewer-verified | evidence_item, response | Evidence status drives verified flag; only Accepted evidence earns credit | Verified or unverified per response; missing evidence list | T05, T07 | Foka Averil | Ready for review |
| R05 | Automated analysis: validation, scoring, critical weakness, overdue review | All assessment tables | Validation checks; weighted score with denominators; critical-failure override; overdue date tests; incomplete flag | Score, rating, flags, calculation trail | T02, T06, T09 | Foka Averil | Ready for review |
| R06 | Approval and exception records | decision | Score informs; authorised approver records outcome, justification, conditions, deadlines, review and expiry dates | Decision record; expired approval flag | T08, T09 | Foka Averil | Ready for review |
| R07 | Remediation and reassessment tracking | finding, corrective_action, assessment, change_event | Link findings to actions; flag overdue actions; material change triggers reassessment; prior versions retained | Action tracker; version history; trigger list | T08, T10 | Foka Averil | Ready for review |
| R08 | Management reporting | All tables | Count each vendor once; list critical vendors, open findings, overdue reviews, open conditions; concentration by service | Summary report with source ID lists; reconciliation | T11, T12 | Foka Averil | Ready for review |
| D01 | 10+ vendors across five categories | 10 vendor rows | Category count check | 5 categories, 2 vendors each | T01 | Foka Averil | Ready for review |
| D02 | At least three vendors supporting business-critical services | vendor_service_link with service tier | Count vendors linked to business-critical services | VEN-001, VEN-002, VEN-003 | T11 | Foka Averil | Ready for review |
| D03 | Critical vendor with missing security evidence | VEN-002 evidence rows with status Missing | Missing evidence scores zero; incomplete flag | VEN-002 rating Incomplete, not favourable | T05 | Foka Averil | Ready for review |
| D04 | Vendor with rejected or expired evidence | VEN-005 rejected item; VEN-006 expired item | Rejected and expired earn no credit | Evidence flags on both vendors | T07 | Foka Averil | Ready for review |
| D05 | Conditionally approved vendor with overdue corrective action | VEN-003 decision and action | Due date earlier than report date and status not Closed | Overdue action flagged | T08 | Foka Averil | Ready for review |
| D06 | One vendor supporting several important services | VEN-001 linked to SVC-01, SVC-03, SVC-04, SVC-05 | Count services per vendor | Concentration flag on VEN-001 | T11 | Foka Averil | Ready for review |
| D07 | Vendor reassessed after material change | VEN-004 change_event and two assessments | Change triggers reassessment; v1 kept, v2 created | Comparison v1 versus v2 | T10 | Foka Averil | Ready for review |
| D08 | Questionnaire populated for all 10 vendors | 240+ response rows | Row count per assessment | 24 or more rows per vendor; VEN-010 deliberately partial | T05 | Foka Averil | Ready for review |
| Q01 | Enter or import a new vendor and calculate criticality | New vendor VEN-011 (demo) | Validate, score factors, map to band | Band with factor points | T03 | Foka Averil | Ready for review |
| Q02 | Change access or dependency and explain new classification | Edit VEN-011 system access and dependency | Recalculate; show points that moved | Higher band with reason text | T04 | Foka Averil | Ready for review |
| Q03 | Process questionnaire responses and identify missing evidence | VEN-002 responses and evidence | Match responses to evidence status | List of missing evidence by question | T05 | Foka Averil | Ready for review |
| Q04 | Show a critical weakness cannot be hidden by strong scores | VEN-009 responses | Critical-failure override | Rating capped despite high aggregate | T06 | Foka Averil | Ready for review |
| Q05 | Generate a vendor assessment report with reasons | Any assessed vendor | Compile score, flags, evidence, reasons | Per-vendor report | T13 | Foka Averil | Ready for review |
| Q06 | Record conditional approval and assign corrective actions | VEN-005 | Create decision and action rows | Decision record with conditions and deadlines | T08 | Foka Averil | Ready for review |
| Q07 | Display overdue actions and an expired assessment | VEN-003, VEN-006 | Date comparison against report date | Overdue and expired lists | T08, T09 | Foka Averil | Ready for review |
| Q08 | Reassess a vendor while preserving the previous assessment | VEN-004 | New assessment_id; old row unchanged | Both versions retrievable | T10 | Foka Averil | Ready for review |
| Q09 | Show handling of invalid inputs, missing values, duplicate IDs | Deliberate bad rows | Validation checks | Rows rejected with reasons | T01, T02 | Foka Averil | Ready for review |
| Q10 | Reconcile management report totals to vendor records | Report and source tables | Sum by category, band, status | Totals equal source row counts | T12 | Foka Averil | Ready for review |

## Acceptance test index

| ID | Test case |
|---|---|
| T01 | Duplicate vendor_id |
| T02 | Missing required value and invalid status or enumeration |
| T03 | New vendor criticality calculation |
| T04 | Changed access or dependency changes the band |
| T05 | Incomplete questionnaire and missing evidence |
| T06 | Critical weakness override |
| T07 | Rejected and expired evidence |
| T08 | Conditional approval with overdue corrective action |
| T09 | Expired approval and overdue review |
| T10 | Reassessment preserving the previous assessment |
| T11 | Concentration risk |
| T12 | Management report reconciliation |
| T13 | Individual report shows supporting reasons |

## Traceability to files

| File | Covers |
|---|---|
| requirements_matrix.md | R01 to R08, D01 to D08, Q01 to Q10 |
| data_dictionary.md | R01, R03, R04, R06, R07 data structures |
| workflow.md | R05, R06, R07, R08 lifecycle and roles |
| demo_scenarios.md | D01 to D08 |
| criticality_method.md (Day 2) | R02 |
| question_bank.csv (Day 2) | R03 |
| risk_scoring_method.md (Day 2) | R05 |
| evidence_and_decision_rules.md (Day 2) | R04, R06 |
| acceptance_cases.md (Day 3) | T01 to T13 |

## Day 2 ownership and inputs

| Day 2 output | Owner | Uses from Day 1 |
|---|---|---|
| criticality_method.md | Colleague (claimed) | vendor fields and allowed values in data_dictionary.md; target bands in demo_scenarios.md |
| risk_scoring_method.md | Colleague (claimed) | response, evidence_item and finding tables; rules in workflow.md; tests T05 to T07 |
| question_bank.csv | Averil (claiming) | question table fields, domain codes, XX-## IDs; needs weight and severity scale from risk_scoring_method.md |
| evidence_and_decision_rules.md | Averil (claiming) | evidence_item and decision tables; evidence handling in workflow.md |
| worked_examples.md | Unclaimed | demo_scenarios.md vendors VEN-001 (favourable), VEN-009 (critical failure), VEN-002 (incomplete evidence) |

Rules every Day 2 file must respect: a calculated score never grants approval; missing, received-unreviewed, rejected and expired evidence never earn a favourable verified score; a critical failure cannot be averaged away.
