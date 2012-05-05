// =======================================================
// Helper Functions

function hide_all_toolbars() {
    $('#folder_toolbar').hide();
    $('#metapage_toolbar').hide();
}

// =======================================================
// Tree Helper Functions

function create_tree() {
    // if you get here then user selected a site, load the tree
    $("#tree").dynatree({
        onActivate: function(node) {
            hide_all_toolbars();

            // load contents of node
            var pieces = node.data.key.split(":");
            var node_type = pieces[0];
            var node_id = pieces[1];

            var link = '/yacon/nexus/metapage_info/';
            if( node_type == 'node' )
                link = '/yacon/nexus/node_info/';

            link += "" + node_id + "/";

            $("div#node_container").load(link);

            // show the appropriate action bar
            if( node_type == 'node') {
                $('#folder_toolbar').show();
            }
            if( node_type == 'metapage') {
                // action is a metapage
                $('#metapage_toolbar').show();
            }
        },
        onPostInit: function(isReloading, isError) {
            // check if the "select_me" variable is set, if so choose that
            // node
            if( select_me != null ) {
                choose_item(select_me);
                select_me = null;
            }
            // check if there is an active node
            node = this.getActiveNode();
            if( node == null ) {
                // no active node, set it to our root; tree has invisible
                // root whose second child is our root
                this.getRoot().getChildren()[1].activate()
            }
            else {
                // tree has active node, activate event event doesn't
                // trigger on a reload, our dynamic content is loaded via
                // activate, so force the activation after initialization
                this.reactivate();
            }
        },
        persist: true,
        initAjax: {
            url: init_ajax_url()
        }
    });
}

function active_node() {
    var tree = $('#tree').dynatree("getTree");
    var node = tree.getActiveNode();
    return node;
}

function active_node_id() {
    var tree = $('#tree').dynatree("getTree");
    var node = tree.getActiveNode();
    if( node == null )
        return node;

    // load contents of node
    var pieces = node.data.key.split(":");
    return pieces[1];
}

function refresh_tree() {
    var tree = $('#tree').dynatree("getTree");
    tree.reload();
    return tree
}

// global var for synch selection after reload
var select_me = null;

function choose_item(key) {
    var tree = $('#tree').dynatree("getTree");
    var node = tree.getNodeByKey(key);

    if( node != null ) {
        node.activate();
    }
}

function init_ajax_url() {
    // can't just hardcode the url as it is dependent on the value of the
    // select box; can't just use a variable inside of the select.change()
    // method as the method doesn't get called in certain reload situations
    // (e.g. undo-close tab in FF)
    value = $('#site_select').attr('value');
    if( value == null || value == "nop" || value == "add" ) {
        // select is set to strange item, return default site
        return '/yacon/nexus/full_tree_default_site/';
    }

    // select is set to a site, return that url
    return '/yacon/nexus/full_tree/' + value + "/";
}

// =======================================================
// Dialog Creation Function

function create_dialog(selector, title, url_generator, success, complete) {
    var height = Math.floor(0.80 * $(window).height());
    var width = Math.floor(0.80 * $(window).width());

    $(selector).dialog({
        autoOpen: false,
        modal: true,
        maxHeight: height,
        height: height,
        maxWidth: width,
        width: width,
        buttons: {
            "Ok":function() {
                var node_id = active_node_id();
                if( node_id != null ) {
                    var url = url_generator();
                    $.ajax({
                        url: url,
                        success: success,
                        complete: complete,
                    });
                }
                else {
                    $(this).dialog('close');
                }
                return false;
            },
            "Cancel":function() {
                $(this).dialog('close');
                return false;
            }
        },
        title: title,
    });
}

// =======================================================
// Document Ready

$(document).ready(function(){
    hide_all_toolbars();

    // setup change action when a new site is picked
    $('#site_select').change(function() {
        var value = $(this).attr('value');
        if( value == 'nop' ) {
            return;
        }
        if( value == 'add' ) {
            console.debug('id10t selected add')
            return;
        }

        // check if a tree exists already
        var tree = $('#tree').dynatree("getTree");
        if( tree.hasOwnProperty('$widget') ) {
            var url = init_ajax_url();
            $('#tree').dynatree("option", "initAjax", {"url": url})
            refresh_tree()
        }
        else {
            create_tree()
        }
    });

    // load list of sites
    $.ajax({
        url: "/yacon/nexus/get_sites/",
        dataType: "json",
        success: function(data) {
            // remove old sites, replace with what server sent
            $('#site_select').children().remove();
            for( var key in data ){
                if( data.hasOwnProperty(key) ){
                    $('#site_select').append('<option value="' + key + '">' 
                        + data[key] + '</option>');
                }
            }

            // add site actions
            $('#site_select').append('<option value="nop">' + 
                '----------</option>');
            $('#site_select').append('<option value="add">Add Site' +
                '</option>');

            // turn widget into jquery style drop down, then force a change
            // event
            $('#site_select').selectbox();
            $('#site_select').change();
        }
    });

    // ---------------------------------------------------------
    // Toolbar Buttons

    // *** Folder Toolbar
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

    // ---------------------------------------------------------
    // Dialog Boxes

    create_dialog('#remove_folder_dialog', 'Remove Folder',
        function() { // url generator
            var node_id = active_node_id();
            return "/yacon/nexus/remove_folder/" + node_id + "/";
        },
        function(data) { // on success of ajax call
            refresh_tree();
        },
        function() { // on completion of ajax call
            $('#remove_folder_dialog').dialog('close');
        }
    );
    create_dialog('#add_folder_dialog', 'Add Folder',
        function() { // url generator
            var node_id = active_node_id();
            var title = $('#add_folder_form input#add_folder_title').val();
            var slug = $('#add_folder_form input#add_folder_slug').val();
            return "/yacon/nexus/add_folder/" + node_id + "/" + title + "/"
                + slug + "/";
        },
        function(data) { // on success of ajax call
            if( data['error'] == null ) {
                select_me = data['key'];
                refresh_tree();
            }
            else {
                // something was wrong with our slug, show the user
                alert(data['error']);
            }
        },
        function() { // on completion of ajax call
            $('#add_folder_dialog').dialog('close');
        }
    );
    create_dialog('#add_page_dialog', 'Add Page',
        function() { // url generator
            var node_id = active_node_id();
            var title = $('#add_page_form input#add_page_title').val();
            var slug = $('#add_page_form input#add_page_slug').val();
            return "/yacon/nexus/add_page/" + node_id + "/" + title + "/"
                + slug + "/";
        },
        function(data) { // on success of ajax call
            if( data['error'] == null ) {
                select_me = data['key'];
                refresh_tree();
            }
            else {
                // something was wrong with our slug, show the user
                alert(data['error']);
            }
        },
        function() { // on completion of ajax call
            $('#add_page_dialog').dialog('close');
        }
    );

    // ---------------------------------------------------------
    // Prepopulate Slug Fields
    $('#add_folder_slug').bind('change.yacon', function() {
        $(this).data('changed', true);
    });

    $('#add_folder_title').bind('keyup.yacon', function() {
        var e = $('#add_folder_slug');
        if( !e.data('changed') ) {
            e.val(URLify($('#add_folder_title').val(), 50));
        }
    });

    $('#add_page_slug').bind('change.yacon', function() {
        $(this).data('changed', true);
    });

    $('#add_page_title').bind('keyup.yacon', function() {
        var e = $('#add_page_slug');
        if( !e.data('changed') ) {
            e.val(URLify($('#add_page_title').val(), 50));
        }
    });
}); // end document ready
