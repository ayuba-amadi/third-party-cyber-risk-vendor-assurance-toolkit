"""Exercise the fictional demo pages through Streamlit AppTest."""

from datetime import date
from pathlib import Path
import unittest
from unittest.mock import patch

try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None


APP = Path(__file__).resolve().parents[2] / "app"


@unittest.skipIf(AppTest is None, "Streamlit AppTest requires the GUI dependencies")
class StreamlitPages(unittest.TestCase):
    def page(self, name):
        app = AppTest.from_file(APP / "streamlit_app.py", default_timeout=30).run()
        if name != "1_Dashboard":
            app.switch_page(f"pages/{name}.py").run()
        self.assertFalse(app.exception)
        return app

    def test_each_page_loads_with_fixture(self):
        from app.ui_helpers import PAGES

        for title, name in PAGES:
            with self.subTest(page=title):
                app = self.page(name)
                self.assertEqual(app.title[0].value.casefold(), title.casefold())
                self.assertEqual(len(app.session_state.workspace.rows("vendor")), 10)

    def test_vendor_search_filter_and_validation(self):
        app = self.page("2_Vendor_Register")
        app.text_input[0].set_value("VEN-003").run()
        self.assertEqual(app.dataframe[0].value.vendor_id.tolist(), ["VEN-003"])
        app.multiselect(key="register_category").set_value(["Payroll"]).run()
        self.assertEqual(len(app.dataframe[0].value), 1)
        next(button for button in app.button if button.label == "Validate vendor").click().run()
        self.assertTrue(any("vendor.csv" in issue.value for issue in app.error))
        self.assertFalse(app.exception)

    def test_report_date_changes_expiry_flag(self):
        app = self.page("5_Decisions")
        app.selectbox(key="decision_vendor").set_value("VEN-006").run()
        self.assertIn("Expired approval", [warning.value for warning in app.warning])
        app.date_input(key="report_date").set_value(date(2026, 10, 20)).run()
        self.assertNotIn("Expired approval", [warning.value for warning in app.warning])
        self.assertFalse(app.exception)

    def test_register_wires_readable_download(self):
        import csv
        from io import StringIO

        with patch("streamlit.download_button", return_value=False) as download:
            self.page("2_Vendor_Register")
        args = next(call.args for call in download.call_args_list if call.args[2] == "vendor.csv")
        payload = args[1].decode("utf-8-sig") if isinstance(args[1], bytes) else args[1]
        self.assertEqual(next(csv.DictReader(StringIO(payload)))["vendor_id"], "VEN-001")

    def test_new_vendor_and_changed_criticality(self):
        app = self.page("2_Vendor_Register")
        workspace = app.session_state.workspace
        row = dict(workspace.rows("vendor")[-1], vendor_id="VEN-011", vendor_name="Live Demo Vendor",
                   data_sensitivity="Internal", system_access="None", dependency_impact="2",
                   replaceability="Moderate", current_assessment_id="", assessment_status="Not started")
        for widget in [*app.text_input, *app.selectbox]:
            if widget.key and widget.key.startswith("vendor_form_"):
                field = widget.key.split("_0_", 1)[1]
                widget.set_value(row[field])
        next(button for button in app.button if button.label == "Save vendor to session").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(workspace.rows("vendor")), 11)
        self.assertEqual(workspace.criticality_preview(row).total_points, 5)
        self.assertFalse(workspace.changed_rows("decision"))
        app.radio[0].set_value("Edit selected vendor").run()
        for field, value in (("system_access", "Privileged"), ("dependency_impact", "4")):
            app.selectbox(key=f"vendor_form_Edit selected vendor_VEN-011_0_{field}").set_value(value)
        next(button for button in app.button if button.label == "Calculate criticality").click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any("5 (Medium) → 9 (High) · +4 points" in item.value for item in app.markdown))
        self.assertEqual(app.dataframe[-1].value.previous.tolist(), ["None", "2"])

    def test_conditional_approval_requires_explicit_confirmation(self):
        from copy import deepcopy

        app = self.page("5_Decisions")
        workspace = app.session_state.workspace
        tables = deepcopy(workspace.tables)
        row = next(row for row in tables["decision"].rows if row["decision_id"] == "DEC-002")
        tables["decision"].rows.remove(row)
        audit_rows = tables["reviewer_audit_entry"].rows
        audit_rows[:] = [item for item in audit_rows if item["record_id"] != "DEC-002"]
        self.assertEqual(workspace.save(tables), [])
        app.selectbox(key="decision_vendor").set_value("VEN-003").run()
        next(widget for widget in app.selectbox if widget.label == "Decision outcome *").set_value("Conditionally Approved")
        values = {"Fictional decision-maker *": "Fictional approver", "Decision-maker role *": row["decision_maker_role"],
                  "Justification *": row["justification"], "Decision date *": row["decision_date"],
                  "Review date *": row["review_date"], "Expiry date *": row["expiry_date"],
                  "Condition deadline": row["condition_deadline"]}
        for widget in [*app.text_input, *app.text_area]:
            if widget.label in values:
                widget.set_value(values[widget.label])
        app.multiselect[0].set_value(["ACT-001"])
        next(button for button in app.button if button.label == "Review decision summary").click().run()
        self.assertIsNone(workspace.pending_decision)
        self.assertTrue(any("Conditions" in issue.value for issue in app.error))
        next(widget for widget in app.text_area if widget.label == "Conditions").set_value(row["conditions"])
        next(widget for widget in app.text_input if widget.label == "Review date *").set_value("1900-01-01")
        next(button for button in app.button if button.label == "Review decision summary").click().run()
        self.assertIsNone(workspace.pending_decision)
        next(widget for widget in app.text_input if widget.label == "Review date *").set_value(row["review_date"])
        next(button for button in app.button if button.label == "Review decision summary").click().run()
        self.assertFalse(app.exception)
        self.assertIsNotNone(workspace.pending_decision)
        self.assertNotIn("ASMT-003", workspace.operations[4])
        next(button for button in app.button if button.label == "Confirm decision in session").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(workspace.operations[4]["ASMT-003"]["outcome"], "Conditionally Approved")
        self.assertIn("ACT-001", workspace.operations[4]["ASMT-003"]["source_ids"])
