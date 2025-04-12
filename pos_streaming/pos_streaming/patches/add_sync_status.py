import frappe

def execute():
    for doctype in ["Sales Invoice", "POS Opening Shift", "POS Closing Shift"]:
        if not frappe.db.exists({"doctype": "Custom Field", "dt": doctype, "fieldname": "sync_status"}):
            frappe.get_doc({
                "doctype": "Custom Field",
                "dt": doctype,
                "label": "Synced",
                "fieldname": "sync_status",
                "fieldtype": "Check",
                "default": 1,
                "insert_after": "naming_series"
            }).insert(ignore_permissions=True)
