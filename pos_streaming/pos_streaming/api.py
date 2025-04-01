import frappe
import requests
import json

REMOTE_URL = "https://test.olambe.com.ng"  # Replace with actual remote site URL
API_KEY = "2ab0299ebc9ccb8"
API_SECRET = "b460f803bd27716"

HEADERS = {
    "Authorization": f"token {API_KEY}:{API_SECRET}",
    "Content-Type": "application/json"
}

def get_unsynced_records(doctype):
    """Fetch all records where sync_status is unchecked (0)."""
    return frappe.get_all(doctype, filters={"sync_status": 0}, fields=["name"])

def sync_record(doctype, record_name):
    """Sync a single record to the remote instance."""
    try:
        doc = frappe.get_doc(doctype, record_name)
        doc_dict = doc.as_dict()
        
        response = requests.post(
            f"{REMOTE_URL}/api/resource/{doctype}",
            json=doc_dict,
            headers=HEADERS,
        )

        if response.status_code == 200:
            frappe.db.set_value(doctype, record_name, "sync_status", 1)
            frappe.db.commit()
            return f"Successfully synced {doctype}: {record_name}"
        else:
            return f"Failed to sync {doctype}: {record_name} - {response.text}"
    
    except Exception as e:
        return f"Error syncing {doctype}: {record_name} - {str(e)}"

def sync_all(doctype):
    """Sync all unsynced records for the given doctype."""
    unsynced_records = get_unsynced_records(doctype)
    messages = []
    for record in unsynced_records:
        messages.append(sync_record(doctype, record["name"]))
    return messages
