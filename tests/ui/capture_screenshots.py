"""Capture the fictional demo using Playwright and a local Streamlit server."""
import csv
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    page = browser.new_page(viewport={"width": 1500, "height": 1050}, accept_downloads=True)
    page.goto("http://localhost:8501")
    page.set_default_timeout(9000)
    def capture(name, focus=None):
        page.locator('[data-testid="stMain"] h1').first.wait_for()
        assert not page.locator('[data-testid="stException"]').count()
        if focus is not None:
            focus.evaluate("(element) => element.scrollIntoView({block: 'center'})")
        page.screenshot(path=f"docs/screenshots/{name}.png", full_page=True)
        print(name, flush=True)
    def go(name, title=None):
        page.get_by_role("link", name=name, exact=True).click()
        page.get_by_role("heading", name=title or name, exact=True).wait_for()
    def vendor(vid):
        page.locator("[data-testid=stMain] [data-testid=stSelectbox]").first.get_by_role("combobox").click()
        page.get_by_role("option").filter(has_text=vid).click()
    capture("dashboard")
    go("Vendor Register", "Vendor register")
    page.get_by_role("textbox", name="Search by vendor ID or name").fill("VEN-001")
    page.get_by_role("textbox", name="Search by vendor ID or name").press("Enter")
    capture("vendor-register")
    with page.expect_download() as info:
        page.get_by_role("button", name="Download vendor record").first.click()
    with info.value.path().open(encoding="utf-8-sig") as handle:
        assert next(csv.DictReader(handle))["vendor_id"] == "VEN-001"
    print("Vendor CSV downloaded and parsed", flush=True)
    page.get_by_role("button", name="Validate vendor").click()
    page.get_by_text("vendor.csv, row", exact=False).first.wait_for()
    capture("data-quality")
    for label, value in {"Vendor ID": "VEN-011", "Vendor name": "Live Demo Vendor", "Service description": "Fictional demo service",
                         "Business owner": "Fictional service owner", "Data types": "None", "Next review date": "2027-05-18"}.items():
        page.get_by_role("textbox", name=f"{label} *", exact=True).fill(value)
    for label, value in {"Category": "Collaboration SaaS", "Data sensitivity": "Internal", "System access": "None",
                         "Dependency impact": "2", "Replaceability": "Moderate", "Subcontractor use": "No"}.items():
        wrapper = page.locator("[data-testid=stSelectbox]").filter(has=page.get_by_text(f"{label} *", exact=True))
        wrapper.get_by_role("combobox").click()
        page.get_by_role("option", name=value, exact=True).click()
    page.get_by_role("button", name="Calculate criticality").click()
    page.get_by_text("Final classification", exact=False).last.wait_for()
    capture("new-vendor-criticality", page.get_by_text("Final classification", exact=False).last)
    go("Assessment")
    vendor("VEN-002")
    page.get_by_text("Completeness: Incomplete", exact=False).first.wait_for()
    capture("missing-evidence")
    vendor("VEN-009")
    page.get_by_text("confirmed critical", exact=False).first.wait_for()
    capture("critical-failure")
    go("Decisions")
    vendor("VEN-003")
    page.get_by_text("Conditionally Approved", exact=False).first.wait_for()
    capture("conditional-approval")
    vendor("VEN-006")
    page.get_by_text("Expired approval", exact=True).wait_for()
    capture("expired-approval")
    go("Remediation")
    page.get_by_text("Overdue actions", exact=True).click()
    capture("overdue-action")
    go("Reassessment")
    vendor("VEN-004")
    page.get_by_role("table", name="Assessment version comparison").get_by_text("ASMT-011", exact=True).wait_for(timeout=6000)
    capture("reassessment")
    go("Reports")
    page.get_by_role("combobox", name="Report type").click()
    page.get_by_role("option", name="Management summary", exact=True).click()
    page.get_by_role("button", name="Generate report").click()
    with page.expect_download() as info:
        page.get_by_role("button", name="Download Markdown", exact=True).click()
    assert "Current vendors" in info.value.path().read_text()
    print("Management Markdown downloaded and read", flush=True)
    capture("management-reconciliation", page.get_by_text("Current vendors", exact=False).last)
