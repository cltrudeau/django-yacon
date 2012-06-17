function hide_all_toolbars() {
    $('#folder_toolbar').hide();
    $('#metapage_toolbar').hide();
    $('#menu_toolbar').hide();
    $('#menucontrol_toolbar').hide();
    $('#menuitem_toolbar').hide();
    $('#site_toolbar').hide();
}

function create_dialog_using_tree(selector, title, ok_label, url_generator, 
        success) {
    // call full with behaviour for items dealing with a selected node in the
    // tree
    create_dialog_full(selector, title, ok_label, 
        function() {
            var node_id = active_node_id();
            if( node_id != null ) {
                var url = url_generator();
                $.ajax({
                    url: url,
                    success: success,
                });
            }
            else {
                $(this).dialog('close');
            }
            return false;
        });
}
