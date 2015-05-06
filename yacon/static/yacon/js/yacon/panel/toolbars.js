function hide_all_toolbars() {
    $('#folder_toolbar').hide();
    $('#metapage_toolbar').hide();
    $('#menu_toolbar').hide();
    $('#menucontrol_toolbar').hide();
    $('#menuitem_toolbar').hide();
    $('#site_toolbar').hide();
}

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
            dialog.load("/yacon/nexus/control/remove_folder_warn/" + node_id 
                + "/");
            dialog.dialog("open");
        }
    });
    $('#add_path').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            $('#add_path_dialog').dialog("open");
        }
    });
}

function load_metapage_toolbar() {
    $('#add_menuitem').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            $('#add_menuitem_dialog').dialog("open");
        }
    });

    $('#remove_page_warn').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            // get the warning about the metapage to remove
            var dialog = $('#remove_page_dialog');
            dialog.load("/yacon/nexus/control/remove_page_warn/" + node_id 
                + "/");
            dialog.dialog("open");
        }
    });

    $('#add_translation').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            $('#add_translation_dialog').dialog("open");
        }
    });

    $('#make_default_page').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            action = confirm('Make this page the default for its parent '
                + 'node?');
            if( action ) {
                $.ajax({
                    url: "/yacon/nexus/control/make_default_metapage/" 
                        + node_id + "/",
                    dataType: "json",
                    success: function(data) {
                        if( data == null ) {
                            refresh_tree();
                        }
                    }
                });
            }
        }
    });
}

function load_menu_toolbars() {
    $('#remove_menu_warn').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            // get the warning about the metapage to remove
            var dialog = $('#remove_menu_dialog');
            dialog.load("/yacon/nexus/control/remove_menu_warn/" + node_id 
                + "/");
            dialog.dialog("open");
        }
    });

    $('#add_metapage_menuitem').button().click(function() {
        alert('To add a menuitem associated with a metapage, use the ' +
            'site tree to find the menuitem and click "Add to Menu" ');
    });

    $('#add_link_menuitem').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            $('#add_link_menuitem_dialog').dialog("open");
        }
    });

    $('#add_header_menuitem').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            $('#add_header_menuitem_dialog').dialog("open");
        }
    });

    $('#remove_menuitem_warn').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            // get the warning about the metapage to remove
            var dialog = $('#remove_menuitem_dialog');
            dialog.load("/yacon/nexus/control/remove_menuitem_warn/" + node_id 
                + "/");
            dialog.dialog("open");
        }
    });

    $('#add_menuitem_translation').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            $('#add_menuitem_translation_dialog').dialog("open");
        }
    });

    $('#menuitem_move_out').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            $.ajax({
                url: "/yacon/nexus/control/move_menuitem_out/" + node_id + "/",
                dataType: "json",
                success: function(data) {
                    refresh_tree();
                }
            });
        }
    });

    $('#menuitem_move_up').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            $.ajax({
                url: "/yacon/nexus/control/move_menuitem_up/" + node_id + "/",
                dataType: "json",
                success: function(data) {
                    refresh_tree();
                }
            });
        }
    });

    $('#menuitem_move_down').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            $.ajax({
                url: "/yacon/nexus/control/move_menuitem_down/" + node_id + "/",
                dataType: "json",
                success: function(data) {
                    refresh_tree();
                }
            });
        }
    });
}

function load_site_sidebar() {
    // *** Site Sidebar -- appears above tree, has site selector
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
        $('#site_toolbar').show();
        var site_id = $('#site_select').val();
        $.ajax({
            url: '/yacon/nexus/control/missing_site_languages/' + site_id +'/',
            success: function(data) {
                if( count_keys(data) != 0 ) {
                    $('#add_site_lang').show();
                }
            },
        });

        // load site info via ajax
        $("div#node_container").load("/yacon/nexus/control/site_info/" + value 
            + "/");
    });
}

function load_site_toolbar() {
    // *** Site Toolbar -- toolbar when site info is displayed
    $('#add_site_lang').button().click(function() {
        $('#add_site_lang_dialog').dialog("open");
    });
}

function load_menucontrol_toolbar() {
    // *** Menu Control Toolbar -- toolbar when Menus root is displayed
    $('#add_menu').button().click(function() {
        $('#add_menu_dialog').dialog("open");
    });
}

function load_toolbars() {
    load_folder_toolbar();
    load_metapage_toolbar();
    load_site_sidebar();
    load_site_toolbar();
    load_menucontrol_toolbar();
    load_menu_toolbars();
}
