import frappe
import requests
import logging
from frappe.utils import get_request_site_address

logger = frappe.logger("pos_streaming")

REMOTE_URL = frappe.conf.get('remote_url')
API_KEY = frappe.conf.get('remote_api_key')
API_SECRET = frappe.conf.get('remote_api_secret')


headers = {
    'Content-Type': 'application/json'
}

# Helper to call remote REST API

def call_remote(path, method='GET', data=None, params=None):
    url = f"{REMOTE_URL}/api/resource/{path}"
    auth = (API_KEY, API_SECRET)
    try:
        response = requests.request(method, url, auth=auth, json=data, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json().get('data')
    except Exception as e:
        logger.error(f"Remote call failed: {e}")
        raise

# 1. Push from Local → Remote

def push_docs(doctype, filters=None):
    filters = filters or { 'sync_status': 0 }
    docs = frappe.get_all(doctype, filters=filters, fields='*')
    for doc in docs:
        data = doc.copy()
        data.pop('name', None)
        try:
            call_remote(f"{doctype}/{doc.name}", method='PUT', data=data)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                call_remote(doctype, method='POST', data={'data': data})
        except Exception as e:
            logger.error(f"Failed to push {doctype} {doc.name}: {e}")
            continue
        frappe.db.set_value(doctype, doc.name, 'sync_status', 1)
    frappe.db.commit()

# 2. Pull from Remote → Local (using last updated)

def pull_docs(doctype):
    field_key = f"last_pull_{doctype.lower().replace(' ', '_')}"
    last_sync_time = frappe.db.get_single_value('System Settings', field_key)
    if not last_sync_time:
        last_sync_time = '2025-01-01 00:00:00'

    # filters = [["modified", ">", last_sync_time]] if modified_filter else []

    try:
        docs = call_remote(doctype, params={"filters": [["modified", ">", last_sync_time]]})
        pulled = 0

        for d in docs:
            d.pop("name", None)
            try:
                doc = frappe.get_doc({**d, "doctype": doctype})
                doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
                pulled += 1

                # Log successful sync
                frappe.get_doc({
                    "doctype": "Sync Log",
                    "direction": "Pull",
                    "doctype_name": doctype,
                    "docname": doc.name,
                    "status": "Success",
                    "message": f"Pulled and inserted."
                }).insert(ignore_permissions=True)

            except Exception as e:
                frappe.get_doc({
                    "doctype": "Sync Log",
                    "direction": "Pull",
                    "doctype_name": doctype,
                    "docname": d.get("name", "UNKNOWN"),
                    "status": "Failed",
                    "message": str(e),
                    "traceback": frappe.get_traceback()
                }).insert(ignore_permissions=True)

        # update sync timestamp
        if pulled > 0:
            ss = frappe.get_single("System Settings")
            setattr(ss, field_key, now())
            ss.save(ignore_permissions=True)

        frappe.msgprint(f"Pulled {pulled} {doctype}(s) from remote.")

    except Exception as e:
        # Catch entire pull failure
        frappe.get_doc({
            "doctype": "Sync Log",
            "direction": "Pull",
            "doctype_name": doctype,
            "docname": "N/A",
            "status": "Failed",
            "message": str(e),
            "traceback": frappe.get_traceback()
        }).insert(ignore_permissions=True)

# Wrapper functions

@frappe.whitelist()
def sync_to_remote():
    for dt in ["Sales Invoice", "POS Opening Shift", "POS Closing Shift"]:
        push_docs(dt)

@frappe.whitelist()
def sync_from_remote():
    for dt in ["Item", "Item Price", "Price List", "POS Profile"]:
        pull_docs(dt)