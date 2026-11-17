# Demonstration Scenarios: Ten-Vendor Map

Version: Day 1 v1.0, ready for review. Date: 16 November 2026.
Expected bands below are targets; Day 2 scoring rules must reproduce them, and any mismatch is logged for the team lead.

## Business services
| service_id | Service | Tier |
|---|---|---|
| SVC-01 | Customer portal | Business-critical |
| SVC-02 | Payroll run | Business-critical |
| SVC-03 | Card payments | Business-critical |
| SVC-04 | Core ERP | Important |
| SVC-05 | Staff email and collaboration | Important |
| SVC-06 | IT helpdesk | Standard |
| SVC-07 | Data backup and recovery | Important |
| SVC-08 | Contract and legal documents | Important |

## Vendor matrix
| vendor_id | Vendor | Category | Services | Target band | Scenario |
|---|---|---|---|---|---|
| VEN-001 | NimbusCloud Hosting | Cloud hosting | SVC-01, SVC-03, SVC-04, SVC-05 | Critical | Multi-service concentration (D06); strong evidence; Approved |
| VEN-002 | PayStream Processing | Payment processing | SVC-03 | Critical | Missing evidence on critical-failure questions (D03); rating Incomplete; decision pending |
| VEN-003 | SalaryBridge Payroll | Payroll | SVC-02 | Critical | Conditionally Approved; overdue corrective action (D05) |
| VEN-004 | SwiftPay Gateway | Payment processing | SVC-03 | High then Critical | Material change: new subcontractor and privileged API access; v1 retained, v2 reassessment (D07) |
| VEN-005 | HelpDeskPro Support | Technical support | SVC-06 | Medium | Rejected evidence item (D04); Conditionally Approved, condition not yet due |
| VEN-006 | SecureTech Managed IT | Technical support | SVC-04, SVC-06 | High | Expired evidence and expired approval (D04); reassessment due |
| VEN-007 | CoreData Backup | Cloud hosting | SVC-07 | High | Favourable assessment; Approved |
| VEN-008 | TalentPay HR | Payroll | none business-critical | Medium | Favourable assessment; Approved |
| VEN-009 | LegalDocs Storage | Collaboration SaaS | SVC-08 | High | Strong overall scores but critical failure on data protection; override; Rejected |
| VEN-010 | BrightMeet Collaboration | Collaboration SaaS | SVC-05 | Low | Incomplete assessment: 14 of 24 questions answered; status In progress |
| VEN-011 | Reserved for live demo | Any | Any | Calculated live | Used for Q01 and Q02; not in the stored data |

## Scenario coverage
| Scenario | Vendors | Requirement |
|---|---|---|
| 10 vendors, five categories, two per category | VEN-001 to VEN-010 | D01 |
| Three vendors supporting business-critical services | VEN-001, VEN-002, VEN-003 (VEN-004 also supports SVC-03) | D02 |
| Critical vendor with missing evidence | VEN-002 | D03 |
| Rejected evidence | VEN-005 | D04 |
| Expired evidence | VEN-006 | D04 |
| Conditionally approved with overdue action | VEN-003 (action due 2026-10-31, still Open) | D05 |
| Vendor supporting several important services | VEN-001 (4 services) | D06 |
| Reassessment after material change | VEN-004 | D07 |
| Questionnaire populated for all vendors | VEN-001 to VEN-010 (24+ rows each, VEN-010 partial) | D08 |
| Invalid input, missing value, duplicate ID demonstrations | Deliberate bad rows in a separate test file, not in the main data | Q09 |

## Response profile per vendor (target, Day 3 fills rows)
| Vendor | Favourable | Unfavourable | Incomplete | Notes |
|---|---|---|---|---|
| VEN-001 | High | Low | None | Accepted evidence for all critical questions |
| VEN-002 | Medium | Medium | Critical-failure evidence Missing | Cannot be favourable |
| VEN-003 | Medium | One High finding (admin MFA gap) | None | Action CA due 2026-10-31 |
| VEN-004 v1 | High | Low | None | Approved before the change |
| VEN-004 v2 | Medium | Medium | Subcontractor evidence Received only | After change on 2026-09-15 |
| VEN-005 | Medium | Low | One item Rejected (out-of-period test report) | Condition: resubmit by 2026-12-15 |
| VEN-006 | Medium | Low | SOC-style report Expired 2026-08-31 | Approval expired 2026-10-31 |
| VEN-007 | High | None | None | Clean |
| VEN-008 | High | Low | None | Clean |
| VEN-009 | High on access and governance | Critical failure: no encryption evidence for regulated data | None | Shows override |
| VEN-010 | Medium | Low | 10 questions unanswered | Flagged Incomplete |

## Expected management report totals (target)
| Measure | Expected |
|---|---|
| Vendors in register | 10 |
| By category | 2 per category |
| Critical band vendors | VEN-001, VEN-002, VEN-003, VEN-004 (after reassessment) |
| Overdue corrective actions | 1 (VEN-003) |
| Expired approvals | 1 (VEN-006) |
| Incomplete assessments | VEN-002, VEN-010 |
| Rejected outcomes | 1 (VEN-009) |
| Concentration: services with more than one vendor | SVC-03 (VEN-001, VEN-002, VEN-004), SVC-05 (VEN-001, VEN-010), SVC-04 (VEN-001, VEN-006) |

Day 3 must verify these totals against the final source data and correct this file where they differ.
