import frappe

def execute():
    for doctype in ["Sales Invoice", "POS Opening Shift", "POS Closing Shift"]:
        if not frappe.db.exists({"doctype": "Custom Field", "dt": doctype, "fieldname": "custom_synced"}):
            frappe.get_doc({
                "doctype": "Custom Field",
                "dt": doctype,
                "label": "Synced",
                "fieldname": "custom_synced",
                "fieldtype": "Check",
                "default": 0
            }).insert(ignore_permissions=True)