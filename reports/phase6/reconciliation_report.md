# Management reconciliation

Report date **2026-11-18**. The regenerated Phase 6 report matched all **33** count and vendor-ID rows in the committed expected management fixture. Its **36** rows and overdue-review detail matched Phase 4. The three extra rows in both generated outputs are totals.

The source register has ten unique vendors. All ten current assessment references resolve to the same vendor in assessment.csv. Eleven assessment IDs exist because ASMT-004 is historical and ASMT-011 is current for VEN-004. Category, criticality and decision groups each sum to ten without duplicating vendors. Service memberships overlap by design.

Date flags compare the applicable due, review or expiry date strictly before 18 November 2026. DEC-005 expired on 31 October 2026 and retains the recorded Approved outcome. DEC-008 remains Rejected and is excluded from expired approvals. ACT-001 and the two overdue review dates were 18 days overdue.

| Breakdown | Group | Count | Source IDs | Linked records |
|---|---|---:|---|---|
| category | Cloud hosting | 2 | VEN-001, VEN-007 | — |
| category | Collaboration SaaS | 2 | VEN-009, VEN-010 | — |
| category | Payment processing | 2 | VEN-002, VEN-004 | — |
| category | Payroll | 2 | VEN-003, VEN-008 | — |
| category | Technical support | 2 | VEN-005, VEN-006 | — |
| criticality | Critical | 4 | VEN-001, VEN-002, VEN-003, VEN-004 | ASMT-001, ASMT-002, ASMT-003, ASMT-011 |
| criticality | High | 3 | VEN-006, VEN-007, VEN-009 | ASMT-006, ASMT-007, ASMT-009 |
| criticality | Low | 1 | VEN-010 | ASMT-010 |
| criticality | Medium | 2 | VEN-005, VEN-008 | ASMT-005, ASMT-008 |
| decision | Approved | 4 | VEN-001, VEN-006, VEN-007, VEN-008 | ASMT-001, ASMT-006, ASMT-007, ASMT-008, DEC-001, DEC-005, DEC-006, DEC-007 |
| decision | Awaiting decision | 3 | VEN-002, VEN-004, VEN-010 | ASMT-002, ASMT-011, ASMT-010 |
| decision | Conditionally Approved | 2 | VEN-003, VEN-005 | ASMT-003, ASMT-005, DEC-002, DEC-004 |
| decision | Rejected | 1 | VEN-009 | ASMT-009, DEC-008 |
| flag | Confirmed critical failure | 2 | VEN-003, VEN-009 | ASMT-003/AM-01, ASMT-009/DP-01 |
| flag | Expired approval | 1 | VEN-006 | ASMT-006, DEC-005 |
| flag | Expired evidence | 1 | VEN-006 | — |
| flag | Incomplete | 5 | VEN-002, VEN-004, VEN-005, VEN-006, VEN-010 | ASMT-002, ASMT-011, ASMT-005, ASMT-006, ASMT-010 |
| flag | Missing evidence | 2 | VEN-002, VEN-010 | — |
| flag | Open condition | 2 | VEN-003, VEN-005 | ASMT-003, ASMT-005, DEC-002, DEC-004 |
| flag | Open finding | 6 | VEN-002, VEN-003, VEN-004, VEN-005, VEN-006, VEN-009 | FND-001, FND-002, FND-003, FND-004, FND-005, FND-006, FND-007 |
| flag | Overdue action | 1 | VEN-003 | ACT-001 |
| flag | Overdue review | 2 | VEN-003, VEN-006 | — |
| flag | Received evidence | 1 | VEN-004 | — |
| flag | Rejected evidence | 1 | VEN-005 | — |
| flag | Unanswered | 1 | VEN-010 | — |
| flag | Unexpired Approved outcome | 3 | VEN-001, VEN-007, VEN-008 | — |
| flag | Unresolved critical question | 3 | VEN-002, VEN-004, VEN-010 | — |
| service concentration | SVC-03 | 3 | VEN-001, VEN-002, VEN-004 | SVC-03 |
| service concentration | SVC-04 | 2 | VEN-001, VEN-006 | SVC-04 |
| service concentration | SVC-05 | 2 | VEN-001, VEN-010 | SVC-05 |
| service concentration | SVC-06 | 2 | VEN-005, VEN-006 | SVC-06 |
| service dependency | Business-critical vendor | 4 | VEN-001, VEN-002, VEN-003, VEN-004 | — |
| vendor concentration | Multiple services | 2 | VEN-001, VEN-006 | VEN-001 → SVC-01, SVC-03, SVC-04, SVC-05, VEN-006 → SVC-04, SVC-06 |
| total | Current vendors | 10 | VEN-001, VEN-002, VEN-003, VEN-004, VEN-005, VEN-006, VEN-007, VEN-008, VEN-009, VEN-010 | — |
| total | Open findings | 7 | FND-001, FND-002, FND-003, FND-004, FND-005, FND-006, FND-007 | — |
| total | Service categories | 5 | Cloud hosting, Collaboration SaaS, Payment processing, Payroll, Technical support | — |

Evidence is available in [the regenerated JSON](evidence/management.json), [the generated fixture comparison](evidence/management_reconciliation.csv), [Phase 4 output](../phase4/management_summary.json) and [the committed expectations](../../sample-data/expected_management.csv).
