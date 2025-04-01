frappe.listview_settings['Sales Invoice'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('Sync Unsynced Records'), function() {
            frappe.call({
                method: 'sync_app.api.sync_all',
                args: { doctype: 'Sales Invoice' },
                callback: function(response) {
                    frappe.msgprint(__('Sync completed.'));
                }
            });
        });
    }
};

frappe.listview_settings['POS Opening Shift'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('Sync Unsynced Records'), function() {
            frappe.call({
                method: 'sync_app.api.sync_all',
                args: { doctype: 'POS Opening Shift' },
                callback: function(response) {
                    frappe.msgprint(__('Sync completed.'));
                }
            });
        });
    }
};

frappe.listview_settings['POS Closing Shift'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('Sync Unsynced Records'), function() {
            frappe.call({
                method: 'sync_app.api.sync_all',
                args: { doctype: 'POS Closing Shift' },
                callback: function(response) {
                    frappe.msgprint(__('Sync completed.'));
                }
            });
        });
    }
};
