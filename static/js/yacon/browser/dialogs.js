function load_dialogs() {
    // *** Folder Toolbar Dialogs
    create_dialog_using_tree('#add_folder_dialog', 'Add Folder', 'Add',
        function() { // url generator
            var node = active_node();
            var key = node.data.key;
            var name = $('#add_folder_form input#add_folder_name').val();
            return "/yacon/browser/add_folder/" + name + "/?node="
                + encodeURIComponent(key);
        },
        function(data) { // on success of ajax call
            var tree = $('#tree').dynatree("getTree");
            var node = tree.getActiveNode();
            if( node == null || node.data.key.substring(0, 6) == 'system' ) {
                refresh_tree();
                return
            }

            // new child was added, re-lazy-load the current node
            node.reloadChildren();
        }
    );

    create_dialog_using_tree('#remove_folder_dialog', 'Remove Folder', 'Remove',
        function() { // url generator
            var node = active_node();
            var key = node.data.key;

            // activate the parent's node so when we come back on the refresh
            // things will be focused there
            node = node.getParent();
            node.activate();
            return "/yacon/browser/remove_folder/?node=" + key;
        },
        function(data) { // on success of ajax call
            refresh_tree();
        }
    );
}
