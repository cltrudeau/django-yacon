function setup() {
    load_toolbars();
    load_dialogs();
    create_tree(activate, init_ajax_url, lazy_read);
}

function activate(node) {
    hide_all_toolbars();

    // load contents of node
    var pieces = node.data.key.split(":");
    var file_type = pieces[0];
    var path = pieces[1];

    if( file_type == 'system') {
        // system node, show a blank page
        if( path == 'public' ) {
            $("div#node_container").html('<p>Directories and files contained '
            + 'in the Public area are accessible by everyone.  These files '
            + ' should be configured to be served directly by the web server.'
            + '</p>');
        }
        else if( path == 'private' ) {
            $("div#node_container").html('<p>Directories and files contained '
            + 'in the Private area are accessible only by those with '
            + 'permission.  These files either need to be served by the '
            + 'application server or using the X-Sendfile method.</p>');
        }
        else {
            $("div#node_container").html('<p>Error in tree</p>');
        }
    }
    else {
        $("div#node_container").load('/yacon/nexus/uploads/folder_info/' 
            + node.data.key + '/');
    }
}


function lazy_read(node) {
    node.appendAjax({
        url:"/yacon/nexus/uploads/sub_tree/",
        data: {
            "key":node.data.key
        }
    });
}


function init_ajax_url() {
    return '/yacon/nexus/uploads/tree_top/';
}
