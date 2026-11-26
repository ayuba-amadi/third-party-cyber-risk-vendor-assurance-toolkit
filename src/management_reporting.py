"""Current vendor measures with source populations and fixture reconciliation."""
from collections import defaultdict

from .loader import load_table
from .reassessment import review_status
from .decision_workflow import APPROVALS


def management_summary(tables, criticality, risks, decisions, remediation, report_date):
    groups = defaultdict(set)
    services = defaultdict(set)
    vendor_services = defaultdict(set)
    vendors = {row["vendor_id"]: row for row in tables["vendor"].rows}
    for link in tables["vendor_service_link"].rows:
        services[link["service_id"]].add(link["vendor_id"])
        vendor_services[link["vendor_id"]].add(link["service_id"])

    def flag(name, vendor_id, condition):
        if condition:
            groups["flag", name].add(vendor_id)

    open_findings = set()
    reviews = []
    for vid, vendor in sorted(vendors.items()):
        aid = vendor["current_assessment_id"]
        risk = risks[aid][0] if aid else {}
        decision = decisions.get(aid, {})
        outcome = decision.get("outcome", "Awaiting decision")
        groups["category", vendor["category"]].add(vid)
        groups["criticality", criticality[aid].final_band if aid else "Unassessed"].add(vid)
        groups["decision", outcome].add(vid)
        related = [row for row in remediation if row["current"] and row["vendor_id"] == vid]
        findings = {row["finding_id"] for row in related if row["finding_status"] == "Open"}
        open_findings.update(findings)
        review = review_status(vendor, report_date)
        if review["days_overdue"]:
            reviews.append(review)
        flags = {
            "Incomplete": risk.get("completeness") == "Incomplete",
            "Confirmed critical failure": risk.get("confirmed_critical_failures"),
            "Unresolved critical question": risk.get("unresolved_critical_questions"),
            "Overdue review": review["days_overdue"], "Expired approval": decision.get("expired_approval"),
            "Overdue action": any(row["action_overdue"] for row in related),
            "Open finding": findings, "Open condition": decision.get("open_condition"),
            "Unexpired Approved outcome": outcome == APPROVALS[0] and decision.get("active_approval"),
            "Unanswered": risk.get("unanswered_questions"),
        }
        for state in ("Expired", "Rejected", "Received", "Missing"):
            flags[f"{state} evidence"] = any(item.endswith(f":{state}") for item in risk.get("evidence_flags", []))
        for name, present in flags.items():
            flag(name, vid, present)
        if len(vendor_services[vid]) > 1:
            groups["vendor concentration", "Multiple services"].add(vid)

    concentration = []
    tiers = {}
    for service in sorted(tables["business_service"].rows, key=lambda row: row["service_id"]):
        sid = service["service_id"]
        ids = sorted(services[sid])
        tiers[sid] = service["service_tier"]
        if service["service_tier"] == "Business-critical":
            if ids:
                groups["service dependency", "Business-critical vendor"].update(ids)
        if len(ids) > 1:
            groups["service concentration", sid].update(ids)
        concentration.append(dict(kind="Service", source_id=sid, name=service["service_name"],
                                  tier=service["service_tier"], count=len(ids), linked_ids=ids,
                                  concentration=len(ids) > 1,
                                  business_critical_concentration=len(ids) > 1 and tiers[sid] == "Business-critical",
                                  multiple_important_services=False))
    for vid in sorted(vendors):
        ids = sorted(vendor_services[vid])
        concentration.append(dict(kind="Vendor", source_id=vid, name=vendors[vid]["vendor_name"],
                                  tier="", count=len(ids), linked_ids=ids, concentration=len(ids) > 1,
                                  business_critical_concentration=False,
                                  multiple_important_services=sum(tiers[sid] in ("Important", "Business-critical")
                                                                  for sid in ids) > 1))
    rows = [dict(breakdown=kind, group=name, count=len(ids), vendor_ids=sorted(ids), source_ids=sorted(ids))
            for (kind, name), ids in sorted(groups.items())]
    rows.extend([
        dict(breakdown="total", group="Current vendors", count=len(vendors), vendor_ids=sorted(vendors),
             source_ids=sorted(vendors)),
        dict(breakdown="total", group="Open findings", count=len(open_findings),
             vendor_ids=sorted(groups.get(("flag", "Open finding"), ())), source_ids=sorted(open_findings)),
        dict(breakdown="total", group="Service categories", count=len({v["category"] for v in vendors.values()}),
             vendor_ids=sorted(vendors), source_ids=sorted({v["category"] for v in vendors.values()})),
    ])
    reconcile(rows, set(vendors))
    reconcile(concentration, set(), id_field="linked_ids")
    return rows, concentration, reviews


def reconcile(rows, vendor_ids, id_field="source_ids"):
    for row in rows:
        ids = row[id_field]
        if row["count"] != len(set(ids)) or len(ids) != len(set(ids)):
            raise ValueError(f"Management count does not reconcile: {row}")
    if id_field == "source_ids":
        for kind in ("category", "criticality", "decision"):
            ids = [vid for row in rows if row["breakdown"] == kind for vid in row["vendor_ids"]]
            if len(ids) != len(vendor_ids) or set(ids) != vendor_ids:
                raise ValueError(f"{kind}: breakdown must include each current vendor exactly once")


def compare_management(rows, path):
    table = load_table(path)
    if table.issues:
        raise ValueError(f"Cannot read management oracle: {table.issues}")
    expected = {}
    for row in table.rows:
        key = row["breakdown"], row["group"]
        if key in expected:
            raise ValueError(f"Duplicate management oracle row {key}")
        expected[key] = int(row["count"]), sorted(row["vendor_ids"].split(";"))
    actual = {(row["breakdown"], row["group"]): (row["count"], row["vendor_ids"])
              for row in rows if row["breakdown"] != "total"}
    errors = [f"{key}: expected {expected.get(key)}, calculated {actual.get(key)}"
              for key in sorted(expected.keys() | actual.keys()) if expected.get(key) != actual.get(key)]
    if errors:
        raise ValueError("Management oracle mismatch\n" + "\n".join(errors))
    return len(expected)
