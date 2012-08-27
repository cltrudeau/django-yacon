function load_dialogs() {
    // *** Folder Toolbar Dialogs
    create_dialog_using_tree('#add_folder_dialog', 'Add Folder', 'Add',
        function() { // url generator
            var node = active_node();
            var key = node.data.key;
            var name = $('#add_folder_form input#add_folder_name').val();
            return "/yacon/browser/add_folder/" + encodeURIComponent(key) 
                + "/" + name + "/";
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
            return "/yacon/browser/remove_folder/" + key + "/";
        },
        function(data) { // on success of ajax call
            refresh_tree();
        }
    );
}
