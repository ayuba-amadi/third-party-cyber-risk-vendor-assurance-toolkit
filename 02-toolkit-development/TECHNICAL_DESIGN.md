# Technical Design — Third-Party Cyber Risk Assessment and Vendor Assurance Toolkit
**Project:** Third-Party Cyber Risk Assessment and Vendor Assurance Toolkit
**Subgroup:** Group 2 — Toolkit Development
**Version:** 0.1 DRAFT
**Date:** 20 November 2026
**Status:** Proposed Technical Design — Pending Team Review

---

## 1. Purpose

This document describes the proposed technical architecture and implementation approach for the Third-Party Cyber Risk Assessment and Vendor Assurance Toolkit.

The toolkit will help analysts register vendors, validate assessment information, evaluate security evidence, calculate risk, track approval decisions and corrective actions, and generate management reports.

The implementation will follow the research team's requirements and documented methodology. Any unresolved policy decisions will be recorded and will not be silently treated as approved rules.

## 2. Technology Selection

The initial implementation will use:

| Component | Technology |
|---|---|
| Programming language | Python |
| Input data | CSV files |
| Output data | CSV and readable report files |
| Interface | Command-line interface (CLI) |
| Testing | Python unittest |
| Version control | Git and GitHub |
| Development environment | Visual Studio Code on Windows |

### Reason for selection

Python provides a reproducible and maintainable way to implement validation, calculations, reporting and testing.

CSV provides a portable data format that can be inspected using spreadsheet applications and processed programmatically.

A command-line interface is appropriate for the first version because it keeps the implementation simple while allowing the team to demonstrate and test the main requirements.

A web interface may be considered in a later version, but it is not part of the initial scope.

## 3. Proposed Architecture

The toolkit will be organised into the following processing stages:

1. Data import — load vendor, service, question, response, evidence and other source records.
2. Data validation — check required fields, identifiers, allowed values, dates and relationships.
3. Criticality assessment — calculate vendor criticality using the approved methodology.
4. Evidence assessment — distinguish supplier claims from reviewer-verified findings and evidence status.
5. Risk calculation — calculate weighted risk, completeness and critical-failure flags.
6. Decision and action tracking — display and preserve human approval decisions, findings and corrective actions.
7. Reassessment — preserve previous assessment versions and process material changes.
8. Reporting — produce individual vendor reports and consolidated management reports.

The toolkit will support human review and decision-making. It will not automatically approve a vendor based on a calculated score.

## 4. Proposed Project Structure

The implementation will follow the repository's agreed folder structure:

```text
third-party-cyber-risk-vendor-assurance-toolkit/
│
├── 01-research-and-risk-assessment/
│
├── 02-toolkit-development/
│   ├── README.md
│   ├── WORKPLAN.md
│   └── TECHNICAL_DESIGN.md
│
├── src/
│   ├── README.md
│   └── vendor_assurance/
│
├── sample-data/
│   └── README.md
│
├── tests/
│   └── README.md
│
├── reports/
│   └── examples/
│
└── docs/
    └── USER_GUIDE.md
```

Directories will be created as implementation work begins. Additional Python modules will be introduced when their responsibilities are defined.

## 5. Data Management

CSV files will be the initial source-data format.

The application will preserve the research team's source fields and map them into internal application structures where necessary.

The core records will include:

- Vendors
- Business services
- Vendor-service relationships
- Assessment versions
- Questions
- Responses
- Evidence items
- Findings
- Corrective actions
- Decisions
- Change events
- Reviewer audit entries

Identifiers such as `vendor_id`, `assessment_id`, `question_id` and `evidence_id` will be used to maintain relationships between records.

The application will validate duplicate identifiers, missing required values, invalid options and orphan references before processing assessments.

Public repository data will contain fictional demonstration records only.

## 6. Validation and Risk Processing

Validation will take place before risk calculations.

Invalid records will be reported with their source row, field and reason. Where possible, valid records will remain available for processing without silently accepting invalid records.

The calculation engine will implement the approved criticality and risk-scoring methodologies.

The engine will distinguish:

- Supplier-reported claims.
- Reviewer-verified answers.
- Accepted evidence.
- Missing, received, rejected and expired evidence.
- Incomplete assessments.
- Confirmed critical failures.

Missing or unverified evidence must never be treated as favourable.

A critical failure must not be concealed by a favourable aggregate score.

Every calculated result should be explainable through its source responses, evidence records, weights, risk values and applicable rules.

## 7. Decisions and Reassessment

Approval decisions will remain separate from calculated risk results.

The toolkit will support:

- Approved
- Conditionally Approved
- Rejected

Decision records should identify the authorised decision-maker, justification, applicable conditions and relevant dates.

Corrective actions will be linked to findings and vendors, with owners, deadlines and statuses.

Material changes, overdue reviews, expired approvals and other approved reassessment triggers will be flagged.

Previous assessment versions must be preserved. A reassessment must create a new assessment record rather than overwrite a submitted assessment.

## 8. Reporting

The initial reporting functions will produce:

### Individual vendor report

- Vendor identification and category.
- Business services supported.
- Criticality classification.
- Assessment completeness.
- Calculated risk percentage and rating, where permitted.
- Critical failures and unresolved evidence.
- Findings and corrective actions.
- Human approval decision.
- Reassessment and expiry flags.

### Management report

- Total registered vendors.
- Vendors by category and criticality.
- Approval decision distribution.
- Incomplete assessments.
- Critical findings.
- Overdue corrective actions.
- Expired approvals and overdue reviews.
- Business-service concentration.

Management counts must be reconciled to distinct vendor IDs and supported by underlying source records.

## 9. Testing Strategy

Testing will use fictional data and repeatable test cases.

The initial test coverage will include:

1. Successful import of valid vendor records.
2. Duplicate vendor identifier rejection.
3. Missing required field validation.
4. Invalid enumeration rejection.
5. Criticality calculation.
6. Missing and unverified evidence handling.
7. Rejected and expired evidence handling.
8. Critical-failure override.
9. Conditional approval and overdue corrective action.
10. Expired approval and overdue review.
11. Reassessment with historical version retention.
12. Management report reconciliation.

The final test cases will be aligned with the research team's acceptance cases when supplied and approved.

## 10. Outstanding Research Decisions and Dependencies

The following matters require confirmation before their corresponding rules are treated as final:

| ID | Outstanding issue |
|---|---|
| RD-01 | Confirm whether all 24 questionnaire questions require evidence. |
| RD-02 | Confirm the critical-failure scoring rule for verified failures versus unresolved critical questions. |
| RD-03 | Confirm evidence validity periods and expiry calculations. |
| RD-04 | Confirm whether an approver may also act as a reviewer. |
| RD-05 | Confirm approval validity periods and conditional approval limits. |
| RD-06 | Resolve inconsistencies in the VEN-005 and VEN-009 completeness scenarios. |
| RD-07 | Confirm the expected number of vendors supporting business-critical services. |
| RD-08 | Obtain the ten-vendor sample data, worked examples and acceptance cases. |
| RD-09 | Obtain the team's formal research-to-development handoff decision. |

Until these matters are resolved, related implementation rules will be identified as provisional and documented.

## 11. Security and Repository Considerations

Only fictional vendor and person data will be committed to the public repository.

Real vendor assessments, credentials, confidential evidence and personal contact information must be stored in an appropriately restricted organisational environment.

GitHub will be used for source-code collaboration and version control, not as a repository for confidential assessment evidence.

## 12. Implementation Status

**Current status:** Technical design drafted.

**Next activities:**
1. Review the design against the Group 2 workplan.
2. Confirm outstanding research dependencies.
3. Establish the Python project structure.
4. Implement CSV import and validation.
5. Develop calculation and reporting modules.
6. Test the toolkit against the demonstration scenarios.
**Document status:** Draft pending team review.
