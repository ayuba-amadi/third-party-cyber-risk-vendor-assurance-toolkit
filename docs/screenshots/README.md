# Screenshot capture checklist

Start the fictional demo at 18 November 2026. The captures below show the tested states. Use PNG and exclude account details and browser chrome. AppTest evidence covers application rendering and selected interactions.

| Filename | Page | Screen state and expected visual result |
|---|---|---|
| dashboard.png | Dashboard | Baseline counts and dated warnings |
| vendor-register.png | Vendor Register | Search VEN-001 and show linked services |
| new-vendor-criticality.png | Vendor Register | VEN-011 from the script, calculated 5 / Medium and factor values |
| missing-evidence.png | Assessment | VEN-002 / ASMT-002, AM-01 and DP-01 missing, Incomplete |
| critical-failure.png | Assessment | VEN-009 / ASMT-009, DP-01 confirmed, High |
| conditional-approval.png | Decisions | VEN-003 / DEC-002, conditions and review dates |
| overdue-action.png | Remediation | VEN-003 / ACT-001 overdue |
| expired-approval.png | Decisions | VEN-006 / DEC-005 expired |
| reassessment.png | Reassessment | VEN-004, ASMT-004 to ASMT-011, CHG-001 and CHG-002 |
| management-reconciliation.png | Reports | Baseline management report and reconciliation |
| data-quality.png | Vendor Register | Validate an empty add-vendor form and show structured file, row, field and correction messages |

All eleven PNGs were captured from the local fictional demo using headless Chromium. See [browser execution evidence](../../reports/phase6/evidence/browser.txt). The Data Quality example shows the validation message on the vendor entry screen, where a rejected form is still visible. The Data Quality page itself was checked separately using AppTest.
