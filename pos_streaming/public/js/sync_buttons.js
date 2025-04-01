frappe.listview_settings['Sales Invoice'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('Sync Unsynced Records'), function() {
            frappe.call({
                method: 'pos_streaming.pos_streaming.api.sync_all',
                args: { doctype: 'Sales Invoice' },
                callback: function(response) {
                    frappe.msgprint(__('Sync completed.'));
                }
            });
        });
    }
};
