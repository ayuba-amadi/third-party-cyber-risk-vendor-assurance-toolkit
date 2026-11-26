# Defect register

| ID | Test | Severity | Initial observed result | Correction | Retest and status |
|---|---|---|---|---|---|
| P6-001 | Q02 | Major | Vendor edit calculated the new score and general warning. The previous values, prior band and signed point change were absent. | Vendor Register displays changed factors with previous and updated values, both bands and point difference. Assessed vendors receive a reassessment warning. | Closed. The Streamlit widget retest asserted the 5 Medium to 9 High comparison, +4 points and previous values. See unittest evidence. |

The initial assessor-script errors were corrected before the final test run. The first duplicate test appended a row without its physical row number. The final test uses the application's candidate builder. The evidence test now addresses the source field `status`. The browser locator was refined to select the primary page heading when the generated report adds its own heading.
