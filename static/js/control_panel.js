// =======================================================
// Tree Helper Functions

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

function choose_item(key) {
    var tree = $('#tree').dynatree("getTree");
    var node = tree.getNodeByKey(key);

    if( node != null ) {
        node.activate();
    }

    return false;
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
// Dialog Action Functions

function remove_folder_warn() {
    var node_id = active_node_id();
    if( node_id != null ) {
        // get the warning about the nodes to remove
        var dialog = $('#remove_folder_dialog');
        dialog.load("/yacon/nexus/remove_folder_warn/" + node_id + "/");
        dialog.dialog("open");
    }
    return false;
}

// =======================================================
// Document Ready

$(document).ready(function(){
    // hide node and metapage action divs
    $('#folder_actions').hide();
    $('#metapage_actions').hide();

    // perform action when user does something with site select
    $('#site_select').change(function() {
        var value = $(this).attr('value');
        if( value == 'nop' ) {
            console.debug('id10t selected separator')
            return;
        }
        if( value == 'add' ) {
            console.debug('id10t selected add')
            return;
        }

        // if you get here then user selected a site, load the tree
        $("#tree").dynatree({
            onActivate: function(node) {
                // hide the context toolbars
                $('#folder_actions').hide();
                $('#metapage_actions').hide();

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
                    $('#folder_actions').show();
                }
                if( node_type == 'metapage') {
                    // action is a metapage
                    $('#metapage_actions').show();
                }
            },
            onPostInit: function(isReloading, isError) {
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
                url: "/yacon/nexus/full_tree/" + value + "/"
            }
        });
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

            // trigger change based on selection
            $('#site_select').change();
        }
    });

    // ---------------------------------------------------------
    // Dialog Boxes

    create_dialog('#remove_folder_dialog', 'Remove Folder',
        function() { // url generator
            var node_id = active_node_id();
            return "/yacon/nexus/remove_folder/" + node_id + "/";
        },
        function() { // on success of ajax call
            refresh_tree();
        },
        function() { // on completion of ajax call
            $('#remove_folder_dialog').dialog('close');
        }
    );
}); // end document ready
