# Vendor Criticality Assessment Method

**Project:** Third-Party Cyber Risk Assessment and Vendor Assurance Toolkit  
**Document Owner:** Saadu Shukurat Titilayo 
**Subgroup:** Research and Risk Assessment  
**Version:** 0.1 DRAFT  
**Date:** 17 November 2026  
**Status:** Draft – Pending Team Review

---

## 1. Purpose

This document defines a proposed method for determining the criticality of third-party vendors.

Vendor criticality helps the organisation understand how important a vendor is to business operations and how much disruption could occur if the vendor's services became unavailable, were compromised, or could no longer be relied upon.

The method considers the sensitivity of information handled by the vendor, the level of system access granted, the potential business impact of disruption, and how difficult it would be to replace the vendor.

The criticality assessment is separate from the security risk assessment. A vendor may be critical to business operations while still having strong security controls.

## 2. Criticality Categories

Each vendor will be assigned one of four criticality categories:

| Criticality | Description |
|---|---|
| Low | The vendor supports activities with limited business impact. Disruption would have minimal consequences and the vendor can be replaced easily. |
| Medium | The vendor supports important activities, but disruption is manageable and alternative arrangements are reasonably available. |
| High | The vendor supports important business operations, handles sensitive information, or has significant system access. Disruption could affect business services. |
| Critical | The vendor supports business-critical operations or creates a significant dependency that could cause serious disruption if the service fails. |

## 3. Assessment Factors

The proposed methodology uses four factors from the project data dictionary.

### 3.1 Data Sensitivity

This measures the sensitivity of information handled by the vendor.

| Data Sensitivity | Proposed Score |
|---|---:|
| None | 0 |
| Internal | 1 |
| Confidential | 2 |
| Regulated | 3 |

### 3.2 System Access

This measures the level of access the vendor has to the organisation's systems.

| System Access | Proposed Score |
|---|---:|
| None | 0 |
| Standard | 1 |
| Privileged | 2 |

### 3.3 Dependency Impact

This measures the potential impact on business operations if the vendor's service becomes unavailable.

The project data dictionary defines this factor on a scale of 1 to 4.

| Dependency Impact | Description | Score |
|---|---|---:|
| 1 | Minor impact | 1 |
| 2 | Limited impact | 2 |
| 3 | Significant impact | 3 |
| 4 | Business-critical outage | 4 |

### 3.4 Replaceability

This measures how difficult it would be to replace the vendor or move the service to another provider.

| Replaceability | Proposed Score |
|---|---:|
| Easy | 1 |
| Moderate | 2 |
| Hard | 3 |
| Very hard | 4 |

## 4. Proposed Criticality Calculation

The proposed calculation is:

**Criticality Score = Data Sensitivity Score + System Access Score + Dependency Impact Score + Replaceability Score**

The maximum possible score is 13.

The proposed classification thresholds are:

| Total Score | Criticality Category |
|---|---|
| 0–3 | Low |
| 4–6 | Medium |
| 7–9 | High |
| 10–13 | Critical |

These thresholds are proposed for team review and must be approved before implementation.

## 5. Criticality Overrides

A vendor's total score should not be the only consideration.

The following proposed override rules ensure that important business dependencies are not underestimated.

### Override 1: Business-Critical Service

Where a vendor supports a business service classified as Business-critical, its criticality should not be lower than High.

### Override 2: Regulated Data and Privileged Access

Where a vendor handles Regulated data and has Privileged system access, its criticality should be Critical.

### Override 3: Severe Dependency and Difficult Replacement

Where dependency impact is 4 and replaceability is Very hard, the vendor should be classified as Critical.

Any override applied must be documented with its reason.

## 6. Missing and Invalid Information

Criticality calculations require complete and valid information.

The following rules are proposed:

- Required fields must not be left blank.
- Values outside the approved data dictionary must be rejected.
- Missing information must not automatically be treated as a low-risk value.
- Where a required factor is missing, the assessment should be flagged as incomplete.
- The assessor should obtain the missing information before confirming the final criticality category.
- Any provisional classification must be clearly labelled as provisional.

## 7. Multiple Business Services

Where a vendor supports more than one business service, all linked services must be considered.

The highest service tier supported by the vendor should be used when applying the business-critical service override.

For example, a vendor supporting both an Important service and a Business-critical service should be treated as supporting a Business-critical service.

The vendor's service links should be retained so that concentration and dependency can also be considered in management reporting.

## 8. Reassessment Triggers

Criticality should be reviewed when a material change affects the vendor's relationship with the organisation.

Examples include:

- Increase in system access.
- Addition of a new data type.
- Increase in service scope.
- Introduction of a new subcontractor.
- Change in ownership.
- Significant change in business dependency.

A material change should trigger a new assessment version.

Previously submitted assessments must be retained and must not be overwritten.

## 9. Worked Criticality Examples

The following examples use fictional vendors from the project demo scenarios.

### VEN-001 – NimbusCloud Hosting

NimbusCloud Hosting supports several services, including the customer portal, card payments, core ERP, and staff email and collaboration.

The vendor supports multiple services and has a Critical target band in the demo scenarios.

Its criticality assessment should consider:

- Data sensitivity.
- System access.
- Dependency impact.
- Replaceability.
- The business-critical services it supports.

The final score must be calculated using the approved methodology.

### VEN-002 – PayStream Processing

PayStream Processing supports card payments, which is classified as a Business-critical service.

The business-critical service override should ensure that its criticality is not classified below High.

Its final category should be determined using the approved scoring method.

### VEN-009 – LegalDocs Storage

LegalDocs Storage supports contract and legal document storage.

Its demo scenario identifies a High target band.

The absence of encryption evidence for regulated data is a security control failure. This should be considered in the risk assessment and critical-failure rules rather than automatically changing the vendor's business criticality category.

## 10. Governance and Review

The criticality methodology should be reviewed and approved by the project team before implementation.

The methodology should be version-controlled.

Changes to scoring factors, thresholds or override rules must be documented.

The criticality result should inform the vendor risk assessment and review priorities. It must not independently determine whether a vendor is approved.

---



