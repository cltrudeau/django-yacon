function load_folder_toolbar() {
    $('#add_folder').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            $('#add_folder_dialog').dialog("open");
        }
    });

    $('#remove_folder_warn').button().click(function() {
        var node = active_node();
        if( node != null ) {
            // get the warning about the nodes to remove
            var key = node.data.key;
            var dialog = $('#remove_folder_dialog');
            dialog.load("/yacon/browser/remove_folder_warn/?node=" + key);
            dialog.dialog("open");
        }
    });
}

function load_toolbars() {
    load_folder_toolbar();
}

function hide_all_toolbars() {
    $('#folder_toolbar').hide();
    $('#remove_folder_warn').show();
}
