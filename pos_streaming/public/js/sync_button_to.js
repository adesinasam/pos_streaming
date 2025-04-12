frappe.listview_settings['Sales Invoice'] = {
    add_fields: ['sync_status'],
    get_indicator: function(doc) {
        return doc.sync_status ? [__('Synced'), 'green'] : [__('Unsynced'), 'orange'];
    },
    onload: function(listview) {
        listview.page.add_menu_item(__('Sync Unsynced'), function() {
            frappe.call({
                method: 'pos_streaming.pos_streaming.api.remote_sync.sync_to_remote',
                args: {},
                freeze: true,
                callback: function() { listview.refresh(); }
            });
        });
    }
};

// frappe.listview_settings['Sales Invoice'] = {
//     onload: function(listview) {
//         listview.page.add_inner_button(__('Sync Unsynced Records'), function() {
//             frappe.call({
//                 method: 'pos_streaming.pos_streaming.api.sync_all',
//                 args: { doctype: 'Sales Invoice' },
//                 callback: function(response) {
//                     frappe.msgprint(__('Sync completed.'));
//                 }
//             });
//         });
//     }
// };