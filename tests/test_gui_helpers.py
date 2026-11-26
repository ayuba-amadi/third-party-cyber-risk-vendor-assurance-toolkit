from pathlib import Path
import unittest

try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None


@unittest.skipIf(AppTest is None, "Install app/requirements.txt for GUI smoke tests")
class GuiTests(unittest.TestCase):
    def setUp(self):
        # Each run initializes the CSV-backed workspace and its validation and
        # operational views. Allow for cold Python/Streamlit startup as well as
        # the fixture load; AppTest's default three seconds is too short here.
        self.app = AppTest.from_file(
            str(Path(__file__).resolve().parents[1] / "app/streamlit_app.py"),
            default_timeout=15,
        ).run()
        self.assertFalse(self.app.exception)

    def page(self, file):
        self.app.switch_page(f"pages/{file}.py").run()
        self.assertFalse(self.app.exception)

    def control(self, kind, label):
        return next(widget for widget in getattr(self.app, kind) if widget.label == label)

    def visible(self):
        texts = [item.value for kind in ("subheader", "markdown", "success", "warning", "error", "info")
                 for item in self.app.get(kind)]
        labels = [item.proto.label for kind in ("expander", "download_button")
                  for item in self.app.get(kind)]
        return "\n".join(texts + labels)

    def test_dashboard_and_all_pages(self):
        self.assertIn("Current vendors · 10", self.visible())
        self.assertIn("Expired approvals · 1", self.visible())
        for filename in ("2_Vendor_Register", "3_Assessment", "4_Evidence_Review", "5_Decisions",
                         "6_Remediation", "7_Reassessment", "8_Reports", "9_Data_Quality"):
            self.page(filename)
            self.assertIn("How to use this page", self.visible())

    def test_assessment_and_evidence_fixtures(self):
        self.page("3_Assessment")
        self.control("selectbox", "Vendor").select("VEN-001").run()
        self.assertIn("ASMT-001", self.visible())
        self.control("selectbox", "Vendor").select("VEN-009").run()
        self.assertIn("Confirmed critical failures impose a High minimum", self.visible())
        self.page("4_Evidence_Review")
        self.control("selectbox", "Vendor").select("VEN-002").run()
        self.control("multiselect", "Evidence status").set_value(["Missing"]).run()
        self.assertIn("Effective status: **Missing**", self.visible())
        self.assertFalse(self.app.exception)

    def test_operations_fixtures(self):
        self.page("5_Decisions")
        conditional = next(row["assessment_id"] for row in self.app.session_state.workspace.rows("decision")
                           if row["outcome"] == "Conditionally Approved")
        vendor = self.app.session_state.workspace.operations[1][conditional]["vendor_id"]
        self.control("selectbox", "Vendor").select(vendor).run()
        self.assertIn("Conditionally Approved", self.visible())
        self.page("6_Remediation")
        self.control("radio", "Show records").set_value("Overdue actions").run()
        self.assertTrue(self.app.dataframe)
        self.page("7_Reassessment")
        self.control("selectbox", "Vendor").select("VEN-004").run()
        self.assertIn("The previous assessment has been preserved", self.visible())
        self.assertEqual(self.app.dataframe[0].value["assessment_id"].tolist(), ["ASMT-004", "ASMT-011"])
        self.assertEqual(self.app.dataframe[1].value["change_id"].tolist(), ["CHG-001", "CHG-002"])

    def test_reports_and_validation(self):
        self.page("8_Reports")
        self.control("button", "Generate report").click().run()
        self.assertIn("Download CSV", self.visible())
        self.assertIn("Download assessment package", self.visible())
        self.control("selectbox", "Report type").select("Management summary").run()
        self.control("button", "Generate report").click().run()
        self.assertIn("Download management package", self.visible())
        self.page("9_Data_Quality")
        self.control("button", "Run validation").click().run()
        self.assertIn("Validation passed.", self.visible())
        self.assertFalse(self.app.exception)

    def test_vendor_entry_validation_and_recalculation(self):
        self.page("2_Vendor_Register")
        for name, value in {"Vendor ID *": "VEN-001", "Vendor name *": "Fictional Test Vendor",
                            "Service description *": "Fictional fulfilment", "Business owner *": "Test owner",
                            "Data types *": "Fictional regulated data", "Next review date *": "2027-01-01"}.items():
            self.control("text_input", name).set_value(value)
        for name, value in {"Category *": "Cloud hosting", "Data sensitivity *": "Regulated",
                            "System access *": "Standard", "Dependency impact *": "2",
                            "Replaceability *": "Easy", "Subcontractor use *": "No"}.items():
            self.control("selectbox", name).select(value)
        self.control("button", "Validate vendor").click().run()
        self.assertTrue(any("duplicate" in issue.value.lower() for issue in self.app.error))
        self.control("text_input", "Vendor ID *").set_value("VEN-011")
        self.control("button", "Calculate criticality").click().run()
        self.assertIn("System Access: Standard", self.visible())
        self.control("selectbox", "System access *").select("Privileged")
        self.control("button", "Calculate criticality").click().run()
        self.assertIn("Final classification · **Critical**", self.visible())
        self.control("button", "Save vendor to session").click().run()
        self.assertIn("Saved Fictional Test Vendor to this session.", self.visible())
        self.assertFalse(self.app.session_state.workspace.changed_rows("decision"))

    def test_missing_evidence_blocks_verification(self):
        self.page("4_Evidence_Review")
        self.control("selectbox", "Vendor").select("VEN-002").run()
        self.control("multiselect", "Evidence status").set_value(["Missing"]).run()
        self.control("checkbox", "Verify with accepted evidence").check()
        self.control("button", "Save evidence review to session").click().run()
        self.assertIn("Verification requires", self.visible())
        self.assertFalse(self.app.session_state.workspace.changed_rows("evidence_item"))

    def test_human_decision_requires_confirmation(self):
        self.page("5_Decisions")
        self.control("selectbox", "Vendor").select("VEN-004").run()
        self.control("selectbox", "Decision outcome *").select("Rejected")
        self.control("text_input", "Fictional decision-maker *").set_value("Fictional Approver")
        self.control("text_input", "Decision-maker role *").set_value("Fictional risk director")
        self.control("text_area", "Justification *").set_value("Fictional test decision pending evidence.")
        self.control("text_input", "Expiry date *").set_value("2027-01-01")
        self.control("text_input", "Review date *").set_value("2026-12-01")
        self.control("button", "Review decision summary").click().run()
        self.assertIn("Fictional decision-maker: Fictional Approver", self.visible())
        self.assertFalse(self.app.session_state.workspace.changed_rows("decision"))
        self.control("button", "Confirm decision in session").click().run()
        ws = self.app.session_state.workspace
        self.assertEqual([row["outcome"] for row in ws.changed_rows("decision")], ["Rejected"])
        self.assertEqual(ws.changed_rows("reviewer_audit_entry")[0]["action"], "Decided")
        self.control("button", "Reset session").click().run()
        self.assertFalse(self.app.session_state.workspace.changed_rows("decision"))
