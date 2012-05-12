function load_folder_toolbar() {
    $('#add_folder').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            $('#add_folder_dialog').dialog("open");
        }
    });

    $('#add_page').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            $('#add_page_dialog').dialog("open");
        }
    });

    $('#remove_folder_warn').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            // get the warning about the nodes to remove
            var dialog = $('#remove_folder_dialog');
            dialog.load("/yacon/nexus/remove_folder_warn/" + node_id + "/");
            dialog.dialog("open");
        }
    });
    $('#add_path').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            $('#add_path_dialog').dialog("open");
        }
    });
    $('#add_path').hide()

}

function load_metapage_toolbar() {
    $('#remove_page_warn').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            // get the warning about the metapage to remove
            var dialog = $('#remove_page_dialog');
            dialog.load("/yacon/nexus/remove_page_warn/" + node_id + "/");
            dialog.dialog("open");
        }
    });

    $('#add_translation').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            $('#add_translation_dialog').dialog("open");
        }
    });
    $('#add_translation').hide()

    $('#make_default_page').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            action = confirm('Make this page the default for its parent '
                + 'node?');
            if( action ) {
                $.ajax({
                    url: "/yacon/nexus/make_default_metapage/" + node_id + "/",
                    dataType: "json",
                    success: function(data) {
                        if( data['error'] == null ) {
                            refresh_tree();
                        }
                    }
                });
            }
        }
    });
}

function load_site_toolbar() {
    // *** Site Toolbar
    $('#site_info').button().click(function() {
        value = $('#site_select').attr('value');
        if( value == null || value == "nop" || value == "add" ) {
            // select is set to strange item, do nothing
            return false;
        }

        // hide toolbars and activate nothing in the tree
        var tree = $('#tree').dynatree("getTree");
        tree.activateKey(null);
        hide_all_toolbars();

        // load site info via ajax
        $("div#node_container").load("/yacon/nexus/site_info/" + value + "/");
    });
}


function load_toolbars() {
    load_folder_toolbar();
    load_metapage_toolbar();
    load_site_toolbar();
}
