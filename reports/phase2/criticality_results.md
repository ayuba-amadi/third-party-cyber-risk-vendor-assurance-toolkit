# Phase 2 criticality results

Phase 2 implements semantic validation and vendor criticality calculation only. Risk scoring, evidence scoring, decision workflow, remediation workflow, management reporting and the Streamlit interface are later-phase work.

Execution date (UTC): 2026-11-26

Report date: 2026-11-18

Source directory: /home/amadi/Documents/GitHub/third-party-cyber-risk-vendor-assurance-toolkit/sample-data

## Calculation methodology

Data sensitivity + system access + dependency impact + replaceability

| Total points | Base band |
|---:|---|
| 2-3 | Low |
| 4-6 | Medium |
| 7-9 | High |
| 10-13 | Critical |

Overrides:

- Business-critical service sets a minimum band of High.
- Regulated data plus Privileged access sets Critical.
- Dependency impact 4 plus Very hard replacement sets Critical.

## Assessment results

| Vendor | Name | Assessment | Factors (points) | Total | Base | Overrides | Final | Complete |
|---|---|---|---|---:|---|---|---|---|
| VEN-001 | NimbusCloud Hosting | ASMT-001 | Regulated (3), Privileged (2), 4 (4), Very hard (4) | 13 | Critical | Business-critical service floor; Regulated plus privileged; Severe dependency plus very hard replacement | Critical | True |

**Calculation trace**
- Assessment: ASMT-001
- Vendor: VEN-001
- Data Sensitivity: Regulated = 3
- System Access: Privileged = 2
- Dependency Impact: 4 = 4
- Replaceability: Very hard = 4
- Base score: 3 + 2 + 4 + 4 = 13
- Base band: Critical
- Linked services: SVC-01, SVC-03, SVC-04, SVC-05
- Highest linked service tier: Business-critical
- Overrides: Business-critical service floor; Regulated plus privileged; Severe dependency plus very hard replacement
- Final band: Critical
| VEN-002 | PayStream Processing | ASMT-002 | Regulated (3), Privileged (2), 4 (4), Hard (3) | 12 | Critical | Business-critical service floor; Regulated plus privileged | Critical | True |

**Calculation trace**
- Assessment: ASMT-002
- Vendor: VEN-002
- Data Sensitivity: Regulated = 3
- System Access: Privileged = 2
- Dependency Impact: 4 = 4
- Replaceability: Hard = 3
- Base score: 3 + 2 + 4 + 3 = 12
- Base band: Critical
- Linked services: SVC-03
- Highest linked service tier: Business-critical
- Overrides: Business-critical service floor; Regulated plus privileged
- Final band: Critical
| VEN-003 | SalaryBridge Payroll | ASMT-003 | Regulated (3), Standard (1), 4 (4), Very hard (4) | 12 | Critical | Business-critical service floor; Severe dependency plus very hard replacement | Critical | True |

**Calculation trace**
- Assessment: ASMT-003
- Vendor: VEN-003
- Data Sensitivity: Regulated = 3
- System Access: Standard = 1
- Dependency Impact: 4 = 4
- Replaceability: Very hard = 4
- Base score: 3 + 1 + 4 + 4 = 12
- Base band: Critical
- Linked services: SVC-02
- Highest linked service tier: Business-critical
- Overrides: Business-critical service floor; Severe dependency plus very hard replacement
- Final band: Critical
| VEN-004 | SwiftPay Gateway | ASMT-004 | Regulated (3), Standard (1), 3 (3), Moderate (2) | 9 | High | Business-critical service floor | High | True |

**Calculation trace**
- Assessment: ASMT-004
- Vendor: VEN-004
- Data Sensitivity: Regulated = 3
- System Access: Standard = 1
- Dependency Impact: 3 = 3
- Replaceability: Moderate = 2
- Base score: 3 + 1 + 3 + 2 = 9
- Base band: High
- Linked services: SVC-03
- Highest linked service tier: Business-critical
- Overrides: Business-critical service floor
- Final band: High
| VEN-005 | HelpDeskPro Support | ASMT-005 | Internal (1), Standard (1), 2 (2), Moderate (2) | 6 | Medium | None | Medium | True |

**Calculation trace**
- Assessment: ASMT-005
- Vendor: VEN-005
- Data Sensitivity: Internal = 1
- System Access: Standard = 1
- Dependency Impact: 2 = 2
- Replaceability: Moderate = 2
- Base score: 1 + 1 + 2 + 2 = 6
- Base band: Medium
- Linked services: SVC-06
- Highest linked service tier: Standard
- Overrides: none
- Final band: Medium
| VEN-006 | SecureTech Managed IT | ASMT-006 | Confidential (2), Privileged (2), 3 (3), Moderate (2) | 9 | High | None | High | True |

**Calculation trace**
- Assessment: ASMT-006
- Vendor: VEN-006
- Data Sensitivity: Confidential = 2
- System Access: Privileged = 2
- Dependency Impact: 3 = 3
- Replaceability: Moderate = 2
- Base score: 2 + 2 + 3 + 2 = 9
- Base band: High
- Linked services: SVC-04, SVC-06
- Highest linked service tier: Important
- Overrides: none
- Final band: High
| VEN-007 | CoreData Backup | ASMT-007 | Confidential (2), Standard (1), 3 (3), Hard (3) | 9 | High | None | High | True |

**Calculation trace**
- Assessment: ASMT-007
- Vendor: VEN-007
- Data Sensitivity: Confidential = 2
- System Access: Standard = 1
- Dependency Impact: 3 = 3
- Replaceability: Hard = 3
- Base score: 2 + 1 + 3 + 3 = 9
- Base band: High
- Linked services: SVC-07
- Highest linked service tier: Important
- Overrides: none
- Final band: High
| VEN-008 | TalentPay HR | ASMT-008 | Confidential (2), None (0), 2 (2), Moderate (2) | 6 | Medium | None | Medium | True |

**Calculation trace**
- Assessment: ASMT-008
- Vendor: VEN-008
- Data Sensitivity: Confidential = 2
- System Access: None = 0
- Dependency Impact: 2 = 2
- Replaceability: Moderate = 2
- Base score: 2 + 0 + 2 + 2 = 6
- Base band: Medium
- Linked services: none
- Highest linked service tier: None
- Overrides: none
- Final band: Medium
| VEN-009 | LegalDocs Storage | ASMT-009 | Regulated (3), Standard (1), 3 (3), Moderate (2) | 9 | High | None | High | True |

**Calculation trace**
- Assessment: ASMT-009
- Vendor: VEN-009
- Data Sensitivity: Regulated = 3
- System Access: Standard = 1
- Dependency Impact: 3 = 3
- Replaceability: Moderate = 2
- Base score: 3 + 1 + 3 + 2 = 9
- Base band: High
- Linked services: SVC-08
- Highest linked service tier: Important
- Overrides: none
- Final band: High
| VEN-010 | BrightMeet Collaboration | ASMT-010 | Internal (1), None (0), 1 (1), Easy (1) | 3 | Low | None | Low | True |

**Calculation trace**
- Assessment: ASMT-010
- Vendor: VEN-010
- Data Sensitivity: Internal = 1
- System Access: None = 0
- Dependency Impact: 1 = 1
- Replaceability: Easy = 1
- Base score: 1 + 0 + 1 + 1 = 3
- Base band: Low
- Linked services: SVC-05
- Highest linked service tier: Important
- Overrides: none
- Final band: Low
| VEN-004 | SwiftPay Gateway | ASMT-011 | Regulated (3), Privileged (2), 4 (4), Hard (3) | 12 | Critical | Business-critical service floor; Regulated plus privileged | Critical | True |

**Calculation trace**
- Assessment: ASMT-011
- Vendor: VEN-004
- Data Sensitivity: Regulated = 3
- System Access: Privileged = 2
- Dependency Impact: 4 = 4
- Replaceability: Hard = 3
- Base score: 3 + 2 + 4 + 3 = 12
- Base band: Critical
- Linked services: SVC-03
- Highest linked service tier: Business-critical
- Overrides: Business-critical service floor; Regulated plus privileged
- Final band: Critical

## Incomplete-input errors

NONE

## Historical snapshot treatment

Every assessment uses its own assessment_criticality_snapshot row. ASMT-004 uses the historical values retained in that snapshot; current VEN-004 fields are used only for ASMT-011 and are never substituted for ASMT-004.

## Comparison with expected_criticality.csv

Status: **PASS**

Compared rows: 11 / 11

All selected assessment results and override reasons match the expected output oracle.

## Limitations

- Phase 2 implements criticality calculation and semantic validation only.
- Risk scoring, evidence scoring, decisions, remediation, management reporting and GUI remain later-phase work.
- Assessment factors are only as reliable as their supplied snapshot source.
- The expected_criticality.csv file is read only for this explicit comparison; it does not supply calculation inputs.
