# Browser defect report template

Record every failure in the [current defect register](../reports/qa/DEFECT_REGISTER.md). Link duplicate observations to the existing defect ID. Chat can alert the team. The register is the required record. Use fictional data only.

| Field | Entry |
|---|---|
| Defect ID | Unique ID, such as DEF-001 |
| Test ID | Linked browser case and execution attempt |
| Page or workflow | |
| Tester name or role | |
| Date and time in WAT (UTC+1) | |
| URL and commit or deployment version | |
| Browser and device size | |
| Preconditions | Report date, session state and fictional IDs |
| Reproduction steps | Numbered browser actions and input values |
| Expected result | |
| Actual result | Include the exact error or incorrect display |
| Screenshot or download evidence | Repository-relative path |
| Severity | Critical, High, Medium or Low |
| Suggested correction | |
| Owner and correction commit | |
| Retest result | Status, WAT time, tested commit, observations and evidence path |
| Closure or acceptance | State, reviewer and rationale |

## Severity

- **Critical** means the toolkit cannot start, data is corrupted or risk results are invalid.
- **High** means a required workflow or demonstration is unusable.
- **Medium** means a material usability or reporting problem.
- **Low** means a cosmetic or minor wording issue.

Release requires zero unresolved Critical or High defects and documented reviewer acceptance of Medium defects. Retest every correction in the browser. QA sign-off must identify the exact tested commit.
