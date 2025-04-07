frappe.listview_settings['Item'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('Sync Unsynced'), function() {
            frappe.call({
                method: 'pos_streaming.pos_streaming.api.remote_sync.sync_from_remote',
                args: { doctype: 'Item' },
                callback: function(response) {
                    frappe.msgprint(__('Sync completed.'));
                }
            });
        });
    }
};