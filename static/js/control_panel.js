// =======================================================
// Helper Functions

function hide_all_toolbars() {
    $('#folder_toolbar').hide();
    $('#metapage_toolbar').hide();
    $('#add_translation').hide()
    $('#add_path').hide()
}

function repopulate_select(selector, data) {
    $(selector).children().remove();
    for( var key in data ){
        if( data.hasOwnProperty(key) ){
            $(selector).append('<option value="' + key + '">' + data[key] 
                + '</option>');
        }
    }
}

function count_keys(data) {
    num_keys = 0;
    for( var key in data ){
        if( data.hasOwnProperty(key) ){
            num_keys++;
        }
    }
    return num_keys;
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
                $.ajax({
                    url: '/yacon/nexus/missing_node_translations/' + 
                        node_id +'/',
                    success: function(data) {
                        if( count_keys(data) != 0 ) {
                            $('#add_path').show()
                        }
                    },
                });
            }
            if( node_type == 'metapage') {
                // action is a metapage
                $('#metapage_toolbar').show();
                $.ajax({
                    url: '/yacon/nexus/missing_metapage_translations/' + 
                        node_id +'/',
                    success: function(data) {
                        if( count_keys(data) != 0 ) {
                            $('#add_translation').show()
                        }
                    },
                });
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

function create_dialog(selector, title, ok_label, url_generator, success, 
        complete) {
    var height = Math.floor(0.80 * $(window).height());
    var width = Math.floor(0.80 * $(window).width());

    $(selector).dialog({
        autoOpen: false,
        modal: true,
        maxHeight: height,
        height: height,
        maxWidth: width,
        width: width,
        buttons: [
            {
                text:ok_label,
                click: function() {
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
            },
            {
                text:"Cancel",
                click:function() {
                    $(this).dialog('close');
                    return false;
                }
            },
        ],
        title: title,
    });
}

// =======================================================
// Inline Action Functions

// global var for which node path to edit
var edit_translation_id = null;

function edit_path(translation_id, lang_code, name, path) {
    edit_translation_id = translation_id;
    var parts = path.split('/');
    var slug = parts.pop();
    if( slug == '' ) 
        slug = parts.pop();

    $('#edit_path_form input#edit_path_lang').val(lang_code);
    $('#edit_path_form input#edit_path_name').val(name);
    $('#edit_path_form input#edit_path_slug').val(slug);
    $('#edit_path_dialog_warn').load("/yacon/nexus/edit_path_warn/" 
        + translation_id + "/");

    $('#edit_path_dialog').dialog('open');
}

// global var for which node path to remove
var remove_translation_id = null;

function remove_path(translation_id) {
    remove_translation_id = translation_id;
    var dialog = $('#remove_path_dialog');
    dialog.load("/yacon/nexus/remove_path_warn/" + translation_id + "/");
    dialog.dialog("open");
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
            repopulate_select('#site_select', data);

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
    $('#add_path').button().click(function() {
        var node_id = active_node_id();
        if( node_id != null ) {
            $('#add_path_dialog').dialog("open");
        }
    });
    $('#add_path').hide()

    // *** MetaPage Toolbar
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

    // *** Folder Toolbar Dialogs
    create_dialog('#remove_folder_dialog', 'Remove Folder', 'Remove',
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
    create_dialog('#add_folder_dialog', 'Add Folder', 'Add',
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
    create_dialog('#add_page_dialog', 'Add Page', 'Add',
        function() { // url generator
            var node_id = active_node_id();
            var pagetype = $('#add_page_form #add_page_pagetype').val();
            var title = $('#add_page_form input#add_page_title').val();
            var slug = $('#add_page_form input#add_page_slug').val();
            return "/yacon/nexus/add_page/" + node_id + "/" + pagetype + "/" 
                + title + "/" + slug + "/";
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
    $('#add_page_dialog').bind('dialogopen.yacon', function(event, ui) {
        // ajax load the page type listing when we pop the dialog
        $.ajax({
            url: "/yacon/nexus/page_types/",
            dataType: "json",
            success: function(data) {
                // remove old sites, replace with what server sent
                repopulate_select('#add_page_pagetype', data);
            }
        });
    });
    create_dialog('#add_path_dialog', 'Add Translation', 'Add',
        function() { // url generator
            console.debug('inside url gen');
            var node_id = active_node_id();
            var lang = $('#add_path_form #add_path_lang').val();
            var name = $('#add_path_form input#add_path_name').val();
            var slug = $('#add_path_form input#add_path_slug').val();
            return "/yacon/nexus/add_path/" + node_id + "/" + lang 
                + "/" + name + "/" + slug + "/";
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
            $('#add_path_dialog').dialog('close');
        }
    );
    $('#add_path_dialog').bind('dialogopen.yacon', function(event, ui) {
        // ajax load the language listing when we pop the dialog
        var node_id = active_node_id();
        $.ajax({
            url: "/yacon/nexus/missing_node_translations/" + node_id + "/",
            dataType: "json",
            success: function(data) {
                // remove old translations, replace with what server sent
                repopulate_select('#add_path_lang', data);
            }
        });
    });

    // *** MetaPage Toolbar Dialogs
    create_dialog('#remove_page_dialog', 'Remove MetaPage', 'Remove',
        function() { // url generator
            var node_id = active_node_id();
            return "/yacon/nexus/remove_page/" + node_id + "/";
        },
        function(data) { // on success of ajax call
            refresh_tree();
        },
        function() { // on completion of ajax call
            $('#remove_page_dialog').dialog('close');
        }
    );

    create_dialog('#add_translation_dialog', 'Add Translation', 'Add',
        function() { // url generator
            console.debug('inside url gen');
            var node_id = active_node_id();
            var lang = $('#add_translation_form #add_translation_lang').val();
            var title = 
                $('#add_translation_form input#add_translation_title').val();
            var slug = 
                $('#add_translation_form input#add_translation_slug').val();
            return "/yacon/nexus/add_translation/" + node_id + "/" + lang 
                + "/" + title + "/" + slug + "/";
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
            $('#add_translation_dialog').dialog('close');
        }
    );
    $('#add_translation_dialog').bind('dialogopen.yacon', function(event, ui) {
        // ajax load the language listing when we pop the dialog
        var node_id = active_node_id();
        $.ajax({
            url: "/yacon/nexus/missing_metapage_translations/" + node_id + "/",
            dataType: "json",
            success: function(data) {
                // remove old translations, replace with what server sent
                repopulate_select('#add_translation_lang', data);
            }
        });
    });

    // ---------------------------------------------------------
    // Inline Action Dialogs

    // *** Node Dialogs
    create_dialog('#remove_path_dialog', 'Remove Path', 'Remove',
        function() { // url generator
            return "/yacon/nexus/remove_path/" + remove_translation_id + "/";
        },
        function(data) { // on success of ajax call
            refresh_tree();
        },
        function() { // on completion of ajax call
            $('#remove_path_dialog').dialog('close');
        }
    );
    create_dialog('#edit_path_dialog', 'Edit Path', 'Save',
        function() { // url generator
            var slug = $('#edit_path_form input#edit_path_slug').val();
            var name = $('#edit_path_form input#edit_path_name').val();
            return "/yacon/nexus/edit_path/" + edit_translation_id + "/" 
                + name + "/" + slug + "/";
        },
        function(data) { // on success of ajax call
            refresh_tree();
        },
        function() { // on completion of ajax call
            $('#edit_path_dialog').dialog('close');
        }
    );

    // ---------------------------------------------------------
    // Prepopulate Slug Fields

    // *** Add Folder 
    $('#add_folder_slug').bind('change.yacon', function() {
        $(this).data('changed', true);
    });
    $('#add_folder_title').bind('keyup.yacon', function() {
        var e = $('#add_folder_slug');
        if( !e.data('changed') ) {
            e.val(URLify($('#add_folder_title').val(), 50));
        }
    });

    // *** Add Page 
    $('#add_page_slug').bind('change.yacon', function() {
        $(this).data('changed', true);
    });
    $('#add_page_title').bind('keyup.yacon', function() {
        var e = $('#add_page_slug');
        if( !e.data('changed') ) {
            e.val(URLify($('#add_page_title').val(), 50));
        }
    });

    // *** Add Translation 
    $('#add_translation_slug').bind('change.yacon', function() {
        $(this).data('changed', true);
    });
    $('#add_translation_title').bind('keyup.yacon', function() {
        var e = $('#add_translation_slug');
        if( !e.data('changed') ) {
            e.val(URLify($('#add_translation_title').val(), 50));
        }
    });
}); // end document ready
