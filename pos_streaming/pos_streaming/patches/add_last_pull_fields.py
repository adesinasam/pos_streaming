import frappe

def execute():
    target_fields = [
        "last_pull_item",
        "last_pull_item_price",
        "last_pull_price_list",
        "last_pull_pos_profile"
    ]

    for fieldname in target_fields:
        if not frappe.db.exists("Custom Field", {"dt": "System Settings", "fieldname": fieldname}):
            frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "System Settings",
                "fieldname": fieldname,
                "label": fieldname.replace("_", " ").title(),
                "fieldtype": "Datetime",
                "insert_after": "language"
            }).insert(ignore_permissions=True)