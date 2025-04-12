import frappe
import requests
import logging
from frappe.utils import get_request_site_address
from frappe.secrets import get as get_secret

logger = frappe.logger("pos_streaming")

# REMOTE_URL = frappe.conf.get('remote_url')
# API_KEY = frappe.conf.get('remote_api_key')
# API_SECRET = frappe.conf.get('remote_api_secret')

REMOTE_URL = get_secret('remote_url')
API_KEY = get_secret('remote_api_key')
API_SECRET = get_secret('remote_api_secret')

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

def pull_docs(doctype, key_field='name', modified_filter=True):
    field_key = f'last_pull_{doctype.replace(" ", "_").lower()}'
    last_sync_time = frappe.db.get_single_value('System Settings', field_key)
    if not last_sync_time:
        last_sync_time = '2025-01-01 00:00:00'

    filters = [["modified", ">", last_sync_time]] if modified_filter else []

    try:
        remote_list = call_remote(doctype, params={"filters": filters})
        for remote in remote_list:
            name = remote[key_field]
            try:
                doc = frappe.get_doc(doctype, name)
                for k, v in remote.items():
                    doc.set(k, v)
                doc.save(ignore_permissions=True)
            except frappe.DoesNotExistError:
                new_doc = frappe.get_doc({"doctype": doctype, **remote})
                new_doc.insert(ignore_permissions=True)
        frappe.db.set_value('System Settings', None, field_key, frappe.utils.now())
        frappe.db.commit()
    except Exception as e:
        logger.error(f"Pull failed for {doctype}: {e}")

# Wrapper functions

@frappe.whitelist()
def sync_to_remote():
    for dt in ["Sales Invoice", "POS Opening Shift", "POS Closing Shift"]:
        push_docs(dt)

@frappe.whitelist()
def sync_from_remote():
    for dt in ["Item", "Item Price", "Price List", "POS Profile"]:
        pull_docs(dt)